# 发布前准备检查清单 (Pre-Release Checklist)

> **适用场景**：当需要为一个 Python 项目做首次发布或版本升级时，按此清单逐项检查。
> **核心原则**：每一步要细细完成；如果遇到从未学过的操作，先进行深度学习再动手，不要凭经验判断。

---

## Phase 0: 现状分析 🧐

在动手前，先全面了解项目的当前状态：

```bash
# 1. 项目基本信息
#    - 项目路径、当前版本、Git 状态
#    - 仓库可见性（私有/公开）、Topics、描述
#    - PyPI 发布状态（是否已有版本上线）

# 2. 结构分析
find . -not -path "./.git/*" -not -path "*/__pycache__/*" -not -path "*.egg-info/*" | sort

# 3. Git 状态
git log --oneline --all
git branch -a
git tag --list
git remote -v

# 4. GitHub 仓库信息
curl -s https://api.github.com/repos/:owner/:repo | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('description'), d.get('topics'), d.get('private'))"
```

### 检查要点

| 检查项 | 说明 |
|:-------|:------|
| 仓库描述 | 是否能让用户 5 秒内明白项目做什么 |
| Topics | 是否包含语言、领域、功能三方面关键词 |
| 许可证 | 是否已选择（推荐 MIT） |
| 社区文件 | README/CONTRIBUTING/CODE_OF_CONDUCT/LICENSE 是否齐全 |
| CI/CD | 是否有 GitHub Actions |
| Git 标签 | 是否有对应版本的 tag |
| CHANGELOG | 是否有变更记录 |

---

## Phase 1: 文档准备 📝

### 1.1 创建/更新 CHANGELOG.md

基于项目实际开发历史和文档（EPICs、Sprint 记录、commit log）整理变更记录：

- **格式**：Keep a Changelog + Semantic Versioning
- **内容来源**：`docs/` 目录中的 EPIC 文档、Sprint 结果、commit log
- **必须包含**：v1.0.0（初始发布）和后续每个版本
- **每个版本的分类**：
  - 🚀 Added — 新功能
  - 🛠️ Changed — 变更
  - 🐛 Fixed — 修复
  - 🧪 Testing — 测试相关
  - 📚 Documentation — 文档相关

```markdown
## [1.1.0] — 2026-05-04

### 🚀 Added
- ...

### 🐛 Fixed
- ...
```

### 1.2 检查 README 一致性

对照实际代码检查 README 中的声明是否准确：
- ❌ 声称"零依赖"但实际有依赖
- ❌ `pip install` 指令包含已过时的参数
- ❌ 项目结构图遗漏重要文件
- ❌ GitHub Topics/Description 为空

---

## Phase 2: 配置清理 🧹

### 2.1 检查 pyproject.toml 完整性

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "package-name"
version = "X.Y.Z"
description = "..."
readme = "README.md"
license = "MIT"                    # SPDX 表达式（现代格式）
authors = [{name = "Author Name"}]
keywords = ["kw1", "kw2"]
classifiers = [                    # 不要包含 License classifier（已废弃）
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    ...
]
dependencies = [...]                # 运行时依赖
requires-python = ">=3.8"          # ⚠️ 必须指定

[project.urls]
Homepage = "https://github.com/owner/repo"
Repository = "https://github.com/owner/repo.git"
Documentation = "https://github.com/owner/repo#readme"

[project.scripts]
cli-name = "package.module:main"   # CLI 入口

[tool.setuptools.packages.find]
include = ["package", "package.*"]
```

### 2.2 检查 setup.py 与 pyproject.toml 是否重叠

**问题**：若 setup.py 中定义了 `install_requires` / `extras_require`，且 pyproject.toml 中也定义了 `dependencies` / `[project.optional-dependencies]`，构建时会报 `overwritten` 警告。

**修复方案**：
- ✅ 推荐：pyproject.toml 作为单一事实来源，setup.py 保持最小兼容包装
  ```python
  """Minimal setup.py for backward compatibility."""
  import re
  from pathlib import Path
  from setuptools import setup, find_packages

  init_path = Path("package") / "__init__.py"
  version = re.search(r'__version__\s*=\s*["\']([^"\']+)', init_path.read_text()).group(1)
  setup(version=version, packages=find_packages())
  ```

### 2.3 版本号统一

三个位置的版本号必须一致：
| 文件 | 位置 |
|------|------|
| `pyproject.toml` | `[project] version = "X.Y.Z"` |
| `__init__.py` | `__version__ = "X.Y.Z"` |
| `setup.py`（如有） | 从 `__init__.py` 读取 |

### 2.4 检查 License 配置

| 配置方式 | 兼容性 | 推荐度 |
|----------|--------|:------:|
| `license = "MIT"`（SPDX 表达式） + 无 License classifier | ✅ twine 6.2+ 支持 | ⭐⭐⭐ 推荐 |
| 仅 `License :: OSI Approved :: MIT License` classifier | ✅ 全兼容 | ⭐⭐ 可选 |
| 两者同时存在 | ⚠️ 可能冲突 | ❌ 避免 |

> **setuptools ≥69** 会自动从 `license` 字段生成 `License-Expression` 和 `License-File` 元数据。`twine ≤ 6.2.0` 不识别这些字段，但 PyPI 接受。如果 `twine check` 报错，降级 setuptools 或只用 classifier。

---

## Phase 3: 测试验证 ✅

### 3.1 运行测试

```bash
python3 -m pytest tests/ -v
# 预期：全部通过
```

### 3.2 构建验证

```bash
# 清理旧构建
rm -rf dist/ build/ *.egg-info

