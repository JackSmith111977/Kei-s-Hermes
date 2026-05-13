---
# SDD Epic 模板
epic_id: ""
title: ""
status: draft  # draft | active | completed | archived
created: YYYY-MM-DD
updated: YYYY-MM-DD
target_version: ""
stories: []
test_data_contract:
  source: tests/fixtures/skills
  ci_independent: true
---

# {epic_id}: {title}

> **状态**: {status}
> **目标版本**: {target_version}
> **包含 Story**: {story_count}

---

## 概述

{简要描述 Epic 的目标和范围}

---

## Story 列表

| Story ID | 标题 | 状态 | 估时 |
|:---------|:-----|:----:|:----:|
| {STORY-1-1} | {标题} | {状态} | {h} |
| {STORY-1-2} | {标题} | {状态} | {h} |

---

## 测试数据契约

- **数据源**: {fixtures 路径}
- **CI 独立**: {是/否}
- **参考模式**: {测试文件}

---

## 完成条件

- [ ] 所有 Story 已完成
- [ ] 全量测试通过
- [ ] 文档已对齐
- [ ] 无 P0/P1 待办
