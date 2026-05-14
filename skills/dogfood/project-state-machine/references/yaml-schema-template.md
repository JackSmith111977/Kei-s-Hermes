# Project State YAML — Schema 模板

将以下内容复制到 `docs/project-state.yaml` 并根据项目自定义。**禁止手动编辑状态字段**——必须通过 `scripts/project-state.py transition` 操作。

## 完整模板

```yaml
# 📊 {project-name} 统一状态机管理中枢
# 
# 这不是一个平凡的数据文件——它是整个项目的状态真相来源 (Source of Truth)。
# 每次状态变更必须通过 project-state.py 操作，不得手动编辑！
# 
# 版本: 1.0.0
# 创建: {YYYY-MM-DD}
# 维护: project-state.py (自动同步 + 门禁检查)

project:
  name: {project-name}
  version: {version}
  current_phase: {phase}
  overall_state: {draft|active|qa_gate|review|approved|released}
  created: {YYYY-MM-DD}
  updated: {YYYY-MM-DD}

# ─── 工作流状态机定义 ───
# 定义四种工作流的状态转换路径及其门禁条件
workflow:
  sdd:
    state_machine:
      - name: CLARIFY
      - name: RESEARCH
      - name: CREATE
      - name: QA_GATE
      - name: REVIEW
      - name: APPROVED
      - name: ARCHITECT
      - name: PLAN
      - name: IMPLEMENT
      - name: COMPLETED
      - name: ARCHIVED
    transitions:
      - from: "(none)"   to: draft     gate: create      checks: []
      - from: draft       to: review    gate: submit      checks: [file_exists, fields_complete]
      - from: review      to: approved  gate: approve     checks: [owner_approved]
      - from: review      to: draft     gate: reject      checks: [reason_recorded]
      - from: approved    to: architect gate: arch_start   checks: [adr_recorded]
      - from: architect   to: plan      gate: plan_start   checks: [plan_file_exists]
      - from: plan        to: implement gate: impl_start   checks: [tasks_defined]
      - from: implement   to: completed gate: complete     checks: [pytest_passes, ac_verified, doc_alignment]
      - from: completed   to: archived  gate: archive      checks: [drift_zero, html_generated]

  gates:
    pre_flight:
      description: 通用守门员
      script: ~/.hermes/scripts/pre_flight.py
      severity: blocking
    state_sync:
      description: 状态同步门禁
      script: python3 scripts/project-state.py verify
      severity: blocking

# ─── 实体状态 ───
entities:
  epics:
    EPIC-001:
      title: "{epic-title}"
      state: draft
      spec_count: 0
      story_count: 0
      completed_count: 0
      priority: P0
      qa_gate_date: null
      review_date: null
  specs:
    SPEC-1-1:
      state: draft
      epic: EPIC-001
      stories: []
  stories:
    STORY-1-1-1:
      state: draft
      epic: EPIC-001
      spec: SPEC-1-1

# ─── Sprint 进度 ───
sprints:
  sprint-1:
    title: "{sprint-title}"
    state: planning
    stories_planned: 0
    stories_completed: 0
    start: null
    end: null

# ─── 质量指标 ───
quality:
  sqs:
    avg: 0
    target: 70
    dimensions:
      s1_structure: 0
      s2_content: 0
      s3_freshness: 0
      s4_association: 0
      s5_discoverability: 0
  tests:
    count: 0
    passing: 0
    target: 0
  chi:
    value: 0
    target: 0.75

# ─── 状态变更日志 ───
history:
  - date: {YYYY-MM-DDThh:mm:ss}
    entity: system
    from: null
    to: created
    action: init
    reason: "初始化统一状态机管理中枢"
    gate: null
```

## YAML 字段约束

| 字段 | 类型 | 约束 |
|:-----|:-----|:------|
| `project.overall_state` | string | 必须为: draft, active, qa_gate, review, approved, released |
| `entities.epics.*.state` | string | 必须为: draft, create, qa_gate, review, approved |
| `entities.specs.*.state` | string | 必须为: draft, review, approved, architect, plan, implement, completed, archived |
| `entities.stories.*.state` | string | 必须为: draft, review, approved, architect, plan, implement, completed, archived |
| `sprints.*.state` | string | 必须为: planning, in_progress, released |
| `quality.*.target` | number | 目标值，用于衡量是否达标 |
| `history[].date` | datetime | ISO 8601 格式，自动填充 |

## 集成清单

- [ ] `docs/project-state.yaml` 已创建并填充初始实体
- [ ] `scripts/project-state.py` 已创建（从 project-state-machine skill 复制）
- [ ] `python3 scripts/project-state.py status` 正常输出
- [ ] `python3 scripts/project-state.py verify` 通过 (exit 0)
- [ ] CI 已添加 `python3 scripts/project-state.py verify` 步骤
- [ ] SDD Workflow 已更新：转态前 verify，转态后 sync
- [ ] Dev Workflow 已更新：提交前 sync + verify
- [ ] QA Workflow 已更新：L4 门禁包含 verify
