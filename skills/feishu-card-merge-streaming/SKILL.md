---
name: feishu-card-merge-streaming
description: Feishu 平台进度消息与 LLM 回复合并为单卡片的流式输出方案。涵盖问题诊断、架构分析、代码修改、测试验证全流程。
tags:
  - feishu
  - streaming
  - card
  - progress-merge
---

# Feishu 卡片合并流式输出方案

## 问题描述

Feishu 平台上，工具进度消息（send_progress_messages）和 LLM 回复流（GatewayStreamConsumer）走两条独立路径，发送多张卡片。

## 根因分析

| 流 | 代码路径 | 卡片行为 |
|:---|:---------|:---------|
| 工具进度 | `send_progress_messages()` → `adapter.send()` / `edit_message()` | 独立进度卡片，`__reset__` 信号控制分段 |
| LLM 回复 | `GatewayStreamConsumer.on_delta()` → `_send_or_edit()` | 单卡片累积（仅 `preserve_message_on_break=True` 时） |

**关键文件**：
- `gateway/run.py` — `send_progress_messages()` 内联函数 (~line 12994)
- `gateway/stream_consumer.py` — `GatewayStreamConsumer` 类
- `gateway/platforms/feishu.py` — `send()` / `edit_message()` 实现

## 解决方案

**Feishu 进度合并**：在 `send_progress_messages()` 中检测 Feishu 平台，将进度消息喂入 `GatewayStreamConsumer.on_delta()`。

### 修改点（gateway/run.py）

```
1. _merge_into_stream 检测 (line ~13013)
   └─ if source.platform == Platform.FEISHU and stream_consumer_holder[0]:
          _merge_into_stream = True

2. __dedup__ 分支 (line ~13058)
   └─ if _merge_into_stream: _merge_sc.on_delta(f"> {raw[1]} (×{raw[2] + 1})\n")

3. __reset__ 分支 (line ~13066)
   └─ if _merge_into_stream: continue  # no-op

4. 常规消息分支 (line ~13084)
   └─ if _merge_into_stream: _merge_sc.on_delta(f"> {raw}\n")

5. CancelledError 分支 (line ~13162)
   └─ if _merge_into_stream: drain + return
```

### 核心代码模式

```python
# 在 send_progress_messages() 内部
_merge_into_stream = False
if source.platform == Platform.FEISHU and stream_consumer_holder is not None:
    _merge_sc = stream_consumer_holder[0]
    _merge_into_stream = _merge_sc is not None

# 处理进度消息时
if _merge_into_stream:
    _merge_sc.on_delta(f"> {msg}\n")
    continue  # 跳过正常的进度卡片逻辑
```

## 测试验证

```bash
cd ~/.hermes/hermes-agent
python3 -m pytest tests/gateway/test_stream_consumer_feishu_progress_merge.py -v
```

**4 个测试用例**：
1. `test_all_content_in_single_card` — 进度+LLM+分段都在一张卡片
2. `test_multiple_tool_boundaries` — 多次工具调用仍保持一张卡片
3. `test_compare_with_default_preserve_false` — 对比验证（无合并模式创建多卡片）
4. `test_progress_feeds_via_on_delta` — 模拟 send_progress_messages 喂入进度消息

## 注意事项

- ✅ 修改后需重启网关：`systemctl --user restart hermes-gateway`
- ✅ 不影响非 Feishu 平台（Telegram/Discord/Slack 等）
- ✅ `_merge_into_stream` 检测不依赖配置，自动按平台启用
- ⚠️ 如果 `stream_consumer_holder[0]` 为 None（流消费者未创建），回退传统模式
- ⚠️ `__reset__` 信号在合并模式下完全忽略，不影响卡片累积

## 参考文件

- `skills/feishu/references/card-config.md` — 卡片配置文档
- `gateway/stream_consumer.py` — StreamConsumerConfig 定义
- `tests/gateway/test_stream_consumer_feishu_progress_merge.py` — 测试文件
