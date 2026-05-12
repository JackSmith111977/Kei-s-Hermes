---
name: sra-dev-workflow
description: "SRA 项目开发工作流 — 版本管理(setuptools-scm) + CI/CD(GitHub Actions) + Reality Check 门禁 + doc-alignment 全生命周期。SRA 开发任务的强制流程。"
version: 1.3.0
triggers:
  - sra 开发
  - sra 版本
  - sra 发布
  - sra ci
  - sra workflow
  - 开发工作流改进
  - 版本号管理
  - github actions
  - reality check
  - 分析前对齐
depends_on:
  - doc-alignment
  - development-workflow-index
  - github-project-ops
  - sdd-workflow
  - sra-qa-workflow
skill_type: workflow
design_pattern: pipeline
---

# SRA 开发工作流 v5.0

> 整合: setuptools-scm 版本管理 + GitHub Actions CI/CD + Reality Check 门禁 + QA 工作流 (L0-L4)

## 📐 QA 门禁速查

> 详细 QA 工作流见 `sra-qa-workflow` skill

| 层级 | 名称 | 时机 | 命令 | 阻断 |
|:----|:-----|:-----|:-----|:----:|
| L0 | 静态分析 | per-commit | `ruff check` + `syntax-check` + fixture integrity | ✅ |
| L1 | 单元测试 | per-commit | `pytest tests/ -q` | ✅ |
| L2 | 集成测试 | pre-merge | `pytest test_daemon_http.py test_cli.py ...` | ✅ |
| L3 | 系统测试 | pre-release | `pytest test_concurrency.py test_force.py ...` | ✅ |
| L4 | 发布门禁 | pre-publish | version + CHANGELOG + build + smoke | ✅ |

**QA 决策**: `skill_view(name="sra-qa-workflow")` → 按变更类型选门禁

## 🔍 Reality Check — SRA 实战步骤

```bash
# 1. 看代码最近做了什么
git log --oneline -30 | head -15

# 2. 跑测试看实际测试数
python -m pytest tests/ -q --tb=short -o "addopts=" 2>&1 | tail -3

# 3. 检查版本号
python -c "from skill_advisor import __version__; print(f'Version: {__version__}')"

# 4. 检查关键文件（不要信文档说"不存在"的文件）
for f in tests/test_dropin.py tests/test_adapters.py .github/workflows/ci.yml; do
  [ -f "$f" ] && echo "✅ $f" || echo "❌ $f missing"
done

# 5. 运行 ruff lint 检查
ruff check skill_advisor/ tests/

# 6. doc-alignment 验证
python3 ~/.hermes/scripts/generate-project-report.py --data docs/project-report.json --verify

# 7. 📋 Backlog 状态检查 — 分析下一开发任务
#    7a. SDD Spec 状态 — 哪些在审阅/进行中？
python3 ~/.hermes/skills/dogfood/sdd-workflow/scripts/spec-state.py list 2>/dev/null || echo "⚠️  SDD 状态不可用"

#    7b. Epic 进度 — 已完成 vs 待办 stories？
#        grep "status.*completed\|status.*pending\|status.*in_progress" docs/EPIC-*.md
echo "=== Epic 完成度 ==="
for epic in docs/EPIC-*.md; do
  [ -f "$epic" ] && echo "$epic: $(grep -c '\[x\]' "$epic" 2>/dev/null || echo 'N/A') ACs checked"
done

#    7c. Sprint 进度 — 当前 Sprint 还剩多少？
python3 -c "
import json
try:
    with open('docs/project-report.json') as f:
        d = json.load(f)
    for s in d.get('sprint_history', []):
        print(f'  {s.get(\"sprint\",\"?\")}: {s.get(\"stories_completed\",\"?\")}/{s.get(\"stories_total\",\"?\")} stories → {s.get(\"version\",\"?\")}')
    print(f'  📌 当前里程碑: {json.dumps(d.get(\"milestone\",{}), indent=2)}')
except Exception as e:
    print(f'  ⚠️  project-report.json 不可读: {e}')
"

#    7d. 检查 project-report.json 中声明的测试数与实际是否一致
python3 -c "
import json
try:
    with open('docs/project-report.json') as f:
        d = json.load(f)
    declared = d.get('tests', {}).get('passing', 0)
    print(f'  📊 project-report 声明: {declared} passing')
except Exception as e:
    print(f'  ⚠️  无法读取 project-report: {e}')
echo '  ⚠️  注意: project-report.json 可能滞后于实际测试结果。以 pytest 输出为准。'
```

## 📋 项目状态分析与下一 Story 选择

### 🎯 Phase 0.5: QA 影响评估（新增）

在每个开发任务开始前，确定所需 QA 门禁等级：

```bash
# 加载 QA 工作流
# skill_view(name="sra-qa-workflow")

# 根据变更类型选择门禁
qa_assess() {
    case "$1" in
        bugfix)  echo "🔧 QA gates: L0+L1";;
        feature) echo "✨ QA gates: L0+L1+L2";;
        refactor) echo "🔨 QA gates: L0+L1+L2";;
        arch)    echo "🏗️  QA gates: L0+L1+L2+L3";;
        release) echo "📦 QA gates: L0+L1+L2+L3+L4";;
        *)       echo "❓ QA gates: L0+L1 (default)";;
    esac
}
```

**变更类型判断标准**：

| 变更类型 | 判断标准 | 示例 |
|:---------|:---------|:------|
| 🔧 bugfix | 改 ≤3 文件，不涉及接口变更 | 修一个类型错误、日志修正 |
| ✨ feature | 改 1-5 文件，涉及新增功能 | 加一个新 CLI 参数、新 API 端点 |
| 🔨 refactor | 改 3-10 文件，不改变外部行为 | 函数重命名、拆分模块 |
| 🏗️ arch | 改 5+ 文件，涉及接口/行为变更 | 新增 ROUTER、修改推荐引擎 |
| 📦 release | 版本号变更、CHANGELOG、发布 | git tag v*.*.* 推送 |

