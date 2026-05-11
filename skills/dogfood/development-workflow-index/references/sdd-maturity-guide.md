# SDD Maturity Guide — Spec-Driven Development 框架速查

> 来源: BMAD v6.6.0, Superpowers (180K⭐), GSD v1.40, SDD 社区研究 (2026-05-11)
> 关联: `development-workflow-index` §8 P0 铁律 #11

---

## 1. SDD 成熟度模型

| 级别 | 名称 | 描述 | 场景 |
|:----:|:-----|:------|:-----|
| L1 | **Spec-First** | 每任务一 Spec，实现后可丢弃。最低仪式感 | 快速 prototype / 一次性任务 |
| L2 | **Spec-Anchored** 🔥 | **推荐**。Spec 是活的，变更先改 Spec 再改代码 | 多数活跃开发项目 |
| L3 | **Spec-as-Source** | Spec 是唯一制品，代码是编译输出。Tessl ($125M) | 实验阶段 |

## 2. 三大框架的 Spec 链对比

```
BMAD:       PRD → Architecture(ADRs) → Epics → Stories → Sprint → Dev
Superpowers: Brainstorm(Design Spec) → Writing Plans(Tech Spec) → TDD → Review
GSD:        PLANNING(Gap Analysis) → BUILDING(Implementation) → Loop
```

| 维度 | BMAD | Superpowers | GSD |
|:-----|:-----|:------------|:-----|
| **Spec 粒度** | PRD → Story（多层） | Design Spec → Tech Plan | 单层 TODO |
| **Spec 位置** | `_bmad-output/` 多文件 | `docs/superpowers/specs/` | 单文件 |
| **审批节点** | PRD→Arch→IR 门禁 | Brainstorm→Plan→Review | 无（自动循环） |
| **上下文策略** | Step-File JIT 加载 | 子代理隔离 200K tokens | 新鲜上下文每任务 |
| **防漂移** | Implementation Readiness 门禁 | Two-Stage Review | Gap Analysis |
| **适合** | 团队/企业/合规 | 有纪律的个人开发者 | 快速 MVP / solo |
| **复杂度** | 高 (21+ agents, 102 skills) | 中 (14 skills) | 低 (3 commands) |

## 3. Spec 的「三不」原则

```
1. 🚫 Specs 不可跳过    —— 复杂任务没有获批 Spec 就写代码 = P0 违规
2. 🚫 Specs 不可静默    —— 变更必须先更新 Spec，再改代码
3. 🚫 Specs 不可漂移    —— 使用 doc-alignment 检测 Spec 与代码的偏差
```

## 4. 合格 Spec 的 5 要素

| # | 要素 | 说明 | 必填？ |
|:-:|:-----|:------|:------:|
| 1 | 用户故事 | As a / I want / So that | ✅ |
| 2 | 验收标准 | 每个 AC 可验证（自动化测试或手动检验） | ✅ |
| 3 | 测试数据契约 | `test_data` 字段，声明 fixture 来源 + CI 独立 | ✅ |
| 4 | 引用链 | `spec_references` 追溯 Epic/Architecture | 🟡 |
| 5 | 不做的范围 | `out_of_scope` 防止 scope creep | 🟡 |

## 5. Spec 完整生命周期

```text
CREATE → APPROVE → IMPLEMENT → VALIDATE → MERGE → MAINTAIN
 写      主人审阅   TDD 实现   测试+验证   代码+文档   漂移检测
```

## 6. SDD vs 传统方法

| 维度 | Vibe Coding | SDD (Spec-Anchored) |
|:-----|:-----------|:-------------------|
| 启动方式 | 「帮我写个XX」 | 先写 Spec，再开发 |
| 上下文 | 依赖 LLM context window | 依赖文件系统 + git |
| 可审计性 | 无（"为什么这么写？"） | 完整（Spec 记录意图） |
| 变更成本 | 高（反向工程意图） | 低（改 Spec → 重新生成） |
| 团队协作 | 单人可用，团队无法 | 多人可并行 |

## 7. 框架选择决策

```
你的团队规模？
├── 1 人, 速度优先 → GSD
├── 2-8 人, 迭代快 → GSD / Ralph Loop
├── 10+ 人, 合规要求 → BMAD
└── 单人但有纪律 → Superpowers / 混合模式
```

## 8. 参考来源

- BMAD Method: https://github.com/bmadcode/BMAD-METHOD (v6.6.0, 46K⭐)
- Superpowers: https://github.com/obra/superpowers (180K⭐)
- GSD: https://github.com/gsd-build/get-shit-done (v1.40, 60K⭐)
- Spec Kit: https://github.com/github/spec-kit
- SDD Guide: https://planu.dev/en/blog/spec-driven-development-guide
- GEICO SDD: https://www.geico.com/techblog/an-introduction-to-spec-driven-development/
