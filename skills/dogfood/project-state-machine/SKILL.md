---
name: project-state-machine
description: "统一状态机管理中枢 — YAML 真相来源 + Python 管理脚本 + 门禁集成 + 漂移检测。项目所有实体（Epics/Specs/Stories/Sprints/质量）的单一状态真相来源。每次状态变更必须通过脚本操作，禁止手动编辑 YAML。"
version: 1.0.0
author: boku (Emma)
tags:
  - state-machine
  - project-management
  - workflow
  - quality-gate
  - drift-detection
  - yaml
triggers:
  - 状态机
  - 项目状态
  - 统一状态
  - state machine
  - project state
  - 状态管理
  - 状态同步
  - 状态验证
  - 状态漂移
  - 实体状态
  - 所有 Epic 状态
  - 查看项目全貌
  - 一致性检查
  - 文档对齐
  - 状态变更
  - 状态转换
  - project-state.yaml
  - project-state.py
  - 状态机初始化
  - 项目状态同步
  - 项目状态验证
  - 发布门禁
  - L4 门禁
  - 版本发布
  - 状态审计
  - 状态日志
  - transition
  - 状态变迁
depends_on:
  - sdd-workflow
  - project-startup-workflow
  - generic-dev-workflow
  - generic-qa-workflow
  - generic-qa-workflow
design_pattern: StateMachine
skill_type: Workflow
---

# 📊 项目统一状态机管理中枢 (Project State Machine)

> **核心理念**: 项目状态的真相来源只有一个。所有实体（Epics、Specs、Stories、Sprints）的状态集中在一个 YAML 文件中管理，每次变更必须通过脚本门禁。

## 快速开始

```bash
# 初始化（新建项目）
cp ~/.hermes/skills/dogfood/project-state-machine/templates/project-state.yaml docs/
pip install pyyaml pygithub gitpython              # 脚本依赖（按需）
python3 scripts/project-state.py sync
python3 scripts/project-state.py verify

# 日常使用
python3 scripts/project-state.py status          # 全局状态
python3 scripts/project-state.py verify          # 一致性验证（CI 门禁）
python3 scripts/project-state.py gate EPIC-002 approved    # 门禁预检
python3 scripts/project-state.py transition EPIC-003 create "开始提取"  # 状态转换
python3 scripts/project-state.py history         # 变更日志

# 初始化后集成到四个工作流（详见 references/workflow-integration-guide.md）：
#   sdd-workflow     → 每次 spec-state 前 verify / 后 sync
#   generic-dev      → Step 7.4 同步 sync + verify
#   generic-qa       → L4 发布门禁 verify
#   project-startup  → Phase 4.5 初始化
```

## 为什么需要统一状态机？

| 问题 | 无状态机方案 | 有状态机方案 |
|:-----|:-----------|:------------|
| **状态分散** | 40+ 文档各写各的 `**状态**`，无人验证一致性 | 一个 YAML 文件 = 真相来源 |
| **手动编辑** | 手动改文档头部的状态字段，可能忘记 | `project-state.py transition` 自动修改 YAML + 记录历史 |
| **无门禁** | 任何人随时可以改状态，无检查 | 每次 transition 前自动验证前置条件 |
| **数据漂移** | 文档说的和实际情况不一致，无人发现 | `project-state.py verify` 一键检测漂移 |
| **无历史** | 不知道什么时候谁改了状态 | 每次 transition 记录到 `history`，可追溯 |

## 架构

```text
docs/project-state.yaml          ← YAML 真相来源（禁止手动编辑！）
scripts/project-state.py         ← 状态机管理器（唯一操作入口）
    ├── status                   ← 显示当前项目状态全景
    ├── scan                     ← 扫描 SDD 文档，检测漂移
    ├── verify                   ← 一致性验证（用于 CI 门禁）
    ├── gate <entity> <to>      ← 非破坏性门禁检查
    ├── transition <entity> <to> ← 状态转换 + 门禁
    ├── sync                     ← 从文档同步状态到 YAML
    ├── list [--by-state|--by-type]
    └── history                  ← 状态变更日志

集成点（每个工作流中）：
    CI (.github/workflows/ci.yml)  → 每次提交时 python3 scripts/project-state.py verify
    SDD Workflow                    → 每次 spec-state.py 前 verify，后 sync
    Dev Workflow (Step 7)           → 提交前 python3 scripts/project-state.py sync + verify
    QA Workflow (L4 Gate)           → 发布前 python3 scripts/project-state.py verify
    Project Startup (Phase 4.5)     → 初始化 python3 scripts/project-state.py init + sync + verify
```

## YAML 文件结构

