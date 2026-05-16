---
name: sdd-workflow
description: "Spec-Driven Development 完整工作流 — 从 Spec 创建到代码实现的自动化生命周期管理。含状态机(spec-state.py)、门禁检查(spec-gate.py)、模板库、技术版本规约。触发「继续」「下一阶段」「phase」「推进」等延续关键词时自动加载，衔接 DEV→QA 工作流链。任何涉及 SDD/规范驱动/Story 开发/阶段推进的任务自动触发。"
version: 3.10.0
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
  - epic 开发
  - epic 计划
  - 开发计划
  - 计划创建
  - 质量升级
  - 增量循环
  - spec 检查
  - story 模板
  - epic 模板
  - 命名规范
  - 命名门禁
  - validate naming
  - 文档名称检查
  - 重命名文档
  - 批量改名
  - 文档迁移
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
  - 用户故事
  - story分解
  - 创建story
  - spec分解
  - 分解方案
  - story拆分
  - 实施路线
  - project report
  - panorama
  - 项目报告
  - html报告
  - 生成报告
  - 继续
  - phase
  - 下一阶段
  - 下一步
  - 继续做
  - continue
  - next phase
  - next step
  - carry on
  - resume
  - 恢复
  - 往下走
  - 启动
  - 阶段推进
  - 推进
  - 联合工作流
  - 全链走通
  - 跑完整链
  - 联合工作流
  - combined workflow
author: Emma (小玛)
license: MIT
depends_on:
  - development-workflow-index
  - writing-plans
  - test-driven-development
  - doc-alignment
  - commit-quality-check
  - sdd-research
  - unified-state-machine
  - phase-gate
  - chain-state
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

# 🧭 SDD Workflow v3.0 — Spec-Driven Development 全生命周期管理

> **核心理念**: 没有批准的 Spec 就不写代码。没有架构设计就不开始实现。
> **设计模式**: 状态机 + 门禁 + 模板 + 架构设计 四位一体

---

## 〇、工作流总览

```
CLARIFY ──→ RESEARCH ──→ SPEC_CREATE ──→ SPEC_REVIEW ──→ STORY_CREATE ──→ STORY_REVIEW ──→ QA_GATE ──→ REVIEW ──→ APPROVED
 需求澄清    sdd-research      写 Spec       🔔 主人审阅    写 Story       🔔 主人审阅     质量检查      最终审阅     批准
  +Reality                                                                                                         ↓
  +Check                                                                                                   ARCHITECT ──→ PLAN ──→ IMPLEMENT
                                                                                                           架构设计      实现计划     技术实现
                                                                                                               +doc-alignment      +
                                                                                                               Phase 0            Phase 1
                                                                                                                                  ↓
                                                                                                                            COMPLETED ──→ ARCHIVED
                                                                                                                             完成      +doc-alignment
                                                                                                                             +Phase 2  Phase 3

**十一个状态，十三个转换门禁，每个门禁必须通过才能进入下一状态。**

### 🔔 审阅门禁详解

| 审阅点 | 触发时机 | 方式 | 门禁条件 |
|:-------|:---------|:-----|:---------|
| **SPEC_REVIEW** | Spec 文档写完后 | 通过飞书消息发送 Spec 摘要给主人 | 主人明确回复"批准"或使用 `spec-state.py approve` |
| **STORY_REVIEW** | Story 文档写完后 | 通过飞书消息发送 Story 摘要给主人 | 主人明确回复"批准"或使用 `spec-state.py approve` |

**铁律**:
- Spec 未批 → 禁止进入 Story 阶段
- Story 未批 → 禁止进入实施阶段
- 驳回时必须记录原因 → `spec-state.py reject <id> "原因"`

---

## 一、Spec 生命周期状态机

> **⚠️ 历史说明**: v3.0 之前的版本使用 `start` 命令。v3.0 起替换为三段式：`architect` → `plan` → `implement`。旧 `sdd_state.json` 自动兼容。

使用 `scripts/spec-state.py` 管理（**2026-05-13 正式上线**，此前该脚本仅存在于文档描述中）：

```bash
# 创建新 Spec（初始化状态机，自动进入 draft）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py create "STORY-1-1" "改进匹配算法"

# 提交审阅（draft → review）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py submit "STORY-1-1"

# 批准（review → approved）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py approve "STORY-1-1"

# 三段式实现（替代旧版 start）：
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py architect "STORY-1-1"  # approved → architect
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py plan "STORY-1-1"      # architect → plan
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py implement "STORY-1-1" # plan → implement

# 完成（implement → completed）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py complete "STORY-1-1"

# 归档（completed → archived）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py archive "STORY-1-1"

# 驳回（review → draft）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py reject "STORY-1-1" "缺少测试用例"

# 重置到 draft（任意状态均可）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py reset "STORY-1-1"

# 检查状态
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py status "STORY-1-1"

# 列出现有所有 Spec（按状态分组）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py list
```

> **⚠️ project-state.yaml 同步**: 每次执行 spec-state.py 的**变更命令**（create/submit/approve/architect/plan/implement/complete/archive/reject/reset）前，**必须先运行** `python3 /home/ubuntu/projects/hermes-cap-pack/scripts/project-state.py verify` 验证项目状态完整性；变更后**必须运行** `python3 /home/ubuntu/projects/hermes-cap-pack/scripts/project-state.py sync` 将最新状态同步至 project-state.yaml。

### 状态转换规则

| 当前状态 | 允许的操作 | 下一状态 | 门禁条件 |
|:---------|:-----------|:---------|:---------|
| (none) | `create` | draft | 提供 story_id + title |
| draft | `submit` | review | Spec 文件存在 + 必需字段完整 |
| review | `approve` | approved | 主人确认批准 |
| review | `reject` | draft | 记录拒绝原因，退回修改 |
| research | `spec_write` | spec_create | 调研完成 |
| spec_create | `spec_submit` | spec_review | Spec 文件存在 + 必需字段完整 |
| **spec_review** | `spec_approve` | **story_create** | 主人确认批准 Spec |
| **spec_review** | `spec_reject` | **research** | 记录拒绝原因，退回调研 |
| **story_create** | `story_submit` | **story_review** | Story 文件存在 + 必需字段完整 |
| **story_review** | `story_approve` | **qa_gate** | 主人确认批准 Story |
| **story_review** | `story_reject` | **spec_create** | 记录拒绝原因，退回 Spec |
| approved | `architect` | architect | 无（主人已批准，开始架构设计）|
| architect | `plan` | plan | 架构文档完整 + ADR 记录完成 |
| plan | `implement` | implement | 实施计划完整 + 任务分解可执行 |
| implement | `complete` | completed | pytest 通过 + AC 验证通过 + doc-alignment Phase 1-2 完成 |
| completed | `archive` | archived | doc-alignment Phase 3 验证通过 (--verify 漂移=0) + HTML 已生成 |
### 8.3 未来自动化的 qa-gate.py

设计中的 `scripts/qa-gate.py` 将实现一键三检：

详见 `references/sdd-known-gaps-and-roadmap.md`。

---

## 九、Spec 分解指南 — 从宽泛 Spec 到可执行 Story

> **适用场景**: 当一个 SPEC 有 3 个以上的验收标准（AC），或涉及多个组件/文件时，不应直接写一个 Story 实现全部，而应先分解为多个 Story。
> **本指南填补了从「Spec Approved」到「ARCHITECT/PLAN」之间的规划空白**。

### 9.1 分解流程

```text
宽泛的 SPEC（如 SPEC-004，6 个 AC）
    ↓
[Step 1] AC 提取 → 列出所有 AC，每个 AC 至少对应一个 Story
    ↓
[Step 2] AC 聚类 → 按依赖关系分组（基础设施优先，独立 AC 可并行）
    ↓
[Step 3] 架构蓝图 → 先画目标文件结构，定义的组件/模块映射到 Story
    ↓
[Step 4] Story 生成 → 每个 AC/AC 组 → 一个 Story（含用户故事 + AC + 技术方案 + 不做的范围）
    ↓
[Step 5] Phase 排序 → 确定执行顺序，每个 Phase 定义入口门禁和出口里程碑
    ↓
可执行的 Story 清单 + Phase 路线图 + 架构蓝图
```

### 9.2 分解原则

| 原则 | 说明 | 反例 |
|:-----|:------|:------|
| **AC → Story** | 每个 AC 至少对应一个 Story。复杂 AC 可拆为多个 Story | 6 个 AC 写 1 个 Story → Story 太胖无法在 1 天内完成 |
| **基础设施优先** | 先建 Core/框架层，再建具体的适配器/实现层 | 先写 Hermes 适配器才想起没有 AgentAdapter Protocol |
| **Phase 有门禁** | 每个 Phase 定义入口条件 + 出口里程碑 | Phase 结束没有验证 → 问题堆积到集成阶段 |
| **架构蓝图先行** | 在分解 Story 前，先画出目标文件结构图 | Story 实现一半发现目录结构不合理 → 返工 |
| **每个 Story 可独立验证** | 每个 Story 的 AC 是可测试的、不依赖下游 Story | Story A「实现框架」，AC 为「代码可运行」→ 太模糊 |

### 9.3 分解模板

当需要分解宽泛 Spec 时，按此模板产出：

```markdown
## SPEC-[XXX] 分解方案

### 架构蓝图

