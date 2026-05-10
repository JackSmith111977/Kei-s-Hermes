---
name: bmad-method
description: "BMad Method (Build More Architect Dreams) - 全生态 AI 驱动开发框架。含 BMM(敏捷开发)、BMB(模块构建)、TEA(测试架构)、BMGD(游戏开发)、CIS(创新智能) 五大模块共 102 个 Skill。项目开发、功能实现、Bug修复等任务自动触发 BMad 工作流。"
version: 2.3.0
triggers:
  # === 核心启动词 ===
  - bmad
  - bmad-method
  - bmm

  # === 项目开发 / 功能实现 ===
  - 项目开发
  - 软件开发
  - 功能开发
  - 功能实现
  - 实现功能
  - 开发功能
  - 开发项目
  - 从 0 到 1
  - 新项目
  - 构建项目
  - 搭建项目
  - 开发流程
  - 开发工作流
  - 开发规范

  # === 代码实现 ===
  - 写代码
  - 编码
  - 实现这个
  - 实现模块
  - 实现 feature
  - 搞开发

  # === Bug 修复 / 问题解决 ===
  - bug修复
  - 修bug
  - 修复bug
  - 修复问题
  - 出了bug
  - 有问题
  - 改bug
  - debug

  # === 重构 / 优化 ===
  - 重构
  - 代码重构
  - 优化代码
  - 代码优化
  - 重写
  - 代码重写

  # === 需求与分析 ===
  - 产品需求
  - 需求文档
  - 产品需求文档
  - PRD
  - 需求分析
  - 写文档
  - 分析需求
  - 产品规划
  - 需求拆解

  # === 架构设计 ===
  - 架构设计
  - 系统设计
  - 技术选型
  - 设计架构
  - 方案设计
  - 技术方案
  - 系统架构

  # === 项目管理 / 敏捷 ===
  - 敏捷开发
  - 敏捷
  - 史诗故事
  - epic
  - user story
  - 用户故事
  - 冲刺
  - sprint
  - 项目规划
  - 项目排期
  - 项目流程
  - 开发流程
  - 迭代
  - 迭代开发
  - sprint规划
  - 回顾

  # === 代码评审 ===
  - 代码评审
  - 代码审查
  - code review
  - 审查代码
  - 评审代码

  # === 测试 ===
  - 测试策略
  - 测试设计
  - 测试框架
  - 单元测试
  - 自动化测试
  - 测试架构
  - tea
  - test architect
  - 测试计划

  # === 模块构建 ===
  - bmb
  - 构建模块
  - 模块构建

  # === 游戏开发 ===
  - gds
  - game dev
  - 游戏开发
  - 游戏设计
  - GDD

  # === 创新与设计思维 ===
  - cis
  - creative intelligence
  - 头脑风暴
  - 设计思维
  - 创新策略
  - 问题解决
  - 故事叙述

  # === 通用开发词汇（低优先级匹配） ===
  - 开发
  - 编程
  - coding
  - implement
  - implementation
  - 做项目
  - 写程序
depends_on:
  - skill-creator
  - writing-plans
  - commit-quality-check
design_pattern: Pipeline
skill_type: Tool Wrapper
---

# 🐎 BMad 全生态 · AI 驱动开发框架 v2.2

> **核心理念**：AI 不是简单的聊天机器人，而是结构化的**专家协作团队**。BMad 通过明确的角色分工和阶段化流程，引导用户完成从构思到落地的全过程。
> **安装版本**：v6.6.0 (全量安装)
> **技能总数**：102 个独立 Skill
> **核心路径**：`~/.hermes/skills/bmad-method/all-skills/`
> **配置路径**：`~/.hermes/skills/bmad-method/_bmad/`
> **用户配置**：`_bmad/config.user.toml` (language=Chinese, user=boku)

---

## 🎯 自动触发场景与决策树

当主人触发本 Skill（任何 triggers 匹配），boku 按以下决策树判断走 BMad 工作流的哪个路径：