# 构建 sdist + wheel
python3 -m build

# 检查构建产物
ls -lh dist/
# → package-X.Y.Z.tar.gz
# → package-X.Y.Z-py3-none-any.whl

# 验证包内容
python3 -m twine check dist/*
# 预期：PASSED（WARNING 可忽略）
```

### 3.3 安装测试

```bash
# 从构建产物安装
pip install dist/*.whl

# 测试导入
python3 -c "from package import YourClass; print('OK')"

# 测试 CLI
cli-name --help
```

---

## Phase 4: Git 与发布 🚀

### 4.1 创建分支

```bash
git checkout -b prepare-release-vX.Y.Z
```

### 4.2 提交变更

```bash
git add -A
git commit -m "chore(release): 发布前准备 — CHANGELOG + 配置清理"
```

### 4.3 推送到 GitHub 并创建 PR

```bash
git push origin prepare-release-vX.Y.Z
```

### 4.4 Review 通过后合并到 main

### 4.5 创建 git tag

```bash
git checkout main
git pull origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

### 4.6 创建 GitHub Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z — Release Title" \
  --notes "Release notes content" \
  --target main
```

### 4.7 发布到 PyPI（可选）

```bash
rm -rf dist/ build/ *.egg-info
python3 -m build
python3 -m twine upload dist/* -u __token__ -p 你的PyPI_TOKEN
pip install --upgrade package-name
```

---

## Phase 5: 发布后验证 🔍

```bash
# 1. 验证 PyPI 版本
curl -s https://pypi.org/pypi/package-name/json | python3 -c "import json,sys; print(json.load(sys.stdin)['info']['version'])"

# 2. 验证 GitHub Release
gh release view vX.Y.Z

# 3. 验证 git tag
git tag --list | grep vX.Y.Z

# 4. 验证 pip 安装
pip install --upgrade package-name
package-name --help
```

---

## 🔴 红线检查清单（发布前必须全部满足）

- [ ] 38+ 测试全部通过
- [ ] 构建成功（sdist + wheel）
- [ ] twine check PASSED
- [ ] CHANGELOG.md 已创建并包含所有版本变更
- [ ] 版本号在 pyproject.toml / __init__.py 中一致
- [ ] pyproject.toml 不缺少 `requires-python` 字段
- [ ] setup.py 无 install_requires 配置重叠（如果有）
- [ ] License 配置不产生 deprecation warning
- [ ] README.md 与代码实际状态一致
- [ ] GitHub Topics 和 Description 已设置
- [ ] 许可证文件（LICENSE）存在
- [ ] git tag 已创建并推送
- [ ] GitHub Release 已创建

---

## 🚩 常见踩坑记录

| 踩坑 | 根因 | 解决方案 |
|:-----|:------|:---------|
| `install_requires overwritten` 警告 | setup.py 和 pyproject.toml 都定义了依赖 | 统一到 pyproject.toml |
| `License classifiers are deprecated` | 在 classifier 中定义 License | 改用 `license = "MIT"` 字段 |
| `requires-python` 未指定 | pyproject.toml 缺少该字段 | 添加 `requires-python = ">=3.8"` |
| `twine check` 报 unrecognized field | setuptools 太新（≥69）生成 PEP 639 字段 | 降级 setuptools 到 <68 |
| git push 需要代理 | 国内服务器直连 GitHub 慢 | 配置 git http.proxy + 启动代理 |
| PyPI 版本已存在但 GitHub 无 Release | 直接 `twine upload` 跳过了 GitHub | 先创建 GitHub Release 再上传 PyPI |
