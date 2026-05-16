---
name: doc-alignment
description: "文档对齐协议 v4.0 — BMAD 式声明式依赖 + 层级事实链 + 自动门禁。文档在 frontmatter 用 `inputs` 字段声明数据依赖 → 脚本自动解析依赖图 → pre-commit 只检查受影响文档。融合 v3.x HTML 报告生命周期管理。每个项目必须用此工作流管理文档一致性。"
version: 4.0.0
triggers:
  - 文档对齐
  - 文档一致性
  - 上下文污染
  - 文档漂移
  - 同步文档
  - 文档陈旧
  - documentation alignment
  - doc drift
  - 项目报告
  - project report
  - PROJECT-PANORAMA
  - html报告
  - 生成报告
  - 报告生成
  - generate report
  - 生命周期
  - documentation lifecycle
  - report lifecycle
  - 全景报告
  - 报告模板
  - 项目全貌
  - 报告缺乏模板
  - 报告设计
  - 报告结构
  - panorama
  - 文档不够全面
  - 无法对齐
  - 重新设计报告
  - 漂移预防
  - 数据层级
  - SSoT
  - single source of truth
  - 门禁
  - pre-commit
  - 文档漂移检测
  - drift prevention
  - source of truth
  - 文档一致性检查
  - 文档门禁
  - doc consistency
  - 六层根因
  - data authority
  - 声明式依赖
  - inputs
  - 层级事实链
  - hierarchical fact chain
  - BMAD
  - bmad-method
  - document-as-cache
author: Emma (小玛)
license: MIT
allowed-tools:
  - read_file
  - patch
  - write_file
  - search_files
  - terminal
  - skill_view
  - memory
metadata:
  hermes:
    tags:
    - documentation
    - workflow
    - quality
    - alignment
    - lifecycle
    - report
    - html
    - project-overview
    category: dogfood
    skill_type: workflow
    design_pattern: lifecycle
---

# 📋 文档对齐协议 v4.0 — BMAD 式声明式依赖 + 自动门禁

> **核心变革 v4.0**: 从「手动操作手册」升级为「声明式依赖框架 + 自动门禁」。  
> 受 **BMAD Method** `inputs` 字段启发：文档在 frontmatter 声明数据依赖 → 脚本自动检测 → 门禁拦截。  
> **v4.0 新增**: §决定式依赖规范、§四层防御体系、§自动验证引擎、§层级事实链

## 对 v3.x 的改进

| 维度 | v3.x (旧) | v4.0 (新) |
|:-----|:----------|:----------|
| 定位 | 📖 手动操作手册 | ⛓️ 声明式依赖框架 + 自动门禁 |
| 触发方式 | 人想到才用 | git commit 自动触发 |
| 工作方式 | 全量手动检查 | 增量自动检查（只验证受影响文档） |
| 依赖 | 人脑记忆 | 机器可读的 `inputs` 声明 |
| 数据依赖 | 隐含在文档中 | 显式声明在 frontmatter |
| 状态追踪 | 无 | 文档自身记录 alignment 字段 |

---

## §1 声明式数据依赖 (受 BMAD Method `inputs` 字段启发)

### 理念

每个文档在 frontmatter 中声明它派生了哪些外部数据源。就像 BMAD 在 TOML 中用 `persistent_facts` 声明上下文依赖，文档用 `inputs` 字段声明数据依赖。

### 格式规范

```yaml
# 文档的 frontmatter 示例
---
name: my-document
inputs:
  - source: pyproject.toml                          # 数据源（文件路径或 shell 命令）
    fields: [version, python_requires]              # 本文档用到的字段
    description: "项目版本号和 Python 版本要求"
  - source: "pytest --collect-only"
    fields: [test_count]
    description: "当前测试总数"
  - source: docs/project-state.yaml
    fields: [epic_status]
    extract: |                                      # 可选：提取值的命令
      python3 -c "
      import yaml
      d = yaml.safe_load(open('docs/project-state.yaml'))
      for k, v in d['entities']['epics'].items():
          print(f'{k}={v[\"state\"]}')
      "

# 文档对齐状态追踪
alignment:
  last_verified: "2026-05-16"
  verified_by: "boku"
  drift_count: 0
---
```

