---
name: development-workflow-index
description: "开发工作流索引 — 整合 BMAD Method(团队级)、Superpowers(开发者铁律)、GSD(极简上下文工程) 三大 SDD 框架的最佳实践。提供自适应流程选择决策树，路由到正确的子 skill。内嵌 Workflow Chain Protocol（SPEC→DEV→QA→COMMIT 四段链式衔接），确保工作流阶段之间不跳过门禁。任何涉及开发/实现/编码/重构/继续/推进等任务时自动加载。"
version: 2.0.0
triggers:
  - 开发工作流
  - 开发流程
  - 怎么开发
  - 怎么做
  - 开始开发
  - 开始实现
  - 开始编码
  - 开发规范
  - 工作流
  - workflow
  - 开发方法
  - 方法论
  - sdd
  - SDD 框架
  - 索引
  - 继续
  - 继续开发
  - phase
  - 下一阶段
  - 推进
  - 工作流链
  - workflow chain
  - chain
author: Emma (小玛)
license: MIT
metadata:
  hermes:
    tags:
      - workflow
      - development
      - methodology
      - index
      - superpowers
      - gsd
    category: dogfood
    skill_type: index
    design_pattern: index
depends_on:
  - sprint-planning
  - writing-plans
  - subagent-driven-development
  - test-driven-development
  - systematic-debugging
  - requesting-code-review
  - commit-quality-check
  - self-review
  - doc-alignment
  - deep-research
  - spike
  - learning-workflow
  - analysis-workflow
  - one-three-one-rule
  - problem-solving-sherlock
  - generic-dev-workflow
  - sdd-workflow
---

# 🧭 开发工作流索引 v1.0

> **整合 Superpowers · GSD 两大 SDD 框架 + Hermes 现有能力**
> 核心理念：**根据任务复杂度自适应选择流程深度，不搞一刀切，不搞企业级仪式感。**

---

## 〇、流程选择决策树 🎯

> **选好路径后，执行阶段统一走 `generic-dev-workflow`（通用开发工作流）的 7 步流程。**
> 本索引负责「选哪条路」，`generic-dev-workflow` 负责「怎么走」。

**在任何开发任务开始时，先走此决策树选择正确的工作流路径：**

```text
任务来了！
│
├── 🤔 「不确定怎么做」或「研究一下」
│   └── 走调研路径 → 见 §1
│
├── ⚡ 「改个小东西」或「快速功能」（1-3 文件，< 1 小时）
│   └── 走快速路径 → 见 §2
│
├── 🎯 「中等功能」（3-10 文件，1-3 天）
│   └── 走标准路径 → 见 §3
│
├── 🏗️ 「复杂项目」（10+ 文件，多天/多周）
│   └── 走完整路径 → 见 §4
│
├── 📋 「规划下个 Sprint」或「分析项目现状」
│   └── 走 Sprint 规划路径 → 见 §7
│
├── 🐛 「修 Bug」
│   └── 走调试路径 → 见 §5
│
├── 🔄 「重构/优化」
│   └── 走审查路径 → 见 §6
│
└── 📝 「需要先写 Spec」或「规范驱动开发」
    └── 走 SDD 路径 → 见 §8
```

### 🔍 Phase 0: pre_flight v2.0 门禁 — 所有路径的强制前序

**在走决策树之前，必须先执行 `pre_flight.py`。** 这是 P0 铁律 #11 的实践步骤。

```text
[BEFORE 任何操作 — 强制 pre_flight 门禁]
  1. 🛑 python3 ~/.hermes/scripts/pre_flight.py "<任务描述>"
     ├── Gate 1: 学习状态检查
     ├── Gate 2: SDD 门禁 — 复杂任务自动调用 spec-gate.py enforce
     └── Gate 3: 技能/包检测 — 自动检测 skill-creator 或 cap-pack 操作
  2. 结果：
     ├── ✅ PASS (exit 0) → 继续走决策树
     └── ❌ BLOCKED (exit 1) → 🛑 STOP！先处理阻塞项

[THEN 标准前序]
  1. 📡 skill_finder.py → 发现相关 skill → 自动加载
  2. 📋 [复杂任务] 写 todo 清单

[AFTER 任何变更]
  1. ✅ 自检（self-review）
  2. 🔍 文档一致性（doc-alignment）
  3. 📝 [有 git] 提交前检查（commit-quality-check）
  4. 🗂️ 经验沉淀（knowledge-ingest）
```
[AFTER 任何变更]
  1. ✅ 自检（self-review）
  2. 🔍 文档一致性（doc-alignment）
  3. 📝 [有 git] 提交前检查（commit-quality-check）
  4. 🗂️ 经验沉淀（knowledge-ingest）
```

---

## 一、调研路径 🔍 ← 从 0 到 1 的探索

### 决策条件
```text
「这个怎么做？」「研究一下」「可行性」「方案对比」
```

### 子阶段

| 阶段 | 加载的 Skill | 任务 | 产出物 |
|:----|:-------------|:-----|:-------|
| **0. 需求理解** | `deep-research` | SCQA 定义范围、明确受众 | 一句话问题定义 |
| **1. 广度搜索** | `deep-research` §Phase1 | 搜索 3-5 个方案，MECE 分类 | 候选清单 |
| **2. 深度验证** | `deep-research` §Phase2 | 价格/可行性交叉验证 | 验证矩阵 |
| **3. Spike 验证** | `spike` | 如果方案不确定 → 建 spike 原型 | spike/NNN-name/ |
| **4. 结构化分析** | `deep-research` §Phase3 | MECE 分类 + 对比矩阵 + 路线 | 分析报告 |

### 从调研进入开发
```
调研完成 → 向主人汇报可行性结论
    → 主人同意 → 进入 §2/§3/§4
    → 方向不对 → 回头重研
