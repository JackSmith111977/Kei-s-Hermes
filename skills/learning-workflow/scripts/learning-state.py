#!/usr/bin/env python3
"""
learning-state.py - 学习流程状态机管理
用法:
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py init "主题"
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py check <step>
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py complete <step>
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py status
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py reset
"""

import json
import os
import sys
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.hermes/learning_state.json")
ARTIFACT_DIR = os.path.expanduser("~/.hermes/learning")

STEPS = {
    "step0_map": {"artifact": os.path.join(ARTIFACT_DIR, "knowledge_map.md")},
    "step1_search": {"artifact": os.path.join(ARTIFACT_DIR, "raw_search_results.md")},
    "step2_read": {"artifact": os.path.join(ARTIFACT_DIR, "reading_notes.md")},
    "step3_extract": {"artifact": os.path.join(ARTIFACT_DIR, "extracted_knowledge.md")},
    "step4_scaffold": {"artifact": None},  # 由 skill-creator 处理
    "step5_validate": {"artifact": None}   # 由 skill-creator 处理
}

def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def init_state(topic):
    state = {
        "topic": topic,
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "steps": {k: {"status": "pending", "artifact": v["artifact"]} for k, v in STEPS.items()}
    }
    save_state(state)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    print(f"✅ 学习流程已初始化：{topic}")
    print(f"📊 状态文件：{STATE_FILE}")
    return state

def check_step(step_name):
    state = load_state()
    if not state:
        print(f"🚨 学习流程未初始化！请先运行 init")
        return False
    step = state["steps"].get(step_name)
    if not step:
        print(f"🚨 未知步骤：{step_name}")
        return False
    
    # 检查状态
    if step["status"] != "completed":
        print(f"🚨 {step_name} 未完成（状态：{step['status']}）")
        return False
    
    # 检查产出物
    if step.get("artifact") and not os.path.exists(step["artifact"]):
        print(f"🚨 {step_name} 的产出物不存在：{step['artifact']}")
        return False
    
    print(f"✅ {step_name} 检查通过")
    return True

def complete_step(step_name):
    state = load_state()
    if not state:
        print(f"🚨 学习流程未初始化！")
        sys.exit(1)
    
    step = state["steps"].get(step_name)
    if not step:
        print(f"🚨 未知步骤：{step_name}")
        sys.exit(1)
    
    step["status"] = "completed"
    step["completed_at"] = datetime.now().isoformat()
    
    # 推进 current_step
    step_keys = list(STEPS.keys())
    current_idx = step_keys.index(step_name)
    if current_idx + 1 < len(step_keys):
        state["current_step"] = current_idx + 2
    
    save_state(state)
    print(f"✅ {step_name} 标记为完成")

def show_status():
    state = load_state()
    if not state:
        print("📭 无活跃学习流程")
        return
    
    print(f"📚 学习主题：{state['topic']}")
    print(f"📊 当前步骤：{state['current_step']}/5")
    print()
    for name, info in state["steps"].items():
        status = info["status"]
        artifact = info.get("artifact", "N/A")
        artifact_exists = os.path.exists(artifact) if artifact else "N/A"
        print(f"  {name}: {status} | 产出物：{artifact_exists}")

def reset_state():
    if os.path.exists(STATE_FILE):
        archive_dir = os.path.expanduser("~/.hermes/learning/archive")
        os.makedirs(archive_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(archive_dir, f"{timestamp}.json")
        os.rename(STATE_FILE, archive_path)
        print(f"✅ 状态已归档到：{archive_path}")
    else:
        print("📭 无活跃状态需要重置")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 learning-state.py {init|check|complete|status|reset} [args]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "init":
        if len(sys.argv) < 3:
            print("🚨 请提供学习主题：learning-state.py init '主题'")
            sys.exit(1)
        init_state(sys.argv[2])
    elif action == "check":
        if len(sys.argv) < 3:
            print("🚨 请提供步骤名：learning-state.py check step1_search")
            sys.exit(1)
        if not check_step(sys.argv[2]):
            sys.exit(1)
    elif action == "complete":
        if len(sys.argv) < 3:
            print("🚨 请提供步骤名：learning-state.py complete step1_search")
            sys.exit(1)
        complete_step(sys.argv[2])
    elif action == "status":
        show_status()
    elif action == "reset":
        reset_state()
    else:
        print(f"🚨 未知操作：{action}")
        sys.exit(1)
