# 版本解析架构设计模式

## 问题

Python 项目在不同安装方式下（开发环境 / editable install / PyPI install）需要正确解析版本号。常见的 `setup.py` 正则解析 `__init__.py` 方式极其脆弱。

## 推荐的版本解析架构

### 三层降级链

```python
def _resolve_version() -> str:
    import os
    import subprocess

    # 层级 1: git describe（开发环境 + editable install）
    _here = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_here)
    git_dir = os.path.join(_project_root, ".git")
    if os.path.isdir(git_dir) or os.path.isfile(git_dir):
        try:
            tag = subprocess.check_output(
                ["git", "describe", "--tags", "--dirty=.dirty", "--always"],
                cwd=_project_root, stderr=subprocess.DEVNULL, timeout=5,
            ).decode().strip().lstrip("v")
            return tag
        except Exception:
            pass

    # 层级 2: importlib.metadata（pip install 正式安装）
    try:
        from importlib.metadata import version as _v
        return _v("package-name")
    except Exception:
        pass

    # 层级 3: _version.py（生成的文件 fallback）
    try:
        from ._version import version as _v
        if _v:
            return _v
    except Exception:
        pass

    return "0.0.0-dev"


__version__ = _resolve_version()
```

### pyproject.toml 配置

```toml
[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
tag_regex = '^(?:[\\w-]+-)?v?(?P<version>[\\d\\.a-b]{3,}(?:rc\\d+)?)$'
version_scheme = "post-release"
local_scheme = "no-local-version"
write_to = "skill_advisor/_version.py"
write_to_template = "__version__ = '{version}'\nversion = '{version}'\n"
```

### setup.py 最小化

```python
"""Minimal setup.py — version handled by pyproject.toml + setuptools-scm."""
from setuptools import setup, find_packages
setup(packages=find_packages())
```

## 各安装方式的版本解析路径

| 安装方式 | 层级 1 (git) | 层级 2 (importlib) | 层级 3 (_version.py) |
|:---------|:------------:|:------------------:|:--------------------:|
| 开发（git clone, 无 pip install） | ✅ `2.1.1-dev` | ❌ 无 metadata | ❌ 可能不存在 |
| editable install (pip install -e .) | ✅ `2.1.1.post0+gXXXX` | ⚠️ 看 build 是否成功 | ⚠️ 写入了但可能被 .gitignore |
| PyPI install (pip install sra-agent) | ❌ 无 .git | ✅ `2.1.1` | ✅ build 时生成 |


## 已知陷阱

### 1. setup.py 正则解析 __init__.py

```python
# ❌ 极度脆弱 — 不要这样做
version = re.search(
    r'__version__\s*=\s*["\']([^"\']+)',
    Path("pkg/__init__.py").read_text()
).group(1)  # 如果 __version__ 改为函数赋值，返回 None → AttributeError
```

### 2. 循环导入

当 `__init__.py` 顶层导入子模块，而子模块又导入 `__version__`：

```python
# __init__.py
from .runtime.daemon import X  # 触发 daemon.py 导入

# daemon.py
from .. import __version__  # __init__.py 还没执行到这 → 循环导入
```

**修复**：将模块级导入移到 `__version__` 定义之后。

### 3. setuptools-scm v10+ 配置变化

- `version_file` → `write_to`（v10 起废弃旧名）
- `vcs-versioning` 是必需依赖（setuptools-scm v10 重构后拆分）
- `tag_regex` 在 TOML 中用单引号 literal string 避免转义地狱

## 实战案例

- **SRA v2.1.1**：版本解析全部失效，`_version.py` 固化在 `2.0.3` 跨越 3 个版本，`setup.py` 正则匹配 `__version__ = _resolve_version()` 返回 None → CI 全炸
- **修复后 v2.1.2**：三层降级链 + 最小化 setup.py + 正确 setuptools-scm 配置 → CI 通过
- **Release**: https://github.com/JackSmith111977/Hermes-Skill-View/releases/tag/v2.1.2
