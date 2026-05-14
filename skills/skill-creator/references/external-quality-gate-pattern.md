# 纯外部质量门禁模式 (External Quality Gate Pattern)

> **模式类型**: Quality Enforcement · Integration  
> **创建日期**: 2026-05-14  
> **来源实践**: cap-pack/skill-quality 能力包  
> **核心原则**: 不修改任何 Hermes 核心代码，通过外部脚本 + cron + 行为规则实现质量门禁

---

## 问题

在 Hermes 环境中执行 skill 操作（创建/编辑/删除）时，质量门禁（SQS 评分、依赖扫描、引用链分析）需要被调用。但：
- 修改 Hermes 核心代码（`file_tools.py`、`delegate_tool.py` 等）需要跟随升级，维护成本高
- 子代理（`delegate_task`）的 `skip_context_files=True` 导致上下文规则丢失
- Curator 后台的 skill 操作不经过任何质量检查

## 方案：5 层外部门禁架构

```
Layer 1: 检测层  ── hermes-locate.py     → 自动定位 Hermes 环境
Layer 2: 监控层  ── cron-based watchdog  → 检测 skill 目录变更
Layer 3: 门禁层  ── pre-flight-enhancer  → 在 pre_flight 中增强检测
Layer 4: 审计层  ── daily/weekly audit   → 事后质量检查
Layer 5: 行为层  ── boku 行为约束规则    → context 注入约束
```

## 各层具体实现

### Layer 1: 环境检测 (hermes-locate.py)
```python
# 自动检测 Hermes 安装类型（git_clone / pip_package / system）
# 定位工具文件、CLI 命令、技能目录（含 profile 目录）
# 识别补丁状态、生成环境指纹
python3 hermes-locate.py --format feishu
```

### Layer 2: 文件监控 (cron-based)
```bash
cron: "*/15 * * * *" → skill-file-watchdog.py  # 15分钟扫 skill 目录变更
cron: "0 6 * * *"    → hermes-version-tracker.py  # 每天检测版本变化
```

### Layer 3: 增强门禁 (pre-flight-enhancer.py)
调用入口：在 `pre_flight.py` 的 Gate 3 末尾调用
```python
# 检测 pre_flight 原生 regex 遗漏的场景：
#   1. write_file(~/.hermes/skills/xxx/SKILL.md)  ← 路径级别操作
#   2. "创建/编辑/删除 [中文][skill]"              ← 中文无空格
# 自动级联调用 delete → gate/create gate
```

### Layer 4: 定期审计 (cron-based)
```bash
cron: "0 7 * * *"  → daily-quality-audit.py
cron: "0 9 * * 1"  → weekly-health-report.py
```

### Layer 5: 行为约束 (boku self-discipline)
在 `cap-pack.yaml` 的 `integration.behaviors` 中声明行为规则。

## 适用场景对比

| 场景 | 纯外部方案 | 核心修改方案 |
|:-----|:---------:|:-----------:|
| 多环境部署（不同 Hermes 版本） | ✅ 自动适应 | ❌ 需每个版本适配 |
| 被频繁升级破坏的补丁 | ✅ 无需维护 | ❌ 每升级必修 |
| 需要 ≥ 90% 覆盖率 | ⚠️ ~70% | ✅ ~100% |
| 零侵入性部署 | ✅ | ❌ |
| 实现成本 | ~5-8 人天 | ~3-5 人天 |
| 长期维护成本 | 低（外部独立迭代） | 高（跟随升级） |

## 与 Hermes 插件系统的关系

纯外部方案与 Hermes 原生插件系统的关系：
- **Hermes 插件**：通过 `plugins/` 目录扩展，可添加新工具/适配器/记忆后端。但目前的插件 API 不支持 tool-call 后置钩子。
- **纯外部方案**：不依赖 Hermes 插件 API，通过 cron + 行为约束 + 现有入口（pre_flight）集成。兼容性更好。
- **未来方向**：如果 Hermes 插件系统发展出 tool-call 生命周期钩子，可将 Layers 1-4 迁移为插件，Layer 5 保持行为约束。
