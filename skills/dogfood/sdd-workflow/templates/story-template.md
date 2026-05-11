---
# SDD Story Spec 模板
#
# 用法:
# 1. 复制到 docs/stories/STORY-XXX-NN.md
# 2. 填写所有字段
# 3. spec-state.py submit <story_id> 提交审阅

story: ""              # 唯一标识，如 SRA-004-01
title: ""              # 简短标题
status: draft          # draft | review | approved | in_progress | completed | archived
created: YYYY-MM-DD
updated: YYYY-MM-DD
epic: ""               # 所属 Epic ID
estimated_hours: 0

# 测试数据契约
test_data:
  source: tests/fixtures/skills
  ci_independent: true
  pattern_reference: ""

# 引用链
spec_references: []
dependencies: []
out_of_scope: []
---

# {story}: {title}

## 用户故事

> As a **{角色}**,
> I want **{功能}**,
> So that **{价值}**.

---

## 验收标准

### AC-1: {标题}
- [ ] 条件: {具体条件}
- [ ] 验证: {测试命令/手动步骤}
- [ ] 预期: {明确的输出}

### AC-2: {标题}
- [ ] 条件: {具体条件}
- [ ] 验证: {测试命令/手动步骤}
- [ ] 预期: {明确的输出}

---

## 技术要求

- {约束 1}
- {约束 2}

---

## 实施计划

### Task 1: {标题}
- 文件: {路径}
- 操作: {具体操作}
- 验证: {验证命令}

---

## 完成检查清单

- [ ] 所有 AC 通过
- [ ] pytest 全绿
- [ ] doc-alignment --verify 通过
- [ ] 代码 + 文档同次 commit
