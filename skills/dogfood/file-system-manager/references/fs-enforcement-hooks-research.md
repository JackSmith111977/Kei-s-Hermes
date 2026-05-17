# Hermes 文件操作介入机制速查

> **用途**: 如何在 Hermes 中拦截/审计文件操作，强制文件系统规范。
> **研究日期**: 2026-05-17 | **来源**: `~/.hermes/docs/research/fs-enforcement-hooks-research.md`

## 三类介入机制

| 层级 | 方式 | 侵入性 | 能力 |
|:----:|:-----|:------:|:-----|
| L1 | `config.yaml` → `hooks:` 块 + shell 脚本 | 无 | 审计/记录 |
| L2 | `~/.hermes/plugins/fs-enforce/` Python 插件 | 低 | 拦截 + 审计 + 诊断命令 |
| L3 | 修改 `tools/file_tools.py` 源码 | 高 | 底层保护 |

## VALID_HOOKS（与文件操作相关）

定义在 `hermes_cli/plugins.py:78-114`:
- `pre_tool_call` — 工具调用前（可 block ✅），kwargs: `tool_name, args, task_id, session_id`
- `post_tool_call` — 工具调用后（审计），kwargs: `tool_name, args, result, task_id, session_id, tool_call_id`
- `on_session_end` — 会话结束（清理），kwargs: `session_id, completed, interrupted`
- `transform_terminal_output` — terminal 输出改写
- `transform_tool_result` — 工具结果改写

## Shell Hooks JSON 协议

**stdin 输入**:
```json
{
  "hook_event_name": "post_tool_call",
  "tool_name": "write_file",
  "tool_input": {"path": "...", "content": "..."},
  "result": "File written to ...",
  "session_id": "sess_abc123"
}
```

**stdout 输出**（block 决策）:
```json
{"action": "block", "message": "文件命名不符合规范"}
```

## Python Plugin 参考实现

参考 `plugins/disk-cleanup/__init__.py`（316 行，最佳实践）:
```python
def register(ctx):
    ctx.register_hook("post_tool_call", _on_post_tool_call)
    ctx.register_hook("on_session_end", _on_session_end)
    ctx.register_command("disk-cleanup", handler=_handle_slash, ...)
```

`_on_post_tool_call` 的 kwargs:
```python
def _on_post_tool_call(
    tool_name: str = "",
    args: Optional[Dict[str, Any]] = None,
    result: Any = None,
    task_id: str = "",
    session_id: str = "",
    tool_call_id: str = "",
    **_: Any,
) -> None:
    # 根据 tool_name 分派: write_file / patch / terminal
```

## 敏感路径保护（现有机制）

`tools/file_tools.py`:
```python
_SENSITIVE_PATH_PREFIXES = ("/etc/", "/boot/", "/usr/lib/systemd/", "/private/etc/", "/private/var/")
_SENSITIVE_EXACT_PATHS = {"/var/run/docker.sock", "/run/docker.sock"}

def _check_sensitive_path(filepath: str, task_id: str = "default") -> str | None:
    """返回错误信息则阻止写入，返回 None 则放行"""
```