### 🎯 Phase 1.7: QA Plan（新增）

在 SDD Spec 获批后、开发开始前，为 Story 定义 QA Plan：

```bash
# QA Plan 模板:
# 1. 变更类型: [bugfix/feature/refactor/arch/release]
# 2. 必需门禁: [L0/L1/L2/L3/L4]
# 3. 新增测试: [哪些测试文件需要新增/修改]
# 4. 回归风险: [哪些模块可能被影响]
# 5. flaky 标记: [已知 flaky 测试列表]
```

---

在完成 Reality Check 后、进入 Phase 1 前，需要明确「下一步做什么」。本流程将代码级 Reality Check 升级为**项目级 Triage**。

### 分析流程

```text
[现实检查结果]
    ↓
1️⃣ 读 Epic 文档 → 确定总进度（% completed vs pending）
2️⃣ 读 Sprint 计划 → 对比当前 Sprint 的目标 stories
3️⃣ 查 SDD Spec 列表 → 是否有未完成的 Spec 卡在 review 状态？
4️⃣ 查依赖链 → 候选 Story 的依赖是否已完成？
5️⃣ 查优先级 → P0 > P1 > P2，优先无依赖的高优项
6️⃣ 推荐 → 给出 1-2 个候选给主人确认
```

### 实战命令

```bash
# 1. Epic 完成度检查
echo "=== Epic 完成度 ==="
for epic in docs/EPIC-*.md; do
  if [ -f "$epic" ]; then
    total=$(grep -cE '^\|.*SRA-.*P[0-9].*\|' "$epic" 2>/dev/null || echo 0)
    done=$(grep -cE '^\|.*✅.*SRA-.*P[0-9].*\|' "$epic" 2>/dev/null || echo 0)
    echo "  $(basename $epic .md): $done/$total stories completed"
  fi
done

# 2. SDD Spec 状态 — 检查未完成的 Spec
python3 ~/.hermes/skills/dogfood/sdd-workflow/scripts/spec-state.py list 2>/dev/null

# 3. 检查候选 Story 是否有 Spec 文件
for sid in SRA-003-15 SRA-003-16; do
  if [ -f "docs/stories/$sid.md" ]; then
    status=$(grep '^status:' "docs/stories/$sid.md" | head -1)
    echo "  📄 $sid: $status"
  else
    echo "  ❌ $sid: 无 Spec"
  fi
done
```

### ⚠️ 重要 Insight：不要轻信 Epic 文档的状态标记

**问题**：EPIC-003 文档顶部标记为 `status: ✅ 全部完成 (v2.0.0)`，但逐项检查各 Story 的验收标准后，实际完成率仅约 **40%**（13/36 个验收项勾选）。

**根因分析**：
| 原因 | 说明 |
|:-----|:------|
| 验收标准粒度不一致 | 有些 Story 5 个 AC，有些 10 个——粗粒度的 Story 更容易显示"完成" |
| 状态标记在文档顶部 | 容易被复制粘贴到新文档，状态与实际脱节 |
| 无自动门禁 | 没有脚本检查 Story AC 勾选率与状态标记的一致性 |
| 「完成」定义模糊 | 有时是「代码实现完成」而不是「所有验收标准通过」 |

**应对策略**：
```bash
# 🔴 必做：Epic 状态分析时，不要只看顶部 status 字段
#     要逐项检查每个 Story 的验收标准勾选情况

# 方法 1: 快速统计 AC 完成率
grep -c '\[x\]' docs/EPIC-003-v2-enforcement-layer.md    # 已勾选 AC
grep -c '\[ \]' docs/EPIC-003-v2-enforcement-layer.md   # 未勾选 AC
# 比较两者比例，不要信任顶部的「全部完成」

# 方法 2: 按 Story 维度逐项检查
for story_id in $(grep -oP 'SRA-\d+-\d+' docs/EPIC-003-v2-enforcement-layer.md | sort -u); do
    echo "=== $story_id ==="
    grep -A5 "### Story.*$story_id" docs/EPIC-003-v2-enforcement-layer.md | head -6
done

# 方法 3: 检查 AC 数量 vs 已完成勾选
python3 -c "
import re
with open('docs/EPIC-003-v2-enforcement-layer.md') as f:
    content = f.read()
stories = content.split('### Story')
for s in stories:
    if not s.strip(): continue
    story_id = re.search(r'SRA-\d+-\d+', s)
    checked = len(re.findall(r'\[x\]', s))
    unchecked = len(re.findall(r'\[ \]', s))
    total = checked + unchecked
    if total > 0:
        print(f'  {story_id.group() if story_id else \"?\":20s} {checked}/{total} AC ({checked*100//total if total else 0}%)')
"
```

**经验法则**：看到「全部完成」标记时，**必须先验证验收标准完成率**。如果完成率 <80%，这个标记不可信。

### 决策矩阵

| 场景 | 推荐动作 |
|:-----|:---------|
| Sprint 有未完成 stories | 接续 Sprint 计划 |
| Epic 有 P0/P1 pending stories | 优先完成无依赖的 P0/P1 |
| 多个候选并列 | 选择对项目质量影响最大的（如测试/配置/文档改进） |
| 全部已完成 | 规划下一 Sprint / 下一 Epic |

### project-report.json 交叉验证

