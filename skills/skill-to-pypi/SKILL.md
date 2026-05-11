---
name: skill-to-pypi
description: "将 Hermes 内部组件（skill/脚本/工具）打包为独立的 Python 开源项目。涵盖项目结构初始化、模块化重构、pyproject.toml/setup.py 配置、测试框架搭建、Git 版本管理、覆盖率目标设定、LICENSE 选择等完整流程。\n\n从一次实战中沉淀：SRA (Skill Runtime Advisor) 从单脚本 skill-advisor.py 转化为独立 GitHub 仓库的完整经验。"
version: 1.1.0
triggers:
  - 开源
  - 发布到 PyPI
  - pip install
  - 打包
  - 独立项目
  - GitHub 发布
  - 开源项目
  - open source
  - publish to pypi
  - package
  - 项目结构
  - project scaffolding
  - twine
  - setuptools
  - pypi 上传
  - license
  - pep 621
  - pep 639
  - wheel
  - sdist
  - 发布前准备
  - 发行版
  - first release
  - CHANGELOG
  - 文档一致性检查
  - pre-release
  - CI 配置
  - GitHub Actions
  - 自动测试
design_pattern: Pipeline + Generator
skill_type: Workflow
---

# 📦 Skill to PyPI · 独立开源项目打包指南 v1.1.0

> **经验来源**：SRA (Skill Runtime Advisor) 从 Hermes 内部单脚本 `skill-advisor.py` 转化为独立 GitHub 仓库的完整实战。  
> **核心教训**：开源项目不是"把文件复制出来就行"，需要模块化重构、测试覆盖、文档完备、安装配置四大支柱。

---

## 〇、决策树：什么时候该独立打包？

现有组件是否适合开源化——
```
组件是 Hermes 特有的吗？
├─ 是（依赖 Hermes Agent 核心 API）→ ❌ 不适合开源，保持为 skill
└─ 否（通用 Python 工具）→ 继续评估
    ↓
组件有独立价值吗？
├─ 否 → 保持为 skill
└─ 是 → 继续评估
    ↓
组件能脱离 Hermes 环境运行吗？
├─ 否（依赖 skill_view/skill_manage 等 Hermes 工具）→ 保持为 skill
└─ 是 → ✅ 适合独立打包！
```

**SRA 的判断过程**：
- ✅ 不依赖 Hermes API（只用文件 I/O + YAML 解析）
- ✅ 有独立价值（任何 AI Agent 都可使用）
- ✅ 通用 Python 库（核心是字符串匹配 + 关键词提取）

---

## 一、项目结构初始化

### 1.1 推荐目录布局

```
your-project/
├── your_package/                     ← 核心包（Python 包名，下划线风格）
│   ├── __init__.py                   ← 版本号 + 公开 API 导出
│   ├── advisor.py                    ← 主入口类
│   ├── indexer.py                    ← 子模块 1
│   ├── matcher.py                    ← 子模块 2
│   ├── memory.py                     ← 子模块 3
│   ├── synonyms.py                   ← 数据/配置
│   └── cli.py                        ← CLI 入口
├── tests/                            ← 测试目录
│   ├── test_matcher.py               ← 核心逻辑测试
│   ├── test_indexer.py               ← 模块测试
│   ├── test_coverage.py              ← 覆盖率端到端测试
│   └── test_benchmark.py             ← 性能基准测试
├── docs/
│   ├── DESIGN.md                     ← 设计文档
│   └── INTEGRATION.md                ← 集成指南
├── README.md                         ← 项目说明（必须）
├── CONTRIBUTING.md                   ← 贡献指南
├── LICENSE                           ← 许可证
├── setup.py                          ← 安装脚本
├── pyproject.toml                    ← 构建配置
└── .gitignore
```

### 1.2 从单文件到包的分解策略

原始状态（单脚本）：
```
skill-advisor.py （~800 行，含 6 个功能域）
```

分解步骤：
```bash
# 1. 创建包目录
mkdir -p your_package/{scripts,tests}

# 2. 按功能域拆分（实战中的拆分线）：
#    - 主类/入口           → advisor.py
#    - 数据索引构建        → indexer.py
#    - 核心匹配算法        → matcher.py
#    - 持久化/状态管理     → memory.py
#    - 静态数据/配置       → synonyms.py
#    - CLI 交互            → cli.py

# 3. 创建 __init__.py 导出主类
echo 'from .advisor import YourClass
__version__ = "1.0.0"' > your_package/__init__.py
```

