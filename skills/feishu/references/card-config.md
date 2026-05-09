# 飞书消息卡片配置指南

> Hermes 飞书网关的 Interactive Card（JSON 1.0）自动包装机制配置与维护

## 概述

> Hermes 飞书网关（`gateway/platforms/feishu.py`）**自动**将所有出站文本消息包装为飞书 Interactive Card。无需额外配置即可生效。

## 最新更新（2026-05-09）

### v2.1 — 动态标题摘要
- 卡片标题现在**自动从内容中提取摘要**，不再是固定的"🐱 小玛"
- 提取优先级：Markdown 标题（#/##/###）→ 首行非空文本 → 默认"🐱 小玛"
- 标题最长 50 字符，超出截断+省略号

### v2.1 — 流式编辑支持
- `FeishuAdapter` 现已声明 `SUPPORTS_MESSAGE_EDITING = True`
- 启用 `streaming.enabled: true` 后，飞书消息将使用 `GatewayStreamConsumer` 渐进式编辑
- 首条消息通过 `send()` 创建，后续内容通过 `edit_message()` 更新同一卡片
- 支持 `finalize` 参数控制卡片完成状态

### v2.2 — 跨工具调用段保留卡片（2026-05-09）

**问题**：多工具调用时，每条 LLM 回复段变成独立卡片。

**根因**：`gateway/run.py` → `stream_delta_callback(None)` → `GatewayStreamConsumer.on_segment_break()` → `_reset_segment_state()` 清空 `_message_id`，导致后续文本创建新卡片。

**修复方案**（修改 `gateway/stream_consumer.py` + `gateway/run.py`）：

在 `StreamConsumerConfig` 新增 `preserve_message_on_break: bool = False`。当为 `True` 时：

```python
# segment break 时不清空 _message_id 和 _accumulated
# 而是添加视觉分隔线后继续编辑同一卡片
self._accumulated = (self._accumulated or "").rstrip() + "\n\n---\n\n"
self._last_sent_text = ""
# _message_id 保持不变 → 后续继续 edit_message()
```

对 Feishu 平台启用：`preserve_message_on_break=(source.platform == Platform.FEISHU)`

**效果**：整个对话回合的所有 LLM 文本累积在**同一张卡片**中，工具调用间用 `---` 分隔。

## 核心配置位置

**文件**：`~/.hermes/hermes-agent/gateway/platforms/feishu.py`

### 关键函数

| 函数 | 行号 | 说明 |
|------|------|------|
| `_build_outbound_payload()` | ~3675 | 入口：判断内容类型，自动调用卡片构建函数 |
| `_build_markdown_card_payload()` | ~509 | Markdown 内容 → 交互式卡片 |
| `_build_text_card_payload()` | ~546 | 纯文本内容 → 简化卡片 |

## 卡片结构

### Markdown 卡片模板

```json
{
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "🐱 小玛"},
    "template": "blue"
  },
  "elements": [
    {"tag": "markdown", "content": "消息内容..."}
  ]
}
```

### 模板颜色自动选择

根据内容前 300 字符的语气自动选择：

| 触发词 | 模板颜色 |
|--------|----------|
| ⚠️ / ❌ / error: / failed: | `red` |
| ⚠ / warning: / caution | `orange` |
| 默认（无触发词） | `blue` |

## 错误处理

- `_INTERACTIVE_CONTENT_INVALID_RE`（~130 行）— 正则检测常见卡片错误
- 发送失败时自动降级为普通文本消息（~1511-1521 行）
- 降级后不会丢失消息内容

## 流式输出与卡片编辑机制

### 数据流链路（Feishu 已合并模式）

```
用户消息
  → gateway/run.py
    → 创建 GatewayStreamConsumer（如果 streaming.enabled=true）
    → 创建 send_progress_messages() 后台任务（工具进度条）
    
    ┌─ Feishu 合并模式 ─────────────────────────────────────┐
    │                                                       │
    │  工具进度消息            LLM 流式输出                   │
    │  (send_progress)         (stream_delta_callback)       │
    │       │                          │                     │
    │       ▼                          ▼                     │
    │  ┌──────────────────────────────────────┐             │
    │  │  GatewayStreamConsumer.on_delta()     │             │
    │  │  → 累积到 _accumulated               │             │
    │  │  → _send_or_edit() 编辑同一卡片       │             │
    │  └──────────────────────────────────────┘             │
    │                         │                              │
    │                         ▼                              │
    │             一张卡片，包含所有内容                       │
    │         (进度消息 + LLM 回复 + --- 分段)                │
    └────────────────────────────────────────────────────────┘
    
    ┌─ 非 Feishu（传统模式）──────────────────────────┐
    │                                                  │
    │  工具进度流 → 单独进度卡片 (编辑)    │
    │  LLM 回复流 → LLM 回复卡片 (流式)    │
    │                                                  │
    │  用户看到：多张卡片                               │
    └──────────────────────────────────────────────────┘
```

### 三条路径对比