**⚠️ 已知问题**: `project-report.json` 中的 `tests.passing` 数量可能滞后于实际测试结果。例如本项目遇到过 project-report 声明 `290 passing` 但实际 `289 passed, 1 failed`（flaky HTTP 测试）的情况。

**应对策略**:
- 始终以 `pytest` 实际输出为真实基线
- 发现差异时更新 project-report.json 以反映现实
- flaky 测试应标记（在项目报告或文档中注明）

---

## ⚠️ CI/CD 常见陷阱

### 陷阱 0: setuptools-scm 在 CI 中版本号解析失败（2026-05-11 新增）

**现象**：push tag 后 CI 构建出的 wheel 版本号是 `0.0.0.dev0` 而不是预期的 `v1.4.0`。

**根因**：setuptools-scm 在 CI 环境中无法正确找到 git tag，导致 fallback 到 `0.0.0.dev0`。

**完整调试记录**见 `references/setuptools-scm-ci-version.md`。

**快速定位命令**：
```bash
# 在 CI 的 build step 中添加 debug 输出
git describe --dirty --tags --long      # 预期: v1.4.0-0-g<sha>
git describe --dirty --long             # 对比: 是否返回了其他 tag？
git tag -l 'v*' --sort=-version:refname | head -5
git cat-file -t v1.4.0                  # commit=轻量, tag=附注
```

**修复方案（已验证可行）**：

方式一：直接写 `_version.py`（简单有效）
```yaml
- name: 🏷️ Set version from tag
  run: |
    VERSION="${GITHUB_REF_NAME#v}"
    mkdir -p skill_advisor
    echo "# Auto-generated by release workflow" > skill_advisor/_version.py
    echo "version = \"$VERSION\"" >> skill_advisor/_version.py
```

方式二：替换 pyproject.toml 动态版本为静态版本（彻底绕过 setuptools-scm）
```yaml
- name: 🔨 Build wheel + sdist
  run: |
    pip install build
    VERSION="${GITHUB_REF_NAME#v}"
    python scripts/set_version.py "$VERSION"
    python -m build
```

**⚠️ 为什么 `SETUPTOOLS_SCM_PRETEND_VERSION` 不总是有效？**
- `python -m build` 创建隔离环境构建，环境变量可能无法传递到构建子进程
- 即使 CI log 显示 `SETUPTOOLS_SCM_PRETEND_VERSION=1.4.0`，setuptools-scm 在隔离环境下仍可能忽略它

**生成 wheel 文件名格式**：`sra_agent-{version}-py3-none-any.whl`

**验证方法**：
```bash
# 查看构建产物
ls -la dist/
# 预期: sra_agent-1.4.0-py3-none-any.whl
```

### 陷阱 0c: 本地 editable install 后版本显示 0.0.0.dev0（2026-05-12 新增）

**现象**：从 GitHub clone 后执行 `pip install -e .`，`sra version` 或 `pip show sra-agent` 显示版本为 `0.0.0.dev0`，但 `git describe --tags` 正确返回 `v2.0.3`。

**根因**：setuptools-scm 在 `pip install -e .`（editable install）模式下，不会自动将版本写入 `version_file` 中指定的文件（如 `skill_advisor/_version.py`）。build 时作为临时依赖安装的 setuptools-scm 不持久化，导致运行时找不到版本信息，fallback 到 `0.0.0.dev0`。

**快速诊断命令**：
```bash
# 1. 检查 git tag 是否正确
git describe --tags --long          # 预期: vX.Y.Z-N-g<SHA>

# 2. 检查 _version.py 是否存在
cat skill_advisor/_version.py       # 预期: __version__ = 'X.Y.Z'

# 3. 检查 setuptools-scm 能否正确提取版本
python3 -c "from setuptools_scm import get_version; print(get_version())"
# 如果 ModuleNotFoundError → 先安装 setuptools-scm
```

**修复方案（已验证可行）**：
```bash
# Step 1: 安装 setuptools-scm（editable 时仅 build 依赖，不持久化）
pip install setuptools-scm

# Step 2: 测试 setuptools-scm 能否正确解析版本
python3 -c "from setuptools_scm import get_version; print(get_version())"
# 预期输出: X.Y.Z（如 2.0.3）

# Step 3: 手动生成 _version.py
python3 -c "
from setuptools_scm import get_version
v = get_version()
with open('skill_advisor/_version.py', 'w') as f:
    f.write(f'__version__ = {v!r}\n')
    f.write(f'version = {v!r}\n')
"

# Step 4: 强制重新安装 editable 模式
pip install -e . --force-reinstall --no-deps

# Step 5: 验证
sra version  # 预期: SRA — Skill Runtime Advisor vX.Y.Z
```

**⚠️ 关键点**：
- `pip install -e . --force-reinstall --no-deps` 是必要步骤——仅生成 `_version.py` 不够，pip 的 egg-info metadata 缓存了旧版本号
- 如果在非 SRA 项目（包名不同）遇到同样问题，原理相同：找到 `version_file` 对应的路径，手动生成即可
- CI 中不会出现此问题（CI 用 `python -m build` 完整构建，setuptools-scm 在隔离环境中正常工作）

### 陷阱 0d: 模块名从 `sra_agent` 变更为 `skill_advisor`（2026-05-12 新增）

**背景**：SRA 项目的 Python 包名在 v2.0.0 重构时从 `sra_agent` 变更为 `skill_advisor`。

**影响**：
| 场景 | 旧写法 ❌ | 新写法 ✅ |
|:-----|:----------|:----------|
| 导入 | `from sra_agent import SkillAdvisor` | `from skill_advisor import SkillAdvisor` |
| CLI 入口 | `sra_agent.cli:main` | `skill_advisor.cli:main` |
| 版本文件 | `sra_agent/_version.py` | `skill_advisor/_version.py` |
| PyPI 包名 | `sra-agent`（不变） | ✅ `sra-agent`（不变） |

