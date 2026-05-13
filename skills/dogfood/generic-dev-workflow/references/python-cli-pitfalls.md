# Python CLI 开发常见陷阱

> 在项目内开发 CLI 工具时经常遇到的 Python 导入路径问题。

## 陷阱：ModuleNotFoundError — 无法导入项目内模块

### 症状

```text
Traceback (most recent call last):
  File "scripts/cli/main.py", line 17, in <module>
    from scripts.cli.commands import (
ModuleNotFoundError: No module named 'scripts'
```

### 根因

Python 的模块搜索路径（`sys.path`）默认包含：
1. 当前脚本所在目录（`scripts/cli/`）
2. 标准库路径
3. site-packages

但**不包含项目根目录**。所以 `from scripts.cli.commands import ...` 找不到 `scripts` 包。

### 修复模式

在 CLI 入口文件和被导入的命令模块中，**各自**添加项目根目录到 `sys.path`：

```python
# scripts/cli/main.py
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # 根据层级调整
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.pkg import something  # 现在可以正常导入了
```

### 为什么入口和命令模块都要加？

如果 `main.py` 调用 `commands.py`，而 `commands.py` 又导入了 `scripts.uca`，当 Python 执行 `commands.py` 时，它会**重新解析导入**——不会继承 `main.py` 修改过的 `sys.path`。

所以 `commands.py` 也需要同样的 `sys.path.insert(0, ...)` 模式。

### 替代方案

| 方案 | 适用场景 | 缺点 |
|:-----|:---------|:-----|
| `sys.path.insert` | 快速原型、项目内 CLI 工具 | 不够优雅、需要每个文件加 |
| `PYTHONPATH=. python3 scripts/cli/main.py` | 单次运行、CI | 每次都要手动加、容易忘记 |
| `pip install -e .` | 正式发布的包 | 需要 pyproject.toml 配置完整 |
| `python -m scripts.cli.main` | 包结构正确时 | 需要 `__init__.py` 和正确层级 |

### 陷阱二：`__init__.py` 在子模块就绪前导入它们

### 症状

```text
scripts/__init__.py:9: in <module>
    from .parser import PackParser, PackParseError
E   ModuleNotFoundError: No module named 'scripts.uca.parser'
```

在创建新的包结构时，`__init__.py` 尝试导入**尚未创建**的子模块导致失败。

### 根因

Python 在导入包时，会先执行 `__init__.py`。如果 `__init__.py` 中导入了子模块（如 `from .parser import PackParser`），Python 会尝试立即加载该子模块。如果该子模块文件**还不存在**，或者它自己的依赖（如 `from .protocol import ...`）形成循环，就会报错。

### 修复模式

**方案 A：先创子模块，再更新 `__init__.py`**

在开发新包时，按以下顺序操作：
1. 先创建 `protocol.py`、`parser.py` 等**子模块文件**（可先写 stub）
2. 最后再更新 `__init__.py` 的导入

**方案 B：惰性导入（lazy import）**

只在 `__init__.py` 中导出名称，实际导入推迟到使用时：

```python
# __init__.py
def get_parser():
    from .parser import PackParser
    return PackParser
```

### 实战教训（cap-pack UCA Core）

创建 `scripts/uca/` 包时，boku 先写了 `__init__.py`（导入了 parser/dependency/verifier），但当时 `parser.py` 尚不存在 → `ImportError`。解决方案：

```bash
# 正确的创建顺序：
1. mkdir scripts/uca/
2. write scripts/uca/protocol.py     # 无依赖
3. write scripts/uca/parser.py       # 依赖 protocol
4. write scripts/uca/dependency.py   # 依赖 protocol
5. write scripts/uca/verifier.py     # 依赖 protocol
6. write scripts/uca/__init__.py     # 最后，导入所有子模块
```

## 最佳实践（项目内 CLI 工具）

1. **入口文件**（`main.py`）始终加 `sys.path.insert`
2. **所有被入口文件直接或间接导入的模块**也加（或者确保它们在同一个包层级下用相对导入）
3. 使用相对导入（`from . import sibling`）而非绝对导入（`from scripts.pkg import ...`）可以减少问题

### 本项目实战

```python
# scripts/cli/main.py — 3 层深度（scripts/cli/main.py → scripts/cli/ → scripts/ → 项目根）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # 3 层

# scripts/uca/parser.py — 使用相对导入避免路径问题
from .protocol import CapPack  # ✅ 正确
# from scripts.uca.protocol import CapPack  # ❌ 可能导致 ImportError
```
