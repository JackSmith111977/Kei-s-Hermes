#!/usr/bin/env python3
"""
Bangumi API Query Script v1.0
支持功能：新番表、排行榜、搜索
依赖：requests (预装于 /usr/bin/python3.12)
"""

import requests
import sys
import json

# API 配置
BASE_URL = "https://api.bgm.tv/v0"
HEADERS = {
    # ⚠️ 重要：User-Agent 是必须的，否则会被 403
    "User-Agent": "boku/hermes-agent/1.0.0 (Contact: ubuntu@hermes)",
    "Accept": "application/json"
}

def format_anime_list(animes):
    """格式化输出番剧列表"""
    md = ""
    for item in animes:
        # 标题：优先中文名
        title = item.get('name_cn') or item.get('name')
        url = item.get('url', '#')
        
        # 评分
        rating = item.get('rating', {}).get('score', 'N/A')
        
        # 日期
        date = item.get('date', '未知日期')
        
        # 标签 (取前3个)
        tags = [t['name'] for t in item.get('tags', []) if t['count'] > 10][:3]
        tag_str = ", ".join(tags) if tags else "无标签"
        
        # 简介
        summary = item.get('summary', '暂无简介')
        if len(summary) > 100:
            summary = summary[:100] + "..."
            
        md += f"### 📺 [{title}]({url})  ⭐ {rating}\n"
        md += f"> **首播**: {date} | **标签**: {tag_str}\n"
        md += f"> {summary}\n\n"
    return md

def get_calendar():
    """获取本周新番表"""
    try:
        # 旧版 API 的 calendar 可能更稳定，或者使用新版的
        # 根据搜索结果，新版是 /calendar (GET)
        r = requests.get(f"https://api.bgm.tv/calendar", headers=HEADERS)
        if r.status_code != 200:
            return f"❌ Error: {r.status_code} {r.text}"
            
        data = r.json()
        days_map = {"Mon": "周一", "Tue": "周二", "Wed": "周三", "Thu": "周四", "Fri": "周五", "Sat": "周六", "Sun": "周日"}
        
        md = "## 📅 本周新番放送表\n\n"
        
        # 按顺序排列
        order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        for day_en in order:
            # API 返回的是一个列表，每个元素有 weekday.en
            day_data = next((d for d in data if d['weekday']['en'] == day_en), None)
            if day_data:
                day_cn = days_map.get(day_en, day_en)
                md += f"### {day_cn}\n"
                items = day_data.get('items', [])
                for item in items:
                    title = item.get('name_cn') or item.get('name')
                    if title:
                        md += f"- [{title}]({item['url']})\n"
                md += "\n"
        
        return md
    except Exception as e:
        return f"❌ Exception: {e}"

def get_rank(limit=10):
    """获取排行榜"""
    try:
        # GET /v0/subjects
        params = {"type": 2, "sort": "rank", "limit": limit}
        r = requests.get(f"{BASE_URL}/subjects", params=params, headers=HEADERS)
        if r.status_code != 200:
            return f"❌ Error: {r.status_code}"
        
        results = r.json().get('data', [])
        return "## 🏆 Bangumi 动画排行榜 (Top {})\n\n".format(limit) + format_anime_list(results)
    except Exception as e:
        return f"❌ Exception: {e}"

def search(keyword, limit=10):
    """搜索番剧"""
    try:
        url = f"{BASE_URL}/search/subjects"
        payload = {
            "keyword": keyword,
            "filter": {
                "type": [2], # 2 = 动画
                "sort": "rank"
            }
        }
        r = requests.post(url, json=payload, headers=HEADERS)
        if r.status_code != 200:
            return f"❌ Error: {r.status_code} {r.text}"
            
        results = r.json().get('data', [])
        if not results:
            return f"🔍 未找到与 '{keyword}' 相关的动画。"
            
        return f"## 🔍 搜索结果：'{keyword}'\n\n" + format_anime_list(results)
    except Exception as e:
        return f"❌ Exception: {e}"

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if action == "calendar":
        print(get_calendar())
    elif action == "rank":
        print(get_rank(limit=10))
    elif action == "search":
        kw = sys.argv[2] if len(sys.argv) > 2 else ""
        if not kw:
            print("Usage: python query_bangumi.py search <keyword>")
        else:
            print(search(kw))
    else:
        print("Usage:")
        print("  python query_bangumi.py calendar   - 获取本周新番表")
        print("  python query_bangumi.py rank       - 获取排行榜")
        print("  python query_bangumi.py search <q> - 搜索番剧")
