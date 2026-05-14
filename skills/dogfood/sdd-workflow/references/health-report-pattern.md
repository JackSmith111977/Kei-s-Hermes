# 健康报告模式 — 工具组合与智能简报

> 由 EPIC-002 Sprint 2 实战沉淀 (2026-05-14)

## 模式概述

当需要生成技能系统的周期性健康度报告时，使用此模式。核心思路是**避免全量审计的时间开销**，改用树状索引的快速 JSON 输出作为数据源。

## 工具选择决策

```
需要全量健康数据？
├── 是 → skill-tree-index.py --json（~3s ✅）
│         ↓
│   解析 JSON list，提取：total_skills, micro_skills, unclassified, module_breakdown
│         ↓
│   对比上次状态 → 检测退化
│
└── 否 → 单个 skill 审计 → skill-lifecycle-audit.py <name>（~1s ✅）

需要全量 lifecycle 状态？
├── 是 → 慎用！--audit 超时风险
│   替代方案: tree-index --json 获取技能列表，逐条 lifecycle status
│   或: 只对有变化的 skill 运行 lifecycle-audit
└── 否 → 直接用
```

## 推荐脚本骨架

```python
# 1. 获取 JSON
tree_result = run_script("skill-tree-index.py", "--json")
tree_data = json.loads(tree_result.stdout)

# 2. 提取指标
total_skills = sum(m.get("total_skills", 0) for m in tree_data)
micro_skills = sum(1 for m in tree_data for c in m.get("clusters", [])
                   for s in c.get("skills", []) if s.get("line_count", 999) < 50)
unclassified = next((m.get("total_skills", 0) for m in tree_data
                     if m.get("module_id") == "unclassified"), 0)

# 3. 退化检测（对比上次存储的状态）
issues = []
if curr_total < prev_total: issues.append(...)
if curr_micro > prev_micro: issues.append(...)

# 4. 智能简报切换
is_full = len(issues) > 0 or "--full" in sys.argv
# 无退化→精简版（仅概览），有退化→完整版（含模块分布 Top 5）
```

## 状态持久化

退化检测需要跨次运行的状态比较。推荐用 `~/.hermes/health-report-state.json`：

```json
{
  "total_skills": 200,
  "micro_skills": 7,
  "unclassified": 41,
  "generated_at": "2026-05-14T08:21:00"
}
```

## Cron 配置

```bash
# 每周日 09:00 自动执行 → 飞书推送
cronjob action=create name=weekly-health-report \
  schedule="0 9 * * 0" script=health-report.py \
  deliver=feishu no_agent=true

# 手动触发
cronjob action=run job_id=<id>
```

## 已知限制

| 限制 | 说明 | 缓解 |
|:-----|:------|:------|
| `--json` 不含 lifecycle 状态 | 树状索引只输出名称/版本/SQS/行数 | 退化检测基于总量对比而非 lifecycle audit |
| 首次运行无基线 | 无法检测退化 | 首次仅输出概览，第二次开始对比 |
| 脚本需在 `~/.hermes/scripts/` | cron 不允许符号链接 | `cp` 实际文件到目标目录 |

## 产出文件

cap-pack 项目中的参考实现：
- `scripts/health-report.py` — 完整实现（含智能简报/退化检测）
- `~/.hermes/scripts/health-report.py` — cron 部署副本