target/dir/
├── core/          ← Phase 0: 基础设施
├── module-a/      ← Phase 1: 主要功能
└── module-b/      ← Phase 2: 扩展

### Phase 0: [名称] — 基础设施
| Story | AC 来源 | 用户故事 | 技术方案 | 出口门禁 |
|:------|:--------|:---------|:---------|:---------|
| STORY-1-1 | AC-1 | As a... I want... | 实现核心框架 | 单元测试全绿 |

### Phase 1: [名称] — 主要功能
...
```

### 9.4 与状态机的集成

分解完成后，在 SDD 状态机中按以下方式管理：

```text
[SPEC 已批准] → 用本指南分解为 N 个 Story
    ↓
对每个 Story：
    python3 spec-state.py create "STORY-1-1" "标题"
    python3 spec-state.py submit "STORY-1-1"
    [主人逐个审批]
    python3 spec-state.py approve "STORY-1-1"
    ↓
按 Phase 分组执行：
    python3 spec-state.py architect "STORY-1-1"
    python3 spec-state.py plan "STORY-1-1"
    python3 spec-state.py implement "STORY-1-1"
    ↓
Phase 门禁验证通过后 → 进入下一 Phase
```

### 9.5 实战案例

cap-pack 项目中 SPEC-004（适配器方案）的完整分解过程见：
`references/spec-decomposition-cap-pack-example.md`

### 9.6 Phase 级别 SPEC 模式（多 Phase EPIC 推荐）🔥

> **实战验证**：EPIC-005 Phase 0 使用此模式——Phase 0 和 Phase 1 各自有独立的 SPEC，分别走完整的 SDD 生命周期。

当一个 EPIC 有多个 Phase 时，**为每个 Phase 创建独立的 SPEC** 比「一个 EPIC 一个 SPEC」更可控：

```text
EPIC-005 ── 包含 4 个 Phase，每个 Phase 一个 SPEC

  SPEC-5-0 (Phase 0: 标准定义)      ← 自己走完 CLARIFY→...→COMPLETED
  SPEC-5-1 (Phase 1: 核心引擎)      ← 依赖 Phase 0 完成 → 单独审批
  SPEC-5-2 (Phase 2: Hermes 集成)   ← 依赖 Phase 1 完成
  SPEC-5-3 (Phase 3: 多 Agent)      ← 依赖 Phase 2 完成
```

#### 为什么用 Phase 级别 SPEC？

| 对比 | 一个 SPEC 包所有 Phase | 每个 Phase 独立 SPEC |
|:-----|:----------------------|:--------------------|
| 审阅粒度 | 一次性审阅全部 → 认知负担大 | 逐个 Phase 审阅 → 方向可及时纠正 |
| 变更影响 | 改一个 Story 影响整个 SPEC | 只影响对应 Phase 的 SPEC |
| 门禁强度 | 无 Phase 级阻断 | Phase N 完成前无法进入 Phase N+1 |
| 前置依赖表达 | 不清晰 | `requires: [Phase-0]` 显式声明 |
| 并行度 | 所有 Story 混在一起 | Phase 0 审批期间可准备 Phase 1 调研 |

#### 命名约定

```text
SPEC-{epic}-0  → Phase 0（标准/基建/前置条件）
SPEC-{epic}-1  → Phase 1（核心功能）
SPEC-{epic}-2  → Phase 2（扩展功能）
SPEC-{epic}-3  → Phase 3（生态/集成）
```

Phase 0 编号使用 `0` 而非 `1`，语义上标示其为「前置条件」，与 phase-gate 的 `requires: [Phase-0]` 对齐。

#### 状态机管理

每个 Phase 的 SPEC 独立走完整 SDD 生命周期：

```bash
# Phase 0 SPEC
spec-state.py create "SPEC-5-0" "标准定义 — Phase 0"
spec-state.py submit "SPEC-5-0" ...
spec-state.py approve "SPEC-5-0"
# ... 创建并完成 3 个 Story ...
spec-state.py complete "SPEC-5-0"  # ← Phase 0 门禁解除

# Phase 1 SPEC（此时才启动）
spec-state.py create "SPEC-5-1" "核心引擎 — Phase 1"
# ...
```

#### 实战案例

EPIC-005 的完整 Phase 0 → SPEC-5-0 分离模式见 hermes-cap-pack 的 `docs/SPEC-5-0.md` 和 `docs/EPIC-005-skill-governance-engine.md`。

---

## ⚠️ 已知陷阱与解决方案

### Phase Gate — Phase 转换门禁（v3.8.0 新增）🔥 新增：Phase 配置注册

**前提条件**: 新创建的 EPIC 没有 Phase 配置，必须先在 `project-state.yaml` 中注册 Phase 结构，否则 `phase-gate.py check` 会报错 `Epic X 没有 Phase 配置`。

```bash
# 注册 Phase 配置（在 project-state.yaml 的 phases: 字段）
# 每个 Phase 需要定义：name、title、acceptance_criteria、requires、stories
# 参见 hermes-cap-pack 的 EPIC-005 实战——创建 NEW EPIC 后,
# phase-gate.py 会一直失败，直到 Phase 配置写入 project-state.yaml
```

**Phase schema 配置示例**（位于 `docs/project-state.yaml` 的 `phases:` 字段）：

EPIC 级别的 Phase 化工作流（如 EPIC-004 的 Phase 0/1/2/3/4）需要显示执行 Phase 门禁，禁止跳过未完成的 Phase。

**问题**：EPIC 中定义了 Phase 内容 → 容易误以为「EPIC 已批准 = 所有 Phase 可直接实施」

**铁律**：
- EPIC 批准 ≠ Phase 批准。每个 Phase 必须在进入前经过 CLARIFY
- Phase N 的 CLARIFY 必须在 Phase N-1 全部完成后才能发起
- 不允许在同一个 CLARIFY 中同时确认多个 Phase

**使用方式**（cap-pack 项目 `scripts/phase-gate.py`）：
```bash
# 列表所有 Phase 状态
python3 scripts/phase-gate.py list EPIC-004

# 检查是否可以进入目标 Phase
python3 scripts/phase-gate.py check EPIC-004 Phase-2

# 开始 Phase（自动检查前置）
python3 scripts/phase-gate.py start EPIC-004 Phase-2

# 标记 Phase 完成
python3 scripts/phase-gate.py complete EPIC-004 Phase-2
```

**Phase schema 配置**（位于 `docs/project-state.yaml` 的 `phases:` 字段）：
```yaml
phases:
  EPIC-XXX:
    title: 描述
    phases:
      - name: Phase-N
        title: Phase 标题
        acceptance_criteria:
          - criteria: AC 描述
            done: false
        requires:
          - Phase-(N-1) 已完成
        stories:
          - STORY-X-Y-Z
    completed_phases:
      - Phase-0
      - Phase-1
```

**集成到 SDD 工作流**：进入 Phase N 前，先运行 `phase-gate.py check` 确认前置条件满足。

### 🔄 Phase 完成文档对齐链（v3.9.0 新增）

Phase 完成后的文档更新应遵循固定的**从底向上链**，确保一致性。通过 EPIC-004 5 个 Phase 验证的模式：

```text
Phase 完成 → 文档对齐链（从底向上）
                │
                ▼
  ╔══════════════════════════════════╗
  ║  Layer 1: Story 文件 (最底层)    ║  ← 先更新
  ║  └─ status: draft → completed   ║
  ║  └─ 所有 AC: [ ] → [x]          ║
  ╚════════════════╤═════════════════╝
                   │
                   ▼
  ╔══════════════════════════════════╗
  ║  Layer 2: SPEC 文件              ║
  ║  └─ status: draft → completed   ║
  ║  └─ 完成检查清单: [ ] → [x]     ║
  ╚════════════════╤═════════════════╝
                   │
                   ▼
  ╔══════════════════════════════════╗
  ║  Layer 3: EPIC 文件              ║
  ║  └─ completed_phases 追加条目   ║
  ║  └─ Phase 定义表标记 ✅         ║
  ║  └─ 优先级表格更新              ║
  ║  └─ 关联文档状态同步            ║
  ╚════════════════╤═════════════════╝
                   │
                   ▼
  ╔══════════════════════════════════╗
  ║  Layer 4: project-report.json    ║  ← 最顶层
  ║  └─ tests.passing 更新          ║
  ║  └─ epics[].stories 追加        ║
  ║  └─ sprint_history 追加         ║
  ╚══════════════════════════════════╝
