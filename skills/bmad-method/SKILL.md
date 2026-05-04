---
name: bmad-method
description: "BMad Method (Build More Architect Dreams) - 全生态 AI 驱动开发框架。含 BMM(敏捷开发)、BMB(模块构建)、TEA(测试架构)、BMGD(游戏开发)、CIS(创新智能) 五大模块共 102 个 Skill。项目开发、功能实现、Bug修复等任务自动触发 BMad 工作流。"
version: 2.1.0
triggers:
  # === 核心启动词 ===
  - bmad
  - bmad-method

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

  # === 代码实现 ===
  - 写代码
  - 编码
  - 实现这个
  - 实现模块
  - 实现 feature

  # === Bug 修复 / 问题解决 ===
  - bug修复
  - 修bug
  - 修复bug
  - 修复问题
  - 出了bug
  - 有问题
  - 改bug

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

  # === 架构设计 ===
  - 架构设计
  - 系统设计
  - 技术选型
  - 设计架构
  - 方案设计
  - 技术方案

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
depends_on:
  - skill-creator
  - writing-plans
design_pattern: Pipeline
skill_type: Tool Wrapper
---

# 🐎 BMad 全生态 · AI 驱动开发框架 v2.0

> **核心理念**：AI 不是简单的聊天机器人，而是结构化的**专家协作团队**。BMad 通过明确的角色分工和阶段化流程，引导用户完成从构思到落地的全过程。
> **安装版本**：v6.6.0 (全量安装)
> **技能总数**：102 个独立 Skill
> **核心路径**：`~/.hermes/skills/bmad-method/all-skills/`
> **配置路径**：`~/.hermes/skills/bmad-method/_bmad/`
> **用户配置**：`_bmad/config.user.toml` (language=Chinese, user=boku)

## 🎯 自动触发场景与决策树

当主人触发本 Skill（任何 triggers 匹配），boku 按以下决策树判断走 BMad 工作流的哪个路径：

