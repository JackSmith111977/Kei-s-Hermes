# SDD 生命周期参考 v1.0

> Spec-Driven Development 的生命周期完整指南

---

## 六阶段生命周期

```
CREATE ──→ REVIEW ──→ APPROVED ──→ IN PROGRESS ──→ COMPLETED ──→ ARCHIVED
  写 Spec   主人审阅    批准开发      实现中           已完成         归档
```

### 阶段 1: CREATE（创建 Spec）

**目标**: 将需求转化为结构化、可验证的 Spec 文档

**步骤**:
1. 确定 Story ID（格式: `{PROJECT}-{EPIC}-{NN}`）
2. 从模板复制（`docs/STORY-TEMPLATE.md`）
3. 填充所有字段（story_id, title, AC, test_data, spec_references, out_of_scope）
4. `spec-state.py create <story_id> "<title>"` 初始化状态

**产物**: `docs/stories/STORY-XXX-NN.md`
**验证**: `spec-gate.py verify <story_id>`

### 阶段 2: REVIEW（审阅）

**目标**: 主人审阅 Spec，确认需求正确

**步骤**:
1. `spec-state.py submit <story_id>` — 提交审阅
2. 向主人展示 Spec
3. 主人决定批准或驳回

**分支**:
- `spec-state.py approve <story_id>` → 批准，进入 Phase 3
- `spec-state.py reject <story_id> "<原因>"` → 驳回，打回 Phase 1

### 阶段 3: APPROVED → IMPLEMENT（开发）

**目标**: 按照批准的 Spec 实现代码

**步骤**:
1. `spec-state.py start <story_id>` — 开始开发
2. 加载 `writing-plans` — 将 AC 拆解为 2-5 分钟任务
3. 按 TDD 实现：每个 AC 对应一个测试
4. `pytest -q` — 确保全量测试通过

**门禁**: 每个 AC 完成后标记检查

### 阶段 4: COMPLETED（完成）

**目标**: 确认实现完整、测试通过、文档对齐

**步骤**:
1. 全量测试: `pytest tests/ -q`
2. 文档对齐: `doc-alignment`
3. 提交前检查: `commit-quality-check`
4. `spec-state.py complete <story_id>`

### 阶段 5: ARCHIVE（归档）

**目标**: 清理状态，将完成的工作归档

**步骤**:
1. `spec-state.py archive <story_id>`

---

## SDD 三不原则（核心约束）

| # | 原则 | 违反后果 | 机械门禁 |
|:-:|:-----|:---------|:---------|
| 1 | Specs 不可跳过 | 方向不对、不可审计 | `spec-gate.py enforce` |
| 2 | Specs 不可静默 | Spec-代码漂移 | `doc-alignment --verify` |
| 3 | Specs 不可漂移 | 基于过时信息决策 | Reality Check + `check-stale` |

---

## Spec 质量检查清单

| 检查项 | 通过标准 |
|:-------|:---------|
| story_id | 格式正确（{PROJECT}-{EPIC}-{NN}） |
| status | 与 spec-state.py 一致 |
| acceptance_criteria | 每个 AC 有条件和验证方式 |
| test_data.source | 引用已有 fixture 路径 |
| test_data.ci_independent | true |
| spec_references | 至少引用 1 个上游文档 |
| out_of_scope | 明确列出不做的功能 |
| 新鲜度 | 最后更新 < 7 天前 |