```

### 铁律
- 🔴 至少 2 轮搜索（广度+深度），禁止 1 轮定论
- 🔴 所有价格数据 ≥2 独立来源交叉验证
- 🔴 调研完成不等于开发开始 — **先汇报，等主人判断**

---

## 二、快速路径 ⚡ ← 小功能 / 单文件变更

### 决策条件
```text
「快速修复」「改一下」「小功能」
< 3 个文件，可 1 小时内完成
```

### 流程

```text
[1] 理解需求 → [2] 写计划 → [3] TDD 实现 → [4] 自检 → [5] 提交
   (思考)     (writing-plans)  (TDD)    (self-review)  (commit-check)
```

### 详细步骤

| 步骤 | Skill | 关键规则 |
|:----|:------|:---------|
| **1. 需求确认** | — | 问清楚改什么、不改什么 |
| **2. 写实施计划** | `writing-plans` | 每步 2-5 分钟，含文件路径+验证命令 |
| **3. 🔍 测试模式发现** | — | 扫同目录已有 fixture：`grep -rn \"FIXTURES_DIR\\|fixtures/\" tests/ 2>/dev/null` |
| **4. TDD 实现** | `test-driven-development` | 🔴 **先写失败测试 → 再写代码** |
| **5. 全量测试** | `terminal` (pytest) | 基线对比：只允许 NEW failures 阻止 |
| **6. 自我审查** | `self-review` | 实施前四问 + 任务交付验证清单 |
| **7. 文档对齐** | `doc-alignment` | 5 步对齐协议 |
| **8. 提交前检查** | `commit-quality-check` | P0 安全检查 + 文档一致性 |
| **9. Git 提交** | `git commit` | Conventional Commits 格式 |

### 铁律
- 🔴 `writing-plans` → `TDD` → `self-review` 顺序不可颠倒
- 🔴 没有先跑`test-driven-development`就写代码 → **删掉重写**
- 🔴 汇报前必须跑 `self-review` 和 `commit-quality-check`

---

## 三、标准路径 🎯 ← 中等复杂功能

### 决策条件
```text
3-10 个文件，涉及跨模块变更
需要规划但不需要完整项目仪式
```

### 流程

**执行阶段统一走 `generic-dev-workflow`（通用开发工作流）的 7 步流程。**
本索引定义「做什么」，`generic-dev-workflow` 定义「怎么做」。

```text
[Phase 1] 规划
    ├── 写 Spec / 实施计划 → writing-plans
    │   └── 如需要正式 Spec → 见 §8 SDD 规范路径
    └── 拆分为 3-8 个原子任务 → todo 清单

[Phase 2] 实现 ← 加载 generic-dev-workflow 按 7 步执行
    └── skill_view(name="generic-dev-workflow")
        ├── Step 3: 实施计划（writing-plans）
        ├── Step 4: TDD 实现（RED-GREEN-REFACTOR）
        └── 每个任务完成后 git commit

[Phase 3] 集成与验证 ← generic-dev-workflow Step 5-6
    ├── Step 5: 全量测试 + 基线对比
    ├── Step 6: 自我审查（self-review 场景 F）
    ├── 测试基础设施检查（P0 铁律 #10）
    └── 集成审查（检查跨任务一致性）

[Phase 4] 提交与对齐 ← generic-dev-workflow Step 7
    ├── doc-alignment → 5 步对齐协议
    ├── 🌐 HTML 报告对齐 — 检查生命周期报告是否反映最新文档状态
    │   ├── 如有 project-report.json → generate-project-report.py 自动同步
    │   └── 如手动维护 → grep 对比 HTML 状态与文档实际状态
    ├── commit-quality-check → P0 全通过
    ├── 经验沉淀 → knowledge-ingest
    └── git commit（代码+文档同次提交）
```

### 两种实现方式选择

| 方式 | 适用场景 | 优点 | 缺点 |
|:----|:---------|:-----|:-----|
| **A: 子代理驱动** | 3+ 任务可并行/独立 | 并行执行、独立上下文、自动审查 | 子代理结果需验证 |
| **B: 手动 TDD** | 任务强依赖/调试中 | 完全控制、无间接错误 | 串行、上下文累 |

### 铁律
- 🔴 规划阶段 `writing-plans` 不可跳过（即使觉得"很简单"）
- 🔴 实现阶段：**每个任务必须 > 0 行测试代码**
- 🔴 子代理完成任务后 → **必须验证其侧效果**（文件是否存在、服务是否运行）
- 🔴 文档与代码必须在**同一次提交**中

---

## 四、完整路径 🏗️ ← 复杂项目 / 多日开发

### 决策条件
```text
10+ 文件，跨多天/多人
新项目 从 0 到 1
需要完整的需求 → 设计 → 实现 → 复盘
```

### 流程 — 融合 BMAD 四阶段

```text
┌──────────────────────────────────────────────────┐
│ Phase 1: 分析（可选）                              │
│   ├── 领域研究       → deep-research §Phase 1     │
│   ├── Spike 可行性   → spike                      │
│   └── 产品简介       → bmad-create-prd (如需要)   │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│   ├── 需求理解       → SCQA 框架                   │
│   ├── Sprint 规划    → sprint-planning §1-5 分析    │
│   ├── 架构设计       → writing-plans / 架构文档    │
│   └── Epic/Story     → todo 拆分                  │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ Phase 3: 实现（迭代）                              │
│   └── 按 Sprint 循环                              │
│       ├── Sprint 规划 → todo 清单                 │
│       ├── 逐个 Story → 见 §3 标准路径 Phase 2      │
│       └── Sprint 结束 → 全量测试 + 审查            │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ Phase 4: 复盘与沉淀                                │
│   ├── 文档全部对齐     → doc-alignment            │
│   ├── 经验沉淀         → knowledge-ingest         │
│   ├── 知识库更新       → L2/L3 知识沉淀            │
│   └── 回顾总结         → 学习反思                 │
└──────────────────────────────────────────────────┘
```