| 字段 | 必填 | 类型 | 说明 |
|:-----|:----:|:-----|:------|
| `source` | ✅ | string | 数据源路径（相对项目根）或 shell 命令 |
| `fields` | ✅ | string[] | 本文档从此源使用的字段名 |
| `description` | ❌ | string | 人类可读说明 |
| `extract` | ❌ | string | 提取值的命令，不写则用默认方式 |

### `source` 的三种类型

| 类型 | 语法 | 示例 | 验证方式 |
|:-----|:------|:------|:---------|
| 文件路径 | 直接路径 | `pyproject.toml` | git diff 检测 |
| shell 命令 | 完整命令 | `"pytest --collect-only"` | 运行命令对比输出 |
| glob 模式 | 含通配符 | `packs/*/cap-pack.yaml` | 检查匹配文件变更 |

### 层级事实链 (Hierarchical Fact Chain)

```
Level 0: 权威来源 (SSoT)
  pyproject.toml          ← 版本号、依赖、Python
  docs/project-state.yaml ← EPIC 状态
  pytest --collect-only  ← 测试数（运行时）
  packs/*/cap-pack.yaml  ← 能力包列表

Level 1: 结构化派生
  docs/project-report.json  ← 从 L0 聚合

Level 2: 人类可读展示
  README.md / QUICKSTART.md / ADAPTER_GUIDE.md / EPIC-*.md
```

**铁律**: 更新数据时只改 SSoT，派生文件通过脚本/模板同步。

参考文件: `docs/standards/document-alignment-v2-spec.md`

---

## §2 四层防御体系: 从源头杜绝文档漂移 🔥

> **核心教训**: 门禁越靠左，修复成本越低。  
> `🟢 commit 前(10秒) < 🟡 CI 发现(5分钟) < 🔴 发布后(30分钟+)`

### 第 1 层: 定义数据层级 SSoT

每个项目初始化时定义：

```text
数据项           权威来源(SSoT)       派生文件
────────────────────────────────────────────────
版本号           pyproject.toml       README, project-report, PANORAMA
测试数           pytest (运行时)      README, project-report
EPIC 状态        project-state.yaml   project-report, EPIC 文档
CLI 命令         CLI help (运行时)    README, QUICKSTART, ADAPTER_GUIDE
```

### 第 2 层: pre-commit 漂移检测脚本

在 `scripts/pre-push.sh` 中加入：

```bash
check_doc_consistency() {
    local errors=0
    # 版本号一致性
    PYPROJ_VER=$(grep "^version" pyproject.toml | grep -oP '\d+\.\d+\.\d+')
    for f in README.md docs/project-report.json; do
        FVER=$(grep -oP '\d+\.\d+\.\d+' "$f" | head -1)
        [ "$PYPROJ_VER" != "$FVER" ] && echo "❌ $f: $FVER" && errors=$((errors+1))
    done
    # EPIC 状态一致性
    python3 -c "..." || errors=$((errors+1))
    # CLI 入口一致性
    grep -rn 'scripts\.cli\.main' docs/ && errors=$((errors+1))
    [ "$errors" -gt 0 ] && echo "🔴 $errors 个漂移" && return 1
    echo "✅ 通过"
}
```

### 第 3 层: CI 漂移门禁

GitHub Actions 中增加 `doc-consistency` job，在 PR 和 push 时自动检查。

### 第 4 层: 提交模板提醒

在 `.gitmessage` 中加入 SSoT 检查清单。

---

## §3 自动验证引擎

### 三个核心脚本

