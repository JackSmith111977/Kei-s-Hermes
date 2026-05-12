---
name: sdd-workflow
description: "Spec-Driven Development 完整工作流 — 从 Spec 创建到代码实现的自动化生命周期管理。含状态机(spec-state.py)、门禁检查(spec-gate.py)、模板库。任何涉及 SDD/规范驱动/Story 开发的任务自动触发。"
version: 1.1.0
triggers:
  - sdd
  - spec-driven
  - 规范驱动
  - 写 spec
  - 创建 story
  - 审批 spec
  - 开发 story
  - 实现 story
  - 验收
  - 完成 story
  - sdd 门禁
  - spec 检查
  - story 模板
  - epic 模板
  - 质量检查
  - 文档质量
  - qa-gate
  - 需求澄清
  - clarify
  - 技术调研
  - 需求确认
  - html对齐
  - 报告对齐
  - 生命周期报告
author: Emma (小玛)
license: MIT
depends_on:
  - development-workflow-index
  - writing-plans
  - test-driven-development
  - doc-alignment
  - commit-quality-check
metadata:
  hermes:
    tags:
      - sdd
      - spec-driven
      - workflow
      - lifecycle
    category: dogfood
    skill_type: workflow
    design_pattern: state-machine
---

# 🧭 SDD Workflow v1.1 — Spec-Driven Development 生命周期管理

> **核心理念**: 没有批准的 Spec 就不写代码。
> **设计模式**: 状态机 + 门禁 + 模板 三位一体

---

## 〇、工作流总览

```
CREATE ──→ REVIEW ──→ APPROVED ──→ IN PROGRESS ──→ COMPLETED ──→ ARCHIVED
 写 Spec    主人审阅   批准开发      实现中           已完成        归档
```

**六个状态，五个转换门禁，每个门禁必须通过才能进入下一状态。**

---

## 一、Spec 生命周期状态机

使用 `scripts/spec-state.py` 管理：

```bash
# 创建新 Spec（初始化状态机）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py create "STORY-004-01" "改进匹配算法"

# 提交审阅（draft → review）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py submit "STORY-004-01"

# 批准（review → approved）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py approve "STORY-004-01"

# 开始实现（approved → in_progress）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py start "STORY-004-01"

# 完成（in_progress → completed）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py complete "STORY-004-01"

# 检查状态
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py status "STORY-004-01"

# 列出现有所有 Spec
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py list
```

### 状态转换规则

| 当前状态 | 允许的操作 | 下一状态 | 门禁条件 |
|:---------|:-----------|:---------|:---------|
| (none) | `create` | draft | 提供 story_id + title |
| draft | `submit` | review | Spec 文件存在 + 必需字段完整 |
| review | `approve` | approved | 主人确认批准 |
| review | `reject` | draft | 记录拒绝原因，退回修改 |
| approved | `start` | in_progress | 无（主人已批准） |
| in_progress | `complete` | completed | pytest 通过 + AC 验证通过 |
| completed | `archive` | archived | doc-alignment 通过 |
| any | `status` | (不变) | 无 |

### 状态文件位置

所有 Spec 状态存储于 `~/.hermes/sdd_state.json`（单个文件，JSON 格式）。

---

## 二、SDD 门禁系统

使用 `scripts/spec-gate.py` 在开发前自动执行：

```bash
# 门禁检查：当前任务是否需要/已有 Spec？
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-gate.py check "改进匹配算法"

# 强制门禁（如果没 Spec 就返回 BLOCKED）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-gate.py enforce "改进匹配算法"
```

### 门禁输出格式

```json
{
  "gate": "spec-approval",
  "passed": true,
  "spec_found": "docs/stories/STORY-004-01.md",
  "spec_status": "approved",
  "message": "✅ Spec 已批准，可以开始开发",
  "blockers": []
}
```

