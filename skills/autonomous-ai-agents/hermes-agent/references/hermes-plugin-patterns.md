# Hermes 插件开发模式

> 从 sra-guard 插件的开发中总结的 Hermes 插件开发通用模式。
> 参考实现: `~/projects/sra/plugins/sra-guard/`

---

## 一、插件基础结构

每个 Hermes 插件是一个目录，放在 `~/.hermes/hermes-agent/plugins/<name>/` 下：

```
plugins/<name>/
├── plugin.yaml          # 插件清单（必选）
├── __init__.py          # 插件入口 + register()（必选）
├── *.py                 # 辅助模块（可选）
├── tests/               # 测试目录（推荐）
└── README.md            # 说明文档（可选）
```

### plugin.yaml 格式

```yaml
name: <plugin-name>       # 插件名，与目录名一致
version: 1.0.0            # 语义化版本
description: "..."        # 一句话描述
hooks:                    # 注册的 hook 列表
  - pre_llm_call
  - pre_tool_call
```

### __init__.py 的 register() 函数

```python
def register(ctx) -> None:
    """Hermes 在发现插件时自动调用此函数。
    
    ctx 提供:
      - register_hook(name, callback)  — 注册生命周期钩子
      - register_command(name, handler, description) — 注册斜杠命令
      - register_tool(...)              — 注册工具
    """
    ctx.register_hook("pre_llm_call", on_pre_llm_call)
    ctx.register_command("my-command", handler=handle_cmd, description="...")
```

## 二、连字符目录名与导入

Hermes 插件目录名允许含连字符（如 `sra-guard`），但 Python 模块名不允许连字符。

### 问题
```python
# ❌ 在 __init__.py 中这样导入会失败
from .client import SraClient  # 相对导入仅在包结构中可用
```

### 解决方案：用 importlib 替代标准 import

```python
# ✅ 在 __init__.py 中用 importlib 加载同级模块
import importlib.util
from pathlib import Path

def _load_helper(name):
    path = Path(__file__).parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(
        f"sra_guard.{name}", str(path)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# 使用
_client_mod = _load_helper("client")
_client = _client_mod.SraClient()
```

### 替代方案：展平结构

对于小型插件，将所有代码放在 `__init__.py` 中，避免模块导入。

参考: `plugins/disk-cleanup/` — 使用相对导入 `from . import disk_cleanup as dg`（Hermes 插件加载器支持此方式）。

## 三、可用 Hook 列表

| Hook | 触发时机 | 回调签名 | 返回值 |
|:-----|:---------|:---------|:-------|
| `pre_llm_call` | 每次 LLM 调用前 | `(messages, session_id, **kwargs)` | `None` 或 `{"context": str}` |
| `pre_tool_call` | 工具执行前 | `(tool_name, args, task_id, session_id, tool_call_id, **kwargs)` | `None` 或 `{"action": "block", "message": str}` |
| `post_tool_call` | 工具执行后 | `(tool_name, args, result, task_id, session_id, tool_call_id, duration_ms, **kwargs)` | 返回值被忽略（observational only） |
| `pre_approval_request` | 危险命令审批前 | `(command, description, ...)` | 观察者，返回值被忽略 |
| `post_approval_response` | 审批响应后 | `(command, choice, ...)` | 观察者，返回值被忽略 |
| `on_session_start` | 会话开始时 | `(session_id, **kwargs)` | `None` |
| `on_session_end` | 会话结束时 | `(session_id, **kwargs)` | `None` |
| `transform_terminal_output` | 终端输出转换 | `(output, **kwargs)` | 转换后的文本 |
| `transform_tool_result` | 工具结果转换 | `(result, **kwargs)` | 转换后的结果 |
| `post_api_request` | API 请求后 | `(response, **kwargs)` | `None` |
| `pre_gateway_dispatch` | Gateway 消息分发前 | `(event, gateway, session_store)` | `None`/`{"action": "skip"}`/`{"action": "rewrite"}` |

### pre_llm_call 上下文注入

```python
def on_pre_llm_call(messages, session_id, **kwargs):
    """返回 {"context": "..."} 会让 Hermes 将文本注入到当前轮次的 user_message 前。
    
    注入位置在 system prompt 之后、用户消息之前。
    不修改 system prompt（保留 prompt cache）。
    上下文是临时的——不持久化到 session DB。
    """
    last = messages[-1] if messages else {}
    if last.get("role") != "user":
        return None
    
    context = get_sra_recommendation(last["content"])
    if context:
        return {"context": context}
    return None
```

### post_tool_call 轨迹记录（Observational Hook）

`post_tool_call` 是一个纯粹的观察者 hook——返回值被 Hermes 框架忽略，不能影响工具执行。适合用于使用量统计、日志、监控。

```python
def on_post_tool_call(tool_name, args, result, task_id, session_id, tool_call_id, duration_ms, **kwargs):
    """工具执行后记录使用轨迹。
    
    Args:
        tool_name: 工具名称（如 "write_file", "skill_view", "web_search"）
        args: 工具参数字典
        result: 工具执行结果（字符串）
        task_id: 任务 ID
        session_id: 会话 ID
        tool_call_id: 工具调用 ID
        duration_ms: 执行耗时（毫秒）
    
    Returns:
        None（返回值被框架忽略）
    """
    try:
        if tool_name in {"skill_view", "skills_list"}:
            # skill_view 是 Hermes 内置工具，通过 tool_name 可检测
            skill_name = args.get("name", "") if isinstance(args, dict) else ""
            record_usage(skill=skill_name, action="viewed")
        elif tool_name not in {"todo", "memory", "session_search"}:
            # 常规工具记录，内部工具过滤
            record_usage(skill="", action="used", tool=tool_name)
    except Exception:
        logger.warning("轨迹记录异常: %s", exc_info=True)
    return None
```

关键要点：
- **skill_view 是标准工具调用**：`tool_name == "skill_view"`，args 包含 `{"name": "..."}`
- **observational only**：返回值被忽略，不阻塞工具
- **duration_ms**：整数毫秒，从调度开始到结束的耗时
- **去重**：同工具短时间连续调用时，建议模块级去重防止刷屏

```python
# 注册方式（在 register() 中）
ctx.register_hook("post_tool_call", on_post_tool_call)
```

## 四、插件开发注意事项

1. **不要修改 Hermes 核心代码** —— 所有自定义行为通过 hook 实现
2. **异常绝不向上传播** —— hook 回调中的异常会被 Hermes 捕获并记录，但插件不应依赖此机制
3. **降级策略** —— 插件依赖的外部服务（如 SRA Daemon）不可用时，应静默返回 None
4. **测试** —— 使用 mock 模拟外部依赖，不依赖真实服务
5. **源码位置** —— 插件源码在项目仓库中管理，通过安装脚本部署