| 脚本 | 用途 | 命令 |
|:-----|:------|:------|
| `scripts/parse-inputs.py` | 解析所有文档的 `inputs` 声明，构建依赖图 | `python3 scripts/parse-inputs.py .` |
| `scripts/detect-drift.py` | 给定 git diff → 只验证受影响文档 | `python3 scripts/detect-drift.py` |
| `scripts/validate-inputs.py` | 验证单个文档的 inputs 是否最新 | `python3 scripts/validate-inputs.py README.md` |

### 使用流程

```bash
# 1. 解析依赖图
python3 scripts/parse-inputs.py .
# 输出: {"pyproject.toml": [("README.md", ["version"]), ...]}

# 2. 检测本次变更影响的文档
python3 scripts/detect-drift.py HEAD
# 输出: {"README.md": ["version"], "docs/project-report.json": ["version"]}

# 3. 验证受影响文档
python3 scripts/validate-inputs.py README.md
# 输出: ✅ README.md 全部 inputs 验证通过
```

---

## 老版本内容保留 (v3.x HTML 报告生命周期管理)

以下内容继承自 v3.x，适用于 HTML 全景报告管理，但推荐优先使用 §1-§3 的声明式依赖 + 自动门禁方案。

### 强制门禁：每次文档变更后必须更新 HTML 报告

> **🚨 铁律**: 任何修改 `project-report.json` / 文档结构 / 模块体系 / Story 状态的操作，**必须** 在 git commit **前** 执行 Phase 1.1 → 1.2 → 1.3。
>
> **违反后果**: HTML 报告与项目实际状态不同步 → 全景报告成为「一次性快照」而非「持续对齐仪表盘」
>
> **合规流程**:
> ```bash
> # 1. 修改 project-report.json（Phase 1.1）
> # 2. 重新生成 HTML 报告（Phase 1.2）
> # 3. 运行 --verify 确认零漂移（Phase 1.3）
> # 4. git add 数据文件 + HTML 报告 + 代码变更
> # 5. git commit
> ```

### Phase 0: 分析前对齐 — Reality Check 🔍

> **P0 门禁**: 在任何「分析项目现状」或「读取项目文档」之前，先执行此阶段。
> 否则你分析的是"文档的世界"而非"代码的世界"。

**时机**: 读取任何文档前 / 开始 Sprint 规划前 / 接手不熟悉的项目时

### 五步验证

```bash
# 1. 看代码最近做了什么
git log --oneline -30 | head -15

# 2. 看测试是否真的通过（不要信文档说的测试数）
python -m pytest tests/ --collect-only -q 2>&1 | tail -1

# 3. 看关键文件是否存在（文档所称"缺失"的文件）
ls -la path/to/alleged-missing-file 2>/dev/null && echo "EXISTS" || echo "MISSING"

# 4. 看版本号（文档所称 vs 实际）
python -c "import json; d=json.load(open('docs/project-report.json')); print('Doc version:', d['project']['version'])"
grep "__version__" src/__init__.py

# 5. 运行 --verify 检测漂移
python3 ~/.hermes/scripts/generate-project-report.py --data docs/project-report.json --verify
```

### 决策

| 验证结果 | 行为 |
|:---------|:-----|
| ✅ 完全一致 | 信任文档，继续分析 |
| ⚠️ 轻微差异（版本号、测试数） | 以代码为准，分析中注明差异 |
| 🔴 重大差异（文件存在性、Story 状态） | 先同步文档，再继续分析 |

### Phase 1: 每次开发迭代（Story/Sprint 完成时）

**强制流程** — 每次完成任务后，在 git commit **之前** 执行：

### 1.1 更新数据文件

修改 `docs/project-report.json` 中的以下字段：

| 场景 | 需要更新的字段 |
|:-----|:--------------|
| 新增模块 | `architecture.module_table[]` |
| 新增 API | `api_endpoints.http[]` 或 `.socket_actions[]` |
| 新增 CLI | `cli_commands[]` |
| Story 完成 | `epics[].stories[].status = "completed"` |
| 测试增长 | `tests.passing`, `.total`, `.files[]` |
| 版本升级 | `project.version` |
| Sprint 完成 | `sprint_history[]` 新增条目 |

