# 🧠 三层知识流动架构 (Knowledge Flow Architecture)

> 发现日期: 2026-05-09
> 来源: 三层知识库改造学习任务 — 信息收集阶段
> 相关 skill: learning-workflow, knowledge-routing, knowledge-precipitation

---

## 当前知识流动路径（含缺口标注）

```
学习/复盘完成
    ↓
learning-workflow STEP 6
    │
    ├─ 4. 经验提取 → ~/.hermes/experiences/active/        ✅ L2
    │     └─ 更新 experiences/index.md
    │
    ├─ 5. 🧬 L3 Brain 沉淀 → ~/.hermes/brain/wiki/        🆕 v5.4
    │     ├─ concepts/  (通用模式/方法论/原则)
    │     ├─ entities/  (人物/工具/项目)
    │     ├─ summaries/ (文档/论文摘要)
    │     └─ analyses/  (对比/推演)
    │     ├─ 更新 brain/index.md
    │     ├─ 追加 brain/log.md
    │     └─ 更新 KNOWLEDGE_INDEX.md
    │
    └─ 6. 自动 Skill 关联                                    ✅ v5.3
          └─ skill-auto-link.py
```

---

## 三层知识沉淀时机

| 沉淀目标 | 触发条件 | 例子 |
|:--------|:---------|:-----|
| L2 Experience | 可复用经验/教训/发现，深度浅 | 「PDF 字体回退方案：先检查 WQY」 |
| L3 Brain/concepts | 通用模式/方法论/原则 | 「Bounded Autonomy」「实施前四问」 |
| L3 Brain/entities | 重要人物/工具/项目 | 「Andrej Karpathy」「GBrain」 |
| L3 Brain/summaries | 文档/论文/学习提炼 | 「文件系统自主管理」 |
| L3 Brain/analyses | 对比分析/推演结论 | 「三层知识库架构对比」 |
| L1 Skill | 复用频率 > 3 次的操作流程 | 「commit-quality-check」 |

## 易错点

- ❌ 具体技巧塞进 L3 Brain → 引发 brain 膨胀 → 应走 L2 Experience
- ❌ 核心概念只塞进 L2 Experience → 难以检索 → 应走 L3 Brain/concepts
- ❌ 学习总结写到 learning/reviews/ 就停 → 必须继续流向 L2 或 L3
- ❌ 更新 brain 页面后不更新 index.md/log.md → 知识无法检索
