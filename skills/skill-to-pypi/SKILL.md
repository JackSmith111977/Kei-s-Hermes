---
name: skill-to-pypi
description: "将 Hermes 内部组件（skill/脚本/工具）打包为独立的 Python 开源项目。涵盖项目结构初始化、模块化重构、pyproject.toml/setup.py 配置、测试框架搭建、Git 版本管理、覆盖率目标设定、LICENSE 选择等完整流程。\n\n从一次实战中沉淀：SRA (Skill Runtime Advisor) 从单脚本 skill-advisor.py 转化为独立 GitHub 仓库的完整经验。"
version: 1.0.0
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
design_pattern: Pipeline + Generator
skill_type: Workflow
---

# 📦 Skill to PyPI · 独立开源项目打包指南 v1.0

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

### 2.2 setup.py（兼容方式）

```python
from setuptools import setup, find_packages
setup(
    name="sra-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["pyyaml>=5.1"],
    extras_require={"dev": ["pytest>=7.0"]},
    entry_points={"console_scripts": ["sra=your_package.cli:main"]},
    python_requires=">=3.8",
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

## 七、✅ 发布检查清单

在发布前检查以下项目：

- [ ] 包结构：`pip install -e .` 能成功安装
- [ ] CLI：`your-cli --help` 能正常显示
- [ ] 测试：`pytest tests/ -v` 全部通过
- [ ] README：包含安装、用法、快速开始
- [ ] LICENSE：已选择许可证（推荐 MIT）
- [ ] .gitignore：覆盖 Python 常见忽略模式
- [ ] 版本号：`__init__.py` 和 `pyproject.toml` 一致
- [ ] License 配置兼容：**不要用 PEP 639 新格式**（旧 twine/setuptools 不兼容）

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

## 八、Red Flags
### 发布前快速验证脚本

```bash
#!/bin/bash
set -e

echo "🔍 检查版本号..."
PYPROJ_VER=$(grep "^version" pyproject.toml | head -1 | cut -d'"' -f2)
INIT_VER=$(grep "__version__" your_package/__init__.py | cut -d'"' -f2)
echo "  pyproject.toml: $PYPROJ_VER"
echo "  __init__.py:    $INIT_VER"
[ "$PYPROJ_VER" = "$INIT_VER" ] || { echo "❌ 版本号不一致！"; exit 1; }

echo "🔧 构建..."
rm -rf dist/ build/ *.egg-info
python3 -m build

