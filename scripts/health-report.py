#!/usr/bin/env python3
"""
health-report.py v2 — Skill 系统健康度报告生成器

由 cron 每周自动调用，生成健康度报告并发送给主人。
使用 skill-tree-index.py --json 获取统计（避免全量 audit 超时）。

用法:
  python3 ~/.hermes/skills/epic002/scripts/health-report.py          # 标准报告
  python3 ~/.hermes/skills/epic002/scripts/health-report.py --full   # 强制完整版
  python3 ~/.hermes/skills/epic002/scripts/health-report.py --brief  # 强制精简版
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ── 路径 ──
CAP_PACK_DIR = Path.home() / "projects" / "hermes-cap-pack"
SCRIPTS_DIR = CAP_PACK_DIR / "scripts"
STATE_FILE = Path.home() / ".hermes" / "health-report-state.json"


def run_script(name: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPTS_DIR / name)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def extract_health_metrics(tree_data: list) -> dict:
    """从 tree index 数据中提取健康度指标"""
    total_skills = 0
    total_modules = len(tree_data)
    micro_skills = 0
    unclassified = 0
    module_breakdown = []

    for mod in tree_data:
        mod_skills = 0
        for cluster in mod.get("clusters", []):
            skills = cluster.get("skills", [])
            mod_skills += len(skills)
            for s in skills:
                if s.get("line_count", 999) < 50:
                    micro_skills += 1
        total_skills += mod_skills
        if mod.get("module_id") == "unclassified":
            unclassified = mod_skills
        module_breakdown.append({
            "module_id": mod["module_id"],
            "count": mod_skills,
            "needs_attention": mod.get("needs_attention", 0),
        })

    # 按技能数排序
    module_breakdown.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_skills": total_skills,
        "total_modules": total_modules,
        "micro_skills": micro_skills,
        "unclassified": unclassified,
        "module_breakdown": module_breakdown[:5],  # Top 5
    }


def detect_degradation(metrics: dict, last_state: dict) -> list[str]:
    """检测退化"""
    issues = []
    if not last_state:
        return issues

    prev_total = last_state.get("total_skills", 0)
    curr_total = metrics["total_skills"]
    if curr_total < prev_total:
        issues.append(f"技能总数减少: {prev_total} → {curr_total}")

    prev_micro = last_state.get("micro_skills", 0)
    curr_micro = metrics["micro_skills"]
    if curr_micro > prev_micro:
        issues.append(f"微小 skill 增加: {prev_micro} → {curr_micro} (↑{curr_micro - prev_micro})")

    prev_uncls = last_state.get("unclassified", 0)
    curr_uncls = metrics["unclassified"]
    if curr_uncls > prev_uncls:
        issues.append(f"未分类 skill 增加: {prev_uncls} → {curr_uncls}")

    return issues


def generate_report(full: bool = False, brief: bool = False) -> str:
    """生成健康度报告"""

    # Step 1: 获取树状索引 JSON（快速）
    tree_result = run_script("skill-tree-index.py", "--json", timeout=30)
    if tree_result.returncode != 0:
        return f"❌ 健康度报告生成失败: skill-tree-index.py 返回 {tree_result.returncode}\n{tree_result.stderr}"

    tree_data = json.loads(tree_result.stdout)
    metrics = extract_health_metrics(tree_data)
    last_state = load_state()
    issues = detect_degradation(metrics, last_state)

    # 保存本次状态
    save_state({
        "total_skills": metrics["total_skills"],
        "micro_skills": metrics["micro_skills"],
        "unclassified": metrics["unclassified"],
        "generated_at": datetime.now().isoformat()[:19],
    })

    # 智能模式
    is_full = full or (not brief and len(issues) > 0)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = [f"📊 **Hermes Skill 健康度报告** — {now}\n"]

    # ── 概览 ──
    parts.append(f"**📈 系统概览**")
    parts.append(f"  📦 能力包: {metrics['total_modules']} 个")
    parts.append(f"  📄 总技能: {metrics['total_skills']} 个")
    parts.append(f"  🔴 微小 skill (<50行): {metrics['micro_skills']} 个")
    parts.append(f"  ❓ 未分类: {metrics['unclassified']} 个")
    parts.append("")

    # ── 退化 ──
    if issues:
        parts.append("**🔴 退化检测**")
        for i in issues:
            parts.append(f"  ⚠️  {i}")
        parts.append("")
    elif not is_full:
        parts.append("✅ **无显著退化**\n")

    # ── Top 模块分布 ──
    if is_full:
        parts.append("**📊 模块分布 Top 5**")
        for m in metrics["module_breakdown"]:
            bar = "█" * max(1, m["count"] // 2)
            parts.append(f"  {m['module_id']:25s} {m['count']:3d} {bar}")
        parts.append("")

    # ── 脚注 ──
    parts.append("---")
    if is_full:
        parts.append(f"*完整版 · 因检测到 {len(issues)} 项变化*")
    else:
        parts.append("*精简版 · 无显著变化*")
    parts.append("*数据源: skill-tree-index.py --json*")

    return "\n".join(parts)


def main():
    full = "--full" in sys.argv
    brief = "--brief" in sys.argv
    report = generate_report(full=full, brief=brief)
    print(report)


if __name__ == "__main__":
    main()
