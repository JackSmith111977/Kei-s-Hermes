#!/usr/bin/env python3
"""
spec-state.py v1.0 — SDD Spec 生命周期状态机

管理 Spec 从 create → submit → approve → start → complete → archive 的完整生命周期。

用法:
  python3 spec-state.py create <story_id> <title> [spec_path]
  python3 spec-state.py submit <story_id>
  python3 spec-state.py approve <story_id>
  python3 spec-state.py reject <story_id> [reason]
  python3 spec-state.py start <story_id>
  python3 spec-state.py complete <story_id>
  python3 spec-state.py archive <story_id>
  python3 spec-state.py status <story_id>
  python3 spec-state.py list
  python3 spec-state.py check-stale [max_days]

状态机:
  (none) → draft → review → approved → in_progress → completed → archived
                     ↓                     ↑
                   draft ← rejected     start
"""
import json
import os
import sys
import glob
from datetime import datetime, timedelta

STATE_FILE = os.path.expanduser("~/.hermes/sdd_state.json")
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPTS_DIR)
PROJECTS = {
    "sra": os.path.expanduser("~/projects/sra"),
}

# ── 状态转换表 ──
# (当前状态, 操作) → 下一状态
TRANSITIONS = {
    (None, "create"): "draft",
    ("draft", "submit"): "review",
    ("review", "approve"): "approved",
    ("review", "reject"): "draft",
    ("approved", "start"): "in_progress",
    ("in_progress", "complete"): "completed",
    ("completed", "archive"): "archived",
}

# 每个状态允许的操作
ALLOWED_OPS = {
    None: ["create"],
    "draft": ["submit", "delete"],
    "review": ["approve", "reject"],
    "approved": ["start"],
    "in_progress": ["complete"],
    "completed": ["archive"],
    "archived": [],  # 终态
}


