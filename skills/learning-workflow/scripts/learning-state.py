#!/usr/bin/env python3
"""
learning-state.py v2.0 — 学习流程状态机管理（多任务版）
用法:
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py init "主题"
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py check <step> [task_id]
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py complete <step> [task_id]
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py reject <step> <reason> [task_id]
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py regress <target_step> [task_id]
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py loop-status [task_id]
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py status [task_id]
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py list
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py reset [task_id]
  python3 ~/.hermes/skills/learning-workflow/scripts/learning-state.py progress [task_id]

改进:
  1. 多任务支持（用 task_id 区分不同学习任务）
  2. 进度百分比估算（基于各步骤的预估工作量权重）
  3. 历史记录追踪（查看所有已完成和进行中的任务）
  4. 自动归档已完成的任务
"""

import json
import os
import sys
import re
import glob
from datetime import datetime
from pathlib import Path

STATE_FILE = os.path.expanduser("~/.hermes/learning_state.json")
HISTORY_FILE = os.path.expanduser("~/.hermes/learning_history.json")
ARTIFACT_DIR = os.path.expanduser("~/.hermes/learning")

# 步骤权重 — 用于进度百分比估算（总和=100）
# 权重基于各步骤的典型工作量占比
STEP_WEIGHTS = {
    "step0_map": 5,       # 知识图谱分析（轻量）
    "step1_search": 20,   # 搜索（中等）
    "step2_read": 30,     # 深度阅读（最重）
    "step3_extract": 20,  # 知识提炼（中等）
    "step4_scaffold": 15, # Skill 脚手架（中等）
    "step5_validate": 10, # 验证测试（轻量）
}

STEPS = {
    "step0_map": {"artifact": os.path.join(ARTIFACT_DIR, "knowledge_map.md")},
    "step1_search": {"artifact": os.path.join(ARTIFACT_DIR, "raw_search_results.md")},
    "step2_read": {"artifact": os.path.join(ARTIFACT_DIR, "reading_notes.md")},
    "step3_extract": {"artifact": os.path.join(ARTIFACT_DIR, "extracted_knowledge.md")},
    "step4_scaffold": {"artifact": None},  # 由 skill-creator 处理
    "step5_validate": {"artifact": None}   # 由 skill-creator 处理
}


def sanitize_task_id(topic):
    """从主题生成安全的 task_id"""
    safe = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]', '_', topic.lower())
    safe = re.sub(r'_+', '_', safe)
    safe = safe.strip('_')
    return safe[:64] or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def load_state():
    """加载所有任务的状态，支持旧版单任务格式自动迁移"""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE) as f:
            raw = json.load(f)
        
        # 检测旧版格式（直接包含 topic 和 steps 字段）
        if "topic" in raw and "steps" in raw:
            # 旧版单任务格式 → 自动迁移到多任务格式，补充缺失字段
            task_id = sanitize_task_id(raw["topic"])
            raw["task_id"] = raw.get("task_id", task_id)
            return {task_id: raw}
        
        # 已经是多任务格式
        if isinstance(raw, dict):
            # 验证所有键的值都是字典（任务对象）
            for key, value in raw.items():
                if isinstance(value, dict) and "steps" in value:
                    # 确保 task_id 字段存在
                    if "task_id" not in value:
                        value["task_id"] = key
                    continue
                else:
                    return {}
            return raw
            
        return {}
    except (json.JSONDecodeError, IOError):
        return {}


def save_state(state):
    """保存所有任务的状态"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def load_history():
    """加载学习历史"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history):
    """保存学习历史"""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def compute_progress(task_state):
    """计算进度百分比"""
    total_weight = 0
    completed_weight = 0
    
    for step_name, step_info in task_state.get("steps", {}).items():
        weight = STEP_WEIGHTS.get(step_name, 15)
        total_weight += weight
        if step_info.get("status") == "completed":
            completed_weight += weight
    
    if total_weight == 0:
        return 0
    
    return round(completed_weight / total_weight * 100)


def estimate_time_left(task_state):
    """估算剩余时间（粗略分钟数）"""
    status_to_minutes = {
        "pending": 0,
        "in_progress": 0,  # 已开始的不算
        "completed": 0,
        "skipped": 0,
    }
    
    step_to_estimate = {
        "step0_map": 2,
        "step1_search": 5,
        "step2_read": 10,
        "step3_extract": 8,
        "step4_scaffold": 6,
        "step5_validate": 4,
    }
    
    remaining = 0
    for step_name, step_info in task_state.get("steps", {}).items():
        if step_info.get("status") in ("pending", "in_progress"):
            remaining += step_to_estimate.get(step_name, 5)
    
    return remaining


