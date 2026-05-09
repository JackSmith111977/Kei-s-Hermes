# SRA 技能遵循强制机制设计

## 体系溯源

本文件记录了 2026-05-09 对话中发现的 Hermes 架构关键信息：

**`model_tools.py` 第 679-737 行存在 `handle_function_call()` 函数，其中已内置 `pre_tool_call` 插件钩子系统。** 该钩子可以通过返回 `block_message` 来阻断工具执行。

这意味着 SRA 强制执行机制的注入点已经就绪，无需修改核心循环。

## 三层强制体系

### Layer 1: Pre-message 契约注入（已有）

SRA 在 `run_conversation()` 中注入 `[SRA]` 前缀（`_query_sra_context()`）。
增强方向：在建议后追加结构化任务契约。

### Layer 2: Pre-tool 校验（核心，利用现有 Hook）

`handle_function_call()` 第 722-737 行：
```python
if not skip_pre_tool_call_hook:
    block_message = get_pre_tool_call_block_message(
        function_name, function_args, ...)
    if block_message is not None:
        return json.dumps({"error": block_message})  # 阻断！
```

**注入点**：注册一个 sra-guard 插件到 `pre_tool_call` hook。
**监控工具**：`write_file`, `patch`, `terminal`, `execute_code`
**校验逻辑**：调用 SRA `/validate` API → 获取未加载的推荐 skill → 提醒/阻断

### Layer 3: 长任务上下文保持

每 N 轮对话（如每 5 轮）重新调用 SRA，检测 Agent 是否已漂移。

## 状态追踪

需要在 `AIAgent` 类中新增 `self.loaded_skills = set()` 追踪已加载技能。
在 `skill_view()` 调用后自动记录。

## 与 Bounded Autonomy 关系

| SRA 层 | 对应约束层 | 强制程度 |
|:---|:---|:---:|
| Layer 1 契约 | 约束先行 + 作用域 | 建议（可忽略） |
| Layer 2 校验 | 验证反馈 + 自主决策 | 提醒（不硬阻断） |
| Layer 3 保持 | 时间盒 + 回滚路径 | 提示（防漂移） |

## 实施路线图

| 优先级 | 改动 | 位置 |
|:---:|:---|:---|
| P0 | `/validate` API 端点 | `daemon.py` |
| P0 | `MONITORED_TOOLS` + FILE_SKILL_MAP | 新建 sra-guard 插件 |
| P1 | pre_tool_call hook 注册 | `builtin_hooks/` |
| P1 | loaded_skills 追踪 | `run_agent.py` |
| P2 | 长任务重注入 | `run_agent.py` |