```yaml
project:                     # 项目基本信息
  name: hermes-cap-pack
  version: 0.7.0
  current_phase: sprint-4
  overall_state: qa_gate

workflow:                    # 工作流状态机定义
  sdd:
    state_machine: [CLARIFY → RESEARCH → SPEC_CREATE → SPEC_REVIEW → STORY_CREATE → STORY_REVIEW → QA_GATE → REVIEW → APPROVED → ARCHITECT → PLAN → IMPLEMENT → COMPLETED → ARCHIVED]
    transitions:              # 每个转换的门禁条件
      - from: implement → to: completed, gate: complete, checks: [pytest, ac_verified, doc_alignment]
  development: ...
  qa: ...
  startup: ...
  gates:                     # 门禁脚本定义
    pre_flight: {script: ~/.hermes/scripts/pre_flight.py, severity: blocking}

entities:                    # 实体状态（唯一真相来源）
  epics:
    EPIC-001: {state: approved, story_count: 20, completed_count: 20, ...}
  specs:
    SPEC-1-1: {state: approved, epic: EPIC-001, stories: [STORY-1-1-1, ...]}
  stories:
    STORY-1-1-1: {state: draft, epic: EPIC-001, spec: SPEC-1-1}

sprints:                     # Sprint 进度
  sprint-1: {state: released, stories_planned: 5, stories_completed: 5}

quality:                     # 质量指标
  sqs: {avg: 67.9, target: 70, dimensions: {s1: 15.5, s4: 6.0}}
  tests: {count: 101, passing: 101}
  chi: {value: 0.6355, target: 0.75}

history:                     # 变更日志（自动记录）
  - {date: ..., entity: EPIC-002, from: create, to: qa_gate, reason: "...", gate: qa_gate}
```

## 核心工作流

### 日常使用

```bash
# 查看项目当前状态
python3 scripts/project-state.py status

# 检测文档状态漂移（扫描 SDD 文档，对比 YAML）
python3 scripts/project-state.py scan

# 执行状态转换（带门禁检查）
python3 scripts/project-state.py gate EPIC-002 approved        # 先检查
python3 scripts/project-state.py transition EPIC-002 approved "主人批准"  # 再执行

# 提交前同步状态 + 验证
python3 scripts/project-state.py sync
python3 scripts/project-state.py verify   # exit 0 = 一致, exit 1 = 有漂移

# 查看历史
python3 scripts/project-state.py history
```

### CI 集成

```yaml
# .github/workflows/ci.yml — 在 consistency job 中添加
- name: 📊 Verify project state consistency
  run: python3 scripts/project-state.py verify
```

### 新项目初始化

当项目已有 SDD 文档结构后：
```bash
# 1. 创建 project-state.yaml
# 手动编写（参考本 skill 的 YAML 结构）

# 2. 创建 project-state.py 管理脚本
# 参考本 skill 的 scripts/project-state.py 模板

# 3. 填充实体状态
python3 scripts/project-state.py sync

# 4. 验证
python3 scripts/project-state.py verify
```

## 状态转换门禁规则

| 当前状态 | 目标状态 | 门禁条件 | 示例命令 |
|:---------|:---------|:---------|:---------|
| draft | review | 文档存在 + 必需字段完整 | `transition SPEC-1-1 review` |
| review | approved | 主人明确批准 | `transition SPEC-1-1 approved` |
| review | draft | 记录拒绝原因 | `transition SPEC-1-1 draft "缺少测试方案"` |
| research | spec_create | 调研完成 | (脚本内触发) |
| spec_create | spec_review | Spec 文件存在 + 必需字段完整 | `transition SPEC-3-1 spec_review` |
| **spec_review** | **story_create** | 🟢 主人批准 | 🔔 通过飞书送审后主人确认 |
| **spec_review** | **research** | 🔴 主人驳回 | 🔔 记录驳回原因后返回调研 |
| **story_review** | **qa_gate** | 🟢 主人批准 | 🔔 通过飞书送审后主人确认 |
| **story_review** | **spec_create** | 🔴 主人驳回 | 🔔 记录驳回原因后返回 Spec |
| approved → completed | (多个中间状态) | 每步有对应 AC | 逐级 transition |
| qa_gate | approved | QA 门禁通过 | `transition EPIC-002 approved` |
| implement | completed | pytest + AC + doc-alignment | `transition STORY-2-1-1 completed` |
| completed | archived | 漂移=0 + HTML 已生成 | `transition STORY-2-1-1 archived` |

## 漂移检测机制

`project-state.py verify` 检查三种不一致：

| 类型 | 严重程度 | 含义 | 处理 |
|:-----|:--------:|:-----|:-----|
| **状态不一致** | 🔴 错误 | YAML 和文档的状态字段不同 | `project-state.py sync` 同步 |
| **文档缺失** | 🟡 警告 | YAML 有记录但找不到对应文件 | 创建文件或从 YAML 移除 |
| **未注册** | 🔴 错误 | 文档存在但 YAML 中未登记 | `project-state.py sync` 注册 |

## 脚本模式详解

### project-state.py 命令参考

