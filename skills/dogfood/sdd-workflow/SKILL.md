---
name: sdd-workflow
description: "Spec-Driven Development 完整工作流 — 从 Spec 创建到代码实现的自动化生命周期管理。含状态机(spec-state.py)、门禁检查(spec-gate.py)、模板库。任何涉及 SDD/规范驱动/Story 开发的任务自动触发。"
version: 1.0.0
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

# 🧭 SDD Workflow v1.0 — Spec-Driven Development 生命周期管理

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
7. ✅ 验证（pytest + doc-alignment + commit-quality-check）
    ↓
8. 📝 Spec 状态更新（complete → archive）
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
    └── real-world-usage-sra-004-01.md ← 真实项目 SDD 完整走通记录
```

## 📚 参考深度阅读

- **`references/sdd-research.md`** — SDD 三大框架（BMAD/Superpowers/GSD）核心对比、成熟度模型、关键数据
- **`references/sdd-lifecycle.md`** — 六阶段完整生命周期指南（CREATE→ARCHIVE 每个阶段的详细操作）
- **`references/real-world-usage-sra-004-01.md`** — 在 SRA 项目中完整走通 SDD 全流程的实战记录

## 🚀 使用示例

### 场景 1：新功能开发

```bash
# 1. 创建 Story Spec
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py create "SRA-004-01" "实现批量推荐接口"
# 2. 用模板填充内容 → 复制 docs/STORY-TEMPLATE.md
# 3. 提交审阅
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py submit "SRA-004-01"
# 4. 主人批准后
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py approve "SRA-004-01"
# 5. 开始开发
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py start "SRA-004-01"
# 6. 实现 + 测试 + doc-alignment
# 7. 完成
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py complete "SRA-004-01"
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py archive "SRA-004-01"
```

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
