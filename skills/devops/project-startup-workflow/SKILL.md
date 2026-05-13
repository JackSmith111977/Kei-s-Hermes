---
name: project-startup-workflow
description: "项目起步基础建设标准化工作流 — 从 0 到 CI 绿灯的 5 阶段顺序流程。涵盖项目骨架、版本管理、CI/CD 管道、文档对齐、质量门禁。基于 cap-pack 项目起步的实战经验。"
version: 1.0.0
triggers:
  - 项目起步
  - 新建项目
  - 项目初始化
  - 基础建设
  - project startup
  - new project
  - project scaffold
  - 创建项目
  - 基础设施
  - 初始化工作流
allowed-tools:
  - terminal
  - read_file
  - write_file
  - patch
  - search_files
  - skill_view
  - skill_manage
metadata:
  hermes:
    tags: [project-setup, infrastructure, ci-cd, scaffolding, workflow]
    category: devops
    skill_type: workflow
    design_pattern: pipeline
---

# 🏗️ 项目起步工作流 (PSW) v1.0

> **核心洞察**：项目基础建设有一个**最优顺序**。顺序错了会反复返工。基于 Hermes-Cap-Pack 项目起步的真实经验沉淀。

## 📐 五阶段总图

```
Phase 0 ── 项目骨架     ← 第一天做，没骨架代码没地方放
    ↓
Phase 1 ── 版本管理     ← 立刻做，没 pyproject.toml → CI 直接崩
    ↓
Phase 2 ── CI/CD 管道   ← 确保 CI 从第一次提交就是绿的
    ↓
Phase 3 ── 文档对齐     ← CI 通过了再回来对齐文档
    ↓
Phase 4 ── 质量门禁     ← 一切稳定后再收口
```

**🚨 铁律**：禁止跳阶段！Phase N 没完成前不能进入 Phase N+1。

---

## Phase 0: 项目骨架 🦴

### 步骤 0.1 — 创建目录
```bash
mkdir -p <project>/{docs,scripts,tests}
cd <project> && git init
```

### 步骤 0.2 — 骨架文件

| 项目类型 | 骨架文件 |
|:---------|:---------|
| Python script | README.md, .gitignore, constraints.md |
| Python package | + pyproject.toml, LICENSE, src/<pkg>/ |
| Node.js | + package.json, LICENSE |
| 纯文档 | README.md, docs/ |

### 步骤 0.3 — README 最小模板
```markdown
# <Project>
> <一句话描述>
## 项目结构
```
<project>/
├── README.md
├── CHANGELOG.md
├── constraints.md
├── .gitignore
├── scripts/
└── docs/
```
```

### 步骤 0.4 — constraints.md
记录不做的事，帮助后续决策。写下"不使用 X""不依赖 Y"。

---

## Phase 1: 版本管理 📦

### 步骤 1.1 — pyproject.toml（即使非 Python 项目也要有）

```toml
[project]
name = "<project>"
version = "0.1.0"
description = "..."
requires-python = ">=3.11"
dependencies = []

[tool.version]
# Managed by scripts/bump-version.py
# Current: 0.1.0
last_bump = "<YYYY-MM-DD>"
bump_type = "patch"
```

**为什么必须有？** `setup-python@v5 cache: pip` 会找它做缓存 key。缺失 = CI 直接 `##[error]` 退出。

### 步骤 1.2 — bump-version.py

**版本映射规则**：
```
patch  ← Story / Debug 更新
minor  ← Spec 更新
major  ← Epic 完成
```

脚本核心逻辑：
```python
# 1. 从 pyproject.toml 读版本
# 2. 递增后写入 3 个目标：
#    - pyproject.toml → version
#    - CHANGELOG.md  → [Unreleased] → 正式版本号
#    - git tag -a vX.Y.Z
```

### 步骤 1.3 — CHANGELOG.md
```markdown
# Changelog
## [Unreleased]
### Added
- 项目起步基础建设
```

### 🚩 版本陷阱
| 陷阱 | 根因 | 解决 |
|:-----|:------|:------|
| `cache: pip` 崩溃 | 无 pyproject.toml | Phase 1 必须创建 |
| 版本号孤立 | 手动改了一处忘另一处 | 永远只用 bump-version.py |
| CI 无 tag 触发 | push 默认不传 tag | 用 bump-version.py 自动 tag |

---

## Phase 2: CI/CD 管道 🤖

