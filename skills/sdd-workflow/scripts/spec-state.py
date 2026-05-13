#!/usr/bin/env python3
"""
spec-state.py v1.0 — SDD Spec 状态机管理

9 状态 8 转换:
  (none) → create → draft
  draft → submit → review
  review → approve → approved
  review → reject → draft
  approved → architect → architect
  architect → plan → plan
  plan → implement → implement
  implement → complete → completed
  completed → archive → archived

用法:
  python3 spec-state.py create <story_id> <title>        # 创建新 Spec
  python3 spec-state.py submit <story_id>                 # 提交审阅
  python3 spec-state.py approve <story_id>                # 批准
  python3 spec-state.py reject <story_id> <reason>        # 驳回
  python3 spec-state.py architect <story_id>              # 开始架构设计
  python3 spec-state.py plan <story_id>                   # 开始实现计划
  python3 spec-state.py implement <story_id>              # 开始实现
  python3 spec-state.py complete <story_id>               # 完成
  python3 spec-state.py archive <story_id>                # 归档
  python3 spec-state.py status [story_id]                 # 查看状态
  python3 spec-state.py list                              # 列出所有 Spec
  python3 spec-state.py reset <story_id>                  # 重置为 draft
"""

import json, os, sys, glob
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.hermes/sdd_state.json")

# === 状态机定义 ===
# current_state: {action: (next_state, [valid_prev_states?])}
ALLOWED_STATES = ["draft", "review", "approved", "architect", "plan", "implement", "completed", "archived"]

TRANSITIONS = {
    # (current_state) → action → (next_state)
    None: { "create": "draft" },
    "draft": { "submit": "review" },
    "review": { "approve": "approved", "reject": "draft" },
    "approved": { "architect": "architect" },
    "architect": { "plan": "plan" },
    "plan": { "implement": "implement" },
    "implement": { "complete": "completed" },
    "completed": { "archive": "archived" },
}

# 允许从任意状态 reset 到 draft
RESET_ALLOWED = True


def load_state():
    """加载状态文件，不存在则返回空字典"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_state(state):
    """保存状态文件"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write('\n')


def get_spec(state, story_id):
    """获取指定 Spec，不存在返回 None"""
    return state.get(story_id)


def log_event(spec, action, detail):
    """记录事件日志"""
    if "logs" not in spec:
        spec["logs"] = []
    spec["logs"].append({
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "detail": detail,
    })


def cmd_create(state, story_id, title):
    if story_id in state:
        print(f"❌ Spec '{story_id}' 已存在")
        return False
    spec = {
        "story_id": story_id,
        "title": title,
        "status": "draft",
        "spec_path": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "completed_at": None,
        "reject_reason": None,
        "logs": [],
    }
    log_event(spec, "create", f"创建 Spec: {title}")
    state[story_id] = spec
    save_state(state)
    print(f"✅ Spec '{story_id}' 已创建（draft）")
    return True


def cmd_transition(state, story_id, action):
    spec = get_spec(state, story_id)
    if not spec:
        print(f"❌ Spec '{story_id}' 不存在")
        return False

    current = spec["status"]

    # 处理 reset 特殊操作
    if action == "reset" and RESET_ALLOWED:
        spec["status"] = "draft"
        spec["updated_at"] = datetime.now().isoformat()
        spec["reject_reason"] = None
        log_event(spec, "reset", "重置为 draft")
        save_state(state)
        print(f"🔄 Spec '{story_id}' 已重置为 draft")
        return True

    # 获取当前状态允许的转换
    transitions_for_state = TRANSITIONS.get(current, {})
    if not transitions_for_state:
        print(f"❌ Spec '{story_id}' 状态为 '{current}'，不允许任何操作")
        return False

    if action not in transitions_for_state:
        allowed = ", ".join(transitions_for_state.keys())
        print(f"❌ Spec '{story_id}' 状态 '{current}' 不允许操作 '{action}'")
        print(f"   允许的操作: {allowed}")
        return False

    new_status = transitions_for_state[action]
    spec["status"] = new_status
    spec["updated_at"] = datetime.now().isoformat()

    # 日志详情
    detail_map = {
        "submit": "提交审阅",
        "approve": "已批准",
        "reject": f"驳回: {sys.argv[3] if len(sys.argv) > 3 else '未说明原因'}",
        "architect": "开始架构设计",
        "plan": "开始实现计划",
        "implement": "开始技术实现",
        "complete": "开发完成",
        "archive": "归档",
    }
    detail = detail_map.get(action, action)

    if action == "complete":
        spec["completed_at"] = datetime.now().isoformat()
    if action == "reject":
        spec["reject_reason"] = sys.argv[3] if len(sys.argv) > 3 else "未说明原因"

    log_event(spec, action, detail)
    save_state(state)

    emoji_map = {
        "draft": "📄", "review": "👀", "approved": "✅",
        "architect": "🏛️", "plan": "📋", "implement": "🏗️",
        "completed": "🎉", "archived": "📦",
    }
    emoji = emoji_map.get(new_status, "➡️")
    print(f"{emoji} Spec '{story_id}': {current} → {new_status}")
    return True