### Phase 2: 版本发布前 — 六源交叉审计

> **⚠️ 2026-05-16 新增**: 发布前的审计从「1-2 个文件检查」升级为跨 6 个数据源的**系统性多源漂移检测**。

### 2.0 预检清单

```text
□ project-report.json 与 pyproject.toml 版本一致
□ README 和 PROJECT-PANORAMA.html 的测试数与 pytest --collect-only 一致
□ EPIC docs 中 epics-id frontmatter status 与 project-state.yaml 中的完成数一致
□ project-state.yaml 的 EPIC completed_count 与实际 Story 文件数一致
□ CHANGELOG 覆盖了自上次发布以来的所有版本变更
□ 全量测试通过（pytest -q）
□ git status clean，无未提交变更
```

### 2.1 六源交叉审计（Multi-Source Drift Scan）

```bash
# 数据源矩阵:
# ① pyproject.toml   → 版本
# ② README.md        → 版本 + 测试数
# ③ PROJECT-PANORAMA.html → 版本 + 测试数
# ④ project-report.json  → 结构化数据
# ⑤ project-state.yaml   → EPIC 状态
# ⑥ EPIC*.md         → EPIC header status
```

### Phase 3: 跨项目复用指南

### 项目初始化脚本

```bash
# 1. 创建数据目录
mkdir -p docs

# 2. 用模板创建 project-report.json
cp ~/.hermes/skills/dogfood/doc-alignment/references/project-report-template.json \
   docs/project-report.json

# 3. 编辑 project-report.json 填入项目信息

# 4. 创建 .gitmessage 提交模板（含 SSoT 检查清单）

# 5. 安装 pre-commit 漂移检测
cp ~/.hermes/skills/dogfood/doc-alignment/references/drift-prevention-four-layers.md \
   docs/references/
```

---

## 参考文件

| 文件 | 内容 | 适用场景 |
|:-----|:-----|:---------|
| `references/drift-prevention-four-layers.md` | **四层防御体系** — SSoT 定义 + pre-commit 脚本 + CI 门禁 + 提交模板 | 文档漂移预防，每个项目初始化时安装 |
| `references/project-report-template.json` | 项目报告 JSON 模板 | 新项目初始化报告 |
| `references/sra-drift-detection.md` | Sprint 2 实测漂移检测命令、根因分析、修复流程 | SRA 项目文档对齐 |
| `references/cap-pack-implementation.md` | hermes-cap-pack 项目实战记录 | 新项目初始化时的参考蓝本 |
| `references/panorama-template-design.md` | 10 章节全景报告模板设计（arc42 + CODITECT） | 设计全景报告时使用 |
| `references/version-alignment-automation.md` | 版本号自动对齐 — bump-version.py sync | 版本号一键同步 |
| `references/ac-audit-methodology.md` | AC 审计方法论 — 五层根因模型 | 理解文档漂移根因 |
| `references/project-report-json-rebuild.md` | project-report.json 全量重建指南 | 系统性漂移修复 |
| `references/epic-ac-verification.md` | Epic Story AC 深度审计 | 接手文档过时的 Epic |

## 外部参考

| 文件 | 内容 | 位置 |
|:-----|:------|:------|
| `docs/analysis/doc-alignment-root-cause.md` | 六层根因分析 + 改进方案 A-E | 项目仓库 `docs/analysis/` |
| `docs/analysis/doc-alignment-deep-dive.md` | BMAD 式声明式依赖 + 缺失门禁场景枚举 | 项目仓库 `docs/analysis/` |
| `docs/standards/document-alignment-v2-spec.md` | inputs 字段规范 + 层级事实链 + 自动验证引擎设计 | 项目仓库 `docs/standards/` |