### 完整路径说明

> ⚠️ **注**: BMAD Method 框架已从本环境删除（项目级框架）。以下路径中使用 GSD + Superpowers 替代 BMAD 的完整流程。

如果项目需要完整团队级流程，直接走 SDD 规范路径（见 §8）：

### 铁律
- 🔴 Phase 2（规划）不可跳过 — 「想到哪做到哪」是项目失败的根源
- 🔴 Phase 4（复盘）不可跳过 — 不总结等于白做
- 🔴 每次 Sprint 结束必须有明确的状态标记（completed/blocked/parked）

---

## 五、调试路径 🐛 ← Bug 修复

### 决策条件
```text
「有 Bug」「报错了」「运行不正常」
```

### 流程 — 融合 Superpowers + Sherlock

```text
[Phase 0] 冷静！不要慌
    └── 花 10 秒回答：在哪？要什么？卡在哪？

[Phase 1] 根因调查 ← 🔴 必须先做！不修症状！
    ├── 读错误信息 → 完整读！不跳过！
    ├── 复现 Bug → 稳定触发？
    ├── 查最近变更 → git log -p / git diff
    └── 追数据流 → search_files 溯源到源头

[Phase 2] 模式分析
    ├── 找工作示例 → 代码库里类似的正确代码
    ├── 对比差异 → 列出每一点差异
    └── 理解依赖 → 需要什么组件/配置/环境

[Phase 3] 假设与验证
    ├── 一个假设 → 「我猜是 X 导致 Y 因为 Z」
    ├── 最小改动 → 只改一行/一个变量
    ├── 验证 → 通过？→ 进 Phase 4。失败？→ 新假设
    └── 看不懂 → 说「我不懂 X」→ 查资料/问主人

[Phase 4] 修复与确认
    ├── 全量测试 → pytest -q
    └── verification-before-completion → 确认真修好了
```

### 加载的 Skill

| 阶段 | Skill | 作用 |
|:----|:------|:-----|
| **全部** | `systematic-debugging` | 4 阶段根因流程 |
| **全部** | `problem-solving-sherlock` | 通用问题解决（含诊断类型速查） |
| Phase 4 | `test-driven-development` | 先写失败测试再修 → 确认修复有效 |

### 铁律
- 🔴 **NO FIXES WITHOUT ROOT CAUSE** — 没找到根因就不准修！
- 🔴 一次只改一个变量 — 多个假设同时验证 = 什么都没验证
- 🔴 修复后必须确认（验证测试）—「我觉得好了」不算好

---

## 六、审查路径 🔄 ← 重构 / 质量审计

### 决策条件
```text
「重构一下」「代码审查」「质量检查」「优化」
```

### 流程

```text
[Phase 1] 代码审查
    ├── requesting-code-review → 安全扫描 + 质量门禁
    ├── commit-quality-check → P0/P1/P2 检查
    └── self-review → 场景 F 任务交付验证

[Phase 2] 深度审计（如需）
    ├── analysis-workflow → 代码库技术债审计（支持并行子代理4层扫描模式）
    ├── analysis-workflow §8 → 并行子代理审计（架构/代码质量/测试/文档同时扫）
    └── 如需第三方审查框架 → 使用 `analysis-workflow` 的并行子代理审计模式

[Phase 3] 修复与重构
    ├── 按优先级修复发现的问题
    └── 回归测试 → pytest 全绿
```

### 铁律
- 🔴 审查者在**独立的上下文**中执行 — 不要自己审自己的代码
- 🔴 子代理作为审查者 → 提供 Spec 原文 + 实现代码供其对比

### 🔍 实战经验：四层并行代码库审计

当需要对一个中大型 Python 项目做四层扫描审计时，使用 `delegate_task` 并行执行效率最高：

```text
[Phase 2] 深度审计（并行子代理模式）
    ├── 方式：delegate_task(max_concurrent_children=3，分两批)
    │
    │   第一批（3 个子代理并行）：
    │   ├── Layer 1: 架构层 — daemon.py 职责、线程安全、配置系统
    │   ├── Layer 2: 代码质量 — except:pass、类型标注、魔法数字
    │   └── Layer 3: 测试覆盖 — 覆盖矩阵、缺失模块、测试质量
    │
    │   第二批（前一批完成后立即启动）：
    │   └── Layer 4: 文档与基础设施 — README、ROADMAP、CI
    │
    └── 合并：boku 主会话收集 4 层报告 → 按 P0/P1/P2 分类排序

⚠️ delegate_task 默认 max_concurrent_children=3，最多同时 3 个子代理。
   4+ 任务时需分批次（3+1 或 2+2），不能一次提交 4 个及以上。

📎 完整可复用配方：`references/sra-audit-recipe.md`（含每层精准命令、分类模板、产出物模板）
```

---

## 七、Sprint 规划路径 📋 ← 项目分析 & 计划制定

### 决策条件
```text
「分析项目现状」「规划下个 Sprint」「敏捷开发计划」
「项目到哪了」「下一步做什么」
```

### 子阶段

| 阶段 | 加载的 Skill | 任务 | 产出物 |
|:----|:-------------|:-----|:-------|
| **1. 项目分析** | `sprint-planning` | Git 状态、测试健康、文档审计、代码质量、技术债 | 多维度分析报告 |
| **2. Backlog 生成** | `sprint-planning` | 从 ROADMAP/TECHDEBT 提取待办、优先级排序、容量规划 | Sprint Backlog |
| **3. 汇报确认** | `sprint-planning` | Dashboard 展示、建议 Sprint 顺序 | 规划报告 |
| **4. 进入开发** | `development-workflow-index` §2/§3/§4 | 确认后进入对应开发路径 | — |

