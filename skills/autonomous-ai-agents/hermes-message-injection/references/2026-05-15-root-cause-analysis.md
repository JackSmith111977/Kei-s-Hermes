# SRA 自动注入根因分析报告（2026-05-15 深度审计）

## 概述

对 SRA 自动注入功能进行全量源码审计，追踪「文档声称已实现」到「代码实际未执行」之间的差距。

## 审计范围

| 检查目标 | 路径 |
|:---------|:-----|
| Hermes run_agent.py | `~/.hermes/hermes-agent/run_agent.py` (~12,000 LOC) |
| Hermes 插件系统 | `~/.hermes/hermes-agent/hermes_cli/plugins.py` |
| SRA force.py | `~/projects/sra/skill_advisor/runtime/force.py` |
| SRA daemon.py | `~/projects/sra/skill_advisor/runtime/daemon.py` |
| SRA EPIC docs | `~/projects/sra/docs/EPIC-001*`, `EPIC-003*` |
| SRA 补丁/安装脚本 | `patches/hermes-sra-integration.patch`, `scripts/install-hermes-integration.sh` |
| SRA 适配器 | `skill_advisor/adapters/__init__.py` |

## 审计流程

### Step 1: 检查 Hermes 端代码存在性

```bash
grep -rn "_query_sra_context" ~/.hermes/hermes-agent/ --include="*.py"
# → 无结果！此函数不存在于任何 Python 文件中

grep -rn "sra\|SRA\|recommend\|8536" ~/.hermes/hermes-agent/run_agent.py
# → 无结果！run_agent.py 完全没有 SRA 相关代码

grep -rn "sra\|SRA\|8536" ~/.hermes/hermes-agent/gateway/run.py
# → 仅一个无关的 "not recommended" 字符串
```

### Step 2: 检查补丁/安装脚本是否存在

```bash
ls -la ~/projects/sra/patches/hermes-sra-integration.patch
# → 存在（4987 bytes, 112 lines）

ls -la ~/projects/sra/scripts/install-hermes-integration.sh
# → 存在（9540 bytes, 259 lines）

# 检查是否曾被应用过
ls -la ~/.hermes/hermes-agent/run_agent.py.sra-backup
# → 不存在！从未备份/从未安装
```

### Step 3: 检查 force.py 消费端

force.py 定义了 4 级注入点（`on_user_message` / `pre_tool_call` / `post_tool_call` / `periodic`），但：
- daemon.py 中 `ForceLevelManager` 被实例化（line 57）但**仅用于 `/status` 端点返回当前级别名称**
- 没有任何代码根据 force level 触发 SRA 调用
- Hermes 端没有任何 `pre_llm_call` / `pre_tool_call` hook 连接 SRA

### Step 4: 检查 EPIC AC 验证盲区

EPIC-001 的 6 个 AC 全部标记 ✅，但全部只检查 SRA 侧：

```markdown
- [x] Gateway 模式：每次消息自动调 SRA  ← 怎么验证的？只验证了补丁文件存在？
- [x] CLI 模式：每次消息自动调 SRA      ← 同上
- [x] SRA Daemon 不可用时优雅降级        ← 这个确实能验证（SRA 侧）
- [x] should_auto_load≥80 时标记         ← SRA 侧验证
- [x] 所有 38 个现有测试通过             ← SRA 侧测试
- [x] 2 秒超时保护                       ← 在补丁函数中定义，但函数从未被加载
- [x] 模块级缓存                         ← 同上
```

**没有 AC 要求验证 Hermes 端 `run_agent.py` 实际被修改。**

### Step 5: 检查 `sra install hermes` 命令

```python
# cli.py 第 426-467 行
def cmd_install(args):
    agent_type = args[0] if args else "hermes"
    if agent_type == "hermes":
        print("📝 安装 SRA 到 Hermes Agent")
        print("步骤 1: ...")      # 只打印！不执行！
        print("步骤 2: ...")
        adapter = get_adapter("hermes")
        print(adapter.to_system_prompt_block())  # 只输出文本
```

这是一个 **help/print 命令**，不执行任何实际安装。真正的安装入口是 `scripts/install-hermes-integration.sh`。

## 三类文档漂移模式

| 模式 | 特征 | 本案例 |
|:-----|:------|:-------|
| **幻影功能** | 文档描述的代码从未存在过 | `_query_sra_context()` 函数 |
| **幻影集成** | 文档称 A↔B 已连接，实际连接不存在 | force.py → Hermes hook |
| **幻影 AC** | AC 标记 ✅ 但代码未实现 | EPIC-003 Story 1-6 的 Hermes 侧 AC |

## AC 审计增强建议

当前 `scripts/ac-audit.py` 只做：
```
扫描文档中的 [x] 标记 → 统计完成率
```

需要增强为双向一致性检查：
```
┌── 正向漂移: 代码已实现 → 文档未勾选 (现有)
└── 逆向漂移: 文档已勾选 → 代码未实现 (缺失)
```

对于跨项目 AC，还需要验证目标项目的代码存在性。

## 关键文件索引

| 文件 | 说明 |
|:-----|:------|
| `~/projects/sra/patches/hermes-sra-integration.patch` | 从未应用的补丁 |
| `~/projects/sra/scripts/install-hermes-integration.sh` | 从未运行的安装脚本 |
| `~/projects/sra/docs/EPIC-001-hermes-integration.md` | 声称已完成的幻影 Epic |
| `~/projects/sra/docs/EPIC-003-v2-enforcement-layer.md` | 含 11 个虚假 ✅ AC |
| `~/projects/sra/docs/INTEGRATION.md` | 描述不存在的自动注入机制 |
| `~/projects/sra/skill_advisor/cli.py` (line 426-467) | `sra install hermes` = print 语句 |
| `~/projects/sra/skill_advisor/runtime/force.py` | 定义了注入点但无消费者 |