### 步骤 2.1 — 选择 CI 检查
| 类型 | 必须 | 可选 |
|:-----|:-----|:------|
| Python scripts | 语法 + YAML 语法 | Ruff, mypy |
| Python package | pytest + flake8 | coverage, tox |
| 文档项目 | Markdown lint | link check |

### 步骤 2.2 — CI workflow 模板
```yaml
# .github/workflows/ci.yml
on:
  push: {branches: [main]}
  pull_request: {branches: [main]}
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11", cache: pip}
      - run: pip install pyyaml
      - run: |
          find . -name '*.py' -not -path './.git/*' -exec python3 -m py_compile {} \;
          echo "✅ Python syntax OK"
      - run: python3 -c "
import yaml, os
for r,_,fs in os.walk('.'):
    if '.git' in r: continue
    for f in fs:
        if f.endswith(('.yaml','.yml')):
            yaml.safe_load(open(os.path.join(r,f)))
print('✅ YAML OK')
"
```

### ⚠️ CI 关键教训
1. **复杂 Python 逻辑写成独立脚本** — YAML 中嵌入 Python 代码的缩进/heredoc 问题极难调试
2. **非阻塞步骤加 `continue-on-error: true`** — 健康检查、告警类步骤不应阻塞 pipeline
3. **本地预测试** — 推送前跑一遍 CI 的所有命令

---

## Phase 3: 文档对齐 📐

### 步骤 3.1 — 扫描版本偏离
```bash
grep -n '[0-9]\+ 技能\|[0-9]\+ 文件' README.md 2>/dev/null
find . -name '*.py' | wc -l
```

### 步骤 3.2 — 对齐三处版本
| 位置 | 检查方法 |
|:-----|:---------|
| pyproject.toml → version | `grep ^version pyproject.toml` |
| CHANGELOG.md 第一条 | `head -5 CHANGELOG.md` |
| README 项目结构图 | `tree -L 2 --gitignore` |

---

## Phase 4: 质量门禁 🔒

### 步骤 4.1 — pre-push.sh
```bash
#!/bin/bash
set -e
find . -name '*.py' -not -path './.git/*' -exec python3 -m py_compile {} \;
python3 -c "
import yaml, os
for r,_,fs in os.walk('.'):
    if '.git' in r: continue
    for f in fs:
        if f.endswith(('.yaml','.yml')): yaml.safe_load(open(os.path.join(r,f)))
print('✅ YAML OK')
"
PKG_VER=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
CHG_VER=$(grep -m1 '^\[' CHANGELOG.md | grep -oP '(?<=\[)\d+\.\d+\.\d+')
[ "$PKG_VER" = "$CHG_VER" ] || [ "$CHG_VER" = "Unreleased" ] && echo "✅ 版本一致或待发布"
```

### 步骤 4.2 — 安全红线
检查硬编码密码 (`sk-`/`gph_`/`api_key`)、示例用户名、Git 历史泄露。

---

## 📋 项目起步检查清单

```
Phase 0: 骨架
  [ ] 目录结构 (docs/ scripts/ tests/)
  [ ] README.md + .gitignore
  [ ] constraints.md（可选）

Phase 1: 版本
  [ ] pyproject.toml（CI cache 用）
  [ ] scripts/bump-version.py
  [ ] CHANGELOG.md + [Unreleased]
  [ ] 首次 git push

Phase 2: CI
  [ ] .github/workflows/ci.yml
  [ ] 语法检查: Python + YAML
  [ ] 复杂逻辑写成独立脚本
  [ ] 本地预测试 ✅
  [ ] 推送后 CI 绿色 ✅

Phase 3: 文档
  [ ] README 数字与实际一致
  [ ] 版本三处一致

Phase 4: 门禁
  [ ] scripts/pre-push.sh
  [ ] 版本一致性检查
  [ ] 安全红线检查
```

---

## 🔄 工作流速查

```bash
# 新项目起步
mkdir -p project/{docs,scripts,tests} && cd project && git init
# → P0: README .gitignore constraints.md
# → P1: pyproject.toml CHANGELOG.md bump-version.py
# → P2: .github/workflows/ci.yml → 本地测试 → push
# → P3: 对齐 README
# → P4: pre-push.sh

# 版本发布
python3 scripts/bump-version.py patch  # story/debug
python3 scripts/bump-version.py minor  # spec
python3 scripts/bump-version.py major  # epic

# 推送
bash scripts/pre-push.sh
git push origin main --tags
```
