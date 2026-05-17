#!/usr/bin/env python3
"""
skill-state-manager.py v1.0 — Skill 生命周期状态管理器

统一管理 skill 的生命周期状态转换。

用法:
  python3 skill-state-manager.py list                        # 列出所有状态
  python3 skill-state-manager.py status <skill>              # 查看单个
  python3 skill-state-manager.py set <skill> <状态> [--reason "..."]  # 设置状态
  python3 skill-state-manager.py deprecate <skill> [--reason "..."]   # 快捷废弃
  python3 skill-state-manager.py archive <skill>             # 快捷归档
  python3 skill-state-manager.py revive <skill>              # 恢复
  python3 skill-state-manager.py batch <条件> <状态> [--dry-run]     # 批量操作
  python3 skill-state-manager.py --help                      # 帮助
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"
LIFECYCLE_FILE = Path.home() / ".hermes" / "skill_lifecycle_state.json"
SQS_SCRIPT = SKILLS_DIR / "skill-creator" / "scripts" / "skill-quality-score.py"
NOW = datetime.now(timezone.utc)

VALID_STATUSES = {"active", "under_review", "frozen", "deprecated", "archived"}
STATUS_EMOJI = {
    "active": "🟢", "under_review": "🟠", "frozen": "🟡",
    "deprecated": "🔴", "archived": "⚫",
}
STATUS_TRANSITIONS = {
    "active": ["under_review", "frozen", "deprecated"],
    "under_review": ["active", "frozen", "deprecated"],
    "frozen": ["active", "deprecated"],
    "deprecated": ["archived"],
    "archived": ["deprecated"],
}
TRANSITION_HELP = {
    ("active", "under_review"): "标记为审核中",
    ("under_review", "active"): "审核通过，恢复正常",
    ("active", "frozen"): "暂时冻结",
    ("frozen", "active"): "恢复活跃",
    ("active", "deprecated"): "标记废弃",
    ("under_review", "deprecated"): "审核不通过，废弃",
    ("frozen", "deprecated"): "不再维护，废弃",
    ("deprecated", "archived"): "归档（废弃 ≥ 30 天）",
    ("archived", "deprecated"): "恢复为废弃状态",
}


# ── 状态持久化 ──────────────────────────────────────────────────

def load_state():
    if LIFECYCLE_FILE.exists():
        try:
            return json.loads(LIFECYCLE_FILE.read_text())
        except Exception:
            return {}
    return {"skills": {}}


def save_state(state):
    LIFECYCLE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LIFECYCLE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n"
    )


def get_skill_status(state, skill_name):
    return state.get("skills", {}).get(skill_name, {"status": "active"})


# ── 状态转换 ──────────────────────────────────────────────────

def transition(skill_name, new_status, state, reason=""):
    if new_status not in VALID_STATUSES:
        print(f"❌ 无效状态: {new_status}")
        print(f"   有效: {', '.join(VALID_STATUSES)}")
        return False

    if "skills" not in state:
        state["skills"] = {}
    if skill_name not in state["skills"]:
        state["skills"][skill_name] = {}

    old_status = state["skills"][skill_name].get("status", "active")

    if old_status == new_status:
        print(f"ℹ️  已在 '{new_status}' 状态")
        return True

    # 检查转换有效性
    if old_status in STATUS_TRANSITIONS:
        if new_status not in STATUS_TRANSITIONS[old_status]:
            print(f"❌ 非法转换: {old_status} → {new_status}")
            allowed = STATUS_TRANSITIONS[old_status]
            print(f"   允许: {', '.join(allowed)}")
            return False

    # 执行转换
    update = {
        "status": new_status,
        f"{new_status}_at": NOW.isoformat(),
    }
    if reason:
        update["status_reason"] = reason
    if new_status == "deprecated" and old_status in ("active", "under_review", "frozen"):
        update["deprecated_at"] = NOW.isoformat()

    state["skills"][skill_name].update(update)
    save_state(state)

    emoji = STATUS_EMOJI.get(new_status, "❓")
    from_emoji = STATUS_EMOJI.get(old_status, "❓")
    help_text = TRANSITION_HELP.get((old_status, new_status), "")
    print(f"  {from_emoji} {old_status} → {emoji} {new_status}  {help_text}")
    if reason:
        print(f"     原因: {reason}")
    return True


# ── 条件批量操作 ──────────────────────────────────────────────

def execute_batch(condition, target_status, dry_run=True):
    state = load_state()
    matched = []

    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            name = os.path.basename(root)
            include = False

            if condition.startswith("sqs<"):
                try:
                    threshold = float(condition[4:])
                    sqs_result = subprocess.run(
                        [sys.executable, str(SQS_SCRIPT), name, "--json"],
                        capture_output=True, text=True, timeout=15
                    )
                    if sqs_result.returncode == 0:
                        sqs_data = json.loads(sqs_result.stdout)
                        total = sqs_data.get("sqs_total", 100)
                        if total < threshold:
                            include = True
                except Exception:
                    pass
            elif condition == "all":
                include = True
            elif condition == "deprecated":
                status = get_skill_status(state, name)
                if status.get("status") == "deprecated":
                    include = True

            if include:
                matched.append(name)

    print(f"\n📋 条件 '{condition}' 匹配 {len(matched)} 个 skill:")
    for m in matched[:20]:
        current = get_skill_status(state, m).get("status", "?")
        print(f"  {current} → {target_status}: {m}")
    if len(matched) > 20:
        print(f"  ...及另外 {len(matched)-20} 个")

    if dry_run:
        print(f"\n🟡 DRY RUN — 未实际执行。去除 --dry-run 以应用。")
        return

    count = 0
    for name in matched:
        if transition(name, target_status, state, f"批量操作: {condition} → {target_status}"):
            count += 1
    print(f"\n✅ 已转换 {count} 个 skill")


# ── 输出 ──────────────────────────────────────────────────────

def cmd_list():
    state = load_state()
    skills = state.get("skills", {})
    if not skills:
        print("📭 无显式状态记录（所有 skill 默认为 active）")
        return

    # 按状态分组
    grouped = {}
    for name, info in skills.items():
        s = info.get("status", "active")
        grouped.setdefault(s, []).append(name)

    print(f"\n📋 生命周期状态 ({len(skills)} 个):")
    for status in ["active", "under_review", "frozen", "deprecated", "archived"]:
        if status in grouped:
            emoji = STATUS_EMOJI.get(status, "❓")
            items = grouped[status]
            print(f"\n  {emoji} {status} ({len(items)}):")
            for name in sorted(items)[:10]:
                extra = ""
                at_key = f"{status}_at"
                if at_key in skills[name]:
                    extra = f" ({skills[name][at_key][:10]})"
                print(f"    {name}{extra}")
            if len(items) > 10:
                print(f"    ...及另外 {len(items)-10} 个")


def cmd_status(skill_name):
    state = load_state()
    info = get_skill_status(state, skill_name)
    status = info.get("status", "active")
    emoji = STATUS_EMOJI.get(status, "❓")

    print(f"\n{emoji} {skill_name}: {status}")
    for key in ["deprecated_at", "archived_at", "status_reason", "replaced_by"]:
        if info.get(key):
            print(f"  {key}: {info[key]}")

    allowed = STATUS_TRANSITIONS.get(status, [])
    if allowed:
        print(f"  可转换至: {'/'.join(allowed)}")


# ── 入口 ──────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    action = sys.argv[1]
    state = load_state()

    if action == "list":
        cmd_list()
    elif action == "status":
        if len(sys.argv) < 3:
            print("用法: skill-state-manager.py status <skill>")
            sys.exit(1)
        cmd_status(sys.argv[2])
    elif action == "set":
        if len(sys.argv) < 4:
            print("用法: skill-state-manager.py set <skill> <状态> [--reason ...]")
            sys.exit(1)
        skill = sys.argv[2]
        new_status = sys.argv[3]
        reason = ""
        if "--reason" in sys.argv:
            ri = sys.argv.index("--reason")
            if ri + 1 < len(sys.argv):
                reason = sys.argv[ri + 1]
        transition(skill, new_status, state, reason)
    elif action in ("deprecate", "archive", "revive"):
        if len(sys.argv) < 3:
            print(f"用法: skill-state-manager.py {action} <skill> [--reason ...]")
            sys.exit(1)
        skill = sys.argv[2]
        target = {"deprecate": "deprecated", "archive": "archived", "revive": "active"}[action]
        reason = ""
        if "--reason" in sys.argv:
            ri = sys.argv.index("--reason")
            if ri + 1 < len(sys.argv):
                reason = sys.argv[ri + 1]
        transition(skill, target, state, reason)
    elif action == "batch":
        if len(sys.argv) < 4:
            print("用法: skill-state-manager.py batch <条件> <状态> [--dry-run]")
            sys.exit(1)
        condition = sys.argv[2]
        target = sys.argv[3]
        dry_run = "--dry-run" in sys.argv
        execute_batch(condition, target, dry_run=dry_run)
    else:
        print(f"❌ 未知操作: {action}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
