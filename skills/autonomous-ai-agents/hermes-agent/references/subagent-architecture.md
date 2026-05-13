# Hermes 子代理架构深度分析

> 基于 `tools/delegate_tool.py` (2,562 行) 源码分析
> 日期: 2026-05-12

## 核心发现：子代理不遵循工作流的三个根因

### 根因 1：`skip_context_files=True`

子代理在创建 `AIAgent` 实例时，传入了 `skip_context_files=True`，这意味着：

| 文件 | 父代理加载 | 子代理加载 |
|:-----|:---------:|:---------:|
| SOUL.md | ✅ | ❌ |
| AGENTS.md / .cursorrules | ✅ | ❌ |
| MEMORY.md / USER.md | ✅ | ❌ |
| Skills 知识 | ✅ (手动 skill_view) | ❌ |

代码路径：
- `run_agent.py` — `AIAgent.__init__` 的 `skip_context_files` 参数
- `tools/delegate_tool.py` — `_build_child_agent()` 中构造子代理时传入

### 根因 2：`delegate_task` 无 `skills` 参数

| 工具 | 能否传 Skills？ | 机制 |
|:-----|:-------------:|:-----|
| `cronjob` | ✅ `skills: ["a", "b"]` | 执行前加载 |
| `delegate_task` | ❌ 不支持 | 需父代理手动复制到 `context` |

这是已提出的 Feature Request [#18963](https://github.com/NousResearch/hermes-agent/issues/18963)。

**实际案例**：某研究子代理拿到 `toolsets=["web"]` 后只能搜索不能导航 URL，循环调用了 42 次搜索 API——因为没有 `delegate-task-guide` 技能的指导。

### 根因 3：极简 System Prompt

子代理收到的系统提示词：

```
"You are a focused subagent working on a specific delegated task."

"YOUR TASK:"
{goal}

"CONTEXT:"
{context}

"Complete this task using the tools available to you. ..."
```

相比父代理（SOUL.md + AGENTS.md + MEMORY.md + Skills），子代理几乎空无一物。

## 子代理生命周期

```
父代理调用 delegate_task()
    ↓
_build_child_agent()     ← 在主线程构建（线程安全的构造函数）
    ├─ 继承父代理 credentials（API key, provider, model）
    ├─ 设置受限 toolsets（strip blocked tools）
    ├─ 设置 skip_context_files=True
    └─ 设置 skip_memory=True
    ↓
_build_child_system_prompt()   ← 构建极简 System Prompt
    ↓
ThreadPoolExecutor 中运行     ← 异步执行（默认最多 3 个并行）
    ├─ 独立 Conversation（无父代理历史）
    ├─ 独立 Terminal Session（自己的 task_id）
    └─ 独立 tool call 缓存
    ↓
结果摘要返回父代理           ← 父代理看不到中间步骤
```

## 工具限制

子代理默认被禁止使用（设计上防止副作用泛滥）：

```python
DELEGATE_BLOCKED_TOOLS = {
    "delegate_task",   # 禁止递归委托（leaf 角色时）
    "clarify",          # 不能问用户问题
    "memory",           # 不能写共享记忆
    "send_message",     # 不能发送跨平台消息
    "execute_code",     # 应逐步推理而非写脚本
}
```

**Orchestrator 例外**：当 `role="orchestrator"` 且 `delegation.max_spawn_depth >= 2` 时，子代理保留 `delegate_task`。

## 配置项

```yaml
# ~/.hermes/config.yaml
delegation:
  max_iterations: 50                  # 每个子代理的最大 turns
  max_concurrent_children: 3          # 并行子代理数
  max_spawn_depth: 1                  # 嵌套深度 (1=flat, 2=orchestrator→leaf, 3=三层)
  orchestrator_enabled: true          # 全局开关
  subagent_auto_approve: false        # auto-deny（安全）
  child_timeout_seconds: 600          # 单子代理超时
  inherit_mcp_toolsets: true          # 继承父代理的 MCP 工具
  # 可选——指定子代理使用不同模型/提供商
  model: "google/gemini-3-flash-preview"
  provider: "openrouter"
```

## 建立专用子代理的三种路径

### 路径 A：Context 注入（今天可用）

```python
delegate_task(
    goal="修复测试污染",
    context=f"""
## 🔴 工作流铁律
1. 任务前必须先 skill_finder 查技能
2. 禁止 cp -r 复制仓库目录
3. 修改前 git commit 当前状态
4. 修改后运行全量测试
## 📂 工作路径
{workspace_path}
""",
    toolsets=["terminal", "file"]
)
```

### 路径 B：实现 `delegate_task(skills=[])` — 需 PR #18963

```python
delegate_task(
    goal="分析代码",
    toolsets=["terminal", "file"],
    skills=["sra-dev-workflow", "sdd-workflow"],
)
```

### 路径 C：独立进程 + Profile + Worktree（完全隔离）

```bash
# 1. 创建专用 Profile
hermes profile create sra-worker --clone

# 2. 在 Worktree 中启动子代理
cd ~/projects/sra
hermes -w -p sra-worker -q "修复测试污染"

# 3. tmux 管理多个专用子代理
tmux new-session -d -s worker1 'hermes -w -p sra-worker -q "任务1"'
tmux new-session -d -s worker2 'hermes -w -p sra-worker -q "任务2"'
```

### 对比

| 维度 | Context 注入 | skills 参数 | 独立进程 |
|:-----|:-----------:|:----------:|:-------:|
| 可用性 | ✅ 今天 | ⏳ 需 PR | ✅ 今天 |
| 含 SOUL.md | ❌ 手动 | ❌ 无 | ✅ 完整 |
| 含 AGENTS.md | ❌ 手动 | ❌ 无 | ✅ 完整 |
| 含 Skills | ❌ 手动 | ✅ skill_view | ✅ 完整 |
| 并行能力 | ✅ 内置 | ✅ 内置 | ⏳ 需 tmux |

## 参考文献

- `tools/delegate_tool.py` — 子代理核心实现
- `run_agent.py` — AIAgent `skip_context_files` 参数
- Hermes Docs: [Subagent Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)
- GitHub Issue [#18963](https://github.com/NousResearch/hermes-agent/issues/18963) — Add `skills` parameter to `delegate_task`
- GitHub Issue [#7876](https://github.com/NousResearch/hermes-agent/issues/7876) — `skip_context_files` for cron jobs
- `bmad-party-mode-orchestration` skill — 多 Actor 并行编排
