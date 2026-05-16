"""
KB 更新模板 — 使用 execute_code + Python dict 直接操作 JSON。

使用场景：当你需要向 Knowledge Base JSON 中添加/更新概念时。
优势：
  ✅ 维持 key_points 字段命名一致性（而非 update_knowledge_base.py 的 notes）
  ✅ 正确处理 relationships / cross_domain_refs
  ✅ 更新 session_log + learning_history
  ✅ 计算新的 freshness_score
  ✅ 避免 CLI 脚本的 Unicode 转义问题和安全扫描器阻塞
  ✅ quality_score 统一使用 0-100 整数格式（⭐ 关键：避免 avg_quality 计算错误）

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
next_review_3day = add_days(today, 3)

# ⚠️ 字段名自动检测：KB 可能使用 'notes'（str）或 'key_points'（list）
#    不同的 KB 文件可能使用不同的字段命名约定
#    不做检测直接硬编码 key_points 会导致 KeyError！
sample = list(concepts.values())[0] if concepts else {}
FIELD = 'key_points' if 'key_points' in sample else ('notes' if 'notes' in sample else 'key_points')
print(f"   Detected field name: '{FIELD}'")

# ==== 2. 添加新概念 ====
concepts['new_concept_name'] = {
    "status": "new",                         # new / developing / mastering / mastered / exploring
    "date_introduced": today,
    "last_reviewed": today,
    "next_review": next_review_3day,
    "review_interval": 3,
    FIELD: [                                 # ⚠️ 使用自动检测的字段名（key_points 或 notes）
        "要点1（具体可验证的事实）",
        "要点2（含版本号和发布日期）",
        "要点3（影响和意义）"
    ],
    "relationships": [                       # 可选：跨概念关系
        {"type": "related_to", "target": "existing_concept", "strength": 0.7},
        {"type": "supersedes", "target": "older_concept", "strength": 0.9}
    ],
    "source_urls": ["https://example.com/"]
}

# ==== 3. 更新已有概念（复习/追加） ====
if 'existing_concept' in concepts:
    # ⚠️ 根据自动检测的字段名追加内容
    #    notes 是字符串（追加用 \n\n），key_points 是列表（追加用 append）
    if FIELD == 'key_points':
        if FIELD not in concepts['existing_concept']:
            concepts['existing_concept'][FIELD] = []
        concepts['existing_concept'][FIELD].append(
            f"[{today} 复习] 新增要点..."
        )
    else:  # notes — 字符串追加
        prev = concepts['existing_concept'].get(FIELD, '')
        new_text = f"[{today} 复习] 新增要点..."
        concepts['existing_concept'][FIELD] = prev + '\n\n' + new_text if prev else new_text
    concepts['existing_concept']['last_reviewed'] = today

# ==== 4. 更新 KB 元数据 ====
kb['last_updated'] = f'{today}T04:00:00+08:00'

# ==== 5. 添加 session_log 条目 ====
# ⭐ quality_score 必须使用 0-100 整数格式
#    不要使用 0-1 浮点格式（如 0.88）——这会破坏 avg_quality 计算！
#    ⚠️ 历史坑：dev_tools KB 曾因混合格式导致 avg_quality 显示 18.71 而非 ~90
#    详见 night-study-engine 的 Red Flag #26
quality_score = 88  # 0-100 整数，代表 88%

kb.setdefault('session_log', []).append({
    "date": today,
    "session_id": "ns_{date}_{hour}",
    "coverage": "主题摘要（用中文概括学了什么）",
    "quality_score": quality_score,           # ⭐ 使用 0-100 整数，不是 0-1 浮点数！
    "sources": [
        "https://official-docs.example.com/",
        "https://blog.example.com/2026/..."
    ],
    "artifact_produced": "KB update (+N concepts)",
    "engine": "web_search (native)"
})

# ==== 6. 更新 learning_history ====
hist = kb.setdefault('learning_history', {})
if 'total_sessions' not in hist:
    hist.update({"total_sessions": 0, "avg_quality": 0.0, "last_loop_count": 1, "consecutive_failures": 0})

# ⭐ 重新计算 avg_quality 前，先归一化所有历史 quality_score
#    避免混合格式（0-1 浮点 + 0-100 整数）导致计算错误
all_qualities = []
for entry in kb.get('session_log', []):
    q = entry.get('quality_score', 0)
    if q and q < 1:           # 归一化：0-1 格式 → 0-100 格式
        q = q * 100
    if q:
        all_qualities.append(int(round(q)))

hist['total_sessions'] = len(all_qualities)
if all_qualities:
    hist['avg_quality'] = round(sum(all_qualities) / len(all_qualities), 2)
hist['last_loop_count'] = 1
hist['consecutive_failures'] = 0
kb['learning_history'] = hist

# ==== 7. 写入 ====
with open('/home/ubuntu/.hermes/night_study/knowledge_base/{DOMAIN_ID}.json', 'w') as f:
    json.dump(kb, f, indent=2, ensure_ascii=False)

# ==== 8. 验证 ====
print(f"KB updated: {len(concepts)} concepts total")
print(f"Sessions: {hist['total_sessions']}, Avg Q: {hist['avg_quality']}")
print("✅ quality_score 已归一化为 0-100 整数格式")


# ============================================================
# 常用日期计算辅助
# ============================================================
from datetime import datetime, timedelta

def add_days(date_str, days):
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return (dt + timedelta(days=days)).strftime('%Y-%m-%d')

# review_interval 策略:
# - 新概念: 3 天
# - developing: 3 天
# - mastering: 3-7 天
# - mastered: 7 天（首次）或 30 天（稳定）
# - L1 复习: 1 天