---

## 二、安装配置

### 2.1 pyproject.toml（推荐，PEP 621）

> ⚠️ **setuptools>=72 已废弃旧格式**：
> - ❌ `license = {text = "MIT"}` → ✅ `license = "MIT"`（PEP 639 字符串表达式）
> - ❌ `License :: OSI Approved :: MIT License` → ✅ 移除该 classifier，由 `license` 字段自动派生
> - ❌ 缺少 `requires-python` → ✅ **必须指定**，否则构建失败

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "sra-agent"
version = "1.0.0"
description = "一句话描述"
readme = "README.md"
license = "MIT"                     # ⚠️ 字符串格式，不能用 {text = "MIT"}
authors = [{name = "Your Name"}]
keywords = ["keyword1", "keyword2"]
requires-python = ">=3.8"           # ⚠️ 必须指定，不指定会构建失败
dependencies = [
    "pyyaml>=5.1",   # 最小依赖
]
# ❌ 不要加 License classifier，新版 setuptools 从 license 字段自动派生
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
]
[project.scripts]
sra = "your_package.cli:main"    # CLI 入口
[tool.setuptools.packages.find]
include = ["your_package", "your_package.*"]
[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 2.2 setup.py（最小兼容方式）

**不要**在 setup.py 中重复定义 `install_requires` 和 `extras_require`——这会导致 `install_requires overwritten in pyproject.toml` 警告。setup.py 应只做最小兼容包装，从 `__init__.py` 读取版本号：

```python
"""Minimal setup.py for backward compatibility.
All project metadata is defined in pyproject.toml.
"""
import re
from pathlib import Path
from setuptools import setup, find_packages

# 从 __init__.py 读取版本号（单一事实来源）
init_path = Path("your_package") / "__init__.py"
version = re.search(
    r'__version__\s*=\s*["\']([^"\']+)',
    init_path.read_text()
).group(1)

setup(
    version=version,
    packages=find_packages(),
)
```

### 2.3 安装测试

```bash
# 开发模式安装
pip install -e ".[dev]"

# 测试导入
python -c "from your_package import YourClass; print('OK')"

# 测试 CLI
sra --help
```

---

## 三、模块化重构关键点

### 3.1 循环依赖预防

经验教训：`synonyms.py` 作为数据文件要**独立于其他模块**。

```python
# ❌ 错误：synonyms.py 导入 matcher
from .matcher import something

# ✅ 正确：synonyms.py 纯数据，不导入任何模块
SYNONYMS = {...}
REVERSE_INDEX = {...}
```

**依赖方向**：`__init__ → advisor → {indexer, matcher, memory} → synonyms`
**绝不能有**：`synonyms → 任何模块`

### 3.2 CLI 入口设计

```python
# cli.py — 作为独立的脚本入口
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
# 确保即使不安装也能运行
```

### 3.3 数据路径设计

技能目录不能硬编码，必须可配置：

```python
class SkillAdvisor:
    def __init__(self, skills_dir=None, data_dir=None):
        self.skills_dir = skills_dir or os.path.expanduser(
            os.environ.get("SRA_SKILLS_DIR", "~/.hermes/skills")
        )
        self.data_dir = data_dir or os.path.expanduser(
            os.environ.get("SRA_DATA_DIR", "~/.sra_agent/data")
        )
```

**原则**：环境变量 > 构造函数参数 > 默认值

---

## 四、测试框架搭建

### 4.1 测试分层

| 层 | 目的 | 示例文件 | 典型数量 |
|----|------|---------|---------|
| **单元测试** | 验证单个函数逻辑 | `test_matcher.py` | 8-15 |
| **模块测试** | 验证子模块集成 | `test_indexer.py` | 6-10 |
| **集成测试** | 验证主类工作流 | `test_matcher.py` 中的 TestAdvisor | 6-10 |
| **覆盖率测试** | 验证对真实数据的覆盖率 | `test_coverage.py` | 2-4 |
| **基准测试** | 性能验证 | `test_benchmark.py` | 2-4 |

### 4.2 覆盖率测试实战

覆盖率的**测试查询**应该怎么设计？

```python
# ❌ 错误：用空的测试数据
skill = {"name": "test", "triggers": ["test"]}
score = matcher.score({"test"}, skill, {})

# ✅ 正确：用真实技能目录（如果存在）
skills_dir = os.path.expanduser("~/.hermes/skills")
if os.path.exists(skills_dir):
    advisor = SkillAdvisor(skills_dir=skills_dir)
    result = advisor.analyze_coverage()
    assert result["coverage_rate"] >= 50
```

**关键经验**：覆盖率测试必须用真实数据才能发现问题。`test_each_skill_individual` 逐 skill 验证的策略是发现匹配漏洞最有效的方式。

### 4.3 同义词表测试

```python
def test_chinese_to_english_mapping(self):
    """中文关键词应有英文映射——这是跨语言匹配的基础"""
    chinese_keys = [k for k in SYNONYMS if any('\u4e00' <= c <= '\u9fff' for c in k)]
    for key in chinese_keys:
        has_english = any(all(c.isascii() for c in v) for v in SYNONYMS[key])
        assert has_english, f"中文同义词 {key} 缺少英文映射"

def test_no_duplicate_synonyms(self):
    """同义词表不应有重复条目——否则会浪费匹配带宽"""
    for key, values in SYNONYMS.items():
        assert len(values) == len(set(v.lower() for v in values))
```

---

## 五、开源文档模板

### 5.1 README.md 结构

```markdown
# 项目名称 — 一句话描述

> **一句吸引人的话**

## 🎯 核心能力

| 能力 | 说明 |
|------|------|

## 🏗️ 架构

## 🚀 快速开始

### 安装

### 基本用法

### CLI 使用

## 📊 基准测试

## 🔌 集成方式

## 🧪 测试

## 📄 许可证
```

### 5.2 LICENSE 选择

- 开源通用 → MIT License
- 需要保护专利 → Apache 2.0
- 要求同样开源 → GPL v3

### 5.3 CONTRIBUTING.md 必须包含

```markdown
## 开发环境
## 代码规范
## 测试（含覆盖率要求）
## 提交 PR 流程
## 发布流程
```

---

## 六、Git 版本管理

```bash
# 初始化
cd your-project
git init
git checkout -b main

# 首次提交前确认 .gitignore
echo "__pycache__/
*.pyc
*.egg-info/
dist/
build/
.venv/
.env
.pytest_cache/
" > .gitignore

# 提交
git add -A
git commit -m "🎉 v1.0.0: initial release"

# 关联远程仓库
git remote add origin https://github.com/YOUR_USER/your-project.git
git push -u origin main

# 打标签（触发 CI 发布）
git tag v1.0.0
git push origin v1.0.0
```

---

## 七、发布前准备流程

在打标签和发布之前，创建一个独立的发布准备分支，按以下步骤系统性地准备：

### 7.1 创建发布分支

```bash
git checkout -b release-v<version>
```

### 7.2 Step 1：项目现状分析

对所有维度做全面摸底：

| 维度 | 检查内容 |
|:-----|:---------|
| 代码质量 | 总行数、模块数、外部依赖、循环依赖 |
| Git 状态 | 分支、标签、提交历史、远程仓库 |
| 测试覆盖 | 测试数量、通过率、边界情况 |
| 文档完备性 | README/RUNTIME/DESIGN/EPIC/SPRINT 等 |
| 构建状态 | `python3 -m build` + `twine check` |
| GitHub 仓库 | 描述、Topics、主页、Issue/PR 模板 |

输出一份 `docs/PROJECT-STATUS-ANALYSIS.md` 报告。

### 7.3 Step 2：创建 CHANGELOG.md

基于 Keep a Changelog 格式 + SemVer：

```markdown
# Changelog

## [Unreleased]

### 🚀 Added
- ...

### 🛠️ Changed
- ...

### 🐛 Fixed
- ...

## [1.0.0] — 2026-01-01
### 🚀 Added
- 初始发布
```

如果 Git 历史较浅（如 squash merge 后只有 2 个 commit），从项目的 docs/ 目录（EPICs、Sprint 计划、设计文档）提取变更记录来编写 CHANGELOG。

### 7.4 Step 3：代码-文档一致性检查

**逐项对比所有文档与实际代码**：

| 检查点 | 方法 | 严重度 |
|:-------|:-----|:------:|
| README CLI 命令表 vs 实际 CLI | `grep "COMMANDS" cli.py` vs README 表格 | 🔴 P0 |
| README API 端点表 vs 实际 API | `grep "do_GET\|do_POST" daemon.py` vs README 表格 | 🔴 P0 |
| 文档中已修复的问题描述 | 搜索"待修复""已知限制"等关键词 | 🔴 P0 |
| 版本号一致性 | pyproject.toml / __init__.py / cli.py help / daemon.py | 🟡 P1 |
| 项目结构图 vs 实际文件树 | 手动对比 | 🟡 P1 |
| pip install 指令准确性 | 确认包名一致 | 🟡 P1 |
| 作者签名 | cli.py version / __init__ / pyproject.toml authors | 🟢 P2 |

按 P0→P1→P2 分级修复，修复后运行全套测试确保不破坏功能。

### 7.5 Step 4：配置清理

检查构建输出中的 deprecation 警告：

```bash
python3 -m build 2>&1 | grep -i "deprecat\|warning\|error"
```

常见问题：
- ❌ `install_requires overwritten` → setup.py 和 pyproject.toml 配置重叠，统一到 pyproject.toml
- ❌ `License classifiers are deprecated` → 添加 `license = "MIT"` 字段或忽略（build 仍然通过）
- ❌ `requires-python` missing → 必须添加

### 7.6 Step 5：添加 CI/CD

创建 `.github/workflows/ci.yml`：

```yaml
name: CI
on:
  push:
    branches: [master, "release-*"]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v

  build:
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install build twine
      - run: python3 -m build
      - run: python3 -m twine check dist/*
```

> ⚠️ **注意**：推送 `.github/workflows/` 下的文件需要 GitHub Token 有 `workflow` 权限。如果推送被拒，在 https://github.com/settings/tokens 中勾选 `workflow` 权限。

同时更新 README 添加 CI 徽章：
```markdown
[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
```

### 7.7 Step 6：最终验证

```bash
# 1. 安全检查 — 无硬编码秘钥
git diff --cached -S "gph_\|sk-\|token\|password\|api_key" || echo "✅ 安全"

# 2. 测试 — 全部通过
pytest tests/ -v

# 3. 构建 — sdist + wheel
python3 -m build && python3 -m twine check dist/*

# 4. 版本号一致性
# pyproject.toml / __init__.py / daemon.py / cli.py 所有版本号一致
```

**提交规范**：
- `docs:` — 文档修复
- `chore:` — 配置清理、作者签名更新
- `ci:` — CI 配置文件添加

---

## 八、✅ 发布准备

发布前请对照 **[第十节](#十-发布检查清单) 的完整检查清单** 逐项确认。

### ⚠️ PyPI License 配置避坑指南（实战教训）

```toml
# ❌ 不要这样写（PEP 639 格式，旧版 setuptools/twine 报错）
license = "MIT"

# ✅ 正确写法（兼容所有版本的工具链）
classifiers = [
    "License :: OSI Approved :: MIT License",
]
```

**问题表现**：`twine check` 或 `twine upload` 报错：
```
ERROR  Invalid distribution metadata: unrecognized field 'license-expression'
ERROR  Invalid distribution metadata: unrecognized field 'license-file'
```

**根因**：新版 setuptools（≥68）会自动从 `license = "MIT"` 生成 `License-Expression: MIT` 和 `License-File: LICENSE` 字段，但 twine 6.x 及旧版 PyPI 不识别这个字段。

**解决方案（二选一）：**
1. **推荐**：不写 `license` 字段，用 `classifier` 替代（兼容所有工具）
2. **降级**：`pip install 'setuptools<68'` 再构建

**其他常见构建问题：**
- `requires-python` 缺失 → setuptools 报 `NoneType' object is not iterable`
- `License classifier` 与 `license` 字段同时存在 → PEP 639 冲突报错
- 版本号不一致（pyproject.toml / setup.py / __init__.py）→ 安装后版本混淆

---

## 九、发布到 PyPI

### 9.1 前置准备

```bash
# 安装构建和发布工具
pip install build twine

# 需要 PyPI API Token：
# 1. 去 https://pypi.org/manage/account/token/ 登录（GitHub OAuth）
# 2. 创建 API Token（Scope 选 "Entire account"）
# 3. 保存 token （格式：pypi-xxxxxxxx）
```

### 9.2 构建

```bash
# 清理旧的构建产物
rm -rf dist/ build/ *.egg-info

# 构建 sdist + wheel
python3 -m build

# 验证构建产物
ls -lh dist/
# → your-package-1.0.0.tar.gz
# → your_package-1.0.0-py3-none-any.whl
```

### 9.3 验证包内容

```bash
python3 -m twine check dist/*
# 如果有 WARNING 可以忽略，PyPI 接受新标准
# 如果 ERROR → 需要修复再上传
```

### 9.4 上传到 PyPI

**前置检查：确认版本号不冲突**
```bash
# 检查 PyPI 上是否已存在相同版本
EXISTS=$(curl -s https://pypi.org/pypi/$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['name'])")/json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['info']['version'])" 2>/dev/null)
LOCAL=$(python3 -c "print(__import__('your_package').__version__)")
if [ "$EXISTS" = "$LOCAL" ]; then
  echo "❌ 版本 $LOCAL 已存在 PyPI，需要 bump 版本号"
  exit 1
fi
```

```bash
# 上传到正式 PyPI
python3 -m twine upload dist/* -u __token__ -p pypi-xxxxxxxx

# 或先上传到 Test PyPI 试水
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/* -u __token__ -p pypi-xxxxxxxx
```

### 9.5 安装验证

```bash
# 从 PyPI 安装
pip install your-package

# 测试 CLI
your-package --help

# 测试导入
python -c "from your_package import YourClass; print('OK')"
```

### 9.6 常见构建错误

| 错误 | 原因 | 修复 |
|------|------|------|
| `License :: OSI Approved :: MIT License` **废弃** | setuptools>=72 不再接受 License classifier | 移除该 classifier，使用 `license = "MIT"` 字段 |
| `requires-python` not specified | PEP 621 要求显式声明 | 添加 `requires-python = ">=3.8"` |
| `license = {text = "MIT"}` **报错** | 旧版 dict 格式 | 改为 `license = "MIT"`（PEP 639 字符串表达式） |
| `InvalidDistribution: unrecognized field 'license-file'` | 新版 setuptools 自动生成，旧版 twine 不兼容 | 升级 twine 或忽略（PyPI 接受） |
| `ModuleNotFoundError: No module named 'build'` | 未安装 build 工具 | `pip install build` |

### 9.7 版本号管理策略

**统一管理三个位置的版本号：**

| 文件 | 位置 |
|------|------|
| `pyproject.toml` | `[project] version = "1.0.0"` |
| `__init__.py` | `__version__ = "1.0.0"` |
| `setup.py`（如有） | `setup(version="1.0.0")` |

> 💡 **最佳实践**：用 `__init__.py` 作为单一事实来源，`setup.py` 从包中读取版本号：
> ```python
> # setup.py
> import re
> with open("your_package/__init__.py") as f:
>     version = re.search(r'__version__\s*=\s*["\']([^"\']+)', f.read()).group(1)
>
> setup(version=version, ...)
> ```

### 9.8 创建 GitHub Release

PyPI 发布后，同步创建 GitHub Release：

```bash
# 切到 master、合并、打标签
git checkout master
git merge release-v<version>
git tag v<version> && git push origin v<version>

# 用 gh CLI 创建 Release（标题只留版本号！）
gh release create v<version> \
  -t "v<version>" \
  -F CHANGELOG.md

# ⚠️ 用户偏好：Release 标题只保留版本号（如 "v1.2.1"），不加描述性文字
# ❌ 错误：gh release create v<version> -t "Project Name v<version> - 新增功能"
# ✅ 正确：gh release create v<version> -t "v<version>"
```

### 9.9 Daemon 感知的发布流程（适用于带后台进程的项目）

如果项目有守护进程（如 SRA），发布时必须管理 daemon 生命周期：

```bash
# 发布全流程（带 daemon 管理）
sra stop                          # 1. 停止 daemon
pip uninstall my-package -y       # 2. 卸载旧版
rm -rf dist/ build/ *.egg-info   
python3 -m build                  # 3. 构建新版
pip install dist/*.whl            # 4. 安装新版
sra start                         # 5. 启动 daemon
sra status                        # 6. 验证 daemon
sra recommend 构建                 # 7. 快速功能验证

# ⚠️ 关键陷阱
# - pip uninstall 不重启 daemon → daemon 用的还是旧版代码
# - 构建前必须清理 dist/ 避免上传旧产物
# - PEP 668 环境需加 --break-system-packages
```

### 9.10 Token 安全存取模式

**通用模式：**

```bash
# 存储（~/.hermes/.env）
echo "TWINE_USERNAME=__token__" >> ~/.hermes/.env
echo "TWINE_PASSWORD=pypi-xxxx" >> ~/.hermes/.env
chmod 600 ~/.hermes/.env

# 使用时加载
source ~/.hermes/.env
twine upload dist/* -u "$TWINE_USERNAME" -p "$TWINE_PASSWORD"
```

**SRA 实战引用（2026-05-07）：**
- Token 已存入 `~/.hermes/.env`，变量名 `TWINE_PASSWORD` / `PYPI_TOKEN`
- 版本号最终发布为 **v1.2.0**（非 v1.1.0，因 PyPI 不允许覆盖已存在的版本）
- 发布步骤: bump version → build → twine upload → git tag → gh release
- 结果: https://pypi.org/project/sra-agent/1.2.0/
- GitHub Release: https://github.com/JackSmith111977/Hermes-Skill-View/releases/tag/v1.2.0
- 发布命令: `source ~/.hermes/.env && twine upload dist/*`

---

## 十、🛑 PyPI 发布实战排坑

### 10.1 pyproject.toml 配置关键事项

**PEP 621 要求 `license` 为字符串而不是 `{text: "MIT"}` 对象：**

```toml
# ❌ 错误
license = {text = "MIT"}
license-files = ["LICENSE"]

# ✅ 正确（PEP 621 兼容格式）
license = "MIT"    # 或用旧版 classifier 方式
```

**PEP 639（setuptools ≥69）会自动生成 `License-Expression` 和 `License-File`：**

```toml
# setuptools ≥69 生成的 METADATA 包含：
# License-Expression: MIT
# License-File: LICENSE
# Dynamic: license-file
```

**兼容性问题：** twine ≤ 6.2.0 不识别这些新字段，会报 `InvalidDistribution: unrecognized field 'license-expression'`。

### 10.2 解决方案对比

| 方案 | 操作 | 复杂度 | 推荐度 |
|------|------|--------|--------|
| **降级 setuptools** | `pip install 'setuptools<68'` | ⭐ 低 | ⭐⭐⭐ 推荐 |
| **删除 license 字段** | 只用 `License :: OSI Approved :: MIT License` classifier | ⭐ 低 | ⭐⭐⭐ 推荐 |
| **修复 wheel metadata** | 手动解压修改 METADATA 文件 | ⭐⭐⭐ 中 | ⭐ 不推荐 |
| **升级 twine 到最新** | `pip install --upgrade twine` | ⭐ 低 | ⭐⭐ 当前最新版仍不兼容 |

### 10.3 实战验证流程

完整流程（从零到发布）：

#### 第 1 步：统一版本号

```bash
# pyproject.toml / setup.py / __init__.py 三个地方版本号必须一致
# pyproject.toml
version = "1.1.0"

# __init__.py
__version__ = "1.1.0"

# setup.py
setup(version="1.1.0", ...)
```

#### 第 2 步：确保 pyproject.toml 完整性

```toml
[project]
name = "your-package"
version = "1.1.0"
description = "..."
readme = "README.md"
authors = [{name = "Your Name"}]
keywords = ["keyword1", "keyword2"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",  # ← 用这种，不要用 license 字段
    "Programming Language :: Python :: 3.8",
]
dependencies = ["pyyaml>=5.1"]
requires-python = ">=3.8"  # ← 这个字段容易遗漏
```

#### 第 3 步：构建

```bash
# 清理旧的构建产物
rm -rf dist/ build/ *.egg-info
python3 -m build

# 确认没有 deprecation 警告
python3 -m build 2>&1 | grep -i "error"
```

#### 第 4 步：上传

```bash
pip install twine
twine upload dist/*.whl -u __token__ -p 你的PyPI_TOKEN
```

### 10.4 发布后验证

```bash
# 方式一：pip 安装测试
pip install your-package

# 方式二：查看 PyPI API
curl -s https://pypi.org/pypi/your-package/json | jq '.info.version'

# 验证可导入
python3 -c "from your_package import YourClass; print('OK')"

# 验证 CLI
your-cli --help
```

### 10.5 已知问题 / 兼容性

| 环境 | 问题 | 处理 |
|------|------|------|
| setuptools ≥69 | 自动生成 `License-Expression` 字段 | 降级到 <68 |
| twine 6.2.0 | 不识别 PEP 639 新字段 | 同上 |
| Python 3.12 | `pip install build` 可能报 `externally-managed-environment` | 加 `--break-system-packages` |
| shell 屏蔽 token | `***` 屏蔽变量 | 用文件存储或手动输入 |

### 10.6 发布的 pyproject.toml 黄金模板

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "package-name"
version = "1.0.0"
description = "一句话描述项目"
readme = "README.md"
authors = [{name = "Author Name"}]
keywords = ["keyword1", "keyword2"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "pyyaml>=5.1",
]
requires-python = ">=3.8"

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[project.scripts]
cli-name = "package.module:main"

[tool.setuptools.packages.find]
include = ["package", "package.*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 10.7 常见错误速查

| 错误信息 | 原因 | 修复 |
|----------|------|------|
| `'NoneType' object is not iterable` | 缺少 `requires-python` | 加 `requires-python = ">=3.8"` |
| `unrecognized field 'license-expression'` | setuptools 太新 | 降级到 <68 |
| `unrecognized field 'license-file'` | twine 不兼容 PEP 639 | 降级 setuptools |
| `Bad credentials` | token 过期或格式不对 | 重新生成 PAT |
| `externally-managed-environment` | 系统 Python 保护 | 加 `--break-system-packages` |
| `Project not found` | 包名已存在 | 换名字或用 `--repository-url` 先试 test.pypi.org |
| `refusing to allow a PAT to create or update workflow` | Token 缺少 `workflow` 权限 | GitHub Token 设置中勾选 `workflow` |
| `400 Bad Request` | 版本号已在 PyPI 存在，不允许覆盖 | bump 版本号（pyproject.toml + __init__.py + setup.py）后重新构建上传 |
| `403 Forbidden` on upload | Token 作用域不匹配项目名或仅限 test.pypi.org | 确认 PyPI Token 的 Project scope 与包名一致，或改为 Entire account |

---

## 十一、☑️ 发布检查清单

### 发布前（准备阶段）

- [ ] CHANGELOG.md 存在，格式正确
- [ ] 版本号：pyproject.toml / setup.py / __init__.py 三者一致
- [ ] 文档一致性检查通过（README/RUNTIME/CLI/API 表完整）
- [ ] pyproject.toml 包含 `requires-python` 和 `license`
- [ ] setup.py 最小化（无配置重叠）
- [ ] .gitignore 覆盖 dist/ build/ *.egg-info .venv
- [ ] CI 配置文件已创建（.github/workflows/ci.yml）
- [ ] README 添加 CI 徽章
- [ ] `pip install -e ".[dev]"` 能成功安装
- [ ] `pytest tests/ -v` 全部通过
- [ ] CLI 入口正常工作：`your-cli --help`
- [ ] 构建验证通过：`python3 -m build && twine check dist/*`
- [ ] 安全检查通过：无硬编码 Token/密码
- [ ] 作者签名已同步（cli.py cmd_version / __init__.py / pyproject.toml）

### 发布中

- [ ] 合并到 master 分支
- [ ] 打 git tag：`git tag v<version> && git push origin v<version>`
- [ ] pip install build twine
- [ ] `rm -rf dist/ && python3 -m build && twine check dist/*`
- [ ] `twine upload dist/* -u __token__ -p TOKEN`
- [ ] 创建 GitHub Release：`gh release create v<version> -t "title" -F CHANGELOG.md`

### 发布后

- [ ] `pip install your-package` 验证安装
- [ ] `your-cli --help` 验证 CLI
- [ ] PyPI API 确认版本更新

---

## 十二、Red Flags

- ❌ **内部依赖未消除**：包不能依赖 `~/.hermes/` 路径，必须通过参数/环境变量配置
- ❌ **数据硬编码**：同义词表、工具路径等必须作为数据文件，不能写死在逻辑代码中
- ❌ **测试覆盖率不足**：至少 38+ 测试，含端到端覆盖率测试
- ❌ **忘记更新版本号**：三个地方要同步（pyproject.toml / setup.py / __init__.py）
- ❌ **缺少脚本入口**：pip install 后要能直接 `your-cli --query` 运行
- ❌ **循环依赖**：数据文件（synonyms.py）绝不能导入逻辑模块
- ❌ **setuptools 版本太新导致 PyPI 拒绝**：≥69 生成 PEP 639 元数据，twine 不兼容
- ❌ **文档落后于代码**：CLI 命令表/API 端点表/已知问题状态必须与代码同步
- ❌ **CI 推送被拒**：.github/workflows/* 需要 GitHub Token 有 workflow 权限
- ❌ **不检查构建警告**：deprecation 警告虽然不阻止构建，但应在发布前清理
