#!/usr/bin/env python3
"""
Hermes Pre-flight Check (v2.0) - 增强版守门员
The "Gatekeeper" script. Enforces Learning Workflow & Skill Discovery.

功能:
  1. 验证工作流步骤是否按顺序完成
  2. 检查 skill_finder 是否已运行
  3. 从 learning_state.json 恢复跨会话状态
  4. 防止 context compaction 后规则丢失
  5. 输出 BLOCKED/PASS 状态供 Agent 解析

用法:
    python3 ~/.hermes/scripts/pre_flight.py "<Task Description>"

输出:
    BLOCKED: <原因>  → Agent 必须停止
    PASS: <提示>     → Agent 可以继续
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

HERMES_DIR = os.path.expanduser("~/.hermes")
STATE_FILE = os.path.join(HERMES_DIR, "learning_state.json")
SOUL_FILE = os.path.join(HERMES_DIR, "SOUL.md")
HERMES_MD_FILE = os.path.join(HERMES_DIR, ".hermes.md")

# 关键规则（即使 context compaction 后也不能丢失）
CRITICAL_RULES = [
    "任何任务开始前，必须按顺序执行 STEP 0-3",
    "不跳过检查，即使觉得知道怎么做",
    "不凭记忆，长对话会稀释上下文",
    "持续学习，完成任务后更新对应 skill",
]


def load_state():
    """加载学习状态"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


def check_soul_md_exists():
    """检查 SOUL.md 是否存在"""
    return os.path.exists(SOUL_FILE)


def check_hermes_md_exists():
    """检查 .hermes.md 是否存在"""
    return os.path.exists(HERMES_MD_FILE)


def check_workflow_sequence(state):
    """检查工作流顺序是否正确"""
    if not state or "workflow_steps" not in state:
        return False, "工作流状态不存在"
    
    steps = state["workflow_steps"]
    step_order = ["STEP_0_pre_flight", "STEP_1_skill_scan", "STEP_2_learning", "STEP_3_execution"]
    
    # 检查是否按顺序完成
    prev_completed = True
    for step in step_order:
        if step in steps:
            if steps[step].get("completed"):
                if not prev_completed:
                    return False, f"{step} 完成但前序步骤未完成"
            else:
                prev_completed = False
    
    return True, "工作流顺序正确"


def check_skill_finder_recent(state):
    """检查 skill_finder 是否最近运行过"""
    if not state or "workflow_steps" not in state:
        return False, "未找到 skill_finder 运行记录"
    
    step1 = state["workflow_steps"].get("STEP_1_skill_scan", {})
    if step1.get("completed"):
        timestamp = step1.get("timestamp")
        if timestamp:
            try:
                last_run = datetime.fromisoformat(timestamp)
                age = datetime.now() - last_run
                if age < timedelta(hours=1):
                    return True, f"skill_finder 最近运行过 ({age.seconds // 60} 分钟前)"
                else:
                    return False, f"skill_finder 运行时间过长 ({age.seconds // 3600} 小时前)"
            except:
                return False, "时间戳解析失败"
    
    return False, "STEP_1 未标记为完成"


def get_compression_status(state):
    """获取压缩状态"""
    if not state or "compression_checkpoints" not in state:
        return "未知", 0
    
    checkpoints = state["compression_checkpoints"]
    if checkpoints:
        last = checkpoints[-1]
        return last.get("timestamp", "未知"), last.get("savings_pct", 0)
    
    return "未压缩", 0


def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "Unknown Task"
    
    print("=" * 60)
    print(f"🔍 [Pre-Flight v2.0] 检查任务: {task}")
    print("=" * 60)
    
    # 加载状态
    state = load_state()
    
    # 检查 1: 状态文件是否存在
    if not state:
        print("\n❌ BLOCKED: 学习状态文件不存在或损坏!")
        print("   必须先运行: python3 ~/.hermes/scripts/learning_state.py init")
        sys.exit(1)
    
    # 检查 2: 关键规则文件
    soul_exists = check_soul_md_exists()
    hermes_exists = check_hermes_md_exists()
    
    print(f"\n📁 关键规则文件:")
    print(f"   SOUL.md: {'✅ 存在' if soul_exists else '❌ 缺失'}")
    print(f"   .hermes.md: {'✅ 存在' if hermes_exists else '❌ 缺失 (最高优先级)'}")
    
    if not hermes_exists:
        print("\n⚠️  WARNING: .hermes.md 不存在，最高优先级规则可能未加载!")
    
    # 检查 3: 工作流顺序
    workflow_ok, workflow_msg = check_workflow_sequence(state)
    print(f"\n🔄 工作流顺序: {'✅' if workflow_ok else '❌'} {workflow_msg}")
    
    # 检查 4: skill_finder 状态
    skill_ok, skill_msg = check_skill_finder_recent(state)
    print(f"📡 Skill 扫描: {'✅' if skill_ok else '⚠️'} {skill_msg}")
    
    # 检查 5: 压缩状态
    comp_time, comp_savings = get_compression_status(state)
    print(f"🗜️  Context 压缩: 最后 {comp_time} (节省 {comp_savings:.0f}%)")
    
    # 检查 6: 规则违规历史
    violations = state.get("rule_violations", [])
    if violations:
        print(f"\n⚠️  历史违规: {len(violations)} 次")
        for v in violations[-3:]:
            print(f"   - {v.get('step', 'Unknown')}: {v.get('reason', 'N/A')}")
    
    # 综合判断
    print("\n" + "=" * 60)
    
    if not workflow_ok:
        print("❌ BLOCKED: 工作流顺序不正确!")
        print(f"   原因: {workflow_msg}")
        print("\n📋 正确流程:")
        print("   STEP 0: python3 pre_flight.py")
        print("   STEP 1: skill_finder.py <关键词>")
        print("   STEP 2: skill_view(name) 或 learning-workflow")
        print("   STEP 3: 执行任务")
        sys.exit(1)
    
    if not skill_ok:
        print("⚠️  WARNING: skill_finder 可能未运行或运行时间过长")
        print("   建议: 重新运行 skill_finder.py 确保 skills 最新")
        # 不阻止，但警告
    
    print("✅ PASS: 预检查通过，可以继续执行")
    print("\n🔒 关键规则提醒 (即使 context compaction 后也必须遵守):")
    for rule in CRITICAL_RULES:
        print(f"   • {rule}")
    
    print("\n💡 提示: 任务完成后，记得更新对应的 skill!")
    print("=" * 60)


if __name__ == '__main__':
    main()