```
主人消息 → 匹配 triggers？
  ├── 项目开发/功能实现/写代码类
  │   ├── 复杂(10+ stories) → 走 BMad 完整流程
  │   │   └── bmad-create-prd → bmad-create-architecture
  │   │       → bmad-create-epics-and-stories
  │   │       → bmad-check-implementation-readiness
  │   │       → bmad-sprint-planning
  │   │       → 循环: create-story → dev-story → code-review
  │   │       → bmad-retrospective
  │   ├── 中等(3-10 stories) → 走简化 BMad
  │   │   └── bmad-create-prd → bmad-create-epics-and-stories
  │   │       → bmad-sprint-planning → dev-story 循环
  │   └── 小功能/快速开发(1-3 stories) → bmad-quick-dev
  │
  ├── Bug修复/问题排查类
  │   ├── 简单bug？ → 直接修复（不走 BMad）
  │   └── 复杂/系统性问题？ → bmad-correct-course + bmad-dev-story
  │
  ├── 重构/优化类
  │   └── → bmad-code-review + bmad-review-adversarial-general + bmad-dev-story
  │
  ├── 需求/文档/分析类
  │   └── → bmad-create-prd / bmad-edit-prd / bmad-validate-prd / bmad-domain-research
  │
  ├── 架构设计/方案类
  │   └── → bmad-create-architecture / bmad-technical-research
  │
  ├── 代码评审类
  │   └── → bmad-code-review / bmad-review-edge-case-hunter
  │
  ├── 测试类
  │   └── → bmad-tea（TEA 测试架构总入口）
  │
  ├── 项目流程管理
  │   ├── 启动Sprint → bmad-sprint-planning
  │   ├── 查进度 → bmad-sprint-status
  │   ├── 回顾 → bmad-retrospective
  │   └── 出问题 → bmad-correct-course
  │
  ├── 游戏开发类
  │   └── → gds-* 系列（加载 gds-agent-game-designer 等）
  │
  └── 创新/头脑风暴类
      └── → bmad-brainstorming / bmad-cis-* 系列
```

> **核心原则：**
> - **简单任务（单文件改bug/加小功能）** → 不需要 BMad，直接干喵
> - **复杂任务（多文件/新功能/重构思）** → 走 BMad 工作流
> - **拿不准** → 走 BMad，宁可多一步流程，不跳过喵！

---

## 🎯 三轨自适应规划 (Scale-Adaptive Planning)

BMad 核心创新之一：根据项目复杂度自动调整规划深度。

| 轨道 | 故事量 | 阶段 | 规划时间 | 仪式级别 |
|:-----|:------:|:-----|:--------:|:--------:|
| **Quick Flow** ⚡ | 1-15 | quick-spec → quick-dev | 15-30min | 低（无Sprint） |
| **BMad Method** 🎯 | 10-50+ | PRD+UX+Arch+Epics | 2-8h | 中（Sprint/Review/Retro） |
| **Enterprise** 🏢 | 30+ | 全流程+安全/合规 | 1-3周 | 高（质量门禁） |

**自适应机制**：
- **条件阶段**：Quick Flow 跳过 Analysis/Solutioning
- **产物粒度**：单 tech-spec → 多页架构文档
- **仪式级别**：从无 Sprint → 完整项目管理
- **自动范围检测**：工作流内置范围不匹配警告

---

## 📋 完整流程速查表（含一致性检测）

### 场景 A: 新项目开发（完整 BMad Method）

```
启动 → bmad-create-prd → bmad-create-architecture
     → bmad-create-epics-and-stories
     → bmad-check-implementation-readiness
     → bmad-sprint-planning
     → 逐个 Story: create-story → dev-story → code-review
     → ⚡ 一致性检测: 加载 commit-quality-check 做文档/安全/范围自检
     → bmad-retrospective → 经验沉淀
```

### 场景 B: 小功能 / Bug 修复（Quick Flow）