```

**为什么从底向上？**
- 底层的 Story 文件定义了「做了什么」
- 中层的 SPEC 汇总了「哪些验收通过了」
- 顶层的 EPIC 和 project-report 是「项目整体状态」
- 先更新底层 → 高层引用底层数据 → 不会产生孤立的更新

**实战验证**：EPIC-004 5 个 Phase（0→4），每次按此链更新，最终 19 个 Story 文件和 6 个 SPEC 全部一致，零漂移。详见 `references/phase-completion-checklist.md`。

**完成检查清单**（每个 Phase 完成时必须执行）：

```bash
# Phase N 完成时 — 从底向上对齐
□ 1. 更新 Story 文件：status=completed, AC=[x]
□ 2. 更新 SPEC 文件：status=completed, 完成条件=[x]
□ 3. 更新 EPIC 文件：completed_phases 追加 Phase N
□ 4. 更新 project-report.json：tests+epics+sprint
□ 5. 验证：grep "^status:" docs/stories/STORY-*.md | grep -v completed → 零
```

---

### AC 审计盲点陷阱：只检 [x] 不验代码存在性

- **问题**：`ac-audit.py` 只检查文档中是否存在 `[x]` 标记，**不验证对应的代码是否真实存在**。例如 EPIC-001 的 AC「Hermes pre_tool_call hook 集成」标记为 ✅，但 Hermes 侧代码从未实现。EPIC-003 中 6 个 AC 同样标记 ✅ 但从未实施。
- **后果**：文档声称「全部完成」，实际集成从未工作。后续开发者基于虚假信息做决策。
- **根因**：AC 审计工具只做文本模式匹配（`grep '\[x\]'`），无法理解 AC 的语义对应关系。AC 的完成状态是一种「文档声明」，不是「代码验证」。
- **解决**：
  1. AC 标记 ✅ 后，必须附加验证方式说明（如「验证: `grep _query_sra_context run_agent.py`」）
  2. 跨项目 AC（如「Hermes 侧集成」）必须端到端验证，不能只检单侧代码
  3. 在 AC 旁添加 `<!-- 验证: <具体命令> -->` 注释，方便后续审计
     - **已验证的配套脚本**: `scripts/ac-audit-code-check.py`（自动解析 `<!-- 验证: -->` 注释并执行验证命令）
  4. 对于「已集成」「已部署」类 AC，必须通过 `curl` / `grep` / `pytest` 实际验证
- **检查清单**：在标记任何 AC 为 ✅ 前，问自己：
  - [ ] 这个 AC 描述的是代码行为还是文档行为？
  - [ ] 如果是代码行为，对应的代码文件是否存在？
  - [ ] 如果是跨系统集成（SRA↔Hermes），两侧代码是否都已实现？
  - [ ] 有没有办法用命令验证？（`grep` / `curl` / `pytest -k`）
- **实战案例**：EPIC-004 分析中发现 EPIC-001/003 共 7 个 AC 标记 ✅ 但实际未实现。详见 `docs/EPIC-004.md` 的问题全景章节。

### 定义→对齐→实施顺序陷阱：代码先于文档

- **问题**：在 SDD 流程中，已经创建了 SPEC 和 Story 并获批准后，boku 有时会**直接开始写代码，跳过「文档对齐」步骤**。例如在 EPIC-004 中，将 Plugin 代码写到 `~/.hermes/hermes-agent/plugins/` 后，被主人纠正「应该在 SRA 项目中管理」。
- **后果**：
  - 代码在错误的位置 → 需要移动文件 → 额外工作量
  - 文档未同步 → 文档与代码脱节 → 下次决策基于过时信息
  - 测试文件路径错误 → 测试失败
- **根因**：急于交付代码，低估了「先对齐文档再实施」的价值。认为「代码写对了就行，文档后面再改」— 但文档对齐决定了代码放哪里、测试怎么跑、别人怎么用。
- **解决**：在实施计划（PLAN）阶段就明确：
  1. **源码管理位置** — 代码在哪个项目的哪个目录下？（不是部署位置）
  2. **部署位置** — 代码最终在哪里运行？
  3. **测试位置** — 测试文件放在哪里？
  4. **文档同步清单** — 哪些文档需要更新？
  5. 这三个位置在 PLAN 阶段就写入 Task，**先于编码 Task 执行**
- **铁律**：在 Task 1「创建文件」之前，先确认「文件在哪里创建」并更新对应文档的结构图。源码位置不确认 → 不写第一行代码。
- **实战案例**：EPIC-004 Phase 0，plugin 代码先写到 `~/.hermes/hermes-agent/plugins/sra-guard/`，被主人纠正后迁移到 `~/projects/sra/plugins/sra-guard/`。如果先在 SPEC 的架构设计部分确认源码位置，可避免返工。

### 标准优先顺序陷阱（Standard-First Ordering）

- **问题**：当构建治理/合规/检测类工具时（如 EPIC-005 的合规检查器），boku 先写了检测器设计，却没有先定义被检测的**标准本身**。结果主人问「到底检测什么？」时，合规描述过于模糊。
- **后果**：
  - 检测维度模糊 → 主人质疑方向 → 需要回头重新定义标准
  - 检测器可能针对错误的标准实现 → 返工
  - SPEC 中的合规描述被评价为「太笼统」
- **根因**：默认的「实现驱动」思维——认为先有工具才有标准。但对于合规/治理类任务，**标准必须先于检测器存在**。标准是检测器的规范来源，而不是从检测器推导标准。
- **解决**：
  1. 合规/治理类 EPIC 的 Phase 0 必须是**标准定义阶段**
  2. 标准必须文档化（`STANDARD.md`）并包含多层维度 + 量化阈值
  3. 标准经主人批准后，再构建检测器
  4. SPEC 中合规相关描述必须写明：检查哪几层、每层什么标准、阈值多少
- **检查清单**：创建合规相关 SPEC 前，问自己：
  - [ ] 被检测的标准是否已明确定义？
  - [ ] 标准是否有分层结构（强制/推荐/最佳实践）？
  - [ ] 每个维度的阈值是否量化？
  - [ ] Owner 是否批准了标准？
- **实战案例**：EPIC-005 Phase 0 被主人纠正为「先制定统一标准」，标准框架（Level 0-3）定义完成后才进入检测器实现。

### 批量创建陷阱：跳过审阅门禁批量写文档

- **问题**：当一个 Epic 有多个 Phase、多个 SPEC 和多个 Story 时（如 EPIC-004 有 4 个 SPEC + 12 个 Story），一次批量创建所有文档，跳过 SPEC_REVIEW 和 STORY_REVIEW 门禁
- **后果**：
  - 主人没有机会在早期纠正方向 → 可能白做
  - 批量创建的文档如果方向错了，回退成本高
  - 违反了「Spec 未批 → 禁止进入 Story 阶段」的铁律
  - 增加了主人认知负担（一次看太多文档）
- **根因**：想快速交付结果，低估了「方向确认」的价值
- **解决**：严格按照状态机逐阶段推进：
  1. EPIC CLARIFY → 主人确认 → EPIC REVIEW → 主人批准
  2. SPEC-1 CLARIFY → RESEARCH → SPEC_CREATE → SPEC_REVIEW → 主人批准
  3. 只有 SPEC 批准后才创建该 SPEC 的 Stories → STORY_REVIEW → 主人批准
  4. 只有当前 SPEC 全部批准后才进入下一个 SPEC 的 CLARIFY
  5. **禁止一次性批量创建超过 1 个 SPEC 或超过 3 个 Story 而不经过审阅门禁**
- **检查清单**：在创建任何文档前，问自己：
  - [ ] 当前 EPIC 是否已批准？
  - [ ] 当前 SPEC 的上一个 SPEC 是否已批准？
  - [ ] 这些 Story 所属的 SPEC 是否已批准？
  - [ ] 如果以上任一为「否」→ 先走审阅门禁，再创建下一步文档

#### 恢复路径：如果已经批量创建了未审阅的文档

当违反上述规则、一次性创建了大量未审阅的 SPEC/Story 文档时：

1. **立即停止创建新文档**，不要再继续推进
2. **`git status --short` 全貌扫描**：先看 `M`（修改了现有文件） vs `??`（新建未跟踪文件），区分哪些是这次批量操作产生的
3. **跑 `project-state.py verify`** 确认当前不一致的全貌
4. **回退**：
   - 修改过的现有文件 → `git checkout -- <file>`（从上次 commit 恢复）
   - 新建的未审阅文件 → `rm -f <file>`（直接删除）
   - 注意：EPIC 文档可能已存在（`M` 状态），只需恢复旧版本；SPEC/Story 文件通常是新建（`??` 状态），直接删除即可
   - 确认所有 EPIC-004/SPEC-4/STORY-4 类文件已清除：`git status --short` 不应再显示相关的 M 或 ??
5. **从头走 CLARIFY**：向主人展示全貌方案，等待方向确认
6. **严格逐阶段推进**：EPIC REVIEW → 批准 → 仅创建当前 SPEC → SPEC REVIEW → 批准 → 仅创建该 SPEC 的 Stories → STORY REVIEW → 批准 → 下一 SPEC
7. **一次只送审一个 SPEC**，不要同时送审多个 SPEC 或超过 3 个 Story

**恢复路径的核心理念**：回退的成本远低于在错误方向上继续推进的成本。不要怕回退——回退后重新走 SDD 流程是主人期望的纠正方式，不是失败。

**实战验证**（2026-05-14 cap-pack EPIC-004）：本恢复路径已在实际项目中被主人要求执行并验证有效。回退步骤完整走通，包括 `git checkout --` 恢复 EPIC/YAML/README 修改 + `rm` 删除 16 个未审阅的 SPEC/Story 文件 → 从 CLARIFY 重新开始 → 主人批准后逐阶段推进 → Phase 0 和 Phase 1 均完整通过 SDD 流程。

### 文档元数据同步陷阱：代码完成 ≠ Story/SPEC 元数据完成

- **问题**：SDD 工作流要求 `spec-state.py complete` 更新状态机，也要求 doc-alignment 更新 `project-report.json`，但 **从不要求更新 Story/SPEC/EPIC 的 markdown 文件自身的元数据**（frontmatter 的 `status` 字段、AC 复选框、完成条件清单）。代码全部完成、测试全绿后，这些文件仍停留在 `status: draft`，AC 全部标记为 `[ ]`。
- **后果**：下次迭代或新开发者查看文档时，看到的 Phase 状态是「全部未完成」。EPIC-004 Phase 0/1/2 共 11 个 Story + 3 SPEC + EPIC + report 全部漂移，主人纠正后才对齐。
- **根因**：SDD 流程把「文档对齐」等同于「更新 project-report.json 和 HTML」，忽略了 markdown 文件自身的元数据。`spec-state.py complete` 只更新状态机，不修改 markdown 文件内容。

### 三维状态一致性陷阱：spec-state.py ≠ 文件 frontmatter ≠ project-state.yaml

- **问题**：即使 `spec-state.py complete "SPEC-X"` 执行成功，`project-state.py verify` 仍可能报「状态不一致」。这是因为 verify 检查**三个独立的状态来源**是否一致：（1）spec-state.py 状态机、（2）markdown 文件的 `> **status**:` frontmatter 字段、（3）project-state.yaml 中的 state 字段。三者完全独立，任一个不同步都会导致 verify 失败。
- **后果**：Phase 完成后 verify 报错 → 需要排查三个地方 → 增加不确定性。
- **根因**：spec-state.py 只管理它自己的 JSON 状态存储；project-state.py sync/verify 从 YAML 和 markdown 文件读取和比对。三个系统各管各的，没有自动同步机制。
- **解决**：
  1. `spec-state.py complete` 后，**必须手动同步** markdown 文件的 `> **status**:` frontmatter 字段（设为其真实状态）
  2. 然后运行 `project-state.py sync` 更新 project-state.yaml
   4. 最后 `project-state.py verify` 确认 zero drift
   5. ⚠️ **关键陷阱: `project-state.py sync` 可能回退状态**：sync 命令从 spec-state.py 的 JSON 存储读取数据，但 spec-state.py 对某些实体的记录可能滞后或缺失（如从未通过 spec-state.py create 创建的条目）。结果是 sync 后已完成的状态被**回退到 draft**。
  **实战案例**（2026-05-16 EPIC-005 Phase 1）：`project-state.py sync` 将 SPEC-5-1 从 completed 回退到 draft。修复方法：patch project-state.yaml 手动修正状态。
修复三步：
  1. 先手动更新 markdown 文件 frontmatter 中的 `> **status**:` 字段
  2. 再运行 `project-state.py sync`
  3. 最后检查 `project-state.py verify`。如果 sync 回退了状态，patch project-state.yaml 修正
  4. 三个层级的同步顺序：markdown frontmatter → project-state.yaml → verify
- **检查清单**：在标记 Phase 完成前，运行以下三维一致性检查：
  ```bash
  # 第一维: spec-state.py 状态机
  python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py status "SPEC-X"
  
  # 第二维: markdown frontmatter
  grep "^> \*\*status\*\*:" docs/SPEC-X.md
  
  # 第三维: project-state.yaml
  python3 -c "import yaml; d=yaml.safe_load(open('docs/project-state.yaml')); print(d['entities']['specs']['SPEC-X']['state'])"
  
  # 全三维一致 → verify 通过
  python3 scripts/project-state.py verify
  ```
- **实战案例**：2026-05-16 SPEC-5-0 完成时，spec-state.py 显示 completed，但 markdown 文件仍为 `> **status**: \`draft\``，verify 报错。
- **自动化方向**：`project-state.py sync` 未来可扩展为自动从 spec-state.py 读取状态并同步到 YAML 和 markdown frontmatter。
- **解决**：
  1. 在 Step 8 COMPLETE 中增加显式的「元数据同步」步骤（见上方修改后的 Step 8）
  2. Story/SPEC/EPIC 三个层级的文件都要更新，缺一不可
  3. 批量更新（10+ 文件）用 `execute_code` + Python 脚本，不要逐个 `patch`
  4. 运行验证命令确认零残留 `[ ]`