### 铁律
- 🔴 Step 1-5 分析不可跳过 — 不做分析就做计划 = 拍脑袋
- 🔴 版本号一致性是 P0 — README/install.sh/ROADMAP 必须同步
- 🔴 汇报后等主人确认再开始开发 — 方向错了白做

---

## 八、SDD 规范路径 📝 ← Spec-Driven Development 全生命周期

### 决策条件
```text
「需要先写 Spec」「规范驱动开发」「创建 Story」「审批 Spec」
复杂任务（3+ 文件/跨模块），需要正式的需求 → 设计 → 实现 → 复盘
```

### 流程 — 六阶段 Spec 生命周期

由 `sdd-workflow` skill 驱动，spec-state.py 状态机管理：

```text
┌──────────────────────────────────────────────────┐
│ Phase 0: SDD 门禁检查（所有开发路径的强制前序）      │
│   └── sdd-workflow skill → spec-gate.py enforce    │
│       ├── PASS ✅ → 继续                           │
│       └── BLOCKED ❌ → 先创建 Spec                 │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ Phase 1: CREATE — 创建 Spec                        │
│   ├── 复制模板: templates/story-template.md        │
│   ├── 填充字段: story_id / AC / test_data / refs   │
│   ├── 初始化状态: spec-state.py create             │
│   └── 验证完整性: spec-gate.py verify              │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ Phase 2: REVIEW — 提交审阅                        │
│   ├── spec-state.py submit → 状态变为 review      │
│   └── 主人审阅 → approve 或 reject                │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ Phase 3: IMPLEMENT — 按 Spec 开发                  │
│   ├── spec-state.py architect → 开始架构设计       │
│   ├── spec-state.py plan → 开始实现计划            │
│   ├── spec-state.py implement → 开始技术实现       │
│   ├── 每个 AC 对应一个测试（TDD）                   │
│   └── 逐个 Task 实现 + 验证                        │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ Phase 4: VALIDATE — 验证与对齐                    │
│   ├── pytest 全量测试                             │
│   ├── doc-alignment --verify                     │
│   └── commit-quality-check                       │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ Phase 5: COMPLETE → ARCHIVE — 完成归档            │
│   ├── spec-state.py complete                     │
│   └── spec-state.py archive                      │
└──────────────────────────────────────────────────┘
```

### 参考文档

| 文档 | 位置 | 用途 |
|:-----|:-----|:------|
| SDD 成熟度指南 | `references/sdd-maturity-guide.md` | SDD 三大框架对比 + 原则速查 |
| SDD 工作流 skill | `sdd-workflow` | 状态机 + 门禁 + 模板（完整可执行） |
| Story 模板 | `templates/story-template.md`（sdd-workflow） | 标准 Story Spec 格式 |
| Epic 模板 | `templates/epic-template.md`（sdd-workflow） | Epic 级 Spec 格式 |
| SDD 生命周期 | `references/sdd-lifecycle.md`（sdd-workflow） | 六阶段完整指南 |
| SDD 已知缺口与路线图 | `references/sdd-known-gaps-and-roadmap.md`（sdd-workflow） | ⚠️ 当前流程审计 + 改进方案（需求澄清/技术调研/质量检查） |

### 已知局限

当前 SDD 流程（v1.0）存在以下已识别的缺口，参见 `sdd-workflow` §六：
1. **Gap A**: CREATE 前缺乏需求澄清阶段
2. **Gap B**: CREATE 前缺乏技术调研阶段
3. **Gap C**: CREATE 后缺乏质量检查阶段

改进路线图已在 `sdd-workflow` 中记录，待主人确认后实施。

### 铁律
- 🔴 P0 铁律 #11: 复杂任务没有获批 Spec 就写代码 = Vibe Coding
- 🔴 每个 AC 必须可验证（自动化测试或手动检验），不可验证的 AC = 废纸
- 🔴 Spec 和代码必须在同一次提交中
- 🔴 变更代码前必须先更新 Spec（Spec-Anchored 核心约束）

---

## 九、铁律体系 ⚖️ — 三大框架原则统一

### 🔴 P0 铁律（不可违背）

| # | 铁律 | 来源 | 违背后果 |
|:-:|:-----|:-----|:---------|
| 1 | **没有需求对齐就写代码 → 废品** | BMAD Phase2 | 需求不稳就开干 → 返工 |
| 2 | **没有根因就修 Bug → 掩耳盗铃** | Superpowers | 症状修复→Bug复发 |
| 3 | **没有失败测试就写代码 → 盲目** | Superpowers TDD | 不知道测什么 |
| 4 | **没自检就汇报 → 不负责** | Hermes self-review | 主人发现遗漏→信任下降 |
| 5 | **代码改了文档不同步 → 污染** | Hermes doc-alignment | 下次决策基于旧信息 |
| 6 | **代码+文档不在同一次提交 → 丢失** | BMAD + Hermes | 版本不一致 |
| 7 | **跳过安全检查就提交 → 危险** | commit-quality-check | 凭泄漏/硬编码 |
| 8 | **调研完直接开干不汇报 → 越权** | deep-research v2.1 | 方向不对白做 |
| **9** | **没验证代码现实就信文档 → 分析误差** | Hermes SRA | 基于过时断言做计划→方向偏航 |
| **10** | **没检查已有测试基础设施就写测试 → 碎片化** | Hermes SRA (Sprint 20) | 重复造轮、CI 环境差异、测试数据不真实 |
| **11** | **没批准 Spec 就写代码 → Vibe Coding** | SDD 元研究 (2026-05-11) | 方向不对白做、上下文丢失、不可审计 |
| **12** | **阶段间 gate 不通过就推进 → 工作流跳过** | Workflow Chain (2026-05-14) | SPEC未完成就开发 → 无上下文；DEV未测试就QA → 假阳性；QA未通过就提交 → 质量下降 |

