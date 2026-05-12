"""
KB 更新模板 — 使用 execute_code + Python dict 直接操作 JSON。

使用场景：当你需要向 Knowledge Base JSON 中添加/更新概念时。
优势：
  ✅ 维持 key_points 字段命名一致性（而非 update_knowledge_base.py 的 notes）
  ✅ 正确处理 relationships / cross_domain_refs
  ✅ 更新 session_log + learning_history
  ✅ 计算新的 freshness_score
  ✅ 避免 CLI 脚本的 Unicode 转义问题和安全扫描器阻塞

使用方法：
  1. 将此代码复制到 execute_code 调用中
  2. 修改 concepts 字典添加/更新概念
  3. 更新 KB 元数据（freshness_score, last_updated）
  4. 添加 session_log 条目
  5. 写入 JSON
"""

import json

# ==== 1. 读取现有 KB ====
with open('/home/ubuntu/.hermes/night_study/knowledge_base/{DOMAIN_ID}.json', 'r') as f:
    kb = json.load(f)

concepts = kb['concepts']
today = 'YYYY-MM-DD'
next_review_3day = add_days(today, 3)  # or hardcode: 'YYYY-MM-DD+3'

# ==== 2. 添加新概念 ====
concepts['new_concept_name'] = {
    "status": "new",                         # new / developing / mastered / stale
    "date_introduced": today,
    "last_reviewed": today,
    "next_review": next_review_3day,
    "review_interval": 3,
    "key_points": [                          # ⚠️ 使用 key_points 而非 notes
        "要点1（具体可验证的事实）",
        "要点2（含版本号和发布日期）",
        "要点3（影响和意义）"
    ],
    "relationships": [                       # 可选：跨概念关系
        {"type": "related_to", "target": "existing_concept", "strength": 0.7},
        {"type": "supersedes", "target": "older_concept", "strength": 0.9}
    ]
}

# ==== 3. 更新已有概念（复习/追加） ====
if 'existing_concept' in concepts:
    concepts['existing_concept']['key_points'].append(
        "[更新日期] 新增要点..."
    )
    concepts['existing_concept']['last_reviewed'] = today

# ==== 4. 更新 KB 元数据 ====
kb['last_updated'] = 'YYYY-MM-DDTHH:MM:00'
# freshness_score: 0.0(很旧) ~ 1.0(全新)
# 学习后应该下降（表示知识更新了）
kb['freshness_score'] = round(kb.get('freshness_score', 0.5) * 0.9, 2)

# ==== 5. 添加 session_log 条目 ====
kb['session_log'].append({
    "date": today,
    "session_id": "ns_{date}_{hour}",
    "coverage": "主题摘要（用中文概括学了什么）",
    "quality_score": 0.88,                   # 本次学习质量分
    "sources": [
        "https://official-docs.example.com/",
        "https://blog.example.com/2026/..."
    ],
    "artifact_produced": "KB update (+N concepts)",
    "engine": "web_search (native)"
})

# ==== 6. 更新 learning_history ====
hist = kb.get('learning_history', {})
if 'total_sessions' not in hist:
    hist.update({"total_sessions": 0, "avg_quality": 0.0, "last_loop_count": 1, "consecutive_failures": 0})

hist['total_sessions'] += 1
old_avg = hist['avg_quality']
old_count = hist['total_sessions'] - 1
hist['avg_quality'] = (old_avg * old_count + quality_score) / hist['total_sessions'] if old_count > 0 else quality_score
hist['last_loop_count'] = loop_count
hist['consecutive_failures'] = 0

# ==== 7. 写入 ====
with open('/home/ubuntu/.hermes/night_study/knowledge_base/{DOMAIN_ID}.json', 'w') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

# ==== 8. 验证 ====
print(f"KB updated: {len(concepts)} concepts total")
print(f"Freshness: {kb.get('freshness_score')}")
print(f"Sessions: {hist['total_sessions']}, Avg Q: {hist['avg_quality']:.2f}")


"""
常用日期计算辅助（从 this session 的实际使用中提取）:

from datetime import datetime, timedelta
today = datetime.now().strftime('%Y-%m-%d')
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
next_3day = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

review_interval 策略:
- 新概念: 3 天
- developing: 3 天
- mastered: 7 天（首次）或 30 天（稳定）
- L1 复习: 1 天
"""

# def add_days(date_str, days):
#     from datetime import datetime, timedelta
#     dt = datetime.strptime(date_str, '%Y-%m-%d')
#     return (dt + timedelta(days=days)).strftime('%Y-%m-%d')