**注意事项**：
- PyPI 包名 `sra-agent` 未变，`pip install sra-agent` 仍正确
- 但源码目录和导入路径已变——引用 SRA 模块的旧脚本需更新导入语句
- 如果本地残留旧版 `sra_agent/` 目录的 editable install，需先 `pip uninstall sra-agent -y` 再安装新版

**快速验证**：
```bash
# 确认安装的是新版结构
python3 -c "import skill_advisor; print(skill_advisor.__file__)"
# 预期指向 skill_advisor/ 目录

# 旧版 sra_agent 应已不存在
python3 -c "import sra_agent" 2>&1  # 预期: ModuleNotFoundError
```

### 陷阱 0b: PyPI Trusted Publisher 配置不正确（2026-05-11 新增）

**现象**：push tag 后 CI Release 流水线的 PyPI 发布步骤报错：
```
❌ Trusted publishing exchange failure
   invalid-publisher: valid token, but no corresponding publisher
```

**根因**：PyPI 的 Trusted Publisher（OIDC）配置字段与 GitHub Actions CI 的实际值不匹配。

**OIDC 字段对齐表**：

| PyPI 表单字段 | OIDC token 字段 | SRA 正确值 | 错误值示例 |
|:--------------|:----------------|:-----------|:-----------|
| PyPI Project Name | `pypi-project-name` | `sra-agent` | `Skill View` |
| Owner | `repository_owner` | `JackSmith111977` | `Kei` |
| Repository name | `repository` | `Hermes-Skill-View` | `repository` |
| Workflow name | `workflow` | `release.yml` | `workflow.yml` |

**字段映射详解**：

| # | 字段 | 真实含义 | 常见误区 | 数据来源 |
|:---:|:-----|:---------|:---------|:---------|
| ① | **PyPI Project Name** | `pyproject.toml` 中的 `[project].name`，不是 README 里的项目名或 PyPI 显示名 | 把 README 里的项目名填进去 | `cat pyproject.toml \| grep "^name ="` |
| ② | **Owner** | **GitHub** 用户名/组织名，不是 PyPI 用户名 | 填了 pyproject.toml 中的 author 名 | `git remote -v \| head -1` |
| ③ | **Repository name** | GitHub 仓库名（URL 中 Owner 后面的部分） | 填了占位符或其他项目的仓库名 | `basename $(git rev-parse --show-toplevel)` |
| ④ | **Workflow name** | `.github/workflows/` 下的文件名（含 `.yml`） | 填了 generic 名字 | `ls .github/workflows/release.yml` |

**修复步骤**：

1. 登录 https://pypi.org/manage/account/publishing/
2. 用上表正确值重新配置 Trusted Publisher
3. 删除已有 tag + 重打：
   ```bash
   git tag -d v1.4.0
   git push origin :refs/tags/v1.4.0
   git tag v1.4.0
   git push origin v1.4.0
   ```

**验证方法**：配置后 CI 重新运行应看到 `🚀 Publishing sra-agent-1.4.0.tar.gz` → `🚀 Publish to PyPI ✅`

详细的调试记录见 `references/pypi-trusted-publisher.md`。

### 陷阱 1: pyproject.toml 配置不正确

| 错误 | 后果 | 修复 |
|:-----|:-----|:-----|
| `version_file` + `write_to` 重复 | setuptools-scm warning | 只用 `version_file` |
| `git_archive = true` | 无效选项，构建失败 | 删除（非 setuptools-scm 选项） |
| `[tool.mypy] python_version = "3.8"` | mypy 报错（3.8 不支持） | 改为 `"3.10"` |
| `[tool.ruff]` 顶级 `per-file-ignores` | 弃用警告 | 改为 `[tool.ruff.lint.per-file-ignores]` |

### 陷阱 2: ruff lint 未提前修复

创建 CI 工作流后，务必先在本地跑 `ruff check`：

```bash
# 自动修复可修的（320+ 常见问题可自动修复）
ruff check --fix .

# 修复剩余不可自动修的
ruff check --unsafe-fixes --fix .

# 配置 per-file-ignores 允许测试文件的合理模式
# 见 pyproject.toml [tool.ruff.lint.per-file-ignores]
```

### 陷阱 3: CI YAML 语法错误

```bash
# 在提交前验证 YAML 语法
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('✅ valid')"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml')); print('✅ valid')"
```

### 陷阱 4: GitHub Actions 版本过时

| Action | 当前推荐版本 | 不推荐 |
|:-------|:------------|:-------|
| `actions/checkout` | `@v4` | `@v3` 以下 |
| `actions/setup-python` | `@v5` | `@v4` 以下 |
| `actions/upload-artifact` | `@v4` | `@v3` 以下 |
| `pypa/gh-action-pypi-publish` | `@release/v1` | 固定 commit hash |

**只有验证通过后，才能信任文档的声明。**

## 🔄 版本管理

**核心原则**: 版本号从 git tag 提取，但不在构建时依赖 setuptools-scm 的 `git describe`（CI 中不可靠）

`__init__.py` 中的 `__version__` 由三层层级推导：
1. `_version.py`（built 包的 setuptools-scm 生成物）
2. `importlib.metadata`（pip install 后的 metadata）
3. `git describe --tags`（开发环境 fallback）

**⚠️ CI 发布流程**: 不再依赖 setuptools-scm 自动检测 tag，改为三重保险（见下方「CI/CD 常见陷阱 > 陷阱 0」）：
- 写 `skill_advisor/_version.py`
- 设置 `SETUPTOOLS_SCM_PRETEND_VERSION` 环境变量（后备）
- 用 `scripts/set_version.py` 替换 `pyproject.toml` 中的动态版本为静态版本