失败时：
```json
{
  "gate": "spec-approval",
  "passed": false,
  "spec_found": null,
  "spec_status": null,
  "message": "❌ BLOCKED: 任务 '改进匹配算法' 没有对应的 Spec",
  "blockers": ["缺少 Spec 文档"]
}
```

### 门禁集成到 AGENTS.md

在开发前门禁中加入：
```bash
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-gate.py enforce "<task_description>"
if [ $? -ne 0 ]; then
    echo "🛑 SDD 门禁拦截！先创建 Spec 再开发。"
    echo "   模板: docs/STORY-TEMPLATE.md（或加载 sdd-workflow skill）"
    exit 1
fi
```

---

## 三、模板系统

### Story Spec 模板

参考文件: `templates/story-template.md`

核心字段：
- **story**: 唯一标识（如 SRA-004-01）
- **title**: 简短标题
- **status**: draft | review | approved | in_progress | completed | archived
- **acceptance_criteria**: 可验证的完成条件列表
- **test_data**: 测试数据契约（source, ci_independent, pattern_reference）
- **spec_references**: 引用链（追溯上游上下文）
- **out_of_scope**: 明确不做的范围

### Epic 模板

参考文件: `templates/epic-template.md`

核心字段：
- **epic_id**: 唯一标识
- **status**: 状态
- **stories**: 包含的 Story 列表
- **test_data_contract**: 测试数据契约

---

## 四、开发前强制流程

```text
[任务开始]
    ↓
1. 🔍 Reality Check（验证代码现实 vs 文档声明）
    ↓
2. 🛑 pre_flight.py 检查
    ↓
3. 📡 skill_finder.py 发现相关 skill
    ↓
4. 📋 SDD Spec 门禁 ← 🔴 本 skill 核心
   ├── spec-gate.py enforce "<task_description>"
   ├── PASS → 继续
   └── BLOCKED → 创建 Spec → 等主人批准 → 再回来
    ↓
5. 📐 测试基础设施检查（已有 fixture 复用）
    ↓
6. 🏗️ 开发（TDD + writing-plans）
    ↓
7. ✅ 验证
   ├── pytest（代码测试）
   ├── doc-alignment（文档漂移检测）
   ├── commit-quality-check（提交前检查）
   └── 🌐 HTML 报告对齐 ← 新增：检查 HTML 生命周期报告是否与文档状态一致
       ├── 如果项目有 `reports/lifecycle.html` 或 `PROJECT-PANORAMA.html`
       ├── 使用 `grep` 对比 HTML 中的状态信息与最新文档状态
       ├── 如有 project-report.json → 运行 `generate-project-report.py` 自动同步
       └── 如无 → 手动更新 HTML 中的状态表格和徽章
    ↓
8. 📋 AC 审计 ← 🔴 新增！确保 Epic AC 与代码同步
   ├── python3 scripts/ac-audit.py check docs/EPIC-*.md
   ├── 确认漂移 = 0
   └── 如未勾选 → python3 scripts/ac-audit.py sync docs/EPIC-*.md --apply
    ↓
9. 📝 Spec 状态更新（complete → archive）
```

---

## 五、与其他 Skill 的集成

| Skill | 集成点 | 触发时机 |
|:------|:-------|:---------|
| `development-workflow-index` | 决策树中 SDD 路径 | 任务开始时 |
| `writing-plans` | 将 Spec 的 AC 转化为实施计划 | APPROVED → IN PROGRESS |
| `test-driven-development` | 每个 AC 对应一个测试 | 实现阶段 |
| `doc-alignment` | Spec 变更后的文档同步 | 任何 Spec 变更后 |
| `commit-quality-check` | 提交前一致性检查 | COMPLETED → ARCHIVED |
| `sra-dev-workflow` | SRA 项目的 SDD 门禁增强 | Phase 1.6 |

---

## 六、已知缺口与改进路线图

> **来源**: SDD 工作流深度审计 (2026-05-12)，基于飞书卡片交互能力 + 文档质量框架 + 学习工作流研究

