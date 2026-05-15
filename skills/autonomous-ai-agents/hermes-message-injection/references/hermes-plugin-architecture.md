# Hermes 插件架构指南 — sra-guard 模式

> **来源**: EPIC-004 Phase 0 (2026-05-15)
> **用途**: 未来将 SRA 功能注入到 Hermes 时的参考架构

---

## 核心模式：用 `importlib` 处理连字符目录名

Hermes 插件目录名使用连字符（如 `sra-guard`、`disk-cleanup`），
Python 不能直接用 `import` 从连字符目录导入模块。

**解决方案**：在 `__init__.py` 中使用 `importlib` 从文件路径加载：

```python
import importlib.util
from pathlib import Path

def _get_client():
    global _client
    if _client is None:
        client_path = Path(__file__).parent / "client.py"
        spec = importlib.util.spec_from_file_location(
            "sra_guard.client", str(client_path)
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _client = mod.SraClient()
    return _client
```

## 插件注册模式

所有 Hermes 插件通过 `plugin.yaml` + `register(ctx)` 函数注册：

### plugin.yaml

```yaml
name: sra-guard
version: 0.1.0
description: "描述"
author: "作者"
hooks:
  - pre_llm_call        # 声明使用的 hook
```

### register() 函数

```python
def register(ctx) -> None:
    """Hermes 插件系统自动调用"""
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
    ctx.register_command("name", handler=fn, description="...")
```

## pre_llm_call hook 模式

用于在每次 LLM 调用前注入上下文。**最适合 SRA 技能推荐的钩子**。

```python
def _on_pre_llm_call(messages, session_id, **kwargs):
    """在 LLM 调用前触发。

    Args:
        messages: 当前对话消息列表
        session_id: 当前会话 ID

    Returns:
        dict | None:
          - {"context": "..."} → Hermes 注入到 user_message 前
          - None → 不注入
    """
    try:
        if not messages or not isinstance(messages, list):
            return None
        last = messages[-1]
        if not isinstance(last, dict) or last.get("role") != "user":
            return None
        text = last.get("content", "")
        if not text:
            return None

        # 调用 SRA Daemon
        client = _get_client()
        if client is None:
            return None

        ctx = client.recommend(text)
        if ctx:
            return {"context": ctx}
    except Exception:
        logger.warning("异常", exc_info=True)
    return None
```

## 双协议 SRA 通信客户端

HTTP (httpx) 优先，Unix Socket 降级：

```python
class SraClient:
    def __init__(self, http_url="http://127.0.0.1:8536",
                 socket_path="~/.sra/srad.sock", timeout=2.0): ...

    def recommend(self, message): ...   # POST /recommend
    def validate(self, tool, args): ... # POST /validate
    def record(self, skill, action): ...# POST /record
    def health(self): ...               # GET /health

    def _request(self, endpoint, payload):
        # HTTP 优先
        result = self._request_http("POST", endpoint, payload)
        if result is not None:
            return result
        # Socket 降级
        return self._request_socket(endpoint, payload)
```

## 源码管理原则

```
~/projects/sra/plugins/sra-guard/          ← 源码（git 管理）
    ├── plugin.yaml
    ├── __init__.py
    ├── client.py
    └── tests/

~/.hermes/hermes-agent/plugins/sra-guard/  ← 部署（安装脚本复制）
```

**不要直接在目标部署目录创建源码。** 安装脚本来做部署。

## Hermes 可用 Hook 清单

| Hook | 触发时机 | 适合场景 | 返回值 |
|:-----|:---------|:---------|:-------|
| `pre_llm_call` | LLM 调用前 | 注入 SRA 推荐上下文 | `{"context": "str"}` \| None |
| `pre_tool_call` | 工具执行前 | 校验技能加载 | `{"action": "block", "message": ""}` \| None |
| `post_tool_call` | 工具执行后 | 记录技能使用 | None |
| `on_session_start` | 会话开始时 | 初始化 SRA session | None |
| `on_session_end` | 会话结束时 | 清理 SRA session | None |