### 版本生命周期

| 阶段 | git tag | 显示的版本 | CI/CD 行为 |
|:-----|:--------|:-----------|:-----------|
| 开发中 | 无新 tag | `v1.3.0-6-ga1b2c3d` 或 fallback | CI 跑测试 |
| 预发布 | `v1.4.0rc1` | `v1.4.0rc1` | CI + 可选 PyPI |
| 正式发布 | `v1.4.0` | `v1.4.0` | CI + PyPI + GitHub Release |

### 版本操作

```bash
# 查看当前版本
python -c "from skill_advisor import __version__; print(__version__)"

# ⚠️ 必须用附注标签（带 -a）！轻量标签在 CI 中不可靠
# 发布新版本：
git tag -a v1.4.0 -m "Release v1.4.0 — 版本说明"
git push origin v1.4.0       # 推送 tag → 自动触发 CI/CD

# GitHub Release 手动创建（如果 CI/CD 尚未自动创建，或需要立即发布）
gh release create v1.4.0 -t "v1.4.0" --generate-notes
# 注意：项目偏好 Release 标题只保留版本号，不加描述文字（-t "vX.Y.Z"）

# 预发布（同样必须用附注标签）
git tag -a v1.4.0rc1 -m "Release candidate v1.4.0rc1"
git push origin v1.4.0rc1

# ⚠️ 不要用 git tag v1.4.0（轻量标签）—— 历史教训：
#   setuptools-scm 在开发环境能找到轻量标签，但在 CI 中可能失败
```

### 故障恢复（发布失败时）

```bash
# 1. 删除远程 tag
git tag -d v1.4.0
git push origin :refs/tags/v1.4.0

# 2. 修复问题（修改代码/工作流）

# 3. 重新打 tag + 推送
git tag -a v1.4.0 -m "Release v1.4.0 — 版本说明"
git push origin v1.4.0
```

> ⚠️ 删除 tag 后重打不会自动删除 GitHub Release。如有已创建的 Release，需要在 GitHub 上手动删除再重试。

## ⚙️ CI/CD 流水线

### CI（每次 push/PR）

`.github/workflows/ci.yml` — 自动执行：
1. 🔬 **syntax-check** — Python 3.9 语法兼容性门禁（2026-05-12 新增）
   - `ast.parse` 验证所有 `.py` 文件可被 Python 3.9 解析
   - 正则扫描 PEP 604 联合类型（`dict | None` 等 3.10+ 特性）
   - 防止 `requires-python` 与代码语法特性脱节
2. 🧪 **pytest** — 全量测试（多 Python 版本矩阵: 3.9/3.10/3.11/3.12）
3. 🧹 **ruff** — lint 检查
4. 🔤 **mypy** — 类型检查（当前 continue-on-error）

### Release（推送 tag）

`.github/workflows/release.yml` — 自动执行：
1. 📦 `python -m build` — 构建 wheel + sdist
2. 🚀 `pypa/gh-action-pypi-publish` — 发布到 PyPI
3. 📝 `gh release create` — 创建 GitHub Release

## 📐 开发前门禁

开发前必须经过：

```
[Phase 0] Reality Check
  ├── git log --oneline -30
  ├── pytest --collect-only
  ├── doc-alignment --verify
  └── version check
       ↓ pass
[Phase 1] skill_finder + pre_flight
  ├── pre_flight.py → BLOCKED? → 停！
  └── skill_finder.py → ≥30分 → 加载
       ↓ pass
[Phase 1.5] 测试模式发现 ← 🔴
  ├── 扫描 tests/ 下已有测试文件的 fixture 模式
  │   grep -rn "FIXTURES_DIR\|fixtures/skills\|_all_yamls" tests/ 2>/dev/null
  ├── 检查 tests/fixtures/ 数据是否可用（重点是已有 fixture 能否替代运行时依赖）
  ├── 【不要幻觉文件名！】引用文件前先 read_file 确认存在
  └── 参考 tests/TEST-DATA-MANIFESTO.md

[Phase 1.6] SDD Spec 门禁 ← 🔴（由 sdd-workflow skill 驱动）
  ├── 自动执行门禁检查：
  │   python3 ~/.hermes/skills/sdd-workflow/scripts/spec-gate.py enforce "<task>"
  │   if [ $? -ne 0 ]; then
  │       echo "🛑 SDD 门禁拦截！先创建 Spec"
  │       echo "   模板: docs/STORY-TEMPLATE.md"
  │       exit 1
  │   fi
  ├── 复杂任务（3+ 文件/跨模块）→ 必须用 docs/STORY-TEMPLATE.md 创建 Story Spec
  ├── 简单任务（1-2 文件/小修复）→ 可跳过但向主人说明
  └── 🔴 铁律: 复杂任务没有获批 Spec 就写代码 = P0 违规
       ↓ pass
[Phase 2] 开发
  └── follow development-workflow-index 决策树
       │
       │ 对每个 Task:
       │   ┌──────────────────────────────────────────────┐
       │   │ Phase 2.5: QA Verify（新增）                 │
       │   │  1. Task 完成后运行 L0 门禁                  │
       │   │  2. 运行关联测试（新功能→新增测试通过）      │
       │   │  3. 全量测试 → 确认不退化                    │
       │   │  4. FLAG: 是否有新 flaky 出现？              │
       │   └──────────────────────────────────────────────┘
       ↓ pass
[Phase 3] 提交前对齐
  │
  ├── Phase 3.5: QA Gate Report（新增）
  │   ├── 按变更类型运行所有必需 QA 门禁
  │   ├── python3 scripts/qa-status.py --gates L0,L1,L2
  │   ├── 确认所有门禁通过
  │   └── 如有门禁失败 → 修复，不提交
  │
  ├── 🎯 AC 审计 ← 🔴 新增！防止文档漂移
  │   ├── 运行 python3 scripts/ac-audit.py check docs/EPIC-*.md
  │   ├── 检查是否有「代码已实现但文档未勾选」的 AC
  │   ├── 如有 → 手动勾选或运行 sync 模式：
  │   │   python3 scripts/ac-audit.py sync docs/EPIC-*.md --apply
  │   └── 确认 dashboard 显示完成率 100%：
  │       python3 scripts/ac-audit.py dashboard docs/EPIC-*.md
  │
  ├── doc-alignment 5步协议
  ├── project-report.json + HTML 更新
  ├── CHANGELOG.md 同步
  ├── 全量测试（本地 + CI 环境差异检查）
  └── 代码+文档同一次提交
```