```
主人消息 → 匹配 triggers？
  ├── 项目开发/功能实现/写代码类
  │   ├── 需要完整流程？ → bmad-create-prd → bmad-create-epics → bmad-dev-story ...
  │   ├── 已有清晰需求？ → bmad-create-epics → bmad-dev-story
  │   └── 小功能/快速开发？ → bmad-quick-dev
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

## 📦 五大模块总览

| 模块 | 全称 | 版本 | 技能数 | 定位 |
|:---|:---|:---|:---|:---|
| **BMM** | BMad Method | 6.6.0 | 49 | 敏捷 AI 驱动开发（核心） |
| **BMB** | BMad Builder | 1.7.0 | 2 | 元模块 — 创建自定义 Agent 和模块 |
| **TEA** | Test Architect | 1.15.1 | 10 | 企业级测试策略与自动化 |
| **BMGD** | Game Dev Studio | 0.4.0 | 36 | 游戏开发全流程 (Unity/Unreal/Godot) |
| **CIS** | Creative Intelligence | 0.2.0 | 10 | 创新、头脑风暴与设计思维 |

## 🧠 BMM 核心角色 (Agents) — 7 个

当需要开发软件或复杂项目时，boku 将加载对应 Agent 作为子代理：

| 角色 ID | 名称 | 职责 | 触发场景 |
|:---|:---|:---|:---|
| **bmad-agent-pm** | 产品经理 | 需求分析、PRD、优先级 | "帮我写产品需求文档" |
| **bmad-agent-analyst** | 业务分析师 | 深度挖掘需求、澄清概念 | "这个需求不太清楚，帮我理理" |
| **bmad-agent-architect** | 架构师 | 系统设计、技术选型 | "设计系统架构" |
| **bmad-agent-ux-designer** | UX 设计师 | 界面交互、用户旅程 | "设计界面交互" |
| **bmad-agent-dev** | 开发者 | 代码实现、单元测试 | "实现这个 Story" |
| **bmad-agent-tech-writer** | 技术文档专家 | API 文档、部署指南 | "写接口文档" |
| **bmad-agent-builder** | 构建器 | 自定义 Agent 创建 | "帮我造个新 Agent" |

## 🔄 BMM 核心工作流 — 34 个

按开发生命周期分组：

### 构思与分析 (Ideation & Analysis)
- `bmad-brainstorming` — 头脑风暴，确定核心价值
- `bmad-product-brief` — 产品简介
- `bmad-prfaq` — PR/FAQ 文档（Amazon 风格）
- `bmad-domain-research` — 领域研究
- `bmad-market-research` — 市场调研
- `bmad-technical-research` — 技术研究
- `bmad-advanced-elicitation` — 高级需求引导

### 需求定义 (Requirements)
- `bmad-create-prd` — 生成产品需求文档 (PRD)
- `bmad-edit-prd` — 编辑/更新 PRD
- `bmad-validate-prd` — 验证 PRD 质量
- `bmad-create-epics-and-stories` — 拆解 Epic 和 User Story
- `bmad-create-story` — 创建单个 User Story

### 架构与设计 (Architecture & Design)
- `bmad-create-architecture` — 系统架构设计
- `bmad-create-ux-design` — UX 设计
- `bmad-check-implementation-readiness` — 实现就绪检查

### 实现与开发 (Implementation)
- `bmad-dev-story` — 按 Story 开发
- `bmad-quick-dev` — 快速开发模式
- `bmad-correct-course` — 纠偏/调整方向

### 代码审查 (Code Review)
- `bmad-code-review` — 标准代码审查
- `bmad-review-adversarial-general` — 对抗性审查
- `bmad-review-edge-case-hunter` — 边界用例猎手

### 测试与质量 (Testing & Quality)
- `bmad-qa-generate-e2e-tests` — 端到端测试生成

### 项目管理 (Project Management)
- `bmad-sprint-planning` — 冲刺规划
- `bmad-sprint-status` — 冲刺状态跟踪
- `bmad-retrospective` — 回顾会议
- `bmad-checkpoint-preview` — 阶段检查点
- `bmad-generate-project-context` — 生成项目上下文
- `bmad-document-project` — 项目文档化
- `bmad-index-docs` — 文档索引
- `bmad-shard-doc` — 文档分片

### 编辑与审查 (Editorial)
- `bmad-editorial-review-prose` — 散文风格审查
- `bmad-editorial-review-structure` — 结构审查

### 元工具 (Meta)
- `bmad-customize` — 自定义配置
- `bmad-distillator` — 内容提炼
- `bmad-help` — 帮助
- `bmad-party-mode` — 派对模式（多 Agent 协作）
- `bmad-workflow-builder` — 工作流构建器

## 🛠️ BMB 构建器模块 — 2 个

- `bmad-bmb-setup` — BMB 环境配置
- `bmad-module-builder` — 模块构建（创建自定义 Agent/工作流/模块）

## 🧪 TEA 测试架构模块 — 10 个

| Skill | 职责 |
|:---|:---|
| `bmad-tea` | TEA 总入口 |
| `bmad-teach-me-testing` | 测试教学 |
| `bmad-testarch-atdd` | 验收测试驱动开发 |
| `bmad-testarch-automate` | 测试自动化 |
| `bmad-testarch-ci` | CI/CD 集成 |
| `bmad-testarch-framework` | 测试框架选型 |
| `bmad-testarch-nfr` | 非功能性需求测试 |
| `bmad-testarch-test-design` | 测试设计 |
| `bmad-testarch-test-review` | 测试审查 |
| `bmad-testarch-trace` | 需求可追溯性 |

## 🎮 BMGD 游戏开发模块 — 36 个

### 角色 (5)
- `gds-agent-game-architect` — 游戏架构师
- `gds-agent-game-designer` — 游戏设计师
- `gds-agent-game-dev` — 游戏开发者
- `gds-agent-game-solo-dev` — 独立游戏开发者
- `gds-agent-tech-writer` — 游戏技术文档专家

### 设计 (8)
- `gds-brainstorm-game` — 游戏头脑风暴
- `gds-create-game-brief` — 游戏简介
- `gds-create-gdd` — 游戏设计文档 (GDD)
- `gds-edit-gdd` — 编辑 GDD
- `gds-validate-gdd` — 验证 GDD
- `gds-create-narrative` — 叙事设计
- `gds-create-ux-design` — 游戏 UX 设计
- `gds-create-prd` / `gds-edit-prd` / `gds-validate-prd` — 游戏 PRD

### 架构与开发 (8)
- `gds-game-architecture` — 游戏架构
- `gds-create-epics-and-stories` — 拆解史诗与故事
- `gds-create-story` / `gds-dev-story` / `gds-quick-dev` — 开发流程
- `gds-correct-course` — 纠偏
- `gds-e2e-scaffold` — 端到端脚手架
- `gds-code-review` — 代码审查
- `gds-performance-test` — 性能测试

### 项目管理 (8)
- `gds-generate-project-context` — 项目上下文
- `gds-document-project` — 项目文档
- `gds-sprint-planning` / `gds-sprint-status` — 冲刺管理
- `gds-retrospective` — 回顾
- `gds-check-implementation-readiness` — 实现就绪
- `gds-domain-research` — 领域研究

### 测试 (4)
- `gds-test-design` — 测试设计
- `gds-test-automate` — 测试自动化
- `gsd-test-framework` — 测试框架
- `gds-test-review` — 测试审查
- `gds-playtest-plan` — 游戏试玩计划

## 💡 CIS 创新智能模块 — 10 个

### Agent 角色 (6)
- `bmad-cis-agent-brainstorming-coach` — 头脑风暴教练
- `bmad-cis-agent-creative-problem-solver` — 创意问题解决者
- `bmad-cis-agent-design-thinking-coach` — 设计思维教练
- `bmad-cis-agent-innovation-strategist` — 创新策略师
- `bmad-cis-agent-presentation-master` — 演讲大师
- `bmad-cis-agent-storyteller` — 故事讲述者

### 方法论 (4)
- `bmad-cis-design-thinking` — 设计思维流程
- `bmad-cis-innovation-strategy` — 创新策略
- `bmad-cis-problem-solving` — 问题解决框架
- `bmad-cis-storytelling` — 故事叙述技巧

## 🛠️ 在 Hermes 中使用

当主人触发本 Skill 时，boku 将通过 `skill_view` 加载对应的子 Skill 并执行。

**使用模式**：

1. **直接调用**：主人说 "帮我用 BMad 写个 PRD"，boku 加载 `bmad-create-prd`
2. **全流程**：主人说 "用 BMad 方法从 0 做一个项目"，boku 按流水线依次启动
3. **专项专家**：主人说 "让 TEA 帮我制定测试策略"，boku 加载 `bmad-tea`

**输出路径**：
所有生成的文档默认保存在当前工作目录的 `_bmad-output/` 文件夹下。

## 🚩 注意事项

- **不要跳过阶段**：没有 PRD 就直接架构设计 = 空中楼阁
- **上下文传递**：每个 Agent 是独立子代理，需传递上一阶段的产出文件路径
- **中文优先**：已配置 communication_language=Chinese, document_output_language=Chinese
- **全 102 个 Skill** 均在 `all-skills/` 目录下，通过 `skill_view` 按需加载