- **检查清单**：在标记 Phase 完成前，问自己：
  - [ ] 所有 Story 文件的 `status` 是否为 `completed`？
  - [ ] 所有 Story 文件的 AC 是否已从 `[ ]` 标记为 `[x]`？
  - [ ] SPEC 文件的 `status` 和完成条件是否已更新？
  - [ ] EPIC 文件的 `completed_phases` 是否有当前 Phase？
  - [ ] project-report.json 的 tests/sprint/module 是否同步？
- **实战案例**：EPIC-004 Phase 0-2 完成后 16 个文档同步更新。详见 `references/phase-completion-checklist.md`。

### 沟通陷阱：展示范围时只给部分信息
- **问题**：当主人问「这个 Epic 是什么」或讨论计划时，如果只展示你当前关注的子集（如「Phase 1 有 3 个模块」），主人会以为这就是全部
- **后果**：主人纠正你「不是只有这些吧？」，降低信任
- **解决**：永远先展示**全貌**（完整列表/所有 Phase），再聚焦当前讨论的子集。先给全景地图，再放大局部

### 沟通陷阱：跨项目和跨会话上下文丢失
- **问题**：
  - 用户说「启动 sdd 工作流」时，boku 默认展示当前项目（如 cap-pack），但用户可能在说另一个项目（如 SRA）
  - 用户说「刚刚发现的问题」「回到 XX 方向」引用前序会话，但 session_search 可能未命中
- **后果**：展示了错误项目的状态 → 用户纠正「回到 XX 项目」；找不到前序上下文 → 来回请求用户重述，降低信任
- **根因**：CLARIFY 阶段缺乏项目上下文确认步骤；跨会话上下文没有自动检索和优雅降级机制
- **解决**：
  1. CLARIFY 阶段先问「哪个项目？」或从对话历史推断
  2. 用户引用前序工作时，先 session_search 检索。结果为空时诚实告知并请用户补充
  3. 不要假设「当前项目 = 用户说的项目」

### Chain State 多 Phase 陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| **chain-state.json 只追踪 workflow stage (SPEC→DEV→QA→COMMIT)，不追踪 EPIC Phase (Phase-0→Phase-1→Phase-2)** | Phase 完成 → `chain-state.json` 显示 COMPLETED，但 `phase` 字段未更新 → 下一个 Phase 启动时没有正确的 Phase 上下文 | 每个 Phase 完成后手动更新 `phase` 字段。详见 `references/phase-completion-checklist.md` 的 §5 |

| 工具 | 场景 | 问题 | 解决方案 |
|:-----|:------|:------|:---------|
| `skill-lifecycle-audit.py --audit` | 全量审计 200+ skill | 耗时 > 30s，cron 场景下不可用 | 改用 `skill-tree-index.py --json` 获取统计（< 5s） |
| `skill-quality-score.py --audit` | 全量评分 | 同上 | 单 skill 评分用直接参数，全量用 `skill-tree-index.py --json` 的 SQS 字段 |
| `skill-lifecycle-audit.py --audit --json` | json 输出 200+ skill | 超时且 json 可能不完整 | 避免全量 audit，改用 `tree-index --json + lifecycle status` 组合 |

**通用原则**: 需要全量技能统计时，优先用 `skill-tree-index.py --json`（< 5s），避免 `lifecycle-audit --audit`（> 30s）。

### 工具输出格式陷阱

| 工具 | 格式假设 | 实际格式 | 陷阱 |
|:-----|:---------|:---------|:------|
| `skill-tree-index.py --json` | 预期 `{"meta": {...}, "tree": [...]}` | 实际是 **list**（每个模块一个元素） | 不要索引 `data["meta"]`，直接遍历 list |
| `generate-project-report.py` | module_table 通用格式 | **必须**用 `module`/`file`/`desc`/`methods` 字段 | 使用 `id`/`name`/`path`/`lines` 会报 KeyError |
| `skill-tree-index.py --health` | 预期含 "SQS" 或 "分数" | 实际无 SQS，只有 "总数/未分类/健康" | 检查字符串用 "健康" 或 "总数" |

### SRA 触发词陷阱：主人说「继续」但 SDD workflow 没被推荐

- **问题**：当主人说「继续」「下一阶段」「继续做」，SRA 没有推荐 sdd-workflow，因为 triggers 中缺少延续/阶段推进类关键词
- **根因**：SRA 四维匹配引擎基于词法+语义匹配。一次消息匹配得分 < 40 就不推荐。原有 triggers 只覆盖了创建类（"写 spec""创建 story"），没有延续类（"继续""phase"）
- **后果**：主人说「继续」→ SRA 无推荐 → boku 不加载 sdd-workflow → 跳过 SDD 流程直接凭感觉做
- **修复**：已在 SDD workflow triggers 中添加以下延续类关键词：
  `继续 phase 下一阶段 下一步 继续做 continue next phase next step carry on resume 恢复 往下走 启动 阶段推进 推进`
- **检查清单**：如果 SRA 没有推荐 SDD workflow，检查 `sra coverage | grep sdd-workflow` 确认 covered=true。如果为 false，说明 triggers 不够覆盖当前对话场景
- **验证方法**：`sra recommend "继续" --json | grep sdd` 确认返回了推荐

`sdd-workflow` v3.6.0 修复了 `skill-tree-index.py --consolidate` 的一个关键 Bug：