## 📋 Sprint 开始/结束检查清单

### Sprint 开始时

- [ ] git pull --rebase 确保最新
- [ ] Reality Check: git log + pytest + doc-alignment --verify
- [ ] 写 Sprint 计划（.hermes/plans/）
- [ ] 更新 project-report.json Sprint 条目
- [ ] 确认版本号（setuptools-scm 自动）

### Sprint 结束时

- [ ] 全量测试通过（pytest -q）
- [ ] AC 审计：运行 python3 scripts/ac-audit.py check docs/EPIC-*.md 确认无漂移
- [ ] Epic 状态文档更新（`docs/EPIC-*.md` 的 status + completed_at）
- [ ] doc-alignment 5步对齐
- [ ] project-report.json + HTML 生成
- [ ] CHANGELOG.md Sprint 条目
- [ ] 所有代码+文档已提交
- [ ] 推送确认 CI 通过
- [ ] 如发布: git tag + push

## 🧪 测试数据策略 — 从真实技能提取的 Fixture

> **核心原则**: 测试数据应来自真实 Hermes 技能，而不是运行时依赖 `~/.hermes/skills`。

### Fixture 目录结构

```
tests/fixtures/
├── skills/                     # 317 个从真实 Hermes 技能提取的 SKILL.md 目录
│   ├── productivity__ocr-and-documents/ocr-and-documents/SKILL.md
│   ├── pdf-layout__SKILL/pdf-layout/SKILL.md
│   └── ...
├── skills_yaml/                # 314 个纯 YAML frontmatter 文件（原始提取）
│   ├── _all_yamls.json         # 313 个聚合后的真实技能记录
│   └── productivity__google-workspace__SKILL.yaml
└── _all_yamls.json             # 同上（快捷入口）
```

### 使用方式（正确示范 ✅）

```python
# ✅ 从 fixture 加载，不依赖 ~/.hermes/skills
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "skills")

advisor = SkillAdvisor(skills_dir=FIXTURES_DIR)
advisor.refresh_index()  # 317 个技能可被索引
```

**参考实现**: `tests/test_matcher.py::TestAdvisor` 中的 `setup_method()`。

### 错误示范 ❌（boku 在 SRA-003-05 中犯的错）

```python
# ❌ 运行时依赖 ~/.hermes/skills，CI 环境没有就 skip
hermes_skills = os.path.expanduser("~/.hermes/skills")
if os.path.isdir(hermes_skills):
    return SkillAdvisor(skills_dir=hermes_skills, ...)
return SkillAdvisor(data_dir=str(tmp_path))  # 没数据，测试无效
```

### 开发新测试时的检查清单

在 SRA 项目中写任何新测试前，必须检查：

- [ ] `tests/fixtures/skills/` 是否有现成的 SKILL.md 数据可用？
- [ ] 现有测试（`test_matcher.py`、`test_coverage.py`）使用了什么 Fixture 模式？
- [ ] 是否需要额外从 Hermes 技能中提取新数据？还是现成的 317 个 skill 已足够？
- [ ] 你的测试是否在本地和 CI 中行为一致？不依赖 `~/.hermes/skills`？

### ⚠️ 陷阱：幻觉文件存在

boku 在 SRA-003-05 开发中犯了严重的幻觉错误——以为 `tests/contract_formatter.py` 存在 `skill_yaml_fixture()` 函数，但实际上这个文件从来不存在。

**预防措施:**
- 引用文件前先 `read_file` 或 `ls` 确认存在
- 不要说「我记得有 XX 函数」——让代码告诉你有什么
- 使用 `search_files` 或 `grep -rl` 全局搜索关键词确认存在性

## ✅ 最终验证步骤（提交前强制执行）

每次 git commit 前，运行以下验证流水线：

