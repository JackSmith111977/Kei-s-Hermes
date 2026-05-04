---
name: hermes-message-injection
description: "向 Hermes Agent 的消息管道注入外部服务上下文（如 SRA 技能推荐）。每次用户消息自动拦截 → 调外部服务 → 将结果作为 [前缀] 注入到消息前。涵盖 run_agent.py 的 run_conversation() 注入点、module-level 缓存、降级策略。"
version: 1.0.0
triggers:
  - hermes 注入
  - hermes 消息拦截
  - message injection
  - sra integration
  - context injection
  - hermes hook
  - run_conversation
  - 消息前置推理
  - 上下文注入
depends_on:
  - hermes-agent
design_pattern: Pipeline Injection
skill_type: Pattern
---

# Hermes Message Injection — 消息管道上下文注入模式

## 问题

需要让每个用户消息在进入 LLM 前自动调外部服务（如 SRA 技能推荐、安全检查、内容过滤等），把结果注入到系统提示或消息中。

## 不可行的方案（已试错）

### 方案 A: AGENTS.md / SOUL.md 文档规则
- 文件中的规则是"劝告式"的，Agent 可能忽略
- 上下文压缩会裁剪掉规则
- 不同模型遵守程度不同
- **结论：不可靠**

### 方案 B: Gateway Hook 系统 (`agent:start` 事件)
- Hermes 自带的 Hook 系统 (`gateway/hooks.py`) 支持注册事件处理器
- Hook 是**异步非阻塞**的——错误被 catch 但不会阻塞消息
- Hook handler **不能修改消息内容或 system prompt**
- **结论：只能触发副作用（写日志/写文件），不能注入上下文**

### 方案 C: 改 `_build_system_prompt()` 或 `prompt_builder.py`
- `_build_system_prompt()` 在整个 session 中**只调用一次**并缓存（见第 3933 行注释）
- 后续 `run_conversation()` 调用复用缓存的 system prompt
- 后续消息不会触发外部服务查询
- **结论：只对第一轮消息有效**

## 最终方案: 改 `run_conversation()` 入口

### 原理

`AIAgent.run_conversation()` 是**每轮消息的唯一入口**——CLI 和 Gateway 都走这个函数。

在第 8677 行 `user_msg = {"role": "user", "content": user_message}` 之前插入拦截逻辑：

```
用户消息 → run_conversation(msg)
              ↓
          调外部服务 HTTP API
              ↓
          将结果作为 [TAG] 前缀注入到 msg 前
              ↓
          user_msg = {"role": "user", "content": "[TAG] ... \n\n原始消息"}
              ↓
          API call → LLM 感知上下文 → 回复
```

### 注入点（需改 run_agent.py）

在 `run_conversation()` 方法中，找到 `# Add user message` 注释，在其前插入：

```python
# ── External Service Context Injection ──────────────────────────
# Query external service and inject as prefix to user message.
# Runs on EVERY turn. Silent on failure.
_service_ctx = _query_service_context(user_message)
if _service_ctx:
    user_message = f"{_service_ctx}\n\n{user_message}"
# ────────────────────────────────────────────────────────────────

# Add user message
user_msg = {"role": "user", "content": user_message}
messages.append(user_msg)
```

### Module-level 函数模板

在 `class AIAgent` 定义之前插入：

```python
_SERVICE_CACHE: dict = {}


def _query_service_context(user_message: str) -> str:
    """Query external service and return formatted context prefix.

    Called on every conversation turn.  Uses MD5 hash cache to avoid
    redundant queries during retries. Returns empty string on failure.
    """
    import urllib.request
    import json as _json
    import hashlib

    service_url = os.environ.get("SERVICE_URL", "http://127.0.0.1:8536/recommend")

    _msg_hash = hashlib.md5(user_message.encode("utf-8")).hexdigest()[:12]
    if _SERVICE_CACHE.get("last_hash") == _msg_hash:
        return _SERVICE_CACHE.get("last_result", "")

    try:
        req = urllib.request.Request(service_url, method="POST")
        payload = _json.dumps({"message": user_message}).encode("utf-8")
        req.data = payload
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = _json.loads(resp.read().decode("utf-8"))

        context = data.get("context", "") or data.get("rag_context", "")
        if not context:
            _SERVICE_CACHE.update(last_hash=_msg_hash, last_result="")
            return ""

        result = f"[SERVICE] 外部推荐:\n{context}"[:2500]

        _SERVICE_CACHE.update(last_hash=_msg_hash, last_result=result)
        return result

    except Exception:
        _SERVICE_CACHE.update(last_hash=_msg_hash, last_result="")
        return ""
```

## 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| **注入点** | `run_conversation()` 中 `# Add user message` 前 | 每轮消息触发，覆盖 CLI + Gateway |
| **注入方式** | 前缀注入到 user_message，不修改 system prompt | 不破坏 prompt caching |
| **缓存** | module-level dict，MD5 hash 做 key | 避免 retry 时重复 HTTP 调用 |
| **超时** | 2 秒 | 快速失败，不阻塞消息 |
| **降级** | try/except 全 catch，返回空字符串 | 服务不可用时不影响正常对话 |

## 搜索助手

```bash
# 找到注入点
grep -n "# Add user message" ~/.hermes/hermes-agent/run_agent.py

# 找到 class AIAgent 之前的位置（插入模块函数）
grep -n "^class AIAgent" ~/.hermes/hermes-agent/run_agent.py
```

## 验证方法

```bash
cd ~/.hermes/hermes-agent
source venv/bin/activate
python3 -c "
import sys; sys.path.insert(0, '.')
from run_agent import _query_service_context
result = _query_service_context('测试消息')
print('注入成功' if result else '无注入内容')
"
```

## 与 Hook 系统的关系

| 机制 | 触发时机 | 是否阻塞 | 能否改消息 |
|------|---------|---------|-----------|
| `agent:start` Hook | LLM 处理前 | 异步非阻塞 | 不能 |
| `run_conversation()` 注入 | 消息入队列前 | 同步阻塞 | 能修改 |

两个机制**互补**：Hook 用于日志/监控等副作用，`run_conversation()` 注入用于实际修改消息内容。
