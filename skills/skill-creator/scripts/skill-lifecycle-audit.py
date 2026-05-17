#!/usr/bin/env python3
"""
skill-lifecycle-audit.py v2.0 — Skill 生命周期审计与退役管理

整合 SQS v2.0 质量评分 + 依赖扫描 + 新鲜度检查 + 生命周期状态管理。

用法:
  python3 skill-lifecycle-audit.py <skill-name>             # 审计单个
  python3 skill-lifecycle-audit.py --audit [--threshold N]  # 审计全部
  python3 skill-lifecycle-audit.py --audit --html            # HTML 报告
  python3 skill-lifecycle-audit.py <skill-name> --json      # JSON 输出
  python3 skill-lifecycle-audit.py status [skill]           # 查看状态
  python3 skill-lifecycle-audit.py auto-archive             # 自动归档过期
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"
SQS_SCRIPT = SKILLS_DIR / "skill-creator" / "scripts" / "skill-quality-score.py"
LIFECYCLE_STATE_FILE = Path.home() / ".hermes" / "skill_lifecycle_state.json"
NOW = datetime.now(timezone.utc)

# ── 有效状态 ──────────────────────────────────────────────────
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
    "archived": ["deprecated"],  # 恢复
}

# ── 状态管理 ──────────────────────────────────────────────────

def load_state():
    if LIFECYCLE_STATE_FILE.exists():
        try:
            return json.loads(LIFECYCLE_STATE_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            return {}
    return {}


def save_state(state):
    LIFECYCLE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LIFECYCLE_STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n"
    )


def get_skill_status(skill_name, state):
    return state.get("skills", {}).get(skill_name, {"status": "active"})


def set_skill_status(skill_name, new_status, state, reason=""):
    if "skills" not in state:
        state["skills"] = {}

    if skill_name not in state["skills"]:
        state["skills"][skill_name] = {}

    old_status = state["skills"][skill_name].get("status", "active")

    # 检查转换是否合法
    if old_status in STATUS_TRANSITIONS:
        if new_status not in STATUS_TRANSITIONS[old_status]:
            print(f"  ⚠️  非法转换: {old_status} → {new_status}")
            print(f"     允许: {old_status} → {'/'.join(STATUS_TRANSITIONS[old_status])}")
            return False

    state["skills"][skill_name].update({
        "status": new_status,
        f"{new_status}_at": NOW.isoformat(),
        "status_reason": reason,
    })
    save_state(state)
    return True


# ── 数据收集 ──────────────────────────────────────────────────

def get_sqs_score(skill_name):
    try:
        result = subprocess.run(
            [sys.executable, str(SQS_SCRIPT), skill_name, "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
    except Exception:
        pass
    return None


def get_freshness(skill_name):
    sk_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not sk_path.exists():
        return {"exists": False}
    mtime = datetime.fromtimestamp(sk_path.stat().st_mtime, tz=timezone.utc)
    days = (NOW - mtime).days
    return {
        "exists": True,
        "last_modified_days_ago": days,
        "freshness": "🟢" if days < 30 else "🟡" if days < 90 else "🟠" if days < 180 else "🔴",
    }


def get_referrers(skill_name):
    referrers = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            try:
                content = (Path(root) / "SKILL.md").read_text(encoding="utf-8")
                fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                if fm_match:
                    import yaml
                    fm = yaml.safe_load(fm_match.group(1)) or {}
                    depends = fm.get("depends_on", []) or []
                    if skill_name in depends:
                        referrers.append(os.path.basename(root))
            except Exception:
                pass
    return referrers


# ── 审计单个 ──────────────────────────────────────────────────

def audit_single(skill_name, output_json=False):
    sqs = get_sqs_score(skill_name)
    fresh = get_freshness(skill_name)
    referrers = get_referrers(skill_name)
    state = load_state()
    lifecycle = get_skill_status(skill_name, state)

    report = {
        "skill": skill_name,
        "sqs": sqs,
        "freshness": fresh,
        "referrers": referrers,
        "referrer_count": len(referrers),
        "lifecycle": lifecycle,
        "audit_timestamp": NOW.isoformat(),
    }

    status = lifecycle.get("status", "active")
    sqs_total = (sqs or {}).get("sqs_total", 0)
    level = (sqs or {}).get("level", "N/A")
    fresh_days = (fresh or {}).get("last_modified_days_ago", -1)

    # 自动检测问题
    issues = []
    if sqs_total < 50:
        issues.append(f"🔴 SQS 过低 ({sqs_total}/140)，建议改进或废弃")
    if status == "deprecated" and fresh_days > 30:
        issues.append(f"🗑️ 已废弃 {fresh_days} 天，建议归档")
    if len(referrers) > 0 and status in ("archived",):
        issues.append(f"⚠️ 已归档但仍有 {len(referrers)} 个引用！")
    if fresh_days > 180 and status == "active":
        issues.append(f"🟡 超过 180 天未活跃，可考虑 frozen")

    if output_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        emoji = STATUS_EMOJI.get(status, "❓")
        print(f"\n{'='*55}")
        print(f"  🔬 生命周期审计: {skill_name}")
        print(f"{'='*55}")
        print(f"  📊 SQS: {sqs_total}/140 {level}")
        if sqs:
            for d, s in (sqs.get("dimensions", {}) or {}).items():
                print(f"       {d}: {s}/20")
        print(f"  🔗 被 {len(referrers)} 个 skill 引用: {', '.join(referrers[:5]) or '无'}")
        if fresh.get("exists"):
            print(f"  ⏱️  最后更新: {fresh_days} 天前 {fresh.get('freshness', '?')}")
        print(f"  🔄 生命周期: {emoji} {status}")
        if lifecycle.get("deprecated_at"):
            print(f"     废弃于: {lifecycle['deprecated_at'][:19]}")
        if issues:
            print(f"\n  💡 建议:")
            for i in issues:
                print(f"     {i}")
        # 建议转换
        allowed = STATUS_TRANSITIONS.get(status, [])
        if allowed:
            print(f"  可转换至: {'/'.join(allowed)}")
        print(f"{'='*55}\n")

    return report


# ── 全量审计 ──────────────────────────────────────────────────

def audit_all(threshold=50, html=False):
    all_results = []
    state = load_state()

    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            name = os.path.basename(root)
            try:
                report = audit_single(name, output_json=False)
                if report:
                    all_results.append(report)
            except Exception:
                pass

    sqs_total_map = {}
    for r in all_results:
        t = (r.get("sqs") or {}).get("sqs_total", 0) or 0
        sqs_total_map[r["skill"]] = t

    all_results.sort(key=lambda r: sqs_total_map.get(r["skill"], 0), reverse=True)

    total = len(all_results)
    below = [r for r in all_results if sqs_total_map.get(r["skill"], 0) < threshold]

    # 状态统计
    status_counts = {}
    for r in all_results:
        s = r.get("lifecycle", {}).get("status", "active")
        status_counts[s] = status_counts.get(s, 0) + 1

    if html:
        _generate_html_report(all_results, total, below, status_counts)
        return

    print(f"\n{'#'*55}")
    print(f"#  🔬 Lifecycle v2.0 审计报告")
    print(f"#  扫描: {total} skills  |  满分: 140")
    print(f"{'#'*55}")
    print(f"\n📊 状态分布:")
    for s, c in sorted(status_counts.items()):
        emoji = STATUS_EMOJI.get(s, "❓")
        print(f"  {emoji} {s}: {c}")

    print(f"\n⚠️  低于阈值({threshold}): {len(below)}")
    for r in below[:15]:
        t = sqs_total_map.get(r["skill"], "?")
        status = r.get("lifecycle", {}).get("status", "?")
        days = (r.get("freshness") or {}).get("last_modified_days_ago", "?")
        print(f"  {t:>5}  {r['skill']:30s} [{status}] ({days}d)")

    if len(below) > 15:
        print(f"  ...及另外 {len(below)-15} 个")

    # 维度统计
    dim_scores = {f"S{i}_": [] for i in range(1, 8)}
    for r in all_results:
        dims = (r.get("sqs") or {}).get("dimensions", {}) or {}
        for dk, dv in dims.items():
            for prefix in dim_scores:
                if dk.startswith(prefix):
                    dim_scores[prefix].append(dv)

    dim_names = {
        "S1_": "元数据完整性", "S2_": "结构合规性", "S3_": "内容可执行性",
        "S4_": "时效性", "S5_": "关联完整性", "S6_": "可发现性", "S7_": "验证覆盖度",
    }
    print(f"\n📊 维度平均分:")
    for prefix, scores in dim_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            name = dim_names.get(prefix, prefix)
            icon = "🟢" if avg >= 15 else ("🟡" if avg >= 10 else "🔴")
            bar = "█" * int(avg) + "░" * (20 - int(avg))
            print(f"  {icon} {name}: {avg:5.1f}/20 {bar}")

    print(f"\n💡 建议自动归档 (deprecated > 30d): ", end="")
    auto_archive_candidates = [
        r for r in all_results
        if r.get("lifecycle", {}).get("status") == "deprecated"
        and (r.get("freshness") or {}).get("last_modified_days_ago", 0) > 30
    ]
    if auto_archive_candidates:
        print(f"{len(auto_archive_candidates)} 个")
        for r in auto_archive_candidates[:5]:
            print(f"  {r['skill']}")
        print(f"\n  运行 `{__file__} auto-archive` 自动处理")
    else:
        print("无")

    print()


def _generate_html_report(results, total, below, status_counts):
    """生成 HTML 格式的审计报告"""
    dim_names = {
        "S1_": "元数据完整性", "S2_": "结构合规性", "S3_": "内容可执行性",
        "S4_": "时效性", "S5_": "关联完整性", "S6_": "可发现性", "S7_": "验证覆盖度",
    }
    report_path = Path.home() / ".hermes" / "reports" / f"skill-lifecycle-audit-{NOW.strftime('%Y%m%d')}.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    lines.append(f"<title>Skill Lifecycle Audit - {NOW.strftime('%Y-%m-%d')}</title>")
    lines.append("<style>body{font-family:-apple-system,sans-serif;max-width:960px;margin:2em auto;padding:0 1em}")
    lines.append("h1{color:#333;border-bottom:2px solid #eee}h2{color:#555}")
    lines.append("table{border-collapse:collapse;width:100%;margin:1em 0}")
    lines.append("th,td{text-align:left;padding:8px;border-bottom:1px solid #ddd}")
    lines.append("tr:hover{background:#f5f5f5}")
    lines.append(".pass{color:#2e7d32}.warn{color:#f57c00}.fail{color:#d32f2f}")
    lines.append(".bar{display:inline-block;height:12px;background:#4caf50;border-radius:6px;vertical-align:middle}")
    lines.append("</style></head><body>")
    lines.append(f"<h1>🔬 Skill Lifecycle Audit v2.0</h1>")
    lines.append(f"<p>Scan: {total} skills | {NOW.strftime('%Y-%m-%d %H:%M')} UTC</p>")

    # Status summary
    lines.append("<h2>Status Distribution</h2><ul>")
    for s in ["active", "under_review", "frozen", "deprecated", "archived"]:
        c = status_counts.get(s, 0)
        emoji = STATUS_EMOJI.get(s, "❓")
        if c > 0:
            lines.append(f"<li>{emoji} {s}: {c}</li>")
    lines.append(f"<li>⚠️ Below threshold: {len(below)}</li></ul>")

    # Table
    lines.append("<h2>All Skills</h2>")
    lines.append("<table><tr><th>Skill</th><th>SQS</th><th>Status</th><th>Fresh</th><th>Refs</th><th>Weak Dims</th></tr>")
    for r in results:
        sqs_total = (r.get("sqs") or {}).get("sqs_total", "?")
        dims = (r.get("sqs") or {}).get("dimensions", {}) or {}
        weak = [dim_names.get(k, k) for k, v in dims.items() if v < 10]
        status = r.get("lifecycle", {}).get("status", "active")
        fresh_days = (r.get("freshness") or {}).get("last_modified_days_ago", "?")
        refs = r.get("referrer_count", 0)
        lines.append(
            f"<tr><td>{r['skill']}</td><td>{sqs_total}/140</td>"
            f"<td>{status}</td><td>{fresh_days}d</td><td>{refs}</td>"
            f"<td>{', '.join(weak[:3]) or '—'}</td></tr>"
        )
    lines.append("</table></body></html>")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📄 HTML 报告已生成: {report_path}")


# ── 自动归档 ──────────────────────────────────────────────────

def auto_archive():
    state = load_state()
    archived = 0

    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            name = os.path.basename(root)
            fresh = get_freshness(name)
            status = get_skill_status(name, state)

            if status.get("status") == "deprecated":
                days = fresh.get("last_modified_days_ago", 0)
                if days > 30:
                    print(f"  📦 {name}: 废弃 {days}d → 归档")
                    set_skill_status(name, "archived", state, "自动归档: 废弃超过30天")
                    archived += 1

    print(f"\n✅ 自动归档完成: {archived} 个 skill 已归档")


# ── 入口 ──────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    output_json = "--json" in sys.argv
    threshold = 50
    for i, arg in enumerate(sys.argv):
        if arg == "--threshold" and i + 1 < len(sys.argv):
            try:
                threshold = int(sys.argv[i + 1])
            except ValueError:
                pass

    action = sys.argv[1]

    if action == "--audit":
        html = "--html" in sys.argv
        audit_all(threshold, html=html)
    elif action == "status":
        skill = sys.argv[2] if len(sys.argv) > 2 else None
        state = load_state()
        if skill:
            life = get_skill_status(skill, state)
            emoji = STATUS_EMOJI.get(life.get("status", "active"), "❓")
            print(f"\n{emoji} {skill}: {life.get('status', 'active')}")
            if life.get("deprecated_at"):
                print(f"   废弃: {life['deprecated_at'][:19]}")
            if life.get("archived_at"):
                print(f"   归档: {life['archived_at'][:19]}")
        else:
            sk = state.get("skills", {})
            if sk:
                print(f"\n📋 生命周期状态 ({len(sk)} 个):")
                for name, info in sorted(sk.items()):
                    emoji = STATUS_EMOJI.get(info.get("status", "active"), "❓")
                    print(f"  {emoji} {name:30s} {info.get('status', 'active')}")
            else:
                print("📭 无显式状态记录 (默认 active)")
    elif action == "auto-archive":
        auto_archive()
    else:
        # 默认: 审计单个 skill
        audit_single(action, output_json=output_json)


if __name__ == "__main__":
    main()
