---
name: feishu-card-merge-streaming
description: Feishu 平台进度消息与 LLM 回复合并为单卡片的流式输出方案。涵盖问题诊断、架构分析、代码修改、测试验证全流程。
tags:
  - feishu
  - streaming
  - card
  - progress-merge
---

# Feishu 卡片流式输出方案（含进度合并回滚记录）

## 问题描述

Feishu 平台上，工具进度消息（send_progress_messages）和 LLM 回复流（GatewayStreamConsumer）走两条独立路径。

## 架构背景

| 流 | 代码路径 | 卡片行为 |
|:---|:---------|:---------|
| 工具进度 | `send_progress_messages()` → `adapter.send()` / `edit_message()` | 独立进度卡片，`__reset__` 信号控制分段 |
| LLM 回复 | `GatewayStreamConsumer.on_delta()` → `_send_or_edit()` | 单卡片累积（仅 `preserve_message_on_break=True` 时） |

**关键文件**：
- `gateway/run.py` — `send_progress_messages()` 内联函数
- `gateway/stream_consumer.py` — `GatewayStreamConsumer` 类
- `gateway/platforms/feishu.py` — `send()` / `edit_message()` 实现

## 官方方案（当前启用）

**两层官方配置**，在 `~/.hermes/config.yaml` 和 `gateway/run.py` 中：

### ① `streaming.enabled: true`

LLM 回复逐字流式输出，通过 `GatewayStreamConsumer` 渐进式编辑同一张卡片。

```yaml
# ~/.hermes/config.yaml
streaming:
  enabled: true
```

### ② `preserve_message_on_break=True`（Feishu 平台专用）

工具调用间的 segment break 不会创建新卡片，而是用 `---` 分隔后继续编辑同一张卡片。

```python
# gateway/run.py (~line 12591)
StreamConsumerConfig(
    preserve_message_on_break=(source.platform == Platform.FEISHU),
    ...
)
```

### 当前行为

```
飞书聊天（官方方案）:
┌─ 卡片 1: LLM 回复（流式更新） ──────┐
│ 文字流式输出...                      │
│ (工具调用间 `---` 分隔)              │
└────────────────────────────────────┘

┌─ 卡片 2: 工具进度（独立） ──────────┐
│ > ⚙️ terminal: "running..."         │
└────────────────────────────────────┘
```

## ❌ 已回滚方案：进度合并（_merge_into_stream）

### 尝试的方案

在 `send_progress_messages()` 中检测 Feishu 平台，将进度消息喂入 `GatewayStreamConsumer.on_delta()`，实现进度+LLM 回复一张卡片。

### 修改点（gateway/run.py，已全部清除）

曾实现 5 处补丁：

```
1. _merge_into_stream 初始化 + Feishu 检测
2. __dedup__ 分支：进度去重消息喂入 on_delta
3. __reset__ 分支：no-op（跳过重置）
4. 常规消息分支：进度消息喂入 on_delta
5. CancelledError 分支：快速清空队列后返回
```

### 回滚原因

**根因**：Context Compaction 打断流式输出 → 飞书空回复。

```
LLM 流式输出中 → 系统触发 Context Compaction → 流式消费者被中断
→ 卡片累积内容丢失 / 响应未 finalize → 飞书收到空卡片
```

合并模式下，进度和 LLM 回复在同一张卡片里，一旦被打断就**全部丢失**。独立卡片模式下，
至少进度卡片和 LLM 卡片不受同一打断影响。

**触发条件**：
- 长对话后自动 Context Compaction（窗口大小触顶）
- Compaction 时机恰好在 `on_delta()` 更新卡片的过程中
- 合并模式下 `preserve_message_on_break=True` 保持卡片存在，但内容尚未推送

### 回滚方法

```bash
# 在 gateway/run.py 中搜索并清除所有 merge_into_stream 相关代码
# 共 5 处，分别在：
#   1. send_progress_messages() 开始处的初始化
#   2. __dedup__ 分支
#   3. __reset__ 分支
#   4. 常规消息分支
#   5. CancelledError 分支

# 验证无残留
grep -r 'merge_into_stream' gateway/run.py || echo "已清除"

# 重启网关生效
systemctl --user restart hermes-gateway
```

### 教训

- **不要将进度和 LLM 回复合并到一张卡片**——它们有不同的生命周期
- 进度消息应保持独立卡片，即使多出一张卡片，也比一次性丢失所有内容好
- Context Compaction 对流式输出的打断是无法预测的，任何合并策略都增加丢失风险
- 官方方案（两张卡片）是最稳健的选择

## 参考文件

- `skills/feishu/references/card-config.md` — 卡片配置文档
- `gateway/stream_consumer.py` — StreamConsumerConfig 定义
- `tests/gateway/test_stream_consumer_feishu_progress_merge.py` — 测试文件