### 6.1 当前识别的流程缺口

| 缺口 | 阶段 | 问题描述 | 影响程度 |
|:-----|:-----|:---------|:--------:|
| **Gap A** | CREATE 之前 | 缺乏需求澄清阶段 → boku 直接按理解假设需求，可能方向跑偏 | 🔴 高 |
| **Gap B** | CREATE 之前 | 缺乏技术调研/深度学习 → 文档质量依赖已有知识，可能遗漏关键信息 | 🟡 中 |
| **Gap C** | CREATE 之后 | 缺乏质量检查/文档对齐 → 文档错误/遗漏可能无人发现 | 🟡 中 |

### 6.2 改进路线图

```text
v1.1 (短期) — 质量门禁先行
  ├── 新增 qa-gate.py：P0→P1→P2 三层文档质量检查
  ├── 新增 CLARIFY 阶段：用 clarify 工具做需求确认
  └── 更新 spec-state.py：新增 clarify/research/qa_review 状态

v1.2 (中期) — 需求澄清强化
  ├── 新增 RESEARCH 阶段：自动触发 learning-workflow
  └── 需求澄清模板 + 检查清单

v2.0 (长期) — 飞书交互卡片
  ├── 改造 feishu.py 支持交互卡片（按钮+选择器+输入框）
  └── 需求澄清通过交互卡片完成
```

### 6.3 详细设计方案

完整的研究文档见 `references/sdd-known-gaps-and-roadmap.md`，包含：
- 飞书卡片交互能力完全矩阵（button/selectMenu/input/form 的回调机制）
- 文档质量检查 9×1 模型（一致性×逻辑性×完整性 × 结构×内容×体系）
- 改进后 9 状态状态机设计（CLARIFY → RESEARCH → CREATE → QA_GATE → REVIEW → APPROVED → IN_PROGRESS → COMPLETED → ARCHIVED）
- Phase 1-4 实施路径

---

## 🗂️ 文件结构

```
~/.hermes/skills/dogfood/sdd-workflow/
├── SKILL.md                         ← 主入口
├── scripts/
│   ├── spec-state.py                ← 状态机（6 状态 5 转换）
│   └── spec-gate.py                 ← 门禁检查器（check/enforce/verify）
├── templates/
│   ├── story-template.md            ← Story Spec 模板
│   └── epic-template.md             ← Epic 模板
└── references/
    ├── sdd-research.md              ← SDD 深度研究（框架对比 + 数据 + 关键洞察）
    ├── sdd-lifecycle.md             ← 六阶段生命周期指南
    ├── real-world-usage-sra-004-01.md ← 真实项目 SDD 完整走通记录
    └── sdd-known-gaps-and-roadmap.md ← 已知缺口与改进路线图（2026-05-12 新增）
```

## 📚 参考深度阅读

- **`references/sdd-research.md`** — SDD 三大框架（BMAD/Superpowers/GSD）核心对比、成熟度模型、关键数据
- **`references/sdd-lifecycle.md`** — 六阶段完整生命周期指南（CREATE→ARCHIVE 每个阶段的详细操作）
- **`references/real-world-usage-sra-004-01.md`** — 在 SRA 项目中完整走通 SDD 全流程的实战记录
- **`references/sdd-known-gaps-and-roadmap.md`** — 当前流程审计、飞书卡片交互研究、质量检查框架、v2.0 设计草案

## 🚀 使用示例

### 场景 1：新功能开发（含 v2.0 流程）

当使用改进后的 SDD v2.0 流程（参见 §六 已知缺口）时，加入 CLARIFY → RESEARCH → QA_GATE 三个阶段：