| 路径 | 行为 | 卡片数量 |
|:---|:-----|:--------|
| **非 Feishu**（preserve_message_on_break=False） | 每次工具调用创建新卡片 | 多张 |
| **Feishu v2.2**（仅 preserve_message_on_break=True） | LLM 回复累积一张卡片，进度单独一张 | 2 张 |
| **Feishu v3.0 合并模式**（preserve_message_on_break=True + 进度合并） | 所有内容（进度+LLM）累积到一张卡片 | **1 张** |

### Feishu 专用：一条合并卡片流

| 流 | 负责人 | Feishu 卡片角色 |
|:---|:-------|:---------------|
| **统一回复流** | `GatewayStreamConsumer`（接收 send_progress_messages 喂入的进度消息） | 单卡片：进度消息 + LLM 回复累积编辑 |

**关键配置**：`preserve_message_on_break=True` + Feishu 平台自动启用进度合并（`_merge_into_stream`）。

**进度消息前缀**：进度消息以 `> ` 前缀喂入流消费者，在卡片中与 LLM 回复视觉区分。

### 关键文件

| 文件 | 角色 |
|:-----|:-----|
| `gateway/stream_consumer.py` | 流式消费者：累积文本、编辑卡片、处理 segment break |
| `gateway/run.py` | 网关主流程：创建消费者、编排进度消息、调用 agent |
| `gateway/platforms/feishu.py` | Feishu 适配器：send_message() / edit_message() 实现 |

## 维护指南

### 修改卡片标题
编辑 `_build_markdown_card_payload()` 中 `"content": "🤖 Hermes"` 为想要的内容。

### 修改颜色逻辑
编辑 header_template 的选择逻辑（`feishu.py ~522-526`），添加或修改触发词和对应的颜色。

### 添加更多卡片元素
在 `elements` 数组中添加新的 tag 元素：
```python
"elements": [
    {"tag": "markdown", "content": content},
    {"tag": "hr"},  # 分割线
    {"tag": "note", "elements": [{"tag": "plain_text", "content": "备注信息"}]}
]
```

### 修改卡片配置
编辑 `config` 字段，如 `wide_screen_mode`、`enable_forward` 等。

### 完全禁用卡片
修改 `_build_outbound_payload()`，直接返回 `("text", content)` 而非调用卡片函数。
### 调整 segment break 行为

Feishu 使用 `preserve_message_on_break=True` 在工具调用间保留卡片。
如需启用新卡片（如清理过长积累），设置 `preserve_message_on_break=False`。
修改点在 `gateway/run.py` 的两个 `StreamConsumerConfig(...)` 创建处。

### Feishu 进度合并模式（v3.0）

**行为**：Feishu 平台上，工具进度消息被喂入 `GatewayStreamConsumer`，与 LLM 回复累积到同一张卡片中。

**实现文件**：`gateway/run.py` → `send_progress_messages()` 内部函数

**代码**：在 `send_progress_messages()` 中：
1. 检测 `source.platform == Platform.FEISHU` 且 `stream_consumer_holder[0]` 存在
2. 设置 `_merge_into_stream = True`
3. 进度消息、去重消息通过 `_merge_sc.on_delta(f"> {msg}\n")` 喂入流消费者
4. `__reset__` 信号在合并模式下是空操作（no-op）
5. 取消（CancelledError）时快速清空队列后返回

**前缀格式**：`> ⚙️ tool_name: "preview"` — `> ` 前缀使进度内容在卡片中视觉区分。

**禁用方法**：在 Feishu 适配器中移除 `_merge_into_stream` 逻辑，或通过 `display.tool_progress` 配置关闭工具进度。

### 重启生效
修改 `feishu.py`、`stream_consumer.py`、`run.py` 后需要**重启飞书网关服务**才能生效。

## 飞书卡片 API 参考

- 消息类型：`msg_type: "interactive"`
- 内容格式：JSON 1.0（飞书卡片协议）
- 支持元素：markdown、plain_text、hr、note、button、image 等
- 接口：`POST /open-apis/im/v1/messages`
- 大小限制：卡片 JSON 序列化后一般不超过 100KB

## 常见问题

**Q：卡片发送失败怎么办？**
A：系统会自动降级为文本消息。查看飞书网关日志可以找到具体错误原因。

**Q：如何调试卡片格式？**
A：在飞书开发者后台的「卡片调试工具」中粘贴卡片 JSON 预览效果。

**Q：为什么工具调用后 LLM 回复变成了新卡片？**
A：这是早期的 segment break 默认行为——`_reset_segment_state()` 清空 `_message_id` 导致新卡片。
已在 v2.2 修复：新增 `preserve_message_on_break` 配置，对 Feishu 启用后所有段累积到同一卡片。

**Q：每次工具调用后卡片中的 `---` 分隔线是什么？**
A：`preserve_message_on_break=True` 时，segment break 在累积文本中插入 `\n\n---\n\n` 作为视觉分段标记。
这是为了保留工具调用的上下文边界，方便阅读。
