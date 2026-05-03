#!/usr/bin/env python3
"""
night_study/round_manager.py - 夜间自习室轮次调度器
功能：按天重置进度、轮询切换领域、写入日志。
用法:
  python3 round_manager.py next   -> 输出当前轮次要学习的领域 JSON
  python3 round_manager.py log "xxx" -> 写入一条日志
"""
import json, os, sys
from datetime import datetime

CONFIG_PATH = os.path.expanduser("~/.hermes/config/night_study_config.json")
STATE_PATH = os.path.expanduser("~/.hermes/state/night_study_state.json")
LOG_PATH = os.path.expanduser("~/.hermes/logs/night_study.log")

def load_json(path):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f: json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_domain():
    config = load_json(CONFIG_PATH)
    state = load_json(STATE_PATH)
    idx = state.get("current_idx", 0)
    domains = config.get("domains", [])
    if not domains: return {"error": "no domains configured"}

    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("date") != today:
        idx = 0
        state["date"] = today
        state["current_idx"] = 0
        # Clear daily log
        with open(LOG_PATH, "w") as f: f.write(f"# 夜间自习日志 - {today}\n")

    if idx >= len(domains):
        state["status"] = "completed_for_day"
        save_json(STATE_PATH, state)
        return {"status": "all_domains_covered"}

    domain = domains[idx]
    state["current_idx"] = idx + 1
    state["status"] = "processing"
    state["current_domain"] = domain["id"]
    save_json(STATE_PATH, state)
    return domain

def log_entry(msg):
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M')}] {msg}\n")

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "next":
        print(json.dumps(get_next_domain(), ensure_ascii=False))
    elif action == "log":
        log_entry(sys.argv[2])