```bash
# === 1. Ruff lint（全量检查）===
ruff check skill_advisor/ tests/
# 预期: "All checks passed!"

# === 2. 类型检查 ===
mypy skill_advisor/
# 预期: 无错误（已知问题逐步修复）

# === 3. 全量测试 ===
python -m pytest tests/ -q --tb=short -o "addopts="
# 预期: "290 passed"（或全部通过）

# === 4. 测试基础设施 & CI 环境差异检查 ===
# 在 CI 环境中缺少的依赖/目录可能导致测试失败：
# ┌────────────────────────┬──────────────────────────────────┐
# │ 在本地有但 CI 没有的   │ 应对策略                         │
# ├────────────────────────┼──────────────────────────────────┤
# │ ~/.hermes/skills/ 目录 │ 必须使用 tests/fixtures/ 替代    │
# │ Hermes Agent 本身      │ 纯单元测试不依赖 Hermes          │
# │ 某些 Python 版本       │ 矩阵测试 (3.9-3.12)              │
# └────────────────────────┴──────────────────────────────────┘

# 🔴 P0 门禁：扫描测试文件是否引用了运行时依赖
if [ -d "tests/fixtures" ]; then
    found=$(grep -rn "hermes/skills\|~/.hermes" tests/ --include="*.py" 2>/dev/null | grep -v "conftest.py" | head -5)
    if [ -n "$found" ]; then
        echo "❌ BLOCKED: 测试文件引用了运行时依赖 ~/.hermes/skills！"
        echo "$found"
        echo "   请使用 tests/fixtures/ 替代。见 tests/TEST-DATA-MANIFESTO.md"
        exit 1
    fi
fi

# ✅ 验证测试 fixture 完整性
python3 -c "
import os
d = 'tests/fixtures/skills'
if os.path.isdir(d):
    count = sum(1 for _,_,files in os.walk(d) for f in files if f == 'SKILL.md')
    assert count >= 300, f'Fixture 退化: {count} < 300'
    print(f'✅ Fixture 完整性: {count} skills')
"

# === 5. 版本一致性 ===
python -c "from skill_advisor import __version__; print(f'Version: {__version__}')"
# 预期: 从 git tag 自动推导的版本号

# === 6. AC 审计 ← 🔴 新增！检查文档是否滞后于代码 ===
python3 scripts/ac-audit.py check docs/EPIC-*.md 2>&1 || true
# 预期: 「漂移: 0 个 AC 滞后于代码」
# 如果有漂移 → 先同步再提交

# === 7. doc-alignment 验证 ===
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json --verify
# 预期: "✅ 数据与代码状态一致"
```

### CI 实战教训（2026-05-11）

| 教训 | 根因 | 预防措施 |
|:-----|:-----|:---------|
| setuptools-scm 在 CI 中版本号解析为 `0.0.0.dev0` | `git describe` 找不到 tag / 隔离环境 env var 不传播 | 显式写 `_version.py` + `scripts/set_version.py` 替换 pyproject.toml 静态版本 |
| `SETUPTOOLS_SCM_PRETEND_VERSION` 环境变量在隔离构建中无效 | `python -m build` 创建的隔离环境不传递父进程 env var | 用文件方式（`_version.py`/pyproject.toml 修改）替代环境变量 |
| CI 没有 Hermes 技能目录 → 契约测试失败 | `test_contract.py` 使用 `~/.hermes/skills` 而非 `FIXTURES_DIR` | 使用 fixture 数据，不依赖本地环境；如必须依赖则 `pytest.skip()` 条件跳过 |
| mypy continue-on-error=true 仍显示 job failure | GitHub Actions 视 `mypy ...` 非零退出为 failure | 用 `mypy ... \|\| echo "⚠️ mypy warnings (non-blocking)"` 确保步骤绿色 |
| ruff 375 个错误阻塞 CI | 创建 CI 前未在本地先跑 `ruff check` | `ruff check --fix` 自动修复 + `per-file-ignores` 分文件配置 |
| 工具配置版本差异（ruff 配置弃用警告） | `[tool.ruff]` 顶级 `per-file-ignores` 弃用 | 更新到 `[tool.ruff.lint.per-file-ignores]` |
| setuptools-scm 在 CI 需要完整 git 历史 | CI 默认 shallow clone (depth=1) 不含 tag | 配置 `actions/checkout@v4` 加 `fetch-depth: 0` |
| 测试不引用已有 fixture 数据 | 开发时没检查 `tests/fixtures/` 和 `test_matcher.py` 的模式 | 开发新测试前先扫一遍同目录下其他测试文件的 fixture 引用模式 |
| `from X import Y` 常量不可通过 reassign X.Y 打补丁 | 测试中修改 `config.STATUS_FILE` 后，`daemon._update_status()` 仍写入原路径 | 必须 patch 引用该常量的模块：`import daemon; daemon.STATUS_FILE = "/new/path"` |
| PEP 604 联合类型语法 (`dict | None`) 在 Python 3.9 CI 中断 | `_load_schema() -> dict | None` 在 Python 3.9 上 TypeError | 最低版本 <3.10 时用 `Optional[dict]` 或 `from __future__ import annotations` |
| Release 工作流 Python 版本脱敏（2026-05-12） | `release.yml` 只用 Python 3.11 测试，不暴露 3.9 兼容性问题 | Release CI 也应在最老版本（3.9）上预检一次，或确保 CI 矩阵全绿才允许 release |

### 陷阱 5: 模块级常量导入不可通过重新赋值打补丁（2026-05-12）

**现象**：测试中执行 `cfg_module.STATUS_FILE = str(test_file)` 后，调用 `daemon._update_status()` 仍然写入原始 `~/.sra/srad.status.json`，而非测试路径。

**根因**：`daemon.py` 使用 `from .config import STATUS_FILE` 在**模块导入时**绑定了 `STATUS_FILE` 的引用。修改 `config.STATUS_FILE` 不会影响 `daemon.STATUS_FILE`——因为 daemon 模块在自己的命名空间中持有独立引用。

```python
# ❌ 不行——daemon.STATUS_FILE 仍指向旧值
from skill_advisor.runtime import config as cfg
cfg.STATUS_FILE = "/new/path"

# ✅ 正确——直接覆盖 daemon 模块中的引用
import skill_advisor.runtime.daemon as daemon_mod
daemon_mod.STATUS_FILE = "/new/path"
```

**黄金规则**：模块级常量导入 (`from X import Y`) 不可通过 reassign X.Y 打补丁。必须 reassign **引用该常量的模块** 的对应属性。

**详见** `references/concurrent-testing-patterns.md` 第 3 节。

### 陷阱 6: 测试文件间全局状态污染 — 模块级变量永久修改（2026-05-12）

