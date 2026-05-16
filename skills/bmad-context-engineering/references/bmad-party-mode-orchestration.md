---
name: bmad-party-mode-orchestration
description: "BMAD 多智能体编排指南。详解如何使用 Party Mode 并行 Spawn Subagent、动态路由上下文、以及进行上下文压缩。适用于需要多视角分析、复杂问题研讨或模拟专家会议的场景。"
version: 1.0.0
triggers:
- BMAD Party Mode
- 多智能体协作
- 并行 Subagent
- Agent 编排
- 上下文压缩
- 专家会议
- 模拟讨论
author: 小玛
license: MIT
allowed-tools:
- terminal
- delegate_task
metadata:
  hermes:
    tags:
    - bmad
    - multi-agent
    - orchestration
    - party-mode
    category: devops
    skill_type: Tool Wrapper
---

# 🎭 BMAD 多智能体编排指南 (Party Mode Orchestration)

> **核心定位**: 本 Skill 指导 boku 如何像 BMAD 一样，优雅地编排多个 Subagent 进行高效协作，避免串行等待和上下文污染。

## 🔍 1. 核心哲学：为什么要用 Party Mode？

普通的多角色对话（Roleplay）会导致 AI 的"观点趋同"（Convergence）。
**Party Mode 的本质**：通过独立 Spawn 子进程，让每个 Agent 拥有**真正的独立思考空间**。

## ⚙️ 2. 编排机制 (Orchestration Mechanics)

### 机制 A: 并行生成 (Parallel Spawn)
**铁律**：永远不要把 Agent A 和 Agent B 串行化！
*   **做法**：在一个 response 中发出**所有** `delegate_task` (Agent tool) 调用。
*   **效果**：
    1.  所有 Agent **同时**接收指令，互不干扰。
    2.  大幅降低延迟（Latency）。
    3.  保证视角的独立性（Diversity of thought）。

### 机制 B: 动态上下文路由 (Dynamic Context Routing)
根据用户的问题，精准选择 Spawn 谁，传递什么上下文：

| 用户场景 | 编排策略 |
| :--- | :--- |
| **开放式讨论** | Spawn 2-4 个相关领域专家，并行执行。 |
| **"A，你怎么看 B 说的？"** | **只 Spawn A**。将 B 的发言作为 Context 传入。 |
| **"让 C 加入讨论"** | Spawn C。传入当前讨论的**摘要**。 |
| **"我同意 D，深入讲讲"** | Spawn D + 1-2 个互补专家，基于 D 的观点扩展。 |

### 机制 C: 上下文压缩 (Context Compression)
随着讨论深入，历史记录会爆炸。
**铁律**：传给 Subagent 的 `Discussion Context` **不得超过 400 字**！
*   **做法**：每 2-3 轮或话题转换时，Orchestrator 必须进行一次**摘要总结 (Summarization)**。
*   **内容**：当前讨论了啥？各 Agent 的立场是什么？用户想干嘛？

## 🛠️ 3. Solo Mode 降级策略

当 Subagent 不可用或需要极速响应时，使用 `--solo` 模式：
*   **做法**：boku 自己扮演所有角色。
*   **要求**：必须严格保持每个角色的 Persona 和 Icon，不能混淆。
*   **格式**：
    ```markdown
    **🏗️ 架构师:** (观点...)

    **🧪 测试员:** (反驳架构师...)
    ```

## 📝 4. 实战应用：如何组织一场专家会议

**Step 1: 选定阵容 (Roster)**
根据任务类型选择 3 个核心 Agent (如：PM + 架构师 + 开发者)。

**Step 2: 注入背景 (Context Injection)**
给每个 Agent 的 Prompt 包含：
1.  **Persona**: 你是谁 (e.g., "你是 Murat，测试架构师...")
2.  **Context**: 项目背景摘要 (< 400 字)。
3.  **Other's Opinions**: 如果是对抗环节，传入其他人的观点。

**Step 3: 收集与呈现 (Collection & Presentation)**
*   **不要**对 Agent 的回答进行总结或 paraphrase！
*   **直接**展示他们的原始发言。
*   **保持**他们的独特语气和格式。

## 🚩 Red Flags

- ❌ **串行调用**: "等 Agent A 说完，再让 Agent B 说" —— 效率极低且容易同质化。
- ❌ **全盘传入**: 把几千字的聊天记录塞给新加入的 Agent —— 导致注意力涣散。
- ❌ **过度总结**: 把 Agent A 精彩的发言总结成一句"Agent A 觉得不错" —— 丢失细节和灵魂。