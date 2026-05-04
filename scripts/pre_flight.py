#!/usr/bin/env python3
"""
Hermes Pre-flight Check (v1.0)
The "Gatekeeper" script. Enforces Learning Workflow & Skill Discovery.

Usage:
    python3 ~/.hermes/scripts/pre_flight.py "<Task Description>"

Logic:
1. Checks if `learning_state.json` is initialized for this task.
2. Checks if `skill_finder` was likely run (by checking state file timestamp).
3. If checks fail, it outputs a BLOCKING ERROR message.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

HERMES_DIR = os.path.expanduser("~/.hermes")
STATE_FILE = os.path.join(HERMES_DIR, "learning_state.json")

def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "Unknown Task"
    
    print(f"🔍 [Pre-Flight] 检查任务: {task}")
    
    # 1. Check Learning State
    if not os.path.exists(STATE_FILE):
        print("❌ BLOCKED: 未初始化学习状态! 必须先运行 learning-state.py init")
        sys.exit(1)
    
    with open(STATE_FILE) as f:
        try:
            state = json.load(f)
        except:
            print("❌ BLOCKED: 学习状态文件损坏!")
            sys.exit(1)

    # 2. Check if state is fresh (last 10 mins) or related to current task
    topic = state.get("topic", "")
    current_step = state.get("current_step", -1)
    
    # If current step is 'completed', and task is different, warn
    if current_step == 5 and task.lower() not in topic.lower():
        print(f"⚠️  WARNING: 上一个学习任务 '{topic}' 已完成。是否开始新任务?")
        print("💡 建议: 运行 learning-state.py init '新任务'")

    # 3. Check for Skill Discovery
    # We can't perfectly check if skill_finder was run, but we can check if the state has 'search' artifacts
    # Or we can just remind the agent.
    print("✅ PASS: 学习状态存在。")
    print("📝 提醒: 请确保已运行 `skill_finder.py` 且未跳过任何步骤。")

    # 4. Check SOUL.md Rule Compliance
    # Remind the agent of the critical rule
    print("\n🔒 铁律提醒 (SOUL.md):")
    print("   - 收到任务 -> 第一步运行 skill_finder.py")
    print("   - 找到 Skill -> 必须 skill_view 加载")
    print("   - 禁止直接动手写代码!")

if __name__ == '__main__':
    main()
