---
name: doc-alignment
description: "文档对齐协议 v3.0 — 数据驱动 HTML 报告完整生命周期管理。包含 project-report.json 标准格式定义、generate-project-report.py 生成器使用、5 步对齐协议。每个项目必须用此工作流管理文档一致性。"
version: 3.2.0
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

# 📋 文档对齐协议 v3.0 — 数据驱动的 HTML 报告生命周期

> **核心变革**: 从「手写 HTML + 事后对齐」升级为「数据驱动 + 自动生成 + 全生命周期管理」

## Phase 0: 分析前对齐 — Reality Check 🔍

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

### 实战案例

参见 `development-workflow-index` §11 Reality Check — 分析前对齐协议。
SRA Sprint 3 因跳过此步骤导致分析误差。

### 深度审计 — Epic Story AC 验证

当文档声称完成度与代码实际差距巨大时（如 EPIC-003 声称 ~40% 但实际 ~95%），  
需要从「5 步快速检查」升级为「逐 Story AC 深度审计」：

```bash
# 0. 🔴 先运行 AC 审计脚本（如果项目有）
python3 scripts/ac-audit.py check docs/EPIC-*.md
# 自动检测代码已实现但文档未勾选的 AC，输出漂移数

# 1. 扫描代码全景
find . -type f -name "*.py" | sort

# 2. 逐 Story AC 核查（文件存在性 + 关键实现检查 + 项目级 grep）
#    详细方法论见:
#    - references/ac-audit-methodology.md（AC 审计通用方法）
#    - references/epic-ac-verification.md（Epic 级验证）

# 3. 运行测试验证
python -m pytest tests/ -x --tb=short -q

# 4. 批量同步 AC（用 ac-audit sync 替代手工勾选）
python3 scripts/ac-audit.py sync docs/EPIC-*.md --apply
# 或使用 execute_code + hermes_tools.patch 避免换行符转义问题
```

详见:
- `references/ac-audit-methodology.md` — 五层根因模型 + 三重加固工作流 + AC 可验证信号速查
- `references/epic-ac-verification.md` — Epic AC 逐项验证方法论

---

## 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                   项目报告生命周期                            │
│                                                             │
│  ① 初始化                 ② 每次迭代             ③ 发布前   │
│  ┌─────────┐              ┌─────────┐           ┌────────┐ │
│  │ 创建     │              │ 更新     │           │ 最终   │ │
│  │ project- │  →  代码变更  │ project │  →  版本  │ 验证 + │ │
│  │ report   │              │ report  │           │ 发布   │ │
│  │ .json    │              │ .json   │           │        │ │
│  └─────────┘              └────┬────┘           └────────┘ │
│        │                       │                            │
│        ▼                       ▼                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ~/.hermes/scripts/generate-project-report.py         │   │
│  │ 读取 JSON 数据 → 渲染 HTML → 输出 PROJECT-PANORAMA  │   │
│  │ .html + --verify 模式检测漂移                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 关键变更

| 维度 | v2.x (旧) | v3.0 (新) |
|:-----|:----------|:----------|
| HTML 维护方式 | 手写，易遗漏 | 自动生成，保证一致 |
| 数据源 | 无（直接编辑 HTML） | `docs/project-report.json`（单一数据源） |
| 跨项目复用 | 每个项目各自手写 | 同一生成器 `~/.hermes/scripts/generate-project-report.py` |
| 版本号同步 | N 处手动改 | 改 1 处 JSON → 全同步 |
| 验证能力 | 无 | `--verify` 自动对比代码状态 |
| 工作流位置 | 事后补救 | 全生命周期内置 |

---

## Phase 0: 项目初始化时的报告创建

**时机**: 项目创建 / AGENTS.md 设置时

```bash
# 1. 创建 project-report.json 标准文件
#    放在 docs/project-report.json

# 2. 编辑 JSON，填入项目基本信息
#    模板参考: skill_view(name="doc-alignment", file_path="references/project-report-template.json")

# 3. 生成初始 HTML
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json \
  --output PROJECT-PANORAMA.html

# 4. 验证
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json --verify

# 5. 提交
git add docs/project-report.json PROJECT-PANORAMA.html
git commit -m "docs: init project report"
```

**必填字段**（简化版 — 至少填这些才能生成可用报告）:
```json
{
  "project": {
    "name": "...",
    "version": "...",
    "description": "...",
    "overview_cards": [{"label":"名称","value":"...","sub":"..."}],
    "info_table": [{"attr":"作者","value":"..."}]
  },
  "architecture": {"layers": [], "module_table": []},
  "api_endpoints": {"http_port": 0, "http": [], "socket_actions": []},
  "cli_commands": [],
  "epics": [{"id":"...","name":"...","stories":[]}],
  "tests": {"passing": 0, "total": 0, "duration_seconds": 0, "files": []},
  "sprint_history": []
}
```

---

## Phase 1: 每次开发迭代（Story/Sprint 完成时）

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

### 1.2 重新生成 HTML

```bash
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json \
  --output PROJECT-PANORAMA.html
```

### 1.3 运行验证

```bash
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json --verify
```

### 1.4 单次提交（数据 + HTML + 代码）

```bash
git add docs/project-report.json PROJECT-PANORAMA.html <其他代码文件>
git commit -m "feat: ..."
```

---

## Phase 2: 版本发布前

### 2.1 全面验证

