# Skill Auto-Link 集成参考

## 位置
`~/.hermes/scripts/skill-auto-link.py`

## 作用
在学习流程(learning-workflow)的 STEP 6 完成后自动执行。当学习任务创建了新 skill，此脚本扫描全部 284 个已有 skill，自动建立 bidirectional `related_skills` 引用。

## 命令速查

| 命令 | 用途 |
|:----|:------|
| `auto-link <skill>` | 为新 skill 自动关联（写入 related_skills） |
| `auto-link <skill> --dry-run` | 预览关联建议 |
| `merge-detect [threshold=70]` | 检测重合度≥threshold%的skill对 |
| `full-scan` | 全量扫描并报告 |
| `report` | 关联状态报告 |
| `score <a> <b>` | 查两个 skill 的关联度 |

## 评分算法
点积法：每命中一个维度就加分（不按比例），最高100分。
- 名称命中：15分
- 标签命中：20分（含同义词扩展）
- 触发词命中：15分
- 分类匹配：10分
- 已有关联：15分
- 正文关键词重叠：最高25分（按重叠词数量分档）

## 当前状态 (2026-05-09)
- 284 个 skill 已扫描
- 69 个有关联关系(24%)
- 174 条总关联引用
- web-ui-ux-design 是最新关联中心(12引用)
- 14 对建议合并的skill pair
- 192 个孤立skill待审查