```text
status              — 显示当前项目状态全景 (Epics/Specs/Sprints/质量)
scan                — 扫描所有 SDD 文档的实际状态，对比 YAML 输出漂移报告
verify              — 一致性验证。exit 0 = 全部一致, exit 1 = 有错误
gate <entity> <to>  — 非破坏性门禁检查：当前状态 → 目标状态是否允许
transition <entity> <to> [reason]  — 执行状态转换（自动过 gate + 记录 history）
sync                — 从文档实际状态同步到 YAML（修复漂移）
list [--by-state|--by-type]  — 列出所有实体，可分组
history             — 查看状态变更日志
init                — 初始化（交互式创建 project-state.yaml）
```

### Verify 输出示例

```text
✅ 一致性验证通过 — 3 Epics, 9 Specs, 28 Stories 全一致
```

```text
🔴 EPIC EPIC-002: YAML=qa_gate, DOC=approved 状态不一致
🟡 STORY STORY-1-1-3: YAML 中有记录但未找到文档文件

✅ 关键状态一致性通过，1 个警告 (非 blocking)
```

## 常见陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| **手动编辑 project-state.yaml** | YAML 语法错误、忘记记录 history | 永远只用 `project-state.py transition` |
| **transition 前忘记 gate 检查** | 状态跳转不符合工作流 | 先 `gate` 再 `transition` |
| **修改文档后忘记 sync** | YAML 和文档漂移 | 在 commit 前运行 `sync + verify` |
| **漂移积累太多再修复** | 不知道哪个版本是正确的 | 每次状态变更后立即 sync |
| **Story 无独立文件** | scan/verify 显示警告 | 创建 Story 时同步创建 md 文件 + YAML 条目 |
| **文档状态字段格式不统一** | scan 扫不到某些文档的状态 | `get_doc_states()` 兼容 `**状态**:` 和 `**status**:` 两种格式 |
| **YAML 缩进被 patch 破坏** | YAMLError，lint 失败 | 修改 YAML 后必须 `python3 -c "import yaml; yaml.safe_load(open(...))"` 验证 |
| **大范围提取只规划部分** | 用户纠正「还有更多没规划」 | 提取/迁移前先做全盘规划（列出全部实体 → 按优先级分组 → 再逐个 Phase 执行） |

## 与现有状态机的关系

该项目状态机是**跨域统一管理器**，不是替代品：

```text
┌──────────────────────────────────────────────────────────────┐
│  project-state.py (跨域统一管理器)                            │
│  管理: 所有 Epics / Specs / Stories / Sprints / 质量         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ sdd-workflow/spec-state.py ─┐  ┌─ learning-state.py ──┐ │
│  │ SDD 生命周期 (单个 Spec)       │  │ 学习流程 (单个任务)    │ │
│  │ draft→review→approved→...     │  │ step0→step1→...      │ │
│  └──────────────────────────────┘  └───────────────────────┘ │
│                                                              │
│  协作方式:                                                   │
│  spec-state.py 变更时 → 手动触发 project-state.py sync       │
│  learning-state.py 变更时 → 独立管理（不影响项目状态）        │
└──────────────────────────────────────────────────────────────┘
```

## 本 skill 的边界

| ✅ 包含 | ❌ 不包含 |
|:--------|:----------|
| 跨项目实体的统一状态管理 | 单个 Spec 的生命周期细节（sdd-workflow 负责） |
| 状态一致性验证 + 漂移检测 | 学习任务的进度管理（learning-workflow 负责） |
| CI 门禁集成 | 代码质量评分（SQS 负责） |
| 工作流集成指南 | Sprint 规划细节（sprint-planning 负责） |
| 状态变更历史追溯 | 用户故事/验收标准管理（sdd-workflow 负责） |

## 技能文件结构

```text
~/.hermes/skills/dogfood/project-state-machine/
├── SKILL.md                         ← 本文件（完整使用指南）
├── scripts/
│   └── project-state.py            ← 管理脚本（复制到项目中即可使用）
├── templates/
│   └── project-state.yaml          ← 新项目初始化模板（即开即用）
└── references/
    ├── yaml-schema-template.md     ← YAML 字段约束与完整模板参考
    ├── workflow-integration-guide.md ← 四种工作流集成详细步骤
    └── script-location.md          ← 脚本位置与在新项目中设置指南（已吸收自 unified-state-machine）
```

## 铁律

| # | 铁律 | 违背后果 |
|:-:|:-----|:---------|
| 1 | **禁止手动编辑 project-state.yaml** | 状态混乱、无法追溯 |
| 2 | **每次状态变更后必须 sync + verify** | YAML 与文档漂移 |
| 3 | **transition 前必须 gate 检查** | 状态跳转不符合工作流 |
| 4 | **修改文档 HEADER 状态字段必须同步 YAML** | 两个真相来源冲突 |
| 5 | **CI 必须包含 verify 步骤** | 漂移不被发现 |
