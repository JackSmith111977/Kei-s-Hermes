# state.db 空间分析报告（2026-05-17）

> Hermes Agent 核心数据库 `~/.hermes/state.db` 的完整空间分析。
> 分析日期：2026-05-17 | 数据采样：~25,000 messages, ~600 sessions

## 核心发现

state.db 的 **459-464MB** 中，大部分是 **FTS 全文检索索引** 的正常占用，不是磁盘泄漏或碎片问题。

## 逐表分析

| 表/索引 | 行数 | 空间(MB) | 占比 | 可否回收 |
|:--------|:----:|:--------:|:----:|:--------:|
| `messages_fts_trigram_data` | 43,307 | **165.1** | 36% | ❌ FTS 索引 |
| `messages_fts_content` × 2 | 50,942 | **152.4** | 33% | ❌ FTS 索引 |
| `messages` | 25,471 | 90.3 | 20% | ✅ 通过 prune |
| `messages_fts_data` | 7,454 | 28.9 | 6% | ❌ FTS 索引 |
| `sessions` | 614 | 20.2 | 4% | ✅ 通过 prune |
| 其他 FTS 辅助索引 | ~59,000 | 1.0 | 0.2% | ❌ |
| 元数据 | 5 | 0 | 0% | — |

**总 FTS 索引空间**：~269MB（58%）
**总数据空间**：~190MB（42%）

## FTS 索引解释

Hermes 使用 SQLite FTS5 的 `trigram` tokenizer 支持全文搜索。trigram tokenizer 将每个词分解为所有可能的 3-gram，因此索引大小通常是原始数据的 3-5 倍。这是预期行为。

`messages_fts_trigram_data`（165MB）是 trigram 倒排索引，是搜索性能的代价。

## 清理效果实测

### 操作 1：VACUUM
```sql
PRAGMA wal_checkpoint(TRUNCATE);  -- 回收 WAL（12MB→0）
VACUUM;                            -- 重建数据库
```
- **前后**：463.8MB → 459.1MB（仅 -4.7MB，占 1%）
- **结论**：freelist 很小（1059 页 / 4.1MB），VACUUM 不是减肥利器

### 操作 2：Sessions Prune（retention_days: 30 → 7）
```bash
# 改配置 + JSON 文件清理 + SQLite prune
find ... -mtime +7 -delete        # JSON: 1,129 → 467 (-662)
hermes sessions prune --older-than 7  # SQLite: 614 → 197 (-417)
```
- **前后**：session JSON 480MB → 270MB（-210MB）
- **messages 表**：25,471 → 8,875（-16,596 条）
- **state.db 变化**：459MB（-5MB，来自 sessions 表和 messages 表记录减少，但 FTS 索引不自动回收）

### 操作 3：FTS 索引重建（不推荐）
```sql
INSERT INTO messages_fts(messages_fts) VALUES('rebuild');
```
- 重建后 FTS 索引可能会略减小，但重建过程需要锁表，代价高
- **结论**：不推荐日常执行，仅在异常膨胀时考虑

## 优化建议

### 短期（每月）
1. ✅ 降低 `retention_days` 到 7 — 阻止 messages 表进一步膨胀
2. ✅ 每月 VACUUM — 回收 freelist（通常 1-5%）
3. ✅ `vacuum_after_prune: true` — prune 后自动回收

### 中期（如果要再减）
4. ⚠️ 考虑降低 FTS 配置（如改为 `content=` 不存储原文，仅索引）
5. ⚠️ 评估是否有必要保留所有 FTS 索引（search 功能是否常用）

### 长期（架构级）
6. 🧠 考虑分库：messages 历史数据归档到独立 SQLite 数据库
7. 🧠 state.db 设置为 `PRAGMA auto_vacuum=1`（增量回收）

## 诊断命令速查

```bash
# 数据库总览
python3 -c "
import sqlite3, os
db = os.path.expanduser('~/.hermes/state.db')
conn = sqlite3.connect(db)
print(f'大小: {os.path.getsize(db)/1024/1024:.0f}MB')
print(f'页数: {conn.execute(\"PRAGMA page_count\").fetchone()[0]}')
print(f'页大小: {conn.execute(\"PRAGMA page_size\").fetchone()[0]}')
print(f'空闲页: {conn.execute(\"PRAGMA freelist_count\").fetchone()[0]}')
conn.close()
"

# 表空间分布
python3 -c "
import sqlite3, os
db = os.path.expanduser('~/.hermes/state.db')
conn = sqlite3.connect(db)
cur = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
for t in cur.fetchall():
    name = t[0]
    count = conn.execute(f'SELECT COUNT(*) FROM \"{name}\"').fetchone()[0]
    pages = conn.execute(f'SELECT SUM(pgsize) FROM dbstat WHERE name=\"{name}\"').fetchone()[0]
    if pages:
        print(f'{name:40s} {count:>8} rows  {pages/1024/1024:>7.1f}MB')
conn.close()
"

# WAL 状态
python3 -c "
import sqlite3, os
db = os.path.expanduser('~/.hermes/state.db')
conn = sqlite3.connect(db)
r = conn.execute('PRAGMA wal_checkpoint').fetchone()
print(f'WAL: {r}')
conn.close()
"
```
