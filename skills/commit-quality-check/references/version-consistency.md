# 版本号一致性检查与修复

> 出自 SRA 项目的实战经验：在新增 `upgrade`/`uninstall` 命令时，
> 先提交后检查，发现 daemon.py 有 3 处硬编码 `"1.1.0"` 与项目的 `1.2.1` 不一致。

## 问题模式

Python 项目中版本号最容易出现不一致的地方：

| 位置 | 表现 | 风险 |
|------|------|------|
| `pyproject.toml` → `version` | 项目的权威版本号 | ✅ 单点 |
| `__init__.py` → `__version__` | Python 包的版本常量 | ✅ 单点 |
| **HTTP handler 硬编码** | `"version": "1.1.0"` | ❌ 容易被忘 |
| **Socket handler 硬编码** | `"sra_version": "1.1.0"` | ❌ 容易被忘 |
| **stats 响应** | `"version": "1.1.0"` | ❌ 容易被忘 |
| **help text 中的版本** | `"SRA v1.1"` | ❌ 容易被忘 |

## 标准修复模式

### 1. 统一从 `__init__.py` 导入

```python
# 在 daemon.py 中
from .. import __version__

# 使用时
"version": __version__,
"sra_version": __version__,
```

### 2. 检测命令（提交前必跑）

```bash
# 扫描所有硬编码版本号
grep -rn '"[0-9]\+\.[0-9]\+\.[0-9]\+"' --include="*.py" . | grep -v __pycache__ | grep -v '.bak'

# 对比关键版本声明文件
grep "version" pyproject.toml
grep "__version__" */__init__.py
```

### 3. 改完后验证

```python
from my_package import __version__
assert __version__ == "1.2.1"
```

## 教训

- 新增 API 端点或 CLI 命令后，**先跑一致性检查再提交**
- 版本号是「到处散落的常量」的典型例子——看到 `"x.y.z"` 就要问：这是从哪来的？该不该统一导入？