```text
# Step 0: CLARIFY — 需求澄清
# boku 输出需求理解 → 主人确认方向正确
# 产出: docs/req_clarification/{task_id}.md
# 方式: clarify 工具或飞书交互卡片

# Step 1: RESEARCH — 技术调研（如需）
# 对不确定的领域走 learning-workflow
# python3 learning-state.py init "调研领域"
# 产出: 调研笔记

# Step 2: CREATE — 创建 Story Spec
python3 spec-state.py create "SRA-005-01" "批量推荐接口"
# 用模板 docs/STORY-TEMPLATE.md 填充内容

# Step 3: QA_GATE — 质量门禁
python3 scripts/spec-gate.py verify "SRA-005-01"   # P0 结构检查
# P1 内容自查 → 加载 self-review 检查准确性
# P2 体系检查 → python3 doc-alignment --verify

# Step 4: REVIEW — 提交审阅
python3 spec-state.py submit "SRA-005-01"
```

⚠️ **常见陷阱**: 跳过 CLARIFY 直接写文档是 SDD v2.0 最常见的违规行为。主人纠正过「文档阶段之前缺乏需求澄清阶段，需要准确了解我的需求」。即使任务看起来简单，也必须先做 CLARIFY——方向跑偏的返工成本远高于几分钟的确认时间。

### 场景 2：SDD 门禁检查（日常开发前）

```bash
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-gate.py enforce "实现批量推荐接口"
# ✅ PASS → 继续开发
# ❌ BLOCKED → 先走场景 1
```

### 场景 3：查看所有 Spec 状态

```bash
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py list
```

---

## 七、铁律

| # | 铁律 | 违背后果 |
|:-:|:-----|:---------|
| 1 | **复杂任务没有获批 Spec 就写代码 = P0 违规** | 方向不对白做、上下文丢失 |
| 2 | **变更代码前必须先更新 Spec** | Spec 与代码不同步 → 下次决策基于错误信息 |
| 3 | **Spec 和代码必须在同一次提交中** | 版本历史无法追溯 |
| 4 | **每个 AC 必须可验证（自动化测试优先）** | 无法判断是否真的完成 |
| 5 | **Spec 过期时间不得超过 7 天** | 代码已变但 Spec 未更新 → 漂移 |
| 6 | **Story 完成时自动同步 Epic AC** | Story Spec 完成 → 运行 ac-audit sync 更新 Epic 文档中对应 AC |

---

## 八、文档质量检查框架（质量门禁原型）

> 在正式实现 `qa-gate.py` 之前，本节定义了文档质量的检查维度和标准。

### 8.1 三层质量门禁

改编自 9×1 校验模型（一致性×逻辑性×完整性 × 结构×内容×体系）：

| 层级 | 优先级 | 检查项 | 自动化程度 |
|:-----|:------:|:-------|:----------:|
| **结构层** | 🟢 P0 | 必需字段齐全（story_id/title/AC/out_of_scope）、Markdown 格式规范、文件命名规范 | 🤖 全自动 |
| **内容层** | 🟡 P1 | 技术描述准确性、术语一致性、信息覆盖完整性 | 🧑‍🤝‍🧑 AI辅助 |
| **体系层** | 🔵 P2 | 跨文档引用链完整、与 Epic/已有 Spec 不矛盾、价值评估 | 🧑 人工决策+自动 |

### 8.2 使用方式

当需要手动检查文档质量时，按以下顺序执行：

```bash
# P0: 结构检查 — 自动
python3 scripts/spec-gate.py verify "<story_id>"

# P1: 内容检查 — 加载 skill 后 AI 自查
# 加载 self-review skill 进行内容审查
skill_view(name="self-review")

# P2: 体系检查 — 文档对齐
python3 doc-alignment --verify
```

### 8.3 未来自动化的 qa-gate.py

设计中的 `scripts/qa-gate.py` 将实现一键三检：

```bash
python3 scripts/qa-gate.py check "<story_id>"
# 输出：P0 ✅ | P1 ⚠️ (2 issues) | P2 ✅ → 门禁: PASS/FAIL
```

详见 `references/sdd-known-gaps-and-roadmap.md`。