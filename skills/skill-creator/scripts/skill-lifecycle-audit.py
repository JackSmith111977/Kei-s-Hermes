#!/usr/bin/env python3
"""
skill-lifecycle-audit.py v1.0 — Skill 生命周期审计与退役管理

整合 SQS 质量评分 + 依赖扫描 + 新鲜度检查 > 一键审计报告。

用法:
  python3 skill-lifecycle-audit.py <skill-name>            # 审计单个 skill
  python3 skill-lifecycle-audit.py --audit [--threshold N] # 审计所有 skill
  python3 skill-lifecycle-audit.py deprecate <skill-name>  # 标记退役
  python3 skill-lifecycle-audit.py revive <skill-name>     # 恢复退役
  python3 skill-lifecycle-audit.py status [skill-name]     # 查看生命周期状态
  python3 skill-lifecycle-audit.py --json                  # JSON 输出
"""

import os, sys, json, subprocess, re
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"
SQS_SCRIPT = SKILLS_DIR / "skill-creator" / "scripts" / "skill-quality-score.py"
DEP_SCAN = SKILLS_DIR / "skill-creator" / "scripts" / "dependency-scan.py"
STATE_FILE = Path.home() / ".hermes" / "skill_lifecycle_state.json"
NOW = datetime.now(timezone.utc)


def load_lifecycle_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            return {}
    return {}


