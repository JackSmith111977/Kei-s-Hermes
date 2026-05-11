---
name: sra-dev-workflow
description: "SRA 项目开发工作流 — 版本管理(setuptools-scm) + CI/CD(GitHub Actions) + Reality Check 门禁 + doc-alignment 全生命周期。SRA 开发任务的强制流程。"
version: 1.0.0
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
skill_type: workflow
design_pattern: pipeline
---

# SRA 开发工作流 v4.0

> 整合: setuptools-scm 版本管理 + GitHub Actions CI/CD + Reality Check 门禁

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
```

## ⚠️ CI/CD 常见陷阱

### 陷阱 0: PyPI Trusted Publisher 配置不正确（2026-05-11 新增）

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

**核心原则**: 版本号只来自 git tag（setuptools-scm 单源）

- `__init__.py` 中的 `__version__` 由三层层级推导：
  1. `_version.py`（built 包的 setuptools-scm 生成物）
  2. `importlib.metadata`（pip install 后的 metadata）
  3. `git describe --tags`（开发环境 fallback）

### 版本生命周期

| 阶段 | git tag | 显示的版本 | CI/CD 行为 |
|:-----|:--------|:-----------|:-----------|
| 开发中 | 无新 tag | `v1.3.0-6-ga1b2c3d` | CI 跑测试 |
| 预发布 | `v1.4.0rc1` | `v1.4.0rc1` | CI + 可选 PyPI |
| 正式发布 | `v1.4.0` | `v1.4.0` | CI + PyPI + GitHub Release |

### 版本操作

```bash
# 查看当前版本
python -c "from skill_advisor import __version__; print(__version__)"

# 不要手动改版本号！如需要发布新版本：
git tag v1.4.0               # 打 tag
git push origin v1.4.0       # 推送 tag → 自动触发 CI/CD

# 预发布
git tag v1.4.0rc1
git push origin v1.4.0rc1
```

## ⚙️ CI/CD 流水线

### CI（每次 push/PR）

`.github/workflows/ci.yml` — 自动执行：
1. 🧪 `pytest` — 全量测试（多 Python 版本矩阵）
2. 🧹 `ruff` — lint 检查
3. 🔤 `mypy` — 类型检查（当前 continue-on-error）

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
       ↓ pass
[Phase 3] 提交前对齐
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

# === 6. doc-alignment 验证 ===
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json --verify
# 预期: "✅ 数据与代码状态一致"
```

### CI 实战教训（2026-05-11）

| 教训 | 根因 | 预防措施 |
|:-----|:-----|:---------|
| CI 没有 Hermes 技能目录 → 契约测试失败 | `test_contract.py` 使用 `~/.hermes/skills` 而非 `FIXTURES_DIR` | 使用 fixture 数据，不依赖本地环境；如必须依赖则 `pytest.skip()` 条件跳过 |
| mypy continue-on-error=true 仍显示 job failure | GitHub Actions 视 `mypy ...` 非零退出为 failure | 用 `mypy ... \|\| echo "⚠️ mypy warnings (non-blocking)"` 确保步骤绿色 |
| ruff 375 个错误阻塞 CI | 创建 CI 前未在本地先跑 `ruff check` | `ruff check --fix` 自动修复 + `per-file-ignores` 分文件配置 |
| 工具配置版本差异（ruff 配置弃用警告） | `[tool.ruff]` 顶级 `per-file-ignores` 弃用 | 更新到 `[tool.ruff.lint.per-file-ignores]` |
| setuptools-scm 在 CI 需要完整 git 历史 | CI 默认 shallow clone (depth=1) 不含 tag | 配置 `actions/checkout@v4` 加 `fetch-depth: 0` |
| 测试不引用已有 fixture 数据 | 开发时没检查 `tests/fixtures/` 和 `test_matcher.py` 的模式 | 开发新测试前先扫一遍同目录下其他测试文件的 fixture 引用模式 |

## 🔗 相关文件

| 文件 | 说明 |
|:-----|:------|
| `docs/DEV-WORKFLOW-IMPROVEMENT.md` | 深度分析文档（问题的根因分析） |
| `.hermes/AGENTS.md` | boku 的强制工作流规则 |
| `pyproject.toml` | setuptools-scm + ruff + mypy 配置 |
| `.github/workflows/ci.yml` | CI 流水线定义 |
| `.github/workflows/release.yml` | Release 流水线定义 |
| `docs/project-report.json` | 项目报告数据源 |
| `references/test-infrastructure-gate.md` | 🔴 测试基础设施机械门禁实战模式（2026-05-11） |
| `references/pypi-trusted-publisher.md` | 📦 PyPI Trusted Publisher 配置与排错指南（OIDC 字段映射、调试命令、重试流程） |