def load_state():
    """加载所有 Spec 的状态"""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_state(state):
    """保存所有 Spec 的状态"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def find_spec_file(story_id):
    """在已知项目中查找 Spec 文件"""
    # 尝试 docs/stories/STORY-{id}.md
    for project_name, project_root in PROJECTS.items():
        candidates = [
            os.path.join(project_root, "docs", "stories", f"STORY-{story_id}.md"),
            os.path.join(project_root, "docs", "stories", f"{story_id}.md"),
        ]
        # 也搜索 docs/stories/ 下包含 story_id 的文件
        stories_dir = os.path.join(project_root, "docs", "stories")
        if os.path.isdir(stories_dir):
            for f in os.listdir(stories_dir):
                if story_id in f and f.endswith(".md"):
                    candidates.append(os.path.join(stories_dir, f))

        for c in candidates:
            if os.path.isfile(c):
                return c
    return None


def get_spec_status_from_file(spec_path):
    """从 Spec 文件的 frontmatter 中读取 status"""
    if not spec_path or not os.path.isfile(spec_path):
        return None
    try:
        with open(spec_path) as f:
            content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                import yaml
                meta = yaml.safe_load(parts[1])
                return meta.get("status") if meta else None
    except Exception:
        pass
    return None


def validate_transition(current_status, operation):
    """验证操作在当前状态下是否允许"""
    key = (current_status, operation)
    if key in TRANSITIONS:
        return True, TRANSITIONS[key]
    
    allowed = ALLOWED_OPS.get(current_status, [])
    if operation not in allowed:
        return False, f"操作 '{operation}' 在状态 '{current_status}' 下不允许"
    
    # 如果 operation 在 allowed 中但不在 TRANSITIONS 中（如 delete）
    return True, None


def action_create(story_id, title, spec_path=None):
    """创建新 Spec"""
    state = load_state()
    if story_id in state:
        # 已存在，检查状态
        existing = state[story_id]
        if existing["status"] != "archived":
            print(f"⚠️  Spec '{story_id}' 已存在（状态: {existing['status']}）")
            print(f"   标题: {existing['title']}")
            print(f"   创建时间: {existing.get('created_at', '未知')}")
            sys.exit(1)
        # archived 的可以重新激活
        print(f"🔄 重新激活已归档的 Spec '{story_id}'")
    
    state[story_id] = {
        "story_id": story_id,
        "title": title,
        "status": "draft",
        "spec_path": spec_path or "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "completed_at": None,
        "reject_reason": None,
        "logs": [
            {"action": "create", "timestamp": datetime.now().isoformat(), "detail": f"创建 Spec: {title}"}
        ]
    }
    save_state(state)
    print(f"✅ 已创建 Spec '{story_id}': {title}")
    print(f"📊 状态: draft")
    print(f"📝 路径: {spec_path or '未设置'}")
    print(f"⏭️  下一步: 填充 Spec 内容 → spec-state.py submit {story_id}")
    return state[story_id]


def action_submit(story_id):
    """提交审阅: draft → review"""
    state = load_state()
    spec = state.get(story_id)
    if not spec:
        print(f"❌ Spec '{story_id}' 不存在")
        sys.exit(1)
    
    ok, next_state = validate_transition(spec["status"], "submit")
    if not ok:
        print(f"❌ {next_state}")
        sys.exit(1)
    
    # 检查 Spec 文件是否存在
    spec_path = spec.get("spec_path") or find_spec_file(story_id)
    if not spec_path or not os.path.isfile(spec_path):
        print(f"⚠️  Spec 文件未找到: {spec_path or '未设置'}")
        print(f"   请先创建 Spec 文件，然后重试")
        print(f"   模板: {os.path.join(SKILL_DIR, 'templates', 'story-template.md')}")
        sys.exit(1)
    
    spec["status"] = next_state
    spec["updated_at"] = datetime.now().isoformat()
    spec["spec_path"] = spec_path
    spec["logs"].append({"action": "submit", "timestamp": datetime.now().isoformat(), "detail": "提交审阅"})
    save_state(state)
    print(f"✅ Spec '{story_id}' 已提交审阅")
    print(f"📊 状态: review → 等待主人审批")
    print(f"📝 文件: {spec_path}")
    return spec


def action_approve(story_id):
    """批准: review → approved"""
    state = load_state()
    spec = state.get(story_id)
    if not spec:
        print(f"❌ Spec '{story_id}' 不存在")
        sys.exit(1)
    
    ok, next_state = validate_transition(spec["status"], "approve")
    if not ok:
        print(f"❌ {next_state}")
        sys.exit(1)
    
    spec["status"] = next_state
    spec["updated_at"] = datetime.now().isoformat()
    spec["logs"].append({"action": "approve", "timestamp": datetime.now().isoformat(), "detail": "主人已批准"})
    save_state(state)
    
    # 同时更新 Spec 文件中的 status frontmatter
    spec_path = spec.get("spec_path") or find_spec_file(story_id)
    if spec_path:
        _update_file_status(spec_path, "approved")
    
    print(f"✅ Spec '{story_id}' 已批准！可以开始开发了")
    print(f"📊 状态: approved")
    print(f"⏭️  下一步: 开发实现 → spec-state.py start {story_id}")
    return spec


def action_reject(story_id, reason="未提供原因"):
    """拒绝: review → draft"""
    state = load_state()
    spec = state.get(story_id)
    if not spec:
        print(f"❌ Spec '{story_id}' 不存在")
        sys.exit(1)
    
    ok, next_state = validate_transition(spec["status"], "reject")
    if not ok:
        print(f"❌ {next_state}")
        sys.exit(1)
    
    spec["status"] = next_state
    spec["updated_at"] = datetime.now().isoformat()
    spec["reject_reason"] = reason
    spec["logs"].append({"action": "reject", "timestamp": datetime.now().isoformat(), "detail": f"驳回: {reason}"})
    save_state(state)
    print(f"🔄 Spec '{story_id}' 已驳回")
    print(f"📊 状态: draft（需修改后重新提交）")
    print(f"📝 原因: {reason}")
    return spec


def action_start(story_id):
    """开始实现: approved → in_progress"""
    state = load_state()
    spec = state.get(story_id)
    if not spec:
        print(f"❌ Spec '{story_id}' 不存在")
        sys.exit(1)
    
    ok, next_state = validate_transition(spec["status"], "start")
    if not ok:
        print(f"❌ {next_state}")
        sys.exit(1)
    
    spec["status"] = next_state
    spec["updated_at"] = datetime.now().isoformat()
    spec["logs"].append({"action": "start", "timestamp": datetime.now().isoformat(), "detail": "开始开发"})
    save_state(state)
    
    # 更新 Spec 文件
    spec_path = spec.get("spec_path") or find_spec_file(story_id)
    if spec_path:
        _update_file_status(spec_path, "in_progress")
    
    print(f"✅ Spec '{story_id}' 开始开发")
    print(f"📊 状态: in_progress")
    print(f"⏭️  记得: 实现完成后 → spec-state.py complete {story_id}")
    return spec


def action_complete(story_id):
    """完成: in_progress → completed"""
    state = load_state()
    spec = state.get(story_id)
    if not spec:
        print(f"❌ Spec '{story_id}' 不存在")
        sys.exit(1)
    
    ok, next_state = validate_transition(spec["status"], "complete")
    if not ok:
        print(f"❌ {next_state}")
        sys.exit(1)
    
    spec["status"] = next_state
    spec["updated_at"] = datetime.now().isoformat()
    spec["completed_at"] = datetime.now().isoformat()
    spec["logs"].append({"action": "complete", "timestamp": datetime.now().isoformat(), "detail": "开发完成"})
    save_state(state)
    
    # 更新 Spec 文件
    spec_path = spec.get("spec_path") or find_spec_file(story_id)
    if spec_path:
        _update_file_status(spec_path, "completed")
    
    print(f"✅ Spec '{story_id}' 开发完成！")
    print(f"📊 状态: completed")
    print(f"⏭️  下一步: 文档对齐 → spec-state.py archive {story_id}")
    return spec


def action_archive(story_id):
    """归档: completed → archived"""
    state = load_state()
    spec = state.get(story_id)
    if not spec:
        print(f"❌ Spec '{story_id}' 不存在")
        sys.exit(1)
    
    ok, next_state = validate_transition(spec["status"], "archive")
    if not ok:
        print(f"❌ {next_state}")
        sys.exit(1)
    
    spec["status"] = next_state
    spec["updated_at"] = datetime.now().isoformat()
    spec["logs"].append({"action": "archive", "timestamp": datetime.now().isoformat(), "detail": "归档"})
    save_state(state)
    print(f"✅ Spec '{story_id}' 已归档")
    print(f"📊 状态: archived")
    return spec


def action_status(story_id):
    """查看 Spec 状态"""
    state = load_state()
    spec = state.get(story_id)
    if not spec:
        print(f"❌ Spec '{story_id}' 不存在")
        print(f"💡 使用 'list' 查看所有 Spec")
        sys.exit(1)
    
    _print_spec(spec)


def action_list():
    """列出所有 Spec"""
    state = load_state()
    if not state:
        print("📭 无 Spec 记录")
        return
    
    # 按状态分组
    by_status = {}
    for sid, spec in state.items():
        s = spec.get("status", "unknown")
        by_status.setdefault(s, []).append(spec)
    
    # 自定义排序
    status_order = ["draft", "review", "approved", "in_progress", "completed", "archived"]
    
    print(f"📋 SDD Spec 总览 ({len(state)} 个)")
    print("=" * 60)
    
    for s in status_order:
        specs = by_status.pop(s, [])
        if not specs:
            continue
        
        status_icon = {
            "draft": "📝", "review": "🔍", "approved": "✅",
            "in_progress": "🔄", "completed": "🎉", "archived": "📦"
        }.get(s, "❓")
        
        print(f"\n  {status_icon} {s.upper()} ({len(specs)}):")
        for sp in specs:
            updated = sp.get("updated_at", "")[:16]
            print(f"    └─ {sp['story_id']}: {sp['title']} [{updated}]")
    
    # 剩余未知状态的
    for s, specs in by_status.items():
        print(f"\n  ❓ {s} ({len(specs)}):")
        for sp in specs:
            print(f"    └─ {sp['story_id']}: {sp['title']}")


def action_check_stale(max_days=7):
    """检查过期的 Spec（超过 max_days 未更新且未完成）"""
    state = load_state()
    if not state:
        print("📭 无 Spec 记录")
        return
    
    now = datetime.now()
    stale_found = False
    
    for sid, spec in state.items():
        status = spec.get("status", "")
        if status in ("completed", "archived"):
            continue
        
        updated_str = spec.get("updated_at", spec.get("created_at", ""))
        try:
            updated = datetime.fromisoformat(updated_str)
            days_old = (now - updated).days
        except (ValueError, TypeError):
            continue
        
        if days_old >= max_days:
            stale_found = True
            icon = "🟡" if days_old < 14 else "🔴"
            print(f"  {icon} [{spec['status']}] {sid}: {spec['title']} — {days_old} 天未更新")
    
    if not stale_found:
        print(f"✅ 所有活跃 Spec 都在 {max_days} 天内更新过")


def _print_spec(spec):
    """打印单个 Spec 详情"""
    status_icon = {
        "draft": "📝", "review": "🔍", "approved": "✅",
        "in_progress": "🔄", "completed": "🎉", "archived": "📦"
    }.get(spec.get("status", ""), "❓")
    
    print(f"{status_icon} Spec: {spec['story_id']}")
    print(f"  └─ 标题: {spec.get('title', '无标题')}")
    print(f"  └─ 状态: {spec.get('status', '未知')}")
    print(f"  └─ 创建: {spec.get('created_at', '未知')[:16]}")
    print(f"  └─ 更新: {spec.get('updated_at', '未知')[:16]}")
    
    if spec.get("completed_at"):
        print(f"  └─ 完成: {spec['completed_at'][:16]}")
    
    if spec.get("reject_reason"):
        print(f"  └─ 驳回原因: {spec['reject_reason']}")
    
    spec_path = spec.get("spec_path", "")
    if spec_path and os.path.isfile(spec_path):
        print(f"  └─ 文件: {spec_path}")
    
    logs = spec.get("logs", [])
    if logs:
        print(f"  └─ 最近操作 ({len(logs)} 条):")
        for log in logs[-3:]:
            print(f"       [{log.get('timestamp', '')[:16]}] {log.get('action', '?')}: {log.get('detail', '')}")


def _update_file_status(spec_path, new_status):
    """更新 Spec 文件 frontmatter 中的 status 字段"""
    if not spec_path or not os.path.isfile(spec_path):
        return
    
    try:
        with open(spec_path) as f:
            content = f.read()
        
        if not content.startswith("---"):
            return
        
        parts = content.split("---", 2)
        if len(parts) < 2:
            return
        
        import re
        frontmatter = parts[1]
        new_fm = re.sub(
            r'^status:\s*.*$',
            f'status: {new_status}',
            frontmatter,
            count=1,
            flags=re.MULTILINE
        )
        
        if new_fm != frontmatter:
            new_content = "---" + new_fm + "---" + parts[2]
            with open(spec_path, "w") as f:
                f.write(new_content)
    except Exception as e:
        print(f"  ⚠️  无法更新 Spec 文件状态: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 spec-state.py {create|submit|approve|reject|start|complete|archive|status|list|check-stale} [args]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "create":
        if len(sys.argv) < 4:
            print("用法: spec-state.py create <story_id> <title> [spec_path]")
            sys.exit(1)
        story_id = sys.argv[2]
        title = sys.argv[3]
        spec_path = sys.argv[4] if len(sys.argv) > 4 else None
        action_create(story_id, title, spec_path)
    
    elif action in ("submit", "approve", "start", "complete", "archive", "status"):
        if len(sys.argv) < 3:
            print(f"用法: spec-state.py {action} <story_id>")
            sys.exit(1)
        story_id = sys.argv[2]
        
        if action == "submit":
            action_submit(story_id)
        elif action == "approve":
            action_approve(story_id)
        elif action == "start":
            action_start(story_id)
        elif action == "complete":
            action_complete(story_id)
        elif action == "archive":
            action_archive(story_id)
        elif action == "status":
            action_status(story_id)
    
    elif action == "reject":
        if len(sys.argv) < 3:
            print("用法: spec-state.py reject <story_id> [reason]")
            sys.exit(1)
        story_id = sys.argv[2]
        reason = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "未提供原因"
        action_reject(story_id, reason)
    
    elif action == "list":
        action_list()
    
    elif action == "check-stale":
        max_days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        action_check_stale(max_days)
    
    else:
        print(f"❌ 未知操作: {action}")
        print("可用操作: create, submit, approve, reject, start, complete, archive, status, list, check-stale")
        sys.exit(1)