**现象**：Release CI 在 `test_init_default_config` 中断言失败：`assert 8080 == 8536`。本地单独运行该测试通过，但运行 `test_config.py` + `test_daemon.py` 时失败。

**根因链**（三层连环污染）：

```
Layer 1: test_config.py 永久修改模块级变量
  └─ cfg_module.SRA_HOME    = tmp_path （不恢复）
  └─ cfg_module.CONFIG_FILE  = tmp_path/config.json （不恢复）
  └─ cfg_module.CONFIG_SCHEMA = tmp_path/config.schema.json （不恢复）

Layer 2: pytest 默认保留 tmp_path 文件
  └─ tmp_path_retention_count=3（保留最近 3 个临时目录）
  └─ tmp_path_retention_policy="all"（保留所有文件）
  └─ config.json 带 http_port=8080 持续存活

Layer 3: test_daemon.py 使用被污染的模块变量
  └─ SRA_HOME → 指向残留的 tmp_path
  └─ CONFIG_FILE → 指向残留的 config.json → 读到 http_port=8080
```

**快速定位命令**：

```bash
# 1. 确认测试顺序依赖 — 单独运行通过 vs 批量运行失败
python -m pytest tests/test_daemon.py::TestSRaDDaemonInit::test_init_default_config -q  # ✅ 通过
python -m pytest tests/test_config.py tests/test_daemon.py -q                           # ❌ 失败

# 2. 检查残留的 pytest tmp_path 文件
find /tmp/pytest-of-*/ -name "config.json" -exec cat {} \;  # → {"http_port": 8080}

# 3. 检查模块级变量当前值
python -c "from skill_advisor.runtime import config as c; print(c.SRA_HOME); print(c.CONFIG_FILE)"
```

**修复方案**：所有修改模块级变量的测试必须用 `try/finally` 恢复原始值：

```python
def test_env_precedence_over_file(self, mock_sra_home):
    from skill_advisor.runtime import config as cfg_module
    orig_home = cfg_module.SRA_HOME
    orig_file = cfg_module.CONFIG_FILE
    orig_schema = cfg_module.CONFIG_SCHEMA
    try:
        cfg_module.SRA_HOME = str(mock_sra_home)
        cfg_module.CONFIG_FILE = str(mock_sra_home / "config.json")
        cfg_module.CONFIG_SCHEMA = str(mock_sra_home / "config.schema.json")
        # ... 测试逻辑 ...
    finally:
        cfg_module.SRA_HOME = orig_home
        cfg_module.CONFIG_FILE = orig_file
        cfg_module.CONFIG_SCHEMA = orig_schema
```

**黄金规则**（对于 python 测试中修改模块级变量的场景）：

| # | 规则 | 示例 |
|:--:|:-----|:------|
| ① | **始终 try/finally 恢复** | 修改 3 个值 → 恢复 3 个值 |
| ② | **不要依赖 pytest tmp_path 的自动清理** | pytest 保留最近 3 个 tmp_path 目录 |
| ③ | **修改模块变量 ≠ 修改导入者的副本** | 见陷阱 5 的黄金规则 |
| ④ | **测试文件按字母序运行时，前面的测试可能污染后面的** | `test_config.py` 在 `test_daemon.py` 之前 |

**详见** `references/test-state-pollution.md`（本 session 完整调试记录）。

### 陷阱 8: CI 失败诊断 — gh CLI 使用模式（2026-05-12）

**快速定位 CI 失败的通用命令**：

```bash
# 1. 查看最近运行状态
gh run list --limit 5 --json name,headBranch,conclusion,status

# 2. 查看失败 job 的日志（用 databaseId）
gh run view <databaseId> --log 2>&1 | grep -E "FAILED|Error|exit code 1" | head -10

# 3. 按 job 名过滤（name 来自 workflow yml 的 name: 字段）
gh run view <databaseId> --log --job "pytest (3.9)" | grep -E "FAILED|Error"

# 4. 确认测试顺序依赖（污染排查）
python -m pytest tests/test_a.py -q          # 单独运行
python -m pytest tests/test_b.py tests/test_a.py -q  # 顺序颠倒运行
```

**用例场景**：当 CI 失败但本地通过时，用 `gh run view --log` 直接查看远程日志，无需登录 GitHub Web UI。

## 🔗 相关文件

| 文件 | 说明 |
|:-----|:------|
| `docs/DEV-WORKFLOW-IMPROVEMENT.md` | 深度分析文档（问题的根因分析） |
| `.hermes/AGENTS.md` | boku 的强制工作流规则 |
| `pyproject.toml` | setuptools-scm + ruff + mypy 配置 |
| `.github/workflows/ci.yml` | CI 流水线定义（含 syntax-check job） |
| `.github/workflows/release.yml` | Release 流水线定义（含 setuptools-scm 绕过方案） |
| `docs/project-report.json` | 项目报告数据源 |
| `references/test-infrastructure-gate.md` | 🔴 测试基础设施机械门禁实战模式（2026-05-11） |
| `references/pypi-trusted-publisher.md` | 📦 PyPI Trusted Publisher 配置与排错指南 |
| `references/setuptools-scm-ci-version.md` | 🏷️ setuptools-scm 在 CI 中版本号解析失败排错 |
| `references/concurrent-testing-patterns.md` | 🧵 并发安全测试模式实战记录 |
| `references/test-state-pollution.md` | 💥 测试文件间全局状态污染调试记录 |
| `../../testing/python-testing/` | 🐍 通用 Python 测试反模式指南（含版本兼容性、模块污染等） |
| `scripts/set_version.py` | 🔧 CI 构建前将 pyproject.toml 动态版本替换为静态版本的脚本 |
