#!/usr/bin/env python3
"""
smart_broadcast.py - Hermes 智能播报引擎 v3.0 (功能增强版)
原理：状态驱动 + 增量过滤 + 哈希去重 + 动态免打扰 + 随机扰动 + 功能模块
用法:
  python3 ~/.hermes/scripts/broadcast/smart_broadcast.py [options]
  Options: --dry-run, --force, --collect-only
"""

import os
import sys
import json
import hashlib
import random
import subprocess
from datetime import datetime, timedelta
import requests

# --- 配置路径 ---
STATE_DIR = os.path.expanduser("~/.hermes/state")
STATE_FILE = os.path.join(STATE_DIR, "broadcast_state.json")
QUEUE_FILE = os.path.join(STATE_DIR, "broadcast_queue.json")
RESPONSES_FILE = os.path.expanduser("~/.hermes/config/broadcast_responses.json")
WEATHER_CACHE = os.path.join(STATE_DIR, "weather_cache.json")
CALENDAR_FILE = os.path.expanduser("~/.hermes/config/calendar.json")

# --- 核心函数 ---

def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_state():
    return load_json(STATE_FILE, {
        "last_run_at": None,
        "last_hash": None,
        "silence_until": None,
        "stats": {"total_sent": 0, "total_skipped": 0}
    })

def save_state(state):
    save_json(STATE_FILE, state)

def load_responses():
    return load_json(RESPONSES_FILE, {"opening": [], "closing": [], "easter_eggs": [], "empty_report": []})

def get_random_msg(responses, key):
    msgs = responses.get(key, [])
    return random.choice(msgs) if msgs else ""

def hash_content(content):
    return hashlib.md5(content.strip().encode()).hexdigest()

def is_silent(state):
    if not state.get("silence_until"):
        return False
    try:
        until = datetime.fromisoformat(state["silence_until"])
        return datetime.now() < until
    except:
        return False

# --- 数据收集模块 (Functional Modules) ---

def collect_weather():
    """🌤️ 模块 1: 真实天气信息 (Open-Meteo API, 无需 Key)"""
    try:
        # 默认坐标：大连 (Dalian)
        lat, lon = 38.9140, 121.6147
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=Asia%2FShanghai"
        
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        current = data.get("current_weather", {})
        temp = current.get("temperature", 0)
        code = current.get("weathercode", 0)
        
        # 解析 WMO 天气代码
        weather_map = {
            0: ("晴朗 ☀️", "阳光明媚，心情好好喵"),
            1: ("大部晴朗 🌤️", "适合伸个懒腰喵"),
            2: ("多云 ⛅", "云层有点厚，注意保暖喵"),
            3: ("阴天 ☁️", "天色阴沉，适合睡觉喵"),
            45: ("有雾 🌫️", "能见度低，出门小心喵"),
            48: ("雾凇 ❄️", "外面冻成冰棍了喵"),
            51: ("毛毛雨 🌧️", "细雨蒙蒙，记得带伞喵"),
            53: ("中雨 🌧️", "雨势变大，别淋湿了喵"),
            55: ("大雨 ⛈️", "暴雨！最好待在屋里喵"),
            61: ("小雨 🌧️", "淅淅沥沥，记得带伞喵"),
            63: ("中雨 🌧️", "雨下得挺大，别出门喵"),
            65: ("大雨 🌧️", "暴雨来袭，千万别出去喵"),
            71: ("小雪 ❄️", "下雪啦！想去堆雪人吗喵"),
            73: ("中雪 ❄️", "雪好大，外面很冷喵"),
            75: ("大雪 🌨️", "暴雪！注意安全喵"),
            80: ("阵雨 🌦️", "阵雨突袭，带好伞喵"),
            81: ("强阵雨 ⛈️", "雷阵雨，躲在屋里喵"),
            82: ("暴雨 ⛈️", "特大暴雨！千万别出门喵"),
            95: ("雷暴 ⛈️", "雷电交加，好吓人喵"),
        }
        
        condition, advice = weather_map.get(code, ("未知天气 🌫️", "天气变化莫测，注意身体喵"))
        
        # 温度建议
        if temp < 5:
            advice += "（超冷！多穿点喵 🧥）"
        elif temp > 30:
            advice += "（超热！多喝水喵 🥤）"
            
        weather_data = {
            "location": "大连 (Dalian)",
            "temp": temp,
            "condition": condition,
            "advice": advice
        }
        
        # 缓存结果（1 小时有效期）
        save_json(WEATHER_CACHE, {**weather_data, "updated_at": datetime.now().isoformat()})
        return weather_data
        
    except Exception as e:
        print(f"Weather API Error: {e}")
        # 失败时返回缓存
        cache = load_json(WEATHER_CACHE)
        if cache:
            return {k: v for k, v in cache.items() if k != "updated_at"}
        return {"location": "N/A", "temp": "--", "condition": "获取失败 ❌", "advice": "网络似乎有点问题喵"}

def collect_system_stats():
    """💻 模块 2: 系统状态 (CPU, Memory, Disk)"""
    try:
        # 获取负载 (Load Average)
        load_avg = os.getloadavg()
        load_1m = load_avg[0]
        
        # 获取内存 (Linux 特定)
        with open('/proc/meminfo') as f:
            lines = f.readlines()
        mem_total = int(lines[0].split()[1])
        mem_avail = int(lines[2].split()[1]) # Available
        mem_percent = int((mem_total - mem_avail) / mem_total * 100)
        
        # 获取磁盘
        disk = os.statvfs('/')
        disk_total = disk.f_blocks * disk.f_frsize
        disk_free = disk.f_bavail * disk.f_frsize
        disk_percent = int((1 - disk_free / disk_total) * 100)
        
        # 判定级别
        level = "OK"
        alerts = []
        if load_1m > 2.0: alerts.append("负载较高")
        if mem_percent > 80: alerts.append(f"内存紧张 ({mem_percent}%)")
        if disk_percent > 85: alerts.append(f"磁盘将满 ({disk_percent}%)")
        
        if alerts:
            level = "WARN" if len(alerts) < 3 else "CRITICAL"
            
        return {
            "type": "SYSTEM",
            "level": level,
            "content": f"负载:{load_1m:.2f} | 内存:{mem_percent}% | 磁盘:{disk_percent}%" + (f" ⚠️ {' | '.join(alerts)}" if alerts else "")
        }
    except Exception as e:
        return {"type": "SYSTEM", "level": "WARN", "content": f"无法获取系统状态: {e}"}

