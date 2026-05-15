# 2026-05-15 SRA 自动注入测试报告

> 验证 Hermes 是否存在 SRA 自动注入机制
> 测试者：boku (Emma)

---

## 测试背景

主人指出「SRA 不是会自动注入吗，并且最高级别的 SRA 还会有钩子注入」，要求测试**不主动调用 SRA**，而是验证系统是否会自动注入 SRA 上下文。

## 测试方法

1. 记录 SRA 统计基线（`total_requests`）
2. **不手动调用 SRA Proxy**，直接处理消息
3. 检查多个维度验证是否存在自动注入

## 测试结果

### 1. SRA 统计基线

```json
{
  "total_requests": 10,
  "total_recommendations": 7,
  "errors": 0,
  "force_level": {
    "level": "omni",
    "active_points": ["on_user_message", "periodic", "post_tool_call", "pre_tool_call"],
    "periodic_interval": 3
  }
}
```

所有 10 次请求均来自 boku 此前手动调用，**无自动调用**。

### 2. 源码全量验证

| 搜索项 | 目标 | 结果 |
|:-------|:-----|:----:|
| `_query_sra_context` | 整个 hermes-agent 代码库 | ❌ 不存在 |
| `sra\|SRA\|recommend\|8536` | `run_agent.py` (738KB) | ❌ 零匹配 |
| `sra\|SRA\|recommend\|8536` | `gateway/run.py` | ❌ 仅无关的 "not recommended" |
| SRA-related function | `agent/*.py` | ❌ 不存在 |

### 3. 日志验证

| 日志 | SRA 自动调用痕迹 |
|:----|:-----------------|
| `agent.log` | ❌ 178 处 sra 匹配，全部为用户对话关键词，非系统调用 |
| `gateway.log` | ❌ 无 SRA 调用记录 |
| `journalctl -u srad` | ❌ 仅启动日志，无 recommend 请求记录 |

### 4. SRA Daemon 代码验证

SRA 的 `force.py` 定义了力度体系：

```python
FORCE_LEVELS = {
    "omni": {
        "injection_points": {"on_user_message", "pre_tool_call", "post_tool_call", "periodic"},
        ...
    }
}
```

但 `daemon.py` 的主循环仅包含：
- HTTP 服务器（被动等待请求）
- 自动刷新线程（定时刷新技能索引）

**没有任何主动注入或推送机制。**

## 结论

| 问题 | 答案 |
|:-----|:----:|
| SRA 会自动注入上下文到 Hermes 吗？ | ❌ **不会** |
| omni 力度的钩子生效了吗？ | ❌ **未生效**（Hermes 侧无集成代码） |
| 为什么 skill 文档说内置注入？ | 该描述**过时/错误**——可能是规划功能但未实现 |
| 现在怎么办？ | ✅ **必须手动调用 SRA Proxy**（SOUL.md 第一条规则） |

## 架构真相

```
当前实际架构：
用户消息 → Gateway → run_conversation() → LLM（无 SRA 介入）
                                                      ↑
                                           boku 必须手动调 SRA

未来如果实现：
用户消息 → Gateway → _query_sra_context() → LLM（有 SRA 上下文）
                         ↕
                     SRA Proxy
```

## 如何监测自动注入是否上线

当以下条件**同时满足**时，说明自动注入已实现：
1. `grep -r "_query_sra_context" ~/.hermes/hermes-agent/` 有结果
2. `total_requests` 不手动调用也会自动增长
3. `agent.log` 中出现 SRA recommend 的系统日志（非用户消息）