```
bmad-bmm-quick-spec → bmad-bmm-quick-dev
→ ⚡ 一致性检测: commit-quality-check（完成即检，不等提交）
```

### 场景 C: 已有项目改造（Brownfield）

```
bmad-bmm-generate-project-context → 按场景 A 或 B
```

### 场景 D: 不知道下一步

```
bmad-help ⭐ — 智能导航，告诉下一件事
```

---

## 📦 五大模块总览

| 模块 | 全称 | 版本 | 技能数 | 定位 |
|:---|:---|:---|:---|:---|
| **BMM** | BMad Method | 6.6.0 | 49 | 敏捷 AI 驱动开发（核心） |
| **BMB** | BMad Builder | 1.7.0 | 2 | 元模块 — 创建自定义 Agent 和模块 |
| **TEA** | Test Architect | 1.15.1 | 10 | 企业级测试策略与自动化 |
| **BMGD** | Game Dev Studio | 0.4.0 | 36 | 游戏开发全流程 (Unity/Unreal/Godot) |
| **CIS** | Creative Intelligence | 0.2.0 | 10 | 创新、头脑风暴与设计思维 |

---

## 🧠 BMM 核心角色 (Agents) — 7 个

| 角色 ID | 名称 | 职责 | 触发场景 |
|:---|:---|:---|:---|
| **bmad-agent-pm** | 产品经理 (John) | 需求分析、PRD、优先级 | "帮我写产品需求文档" |
| **bmad-agent-analyst** | 业务分析师 | 深度挖掘需求、澄清概念 | "这个需求不太清楚" |
| **bmad-agent-architect** | 架构师 (Winston) | 系统设计、技术选型 | "设计系统架构" |
| **bmad-agent-ux-designer** | UX 设计师 (Sally) | 界面交互、用户旅程 | "设计界面交互" |
| **bmad-agent-dev** | 开发者 (Amelia) | 代码实现、单元测试 | "实现这个 Story" |
| **bmad-agent-tech-writer** | 技术文档专家 | API 文档、部署指南 | "写接口文档" |
| **bmad-agent-builder** | 构建器 | 自定义 Agent 创建 | "帮我造个新 Agent" |

**设计哲学**：6 大核心原则
1. **Human-AI Partnership** — 人类提供愿景，AI 提供结构
2. **Context Engineering** — 文档即上下文，产物链驱动
3. **Progressive Elaboration** — 高层目标逐步精化到可执行单元
4. **Agent Specialization** — 不同角色(PM/Architect/Dev)各司其职
5. **Methodology Over Generation** — 方法论引导 > 直接生成代码
6. **🪶 Injection Over Interruption** — 构建 Agent 守护机制时，**注入优先、阻断慎用**。在适当时机注入上下文和建议，让 Agent 自主决定是否采纳，而非强行阻断工具执行。力度不是「阻断强度」，而是「注入覆盖度」——控制的是在哪些时机注入推荐，而非是否允许执行。

---

## 🔄 BMM 四阶段流程详解

```
Phase 1: Analysis (Optional)
  ↓                         Brainstorming → Research → Product Brief
Phase 2: Planning (Required)
  ↓                         PRD + UX Design (定义 WHAT & WHY)
Phase 3: Solutioning (Method)
  ↓                         Architecture + Epics (定义 HOW & WHAT UNITS)
Phase 4: Implementation
                              Sprint-by-sprint (交付 WORKING SOFTWARE)
```

### Phase 1: 分析（可选）
> 探索问题空间，在投入规划前验证想法
- `bmad-brainstorming` — 头脑风暴
- `bmad-bmm-research` — 领域/市场/技术研究
- `bmad-bmm-create-product-brief` — 产品简介

### Phase 2: 规划（必须）
> 定义构建什么、为谁构建
- `bmad-bmm-create-prd` — 定义需求（FRs/NFRs）→ 产出 PRD.md
- `bmad-bmm-create-ux-design` — 用户体验设计 → 产出 ux-spec.md