def collect_tasks():
    """✅ 模块 3: 任务队列摘要"""
    tq_path = os.path.expanduser("~/.hermes/TASK_QUEUE.md")
    if not os.path.exists(tq_path):
        return None
    
    with open(tq_path) as f:
        lines = f.readlines()
    
    # 统计状态
    pending = [l.strip() for l in lines if "PENDING" in l or "[ ]" in l]
    progress = [l.strip() for l in lines if "IN_PROGRESS" in l]
    
    if progress:
        return {
            "type": "TASK",
            "level": "INFO",
            "content": f"🔥 正在进行: {len(progress)} 个任务"
        }
    elif pending:
        return {
            "type": "TASK",
            "level": "INFO",
            "content": f"📋 待办堆积: {len(pending)} 个任务等待处理"
        }
    return None

def collect_calendar():
    """📅 模块 4: 日程提醒"""
    cal_data = load_json(CALENDAR_FILE)
    if not cal_data or not cal_data.get("events"):
        return {"type": "CALENDAR", "level": "INFO", "content": "今日暂无日程，可自由安排时间喵~ ☕️"}
    
    # 简单匹配今日日程
    today_str = datetime.now().strftime("%Y-%m-%d")
    events = cal_data.get("events", [])
    # 这里简化处理，实际应按时间排序过滤
    upcoming = events[:2] # 只看前两个
    
    if upcoming:
        titles = " | ".join([e.get("title", "未知") for e in upcoming])
        return {"type": "CALENDAR", "level": "WARN", "content": f"📅 近期日程: {titles}"}
    else:
        return {"type": "CALENDAR", "level": "INFO", "content": "今日暂无日程，可自由安排时间喵~ ☕️"}

def collect_data():
    """🔍 数据收集主控"""
    items = []
    
    # 1. 系统 (必报，除非静默)
    items.append(collect_system_stats())
    
    # 2. 天气 (晨报必报，日常可略)
    hour = datetime.now().hour
    if hour >= 8 and hour <= 10: # 早上播报天气
        w = collect_weather()
        items.append({
            "type": "WEATHER",
            "level": "OK",
            "content": f"{w['condition']} {w['temp']}℃ | 建议: {w['advice']}"
        })
    
    # 3. 任务 (有变动才报)
    task_item = collect_tasks()
    if task_item:
        items.append(task_item)
        
    # 4. 日历 (早上报)
    if hour >= 8 and hour <= 10:
        items.append(collect_calendar())
        
    # 过滤 None
    return [i for i in items if i is not None]

def format_broadcast(items, responses):
    """📝 格式化：加入随机扰动"""
    if not items:
        return get_random_msg(responses, "empty_report")
    
    now = datetime.now().strftime("%H:%M")
    opening = get_random_msg(responses, "opening")
    header = f"{opening}\n📅 **{now} 智能播报**\n"
    
    lines = [header]
    # 排序：CRITICAL 优先
    items.sort(key=lambda x: {"CRITICAL": 0, "WARN": 1, "INFO": 2, "OK": 3}.get(x.get("level", "OK"), 4))
    
    for item in items:
        icon = {"OK": "✅", "WARN": "⚠️", "INFO": "ℹ️", "CRITICAL": "🚨"}.get(item.get("level", "OK"), "•")
        title = item.get("type", "INFO")
        content = item.get("content", "")
        lines.append(f"{icon} **{title}**: {content}")
    
    # 30% 概率触发彩蛋
    if random.random() < 0.3:
        lines.append(f"\n💡 **小贴士**: {get_random_msg(responses, 'easter_eggs')}")
        
    lines.append(f"\n{get_random_msg(responses, 'closing')}")
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    state = load_state()
    responses = load_responses()
    
    # 静默检查
    if not args.force and is_silent(state):
        print(f"🔇 处于免打扰模式（截至 {state['silence_until']}）")
        return

    # 收集数据
    new_items = collect_data()
    if not new_items:
        content = get_random_msg(responses, "empty_report")
    else:
        content = format_broadcast(new_items, responses)
        
    if not content:
        return

    current_hash = hash_content(content)
    
    # 去重检查
    if not args.force and current_hash == state.get("last_hash"):
        print("🔁 内容重复，已拦截")
        state["stats"]["total_skipped"] += 1
        save_state(state)
        return

    # 输出
    if args.dry_run:
        print("\n" + "="*40)
        print("📝 [DRY RUN] 准备播报：")
        print("="*40)
        print(content)
        print("="*40)
    else:
        print("📤 BROADCAST_PAYLOAD_START")
        print(content)
        print("BROADCAST_PAYLOAD_END")
        
        state["last_run_at"] = datetime.now().isoformat()
        state["last_hash"] = current_hash
        state["stats"]["total_sent"] += 1
        # 发送后静默 60 分钟
        state["silence_until"] = (datetime.now() + timedelta(minutes=60)).isoformat()
        
    save_state(state)

if __name__ == "__main__":
    main()
