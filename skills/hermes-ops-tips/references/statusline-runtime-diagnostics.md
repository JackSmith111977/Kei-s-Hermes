# Statusline 运行状态诊断要点

> 集成后验证指南 — 确认 statusline 不仅在代码中"存在"，而且在运行时"生效"

## 核心问题：集成 ≠ 运行

statusline 的代码可能已经完全集成（import 在、调用点在、gateway 重启了），但仍然不会出现在回复中。

## 常见失败模式

### 模式 1：agent_result 数据依赖

`build_statusline()` 在运行时会检查 `agent_result` 中的以下字段：

```python
agent_result.get("model")              # 无 → 模型名段缺失
agent_result.get("last_prompt_tokens")  # 无 → context bar 缺失
agent_result.get("input_tokens")        # 无 → context bar 缺失
agent_result.get("output_tokens")       # 无 → context bar 缺失
agent_result.get("context_length")      # 无 → 使用模型启发式值
```

**当所有字段都缺失时，`segments` 为空列表，函数返回 `""`**，没有任何错误。

### 模式 2：日志盲区

```python
try:
    _statusline = build_statusline(...)
    if _statusline and response:
        response += _statusline
except Exception:
    logger.debug("Statusline generation failed (non-fatal)", exc_info=True)
```

- 成功时的**空输出不会被记录**（不是异常）
- 异常只在 **DEBUG 级别** 记录，默认 `agent.log` 只有 INFO+
- 所以正常日志里完全看不到 statusline 的任何活动痕迹

### 模式 3：Git 信息静默失败

```python
result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
    capture_output=True, text=True, timeout=3,
    cwd=os.getcwd() if os.getcwd() else None,
)
```

- gateway 以 systemd 运行时，`os.getcwd()` 可能是 `/` 或其他非 git 目录
- `subprocess.TimeoutExpired` 和 `FileNotFoundError` 被静默捕获
- 所以 git 信息段通常为 None，不影响其他段

## 快速定位法

```bash
# 1. 确认集成链路（3 步检查）
cd ~/.hermes/hermes-agent
echo "---文件存在---"
ls -la gateway/statusline.py
echo "---import 存在---"
grep "from gateway.statusline" gateway/run.py
echo "---调用点存在---"
grep -A5 "build_statusline(" gateway/run.py

# 2. 检查 gateway 是否加载了新代码
echo "---statusline.py 修改时间---"
stat --format='%y' gateway/statusline.py
echo "---gateway 启动时间---"
ps -o lstart,pid,cmd -p $(systemctl --user show hermes-gateway -p MainPID --value)

# 3. Python 直接测试函数行为
python3 -c "
import sys; sys.path.insert(0, '.')
from gateway.statusline import build_statusline
# 模拟无数据的情况
print(repr(build_statusline(agent_result={}, platform='feishu')))
print(repr(build_statusline(agent_result=None, platform='feishu')))
# 模拟有数据的情况
print(repr(build_statusline(agent_result={
    'model': 'test/model',
    'last_prompt_tokens': 50000,
    'input_tokens': 45000,
    'output_tokens': 5000,
}, platform='feishu')))
"

# 4. 查看实际 agent_result 结构
grep -B5 -A30 "agent_result = await" gateway/run.py | head -50
```

## 终极测试：发一条消息验证

最直接的验证方式：向飞书发一条消息，看回复末尾是否有 statusline 脚注。

如果 statusline 代码已集成但无输出，且 Python 直接测试显示函数正常工作，问题就在 `agent_result` 数据本身 — 需要检查 `_run_agent()` 返回的字典包含了哪些字段。
