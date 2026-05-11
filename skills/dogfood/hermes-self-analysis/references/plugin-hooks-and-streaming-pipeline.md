# Hermes 插件钩子系统与流式输出管线

> 基于 2026-05-11 源码审计。涵盖 VALID_HOOKS 清单、输出数据流、钩子 gap 分析。

---

## 一、插件钩子系统

### 1.1 定义位置

| 文件 | 行号 | 内容 |
|------|:----:|------|
| `hermes_cli/plugins.py` | L78 | `VALID_HOOKS: Set[str]` 集合定义 |
| `hermes_cli/plugins.py` | L597 | `PluginManager` 类：发现/加载/调用 |
| `hermes_cli/plugins.py` | L1184 | `discover_plugins()` 入口函数 |
| `hermes_cli/plugins.py` | L534 | `register_hook()` 校验钩子名 |

### 1.2 完整 VALID_HOOKS 清单

```python
VALID_HOOKS: Set[str] = {
    # ─── 工具生命周期 ──────────────────────────────────
    "pre_tool_call",             # 工具执行前。kw: tool_name, args, task_id
    "post_tool_call",            # 工具执行后。kw: +result
    
    # ─── LLM 调用生命周期（每次 LLM API 调用，非逐 token）───
    "pre_llm_call",              # LLM 调用前。kw: session_id, user_message, conversation_history, is_first_turn, model
    "post_llm_call",             # LLM 调用后。kw: +assistant_response
    
    # ─── API 请求 ──────────────────────────────────────
    "pre_api_request",           # API 请求前
    "post_api_request",          # API 请求后
    
    # ─── 结果转换 ──────────────────────────────────────
    "transform_terminal_output", # 终端输出转换
    "transform_tool_result",     # 工具结果转换
    
    # ─── 会话生命周期 ──────────────────────────────────
    "on_session_start",          # 会话开始
    "on_session_end",            # 会话结束
    "on_session_finalize",       # 会话最终化
    "on_session_reset",          # 会话重置
    
    # ─── 子代理 ────────────────────────────────────────
    "subagent_stop",             # 子代理停止
    
    # ─── 网关入站拦截 ──────────────────────────────────
    "pre_gateway_dispatch",      # 网关收到用户消息后、auth+分发前
                                 # 返回值: {"action": "skip"|"rewrite"|"allow", ...}
                                 # kw: event, gateway, session_store
    
    # ─── 审批流程 ──────────────────────────────────────
    "pre_approval_request",      # 风险操作审批前。kw: command, description, pattern_key, surface
    "post_approval_response",    # 审批响应后。kw: +choice
}
```

### 1.3 钩子调用规范

```python
# 调用方式（所有钩子统一入口）
from hermes_cli.plugins import invoke_hook

results = invoke_hook("hook_name", **kwargs)
# 返回值：list[Any]  — 所有非 None 的回调返回值聚合
# 异常：不会传播 — 每个回调被 try/except 包裹
# 返回值用途：pre_gateway_dispatch 用 action dict 控制流程，
#             其他钩子的返回值通常被忽略（仅用于观察）
```

### 1.4 插件文件结构

```
~/.hermes/plugins/<plugin-name>/
├── plugin.yaml          # 清单：name, kind(standalone|backend|platform|exclusive), description
└── main.py              # 入口：def register(ctx) → ctx.register_hook(...)

# 用户插件存放在 ~/.hermes/plugins/（自动发现）
# 项目插件存放在 ./.hermes/plugins/（需 HERMES_ENABLE_PROJECT_PLUGINS=1）
```

### 1.5 启用/禁用

```bash
hermes plugins enable  <name>   # 启用
hermes plugins disable <name>   # 禁用
hermes plugins list             # 列出所有插件
```

---

## 二、流式输出管线

### 2.1 数据流全链路

```
┌─ AIAgent.run_conversation() ─────────────────────┐
│                                                    │
│  LLM API 逐 token 返回                              │
│    → stream_delta_callback(text)    ← 每个 token   │
│    → interim_assistant_callback()   ← 工具间注释    │
│    → step_callback()                ← 每步回调     │
│                                                    │
└──────────────────────┬─────────────────────────────┘
                       │
                       ▼
┌─ gateway/run.py ──────────────────────────────────┐
│                                                     │
│  _stream_delta_cb(text):  ← (L13394)               │
│     if _run_still_current():                        │
│         _stream_consumer.on_delta(text)             │
│                                                     │
│  _interim_assistant_cb(text):  ← (L13401)           │
│     _stream_consumer.on_commentary(text)             │
│                                                     │
└──────────────────────┬─────────────────────────────┘
                       │
                       ▼
┌─ GatewayStreamConsumer (stream_consumer.py) ──────┐
│                                                     │
│  on_delta(text):              ← 线程安全，同步调用   │
│     → self._queue.put(text)   ← 入 asyncio 队列     │
│                                                     │
│  run():                        ← async 后台任务      │
│     while True:                                      │
│         item = await get()    ← 从队列取             │
│         self._accumulated += text                    │
│         if 超缓冲阈值 / 超编辑间隔:                   │
│             self._send_or_edit()                     │
│         if item is _DONE: break                      │
│                                                     │
│  _send_or_edit():                                    │
│     if self._message_id is None:                     │
│         self._message_id = adapter.send(...)         │
│     else:                                            │
│         adapter.edit_message(...)                     │
│                                                     │
│  finish():                     ← 流完成信号          │
│     self._queue.put(_DONE)                           │
│                                                     │
│  on_segment_break():          ← 工具调用边界         │
│     preserve_message_on_break=True 时:               │
│       累积 "---" 分隔后继续编辑同一卡片               │
│     preserve_message_on_break=False 时:              │
│       清空 _message_id → 后续内容发新卡片             │
│                                                     │
└──────────────────────┬─────────────────────────────┘
                       │
                       ▼
┌─ Platform Adapter (如 feishu.py) ─────────────────┐
│                                                     │
│  FeishuAdapter.send()                               │
│     → POST /open-apis/im/v1/messages                │
│     → 返回 message_id                               │
│                                                     │
│  FeishuAdapter.edit_message()                        │
│     → PATCH /open-apis/im/v1/messages/{message_id}  │
│     → 更新卡片内容                                   │
│                                                     │
│  SUPPORTS_MESSAGE_EDITING = True  ← 声明支持编辑    │
│  REQUIRES_EDIT_FINALIZE = False   ← 无需显式 finalize│
└─────────────────────────────────────────────────────┘
```

