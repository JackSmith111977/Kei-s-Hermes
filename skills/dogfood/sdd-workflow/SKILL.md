---
name: sdd-workflow
description: "Spec-Driven Development 完整工作流 — 从 Spec 创建到代码实现的自动化生命周期管理。含状态机(spec-state.py)、门禁检查(spec-gate.py)、模板库、技术版本规约。任何涉及 SDD/规范驱动/Story 开发的任务自动触发。"
version: 3.3.0
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

# 🧭 SDD Workflow v3.0 — Spec-Driven Development 全生命周期管理

> **核心理念**: 没有批准的 Spec 就不写代码。没有架构设计就不开始实现。
> **设计模式**: 状态机 + 门禁 + 模板 + 架构设计 四位一体

---

## 〇、工作流总览

```
CLARIFY ──→ RESEARCH ──→ CREATE ──→ QA_GATE ──→ REVIEW ──→ APPROVED
 需求澄清     技术调研      写 Spec      质量检查     主人审阅     批准
                                                                  ↓
                                                          ARCHITECT ──→ PLAN ──→ IMPLEMENT
                                                           架构设计      实现计划     技术实现
                                                                                        ↓
                                                                                  COMPLETED ──→ ARCHIVED
                                                                                   完成          归档
```

**九个状态，八个转换门禁，每个门禁必须通过才能进入下一状态。**
**新增**: ARCHITECT（架构设计）、PLAN（实现计划）、IMPLEMENT（技术实现）三阶段替代原 IN_PROGRESS。

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

### 状态转换规则

| 当前状态 | 允许的操作 | 下一状态 | 门禁条件 |
|:---------|:-----------|:---------|:---------|
| (none) | `create` | draft | 提供 story_id + title |
| draft | `submit` | review | Spec 文件存在 + 必需字段完整 |
| review | `approve` | approved | 主人确认批准 |
| review | `reject` | draft | 记录拒绝原因，退回修改 |
| approved | `architect` | architect | 无（主人已批准，开始架构设计）|
| **architect** | `plan` | **plan** | 架构文档完整 + ADR 记录完成 |
| **plan** | `implement` | **implement** | 实施计划完整 + 任务分解可执行 |
| implement | `complete` | completed | pytest 通过 + AC 验证通过 |
| completed | `archive` | archived | doc-alignment + HTML对齐 通过 |
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
8. 🏗️ IMPLEMENT — 技术实现（plan → implement）
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
   ├── 逐个 Task 实现：写测试→写代码→验证→提交
   └── 每个 Task 完成后原子 git commit
    ↓
9. ✅ 验证
   ├── pytest（全量测试）
   ├── doc-alignment（文档漂移检测）
   ├── commit-quality-check（提交前检查）
   ├── 🌐 HTML 报告对齐
   │   ├── 如有 project-report.json → `generate-project-report.py` 自动同步
   │   └── 如无 → 手动更新 HTML 状态表
   └── 🔴 **版本合规检查（新增）**
       ├── 读取 `docs/tech-spec/{story_id}.md` 版本清单
       ├── 检查 lock 文件（requirements.txt / poetry.lock）版本是否匹配
       ├── 检查代码中使用的 API 是否与声明的版本一致
       │   └── 示例：tech-spec 声明 FastAPI 0.110 → 代码中不应使用 0.111 API
       └── 如不匹配 → 记录偏差至决策日志，更新 tech-spec 或修复代码
    ↓
10. 📋 AC 审计 — 确保 Epic AC 与代码同步
    ├── python3 scripts/ac-audit.py check docs/EPIC-*.md
    ├── 确认漂移 = 0
    └── 如未勾选 → python3 scripts/ac-audit.py sync docs/EPIC-*.md --apply
    ↓
11. 📝 Spec 状态更新（implement → complete → archive）
```

---

## 五、与其他 Skill 的集成

| Skill | 集成点 | 触发时机 |
|:------|:-------|:---------|
| `development-workflow-index` | 决策树中 SDD 路径 | 任务开始时 |
| `architecture-diagram` / `mermaid-guide` | 架构图生成 | ARCHITECT 阶段 |
| `writing-plans` | 将 Spec 的 AC 转化为原子任务 | PLAN 阶段 |
| `generic-dev-workflow` | 7 步标准开发实施 | IMPLEMENT 阶段 |
| `test-driven-development` | RED-GREEN-REFACTOR 循环 | IMPLEMENT 阶段 |
| `subagent-driven-development` | 子代理并行 + 双阶段审查 | IMPLEMENT 阶段（可选） |
| `doc-alignment` | Spec 变更后的文档同步 | 任何变更后 + COMPLETED |
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
    └── sdd-known-gaps-and-roadmap.md ← 已知缺口与改进路线图
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

## 🚀 使用示例

### 场景 1：新功能开发（含 v3.0 完整流程）

当使用 SDD v3.0 完整流程时，包含 CLARIFY → RESEARCH → CREATE → QA_GATE → REVIEW → APPROVED → ARCHITECT → PLAN → IMPLEMENT：

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
doc-alignment --verify
# HTML 报告对齐检查
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

迁移后需同步更新：
- 文件内部 `story_id` 字段（Story 文件）
- SPEC 文件的 `epic` 引用
- 所有交叉引用（Epic 列表、Spec 范围、其他 Story 文件内的引用）
- EPIC 交付物清单中的对应行
- pre_flight.py / spec-gate.py 等脚本中的搜索路径

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