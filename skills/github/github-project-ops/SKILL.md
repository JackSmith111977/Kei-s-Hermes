---
name: github-project-ops
description: GitHub 项目运维完整指南 — 仓库管理、分支保护、Issue/PR 工作流、CI/CD (Actions)、安全 (Secret Scanning/Dependabot/CodeQL)、Release (SemVer/semantic-release)、社区运营、备份迁移。
version: 1.1.0
triggers:
  - github
  - 项目运维
  - 分支保护
  - branch protection
  - rulesets
  - ci/cd
  - github actions
  - dependabot
  - codeql
  - code scanning
  - secret scanning
  - semantic release
  - semver
  - 版本管理
  - release
  - pull request
  - code review
  - issues
  - issue triage
  - 社区运营
  - open source
  - 开源
  - contributing guide
  - stale bot
  - 备份仓库
  - repository management
  - 文档一致性
  - 代码审计
  - 文档飘移
  - doc drift
  - 发布前准备
  - pre-release
  - 项目现状分析
  - 代码文档对比
  - documentation audit
allowed-tools:
  - terminal
  - read_file
  - write_file
  - search_files
  - patch
metadata:
  hermes:
    tags:
      - GitHub
      - Repository Management
      - Branch Protection
      - CI/CD
      - GitHub Actions
      - Security
      - Dependabot
      - Code Scanning
      - Release
      - SemVer
      - semantic-release
      - Community
      - Open Source
    category: github
    skill_type: library-reference
    design_pattern: domain-guide
    related_skills:
      - git-advanced-ops
      - github-auth
      - github-pr-workflow
      - github-code-review
      - github-issues
      - github-repo-management
      - linux-ops-guide
---

# GitHub 项目运维指南 🚀

> **涵盖**：仓库管理 → 分支保护 → Issue/PR 协作 → CI/CD → 安全 → Release → 社区运营 → 备份迁移

---

## 📋 目录

