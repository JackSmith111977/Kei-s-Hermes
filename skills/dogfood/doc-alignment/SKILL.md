---
name: doc-alignment
description: "文档对齐协议 v3.3 — 数据驱动 HTML 报告完整生命周期管理。包含 project-report.json 标准格式定义、generate-project-report.py 生成器使用、5 步对齐协议、10 章全景报告模板设计（arc42 + CODITECT）。每个项目必须用此工作流管理文档一致性。"
version: 3.3.0
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
>
> **⚠️ 2026-05-14 重要变更**: HTML 生成方式从 `generate-project-report.py` 脚本模板
> 升级为 `project-report-generator` Hermes Skill 的 LLM 驱动五阶段创作。
> 项目报告的数据源（project-report.json）生命周期管理和对齐协议保持不变，
> 但 HTML 创作层已替换为更灵活、更高质量的 Skill 驱动模式。
> **详见 [新方案对照表](#新方案与旧方案的对比)**。

## 强制门禁：每次文档变更后必须更新 HTML 报告

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
│  │   │   │                            │
│        │                       │                            │
│        ▼                       ▼                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ~/.hermes/scripts/generate-project-report.py         │   │
│  │ 读取 JSON 数据 → 渲染 HTML → 输出 PROJECT-PANORAMA  │   │
│  │ .html + --verify 模式检测漂移                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ⚠️ 2026-05-14: HTML 创作层已升级                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ project-report-generator Hermes Skill                │   │
│  │ 五阶段 LLM 驱动创作 (Phase 0~4 + 门禁)               │   │
│  │ 替代 generate-project-report.py 的脚本模板模式        │   │
│  │ project-report.json 作为数据源保持不变                │   │
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

### 新方案与旧方案的对比 (2026-05-14)

| 维度 | 旧方案 (generate-project-report.py) | ✅ 新方案 (project-report-generator skill) |
|:-----|:---------------------------------|:----------------------------------------|
| HTML 生成方式 | Python 脚本 + `.replace()` 模板替换 | LLM 五阶段从零创作 (Phase 0~4) |
| 设计灵活性 | 固定模板，改设计需改代码 | 每次根据项目特点定制配色/布局/叙事 |
| LLM 参与度 | 无（LLM 只写脚本，不参与创作） | LLM 全程驱动：分析数据→设计叙事→创作 HTML |
| 质量管理 | 无 Review 流程 | R1/R2/R3 三层反思门禁 + QG 综合门禁 |
| 数据源 | project-report.json | project-report.json + SQS DB + git + 文档扫描 |
| 复用方式 | CLI 脚本跨项目调用 | Hermes Skill 跨项目加载 |
| 可组合性 | 独立脚本 | 可配合 web-ui-ux-design / visual-aesthetics 等 skill |

**向后兼容说明**:
- `project-report.json` 数据格式完全不变，仍作为项目主数据源
- `--verify` 漂移检测逻辑仍保留（在 skill 的 Phase 4 门禁中手工验证）
- 旧脚本 `generate-project-report.py` 不再自动调用，保留但不维护

---

## Phase 0: 项目初始化时的报告创建

**时机**: 项目创建 / AGENTS.md 设置时

```bash
# 1. 创建 project-report.json 标准文件
#    放在 docs/project-report.json

# 2. 编辑 JSON，填入项目基本信息
#    模板参考: skill_view(name="doc-alignment", file_path="references/project-report-template.json")

# 3. 生成初始 HTML 报告
#    ⚠️ 旧方案 python3 generate-project-report.py 已废弃
#    ✅ 改用 project-report-generator skill 五阶段创作
#    加载 skill 后按 Phase 0→1→2→3→4 流程创作

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

### 1.2 创作 HTML 报告

⚠️ **脚本模板已废弃** — 不再直接调用 `generate-project-report.py`。改为加载 Hermes Skill 进行五阶段 LLM 驱动创作：

```yaml
# 三步组合装（替代旧的 python3 generate-project-report.py）
1. skill_view(name='project-report-generator')    # 五阶段创作工作流
2. skill_view(name='web-ui-ux-design')             # UI/UX 设计知识
3. skill_view(name='visual-aesthetics')            # 视觉审美标准
```

然后按 skill 中的 Phase 0 → 1 → 2 → 3 → 4 顺序执行。每次报告都从零创作，设计系统/叙事结构/HTML 代码全部手工定制，无模板替换。

### 1.2a 浏览器预览验证（强制）

HTML 创作完成后，**必须**用浏览器实际预览验证，不能仅凭代码判断：

```bash
# 1. 浏览器导航到本地 HTML 文件
browser_navigate(url="file:///path/to/PROJECT-PANORAMA.html")

# 2. 检查渲染结果中的关键元素（通过返回的 snapshot 确认）
#    - 标题是否正确
#    - KPI 卡片数字是否正确
#    - 所有章节是否渲染
#    - 表格/卡片/时间线是否完整

# 3. 如有视觉异常 → 回到 1.2 修正后再预览
```

**常见失败模式**:
- ❌ HTML 标签未闭合 → 页面空白或截断
- ❌ CSS 类名拼写错误 → 样式不生效
- ❌ JS 变量未定义 → Chart.js 不渲染
- ❌ 路径错误 → 图片/外部资源 404

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

### 生成器位置 (旧方案，不再维护)

> ⚠️ 2026-05-14: 生成方案已从 `generate-project-report.py` 脚本升级为 `project-report-generator` Hermes Skill。
> 旧脚本保留但不维护，新项目请使用 Hermes Skill 方案。

- 修改生成器 → 所有项目的 HTML 自动获得更新
- 无需在每个项目安装依赖（纯 Python 标准库）
- 可通过 `--output` 指定输出路径，适配不同项目结构

### 数据格式标准

`project-report.json` 的 JSON Schema 见 references/。

**⚠️ 必填字段约定**（generator 解析依赖）：

| 区域 | 字段 | 格式要求 | 示例 |
|:-----|:------|:---------|:------|
| `architecture.module_table[]` | 每行 | **必须**含 `module`/`file`/`desc`/`methods` 四个 key | `{"module": "Parser", "file": "parser.py", "desc": "解析器", "methods": ["parse()"]}` |
| `architecture.layers[].modules[]` | 模块名 | **string 数组**，非对象 | `["ModuleA", "ModuleB"]` |
| `epics[].stories[]` | 每行 | **必须**含 `id`/`name`/`status` | `{"id": "STORY-1-1", "name": "功能", "status": "completed"}` |
| `tests.files[]` | 每行 | **必须**含 `name`/`tests`/`passing` | `{"name": "test_a.py", "tests": 10, "passing": 10}` |

**常见错误**: 使用 `id`/`name`/`path`/`lines` 替代 `module`/`file`/`desc`/`methods` 会报 `KeyError: 'module'`。所有字段名必须完全匹配 generator 期望。

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
| `references/cap-pack-implementation.md` | hermes-cap-pack 项目实战记录 — project-report.json 完整数据示例 | 新项目初始化时的参考蓝本 |
| `references/panorama-template-design.md` | **10 章节全景报告模板设计**（基于 arc42 + CODITECT）— 含每节规格、数据源矩阵、HTML 模板技术 | 设计/重写项目全景报告时使用 |
| `references/version-alignment-automation.md` | **版本号自动对齐** — bump-version.py sync 实现原理 + 扩展指南 | 文档版本号不同步时的一键修复方案 |
| `references/merge-annotation-pattern.md` | **模块合并标注模式** — `[^n]` 脚注工作流 + 全文档交叉引用清单 + 变更原因标注规范 | 合并/重命名/废弃模块时的全文档对齐操作，含实战可复用的 checklist |
## Phase 4: 全景报告模板重设计

> **前置条件**: 当用户指出当前项目报告"缺乏模板/内容不全面/无法做文档对齐"时，走此流程。
> **典型信号**: 用户说"深度循环学习一下项目报告文档的设计"、"报告缺乏明确的模板"

**时机**: 项目全景报告自身的设计存在结构性缺陷时（不是数据过时，而是模板不够好）

### 4.1 需求诊断

用户指出项目报告的问题通常属于以下三类之一：

| 问题类型 | 判断标准 | 解决方案 |
|:---------|:---------|:---------|
| 🏗️ **模板缺失** | 报告没有固定的章节结构，信息随意堆叠 | 设计标准化模板（见下方 10 章模板） |
| 📉 **覆盖不足** | 缺少架构/质量/风险/路线图等关键视角 | 按 10 章模板补全缺失章节 |
| 🔗 **无法对齐** | 报告内容无法追溯到 SDD 文档体系 | 每节标注数据源和对应文档路径 |

### 4.2 方法论基础 — 三大标准融合

设计全景报告模板时，融合以下业界标准：

| 标准 | 来源 | 贡献 |
|:-----|:------|:------|
| **arc42** (12 章) | arc42.org — 软件架构文档行业标准 | 架构描述、约束条件、质量场景的结构化方法 |
| **CODITECT** (8 节) | CODITECT 项目状态报告标准 | 执行摘要+状态仪表盘+关键交付+风险 |
| **项目管理最佳实践** | Atlassian/Asana 项目报告模板 | KPI 卡片、进度条、Sprint 时间线 |

### 4.3 标准化 10 章模板

```
┌─ 头部: 项目身份 + 元数据 + 状态徽章
│
├─ §1 执行摘要 (BLUF)
│   ├─ 一句话结论
│   ├─ N 个 KPI 卡片（版本/测试/健康/Story 数/代码量/报告数）
│   └─ 健康度仪表盘
│
├─ §2 项目概况
│   ├─ 背景与目标
│   ├─ 范围与边界
│   └─ Sprint 时间线
│
├─ §3 架构总览
│   ├─ N 层架构图
│   ├─ 模块全景表（含质量分）
│   └─ 技术栈矩阵
│
├─ §4 Epics & 交付进度
│   ├─ Epic 状态卡（含完成率进度条）
│   ├─ Story 交付清单
│   └─ 文档对齐矩阵（Story ↔ Spec ↔ EPIC）
│
├─ §5 质量全景
│   ├─ 总体健康度 + 趋势
│   ├─ 五维分析
│   ├─ 模块分布
│   └─ 低分排行榜
│
├─ §6 测试与 CI/CD
│   ├─ 测试统计 + 文件分布
│   ├─ CI 门禁状态
│   └─ 自动化 pipeline
│
├─ §7 文档体系
│   ├─ SDD 文档树（类型/名称/状态/路径链接）
│   └─ 文档对齐矩阵（可追溯性）
│
├─ §8 风险与技术债务
│   ├─ 已知问题
│   ├─ P0/P1/P2 待办
│   └─ 改进建议
│
├─ §9 路线图
│   ├─ 已完成
│   ├─ 当前阻塞
│   └─ 规划中
│
└─ §10 附录
    ├─ 术语表
    └─ 数据源说明
```

### 4.4 实现模式

**数据驱动**: 报告内容从结构化数据源自动生成（project-report.json + 数据库查询 + 文件扫描 + git 状态），不手写硬编码。

**HTML 模板技术**: 使用占位符替换模式而非 f-string，避免 CSS/JS 花括号与 f-string 语法冲突：

```python
# ❌ 不要用 f-string 嵌入 HTML 模板（花括号冲突）:
html = f"""<style>.cls {{ color: {val} }}</style>"""

# ✅ 用占位符替换:
TEMPLATE = """<style>.cls { color: __VAL__ }</style>"""
html = TEMPLATE.replace("__VAL__", str(val))
```

**文档对齐**: 每节标注数据源路径，支持从报告到原始文档的双向追溯。

### 4.5 数据源矩阵

| § | 章节 | 数据源 | 文档对齐 |
|:-:|:-----|:-------|:--------:|
| 1 | 执行摘要 | project-report.json | — |
| 2 | 项目概况 | project-report.json | EPIC/Spec 文档 |
| 3 | 架构总览 | JSON + SQS DB | SPEC-2-1 |
| 4 | Epics | project-report.json | 全部 docs/*.md |
| 5 | 质量全景 | SQS DB (SQLite) | SPEC-2-2 |
| 6 | 测试 | project-report.json | .github/workflows/ |
| 7 | 文档体系 | docs/ 目录扫描 | docs/*.md |
| 8 | 风险 | SQS DB | EPIC-xxx |
| 9 | 路线图 | project-report.json | — |
| 10 | 附录 | 静态 | — |

### 🚩 实战教训（2026-05-14, hermes-cap-pack）

**背景**: PROJECT-PANORAMA.html 只有简单信息陈列，缺乏模板结构。主人指出无法做文档对齐。

**修复流程**:
1. 学习 arc42 + CODITECT + 项目管理三大标准
2. 设计 10 章模板结构
3. 实现 `scripts/generate-panorama.py`（数据驱动生成器）
4. 生成新 HTML → 所有 10 章自动填充

**关键教训**:
- ❌ HTML 模板不要用 f-string（花括号与 CSS/JS 冲突不可调和）
- ✅ 用占位符字符串（`__PLACEHOLDER__`）+ `.replace()` 替换
- ✅ 数据驱动比手写 HTML 更可靠、更易维护
- ✅ 每节标注数据源 = 文档对齐的基础设施

---

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
