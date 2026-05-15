# Hermes Plugin Hooks API

> 来源: Hermes `hermes_cli/plugins.py` + 测试文件 (`tests/test_model_tools.py`, `tests/hermes_cli/test_plugins.py`)
> 更新: 2026-05-15

## 可用 Hooks

`VALID_HOOKS` 定义于 `hermes_cli/plugins.py:78`：

- `pre_tool_call` — 工具调用前，可阻断
- `post_tool_call` — 工具调用后，观察性
- `transform_tool_result` — 工具结果转换
- `transform_terminal_output` — 终端输出转换
- `pre_llm_call` — LLM 调用前，可注入上下文
- `post_llm_call` — LLM 调用后
- `pre_api_request` — API 请求前
- `post_api_request` — API 请求后
- `on_session_start` — 会话开始
- `on_session_end` — 会话结束
- `on_session_finalize` — 会话终结
- `on_session_reset` — 会话重置
- `pre_gateway_dispatch` — Gateway 分发前
- `subagent_stop` — 子代理停止

## 回调签名

### pre_llm_call (Phase 1: 上下文注入)

```python
def on_pre_llm_call(
    messages: list,          # 对话消息列表 [{"role": ..., "content": ...}, ...]
    session_id: str,
    **kwargs
) -> dict | None:
    """
    返回值:
      {"context": "..."}  → 注入到 user message 前
      None                → 不注入
    """
```

### post_llm_call

```python
def on_post_llm_call(
    messages: list,
    response: str,
    session_id: str,
    **kwargs
) -> None:
    """观察性，返回值被忽略"""
```

### pre_tool_call (Phase 2: 工具校验)

```python
def on_pre_tool_call(
    tool_name: str,          # "write_file", "patch", "web_search"...
    args: dict,              # 工具参数字典
    task_id: str,
    session_id: str,
    tool_call_id: str,
    **kwargs
) -> dict | None:
    """
    返回值:
      {"action": "block", "message": "..."}  → 阻断工具执行
      None                                    → 放行
    """
```

### post_tool_call (Phase 3: 轨迹追踪)

```python
def on_post_tool_call(
    tool_name: str,
    args: dict,
    result: str,             # 工具执行结果（字符串）
    task_id: str,
    session_id: str,
    tool_call_id: str,
    duration_ms: int,        # 执行耗时（毫秒），非负整数
    **kwargs
) -> None:
    """观察性，返回值被框架忽略"""
```

### transform_tool_result

```python
def on_transform_tool_result(
    tool_name: str,
    args: dict,
    result: str,
    duration_ms: int,
    **kwargs
) -> str | None:
    """
    返回值:
      str   → 替换原始 result
      None  → 保持原始 result 不变
    """
```

## 注册方式

```python
def register(ctx) -> None:
    ctx.register_hook("pre_llm_call", on_pre_llm_call)
    ctx.register_hook("pre_tool_call", on_pre_tool_call)
    ctx.register_hook("post_tool_call", on_post_tool_call)
```

## 关键注意事项

- post hooks（`post_tool_call`, `post_llm_call`）是**观察性**的，返回值被框架忽略，无法阻断执行
- `pre_tool_call` 是唯一可以**阻断工具执行**的 hook（返回 `{"action": "block", ...}`）
- `pre_llm_call` 通过返回 `{"context": "..."}` 注入上下文到 user message 前
- 所有 hook 都应用 `try/except` 包裹，异常时静默降级
- `unknown hook name` 会产生 WARNING 但不会阻止插件加载（向前兼容）
- 验证: `hermes_cli/plugins.py:534`