> **铁律 #10 详解**: 在任何项目中写新测试前，必须先做「测试模式发现」:
> 1. 扫描 `tests/` 下已有文件的 Fixture 引用模式（`grep -rn "FIXTURES_DIR\|fixtures/" tests/`）
> 2. 检查 `tests/fixtures/` 目录是否存在已有的测试数据
> 3. 确认新测试能复用现有 Fixture，而非引入新的运行时依赖
> 4. **不要幻觉文件/函数存在** — 引用前先 `read_file` 或 `grep -rl` 确认
> 5. **参考 `tests/TEST-DATA-MANIFESTO.md`** 了解所有可用 fixture
> 
> **实战案例**: SRA 项目的 `tests/fixtures/` 中有 317 个从真实 Hermes 技能提取的 SKILL.md，
> 但 `test_contract.py` 开发时没使用，导致 CI 环境失败。
> 而同目录下 `test_matcher.py` 已经正确使用了 `FIXTURES_DIR` 模式。
> 教训：**眼睛看到了不等于思维复用了** — 要把检查已有模式变成显式步骤。
> 
> **🔴 机械门禁（2026-05-11 新增）**:
> 以下检查必须在 pre-flight 阶段自动执行：
> ```bash
> # 门禁 1: 如果有 fixture 目录，新测试禁止引用运行时依赖
> if [ -d "tests/fixtures" ]; then
>     grep -rn "hermes/skills\|~/.hermes" tests/ 2>/dev/null && {
>         echo "❌ BLOCKED: 测试引用了运行时依赖 ~/.hermes/skills！"
>         echo "   请使用 tests/fixtures/ 替代"
>         exit 1
>     }
> fi
> 
> # 门禁 2: 验证 fixture 完整性（数据源不退化）
> python3 -c "
> import os
> d = 'tests/fixtures/skills'
> if os.path.isdir(d):
>     count = sum(1 for _,_,files in os.walk(d) for f in files if f == 'SKILL.md')
>     assert count >= 300, f'Fixture 退化: {count} < 300'
>     print(f'✅ {count} valid fixture skills')
> "
> ```
> 这两个门禁是 **可自动执行的确定性检查**，不依赖 AI 的判断力。
> 详见 `tests/TEST-DATA-MANIFESTO.md`。

> **铁律 #11 详解 — SDD: 没有批准的 Spec 就不写代码**:
> 这是从 Vibe Coding 到 Spec-Driven Development 的核心转变。
> 
> **三种 SDD 模式**（按规范强度递增）:
> | 模式 | 描述 | 适用场景 |
> |:-----|:------|:---------|
> | **Spec-First** | 每个任务写 Spec，实现后可丢弃 | 快速 prototype |
> | **Spec-Anchored** 🔥 | Spec 是活的，变更先改 Spec 再改代码 | **推荐（多数项目）** |
> | **Spec-as-Source** | Spec 是唯一制品，代码是派生品 | 实验阶段 |
> 
> **Spec 三不原则（核心约束）**:
> 1. 🚫 **Specs 不可跳过** — 复杂任务没有获批 Spec 就写代码 = P0 违规
> 2. 🚫 **Specs 不可静默** — 变更必须先更新 Spec，再改代码
> 3. 🚫 **Specs 不可漂移** — 使用 doc-alignment 检测 Spec 与代码的偏差
> 
> **一个合格 Spec 必须包含**:
> - 用户故事（As a / I want / So that）
> - 验收标准（Acceptance Criteria，每个可验证）
> - 测试数据契约（test_data 字段，声明 fixture 来源）
> - 引用链（spec_references，追溯上游上下文）
> - 明确不做的范围（out_of_scope，防止 scope creep）
> 
> **Spec 完整生命周期**:
> ```text
> CREATE → APPROVE → IMPLEMENT → VALIDATE → MERGE → MAINTAIN
>  写      主人审阅   TDD 实现   测试+验证   代码+文档   漂移检测
> ```
> 
> **实战模板**: 见 `docs/STORY-TEMPLATE.md`（SRA 项目标准 Story Spec）。
> **SDD 深度参考**: `references/sdd-maturity-guide.md` — 三大框架对比表、成熟度模型、Spec 5 要素、生命周期。

### 🟡 P1 准则（建议遵守）

| # | 准则 | 来源 | 说明 |
|:-:|:-----|:-----|:-----|
| 1 | 每步 2-5 分钟 | Superpowers | 防止规划太粗 |
| 2 | 基线对比测试 | Superpowers | stash→baseline→apply |
| 3 | 原子 Git 提交 | GSD | 每任务独立提交 |
| 4 | 审查用独立子代理 | Superpowers | 不自己审查自己 |
| 5 | 实施前四问 | Hermes self-review | 方案可被 AI 执行？ |

### 🟢 P2 建议（最佳实践）

| # | 实践 | 来源 |
|:-:|:-----|:-----|
| 1 | MECE 分类 | deep-research |
| 2 | 结论先行 (BLUF) | deep-research |
| 3 | 实施计划写完整代码 | writing-plans |
| 4 | Process File 不累积上下文 | analysis-workflow |
| 5 | 自适应粒度：快/中/完整 | BMAD 三轨 |

---

## 十、Skill 对照总表 📋

### 按阶段分类