- **根因**: `build_tree()` 中未分类 cluster 缺少 `count` 字段，但 `print_tree()` 直接访问 `cluster['count']`
- **症状**: `--consolidate` 模式下 KeyError: 'count'
- **修复**: 在 `build_tree()` 的 unclassified 分支添加 `"count": len(unclassified)`
- **验证**: `--consolidate` 不再崩溃，正常输出合并建议

---

## 🗂️ 文件结构

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
  "spec_found": "docs/stories/STORY-1-1.md",
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

### 门禁集成到 pre_flight v2.0（2026-05-13 升级）

`pre_flight.py` v2.0 现已集成 SDD 门禁作为其 Gate 2/3。日常开发前只需运行：

```bash
python3 ~/.hermes/scripts/pre_flight.py "<task_description>"
```

pre_flight 自动完成三类检查：
1. **学习状态** — learning_state.json
2. **SDD 门禁** — 自动调用 spec-gate.py check（简单任务跳过，复杂任务强制）
3. **技能/包检测** — 自动检测 skill-creator 或 cap-pack 操作需求

**结果**：
- ✅ 全通过 → 继续
- ❌ SDD BLOCKED → 先创建 Story → 主人批准 → 再回来

其中 SDD 门禁逻辑：
```bash
# 由 pre_flight.py 自动调用，无需手动执行
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-gate.py check "<task_description>"
# 或强制模式（exit 1 时 BLOCKED）
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-gate.py enforce "<task_description>"
```

---

## 三、模板系统

### Story Spec 模板

参考文件: `templates/story-template.md`

核心字段：
- **story**: 唯一标识（如 STORY-1-5, STORY-3-1）
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
1. 🔍 Reality Check（验证代码现实 vs 文档声明）— 加载 doc-alignment Phase 0
   │
   ├── git log --oneline -30 | head -15           # 看代码最近做了什么
   ├── python -m pytest tests/ --collect-only -q   # 看测试是否真的通过
   ├── python3 ~/.hermes/scripts/generate-project-report.py --data docs/project-report.json --verify
   │   └── 如果项目有 project-report.json → --verify 检测漂移
   ├── 检查关键文件是否存在（文档所称 vs 实际）
   ├── 检查版本号一致性（文档 vs 代码）
   └── 决策：
       ├── ✅ 完全一致 → 信任文档，继续分析
       ├── ⚠️ 轻微差异 → 以代码为准，分析中注明
       └── 🔴 重大差异 → 先同步文档，再继续
    ↓
1.5 📊 项目状态检查
   ├── python3 /home/ubuntu/projects/hermes-cap-pack/scripts/project-state.py status
   └── 确认当前项目状态正常后继续
    ↓
2. 🛑 pre_flight.py 检查
    ↓
3. 📡 skill_finder.py 发现相关 skill
    ↓
4. 📋 SDD 门禁
   ├── python3 scripts/validate-sdd-naming.py --dir .  # 命名规范门禁
   │   └── 违规时 exit 1 → 先修正命名再继续
   ├── python3 scripts/spec-gate.py enforce "<task_description>"  # Spec 门禁
   ├── PASS → 继续
   └── BLOCKED → 创建 Spec → 等主人批准 → 再回来
    ↓
5. 📐 测试基础设施检查（已有 fixture 复用）
    ↓
6. 🏛️ ARCHITECT — 架构设计（APPROVED → architect）
   ├── 加载 `architecture-diagram` / `mermaid-guide` skill（如需架构图）
   ├── 确认技术选型：语言/框架/库/外部服务
   ╞══ 📋 技术版本规约（新增）═══
   │   ├── 使用 `templates/tech-spec.md` 创建技术版本清单
   │   ├── 每项技术必须锁定**精确版本**（禁止 ^ ~ latest）
   │   ├── 每项技术必须提供版本对应的 **API 参考文档链接**
   │   └── 从包管理文件（requirements.txt / pyproject.toml）提取依赖
   ├── 设计数据模型：实体、字段、关系
   ├── 设计 API 契约：端点、请求/响应格式
   ├── 记录 ADR（Architecture Decision Records）：
   │   ├── 决策内容：选了什么
   │   ├── 备选方案：没选什么
   │   └── 理由：为什么选这个
   ├── 明确文件变更范围：新建/修改/删除哪些文件
   └── 产出：
       ├── `docs/arch/{story_id}.md`（架构设计文档）
       └── `docs/tech-spec/{story_id}.md`（技术版本规约）🌟 新增
    ↓
7. 📋 PLAN — 实现计划（architect → plan）
   ├── 加载 `writing-plans` skill
   ├── 将架构设计拆分为 2-5 分钟的原子任务
   ├── 每个任务包含：文件路径 + 具体改动 + 验证命令
   ├── 标注任务依赖顺序（不可并行 vs 可并行）
   └── 产出：实施计划（todo 清单或 `docs/plans/{story_id}.md`）
    ↓
# Step 7: IMPLEMENT — 技术实现（plan → implement）
   ├── 加载 `generic-dev-workflow` skill（7 步开发流程）
   ├── 加载 `test-driven-development` skill（RED-GREEN-REFACTOR）
   ├── 🔴 **API 版本对照（新增强制步骤）**
   │   ├── 实现前：读取 `docs/tech-spec/{story_id}.md` 确认当前版本
   │   ├── 实现中：对照技术版本对应的 **API 参考文档** 使用正确的 API
   │   │   └── 示例：Python 3.11 用 `https://docs.python.org/3.11/`
   │   │   └── 示例：FastAPI 0.110 用 `https://fastapi.tiangolo.com/0.110/`
   │   ├── 禁止：凭训练数据中的旧 API 知识直接写代码
   │   └── 如版本不确定 → 先 web_search 获取版本对应文档 + 再实现
   ├── 可选：`subagent-driven-development`（子代理并行 + 双阶段审查）
   ├── **🔄 独立 Story 可并行执行**：Phase 内无依赖关系的 Story，用 `delegate_task` 并行执行
   │   ├── 条件：两个 Story 无共享资源/文件冲突、无顺序依赖
   │   ├── 方式：`delegate_task(tasks=[...])` 一次派发多个独立 Story
   │   ├── 验证：每个 delegate 内部独立完成 → boku 统一汇总 verify
   │   └── 实战案例：EPIC-005 Phase 0 的 STORY-5-0-2 和 STORY-5-0-3（规则集 + 编排模式，无依赖）并行执行
   ├── 逐个 Task 实现：写测试→写代码→验证→提交
   └── 每个 Task 完成后原子 git commit
    ↓
9. ✅ 验证
   ├── pytest（全量测试）
   ├── commit-quality-check（提交前检查）
   ├── 📋 **doc-alignment — HTML 报告对齐协议**
   │   │
   │   ├── Phase 0.5: Story/SPEC/EPIC 元数据同步（⚠️ 关键：代码完成 ≠ 文档完成）
│   │   代码通过测试后，必须手动同步所有 markdown 元数据，否则下次迭代时
│   │   文档仍为 draft/active 状态，AC 标记仍为 [ ]，造成系统性文档漂移。
│   │   ├── Story 文件: status → completed, 所有 AC [ ] → [x]
│   │   ├── SPEC 文件: status → completed, 完成条件 [ ] → [x]
│   │   ├── EPIC 文件: 更新 completed_phases, 标记对应 Phase 为 ✅
│   │   └── 批量操作技巧: 10+ 文件时用 execute_code + Python 脚本
│   │       (re.sub 批量替换) 比逐个 patch 高效。示例见 references/phase-completion-checklist.md
│   │
│   ├── Phase 1: 更新数据文件
   │   │   ├── 修改 docs/project-report.json（如有）：
   │   │   │   ├── Story 完成 → epics[].stories[].status = "completed"
   │   │   │   ├── 新增模块/Tests → architecture/tests 字段更新
   │   │   │   ├── 版本升级 → project.version 更新
   │   │   │   └── Sprint 完成 → sprint_history[] 新增条目
   │   │   └── 如无 project-report.json → 创建标准 JSON（模板见 doc-alignment references/）
   │   │
   │   ├── Phase 2: 重新生成 HTML
   │   │   ├─ 运行命令：
   │   │   │
   │   │   │   ```bash
   │   │   │   # ❌ 旧方案: python3 ~/.hermes/scripts/generate-project-report.py 已废弃 (主人明确否定模板脚本)
   # ✅ 新方案: 加载 project-report-generator skill 实现五阶段 LLM 驱动创作
   #     skill_view(name='project-report-generator')
   #     skill_view(name='web-ui-ux-design')
   #     skill_view(name='visual-aesthetics')
   │   │   │       --data docs/project-report.json \
   │   │   │       --output PROJECT-PANORAMA.html
   │   │   │   ```
   │   │   │
   │   │   └─ 确保 HTML 与 docs/project-report.json 同 commit
   │   │
   │   └── Phase 3: 验证
   │       ├── python3 ~/.hermes/scripts/generate-project-report.py --data docs/project-report.json --verify
   │       └── 漂移数 = 0 → ✅ | 漂移数 > 0 → 🔴 修复后再提交
   │
   ├── 🔴 **版本合规检查（新增）**
       ├── 读取 `docs/tech-spec/{story_id}.md` 版本清单
       ├── 检查 lock 文件（requirements.txt / poetry.lock）版本是否匹配
       ├── 检查代码中使用的 API 是否与声明的版本一致
       │   └── 示例：tech-spec 声明 FastAPI 0.110 → 代码中不应使用 0.111 API
       └── 如不匹配 → 记录偏差至决策日志，更新 tech-spec 或修复代码
    ↓
