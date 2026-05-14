# 🏗️ 后置质量升级阶段 — EPIC-004 规划参考

> **来源**: 2026-05-14 hermes-cap-pack EPIC-004 规划
> **适用场景**: 所有能力包提取完成后，统一进行质量升级

## 动机

当前能力包提取只完成了 L1 Skills 层（SKILL.md 复制）。但完整的能力包应包含三层知识体系：

| 层 | 当前 | 目标 |
|:---|:-----|:-----|
| L1 Skills | ✅ 已提取 | 保持不变 |
| L2 Experiences | ❌ 缺失 | 每个包补充实战经验文档 |
| L3 Brain | ❌ 缺失 | 每个包补充概念/实体/分析知识 |

## 三阶段计划

### Phase A: 三层改造

为每个 pack 补充 EXPERIENCES/（L2）和 KNOWLEDGE/（L3）目录：

```text
packs/<name>/
├── cap-pack.yaml          # ✅ 已有
├── SKILLS/                # ✅ 已有 (L1)
├── EXPERIENCES/           # ❌ 新增 (L2)
│   └── <exp-id>.md        # — 实战经验/教训/最佳实践
└── KNOWLEDGE/             # ❌ 新增 (L3)
    ├── concepts/          # — 核心概念/模式
    ├── entities/          # — 重要实体/工具/人物
    └── summaries/         # — 技术文档摘要
```

**工作量**: 每个大型包 ~1h，中型 ~45min，小型 ~30min

### Phase B: 健康度检测

全量 SQS 运行 + 按 pack 统计健康度：

| 指标 | 当前 | 目标 |
|:-----|:----:|:----:|
| CHI | 0.6355 | ≥ **0.85** |
| SQS 平均分 | 67.9 | ≥ **80** |
| 低分项占比 | 47% | ≤ **15%** |

### Phase C: 合并/清理

运行 `skill-tree-index.py --consolidate` 识别重叠 skill：
- 完全重复 → 合并（保留高质量版本）
- 部分重叠 → 内容取并集
- 低分废弃 → 标记 deprecated 或删除

## 参考

- `~/projects/hermes-cap-pack/docs/EPIC-004-quality-upgrade.md` — 完整规划文档
- `capability-pack-design` §六 健康诊断方法论
- `capability-pack-design` §四-D 合并工作流
