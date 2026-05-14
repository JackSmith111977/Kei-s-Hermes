# hermes-cap-pack 项目数据源参考

> 在为此项目生成报告时使用的数据源和命令。作为 `project-report-generator` skill Phase 1 的参考模板。

## 数据源清单

| 数据 | 位置 | 获取命令 |
|:-----|:-----|:---------|
| 项目元数据 | `docs/project-report.json` | `python3 -c "import json; print(json.load(open('...')))"` |
| SQS 评分 | `~/.hermes/data/skill-quality.db` (SQLite) | `python3 -c "import sqlite3; conn=sqlite3.connect('...')"` |
| SQS 趋势 | `score_history` 表 | `SELECT DATE(scored_at), AVG(sqs_total) FROM score_history GROUP BY 1 ORDER BY 1` |
| SQS 5 维 | `scores` 表的 s1~s5 列 | `SELECT AVG(s1), AVG(s2), AVG(s3), AVG(s4), AVG(s5) FROM scores` |
| SDD 文档 | `docs/*.md` + `docs/stories/*.md` | `ls docs/EPIC-*.md docs/SPEC-*.md && ls docs/stories/STORY-*.md \| wc -l` |
| Git 状态 | `.git/` | `git log --oneline \| wc -l && git describe --tags --always` |
| 测试状态 | `scripts/tests/` | `python3 -m pytest scripts/tests/ -q \| tail -5` |
| 脚本统计 | `scripts/*.py` | `ls scripts/*.py \| wc -l && wc -l scripts/*.py \| tail -1` |
| CI 状态 | `.github/workflows/ci.yml` | 文件存在性检查 |

## 常见查询模式

### SQS 分布
```python
low = c.execute('SELECT COUNT(*) FROM scores WHERE sqs_total < 50').fetchone()[0]
mid = c.execute('SELECT COUNT(*) FROM scores WHERE sqs_total >= 50 AND sqs_total < 70').fetchone()[0]
high = c.execute('SELECT COUNT(*) FROM scores WHERE sqs_total >= 70').fetchone()[0]
```

### Top / Bottom 技能
```python
top = c.execute('SELECT skill_name, sqs_total FROM scores ORDER BY sqs_total DESC LIMIT 5').fetchall()
bot = c.execute('SELECT skill_name, sqs_total FROM scores ORDER BY sqs_total ASC LIMIT 5').fetchall()
```

## 注意事项
- SQLite 表 `scores` 的维度列名为 `s1`~`s5`（不是 `d1`~`d5`）
- s1=结构完整性, s2=内容质量, s3=时效新鲜度, s4=关联完整性, s5=可发现性
- `project-report.json` 的 `sprints` 和 `epics[].stories[]` 可能过期——优先从 git 和文档扫描获取