| 阶段 | Skill 名称 | 作用 | 来源框架 |
|:----|:-----------|:-----|:---------|
| **调研** | `deep-research` | 深度调研工作流（MECE+SCQA+BLUF） | Hermes |
| **调研** | `spike` | 原型快速验证 | GSD |
| **规划** | `sprint-planning` | 项目分析 + Sprint Backlog 生成 | Hermes |
| **规划** | `writing-plans` | 编写实施计划（含全部代码） | Superpowers |
| **规划** | `one-three-one-rule` | 1-3-1 方案对比决策 | Hermes |
| **规划** | `information-decomposition` | 信息分解决策 | Hermes |
| **实现** | `test-driven-development` | RED-GREEN-REFACTOR 循环 | Superpowers |
| **实现** | `subagent-driven-development` | 子代理驱动+双阶段审查 | Superpowers |
| **审查** | `requesting-code-review` | 安全扫描+质量门禁 | Superpowers |
| **审查** | `commit-quality-check` | 提交前一致性+安全检查 | Hermes |
| **审查** | `self-review` | 通用自我审查 | Hermes |
| **调试** | `systematic-debugging` | 4 阶段根因调试 | Superpowers |
| **调试** | `problem-solving-sherlock` | 通用问题解决 | Hermes |
| **调试** | `bmad-correct-course` |  Sprint 中途纠偏 | BMAD |
| **文档** | `doc-alignment` | 5 步文档对齐协议 | Hermes |
| **数据** | `analysis-workflow` | 大文件分析+Map-Reduce | Hermes |
| **学习** | `learning-workflow` | 学习状态机+反射门禁 | Hermes |
| **质量** | `bmad-check-implementation-readiness` | 实施就绪门禁 | BMAD |
| **测试** | `dogfood` | Web 应用系统性 QA | Hermes |
| **测试** | `bmad-tea` | 测试架构（企业级） | BMAD |
| **CI/CD** | `references/python-ci-cd-patterns.md` | CI/CD 配置模式 + 常见问题排查 | Hermes |
| **AI** | `bmad-method` | 完整 BMAD 框架入口 | BMAD |

### 按框架来源分类

| 框架 | 核心贡献 | Hermes 已覆盖 |
|:-----|:---------|:--------------|
| **BMAD Method** | 团队级流程、上下文工程、Party Mode | 部分（缺 Step-File 架构） |
| **Superpowers** | 铁律体系、Two-Stage Review、Baseline-Aware | 大部分（缺自动化 Two-Stage） |
| **GSD** | 极简上下文工程、Parallel Waves | 少（缺 PROJECT.md 链式文件） |

---

## 十一、启动模板 🚀

### 「开始一个新功能」—— 以"添加用户注册功能"为例

```text
主人说：「做一个用户注册功能」
→ 决策树 → 标准路径（3-10 文件）

[Phase 1] 规划
    1. 确认需求：「主人，注册功能需要邮箱+密码+昵称三个字段？
       验证码？需要邮箱验证吗？」
    2. skill_view(name="writing-plans") → 写实施计划
       ├── Task 1: 创建 User 模型（含 email/password_hash/nickname）
       ├── Task 2: 创建注册 POST /api/register 端点
       ├── Task 3: 添加密码哈希工具函数
       └── Task 4: 添加输入验证中间件

[Phase 2] 实现（子代理驱动）
    3. skill_view(name="subagent-driven-development")
       └── 逐个 Task 实现 + Spec 审查 + 质量审查

[Phase 3] 验证
    4. pytest tests/ -q → 全量测试
    5. skill_view(name="self-review") → 场景 F
    6. skill_view(name="doc-alignment") → 更新 API 文档
    7. skill_view(name="commit-quality-check") → 提交前检查

[Phase 4] 提交
    8. git add -A && git commit -m "feat: add user registration endpoint"
    9. 向主人汇报（含检查报告）
```

### 「修复登录 Bug」—— 以"用户登录报 500"为例

```text
主人说：「登录接口报 500 了」

→ 决策树 → 调试路径

[Phase 0] 冷静
    「在 login endpoint，用户 POST 密码时报 500，
     预期返回 token，实际返回 500 Internal Server Error」

[Phase 1] 根因
    1. 读错误 → read_file 看日志
    2. 复现 → curl -X POST /api/login -d '{"email":"test@test.com","pass":"123"}'
    3. 查变更 → git log --oneline -5
    4. 追数据流 → 发现 password_hash 字段在 User 模型中不存在
       ← 根因：新模型迁移没跑，数据库表缺字段！

[Phase 2] 修复
    5. alembic upgrade head → 跑迁移
    6. 写测试 → test_login_with_valid_credentials
    7. 验证通过 → pytest -k test_login

[Phase 3] 确认
    8. curl 确认 200 OK
    9. 汇报：「根因是数据库迁移没执行，已修复」
```

### 「代码审查」—— 批量审计

```text
主人说：「帮我整体 review 一下这次的代码」

→ 决策树 → 审查路径

[Phase 1] 快速扫描
    1. skill_view(name="requesting-code-review")
       ├── git diff --cached → 安全扫描
       └── pytest -q → 基线对比

[Phase 2] 深度审计
    2. skill_view(name="analysis-workflow")
       └── 代码库技术债审计 → references/codebase-tech-debt-audit.md

[Phase 3] 报告
    3. 汇总为结构化报告：
       ├── 🔴 严重问题 (0 个) ✓
       ├── 🟡 重要问题 (2 个)
       │   ├── 硬编码版本号 → 改为 pyproject.toml 引用
       │   └── 裸 except → 指定异常类型
       └── 🟢 建议 (3 个) → 按需处理
    4. 汇报
```

---

## 附录：三大框架设计哲学对比

| 维度 | BMAD Method | Superpowers | GSD |
|:-----|:-----------|:------------|:-----|
| **目标受众** | 团队/多人项目 | 有纪律的个人开发者 | Solo developer |
| **设计哲学** | 结构化、角色化、流程化 | 铁律驱动、不可违背原则 | 极简、系统复杂用户简单 |
| **流程深度** | 深（4 阶段、102 skill） | 中（7 步、约 15 skill） | 浅（6 命令、约 10 文件） |
| **上下文策略** | Step-File JIT + TOML 注入 | 子代理隔离 + 计划文件 | 结构化文件链 |
| **质量保障** | Implementation Readiness + Code Review | Two-Stage Review + TDD | Verify Work + Forensics |
| **弱点** | 太重，小项目杀鸡用牛刀 | 铁律有时过于 rigid | 缺协作/团队支持 |
| **最适合** | 完整产品开发 | 有纪律的功能开发 | 快速 MVP/独立开发 |