```bash
# 验证数据一致性
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json --verify

# 对比 HTML 与 API-REFERENCE.md 的端点列表
echo "=== HTTP Endpoints ==="
grep -c "POST /force" PROJECT-PANORAMA.html
grep -c "POST /force" docs/API-REFERENCE.md

echo "=== CLI Commands ==="
grep -c "sra force" PROJECT-PANORAMA.html
grep -c "sra force" docs/API-REFERENCE.md
```

### 2.2 版本号一致性检查

```bash
# project-report.json vs __init__.py (静态包)
JSON_VER=$(python3 -c "import json; print(json.load(open('docs/project-report.json'))['project']['version'])")
INIT_VER=$(grep "__version__" skill_advisor/__init__.py | grep -oP '"\\K[^"]+')
if [ "$JSON_VER" != "$INIT_VER" ]; then
  echo "❌ 版本号不一致: $JSON_VER vs $INIT_VER"
fi

# ⚠️ 对于 setuptools-scm 动态版本的项目（如 SRA），__init__.py 中无静态版本号，
#    --verify 会误报版本号漂移。这是已知限制——setuptools-scm 在构建时从 git tag
#    推导版本，__init__.py 只有多级动态 fallback（_version.py → importlib → git describe）。
#    
#    判断方法：如果 git describe 能正确解析出版本号，说明动态版本正常工作：
#    git describe --tags --long  # 示例输出: v2.0.2-2-gfd5a6b6
#    
#    在这种情况下，以 git tag 为准，忽略 --verify 的版本号误报。
```

### 2.3 测试数量验证

```bash
pytest tests/ --collect-only -q 2>&1 | tail -1
# 对比 project-report.json 中的 tests.passing
```

---

## Phase 3: 跨项目复用指南

### 项目初始化脚本

任何新项目可以使用以下命令初始化报告：

```bash
# 1. 创建数据目录
mkdir -p docs

# 2. 用模板创建 project-report.json
cp ~/.hermes/skills/dogfood/doc-alignment/references/project-report-template.json \
   docs/project-report.json

# 3. 编辑 project-report.json 填入项目信息

# 4. 生成 HTML
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json \
  --output PROJECT-PANORAMA.html

# 5. 加入 .gitignore 排除？不——PROJECT-PANORAMA.html 应被追踪！
#    project-report.json 是数据源，也需追踪
```

### 生成器位置

生成器位于 `~/.hermes/scripts/generate-project-report.py`，所有项目共享。

- 修改生成器 → 所有项目的 HTML 自动获得更新
- 无需在每个项目安装依赖（纯 Python 标准库）
- 可通过 `--output` 指定输出路径，适配不同项目结构

### 数据格式标准

`project-report.json` 的 JSON Schema 见 references/。

---

## 漂移检测清单

### 高频漂移（每次开发必须检查）

| 检查项 | 检测命令 |
|:-------|:---------|
| 版本号一致性 | `JSON_VER VS __init__.py` |
| 新 API 端点 | `grep -c 新端点 docs/API-REFERENCE.md` |
| Story 状态 | `epics[].stories[].status` 是否及时更新 |
| 测试数量 | `pytest --collect-only` 对比 project-report.json |

### 中频漂移（Sprint 完成时检查）

| 检查项 | 检测命令 |
|:-------|:---------|
| CLI 命令列表 | 对比 `cli.py` COMMANDS dict 与 project-report.json |
| 模块列表 | 对比实际文件与 `module_table[]` |
| Sprint 历史 | `sprint_history[]` 是否最新 |

### 低频漂移（版本发布前检查）

| 检查项 | 检测命令 |
|:-------|:---------|
| raw URL 分支 | `grep 'raw.*main/' README.md` vs `git branch -r \| grep origin/HEAD` |
| LICENSE 年份 | 当前年份 vs LICENSE 文件 |
| 作者信息 | 团队成员变更 |

---

## 参考文件

| 文件 | 内容 | 适用场景 |
|:-----|:-----|:---------|
| `references/sra-drift-detection.md` | Sprint 2 实测漂移检测命令、根因分析、修复流程 | SRA 项目文档对齐 |
| `references/project-report-template.json` | 项目报告 JSON 模板 | 新项目初始化报告 |
| `references/system-redesign-case-study.md` | 系统性改造实战案例（构建→验证→通用化） | 改造类任务的参考方法论 |
| `references/epic-ac-verification.md` | Epic Story AC 深度审计方法论—文档对标代码的逐项验证 | 接手文档过时的 Epic 时使用 |
| `references/ac-audit-methodology.md` | AC 审计方法论—五层根因模型 + 三重加固工作流 + 可验证信号速查 | 理解文档漂移根因 + 实施 AC 自动审计 |

## 实战案例

### SRA 项目迁移实录（2026-05-11）

**背景**: SRA 已完成 Sprint 2，版本 v1.3.0，但 PROJECT-PANORAMA.html 仍显示 v1.2.1

**根因**: 旧工作流中 HTML 是手写的，缺少自动化机制

**修复流程**:
1. 创建 `~/.hermes/scripts/generate-project-report.py`
2. 创建 `docs/project-report.json`（从现有代码提取数据）
3. 运行生成器 → 自动输出 v1.3.0 HTML
4. `--verify` 模式检测到 0 个漂移

**经验**: 数据驱动模式将「HTML 编辑」从手工劳动变成「改 JSON → 点生成」，消除了遗忘的可能性。

---

## 生成器 CLI 参考

```bash
# 生成 HTML
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json \
  --output PROJECT-PANORAMA.html

# 只验证不生成
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json --verify

# 指定不同输出路径
python3 ~/.hermes/scripts/generate-project-report.py \
  --data docs/project-report.json \
  --output ~/public/project-report.html
```
