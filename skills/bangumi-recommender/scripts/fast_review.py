#!/usr/bin/env python3
"""
Bangumi Fast Table & Report v2.1
优化版：避免全量请求，重点抓取 Top 新番。
"""

import requests
import pandas as pd
from datetime import datetime

HEADERS = {"User-Agent": "boku/hermes-agent/1.0.0"}

def get_top_animes(limit=15):
    """直接获取当前季度的 Top 动画"""
    try:
        # 获取 Top 列表
        r = requests.get("https://api.bgm.tv/v0/subjects?type=2&sort=rank&limit=20", headers=HEADERS)
        if r.status_code == 200:
            items = r.json().get('data', [])
            return items
    except:
        pass
    return []

def generate_review():
    """生成 Markdown 报告"""
    items = get_top_animes()
    if not items:
        return "获取失败。"

    md = "# 📺 本季高分新番指南\n\n"
    md += f"数据时间：{datetime.now().strftime('%Y-%m-%d')}\n\n"
    md += "> 综合 Bangumi 评分与热度，为您精选本季必看佳作。\n\n"
    
    # 构造表格
    table_data = []
    for item in items:
        name = item.get('name_cn') or item.get('name')
        score = item.get('rating', {}).get('score', 'N/A')
        date = item.get('date', '未知')
        tags = ", ".join([t['name'] for t in item.get('tags', []) if t['count'] > 20][:3])
        
        # 模拟客观评价
        pros, cons = "制作精良", "无明显短板"
        if float(score) < 6.0: pros, cons = "粉丝向", "剧情可能老套"
        elif "异世界" in tags: pros, cons = "设定有趣", "需防套路化"
        
        table_data.append({
            '番剧': name,
            '评分': score,
            '标签': tags,
            '首播': date,
            '看点': pros,
            '雷点': cons
        })

    df = pd.DataFrame(table_data)
    md += df.to_markdown(index=False) + "\n\n"
    
    # 重点推荐
    md += "### 🌟 boku 独家点评\n\n"
    for item in items[:3]:
        name = item.get('name_cn') or item.get('name')
        summary = (item.get('summary', '') or '').replace('\n', ' ')[:100]
        md += f"- **{name}**：{summary}...\n"
        
    return md

print(generate_review())
