# Python 版本兼容性 CI 失败真实案例

> 来源: SRA v2.0.0–v2.0.2 发布过程
> 日期: 2026-05-12

---

## 案例 1: PEP 604 联合类型语法在 CI 矩阵中崩溃

### 症状

Release CI 在 Python 3.9 上失败：
```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```
Python 3.10/3.11/3.12 全部通过。Release 流程（只用 3.11）也通过。

### 根因

`skill_advisor/runtime/config.py` 使用了 `dict | None` 语法（PEP 604，Python 3.10+），
但 `pyproject.toml` 声明了 `requires-python = ">=3.8"`，CI 矩阵包含 Python 3.9。

`dict | None` 在 Python 3.9 上是有效的 Python 语法表达式（`__or__` 操作），
但在类型注解上下文中，`dict`（类对象）与 `None`（NoneType）的 `|` 操作未定义 → TypeError。

### 为什么 Release CI 没发现？

`release.yml` 只用 `python-version: "3.11"` 测试，完全跳过了 3.9 的问题。
→ Release 工作流的 Python 版本脱敏。

### 修复

将 `dict | None` 改为 `dict`：
```python
# ❌ 3.10+
def _load_schema() -> dict | None:
    ...

# ✅ 3.8+
def _load_schema() -> dict:
    ...
```

### 反思

`ast.parse` 无法捕获此问题（`dict | None` 是合法 Python 语法），
必须在 CI 中增加：
1. `ruff check --target-version py39` 
2. 正则扫描 PEP 604 联合类型模式
3. 确保 release.yml 的 Python 版本覆盖 CI 矩阵最老版本

---

## 案例 2: Release 通过了但 CI 红了

### 现象

- Release v2.0.1 CI: ✅ success（只在 3.11 上跑）
- CI on master: ❌ failure（3.9 上 PEP 604 语法错误）
- 用户反馈「CI 仍然有问题」

### 根因

Release 工作流和 CI 工作流使用不同的 Python 版本矩阵：
- `release.yml`: 只测 3.11
- `ci.yml`: 测 3.9 / 3.10 / 3.11 / 3.12

### 预防

Release 不能只在高版本 Python 上验证。至少增加一个低版本检查：

```yaml
# release.yml 增加低版本预检
- name: 🧪 Low-version syntax check
  run: |
    pip install ruff
    ruff check --target-version py39 --select UP skill_advisor/
```

或者更严格：确保 CI 矩阵**全部通过**后才允许触发 release。
