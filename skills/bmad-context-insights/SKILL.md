---
name: bmad-context-insights
description: "BMAD 核心架构与上下文工程深度解析。包含 TOML 上下文注入机制、Party Mode 多智能体并行编排、Step-File 架构流派对比及 project-context.md 契约。"
triggers: [bmad配置, bmad架构, party mode, 上下文注入, 多智能体编排, project-context, bmad context]
---

# BMAD Context & Architecture Insights

## 1. 上下文注入机制 (Context Injection)
BMAD 不仅仅是 Prompt，它是基于文件系统的 AI 操作系统。
- **核心脚本**: `resolve_customization.py` 负责合并配置。
- **合并顺序**: Skill Default < Team Config < User Config.
- **灵魂文件**: `project-context.md`。通过在 TOML 中配置 `persistent_facts` 指向该文件，强制 AI Agent 在启动时加载项目规则。

## 2. 流程控制流派 (Workflow Styles)
- **流派 A (Micro-File)**: 将步骤拆分为 `step-01.md`, `step-02.md` 等。
    - *优点*: 极强防呆，AI 无法跳步。
    - *适用*: PRD、Architecture 等严谨流程。
- **流派 B (In-Skill XML)**: 步骤写在 SKILL.md 的 `<workflow>` XML 标签内。
    - *优点*: 启动快。
    - *缺点*: AI 在长文中易迷失。
    - *适用*: Dev Story 等快速迭代。

## 3. Party Mode 多智能体编排 (Multi-Agent Orchestration)
- **并行生成 (Parallel Spawn)**: 同时召唤多个 Agent (如 PM, Arch, Dev) 接收指令，保证视角独立，防止互相吹捧。
- **动态路由 (Dynamic Context Routing)**: 用户问 "A 怎么看 B?" 时，只 Spawn A，并注入 B 的发言作为上下文。
- **上下文压缩 (Context Compression)**: 讨论摘要必须控制在 **400字以内**，防止 Subagent 迷失在海量信息中。

## 4. 开发实践
- **Artifact 导向**: 所有学习/开发必须产出文件 (Skill/MD)，否则视为无效。
- **TDD 强制**: 开发 Story 必须先写失败测试 (RED)，再写代码 (GREEN)。