---

## 十二、Reality Check — 分析前对齐协议 🔍

> **P0 铁律 #9 的实践指南**: 在任何「分析项目现状」或「制定计划」的任务中，
> 必须先验证代码现实，再读文档。文档描述的是过去，代码描述的是现在。

### 适用场景

| 场景 | 示例 |
|:-----|:------|
| 分析项目进度 | 「项目现在到哪了？」「帮我看看当前的进度」 |
| 制定开发计划 | 「规划下一个 Sprint」「下一步做什么」 |
| 技术债评估 | 「代码质量如何？」「有哪些技术债」 |
| 版本发布准备 | 「检查一下可以发布了吗」 |

### 三不原则

```text
不直接读文档         → 先看 git log / 代码
不直接信断言         → 先验证（测试数、文件存在性、版本号）
不跳过验证就分析     → 这是 P0 铁律 #9，不可违背
```

### 五步验证流程

| 步骤 | 操作 | 验证什么 | 发现过的问题 |
|:-----|:-----|:---------|:------------|
| **1. git log** | `git log --oneline -30 \| head -15` | 最近做了什么、有哪些未推送的提交 | 文档说某功能未实现，但 commit 显示已做 |
| **2. pytest 计数** | `pytest --collect-only -q \| tail -1` | 实际测试数 vs 文档声称的测试数 | 文档说 174 测试，实际 290 |
| **3. 文件存在性** | `ls file1 file2` | 文档声称不存在的文件 | 文档说 test_dropin.py 不存在，实际存在 |
| **4. 版本验证** | `python -c "from pkg import __version__"` | 实际版本 vs 文档版本 | pyproject.toml 是 v1.2.1，__init__ 已是 v1.3.0 |
| **5. doc-alignment** | `generate-project-report.py --verify` | 数据源与代码一致性 | 版本号漂移、测试数不匹配 |

### 验证通过后

```text
✅ 五步通过 → 可以安全地使用文档进行分析
⚠️ 发现差异 → 以代码现实为准，在分析中注明差异
❌ 重大差异 → 先同步文档，再继续分析
```

### 实战教训（SRA Sprint 3 案例）

在 SRA Sprint 3 开始时，boku 直接读取了 TECHDEBT-ANALYSIS.md 并假设其内容是最新的，结果：

| 文档声称 | 代码现实 | 误差代价 |
|:---------|:---------|:---------|
| test_dropin.py 不存在 | ✅ 290 行测试已存在 | Sprint 计划多估了 2h |
| A-7 线程安全未修复 | ✅ SRA-003-18 已修 | 做了不必要的分析 |
| daemon.py 类型标注 33% | ✅ SRA-003-19 已修至 84% | 低估了代码质量 |

**教训**: `git log --oneline -30` 本应在第一步执行——它能直接看到「SRA-003-18: fix thread safety」「SRA-003-19: add type annotations」等 commit，从而避免所有上述误差。

### 关联 Skill

| Skill | 用途 |
|:------|:------|
| `sra-dev-workflow` | SRA 项目专属开发工作流（版本管理 + CI/CD + Reality Check） |
| `doc-alignment` | 文档对齐协议（含 project-report.json 数据驱动管理） |
| `sprint-planning` | Sprint 规划方法论（Reality Check 是前置步骤） |

## 📚 参考深度阅读

| 文件 | 用途 |
|:-----|:------|
| `references/sdd-maturity-guide.md` | SDD 三大框架对比 + 成熟度模型 |
| `references/sra-audit-recipe.md` | SRA 四层并行审计配方 |
| `references/python-ci-cd-patterns.md` | CI/CD 配置模式 + 常见问题排查 |
| `references/skill-finder-recovery.md` | **skill_finder.py 91-byte stub 恢复指南** |
| `references/workflow-enforcement-research.md` | **业界方案汇总（ToolGuards/MI9/Claude Hooks 等推模式门禁研究）** |

## 十三、来源与参考 📚

| 框架 | 来源 | 版本 |
|:-----|:-----|:-----|
| **BMAD Method** | https://github.com/bmadcode/BMAD-METHOD | v6.6.0 (102 skills) |
| **Superpowers** | https://github.com/obra/superpowers | Latest (176K stars) |
| **GSD** | https://github.com/gsd-build/get-shit-done | v1.30.0+ |
| **Hermes Agent** | https://github.com/NousResearch/hermes-agent | Bundled with system |

### 验证方式

本索引 skill 中引用的所有框架内容均通过以下方式验证：
1. **BMAD Method**: 通过本地安装的 `bmad-method` skill（102 子 skill）实际验证 + 官方 Mintlify 文档 + GitHub 源码
2. **Superpowers**: 通过本地安装的改编 skill（`writing-plans`, `subagent-driven-development`, `test-driven-development`, `systematic-debugging`, `requesting-code-review`）实际使用验证 + GitHub README
3. **GSD**: 通过官方文档 + GitHub 源码 + npm 包 README 验证
4. **Hermes 内部 skill**: 通过 `skill_view()` 实时加载验证

所有引用内容均来源于实际部署的代码和文档，非 AI 臆造。

---

## 十四、Workflow Chain Protocol 🚦 — 工作流链式衔接

> **核心理念**: 三阶段（SDD→DEV→QA）不是孤立的文档，而是**可执行的状态链**。每个阶段之间的 transition 必须通过 gate 检查，防止凭感觉跳过。

### 14.1 链定义