- [仓库管理](#1-仓库管理)
- [分支保护](#2-分支保护)
- [协作工作流](#3-协作工作流)
- [CI/CD (GitHub Actions)](#4-cicd-github-actions)
- [安全管理](#5-安全管理)
- [Release 管理](#6-release-管理)
- [社区运营](#7-社区运营)
- [备份与迁移](#8-备份与迁移)
- [快速参考](#9-快速参考)

---

## 1. 仓库管理

### 1.1 仓库创建与配置

```bash
# 使用 gh CLI 创建
gh repo create my-project --public --clone

# 使用 gh CLI 创建带模板
gh repo create my-project --template org/template-repo
```

### 1.2 仓库设置项

| 设置项 | 推荐值 | 说明 |
|--------|--------|------|
| Default branch | `main` | 现代命名规范 |
| Squash merging | ✅ 启用 | 保持干净历史 |
| Allow auto-merge | ✅ | 提高效率 |
| Issues | ✅ 启用 | 任务跟踪 |
| Discussions | 看社区需求 | Q&A 和讨论 |
| Wikis | 大项目启用 | 完整文档 |
| Projects | ✅ 启用 | 看板管理 |
| Sponsorships | 可选 | 开源项目推荐 |

### 1.3 仓库设置操作

```bash
# 使用 gh CLI 修改设置
gh api -X PATCH repos/:owner/:repo \
  -F allow_squash_merge=true \
  -F delete_branch_on_merge=true

# 列出所有仓库（批量操作）
gh repo list owner --no-archived --json name,id

# 批量设置（脚本化）
for repo in $(gh repo list owner --no-archived --json name -q '.[].name'); do
  gh api -X PATCH repos/owner/$repo \
    -F allow_squash_merge=true
done
```

### 1.4 仓库 SEO — Topics 与 Description

**这是开源项目最容易被忽视但最重要的设置。** 没有 Topics 和 Description 的项目在 GitHub 搜索中完全不可见。

```bash
# 通过 API 设置（需要 PAT）
curl -X PATCH https://api.github.com/repos/:owner/:repo \
  -H "Authorization: Bearer <PAT>" \
  -H "Accept: application/vnd.github+json" \
  -d '{
    "description": "一句话吸引人的项目描述，让人5秒内知道这是做什么的",
    "homepage": "https://github.com/:owner/:repo"
  }'

# 设置 Topics（需要 PAT）
curl -X PUT https://api.github.com/repos/:owner/:repo/topics \
  -H "Authorization: Bearer <PAT>" \
  -H "Accept: application/vnd.github.mercy-preview+json" \
  -d '{"names": ["keyword1", "keyword2", "python", "cli"]}'
```

**推荐 Topics 选择的 3 原则：**
1. **语言/框架**：python, nodejs, cli
2. **领域**：devops, security, automation
3. **功能**：recommendation-engine, ai-agent, skill-management

**检查当前状态：**
```bash
# 查看 Topics 和 Description（无需认证）
curl -s https://api.github.com/repos/:owner/:repo | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f'描述: {d.get(\"description\")}'); print(f'Topics: {d.get(\"topics\")}')"
```

**典型错误**：Topics 为空、Description 为 None — 这等于在 GitHub 上隐姓埋名。

---

### 1.5 文档一致性检查

当需要检查 GitHub 仓库的实际内容与文档描述是否一致时，使用以下方法论：

```
文档一致性检查流程：
  1. 扫描全部文件清单（排除 .git/__pycache__）
  2. 提取关键基准信息：
     - GitHub API 获取远程仓库状态（描述/Topics/分支/许可）
     - 本地 CLI 入口文件检查（命令列表）
     - 版本号/依赖/测试数量
  3. 逐段比对 README 与真实代码
  4. 按严重程度分类问题：
     🔴 严重：数据错误（如声称零依赖但实际有依赖）
     🟡 中等：信息不完整（如项目结构图遗漏文件）
     🟢 轻微：格式/表述优化
  5. 安全边界原则：只修文档，不碰业务代码
  6. 修复后跑全套测试验证

检查清单（8 项核心检查点）：
- [ ] Badges 准确性（tests/coverage/license/latency）
- [ ] CLI 命令表 vs 实际代码入口
- [ ] 项目结构图 vs 实际文件树
- [ ] 基准测试数据可复现
- [ ] pip install 指令是否准确
- [ ] docs/ 目录文档与 README 同步
- [ ] GitHub Topics/Description 是否为空
- [ ] 仓库健康度（README/CONTRIBUTING/LICENSE/CODE_OF_CONDUCT/模板）
```

**典型发现的「文档飘移」问题：**
- README 中声称"零依赖"但实际有 pyyaml 依赖
- 项目结构图遗漏 .github/ pyproject.toml 等重要文件
- pip install 指令包含 --user 参数（PyPI 发布后不需要）
- GitHub Topics/Description 为空（项目完全不可被搜索发现）

### 1.6 深度文档审计模式（进阶）

当需要系统性审计代码与文档的一致性时，使用以下 5 种结构化对比模式。详见 `references/code-doc-audit-patterns.md`。

| 模式 | 目标 | 典型发现 |
|:-----|:-----|:---------|
| **A: CLI 命令表审计** | README 命令表 vs 实际 CLI 入口 | README 遗漏辅助命令 |
| **B: API 端点审计** | API 文档 vs 实际路由 | 文档遗漏辅助端点、声明了不存在的端点 |
| **C: 算法参数审计** | 文档中权重/阈值 vs 代码常量 | 代码有额外参数但文档未记录 |
| **D: 版本号一致性扫描** | 全仓版本号引用一致性 | help 输出/安全表版本号过时 |
| **E: 项目结构图审计** | 结构图 vs 实际文件树 | 遗漏新目录、已删除文件未更新 |

**一致性评分标准**：按代码准确性(30%)、文档完整性(25%)、文档时效性(25%)、元数据一致性(20%) 四个维度评分，低于 70% 禁止发布。

---

## 2. 分支保护

### 2.1 核心设置（两步走）

**📌 方法一：Branch Protection Rules（仓库级）**

```bash
# 通过 gh API 创建分支保护规则
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["continuous-integration", "codeql"]
  },
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_last_push_approval": true
  },
  "enforce_admins": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
```

**📌 方法二：Rulesets（组织级推荐）**

Rulesets 比分文保护规则更灵活，支持分层管理：

| 层级 | 适用场景 | 必设规则 |
|------|----------|----------|
| 🟢 **基础层** | 所有活跃仓库 | Require PR + Require status checks |
| 🟡 **生产层** | production=true | + Require approvals(1) + up-to-date + conversation resolution |
| 🔴 **安全层** | security_tier=high | + Signed commits + Lock branch + 禁止 bypass |

### 2.2 必选规则项

1. **Require a pull request before merging** ✅
2. **Require approvals** (≥1) ✅
3. **Dismiss stale pull request approvals** ✅
4. **Require status checks to pass before merging** ✅
5. **Require branches to be up to date before merging** ✅
6. **Require conversation resolution before merging** ✅
7. **Do not allow bypassing the above settings** ✅

### 2.3 CODEOWNERS 文件

创建 `.github/CODEOWNERS`：

```
# 全局 owner
* @org/maintainers

# 特定模块
src/api/ @org/api-team
src/frontend/ @org/frontend-team
docs/ @org/docs-team

# 敏感文件安全
SECURITY.md @org/security-team
```

---

## 3. 协作工作流

### 3.1 Issue 管理

**标签体系（推荐）：**

```
类型: bug / enhancement / documentation / question
优先级: P0-critical / P1-high / P2-medium / P3-low
状态: needs-reproduction / waiting-for-response / ready-for-review
入门: good first issue / help wanted
```

**Issue Templates（`.github/ISSUE_TEMPLATE/`）：**

```yaml
name: Bug Report
description: 报告一个问题
title: "[Bug]: "
labels: ["bug"]
body:
  - type: textarea
    id: description
    attributes:
      label: 问题描述
      description: 清晰描述问题
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: 复现步骤
      placeholder: 1. 打开... 2. 点击... 3. 看到错误
  - type: textarea
    id: expected
    attributes:
      label: 期望行为
```

**Triage 流程（每天 15 分钟）：**
1. 检查新 Issue → 标签 + 分配负责人
2. 关闭重复项（带引用链接）
3. 回复模板消息（saved replies）
4. 标记 `good first issue` 给新人

### 3.2 Pull Request 工作流

**PR 创建规范：**

```markdown
## 描述
[清晰描述这个 PR 做了什么]

## 类型
- [ ] Bug Fix
- [ ] Feature
- [ ] Refactor
- [ ] Documentation

## 检查清单
- [ ] 测试通过
- [ ] 代码 Review 中
- [ ] 文档已更新

## 相关 Issue
Closes #123
```

**PR Review 最佳实践：**
- **小即是美**：10 行 = 10 个问题，500 行 = "looks fine"
- **分而治之**：复杂任务拆成多个小 PR
- **提问先行**：用问题代替指责，给对方解释空间
- **正面反馈**：除了指出问题，也要表扬好的代码
- **及时审阅**：PR 挂越久，合入成本越高

**Merge 策略选择：**

| 策略 | 推荐场景 | 效果 |
|------|----------|------|
| **Squash and Merge** | ✅ 默认推荐 | 把整个 PR 压缩为 1 个 commit |
| **Rebase and Merge** | 需要保留每个 commit | 线性历史 |
| **Merge Commit** | 保留完整分支拓扑 | 保留所有上下文 |

### 3.3 gh CLI 搜索速查

```bash
# Issue 查询
gh issue list --search 'no:assignee label:"bug" sort:created-asc'
gh issue list --search 'label:"good first issue"'
gh issue list --search 'author:@me'

# PR 查询
gh pr list --search 'review:required'              # 等待 Review
gh pr list --search 'review:changes_requested'      # 需要修改
gh pr list --search 'is:draft'                      # Draft PR
gh pr list --search 'review-requested:@me'          # 等我 Review
gh pr list --search 'is:merged sort:updated-desc'   # 最新合并
gh pr list --search 'author:@me is:open'            # 我的 PR
```

---

## 4. CI/CD (GitHub Actions)

### 4.1 标准 CI 流水线

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# ⚠️ 最小权限原则
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15  # ⚠️ 防止卡死
    strategy:
      matrix:
        node: [18, 20]  # 矩阵测试
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run lint
```

### 4.2 GitHub Actions 最佳实践清单

| 实践 | 说明 | 优先级 |
|------|------|--------|
| **PIN commit SHA** | 不要用 `@v4` 标签，用 `@abc123def` | 🔴 安全 |
| **最小权限** | `permissions:` 显式声明 | 🔴 安全 |
| **timeout-minutes** | 每个 job 设置超时 | 🟡 稳定 |
| **依赖缓存** | `actions/setup-*` 内置或 `actions/cache` | 🟡 性能 |
| **矩阵构建** | `strategy.matrix` 多版本测试 | 🟡 质量 |
| **Reusable Workflows** | 复用公共流水线 | 🟢 效率 |
| **Secret 管理** | `${{ secrets.XXX }}`，不要硬编码 | 🔴 安全 |

### 4.3 Reusable Workflows

```yaml
# 定义可复用工作流 .github/workflows/ci-reusable.yml
on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string
    secrets:
      NPM_TOKEN:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci
      - run: npm test

# 调用
jobs:
  ci:
    uses: ./.github/workflows/ci-reusable.yml@main
    with:
      node-version: '20'
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### 4.5 Python CI 测试可移植性

> 详细指南见 `references/python-ci-test-fixtures.md`

当测试依赖本地环境路径（如 `~/.hermes/skills`）时，CI 环境会无法运行。解决方案是创建 `tests/fixtures/` 目录，用 10-20 个模拟数据文件替代真实环境依赖。

**核心原则**：
- Fixtures 放入 git 仓库（`tests/fixtures/`），clone 即用
- 测试类始终初始化对象，用 `has_*` 标志位区分环境
- CI 工作流不需要额外 setup 步骤

详见 `references/python-ci-test-fixtures.md`。

### 4.6 CI 陷阱与修复模式

#### ⚠️ 陷阱1: `setup-python@v5` + `cache: pip` 缺依赖清单文件

**现象**：`actions/setup-python@v5` 配置了 `cache: pip`，但仓库没有 `pyproject.toml` 或 `requirements.txt`，导致 job 硬错误退出：

```
##[error]No file matched to [**/requirements.txt or **/pyproject.toml]
```

**根因**：`cache: pip` 需要找到 pip 支持的依赖清单文件来计算缓存 key。纯脚本项目（无 python 包结构）会触发此错误。

**修复方案**：

| 方案 | 适用场景 | 操作 |
|:-----|:---------|:-----|
| 🥇 **创建 pyproject.toml** | 有依赖管理的项目 | 添加 `[build-system]` 和 `[project]` 段，声明 pyyaml 等依赖 |
| 🥈 **去掉 `cache: pip`** | 纯脚本项目，无 pip 依赖 | 删除 `cache: pip` 行，只留 `python-version` |
| 🥉 **创建 requirements.txt** | 依赖极少 | 写入 `pyyaml>=6.0` 等 |

**最佳实践**：即使是不发布的脚本项目，也推荐创建 `pyproject.toml`，声明版本号 + 依赖，一举两得（CI 缓存 + 版本管理）。

#### ⚠️ 陷阱2: YAML 块标量 `|` + shell heredoc 缩进冲突

**现象**：在 `run: |` 中使用 Python heredoc (`python3 << 'PYEOF'`)，Python 代码没有缩进到 YAML 块标量要求的级别，导致 YAML 解析器提前终止块标量：

```yaml
# ❌ 错误 — `import yaml` 在 column 1，YAML 块提前终止
      - name: YAML check
        run: |
          python3 << 'PYEOF'
import yaml, sys, os   # <- column 1 < 块标量缩进 (10)!
errors = []
PYEOF
```

**修复方案**（按推荐优先级）：

| 方案 | 说明 | 优点 |
|:-----|:------|:------|
| 🥇 **提取为独立脚本** | 将 Python 代码写入 `scripts/ci-xxx.py`，CI 中仅调用 `python3 scripts/ci-xxx.py` | 无缩进冲突，可本地复现，可维护 |
| 🥈 **`python3 -c` 单行** | 用 `python3 -c "..."` 将代码写在一行内 | 适合短逻辑，不需要脚本文件 |
| 🥉 **YAML 折叠块 `>`** | 用 `>` 替代 `|` 配合 `\n`，不推荐 | 代码可读性差 |

**推荐模式**（独立脚本）：

```yaml
# .github/workflows/ci.yml
jobs:
  lint:
    steps:
      - uses: actions/checkout@v4
      - run: pip install pyyaml
      - name: YAML syntax check
        run: python3 scripts/ci-check-yaml.py  # 逻辑在独立脚本中
```

#### 🔧 模式: 纯脚本 Python 项目的 CI 架构

当仓库只有 `.py` 脚本（无 `setup.py`/`pyproject.toml` 包结构）时，推荐 CI 架构：

```yaml
jobs:
  lint:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          # cache: pip   ← 无 pyproject.toml 时去掉此行
      - run: pip install pyyaml   # 显式装依赖
      - run: |
          # Python 语法检查
          find . -name '*.py' -not -path './.git/*' \
            -exec python3 -m py_compile {} \;
      - run: python3 scripts/validate-all.py  # 独立验证脚本

  consistency:
    needs: lint
    steps:
      - run: python3 scripts/ci-cross-ref-check.py
```

**优势**：lint → validate → consistency 三段式并行，每段职责单一。
**关键**：复杂逻辑放在独立脚本中，workflow 只做编排。

```yaml
# 生产部署需要审批
deploy:
  runs-on: ubuntu-latest
  environment: production  # 需要审批
  needs: [test, security]
  steps:
    - run: ./deploy.sh
```

---

## 5. 安全管理

### 5.1 三层防护架构

```
┌─────────────────────────────────────────────┐
│  金库层：Secret Scanning                     │
│  ─── 自动检测密钥泄露 · Push Protection      │
├─────────────────────────────────────────────┤
│  依赖层：Dependabot                          │
│  ─── 漏洞告警 · 自动修复 PR · 版本更新        │
├─────────────────────────────────────────────┤
│  代码层：Code Scanning (CodeQL)              │
│  ─── 静态分析 · CI 集成 · 阻止漏洞合并        │
└─────────────────────────────────────────────┘
```

### 5.2 Secret Scanning

**启用位置**：Settings → Code security → Secret scanning

```bash
# 通过 API 开启
gh api -X PATCH repos/:owner/:repo \
  -F security_and_analysis[secret_scanning][status]=enabled

# 自定义检测模式（组织级）
gh api /orgs/:org/code-security/secret-scanning/custom-patterns \
  -F name="my-api-key" \
  -F regex='(MY_APP_[A-Z0-9_]{32})'
```

### 5.3 Dependabot 配置

**`.github/dependabot.yml` （推荐配置）：**

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Shanghai"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "automerge"
    groups:
      dev-dependencies:
        patterns:
          - "*"
        update-types:
          - "patch"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

### 5.4 Code Scanning (CodeQL)

```yaml
# .github/workflows/codeql.yml
name: CodeQL
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript
      - uses: github/codeql-action/analyze@v3
```

> **集成到分支保护**：在 Branch Protection 中 Require status checks → 添加 `CodeQL` 和 `Analyze (javascript)`

### 5.5 供应链安全清单

- [ ] 使用锁文件（`package-lock.json` / `yarn.lock` / `Pipfile.lock`）
- [ ] 启用 Dependabot security updates
- [ ] 启用 Dependency review（CI 中阻止有漏洞的依赖合并）
- [ ] 生成 SBOM（`advanced-security/generate-sbom-action`）
- [ ] 定期 audit（`npm audit` / `pip-audit`)
- [ ] 签名 commits 和 tags

---

## 6. Release 管理

### 6.1 Semantic Versioning（语义化版本）

```
vMAJOR.MINOR.PATCH
   ↑      ↑     ↑
   │      │     └── Patch：向下兼容的 bug 修复
   │      └── Minor：向下兼容的新功能
   └── Major：不兼容的 API 变更
```

### 6.2 Conventional Commits（约定式提交）

| 提交类型 | 说明 | 版本影响 |
|----------|------|----------|
| `feat:` | 新功能 | MINOR |
| `fix:` | Bug 修复 | PATCH |
| `feat!:` / `fix!:` | Breaking Change | MAJOR |
| `docs:` | 文档 | 无 |
| `chore:` | 构建/工具 | 无 |
| `refactor:` | 重构 | 无 |
| `BREAKING CHANGE:` | 正文中声明 | MAJOR |

### 6.3 semantic-release 集成

**安装配置：**

```bash
npm install -D semantic-release @semantic-release/github @semantic-release/changelog @semantic-release/git
```

**`.releaserc.json`：**

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", {
      "changelogFile": "CHANGELOG.md"
    }],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
    }],
    "@semantic-release/github"
  ]
}
```

**GitHub Actions 自动化：**

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    branches: [main]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 6.4 发布前准备（手动流程）

当需要手动准备一个版本发布时（不依赖 semantic-release），参考以下步骤：

1. **分支**：创建 `prepare-release-vX.Y.Z` 分支
2. **CHANGELOG**：基于 docs/ 目录的 EPIC/Sprint 记录整理变更
3. **配置清理**：统一 pyproject.toml 和 setup.py，修复 deprecation 警告
4. **版本号检查**：确保 pyproject.toml / __init__.py 版本号一致
5. **构建验证**：`python3 -m build && twine check dist/*`
6. **测试**：`python3 -m pytest tests/ -v`
7. **打 tag**：`git tag vX.Y.Z && git push origin vX.Y.Z`
8. **GitHub Release**：`gh release create vX.Y.Z --notes "..."`

> 📋 完整操作步骤和详细检查清单见 `references/pre-release-checklist.md`

### 6.5 完整流水线图

```
[feat/fix/commit] → [Push → PR] → [CI 通过] → [Merge to main]
                                                    ↓
                                           semantic-release
                                                    ↓
                               ┌────────┬──────┬───────────┐
                               ↓        ↓      ↓           ↓
                           分析提交  计算版本 生成CHANGELOG 创建Release
                                                    ↓
                                             推送git tag
```

---

## 7. 社区运营

### 7.1 必要文件清单

创建以下文件到仓库根目录或 `.github/`：

| 文件 | 用途 | 推荐 |
|------|------|------|
| `README.md` | 项目介绍/安装/使用 | ✅ 必须 |
| `CONTRIBUTING.md` | 贡献指南 | ✅ 推荐 |
| `CODE_OF_CONDUCT.md` | 行为准则 | ✅ 推荐（Contributor Covenant） |
| `LICENSE` | 许可证 | ✅ 必须 |
| `SECURITY.md` | 安全策略 | ✅ 推荐 |

**README 内容模板：**

```markdown
# 项目名称

> 一句话描述

[![CI](https://img.shields.io/github/actions/workflow/status/owner/repo/ci.yml)](https://...)
[![npm](https://img.shields.io/npm/v/pkg)](https://...)
[![License](https://img.shields.io/github/license/owner/repo)](LICENSE)

## 安装
\`\`\`bash
npm install my-package
\`\`\`

## 快速开始
\`\`\`javascript
const myPkg = require('my-package');
\`\`\`

## API
...

## 贡献
欢迎提交 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证
MIT — 详见 [LICENSE](LICENSE)
```

### 7.2 Stale Bot 配置

```yaml
# .github/workflows/stale.yml
name: Stale
on:
  schedule:
    - cron: '0 9 * * 1'  # 每周一 9:00

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v9
        with:
          days-before-stale: 60
          days-before-close: 14
          stale-issue-label: 'stale'
          stale-issue-message: >
            此 Issue 60 天无活动，标记为 stale。
            如有更新请回复，14 天后将自动关闭。
          stale-pr-label: 'stale'
          exempt-issue-labels: 'pinned,security,planned'
          exempt-pr-labels: 'pinned,dependencies'
```

> ⚠️ **注意**：Stale Bot 会降低活跃贡献者数量。建议手动+自动结合，对 `good first issue` 和 `pinned` 标签豁免。

### 7.3 社区健康检查

GitHub 自动提供 **Community Standards** 检查（仓库 → Insights → Community）：
- README ✓ / CONTRIBUTING ✓ / LICENSE ✓ / Code of Conduct ✓
- Issue Templates ✓ / PR Templates ✓

---

## 8. 备份与迁移

### 8.1 完整备份

```bash
# 镜像克隆（包含所有分支/tags/PR）
git clone --mirror https://github.com/owner/repo.git
cd repo.git

# 推送到新位置
git remote add backup https://github.com/backup-org/repo-backup.git
git push --mirror backup

# 定期备份脚本
#!/bin/bash
repos=("repo1" "repo2" "repo3")
for repo in "${repos[@]}"; do
  git clone --mirror "https://github.com/owner/$repo.git" "/backup/$repo.git"
done
```

### 8.2 gh CLI 迁移

```bash
# 列出并迁移
gh repo list owner --limit 100 --json name,url
gh repo create new-owner/$repo --private
gh repo clone owner/$repo
cd $repo
git remote add new https://github.com/new-owner/$repo.git
git push --mirror new
```

### 8.3 镜像同步

```bash
# 使用 GitHub Actions 自动同步
# .github/workflows/mirror.yml
name: Mirror
on:
  schedule:
    - cron: '0 2 * * *'
jobs:
  mirror:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: |
          git remote add mirror https://${{ secrets.MIRROR_TOKEN }}@github.com/mirror-org/repo.git
          git push --mirror mirror
```

---

## 9. 快速参考

### 9.1 gh CLI 速查

```bash
# 仓库
gh repo create/delete/list/view
gh repo fork/clone

# Issue
gh issue list/create/close/view/reopen
gh issue --search 'no:assignee label:bug'

# PR
gh pr list/create/checkout/review/merge/close
gh pr review --approve/--comment/--request-changes
gh pr merge --squash/--rebase/--merge

# 分支保护
gh api /repos/:owner/:repo/branches/main/protection

# CI/CD
gh run list --workflow=ci.yml
gh run watch

# Release
gh release list/create/delete
gh release create v1.0.0 --notes "Release notes"
```

### 9.2 GitHub API 速查

```bash
# 仓库设置
PATCH /repos/:owner/:repo
GET  /repos/:owner/:repo

# 分支保护
GET/PUT/DELETE /repos/:owner/:repo/branches/:branch/protection

# Actions
GET /repos/:owner/:repo/actions/runs
POST /repos/:owner/:repo/actions/workflows/:file/dispatches

# 安全
GET /repos/:owner/:repo/dependabot/alerts
GET /repos/:owner/:repo/code-scanning/alerts
GET /repos/:owner/:repo/secret-scanning/alerts

# Release
GET /repos/:owner/:repo/releases
POST /repos/:owner/:repo/releases
```

### 9.3 日常运维清单

- **每日**：Triage Issues（15min）、Review 待审 PR、检查 CI 失败
- **每周**：Dependabot PR 合并、Stale Bot 检查、安全告警处理
- **每月**：Release 计划、依赖 audit、备份检查
- **每季度**：权限审查、Rulesets 更新、贡献者统计

### 9.4 相关 Skill

- [git-advanced-ops](../git-advanced-ops/SKILL.md) — Git 高级操作（代理/rebase/stash/冲突解决）
- [github-auth](../github-auth/SKILL.md) — GitHub 认证（PAT/SSH/gh CLI）
- [github-pr-workflow](../github-pr-workflow/SKILL.md) — PR 完整工作流
- [github-code-review](../github-code-review/SKILL.md) — Code Review 流程
- [github-issues](../github-issues/SKILL.md) — Issues 管理
- [github-repo-management](../github-repo-management/SKILL.md) — 仓库管理
- [linux-ops-guide](../../devops/linux-ops-guide/SKILL.md) — Linux 运维（runner/监控基础）