10. 📋 AC 审计 — 确保 Epic AC 与代码同步（含代码存在性验证）
    ├── python3 scripts/ac-audit.py check docs/EPIC-*.md
    ├── 确认漂移 = 0
    ├── 🔴 **关键步骤：代码存在性验证**（AC 审计盲点防范）
    │   ├── `[x]` 标记 ≠ 代码真实存在。必须验证每个标记 ✅ 的 AC 有对应代码。
    │   ├── 检查方法：grep / curl / pytest 等命令验证
    │   │   └── 示例：如 AC 说「Hermes pre_tool_call hook 集成」
    │   │        → `grep -r "pre_tool_call" plugins/sra-guard/`
    │   │   └── 示例：如 AC 说「端点已实现」
    │   │        → `curl http://127.0.0.1:8536/health`
    │   └── 跨系统 AC 必须两侧验证
    └── 如未勾选 → python3 scripts/ac-audit.py sync docs/EPIC-*.md --apply
    ↓
11. 📝 Spec 状态更新（implement → complete → archive）
```

---

## 五、与其他 Skill 的集成

| Skill | 集成点 | 触发时机 |
|:------|:-------|:---------|
| `sdd-research` | RESEARCH 阶段结构化调研方法论 | 进入 RESEARCH 阶段时 |
| `development-workflow-index` | 决策树中 SDD 路径 | 任务开始时 |
| `architecture-diagram` / `mermaid-guide` | 架构图生成 | ARCHITECT 阶段 |
| `writing-plans` | 将 Spec 的 AC 转化为原子任务 | PLAN 阶段 |
| `generic-dev-workflow` | 7 步标准开发实施 | IMPLEMENT 阶段 |
| `test-driven-development` | RED-GREEN-REFACTOR 循环 | IMPLEMENT 阶段 |
| `subagent-driven-development` | 子代理并行 + 双阶段审查 | IMPLEMENT 阶段（可选） |
| `doc-alignment` | HTML 报告全生命周期管理与文档漂移检测 | 任何变更后 + COMPLETED + ARCHIVED |
| | ├─ Phase 0: Reality Check | CLARIFY 阶段（任务开始前） |
| | ├─ Phase 1: 更新数据文件 + 生成 HTML | COMPLETED 时（验证步骤中） |
| | └─ Phase 2-3: 验证漂移 + 发布前检查 | ARCHIVED 门禁（漂移=0 才能归档） |
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
  ├── 新增 RESEARCH 阶段：自动触发 sdd-research skill（多轮搜索 + 来源验证）
  └── 需求澄清模板 + 检查清单

v2.0 (长期) — 飞书交互卡片
  ├── 改造 feishu.py 支持交互卡片（按钮+选择器+输入框）
  └── 需求澄清通过交互卡片完成
```

### 6.3 详细设计方案

完整的研究文档见 `references/sdd-known-gaps-and-roadmap.md`，包含：
- 飞书卡片交互能力完全矩阵（button/selectMenu/input/form 的回调机制）
- 文档质量检查 9×1 模型（一致性×逻辑性×完整性 × 结构×内容×体系）
- 改进后 9 状态状态机设计（CLARIFY → RESEARCH → CREATE → QA_GATE → REVIEW → APPROVED → ARCHITECT → PLAN → IMPLEMENT → COMPLETED → ARCHIVED）
- Phase 1-4 实施路径

---

## 🗂️ 文件结构

```text
~/.hermes/skills/dogfood/sdd-workflow/
├── SKILL.md                         ← 主入口
├── scripts/
│   ├── spec-state.py                ← ⚡ 已实现！9 状态状态机
│   ├── spec-gate.py                 ← ⚡ 已实现！门禁检查器
│   └── validate-sdd-naming.py       ← ⚡ 已实现！命名规范门禁（2026-05-13）
├── templates/
│   ├── story-template.md            ← Story Spec 模板
│   └── epic-template.md             ← Epic 模板
└── references/
    ├── sdd-research.md              ← SDD 深度研究
    ├── sdd-lifecycle.md             ← 六阶段生命周期指南
    ├── real-world-usage-sra-004-01.md ← SRA 项目实战记录
    ├── sdd-known-gaps-and-roadmap.md ← 已知缺口与改进路线图
    ├── session-context-recovery.md  ← 跨会话上下文恢复协议（2026-05-15）
    ├── batch-rename-pitfalls.md     ← 批量重命名陷阱与安全替换模式
    ├── sdd-doc-alignment-integration.md ← SDD × doc-alignment 集成协议 v1.0（2026-05-14）
    - `references/feishu-review-flow.md`        ← Spec/Story 飞书审阅工作流与消息模板
    - `references/combined-workflow-epic005-p3.md` ← 联合工作流实战记录：EPIC-005 Phase 3 全链无停顿
```

> ⚠️ **历史**: 2026-05-13 之前 spec-state.py 和 spec-gate.py 仅在文档中描述但未实现。2026-05-13 在 hermes-cap-pack 项目中重建实现。如果在现有安装中找不到脚本，运行以下命令检验：
> ```bash
> ls ~/.hermes/skills/sdd-workflow/scripts/
> # 应输出: spec-state.py  spec-gate.py

## 📚 参考深度阅读

- **`references/sdd-research.md`** — SDD 三大框架（BMAD/Superpowers/GSD）核心对比、成熟度模型、关键数据
- **`references/sdd-lifecycle.md`** — 六阶段完整生命周期指南（CREATE→ARCHIVE 每个阶段的详细操作）
- **`references/real-world-usage-sra-004-01.md`** — 在 SRA 项目中完整走通 SDD 全流程的实战记录
- **`references/sdd-known-gaps-and-roadmap.md`** — 当前流程审计、飞书卡片交互研究、质量检查框架、v2.0 设计草案
- **`references/session-context-recovery.md`** — 跨会话上下文恢复协议：当用户引用前序会话中的问题/报告但 session_search 未命中时的 4 步恢复流程 + 项目上下文切换协议
- **`references/batch-rename-pitfalls.md`** — 批量文档重命名陷阱（字符串包含问题）与安全替换模式
    - `references/epic-004-multi-phase-pattern.md` — 多 Phase EPIC 完整实战模式：从 Phase 0 到收尾的 22 Story 完整生命周期管理
    - `references/cap-pack-naming-migration.md` — CAP Pack 项目命名迁移实战记录（含完整检查清单）
    - `references/epic-005-phase0-pattern.md` — Phase 级别 SPEC 模式实战：SPEC-5-0（标准定义）与 SPEC-5-1（核心引擎）分离的 Phase 0 完整生命周期

## 🔗 Workflow Chain Protocol — SDD→DEV→QA 三段链式衔接

SDD 不是终点。Story 完成（COMPLETED）后，应自动链入开发工作流和 QA 门禁。

### 两种链模式：逐段推进 vs 联合工作流

根据主人的指令密度，有两种链模式：

| 模式 | 触发词 | 行为 | 适用场景 |
|:-----|:-------|:------|:---------|
| **逐段推进** (默认) | 「批准」「继续」「推进」 | 每完成一个阶段等待主人确认后进入下一阶段 | 常规开发，主人想随时纠正方向 |
| **联合工作流** | 「可以进行联合工作流」「跑完整链」「全链走通」 | 一次跑完 SPEC→DEV→QA→COMMIT 全链，最后汇报结果 | Phase 范围已明确、主人信任方向 |

#### 联合工作流流程 (实战验证: EPIC-005 Phase 3)

```text
主人：「可以进行联合工作流」

boku：
  1. 创建 SPEC + Story 文档 (一次性全部创建)
  2. 更新 project-state.yaml 记录新实体
  3. 按依赖顺序启动 DEV：
     a. 基础层 Story 先 (如 STORY-5-3-1: 适配器基类)
     b. 无依赖 Story 并行 (如 STORY-5-3-2 MCP + STORY-5-3-3 适配器)
  4. QA L0-L2 门禁 (语法→测试→集成验证)
  5. 一次过更新所有状态追踪文件 (见下方「Phase-end 一次性对齐」)
  6. COMMIT (一条 commit 包含全链交付)
  7. 向主人展示结果

关键区别：没有逐阶段 "主人批准？" 的停顿。
           一次规划 → 一次实施 → 一次验证 → 一次提交。
```

#### 联合工作流使用条件

✅ Phase 范围已在 EPIC 文档中明确（如 EPIC-005 Phase 3 有 3 个 Story 定义）
✅ 主人主动说了「联合工作流」「跑完整链」或同类词
✅ 当前 Phase 的依赖 Phase 全部已完成
✅ 无需在 DEV 过程中向主人请求架构决策（决策已由主人或 EPIC 文档覆盖）

❌ Phase 范围模糊或 EPIC 文档只有标题没有细节 → 先 CLARIFY，不可用联合工作流
❌ 主人没有明确说联合工作流 → 默认逐段推进
❌ 需要主人做架构决策 → 逐段推进

#### Phase-end 一次性对齐技术 (实战验证: EPIC-005 Phase 3)

在联合工作流中，**不要逐个 Story 地更新状态追踪文件**，而是在 Phase end 一次性更新所有文件：

```text
Phase 实现完成 → 一次性对齐 5+ 文件：