def cmd_status(state, story_id=None):
    if story_id:
        spec = get_spec(state, story_id)
        if not spec:
            print(f"❌ Spec '{story_id}' 不存在")
            return
        emoji_map = {
            "draft": "📄", "review": "👀", "approved": "✅",
            "architect": "🏛️", "plan": "📋", "implement": "🏗️",
            "completed": "🎉", "archived": "📦",
        }
        emoji = emoji_map.get(spec["status"], "❓")
        print(f"\n{'='*50}")
        print(f"  {emoji} {spec['story_id']}: {spec['title']}")
        print(f"  状态: {spec['status']}")
        print(f"  创建: {spec['created_at'][:19]}")
        print(f"  更新: {spec['updated_at'][:19]}")
        if spec.get('completed_at'):
            print(f"  完成: {spec['completed_at'][:19]}")
        if spec.get('reject_reason'):
            print(f"  驳回原因: {spec['reject_reason']}")
        if spec.get('spec_path'):
            print(f"  路径: {spec['spec_path']}")
        if spec.get('logs'):
            print(f"  事件数: {len(spec['logs'])}")
        print(f"{'='*50}\n")
    else:
        # 列出所有
        cmd_list(state)


def cmd_list(state):
    if not state:
        print("📭 (无 Spec)")
        return
    print(f"\n📋 SDD Spec 列表 ({len(state)} 个):")
    print(f"{'='*60}")
    # 按状态分组
    status_order = ["draft", "review", "approved", "architect", "plan", "implement", "completed", "archived"]
    status_emoji = {
        "draft": "📄", "review": "👀", "approved": "✅",
        "architect": "🏛️", "plan": "📋", "implement": "🏗️",
        "completed": "🎉", "archived": "📦",
    }
    for status in status_order:
        items = [(sid, s) for sid, s in state.items() if s.get("status") == status]
        if items:
            print(f"\n  {status_emoji.get(status, '❓')} {status}:")
            for sid, s in sorted(items):
                print(f"    ├─ {sid}: {s.get('title', '(无标题)')}")
                if s.get('spec_path'):
                    print(f"    └─ 📍 {s['spec_path']}")
    print()


def cmd_reset(state, story_id):
    return cmd_transition(state, story_id, "reset")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]
    state = load_state()

    if action == "create":
        if len(sys.argv) < 4:
            print("用法: spec-state.py create <story_id> <title>")
            sys.exit(1)
        cmd_create(state, sys.argv[2], sys.argv[3])

    elif action == "list":
        cmd_list(state)

    elif action == "status":
        if len(sys.argv) > 2:
            cmd_status(state, sys.argv[2])
        else:
            cmd_status(state)

    elif action in ("submit", "approve", "reject", "architect", "plan",
                    "implement", "complete", "archive", "reset"):
        if len(sys.argv) < 3:
            print(f"用法: spec-state.py {action} <story_id> [reason]")
            sys.exit(1)
        cmd_transition(state, sys.argv[2], action)

    else:
        print(f"❌ 未知操作: {action}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
