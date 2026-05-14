# 🔀 Cap-Pack 模块合并模式

> 来源: 2026-05-14 knowledge-base → learning-engine 实际合并
> 相关 skill: project-report-generator, doc-alignment, sdd-workflow

## 合并触发条件

| 条件 | 示例 | 决策 |
|:-----|:-----|:-----|
| 核心技能已被另一个 pack 吸收 | knowledge-precipitation, knowledge-routing 已在 learning-engine | ⚡ 合并 |
| 包间存在循环依赖 | learning-engine → knowledge-base, knowledge-base → ... | ⚡ 合并 |
| 独立包只有 2-3 个独特技能 | knowledge-base 合并后只剩 memory-management 等 | ⚡ 合并 |
| 两个包方法论紧密耦合 | 知识沉淀与学习研究不可分割 | ⚡ 合并 |

## 合并流程（7 步）

```text
Step 1 ── 决策记录
  - 在 SPEC-1-1 模块分割方案中添加 [^1] 脚注
  - 在 EPIC-003 提取路线图中添加 ⚡ 行
  - 在 README 中添加脚注说明
  
Step 2 ── 更新 learning-engine/cap-pack.yaml
  - 移除对 knowledge-base 的 dependencies 引用
  - 添加注释: "# ⚡ knowledge-base 已合并至此包"
  
Step 3 ── 更新模块表（6 份文档）
  - SPEC-1-1: 模块表 + 分层图 + cap-pack 示例全部更新
  - EPIC-003-module-extraction: Phase 2 表 + 路线图 + KPI
  - EPIC-003-comprehensive-roadmap: 全景表 + Phase 5 + 依赖图 + KPI
  - SPEC-3-3: 模块 5 改为 learning-engine(含知识库)
  - SPEC-2-3: SRA 分类别名合并
  - README: 包列表 + 覆盖统计

Step 4 ── 更新 project-report.json
  - 模块数 18+3 → 17+3
  - 去掉 knowledge-base 行
  - 更新覆盖百分比 (37% 7/19 → 47% 8/17)

Step 5 ── 更新 PROJECT-PANORAMA.html
  - 添加合并注释醒目框
  - 更新 KPI 卡片
  - 更新包列表

Step 6 ── 更新 project-state.yaml
  - EPIC story_count / completed_count

Step 7 ── git commit
  - 提交信息标注 BREAKING CHANGE
  - 所有文件同一次提交
```

## 合并后必须更新的文件清单

```
✅ packs/<target>/cap-pack.yaml              — 移除依赖 + 注释
✅ docs/SPEC-1-1.md                           — 模块表 + 分层图 + 示例 + [^1]脚注
✅ docs/EPIC-003-module-extraction.md         — Phase 表 + 路线图 + KPI + 脚注
✅ docs/plans/EPIC-003-comprehensive-roadmap.md — 全景表 + Phase 5 + 依赖图 + KPI
✅ docs/SPEC-3-3.md                           — 模块列表 + 执行计划 + AC
✅ docs/SPEC-2-3.md                           — SRA 分类别名合并
✅ README.md                                  — 包列表 + 覆盖统计 + 脚注
✅ docs/project-report.json                   — 模块数 + 覆盖 + 架构
✅ PROJECT-PANORAMA.html                      — 合并注释 + KPI + 包列表
✅ docs/project-state.yaml                    — EPIC/story 计数
```

## 合并注释模板

> **⚡ 合并注释**: `{source}`（原独立模块）已合并至 `{target}`。
> 原因：① 核心技能已在 {target} 提取时吸收；② 消除包间循环依赖；③ 降低管理成本。
> 合并后模块体系从 {old_count} 更新为 **{new_count}**。
> 详见 SPEC-1-1 合并注释 [^1]。