def init_state(topic):
    """初始化一个新任务"""
    state = load_state()
    task_id = sanitize_task_id(topic)
    
    # 检查是否已存在同名任务
    i = 1
    original_id = task_id
    while task_id in state:
        task_id = f"{original_id}_{i}"
        i += 1
    
    task_state = {
        "topic": topic,
        "task_id": task_id,
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "loop_count": {
            "r1": 0,
            "r2": 0,
            "r3": 0,
            "qg": 0
        },
        "refusal_log": [],
        "steps": {
            k: {
                "status": "pending",
                "artifact": v["artifact"]
            } for k, v in STEPS.items()
        }
    }
    
    state[task_id] = task_state
    save_state(state)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    
    print(f"✅ 新学习任务已创建！")
    print(f"📚 主题: {topic}")
    print(f"🔖 任务ID: {task_id}")
    print(f"📊 当前进度: 0%")
    print(f"⏭️  下一步: STEP 1 - 知识图谱分析")
    return task_state


def check_step(step_name, task_id=None):
    """检查某步骤是否完成"""
    state = load_state()
    task_id, task_state = _resolve_task(state, task_id)
    
    if not task_state:
        return False
    
    step = task_state["steps"].get(step_name)
    if not step:
        print(f"🚨 未知步骤：{step_name}")
        return False
    
    # 检查状态
    if step["status"] != "completed":
        print(f"🚨 [{task_id}] {step_name} 未完成（状态：{step['status']}）")
        return False
    
    # 检查产出物
    if step.get("artifact") and not os.path.exists(step["artifact"]):
        print(f"🚨 [{task_id}] {step_name} 的产出物不存在：{step['artifact']}")
        print(f"   ⚠️ 产出物丢失！请重新执行此步骤。")
        return False
    
    progress = compute_progress(task_state)
    print(f"✅ [{task_id}] {step_name} 检查通过（当前总进度：{progress}%）")
    return True


def complete_step(step_name, task_id=None):
    """标记某步骤为完成"""
    state = load_state()
    task_id, task_state = _resolve_task(state, task_id)
    
    if not task_state:
        sys.exit(1)
    
    step = task_state["steps"].get(step_name)
    if not step:
        print(f"🚨 未知步骤：{step_name}")
        sys.exit(1)
    
    step["status"] = "completed"
    step["completed_at"] = datetime.now().isoformat()
    
    # 推进 current_step
    step_keys = list(STEPS.keys())
    current_idx = step_keys.index(step_name)
    if current_idx + 1 < len(step_keys):
        task_state["current_step"] = current_idx + 2
    
    state[task_id] = task_state
    save_state(state)
    
    progress = compute_progress(task_state)
    remaining = estimate_time_left(task_state)
    print(f"✅ [{task_id}] {step_name} 标记为完成")
    print(f"📊 当前总进度: {progress}%")
    print(f"⏱️  预计剩余: ~{remaining} 分钟")
    
    # 如果全部完成，给出提示
    if progress == 100:
        print(f"🎉 [{task_id}] 所有步骤已完成！")
        print(f"💡 提示: 使用 'learning-state.py reset {task_id}' 归档此任务")


def show_status(task_id=None):
    """显示任务状态"""
    state = load_state()
    
    if task_id:
        # 显示指定任务
        task_state = state.get(task_id)
        if not task_state:
            print(f"🚨 未找到任务：{task_id}")
            print("💡 使用 'list' 查看所有任务")
            return
        _print_task_status(task_state)
    elif state:
        # 有多个任务，显示最后一个创建的
        task_keys = list(state.keys())
        if len(task_keys) == 1:
            _print_task_status(state[task_keys[0]])
        else:
            print(f"📚 共有 {len(task_keys)} 个活跃任务:")
            for tid in task_keys:
                ts = state[tid]
                progress = compute_progress(ts)
                status_icon = "✅" if progress == 100 else "🔄" if progress > 0 else "⏳"
                print(f"  {status_icon} [{tid}] {ts['topic']} — {progress}%")
            print()
            print(f"💡 使用 'status <task_id>' 查看详情")
    else:
        print("📭 无活跃学习任务")
        print("💡 使用 'init \"主题\"' 开始新的学习任务")


