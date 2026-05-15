# SRA 自动注入根因分析 — EPIC-004 背景

> **分析日期**: 2026-05-15
> **分析范围**: SRA 项目 + Hermes Agent 集成
> **关联 Epic**: EPIC-004 (SRA Hermes 原生插件集成)

---

## 核心发现

**SRA 自动注入从未真正工作过。**

SRA 服务端（Daemon、四维匹配引擎、force 级别、validate 端点）全部实现正确，
但 Hermes 端的集成代码从未被执行。

```
EPIC-001 宣称: ✅                    现实: ❌
  _query_sra_context() 已实现          run_agent.py 中零 SRA 代码
  "每次消息自动调 SRA"                 补丁从未执行
  自动注入正常工作                     唯一方式是手动 curl
```

---

## 根因分析

### 根因 1: EPIC-001 验收标准只覆盖 SRA 侧

EPIC-001 的 6 个 AC:
- `[x] Gateway 模式：每次消息自动调 SRA` — ❌ 不存在
- `[x] CLI 模式：每次消息自动调 SRA` — ❌ 不存在
- `[x] 2 秒超时保护` — ❌ 不存在
- ...

**没有一个 AC 要求验证 Hermes 端是否实际被修改。**

AC 只检查了 SRA 侧是否产出了补丁文件（`patches/hermes-sra-integration.patch` 和
`scripts/install-hermes-integration.sh`），但从未验证这些文件是否被实际执行。

### 根因 2: AC 审计只检查文档标记

`scripts/ac-audit.py` 只搜索 `[x]` 标记，不验证对应的代码是否真实存在。

Story 1 说 "Hermes pre_tool_call hook 集成" 有 `[x]`，但代码中找不到任何 Hermes hook
连接 SRA 的痕迹。

### 根因 3: 集成方案选择了最脆弱的方式

`sed -i` 修改 `run_agent.py` 依赖行号定位，Hermes 升级后：
- 行号变化 → 补丁落点偏移
- `git checkout` 覆盖修改 → 补丁丢失
- 无自动恢复机制 → 需手动重装

### 根因 4: `sra install hermes` 是假命令

```python
def cmd_install(args):
    print("步骤 1: 确保 SRA Daemon 已启动")
    print("步骤 2: 在 Hermes 的 learning-workflow 前置层添加:")
    print(adapter.to_system_prompt_block())
    print("步骤 3: 当需要查询推荐时加载 skill-advisor:")
```

这只是一个 print 语句，**不执行任何实际安装操作**。

### 根因 5: force.py 定义了注入点但无消费者

`force.py` 中定义了 4 级注入覆盖度：
- `on_user_message` — 无人调用 POST /recommend
- `pre_tool_call` — 无人调用 POST /validate
- `post_tool_call` — 无人调用 POST /record
- `periodic` — 无人周期性重查询 SRA

ForceLevelManager 仅在 `/status` 端点返回当前级别名称，从未用于实际注入控制。

---

## 影响分析

| 维度 | 影响 |
|:-----|:------|
| SRA 推荐系统 | 唯一工作方式是手动 curl → 每次消息依赖 boku 记住要调 |
| SOUL.md 铁律 | 用文本规则约束，依赖模型遵循，不可靠 |
| 用户体验 | 主人发现 SRA "没工作" → 信任下降 |
| 开发效率 | boku 不知道有哪些 skill 可用 → 可能用错/遗漏 |
| EPIC-003 校验 | pre_tool_call 校验从未生效 → 工具调用无技能保障 |

---

## 修复方向

EPIC-004 采用 **Hermes 插件方案** 替代补丁方案：

```
┌──────────────────────────────────────────────────────┐
│  EPIC-004: 从补丁到插件的架构重构                      │
│                                                      │
│  Phase 0 ✅: sra-guard 插件框架                        │
│  Phase 1 ⏳: 消息前置注入 + [SRA] 上下文格式化          │
│  Phase 2 ⏳: pre_tool_call → POST /validate           │
│  Phase 3 ⏳: 技能使用轨迹追踪                            │
│  Phase 4 ⏳: 周期性重注入防漂移                          │
│  Phase 5 ⏳: 文档漂移修复（EPIC-001/003 标记修正）      │
│  Phase 6 ⏳: 端到端测试 + CI 门禁（AC 代码存在性检查）   │
└──────────────────────────────────────────────────────┘
```

核心变化：
- 不修改 Hermes 核心代码（零侵入）
- 利用 Hermes 已有的 `pre_llm_call` hook 注入上下文
- 插件自动发现，升级后保留
- 每个 Phase 有自动化测试保障

---

## 预防措施（避免同类问题）

1. **跨项目验收标准** — 涉及两个项目的 Story（如 Hermes + SRA），AC 必须在两端都验证
2. **AC 代码存在性检查** — CI 门禁应检查 AC 所述的代码是否存在，而不只是文档中打了 [x]
3. **端到端集成测试** — 验证真实调用链（用户消息 → SRA 注入 → LLM 回复）而非仅单元测试
4. **`install` 命令不能是 print 语句** — CLI 的 install 子命令必须实际执行安装，或明确报错