┌─ Layer 1: Story 文件 frontmatter ──────────────┐
│  status: draft → completed (3+ 文件一次过)        │
│  用 execute_code + Python 批量 replace, 不逐个 patch│
├─ Layer 2: SPEC 文件 frontmatter ─────────────────┤
│  status: draft → completed                       │
├─ Layer 3: EPIC 文件 ─────────────────────────────┤
│  Phase AC [ ] → [x], 标记 ✅                     │
├─ Layer 4: project-state.yaml ────────────────────┤
│  completed_count 更新, story state 更新           │
├─ Layer 5: project-report.json ───────────────────┤
│  stories[].status, sprint_history, epics[] 更新   │
├─ Layer 6: chain-state.json ──────────────────────┤
│  phase 字段更新, COMPLETED 标记                   │
└──────────────────────────────────────────────────┘

# 最后: 一次验证
python3 scripts/project-state.py verify

批量效率提示：
- 10+ 文件 frontmatter 更新：execute_code + Python str.replace
- YAML/JSON 文件更新：patch 或 execute_code + yaml/json 库
- chain-state.json 的 phase 字段：手动写入最新 Phase 编号
```

### chain-state.json Phase 追踪陷阱

**问题**: chain-state.json 只追踪 workflow stage (SPEC→DEV→QA→COMMIT)，不自动追踪 EPIC Phase (Phase-0→Phase-1→Phase-2)。chain-state.py advance 只切换 stage，不会更新 `phase` 字段。

**后果**: Phase 完成 → chain-state.json 显示 COMPLETED 但 `phase` 字段仍是旧值 → 下一个 Phase 启动时没有正确的 Phase 上下文。

**解决**: 每个 Phase 完成时，手动更新 chain-state.json 的 `phase` 字段：

```json
{
  "EPIC-005": {
    "epic": "EPIC-005",
    "current_stage": "COMPLETED",
    "completed_stages": ["SPEC", "DEV", "QA", "COMMIT"],
    "phase": "Phase-3",  // ← 手动更新！
    "gate_history": []
  }
}
```

**检查清单**: Phase 完成时，问自己：
- [ ] chain-state.json 的 `phase` 字段是否已更新为当前 Phase？
- [ ] 如果下一个 Phase 是第一个，`phase` 应设为 `Phase-0`


### 三段链

```
SDD COMPLETED ──→ DEV ──→ QA ──→ COMMIT
   │               │        │        │
   │  gate:        │ gate:  │ gate:  │
   │ spec 已批准   │ 测试全绿│ 全部   │
   │               │ self-   │ 门禁   │
   │               │ review  │ 通过   │
   ▼               ▼        ▼        ▼
chain-state.py 自动推进（advance 命令）
```

### 使用方式

在 cap-pack 项目中：

```bash
# 1. 启动链（在 SDD CLARIFY 阶段执行）
python3 scripts/chain-state.py start EPIC-004 SPEC

# 2. 推进到下一阶段（在 Story COMPLETED 后执行）
python3 scripts/chain-state.py advance EPIC-004

# 3. 查看链状态
python3 scripts/chain-state.py status EPIC-004

# 4. 强制推进（跳过 gate）
python3 scripts/chain-state.py advance EPIC-004 --force
```

### 自动加载

chain-state.py advance 成功后，会自动提示加载下一个阶段的 skill：
- SPEC → DEV: `skill_view(name='generic-dev-workflow')`
- DEV → QA: `skill_view(name='generic-qa-workflow')`
- QA → COMMIT: `skill_view(name='generic-dev-workflow')`（Step 7 提交与对齐）

### 关键文件

| 文件 | 位置 | 用途 |
|:-----|:------|:------|
| `chain-state.py` | cap-pack/scripts/ | 链状态机 |
| `chain-gate.py` | cap-pack/scripts/ | 链门禁检查器 |
| `workflow-chain.yaml` | cap-pack/docs/ | 链定义配置 |
| `chain-state.json` | cap-pack/docs/ | 链状态持久化 |

### 铁律

- 🔴 **不要在 SDD COMPLETED 后直接开始写代码** — 先 `chain-state.py advance` 进入 DEV 阶段。或者更完整的顺序：SDD Story 完成后 → `chain-state.py advance` → 加载 generic-dev-workflow → 开发 → 自行验证 → `chain-state.py advance` → 加载 generic-qa-workflow → QA 门禁 → `chain-state.py advance` → COMMIT。
  **实战案例**: EPIC-005 Phase 0/1/2 均使用此模式：SDD SPEC/Story 完成后依次 advance 通过 SPEC→DEV→QA→COMMIT，每阶段独立验证门禁。
- 🔴 **不要在 DEV 完成后跳过 QA** — Step 5 的嵌入式 QA 门禁会自动加载 generic-qa-workflow
- 🔴 如果 chain-state.py advance 被 gate 阻止 → 修复 gate 条件再重试，不要 --force

### 场景 1：新功能开发（含 v3.0 完整流程）

当使用 SDD v3.0 完整流程时，包含 CLARIFY → RESEARCH → CREATE → QA_GATE → REVIEW → APPROVED → ARCHITECT → PLAN → IMPLEMENT：

```text
# Step 0: CLARIFY — 需求澄清
## 子步骤:
# 0a. 项目上下文确认 — 用户说"启动 sdd 工作流"时，先确认哪个项目
#     不要默认当前项目，显式询问或从对话历史推断项目上下文
#     (实战教训: 用户说"启动 sdd 工作流"，boku 展示了 cap-pack → 被纠正"回到 sra 项目")
# 0b. 会话历史检索 — 搜索 session history 获取近期相关讨论
#     用户说"刚刚发现的问题""之前讨论过的"等引用前序工作时，主动 session_search
#     如 session_search 结果为空 → 诚实报告并请用户补充，不要假设
# 0c. 需求理解输出 — boku 输出项目全貌 + 需求理解
#     永远先展示全貌(所有 EPIC/Phase)，再聚焦当前讨论的子集
# 0d. 主人确认 — 主人确认方向正确后，进入下一阶段
# 产出: docs/req_clarification/{task_id}.md
# 方式: clarify 工具或飞书交互卡片

# Step 0.5: Reality Check — 加载 doc-alignment Phase 0
# ❌ 旧: python3 ~/.hermes/scripts/generate-project-report.py --verify 已废弃
# ✅ 新: 由 project-report-generator skill Phase 4 的门禁自行验证
# ✅ 新: 用 project-report-generator skill 五阶段创作 HTML
#     --data docs/project-report.json --verify
# ⚠️ 如项目有 project-report.json → 必须在此步验证文档与代码一致性

# Step 1: RESEARCH — 技术调研（sdd-research 结构化调研）
# 加载 sdd-research skill → 多轮搜索 + 来源验证 + MECE 分析
# 产出: docs/research/{spec-id}.md 调研笔记 → 输入 SPEC CREATE
# 产出: 调研笔记

# Step 2: CREATE — 创建 Story Spec
python3 spec-state.py create "STORY-1-1" "批量推荐接口"
# 用模板 docs/stories/STORY-TEMPLATE.md 填充内容

# Step 3: QA_GATE — 质量门禁
python3 scripts/spec-gate.py verify "STORY-1-1"   # P0 结构检查
# P1 内容自查 → 加载 self-review 检查准确性
# P2 体系检查 → python3 doc-alignment --verify

# Step 4: REVIEW — 提交审阅
python3 spec-state.py submit "STORY-1-1"

# [主人批准后]

# Step 5: ARCHITECT — 架构设计
# 加载 architecture-diagram skill
# 加载 arch-template.md
# 产出: docs/arch/STORY-1-1.md（含 ADR、数据模型、API契约）
python3 spec-state.py architect "STORY-1-1"

# Step 6: PLAN — 实现计划
# 加载 writing-plans skill
# 拆分为 2-5 分钟原子任务，标注依赖
# 产出: todo 清单或 docs/plans/STORY-1-1.md
python3 spec-state.py plan "STORY-1-1"

# Step 7: IMPLEMENT — 技术实现
# 加载 generic-dev-workflow + TDD + 可选 subagent
# 逐个 Task: RED→GREEN→REFACTOR→验证→提交
python3 spec-state.py implement "STORY-1-1"

# Step 8: COMPLETE — 完成归档
pytest tests/ -q

# 🔴 强制步骤：Story/SPEC/EPIC 元数据同步（代码完成 ≠ 文档完成）
# 代码通过测试后，必须同步更新所有相关 markdown 文件的元数据。
# 不执行此步 → 文档仍为 draft → 下次迭代出现文档漂移。
#
# 同步清单：
#   ├── Story 文件: status: completed, 所有 AC [ ] → [x]
#   ├── SPEC 文件: status: completed, 完成条件 [ ] → [x]
#   ├── EPIC 文件: 更新 completed_phases, 标记对应 Phase 为 ✅
#   └── project-report.json: 同下
#
# 批量更新技巧（10+ 文件时用）：
#   execute_code + Python (re.sub / str.replace) 比逐个 patch 高效可靠
#   示例: 用 execute_code 做 content.replace("- [ ] ", "- [x] ") 批量标记 AC

