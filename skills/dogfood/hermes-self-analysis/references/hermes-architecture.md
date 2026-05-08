# Hermes Agent 架构全景 (v2.0)

## 项目规模
- **Python 文件**: 1,464 个
- **总代码行数**: 707,214 行
- **测试**: ~17K 测试 / ~900 测试文件

## 8 层架构

```
Layer 1 (P0): 核心运行时    — run_agent.py / cli.py / batch_runner.py
Layer 2 (P0): 网关平台      — gateway/ (飞书/微信/Telegram 等 20+ 平台)
Layer 3 (P1): 工具系统      — tools/ (72 个工具文件 / 7 种终端后端)
Layer 4 (P1): 插件生态      — plugins/ (15 个插件目录)
Layer 5 (P2): 数据状态      — hermes_state.py / Memory API
Layer 6 (P2): 基础设施      — cron/ / acp_adapter/ / ui-tui/ / checkpoints
Layer 7 (P3): 运行环境      — local / docker / ssh / modal / singularity
Layer 8 (P3): 测试系统      — tests/ (17K 测试)
```

## 核心文件

| 文件 | 行数 | 核心类/功能 |
|:---|:---:|:---|
| `run_agent.py` | 14,471 | AIAgent ~60 参数 init / 对话循环 / 工具调用 |
| `cli.py` | 12,508 | HermesCLI / 36+ 命令 / prompt_toolkit TUI |
| `gateway/run.py` | 15,059 | GatewayRunner / 平台适配器生命周期 |
| `hermes_state.py` | 2,669 | SessionDB / SQLite + FTS5 |
| `tools/registry.py` | 537 | ToolRegistry / 工具注册与调度 |
| `model_tools.py` | 847 | 工具编排 / toolset 管理 |

## AIAgent 核心设计模式

| 模式 | 位置 | 说明 |
|:---|:---:|:---|
| 懒加载 OpenAI SDK | run_agent.py:40-86 | 延迟导入 ~240ms，守护进程不崩溃 |
| 迭代预算 | run_agent.py:272-312 | 父子代理共享 max_iterations |
| SRA 上下文注入 | run_agent.py:10802 | 消息前插入技能推荐 |
| 上下文压缩 | run_agent.py:10865+ | 长对话自动压缩中间轮次 |
| 插件钩子 | run_agent.py:10912+ | pre_llm_call / on_session_start |
| Fallback 链 | run_agent.py:~10660 | 主模型失败自动降级 |
| Tool Guardrails | agent/tool_guardrails.py | 工具调用安全护栏 |
| Checkpoints | 内置 | 文件变更前快照，/rollback 回滚 |

## CLI 命令列表 (36+)

/help, /quit, /profile, /tools, /toolsets, /config, /clear, /new, /resume,
/model, /retry, /history, /title, /rollback, /snapshot, /stop, /agents,
/paste, /copy, /image, /branch, /gquota, /personality, /cron, /curator,
/kanban, /skills, /background, /browser, /goal, /skin, /footer,
/reasoning, /busy, /fast, /debug

## 工具调用三种模式
- **顺序执行**: `_execute_tool_calls_sequential` — 可靠
- **并行执行**: `_execute_tool_calls_concurrent` — 性能优先
- **自动选择**: `_execute_tool_calls` — 根据配置

## 7 种终端后端
local, docker, ssh, singularity, modal, daytona, vercel_sandbox

## 20+ 平台适配器
telegram, discord, slack, whatsapp, signal, matrix, mattermost, email, sms,
dingtalk, feishu, wecom, weixin, bluebubbles, qqbot, homeassistant, webhook,
api_server, yuanbao

## 4 种 API Mode
chat_completions, codex_responses, anthropic_messages, bedrock_converse