```
┌──────────┐    Gate: spec    ┌──────────┐    Gate: tests   ┌──────────┐    Gate: QA     ┌────────┐
│  SPEC    │─── approved ──▶│  DEV     │─── all pass ──▶│  QA      │─── L0-Lx ok ──▶│ COMMIT │
│  sdd-    │    + chain      │  generic-│    + chain     │  generic-│    + chain     │ 对齐+  │
│  workflow│    advance      │  dev     │    advance     │  qa      │    advance     │ 提交   │
│  spec-   │                 │  -work   │                │  -work   │                │        │
│  state.py│                 │  -flow   │                │  -flow   │                │        │
└──────────┘                 └──────────┘                └──────────┘                └────────┘
     ↑                            ↑                           ↑
  chain-state.py             Step 5 自动                  chain-state.py
  advance → gate             QA 门禁嵌入                  advance → gate
```

**实现文件**（项目根目录）:
| 文件 | 用途 |
|:-----|:------|
| `scripts/chain-state.py` | 链状态机 — `start/advance/status/check/reset` |
| `scripts/chain-gate.py` | 门禁检查器 — `check_spec/check_dev/check_qa/check_commit` |
| `scripts/phase-gate.py` | Phase 门禁 — 检查 Epic Phase 是否按顺序推进 |
| `docs/workflow-chain.yaml` | 链定义配置（stages/gates/hooks） |
| `docs/chain-state.json` | 链状态持久化（chain-state.py 自动管理） |

### 14.2 使用方式

```bash
# 1. 启动链（从 SPEC 开始）
python3 scripts/chain-state.py start EPIC-004 SPEC

# 2. 查看链状态
python3 scripts/chain-state.py status EPIC-004

# 3. 推进到下一阶段（自动跑 gate）
python3 scripts/chain-state.py advance EPIC-004

# 4. 强制推进（跳过 gate，仅调试用）
python3 scripts/chain-state.py advance EPIC-004 --force

# 5. 单独检查 gate
python3 scripts/chain-gate.py check_spec STORY-4-6
python3 scripts/chain-gate.py check_qa

# 6. 查看所有活跃链
python3 scripts/chain-state.py list

# 7. Phase 门禁（Epic 内阶段推进）
python3 scripts/phase-gate.py start EPIC-004 Phase-2
python3 scripts/phase-gate.py list EPIC-004
```

### 14.3 自动钩子

| 过渡 | Gate 检查 | 通过后自动 |
|:-----|:----------|:-----------|
| SPEC→DEV | Story 已批准 | 加载 `generic-dev-workflow` |
| DEV→QA  | 测试全绿 + self-review | 加载 `generic-qa-workflow` |
| QA→COMMIT | 交叉引用 + 项目状态一致 | 加载 `generic-dev-workflow` Step 7 |

### 14.4 铁律

- 🔴 **P0**: 没有通过 gate 就进入下一阶段 = 工作流跳过 = 需回退
- 🔴 **P0**: SDD 未批准就写代码 = 先创建 Spec 送审
- 🔴 **P1**: `chain-state.py advance` 必须在每个阶段完成后执行
- 🔴 **P1**: Phase gate 禁止跳过未完成的 Phase（如 Phase-0 未完成就进 Phase-2）

### 14.5 与 SRA 的关系

SDD/DEV/QA workflows 的 triggers 已补充延续关键词（`继续` `phase` `下一阶段` `continue`），确保用户说「继续」时 SRA 能推荐对应 workflow。如果 SRA 未推荐：
1. 检查 `sra coverage | grep <skill>` → `covered=true`？
2. 运行 `sra refresh` 刷新索引
3. 如果 skill 是新建或刚修改 triggers → 需要 refresh 才能生效

---

## 十五、常见陷阱与恢复模式

### 15.1 91-byte 脚本 Stub 腐败（learned 2026-05-14）

**症状**: `skill_finder.py` 或其他 learning-workflow 脚本仅 91 字节，内容只剩 `print(f'{script_name} OK')`。
**根因**: `write_file` 或 `patch` 操作目标文件时，意外覆盖了核心脚本。
**检测**: `wc -c ~/.hermes/skills/learning-workflow/scripts/skill_finder.py` → 若为 91 则 stub。
**恢复**:
```bash
# 从 profile 备份复制
cp ~/.hermes/profiles/research/skills/learning-workflow/scripts/skill_finder.py \
   ~/.hermes/skills/learning-workflow/scripts/skill_finder.py
# 或从其他未损坏的 profile
cp ~/.hermes/profiles/experiment/skills/learning-workflow/scripts/skill_finder.py \
   ~/.hermes/skills/learning-workflow/scripts/skill_finder.py
```
**预防**: 核心脚本 git commit 后不要未经验证的 `write_file` 或 `cp` 覆盖。

### 15.2 SRA 推荐为空（阶段性关键词缺失）

**当用户说「继续」「下一步」「推进」时 SRA 无推荐**：
- 检查对应 workflow 的 triggers 是否包含延续类关键词
- 补充后在 SRA 中运行 `sra refresh` 使新 triggers 生效
- SRA 四维匹配中词法维度占 40%——triggers 是最高效的匹配改进点

### 15.3 工作流链不一致

**症状**: chain-state.json 中的状态与 project-state.yaml 中的 Story 状态不一致。
**解决**: 
```bash
python3 scripts/chain-state.py reset EPIC-004  # 重置链
python3 scripts/chain-state.py start EPIC-004 SPEC  # 重新开始
# 然后 chain-state.py advance 逐步推进，确保每步 gate 通过
```

---

## 更新记录

| 版本 | 日期 | 变更 |
|:-----|:-----|:------|
| 2.1.0 | 2026-05-14 | 新增 §14 Workflow Chain Protocol + §15 常见陷阱与恢复模式 + P0铁律 #12 |
| 1.2.0 | 2026-05-11 | 新增 §7 Sprint 规划路径 + `sprint-planning` skill 引用 |