### Phase 3: 解决方案设计
> 决定如何构建并拆解工作
- `bmad-bmm-create-architecture` — 技术决策 + ADRs → architecture.md
- `bmad-bmm-create-epics-and-stories` — 拆解 Epic/Story → Epic files
- `bmad-bmm-check-implementation-readiness` — 门禁检查 → PASS/CONCERNS/FAIL

### Phase 4: 实现
> 逐个 Story 构建，**每次代码变更后必须做一致性检测**
- `bmad-bmm-sprint-planning` — Sprint 规划（初始化跟踪）
- `bmad-bmm-create-story` — 准备 Story 上下文
- `bmad-bmm-dev-story` — 实现 Story → 工作代码 + 测试
- `bmad-bmm-code-review` — 代码审查
- `bmad-bmm-correct-course` — 中途纠偏
- **⚡ `commit-quality-check`** — **一致性检测（强制步骤）**: 文档/安全/版本/变更范围自检
- `bmad-bmm-retrospective` — 回顾会议

### Quick Flow（并行快速通道）
> 跳过 Phase 1-3，适用于 1-15 stories 的简单工作
- `bmad-bmm-quick-spec` → tech-spec.md
- `bmad-bmm-quick-dev` → 工作代码 + 测试

---

## 🔧 Workflow Engine 架构

所有 BMad 工作流遵循 **Step-file Architecture**：
- **Micro-file Design**: 每个步骤是独立指令文件
- **Just-In-Time Loading**: 仅当前步骤在内存
- **Sequential Enforcement**: 严禁跳过或优化顺序
- **State Tracking**: 用 stepsCompleted 数组追踪
- **Append-Only Building**: 追加方式构建文档
- **Menu-Driven**: 在关键决策点暂停等待用户输入

**Step 处理规则**：
1. 读完整文件再行动
2. 按编号顺序执行
3. 遇到菜单等待用户选择
4. 仅当用户选 "C" 才继续
5. 更新 stepsCompleted 后加载下一步
6. 按指示加载下一步文件

---

## 🛠️ 在 Hermes 中使用

当主人触发本 Skill 时，boku 将通过 `skill_view` 加载对应的子 Skill 并执行。

**使用模式**：
1. **直接调用**：主人说 "帮我用 BMad 写个 PRD"，boku 加载 `bmad-create-prd`
2. **全流程**：主人说 "用 BMad 方法从 0 做一个项目"，boku 按流水线依次启动
3. **专项专家**：主人说 "让 TEA 帮我制定测试策略"，boku 加载 `bmad-tea`

**输出路径**：所有生成的文档默认保存在当前项目目录的 `_bmad-output/` 下。

---

## 🚩 注意事项（避坑指南）

- ❌ **跳过 PRD 直接写代码** → 需求不稳就开干
  - ✅ 先打地基：至少走 PRD → Architecture → Epic
- ❌ **跳过 Implementation Readiness 检查**
  - ✅ 必跑 bmad-check-implementation-readiness
- ❌ **Quick Flow 做复杂项目**（10+ stories）
  - ✅ 必须走 BMad Method 完整流程
- ❌ **Agent 上下文传递断裂**
  - ✅ 管理明确文件路径传递
- ❌ **所有工作在一个 session 里完成** → 上下文爆炸
  - ✅ 每个阶段/工作流开新 session
- ❌ **User Story 写得太大**
  - ✅ 遵循 INVEST 原则
- ❌ **Retrospective 沦为形式**
  - ✅ 每个 Retro 至少产出一个可执行改进行动
- ❌ **完成任务直接提交，跳过一致性检测**
  - ✅ 任何代码/文档变更后，**先跑 commit-quality-check** 再汇报或提交
  - ✅ 检测内容包括：安全红线、文档一致性、版本号一致性、变更范围纯净度
- ❌ **CI 阶段才做质量检查**
  - ✅ 一致性检测最晚在 git commit 前、**最好在完成任务后立即执行**

