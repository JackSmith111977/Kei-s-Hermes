# SDD 工作流实战记录 — SRA-004-01

> 2026-05-11 | 首次完整走通 SDD 六阶段生命周期
> 关联: `sdd-workflow` SKILL.md | `development-workflow-index` §8

---

## 任务概述

将 `sdd-workflow` skill 集成到 SRA 的 `sra-dev-workflow` skill 中：
- 添加 `sdd-workflow` 到 depends_on
- 用 `spec-gate.py enforce` 替换 Phase 1.6 的手动检查
- 引用 `docs/STORY-TEMPLATE.md` 模板

## 完整时间线

| 阶段 | 时间 | 操作 | 状态 |
|:-----|:-----|:-----|:-----|
| **CREATE** | 20:51 | 创建 `docs/stories/SRA-004-01.md` + `spec-state.py create` | draft |
| **SUBMIT** | 20:51 | `spec-state.py submit SRA-004-01` | review |
| **APPROVE** | 21:35 | 主人批准 | approved |
| **START** | 21:35 | `spec-state.py start SRA-004-01` | in_progress |
| **IMPLEMENT** | 21:35-21:36 | 2 个 Task（depends_on + Phase 1.6 门禁） | — |
| **COMPLETE** | 21:36 | `spec-state.py complete SRA-004-01` | completed |
| **ARCHIVE** | 21:36 | `spec-state.py archive SRA-004-01` | archived |

**总耗时: 45 分钟**

## 关键命令记录

```bash
# 创建
cp docs/STORY-TEMPLATE.md docs/stories/SRA-004-01.md
# 编辑填充 frontmatter + AC...
python3 scripts/spec-state.py create "SRA-004-01" "标题" ~/projects/sra/docs/stories/SRA-004-01.md

# 验证完整性
python3 scripts/spec-gate.py verify "SRA-004-01"

# 提交审阅
python3 scripts/spec-state.py submit "SRA-004-01"

# 批准后开发
python3 scripts/spec-state.py approve "SRA-004-01"
python3 scripts/spec-state.py start "SRA-004-01"

# 实现 Task 1: depends_on
# → patch sra-dev-workflow/SKILL.md 加入 sdd-workflow

# 实现 Task 2: Phase 1.6 门禁
# → 替换为 spec-gate.py enforce "<task>" + exit code 检查

# 验证所有 AC
grep "sdd-workflow" ~/.hermes/skills/dogfood/sra-dev-workflow/SKILL.md
grep "spec-gate.py" ~/.hermes/skills/dogfood/sra-dev-workflow/SKILL.md
grep "STORY-TEMPLATE" ~/.hermes/skills/dogfood/sra-dev-workflow/SKILL.md
cd ~/projects/sra && python -m pytest tests/ -q

# 完成归档
python3 scripts/spec-state.py complete "SRA-004-01"
python3 scripts/spec-state.py archive "SRA-004-01"
```

## 发现的问题 & 改进

1. **Spec 文件必须先手动创建再初始化**：`spec-state.py create` 不会自动创建 Spec 文件。流程是先 `cp` 模板再 `create`。
2. **`spec-gate.py` 的 SEARCH_PATHS 硬编码**：目前只搜了 `~/projects/sra/`。多项目时需要扩展。
3. **`spec-state.py approve` 自动更新 Spec 文件状态**：✅ 工作正常，会同步更新 frontmatter 的 `status` 字段。
4. **完整性检查 7/7 通过**：story_id / status / AC / user_story / test_data / out_of_scope / spec_references 全部覆盖。

## 模板

本次使用的 Story Spec 文件: `docs/stories/SRA-004-01.md`（可复用为模板参考）