### 2.2 关键配置项

| 配置 | 位置 | 说明 |
|------|------|------|
| `streaming.enabled: true` | `config.yaml` | 启用流式输出 |
| `streaming.edit_interval: 1.0` | `StreamConsumerConfig` | 编辑间隔（秒） |
| `streaming.buffer_threshold: 40` | `StreamConsumerConfig` | 缓冲字符数触发编辑 |
| `streaming.cursor: " ▉"` | `StreamConsumerConfig` | 光标字符 |
| `preserve_message_on_break=True` | `gateway/run.py` L12591 | Feishu 专用：工具调用间保持同一卡片 |
| `fresh_final_after_seconds: 0` | `StreamConsumerConfig` | Telegram 专用：最终消息新鲜度 |

### 2.3 三种卡片模式对比

| 模式 | 配置 | LLM 输出 | 工具进度 | 卡片数 |
|------|------|----------|----------|:------:|
| 传统模式 | 默认 | 每段新卡片 | 独立进度卡片 | 多张 |
| Feishu v2.2 | `preserve_message_on_break=True` | 同一张卡片累积 | 独立进度卡片 | 2 张 |
| Feishu v3.0（已回滚） | + `_merge_into_stream` | 同一张卡片累积 | 合并到同一张 | **1 张** |

---

## 三、钩子 Gap 分析

### 3.1 现有钩子的覆盖范围

```
入站方向（用户 → Agent）:
  pre_gateway_dispatch  ✅  可拦截/改写/跳过用户消息

Agent 内部:
  pre_llm_call / post_llm_call      ✅  每个 LLM API 调用
  pre_tool_call / post_tool_call    ✅  每个工具调用
  pre_api_request / post_api_request ✅  每个外部 API 请求

出站方向（Agent → 用户）:
  ❌ 没有任何钩子可以拦截流式输出的 token
  ❌ 没有任何钩子可以拦截平台适配器发出的消息
  ❌ 没有任何钩子可以修改/增强卡片内容
```

### 3.2 需要新增的钩子（如果需要插件式输出拦截）

```python
# 建议新增到 VALID_HOOKS 的钩子
"post_stream_delta",           # 流式输出段。kw: text, session_id, platform, chat_id
                               # 返回值: {"text": "..."} 可改写内容
"post_stream_segment",         # 段结束（工具边界）。kw: segment_type, accumulated
"post_stream_finalize",        # 流完成。kw: full_text, session_id
```

### 3.3 新增位置

| 位置 | 代码 | 说明 |
|------|------|------|
| `gateway/run.py` L13394 | `_stream_delta_cb` 中调用 | 捕获每个 token |
| `gateway/stream_consumer.py` | `on_segment_break()` 中 | 捕获段边界 |
| `gateway/stream_consumer.py` | `finish()` 中 | 捕获流完成事件 |

---

## 四、Context Compaction 对流式输出的影响

### 4.1 问题描述

Context Compaction（上下文压缩）是 Hermes 在 token 窗口接近上限时自动触发的压缩机制。在流式输出过程中触发 Compaction 会导致：

1. `GatewayStreamConsumer` 的后台 asyncio 任务被中断
2. `_accumulated` 累积内容丢失
3. `edit_message()` 调用未 finalize → 飞书收到空/不完整卡片
4. 用户看到空白或不完整的回复

### 4.2 触发条件

- 长对话后 token 窗口 > 50%
- Compaction 时机恰好在 `on_delta()` 更新卡片的过程中
- 单卡片累积模式（`preserve_message_on_break=True`）下损失更大

### 4.3 缓解策略

1. **本地 Checkpoint**：每 200 字符保存一次累积内容到本地文件
2. **自动降级**：检测到异常后回退到双卡片模式（最稳健）
3. **心跳检测**：定期发送心跳 token 保持流活跃

---

## 五、实现插件式输出拦截的四种方案

| 方案 | 侵入性 | 优点 | 缺点 | 推荐场景 |
|:----|:------:|------|------|---------|
| **A: StreamConsumer 注入** | 低 | 不改 VALID_HOOKS，5 行代码 | 不是插件架构 | 快速验证 |
| **B: 新增 post_stream_delta 钩子** | 中 | 真正的插件架构，可扩展 | 需修改核心 3 个文件 | 生产推荐 |
| **C: 自定义 FeishuAdapter** | 低 | 不改核心，完全控制卡片 | 仅限 Feishu | 飞书专用 |
| **D: SSE 反向代理** | 高 | 完全独立 | 仅限 API Server 模式 | 特殊场景 |

详见 `feishu-card-merge-streaming` skill 中的回滚记录和教训总结。
