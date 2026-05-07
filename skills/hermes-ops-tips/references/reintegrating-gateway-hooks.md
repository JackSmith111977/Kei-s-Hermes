# Gateway 自定义 Hook 恢复指南

> 基于 2026-05-07 v0.10.0 → v0.12.0 升级后 statusline 失效的修复实战记录

## 问题现象

升级后发现某个自定义功能（如状态栏、自定义消息处理、特殊响应格式等）不再工作了。
文件虽然还在 `gateway/` 目录下，但功能不生效。

## 根因诊断

**核心判断规则**：文件存在 ≠ 功能可用。升级后 `gateway/run.py` 被完全重写，原有的 import 和调用点全部丢失。

### 诊断三步法

```bash
# Step 1: 确认文件存在
ls -la gateway/statusline.py

# Step 2: 确认文件被其他代码引用
grep -rn "gateway.statusline" gateway/
# 期望输出: gateway/run.py:from gateway.statusline import build_statusline
# 如果只搜到 statusline.py 自身 → 死代码！

# Step 3: 确认函数被调用
grep -n "build_statusline" gateway/run.py
# 期望输出: 出现 import 行 + 调用行
# 如果只有 import 行 → 只导入未调用
# 如果全无 → 完全未接入
```

### 对比旧版本找到集成点

```bash
# 如果有旧版本备份，直接对比
grep -n "from gateway.statusline" hermes-agent_old_v0.10.0/gateway/run.py
grep -n "build_statusline" hermes-agent_old_v0.10.0/gateway/run.py

# 查看旧版本的集成上下文（-B5 -A10 显示前后代码）
grep -n -B5 -A10 "build_statusline" hermes-agent_old_v0.10.0/gateway/run.py
```

## 恢复步骤（通用模板）

### 1. 添加 import

在 `gateway/run.py` 的导入区域（与其他 gateway import 放在一起）：

```python
from gateway.statusline import build_statusline
```

**位置选择**：找到 `from hermes_cli.config import cfg_get` 或类似的 gateway 相关 import 行，添加在它们之后。

### 2. 添加调用点

在响应组装完成之后、发送之前插入调用。

**精确位置特征**：在 `gateway/run.py` 中搜索以下标记：

```python
# Emit agent:end hook
```

这是发送前的最后一个集成点。在它之前添加自定义 footer 处理：

```python
# Append statusline footer (model, context, git info)
try:
    _platform_name = getattr(source.platform, "value", "") if source.platform else ""
    _statusline = build_statusline(
        agent_result=agent_result,
        platform=_platform_name,
    )
    if _statusline and response:
        response += _statusline
except Exception:
    logger.debug("Statusline generation failed (non-fatal)", exc_info=True)
```

### 3. 语法验证

```bash
cd ~/.hermes/hermes-agent
python3 -c "import ast; ast.parse(open('gateway/run.py').read()); print('✅ syntax OK')"
python3 -c "from gateway.statusline import build_statusline; print('✅ import OK')"
```

### 4. 重启网关

```bash
systemctl --user restart hermes-gateway
journalctl --user -u hermes-gateway --since "30 sec ago" --no-pager | tail -10
```

## 通用原则：如何找到正确的注入点

Hermes gateway 的响应处理流程：

```
agent_result ← _run_agent()
    ↓
response = agent_result.get("final_response")
    ↓
_empty response normalization
    ↓
_session_id update
    ↓
_reasoning display (if enabled)
    ↓
【★ 自定义 hook 最佳注入点 ★】← 在 runtime_footer 之后
    ↓
_agent:end hook 发射
    ↓
_process watchers
    ↓
_send response to platform adapter
```

**注入点选择原则**：
- 在 `agent:end` hook 之前（确保 hook 看到完整响应）
- 在 `reasoning display` 之后（防止被前缀覆盖）
- 在 `_send_response` 之前（确保修改生效）

## 其他自定义 Gateway 功能恢复模式

对于其他自定义功能（非 statusline）：

1. **消息预处理钩子**：搜索 `async def _handle_message` / `_preprocess`，在旧版本对应的位置插入
2. **响应后处理**：在 `agent:end` hook 之前或 `emit` 回调中插入
3. **工具调用拦截**：搜索 `handle_function_call`，如有自定义 tool 参考旧版接入