def save_lifecycle_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def get_sqs_score(skill_name):
    """调用 SQS 脚本获取质量分"""
    try:
        result = subprocess.run(
            [sys.executable, str(SQS_SCRIPT), skill_name, "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        return None
    except:
        return None


def get_dependency_info(skill_name):
    """调用依赖扫描获取引用信息"""
    try:
        result = subprocess.run(
            [sys.executable, str(DEP_SCAN), "--target", skill_name],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        refs = re.findall(r'→ 被 (\d+) 个 skill 引用', output)
        deps = re.findall(r'← 依赖: (.+)', output)
        return {
            "referenced_by_count": int(refs[0]) if refs else 0,
            "dependencies": deps[0].split(', ') if deps else [],
            "raw_output": output[:200],
        }
    except:
        return {"referenced_by_count": 0, "dependencies": []}


def get_freshness_score(skill_name):
    """检查新鲜度"""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        return {"exists": False}
    mtime = datetime.fromtimestamp(skill_path.stat().st_mtime, tz=timezone.utc)
    days = (NOW - mtime).days
    return {
        "exists": True,
        "last_modified_days_ago": days,
        "freshness": "🟢" if days < 30 else "🟡" if days < 90 else "🔴" if days > 180 else "🟠",
    }


def cmd_audit_single(skill_name, output_json=False):
    """审计单个 skill 的完整生命周期"""
    sqs = get_sqs_score(skill_name)
    deps = get_dependency_info(skill_name)
    fresh = get_freshness_score(skill_name)
    lc_state = load_lifecycle_state()
    lifecycle = lc_state.get(skill_name, {"status": "active"})

    report = {
        "skill": skill_name,
        "sqs": sqs,
        "dependencies": deps,
        "freshness": fresh,
        "lifecycle": lifecycle,
        "audit_timestamp": NOW.isoformat(),
    }

    if output_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report

    print(f"\n{'='*55}")
    print(f"  🔬 生命周期审计: {skill_name}")
    print(f"{'='*55}")

    # SQS
    if sqs:
        total = sqs.get("sqs_total", 0)
        level = sqs.get("level", "?")
        print(f"  📊 SQS: {total}/100  {level}")
        for dim, score in sqs.get("dimensions", {}).items():
            print(f"       {dim}: {score}/20")
    else:
        print(f"  ❌ SQS: 无法评分")

    # 引用关系
    print(f"  🔗 被 {deps.get('referenced_by_count', '?')} 个 skill 引用")
    if deps.get("dependencies"):
        print(f"     ← 依赖: {', '.join(deps['dependencies'])}")

    # 新鲜度
    if fresh.get("exists"):
        days = fresh.get("last_modified_days_ago", 0)
        emoji = fresh.get("freshness", "?")
        print(f"  ⏱️  最后更新: {days} 天前 {emoji}")

    # 生命周期状态
    lc_status = lifecycle.get("status", "active")
    emoji_map = {
        "active": "🟢", "deprecated": "🔴", "frozen": "🟡",
        "archived": "⚫", "under_review": "🟠",
    }
    print(f"  🔄 生命周期: {emoji_map.get(lc_status, '❓')} {lc_status}")

    # 综合建议
    print(f"\n  💡 建议:")
    suggestions = []

    if sqs and sqs.get("sqs_total", 0) < 50:
        suggestions.append(f"🔴 质量分过低，建议立即改进")
        if lifecycle.get("status") != "deprecated":
            suggestions.append(f"   → 考虑标记为 deprecated 或更新内容")

    if sqs and sqs.get("dimensions", {}).get("S4_relations", 20) < 10:
        suggestions.append(f"🟡 缺少依赖声明 (depends_on)，建议补充")

    if sqs and sqs.get("dimensions", {}).get("S5_discoverability", 20) < 10:
        suggestions.append(f"🟡 triggers/tags 不足，影响 skill_finder 发现")

    if fresh.get("last_modified_days_ago", 0) > 180:
        suggestions.append(f"🔴 超过 180 天未更新，建议检查内容是否仍有效")

    if deps.get("referenced_by_count", 0) == 0 and fresh.get("last_modified_days_ago", 0) > 90:
        suggestions.append(f"🟠 无引用 + 超过 90 天未更新 → 可考虑归档")

    for s in suggestions or ["✅ 状态良好，无需操作"]:
        print(f"     {s}")

    print(f"{'='*55}\n")
    return report


def cmd_audit_all(threshold=50, output_json=False):
    """审计所有 skill"""
    all_results = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            name = os.path.basename(root)
            try:
                report = cmd_audit_single(name, output_json=False)
                if report:
                    all_results.append(report)
            except:
                pass

    # 按 SQS 排序
    all_results.sort(key=lambda r: (r.get("sqs") or {}).get("sqs_total", 0) or 0)

    total = len(all_results)
    below = [r for r in all_results if (r.get("sqs") or {}).get("sqs_total", 100) < threshold]

    print(f"\n{'#'*55}")
    print(f"#  🔬 全量生命周期审计报告")
    print(f"#  扫描: {total} skills")
    print(f"#  低于阈值({threshold}): {len(below)}")
    print(f"{'#'*55}")

    if below:
        print(f"\n⚠️  需关注 ({len(below)} 个):")
        for r in below[:15]:
            sqs_total = (r.get("sqs") or {}).get("sqs_total", 0)
            life = r.get("lifecycle", {}).get("status", "active")
            fresh_days = (r.get("freshness") or {}).get("last_modified_days_ago", 0)
            print(f"  {sqs_total:5.1f}  {r['skill']:30s} [{r.get('lifecycle',{}).get('status','?')}] ({fresh_days}d)")
        if len(below) > 15:
            print(f"  ...及另外 {len(below)-15} 个")

    if output_json:
        print(json.dumps({
            "total": total,
            "below_threshold": len(below),
            "results": all_results,
        }, ensure_ascii=False, indent=2))


def cmd_deprecate(skill_name):
    """标记 skill 为 deprecated"""
    state = load_lifecycle_state()
    if skill_name not in state:
        state[skill_name] = {}
    state[skill_name]["status"] = "deprecated"
    state[skill_name]["deprecated_at"] = NOW.isoformat()

    # 检查引用
    deps = get_dependency_info(skill_name)
    if deps.get("referenced_by_count", 0) > 0:
        print(f"⚠️  警告: {skill_name} 被 {deps['referenced_by_count']} 个 skill 引用!")
        print(f"   退役后这些引用将断裂。请先更新引用者。")

    save_lifecycle_state(state)
    print(f"🔴 Skill '{skill_name}' 已标记为 deprecated")


def cmd_revive(skill_name):
    """恢复已退役的 skill"""
    state = load_lifecycle_state()
    if skill_name in state:
        state[skill_name]["status"] = "active"
        state[skill_name]["revived_at"] = NOW.isoformat()
        save_lifecycle_state(state)
        print(f"🟢 Skill '{skill_name}' 已恢复为 active")
    else:
        print(f"⚠️  Skill '{skill_name}' 无生命周期状态")


def cmd_status(skill_name=None):
    """查看生命周期状态"""
    state = load_lifecycle_state()
    if skill_name:
        info = state.get(skill_name, {"status": "active (default)"})
        print(f"\n  🔄 {skill_name}: {info.get('status', 'active')}")
        if info.get("deprecated_at"):
            print(f"     退役: {info['deprecated_at'][:19]}")
        return

    if not state:
        print("📭 (无显式的生命周期状态，默认为 active)")
        return

    print(f"\n📋 生命周期状态 ({len(state)} 个):")
    for name, info in sorted(state.items()):
        emoji = {"active": "🟢", "deprecated": "🔴", "frozen": "🟡",
                 "archived": "⚫", "under_review": "🟠"}.get(info.get("status"), "❓")
        print(f"  {emoji} {name:30s} {info.get('status', '?')}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)

    output_json = '--json' in sys.argv
    threshold = 50
    for i, arg in enumerate(sys.argv):
        if arg == '--threshold' and i + 1 < len(sys.argv):
            try:
                threshold = int(sys.argv[i + 1])
            except:
                pass

    action = sys.argv[1]

    if action == '--audit':
        cmd_audit_all(threshold, output_json)
    elif action == 'deprecate' and len(sys.argv) > 2:
        cmd_deprecate(sys.argv[2])
    elif action == 'revive' and len(sys.argv) > 2:
        cmd_revive(sys.argv[2])
    elif action == 'status':
        cmd_status(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        cmd_audit_single(action, output_json)


if __name__ == "__main__":
    main()