def _print_task_status(task_state):
    """打印单个任务的状态详情"""
    progress = compute_progress(task_state)
    remaining = estimate_time_left(task_state)
    
    print(f"📚 主题: {task_state['topic']}")
    print(f"🔖 任务ID: {task_state['task_id']}")
    print(f"📊 总进度: {progress}% | 步骤 {task_state['current_step']}/5")
    print(f"⏱️  预计剩余: ~{remaining} 分钟")
    print(f"🕐 创建时间: {task_state.get('created_at', '未知')}")
    print()
    
    # 进度条
    bar_len = 30
    filled = int(bar_len * progress / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"  [{bar}] {progress}%")
    print()
    
    for name, info in task_state["steps"].items():
        status = info["status"]
        artifact = info.get("artifact", "N/A")
        artifact_exists = os.path.exists(artifact) if isinstance(artifact, str) and artifact else "N/A"
        
        # 状态图标
        if status == "completed":
            icon = "✅"
        elif status == "in_progress":
            icon = "🔄"
        elif status == "skipped":
            icon = "⏭️"
        else:
            icon = "⏳"
        
        # 步骤名称简化显示
        step_display = {
            "step0_map": "知识图谱",
            "step1_search": "联网搜索",
            "step2_read": "深度阅读",
            "step3_extract": "知识提炼",
            "step4_scaffold": "Skill脚手架",
            "step5_validate": "验证测试"
        }.get(name, name)
        
        weight = STEP_WEIGHTS.get(name, 15)
        weight_bar = "▰" * (weight // 5) + "▱" * ((20 - weight) // 5)
        
        print(f"  {icon} {step_display} [{status}]")
        print(f"      权重: {weight_bar} ({weight}%) | 产出物: {artifact_exists}")


def list_tasks():
    """列出所有学习任务（包括已完成已归档的）"""
    state = load_state()
    
    print("=" * 50)
    print("📋 当前活跃任务")
    print("=" * 50)
    
    if state:
        for tid, ts in state.items():
            progress = compute_progress(ts)
            created = ts.get("created_at", "")[:16]
            print(f"  {tid}")
            print(f"    📚 {ts['topic']} | {progress}% | {created}")
    else:
        print("  (无活跃任务)")
    
    # 显示历史记录
    history = load_history()
    print()
    print("=" * 50)
    print("📜 已完成历史任务")
    print("=" * 50)
    
    if history:
        for h in history[-10:]:
            completed = h.get("completed_at", h.get("created_at", ""))[:16]
            progress = h.get("final_progress", 100)
            print(f"  ✅ {h['topic']} | {progress}% | {completed}")
    else:
        print("  (无历史记录)")
    
    print()
    print(f"🧮 活跃: {len(state)} | 历史: {len(history)}")


def reset_state(task_id=None):
    """归档任务"""
    state = load_state()
    
    if task_id:
        # 归档指定任务
        task_state = state.pop(task_id, None)
        if not task_state:
            print(f"🚨 未找到任务：{task_id}")
            sys.exit(1)
        _archive_and_save(task_state, state)
    elif state:
        # 归档所有已完成的任务
        completed = {k: v for k, v in state.items() if compute_progress(v) == 100}
        active = {k: v for k, v in state.items() if compute_progress(v) < 100}
        
        if not completed:
            print("📭 没有已完成的任务需要归档")
            return
        
        for tid, ts in completed.items():
            print(f"  归档: [{tid}] {ts['topic']} ({compute_progress(ts)}%)")
        
        # 保留未完成的任务
        save_state(active)
        
        # 将已完成的加入历史
        history = load_history()
        for ts in completed.values():
            history.append({
                "topic": ts["topic"],
                "task_id": ts["task_id"],
                "created_at": ts.get("created_at", ""),
                "completed_at": datetime.now().isoformat(),
                "final_progress": compute_progress(ts),
            })
        save_history(history)
        
        print(f"✅ 已归档 {len(completed)} 个任务，剩余 {len(active)} 个进行中")
    else:
        print("📭 无活跃状态需要重置")


def _archive_and_save(task_state, remaining_state):
    """归档单个任务并保存剩余状态"""
    progress = compute_progress(task_state)
    
    # 保存到历史
    history = load_history()
    history.append({
        "topic": task_state["topic"],
        "task_id": task_state["task_id"],
        "created_at": task_state.get("created_at", ""),
        "completed_at": datetime.now().isoformat(),
        "final_progress": progress,
        "loop_count": task_state.get("loop_count", {}),
    })
    save_history(history)
    
    # 保存剩余状态
    save_state(remaining_state)
    
    print(f"✅ 任务已归档：{task_state['topic']} ({progress}%)")


def regress_step(target_step, task_id=None):
    """回退到指定步骤（重置该步骤及后续所有步骤为 pending）"""
    state = load_state()
    task_id, task_state = _resolve_task(state, task_id)
    if not task_state:
        sys.exit(1)
    
    step_keys = list(STEPS.keys())
    if target_step not in step_keys:
        print(f"🚨 未知步骤：{target_step}")
        print(f"💡 可用步骤: {', '.join(step_keys)}")
        sys.exit(1)
    
    target_idx = step_keys.index(target_step)
    current_idx = task_state.get("current_step", 1) - 1
    
    if target_idx >= current_idx:
        print(f"🚨 无法回退：{target_step} (索引 {target_idx}) 不在已完成步骤之前")
        print(f"💡 当前步骤: step{current_idx + 1} ({step_keys[current_idx] if current_idx < len(step_keys) else '完成'})")
        sys.exit(1)
    
    for i in range(target_idx, len(step_keys)):
        task_state["steps"][step_keys[i]]["status"] = "pending"
        if "completed_at" in task_state["steps"][step_keys[i]]:
            del task_state["steps"][step_keys[i]]["completed_at"]
    
    task_state["current_step"] = target_idx + 1
    
    state[task_id] = task_state
    save_state(state)
    
    progress = compute_progress(task_state)
    loop = task_state.get("loop_count", {}).get("r1", 0) + \
           task_state.get("loop_count", {}).get("r2", 0) + \
           task_state.get("loop_count", {}).get("r3", 0)
    print(f"🔄 [{task_id}] 已回退到 {target_step}")
    print(f"📊 当前进度: {progress}%")
    print(f"🔄 本次循环: L2 总计 {loop} 次")
    print(f"⏭️  继续从 STEP {target_idx + 1} 开始")


def reject_step(step_name, reason, task_id=None):
    """标记某步骤为'需重做'，记录原因"""
    state = load_state()
    task_id, task_state = _resolve_task(state, task_id)
    if not task_state:
        sys.exit(1)
    
    step = task_state["steps"].get(step_name)
    if not step:
        print(f"🚨 未知步骤：{step_name}")
        print(f"💡 可用步骤: {', '.join(STEPS.keys())}")
        sys.exit(1)
    
    step["status"] = "needs_revision"
    step["rejected_at"] = datetime.now().isoformat()
    step["reject_reason"] = reason
    
    if "completed_at" in step:
        del step["completed_at"]
    
    # 记录到 refusal_log
    task_state.setdefault("refusal_log", []).append({
        "step": step_name,
        "reason": reason,
        "rejected_at": step["rejected_at"]
    })
    
    state[task_id] = task_state
    save_state(state)
    
    print(f"🔴 [{task_id}] {step_name} 标记为 \"需重做\"")
    print(f"📝 原因: {reason}")


def loop_status(task_id=None):
    """显示循环状态"""
    state = load_state()
    task_id, task_state = _resolve_task(state, task_id)
    if not task_state:
        return
    
    loop_count = task_state.get("loop_count", {"r1": 0, "r2": 0, "r3": 0, "qg": 0})
    refusal_log = task_state.get("refusal_log", [])
    
    print(f"🔄 循环状态: [{task_id}] {task_state['topic']}")
    print()
    print(f"  L2 中间反思循环 (上限 2 次/检查点):")
    print(f"    R1 搜索质量: {loop_count.get('r1', 0)}/2 " +
          ("⚠️ 已达上限" if loop_count.get('r1', 0) >= 2 else "✅ 还有空间"))
    print(f"    R2 理解深度: {loop_count.get('r2', 0)}/2 " +
          ("⚠️ 已达上限" if loop_count.get('r2', 0) >= 2 else "✅ 还有空间"))
    print(f"    R3 提炼完整性: {loop_count.get('r3', 0)}/2 " +
          ("⚠️ 已达上限" if loop_count.get('r3', 0) >= 2 else "✅ 还有空间"))
    print(f"  L3 质量门禁 (上限 3 次):")
    print(f"    QG 质量门禁: {loop_count.get('qg', 0)}/3 " +
          ("⚠️ 已达上限" if loop_count.get('qg', 0) >= 3 else "✅ 还有空间"))
    print()
    
    if refusal_log:
        print(f"  📋 拒绝记录 ({len(refusal_log)} 条):")
        for entry in refusal_log[-5:]:
            print(f"    🔴 {entry['step']}: {entry['reason'][:80]}")
    else:
        print(f"  📋 无拒绝记录")
    
    # 步骤状态总览
    print()
    print(f"  📊 步骤状态:")
    for name, info in task_state["steps"].items():
        status_icon = {
            "completed": "✅",
            "in_progress": "🔄",
            "pending": "⏳",
            "skipped": "⏭️",
            "needs_revision": "🔴"
        }.get(info["status"], "❓")
        step_display = list(STEPS.keys()).index(name) + 1
        print(f"    {status_icon} step{step_display} {name}: {info['status']}")


def _resolve_task(state, task_id):
    """解析 task_id，如果未指定则使用最新任务"""
    if not state:
        print("📭 无活跃学习任务")
        return None, None
    
    if task_id:
        if task_id not in state:
            print(f"🚨 未找到任务：{task_id}")
            print(f"💡 可用任务: {', '.join(state.keys())}")
            return None, None
        return task_id, state[task_id]
    
    # 使用最新创建的任务
    sorted_tasks = sorted(state.items(), key=lambda x: x[1].get("created_at", ""), reverse=True)
    tid, ts = sorted_tasks[0]
    
    if len(sorted_tasks) > 1:
        print(f"💡 [默认] 使用最近任务: [{tid}] {ts['topic']}")
        print(f"   ⚠️  有 {len(sorted_tasks)} 个活跃任务，建议指定 task_id")
    
    return tid, ts


def show_progress(task_id=None):
    """显示进度条"""
    state = load_state()
    task_id, task_state = _resolve_task(state, task_id)
    
    if not task_state:
        return
    
    progress = compute_progress(task_state)
    remaining = estimate_time_left(task_state)
    
    print(f"📚 {task_state['topic']}")
    
    # 大进度条
    bar_len = 50
    filled = int(bar_len * progress / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"  [ {bar} ]")
    print(f"  {progress}% 完成 | 剩余 ~{remaining} 分钟")
    print()
    
    # 分步进度
    for step_name, step_info in task_state["steps"].items():
        status = step_info["status"]
        step_display = {
            "step0_map": "📐 知识图谱",
            "step1_search": "🔍 联网搜索",
            "step2_read": "📖 深度阅读",
            "step3_extract": "🧪 知识提炼",
            "step4_scaffold": "🏗️ Skill脚手架",
            "step5_validate": "✅ 验证测试"
        }.get(step_name, step_name)
        
        if status == "completed":
            marker = "[✓]"
        elif status == "in_progress":
            marker = "[~]"
        elif status == "skipped":
            marker = "[-]"
        else:
            marker = "[ ]"
        
        print(f"  {marker} {step_display}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 learning-state.py {init|check|complete|status|list|reset|progress} [args]")
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
        step_name = sys.argv[2]
        task_id = sys.argv[3] if len(sys.argv) > 3 else None
        if not check_step(step_name, task_id):
            sys.exit(1)
    elif action == "complete":
        if len(sys.argv) < 3:
            print("🚨 请提供步骤名：learning-state.py complete step1_search")
            sys.exit(1)
        step_name = sys.argv[2]
        task_id = sys.argv[3] if len(sys.argv) > 3 else None
        complete_step(step_name, task_id)
    elif action == "status":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        show_status(task_id)
    elif action == "list":
        list_tasks()
    elif action == "reset":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        reset_state(task_id)
    elif action == "progress":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        show_progress(task_id)
    elif action == "regress":
        if len(sys.argv) < 3:
            print("🚨 请提供目标步骤：learning-state.py regress step1_search")
            sys.exit(1)
        target_step = sys.argv[2]
        task_id = sys.argv[3] if len(sys.argv) > 3 else None
        regress_step(target_step, task_id)
    elif action == "reject":
        if len(sys.argv) < 4:
            print("🚨 用法：learning-state.py reject <step> <reason>")
            sys.exit(1)
        step_name = sys.argv[2]
        reason = sys.argv[3]
        task_id = sys.argv[4] if len(sys.argv) > 4 else None
        reject_step(step_name, reason, task_id)
    elif action == "loop-status":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        loop_status(task_id)
    else:
        print(f"🚨 未知操作：{action}")
        print("可用操作: init, check, complete, reject, regress, loop-status, status, list, reset, progress")
        sys.exit(1)