# doc-alignment Phase 1: 更新数据文件（project-report.json）
# 编辑 docs/project-report.json → 更新 Story 状态/版本号/Tests 等

# doc-alignment Phase 2: 重新生成 HTML
# ❌ 旧: python3 ~/.hermes/scripts/generate-project-report.py --verify 已废弃
# ✅ 新: 由 project-report-generator skill Phase 4 的门禁自行验证
# ✅ 新: 用 project-report-generator skill 五阶段创作 HTML
#     --data docs/project-report.json \
#     --output PROJECT-PANORAMA.html

# doc-alignment Phase 3: 验证漂移
# ❌ 旧: python3 ~/.hermes/scripts/generate-project-report.py --verify 已废弃
# ✅ 新: 由 project-report-generator skill Phase 4 的门禁自行验证
# ✅ 新: 用 project-report-generator skill 五阶段创作 HTML
#     --data docs/project-report.json --verify
# 漂移数 > 0 → 修复后再提交

# AC 审计
python3 scripts/ac-audit.py check docs/EPIC-*.md
python3 scripts/ac-audit.py sync docs/EPIC-*.md --apply

# 状态机完成
python3 spec-state.py complete "STORY-1-1"
python3 spec-state.py archive "STORY-1-1"
```

⚠️ **常见陷阱**: 跳过 CLARIFY 直接写文档是 SDD 最常见的违规行为。主人纠正过「文档阶段之前缺乏需求澄清阶段」。即使任务看起来简单，也必须先做 CLARIFY。

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
| **7** | **文档命名统一为层级归属格式：`EPIC-{n}` / `SPEC-{epic}-{seq}` / `STORY-{epic}-{spec}-{seq}`** | 跨项目无法对齐、工具链解析失败、混淆 |
| **8** | **每次 Spec 状态变更后必须同步 project-state.yaml — `python3 /home/ubuntu/projects/hermes-cap-pack/scripts/project-state.py sync`** | project-state.yaml 与 Spec 状态不同步 → 项目全景报告不准确 |
| **9** | **先定义→对齐文档→再实施。PLAN 阶段必须确认源码位置、部署位置、测试位置，先于编码** | 代码在错误目录 → 返工；文档与代码脱节 → 下次决策错误 |
| **10** | **AC 标记 ✅ 必须附加代码存在性验证，不能仅凭文档声明** | EPIC-001/003 虚假 ✅ → 整个集成方案从未工作 |

### 7.1 统一文档命名规范详解

所有 SDD 文档（EPIC/SPEC/STORY）必须遵循层级归属命名格式，从文件名直接看出文档在体系中的位置。

#### 7.1.1 命名格式总表

| 文档类型 | 格式 | 示例 | 说明 |
|:---------|:-----|:-----|:------|
| **EPIC** | `EPIC-{n}`（可带描述后缀） | `EPIC-001`, `EPIC-001-feasibility` | `{n}` 为 **3 位顺序号**，描述后缀可选（仅限 EPIC 顶层入口） |
| **SPEC** | `SPEC-{epic}-{seq}` | `SPEC-1-4`, `SPEC-2-1` | `{epic}`=所属 EPIC 编号, `{seq}`=该 EPIC 内顺序号 |
| **STORY** | `STORY-{epic}-{spec}-{seq}` | `STORY-1-4-3`, `STORY-2-2-1` | `{spec}`=所属 SPEC 号, `{seq}`=该 SPEC 内顺序号 |
| **PLAN** | `EPIC-{n}-{description}` | `EPIC-003-phase1-decomposition` | EPIC 级别的分解方案/计划 |
| **ARCH** | `ARCH-{epic}-{spec}-{seq}` | `ARCH-1-4-3` | 架构设计文档（SDD ARCHITECT 阶段产出） |
| **TECH** | `TECH-{epic}-{spec}-{seq}` | `TECH-1-4-3` | 技术版本规约（SDD ARCHITECT 阶段产出） |

#### 7.1.2 参数说明

| 参数 | 含义 | 取值规则 | 示例 |
|:-----|:------|:---------|:-----|
| `{n}` | EPIC 编号 | 3 位数字，全局顺序 | `001`, `002` |
| `{epic}` | EPIC 编号（简写） | 数字，与 EPIC-{n} 的 n 对应 | EPIC-001 → `1` |
| `{spec}` | SPEC 在该 EPIC 内序号 | 数字，从 1 开始 | EPIC-001 的第 4 个 SPEC → `4` |
| `{seq}` | STORY 在该 SPEC 内序号 | 数字，从 1 开始 | SPEC-1-4 的第 3 个 STORY → `3` |

#### 7.1.3 目录结构

```
docs/
├── EPIC-001.md                     # Epic 文档（顶层）
├── EPIC-002.md
├── SPEC-1-1.md                     # Spec 文档（顶层，带层级前缀）
├── SPEC-1-2.md
├── STORY-TEMPLATE.md               # 模板文件
├── stories/
│   ├── STORY-1-1-1.md              # Story 文档（子目录）
│   ├── STORY-1-1-2.md
│   ├── STORY-1-4-3.md
│   └── ...
├── plans/
│   └── EPIC-003-phase1-decomposition.md  # 分解方案
├── arch/
│   └── ARCH-1-4-3.md               # 架构设计（可选）
└── tech-spec/
    └── TECH-1-4-3.md               # 技术版本规约（可选）
```

#### 7.1.4 归属关系可视化

文件名直接表达了完整的层级链：

```
EPIC-001
 └── SPEC-1-4              → EPIC-001 的第 4 个 SPEC
      └── STORY-1-4-3       → SPEC-1-4 的第 3 个 STORY
           └── ARCH-1-4-3   → STORY-1-4-3 的架构设计文档
           └── TECH-1-4-3   → STORY-1-4-3 的技术版本规约
```

**无需打开文件即可知道归属关系。**

#### 7.1.5 规范要点

- ✅ `STORY-1-4-3.md` — EPIC-001 / SPEC-1-4 的第 3 个 Story
- ✅ `SPEC-2-1.md` — EPIC-002 的第 1 个 Spec
- ✅ 文件内部的 `story_id`、`epic`、`spec_ref` 字段必须与文件名严格一致
- ✅ SPEC 和 STORY 的编号在各自层级内从 1 开始连续编号

#### 7.1.6 禁止的格式

- ❌ `STORY-001-splitting-analysis.md`（带描述，v0.3.0 前旧格式）
- ❌ `STORY-1-1.md`（缺失 SPEC 层级）
- ❌ `SPEC-001-splitting.md`（带描述，无层级前缀）
- ❌ `SRA-004-01`（项目前缀）
- ❌ `S-NNN`（缩写）

#### 7.1.7 创建新文档时的命名步骤

```text
1. 确定 EPIC 编号 → EPIC-{n}（如 EPIC-003）
2. 确定是该 EPIC 的第几个 SPEC → SPEC-{epic}-{seq}（如 SPEC-3-1）
3. 确定是该 SPEC 的第几个 STORY → STORY-{epic}-{spec}-{seq}（如 STORY-3-1-1）
```

#### 7.1.8 迁移要求

迁移后需同步更新所有交叉引用（详见 7.1.11 变更检查清单）。

#### 7.1.9 脚本门禁

```bash
# 命名规范门禁检查（已集成到 CI 和 pre_flight）
python3 ~/.hermes/skills/sdd-workflow/scripts/validate-sdd-naming.py
# 输出：命名规范合规报告，exit code=0（通过）/ 1（有违规）
```

#### 7.1.10 文档迁移工作流

当需要对存量文档进行批量改名/迁移时，按此流程执行：

```text
Step 1: 定义 → 在 SDD skill 中明确命名规范（本 skill 的 7.1 节）
Step 2: 门禁 → 创建 validate-sdd-naming.py 脚本作为自动化检测
Step 3: 验证 → 先跑门禁，确认当前违规清单
Step 4: 执行 → 批量改名（文件 + 内部字段 + 交叉引用）
Step 5: 复核 → 再跑门禁，确认零违规 → exit 0
```

**关键原则**：规则（门禁脚本）必须先于改名执行。改名后再创建门禁等于没有门禁。

#### 7.1.11 变更检查清单

迁移后需同步更新：
- 文件内部 `story_id` 字段（Story 文件）
- SPEC 文件的 `epic` 引用
- 所有交叉引用（Epic 列表、Spec 范围、其他 Story 文件内的引用）
- EPIC 交付物清单中的对应行
- pre_flight.py / spec-gate.py 等脚本中的搜索路径
- CI 配置中的文件路径（如存在）

> ⚠️ **批量重命名陷阱**：字符串包含导致的交叉引用损坏（如 `STORY-1-1` 包含在 `STORY-1-10` 中）。
> 详见 `references/batch-rename-pitfalls.md` — 包含安全替换模式和实战案例。

---

<div style="border-left: 4px solid #e74c3c; padding-left: 1em; margin: 1em 0;">
<strong>⚠️ 本节（7.1）取代了旧版 7.1 Story 命名规范详解。v3.3.0 前版本仅定义 <code>STORY-{epic}-{seq}</code> 格式。</strong>
</div>

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
# P0: 结构检查 — 自动（两步）
python3 scripts/validate-sdd-naming.py --dir .    # 命名规范门禁
python3 scripts/spec-gate.py verify "<story_id>"   # Spec 完整性检查

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