---

## 🧪 TEA 测试架构模块 — 10 个

> **Agent: Murat** (Master Test Architect and Quality Advisor)
> **用途**: 风险驱动的企业级测试策略、自动化与发布门禁
> **安装**: `npx bmad-method install` → 选择 "Test Architect (TEA)"
> **文档**: https://docs.bmad-method.org/reference/testing/

| Skill | 码 | 职责 |
|:---|:---:|:---|
| `bmad-tea` | — | TEA 总入口（加载 Murat 菜单） |
| `bmad-teach-me-testing` | TMT | 测试教学（7 节课，1-2 周） |
| `bmad-testarch-atdd` | AT | 验收测试驱动开发（TDD 红阶段） |
| `bmad-testarch-automate` | TA | 扩展自动化测试覆盖 |
| `bmad-testarch-ci` | CI | CI/CD 质量管线设置 |
| `bmad-testarch-framework` | TF | 测试框架搭建（Playwright/Cypress） |
| `bmad-testarch-nfr` | NR | 非功能性需求评估 |
| `bmad-testarch-test-design` | TD | 风险驱动测试规划 + P0-P3 优先级 |
| `bmad-testarch-test-review` | RV | 测试质量审计（0-100 评分 5 维度） |
| `bmad-testarch-trace` | TR | 需求→测试覆盖映射 + Go/No-Go 门禁 |

**在 BMM 四阶段中的集成**:
| 阶段 | TEA Workflows | 频率 |
|------|--------------|:----:|
| Phase 2 规划 | (无) | — |
| Phase 3 解决方案 | framework, ci | 一次/项目 |
| Phase 4 实现 | test-design, atdd, automate, test-review, trace | 每个 Epic/Story |
| Release 发布 | nfr-assess, trace Phase2 | 每个 Epic |

**子代理架构**: automate/atdd 各 3 个并行子代理，test-review 6 个(5并行)，nfr-assess 5 个(4并行)

---

## 💡 CIS 创新智能模块 — 10 个

> **6 大 Agent**: Carson(头脑风暴) | Maya(设计思维) | Victor(创新战略) | Dr.Quinn(问题解决) | Sophia(叙事) | Caravaggio(演示)
> **文档**: https://cis-docs.bmad-method.org/

| Agent | 工作流 | 用途 |
|:------|:-------|:-----|
| **Carson** 🧠 | `bmad-cis-agent-brainstorming-coach` | 36 种技巧 x 7 类结构化头脑风暴 |
| **Maya** 🎨 | `bmad-cis-agent-design-thinking-coach` | 5 阶段设计思维（共情→定义→构思→原型→测试） |
| **Victor** 📊 | `bmad-cis-agent-innovation-strategist` | 颠覆性机会与商业模式创新 |
| **Dr. Quinn** 🔍 | `bmad-cis-agent-creative-problem-solver` | 系统性问题诊断与根因分析 |
| **Sophia** 📖 | `bmad-cis-agent-storyteller` | 25 种故事框架叙事 |
| **Caravaggio** 🎭 | `bmad-cis-agent-presentation-master` | 结构化演示（coming soon） |

**方法论**:
- `bmad-cis-design-thinking` — 设计思维流程
- `bmad-cis-innovation-strategy` — 创新策略
- `bmad-cis-problem-solving` — 问题解决框架
- `bmad-cis-storytelling` — 故事叙述技巧

## 📚 参考资料

- `references/sprint-iteration-workflow.md` — Sprint 迭代规划与 Git 分支工作流（启动新迭代时的标准流程）

---

## 🔗 关联 Skill

- `skill-creator` — 依赖（Skill 创建框架）
- `writing-plans` — 依赖（计划编写）
- `commit-quality-check` — 依赖（一致性检测 — 每个 Story 完成后强制执行）
- `learning-workflow` — 学习新主题时联动
- `deep-research` — 深度调研阶段联动
