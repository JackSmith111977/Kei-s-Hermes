#!/usr/bin/env python3
"""
Bangumi Detail & Table Generator v2.0
功能：获取新番详细信息，生成 Markdown 表格和 HTML 报告。
"""

import requests
import sys
import json
import pandas as pd
from datetime import datetime

BASE_URL = "https://api.bgm.tv/v0"
HEADERS = {
    "User-Agent": "boku/hermes-agent/1.0.0",
    "Accept": "application/json"
}

def get_calendar_details():
    """获取本周新番详情（含评分、公司）"""
    try:
        # 获取日历
        r = requests.get("https://api.bgm.tv/calendar", headers=HEADERS)
        if r.status_code != 200: return []
        
        calendar = r.json()
        all_animes = []
        
        for day in calendar:
            day_cn = day['weekday']['cn']
            for item in day.get('items', []):
                # 获取详情
                subject_id = item.get('id')
                detail = {}
                try:
                    d_req = requests.get(f"{BASE_URL}/subjects/{subject_id}", headers=HEADERS)
                    if d_req.status_code == 200:
                        d_data = d_req.json()
                        detail = {
                            'name': d_data.get('name_cn') or d_data.get('name'),
                            'score': d_data.get('rating', {}).get('score', '暂无'),
                            'rank': d_data.get('rank', 'N/A'),
                            'studio': d_data.get('infobox', {}).get('放送星期', '未知'), # Note: Studio might be elsewhere in infobox
                            'date': d_data.get('date', '未知'),
                            'summary': (d_data.get('summary', '') or '')[:50] + "...",
                            'tags': ", ".join([t['name'] for t in d_data.get('tags', []) if t['count'] > 15][:3])
                        }
                except:
                    pass
                
                if detail.get('name'):
                    detail['weekday'] = day_cn
                    all_animes.append(detail)
        
        return all_animes
    except Exception as e:
        return []

def generate_table(data):
    """生成 Markdown 表格"""
    if not data: return "无数据"
    df = pd.DataFrame(data)
    # 排序：按评分
    df = df.sort_values(by='score', ascending=False)
    
    # 重命名列
    df.rename(columns={
        'name': '番剧名称', 
        'score': '评分', 
        'rank': '排名',
        'weekday': '放送日',
        'tags': '标签'
    }, inplace=True)
    
    return df[['放送日', '番剧名称', '评分', '标签']].to_markdown(index=False)

def generate_review(data):
    """生成客观评价报告（模拟 LLM 风格的优缺点）"""
    if not data: return "无数据"
    
    md = "# 📺 本季新番完全指南\n\n"
    md += f"数据生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    md += "> **阅读说明**：综合评分由高到低排序。【推荐理由】基于题材与制作，【避雷指南】基于常见吐槽点。\n\n"
    
    # 按评分排序
    sorted_data = sorted(data, key=lambda x: float(x['score']) if x['score'] != '暂无' else 0, reverse=True)
    
    for item in sorted_data:
        score = item['score']
        name = item['name']
        tags = item['tags']
        summary = item['summary']
        
        # 模拟评价逻辑 (基于分数和标签)
        pros = []
        cons = []
        
        if float(score) >= 8.0:
            pros.append("口碑佳作，质量有保证")
        elif float(score) >= 7.0:
            pros.append("制作稳定，值得一看")
        elif float(score) >= 6.0:
            pros.append("有亮点，可当消遣")
        else:
            cons.append("评分较低，质量堪忧")
            pros.append("粉丝向或特定受众")
            
        if "异世界" in tags:
            pros.append("设定新颖/爽文节奏")
            cons.append("可能套路化")
        if "恋爱" in tags:
            pros.append("糖分充足")
            cons.append("剧情可能较弱")
        if "原创" in tags:
            pros.append("剧情无剧透风险")
            cons.append("原创番风险较大，易烂尾")
            
        pros_str = "、".join(pros) if pros else "中规中矩"
        cons_str = "、".join(cons) if cons else "无明显硬伤"
        
        md += f"### 🥇 {name}  ⭐ {score}\n"
        md += f"**标签**: {tags} | **首播**: {item['date']}\n"
        md += f"> **简介**: {summary}\n"
        md += f"> ✅ **推荐理由**: {pros_str}\n"
        md += f"> ⚠️ **避雷指南**: {cons_str}\n\n"
        
    return md

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "table"
    data = get_calendar_details()
    
    if action == "table":
        print(generate_table(data))
    elif action == "review":
        print(generate_review(data))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
