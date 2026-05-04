#!/usr/bin/env python3
"""
learning_state.py - 学习状态持久化管理器

功能:
  1. 持久化记录工作流遵从状态
  2. 记录已加载的 skills 和学习进度
  3. 为 pre_flight.py 提供状态查询接口
  4. 跨会话保持关键规则，防止 context compaction 后丢失

用法:
  python3 learning_state.py mark_step_complete "STEP_1" "skill_finder"
  python3 learning_state.py mark_step_complete "STEP_2" "web-access"
  python3 learning_state.py get_state
  python3 learning_state.py reset
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.hermes/learning_state.json")

DEFAULT_STATE = {
    "version": 1,
    "last_updated": None,
    "session_id": None,
    "current_task": None,
    "workflow_steps": {
        "STEP_0_pre_flight": {"completed": False, "timestamp": None, "result": None},
        "STEP_1_skill_scan": {"completed": False, "timestamp": None, "skills_found": []},
        "STEP_2_learning": {"completed": False, "timestamp": None, "skills_loaded": []},
        "STEP_3_execution": {"completed": False, "timestamp": None, "actions_taken": []},
    },
    "loaded_skills": [],
    "learning_history": [],
    "rule_violations": [],
    "compression_checkpoints": [],
}


def load_state():
    """加载状态文件"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                # 合并默认值（防止新版本字段缺失）
                for key, value in DEFAULT_STATE.items():
                    if key not in state:
                        state[key] = value
                return state
        except Exception as e:
            print(f"⚠️ 状态文件损坏，使用默认状态: {e}")
            return DEFAULT_STATE.copy()
    return DEFAULT_STATE.copy()


def save_state(state):
    """保存状态文件"""
    state["last_updated"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def mark_step_complete(step_name, details=None):
    """标记步骤完成"""
    state = load_state()
    
    if step_name in state["workflow_steps"]:
        state["workflow_steps"][step_name]["completed"] = True
        state["workflow_steps"][step_name]["timestamp"] = datetime.now().isoformat()
        if details:
            state["workflow_steps"][step_name].update(details)
    
    save_state(state)
    print(f"✅ {step_name} 已标记为完成")


def mark_step_incomplete(step_name, reason=None):
    """标记步骤未完成（违规）"""
    state = load_state()
    
    if step_name in state["workflow_steps"]:
        state["workflow_steps"][step_name]["completed"] = False
        state["workflow_steps"][step_name]["timestamp"] = datetime.now().isoformat()
        state["workflow_steps"][step_name]["result"] = f"INCOMPLETE: {reason or 'Unknown'}"
    
    # 记录违规
    state["rule_violations"].append({
        "step": step_name,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    })
    
    save_state(state)
    print(f"⚠️ {step_name} 标记为未完成: {reason}")


def record_skill_loaded(skill_name, category=None):
    """记录加载的 skill"""
    state = load_state()
    
    skill_record = {
        "name": skill_name,
        "category": category,
        "loaded_at": datetime.now().isoformat(),
    }
    
    state["loaded_skills"].append(skill_record)
    
    # 更新 STEP_2
    if "STEP_2_learning" in state["workflow_steps"]:
        state["workflow_steps"]["STEP_2_learning"]["skills_loaded"].append(skill_name)
    
    save_state(state)


def record_compression_checkpoint(summary_length=None, savings_pct=None):
    """记录压缩检查点"""
    state = load_state()
    
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "summary_length": summary_length,
        "savings_pct": savings_pct,
        "workflow_status_at_compression": {
            step: data["completed"] 
            for step, data in state["workflow_steps"].items()
        },
    }
    
    state["compression_checkpoints"].append(checkpoint)
    
    # 只保留最近 10 个检查点
    state["compression_checkpoints"] = state["compression_checkpoints"][-10:]
    
    save_state(state)


def get_state_summary():
    """获取状态摘要"""
    state = load_state()
    
    print("=" * 60)
    print("📊 学习状态摘要")
    print("=" * 60)
    print(f"最后更新: {state.get('last_updated', 'Never')}")
    print(f"当前任务: {state.get('current_task', 'None')}")
    print()
    
    print("🔄 工作流步骤状态:")
    for step, data in state["workflow_steps"].items():
        status = "✅" if data.get("completed") else "❌"
        timestamp = data.get("timestamp", "Never")
        print(f"  {status} {step} (最后检查: {timestamp})")
    
    print()
    print(f"📚 已加载 Skills: {len(state['loaded_skills'])}")
    for skill in state["loaded_skills"][-5:]:  # 最近 5 个
        print(f"  - {skill['name']} ({skill.get('category', 'N/A')})")
    
    print()
    print(f"⚠️ 规则违规次数: {len(state['rule_violations'])}")
    for violation in state["rule_violations"][-3:]:  # 最近 3 次
        print(f"  - {violation['step']}: {violation.get('reason', 'Unknown')}")
    
    print()
    print(f"🗜️ 压缩检查点: {len(state['compression_checkpoints'])}")
    
    print("=" * 60)


def reset_state():
    """重置状态"""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print("🔄 状态已重置")
    else:
        print("ℹ️ 状态文件不存在，无需重置")


def check_workflow_compliance():
    """检查工作流遵从性"""
    state = load_state()
    
    steps = state["workflow_steps"]
    
    # 检查是否按顺序完成
    step_order = ["STEP_0_pre_flight", "STEP_1_skill_scan", "STEP_2_learning", "STEP_3_execution"]
    
    compliance = {
        "compliant": True,
        "issues": [],
        "last_completed_step": None,
    }
    
    prev_completed = True
    for step in step_order:
        if step in steps:
            if steps[step]["completed"]:
                if not prev_completed:
                    compliance["compliant"] = False
                    compliance["issues"].append(f"{step} 完成但前序步骤未完成")
                compliance["last_completed_step"] = step
            else:
                prev_completed = False
    
    return compliance


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  learning_state.py mark_step_complete <step_name> [details_json]")
        print("  learning_state.py mark_step_incomplete <step_name> [reason]")
        print("  learning_state.py record_skill <skill_name> [category]")
        print("  learning_state.py get_state")
        print("  learning_state.py check_compliance")
        print("  learning_state.py reset")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "mark_step_complete":
        if len(sys.argv) < 3:
            print("错误: 需要提供 step_name")
            sys.exit(1)
        step_name = sys.argv[2]
        details = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
        mark_step_complete(step_name, details)
    
    elif action == "mark_step_incomplete":
        if len(sys.argv) < 3:
            print("错误: 需要提供 step_name")
            sys.exit(1)
        step_name = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else None
        mark_step_incomplete(step_name, reason)
    
    elif action == "record_skill":
        if len(sys.argv) < 3:
            print("错误: 需要提供 skill_name")
            sys.exit(1)
        skill_name = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else None
        record_skill_loaded(skill_name, category)
    
    elif action == "record_compression":
        summary_length = int(sys.argv[2]) if len(sys.argv) > 2 else None
        savings_pct = float(sys.argv[3]) if len(sys.argv) > 3 else None
        record_compression_checkpoint(summary_length, savings_pct)
    
    elif action == "get_state":
        get_state_summary()
    
    elif action == "check_compliance":
        compliance = check_workflow_compliance()
        if compliance["compliant"]:
            print("✅ 工作流遵从性检查通过")
        else:
            print("❌ 工作流遵从性问题:")
            for issue in compliance["issues"]:
                print(f"  - {issue}")
        print(f"最后完成步骤: {compliance['last_completed_step']}")
    
    elif action == "reset":
        reset_state()
    
    else:
        print(f"未知操作: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