echo "✅ twine check..."
python3 -m twine check dist/*

echo "🧪 测试..."
pytest tests/ -q

echo ""
echo "✅ 一切就绪！可以发布了。"
echo "   上传命令: python3 -m twine upload dist/* -u __token__ -p 你的TOKEN"
```
## 八、发布到 PyPI（v1.1.0 新增）

### 8.1 前置准备

```bash
# 安装构建和发布工具
pip install build twine

# 需要 PyPI API Token：
# 1. 去 https://pypi.org/manage/account/token/ 登录（GitHub OAuth）
# 2. 创建 API Token（Scope 选 "Entire account"）
# 3. 保存 token （格式：pypi-xxxxxxxx）
```

### 8.2 构建

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

### 8.3 验证包内容

```bash
python3 -m twine check dist/*
# 如果有 WARNING 可以忽略，PyPI 接受新标准
# 如果 ERROR → 需要修复再上传
```

### 8.4 上传到 PyPI

```bash
# 上传到正式 PyPI
python3 -m twine upload dist/* -u __token__ -p pypi-xxxxxxxx

# 或先上传到 Test PyPI 试水
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/* -u __token__ -p pypi-xxxxxxxx
```

### 8.5 安装验证

```bash
# 从 PyPI 安装
pip install your-package

# 测试 CLI
your-package --help

# 测试导入
python -c "from your_package import YourClass; print('OK')"
```

### 8.6 常见构建错误

| 错误 | 原因 | 修复 |
|------|------|------|
| `License :: OSI Approved :: MIT License` **废弃** | setuptools>=72 不再接受 License classifier | 移除该 classifier，使用 `license = "MIT"` 字段 |
| `requires-python` not specified | PEP 621 要求显式声明 | 添加 `requires-python = ">=3.8"` |
| `license = {text = "MIT"}` **报错** | 旧版 dict 格式 | 改为 `license = "MIT"`（PEP 639 字符串表达式） |
| `InvalidDistribution: unrecognized field 'license-file'` | 新版 setuptools 自动生成，旧版 twine 不兼容 | 升级 twine 或忽略（PyPI 接受） |
| `ModuleNotFoundError: No module named 'build'` | 未安装 build 工具 | `pip install build` |

### 8.7 版本号管理策略

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

---

## 八、🛑 PyPI 发布实战排坑 v2.0

### 8.1 pyproject.toml 配置关键事项

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

### 8.2 解决方案对比

| 方案 | 操作 | 复杂度 | 推荐度 |
|------|------|--------|--------|
| **降级 setuptools** | `pip install 'setuptools<68'` | ⭐ 低 | ⭐⭐⭐ 推荐 |
| **删除 license 字段** | 只用 `License :: OSI Approved :: MIT License` classifier | ⭐ 低 | ⭐⭐⭐ 推荐 |
| **修复 wheel metadata** | 手动解压修改 METADATA 文件 | ⭐⭐⭐ 中 | ⭐ 不推荐 |
| **升级 twine 到最新** | `pip install --upgrade twine` | ⭐ 低 | ⭐⭐ 当前最新版仍不兼容 |

### 8.3 实战验证流程

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

#### 第 3 步：构建（降级版）

```bash
# 先用旧版 setuptools 避免 PEP 639 兼容问题
pip install 'setuptools<68'

# 构建
rm -rf dist/ build/ *.egg-info
python3 -m build

# 检查 METADATA 中是否有 License-Expression 字段
python3 -c "
import zipfile
with zipfile.ZipFile('dist/*.whl') as z:
    for name in z.namelist():
        if name.endswith('METADATA'):
            content = z.read(name).decode()
            for line in content.split('\n'):
                if 'license' in line.lower():
                    print(line)  # 确认没有 License-Expression
"
```

#### 第 4 步：上传

```bash
# 安装 twine
pip install twine

# 上传 wheel（优先）
twine upload dist/*.whl -u __token__ -p 你的PyPI_TOKEN

# 如果需要上传 sdist
twine upload dist/*.tar.gz -u __token__ -p 你的PyPI_TOKEN
```

#### 第 5 步：恢复环境

```bash
# 恢复最新版 setuptools
pip install 'setuptools>=61.0'
```

### 8.4 发布后验证

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

### 8.5 已知问题 / 兼容性

| 环境 | 问题 | 处理 |
|------|------|------|
| setuptools ≥69 | 自动生成 `License-Expression` 字段 | 降级到 <68 |
| twine 6.2.0 | 不识别 PEP 639 新字段 | 同上 |
| Python 3.12 | `pip install build` 可能报 `externally-managed-environment` | 加 `--break-system-packages` |
| shell 屏蔽 token | `***` 屏蔽变量 | 用文件存储或手动输入 |

### 8.6 发布的 pyproject.toml 黄金模板

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

### 8.7 常见错误速查

| 错误信息 | 原因 | 修复 |
|----------|------|------|
| `'NoneType' object is not iterable` | 缺少 `requires-python` | 加 `requires-python = ">=3.8"` |
| `unrecognized field 'license-expression'` | setuptools 太新 | 降级到 <68 |
| `unrecognized field 'license-file'` | twine 不兼容 PEP 639 | 降级 setuptools |
| `Bad credentials` | token 过期或格式不对 | 重新生成 PAT |
| `externally-managed-environment` | 系统 Python 保护 | 加 `--break-system-packages` |
| `Project not found` | 包名已存在 | 换名字或用 `--repository-url` 先试 test.pypi.org |

---

## 九、☑️ 发布检查清单

- [ ] 版本号：`pyproject.toml` / `setup.py` / `__init__.py` 三者一致
- [ ] pyproject.toml 包含 `requires-python`
- [ ] License 用 classifier 方式（`License :: OSI Approved :: MIT License`）
- [ ] README.md 存在且格式正确
- [ ] `.gitignore` 覆盖 `dist/ build/ *.egg-info .venv`
- [ ] `pip install -e .` 能成功安装
- [ ] `pytest tests/ -v` 全部通过
- [ ] CLI 入口有定义：`your-cli --help`
- [ ] 构建产物检查：`python3 -m build`
- [ ] 修复 setuptools 版本：降级到 <68
- [ ] 上传：`twine upload dist/*.whl -u __token__ -p TOKEN`
- [ ] 恢复 setuptools 版本
- [ ] 打 git tag：`git tag v1.0.0 && git push origin v1.0.0`

---

## 十、Red Flags

- ❌ **内部依赖未消除**：包不能依赖 `~/.hermes/` 路径，必须通过参数/环境变量配置
- ❌ **数据硬编码**：同义词表、工具路径等必须作为数据文件，不能写死在逻辑代码中
- ❌ **测试覆盖率不足**：至少 38+ 测试，含端到端覆盖率测试
- ❌ **忘记更新版本号**：三个地方要同步（`pyproject.toml` / `setup.py` / `__init__.py`）
- ❌ **缺少脚本入口**：`pip install` 后要能直接 `your-cli --query` 运行
- ❌ **循环依赖**：数据文件（synonyms.py）绝不能导入逻辑模块
- ❌ **setuptools 版本太新导致 PyPI 拒绝**：≥69 生成 PEP 639 元数据，twine 不兼容
