# SDD 深度研究参考 — Spec-Driven Development 框架分析

> 来源: 2026-05-11 深度循环学习（BMAD v6.6, Superpowers 180K⭐, GSD v1.40）
> 关联: `sdd-workflow` skill, `development-workflow-index` §8

---

## 1. SDD 为什么存在

**Vibe Coding 的失败模式**不是 prompt 问题，而是缺乏结构化 backbone：

| 指标 | 数据 | 来源 |
|:-----|:-----|:-----|
| AI 代码质量问题 | 1.7x more major issues, 2.74x 安全漏洞 | CodeRabbit 470 PRs |
| AI 代码安全 | ~45% 样本未通过安全测试 | Veracode 2025 |
| 修复时间 | 66% 的开发者花更多时间修 AI 代码 | Developer Survey |
| 预计技术债 | $1.5 trillion by 2027 | Industry Projection |

**根因**: 没有规范（Spec）作为一等制品。每次决策依赖 LLM 的临时上下文窗口，无法持久化、无法审计、无法复现。

## 2. 三大框架的核心理念

| 框架 | 核心命题 | 解决什么问题 | 一句话 |
|:-----|:---------|:------------|:-------|
| **BMAD** | 用角色分工模拟敏捷团队 | 复杂项目的治理和可审计性 | 「hire an entire engineering team」 |
| **Superpowers** | 用铁律链强制工程纪律 | 个人开发者的自律和一致性 | 「install engineering discipline」 |
| **GSD** | 用上下文隔离击败 context rot | 长任务/大项目的上下文保持 | 「context rot is the primary failure mode」 |

## 3. Spec 三不原则（核心约束）

来自三大框架的共同交集，适用于任何 SDD 实践：

| # | 原则 | 机械门禁 | 违反后果 |
|:-:|:-----|:---------|:---------|
| 1 | Specs **不可跳过** | `spec-gate.py enforce` | 不可审计、方向不对 |
| 2 | Specs **不可静默** | `doc-alignment --verify` | Spec-代码漂移 |
| 3 | Specs **不可漂移** | Reality Check + `check-stale` | 基于过时信息决策 |

## 4. 关键数据点

### BMAD v6.6 (2026-04)
- 42 skills → 102 skills（五大模块）
- 跨平台: Claude Code, Cursor, Codex
- 案例: 50k LOC COBOL→Java 迁移, 40% 集成时间减少

### Superpowers (2026-05)
- 14 skills, 180K⭐
- 核心「Subagent-Driven Development」: 每个 Task 新鲜上下文 + Two-Stage Review
- 强制流程: Brainstorm → Plan → TDD → Review → Finish

### GSD v1.40 (2026-05)
- 3-phase funnel: PLANNING → BUILDING → Loop
- Minimal Install Profile: 系统 prompt 从 12k→700 tokens (-94%)
- 案例: 100k LOC / 2 周（solo developer）

## 5. SDD 的技术经济学

| 模式 | 修 Bug 的成本 | 可审计性 | 团队规模 |
|:-----|:------------|:---------|:---------|
| Vibe Coding | 高（反向工程意图） | 无 | 单人 |
| Spec-First | 中（改 Spec 重做） | 部分 | 1-3 人 |
| **Spec-Anchored** | **低（改 Spec 更新实现）** | **完整** | **2-10 人** |
| Spec-as-Source | 极低（改 Spec 自动生成） | 完整 | 实验阶段 |

## 6. 参考来源

- BMAD Method: https://github.com/bmadcode/BMAD-METHOD (v6.6.0)
- Superpowers: https://github.com/obra/superpowers
- GSD: https://github.com/gsd-build/get-shit-done
- GEICO SDD Intro: https://www.geico.com/techblog/an-introduction-to-spec-driven-development/
- Planu SDD Guide: https://planu.dev/en/blog/spec-driven-development-guide
- The Great Framework Showdown (Rick Hightower): https://medium.com/@richardhightower/the-great-framework-showdown-superpowers-vs-bmad-vs-speckit-vs-gsd
