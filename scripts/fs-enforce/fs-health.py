#!/usr/bin/env python3
"""
fs-health.py — 文件系统健康检查脚本

检查 Hermes 文件系统的健康状态，整合以下维度：
  1. 根目录散乱文件检查（参照 file-system-manager 的 file-health-check.py）
  2. 命名规范检查（随机抽样）
  3. 保护路径完整性检查
  4. 磁盘使用率检查
  5. Skill 合规性快速检查
  6. 审计日志完整性检查

用法:
  python3 fs-health.py               # 输出 Markdown 报告
  python3 fs-health.py --html         # 输出 HTML 报告
  python3 fs-health.py --deliver      # 适合发送给用户的格式
"""

import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── 配置 ───────────────────────────────────────────────────────────────
HERMES_HOME = os.path.expanduser(os.environ.get("HERMES_HOME", "~/.hermes"))
AUDIT_LOG = os.path.join(HERMES_HOME, "data", "fs-audit", "audit.log")
SKILLS_DIR = os.path.join(HERMES_HOME, "skills")

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# ── 检查函数 ──────────────────────────────────────────────────────────

def check_root_clutter() -> list:
    """检查根目录散乱文件。"""
    issues = []
    expected_dirs = {
        "config", "skills", "scripts", "cache", "cron",
        "docs", "data", "state", "providers", "archive",
        "experiences", "brain", "sessions", "learning",
        "plugins", "sandboxes", "profiles",
    }
    expected_files = {
        "AGENTS.md", "SOUL.md", "state.db",
        "channel_directory.json", "installed_packs.json",
        "sdd_state.json",
    }

    try:
        for item in os.listdir(HERMES_HOME):
            if item.startswith("."):
                continue
            full = os.path.join(HERMES_HOME, item)
            if os.path.isdir(full) and item in expected_dirs:
                continue
            if os.path.isfile(full) and item in expected_files:
                continue
            if os.path.isdir(full):
                issues.append({"type": "info", "msg": f"未知目录: {item}"})
            else:
                issues.append({"type": "warning", "msg": f"根目录散乱文件: {item}"})
    except OSError as e:
        issues.append({"type": "error", "msg": f"无法读取根目录: {e}"})

    return issues


def check_protected_paths() -> list:
    """检查保护路径是否存在。"""
    issues = []
    protected = ["AGENTS.md", "SOUL.md", "config/config.yaml", "state.db"]
    for p in protected:
        full = os.path.join(HERMES_HOME, p)
        if not os.path.exists(full):
            issues.append({"type": "error", "msg": f"保护路径缺失: {p}"})
    return issues


def check_naming_sample(sample_size: int = 20) -> list:
    """随机抽样检查文件名规范。"""
    issues = []
    forbidden_chars = set(' \\:*?"<>|')
    forbidden_names = {"test.txt", "output.json", "file.py",
                       "new_1.md", "untitled.md", "tmp.txt"}

    all_files = []
    for root, dirs, files in os.walk(HERMES_HOME):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        for f in files:
            if any(skip in root for skip in ["node_modules", ".git", "__pycache__"]):
                continue
            all_files.append(os.path.join(root, f))

    sample = random.sample(all_files, min(sample_size, len(all_files)))
    for f in sample:
        basename = os.path.basename(f)
        name_issues = []

        if " " in basename:
            name_issues.append("含空格")
        for c in forbidden_chars:
            if c in basename:
                name_issues.append(f"含禁止字符")
                break
        if basename.lower() in forbidden_names:
            name_issues.append("禁止文件名")
        if "." in basename:
            ext = basename.rsplit(".", 1)[1]
            if ext != ext.lower():
                name_issues.append("扩展名未小写")

        if name_issues:
            rel = f[len(HERMES_HOME):] if f.startswith(HERMES_HOME) else f
            issues.append({
                "type": "warning",
                "msg": f"命名违规: {rel} — {'; '.join(name_issues)}",
            })

    return issues


def check_disk_usage() -> list:
    """检查磁盘使用率。"""
    issues = []
    try:
        stat = os.statvfs(HERMES_HOME)
        total = stat.f_frsize * stat.f_blocks
        free = stat.f_frsize * stat.f_bfree
        used = total - free
        usage_pct = (used / total) * 100

        issues.append({
            "type": "info",
            "msg": f"磁盘总容量: {total / 1024**3:.1f}GB, "
                   f"已用: {used / 1024**3:.1f}GB ({usage_pct:.0f}%), "
                   f"可用: {free / 1024**3:.1f}GB",
        })

        if usage_pct > 80:
            issues.append({"type": "warning", "msg": f"磁盘使用率 {usage_pct:.0f}%，超过 80% 警戒线"})
        if usage_pct > 90:
            issues.append({"type": "error", "msg": f"磁盘使用率 {usage_pct:.0f}%，超过 90% 危险线"})

        # 各主要目录大小
        for subdir in ["skills", "cache", "sessions", "cron", "docs", "scripts"]:
            path = os.path.join(HERMES_HOME, subdir)
            if os.path.exists(path):
                size = sum(
                    os.path.getsize(os.path.join(dp, f))
                    for dp, dn, fn in os.walk(path)
                    for f in fn
                ) / 1024**2
                issues.append({
                    "type": "info",
                    "msg": f"  {subdir}/: {size:.1f}MB",
                })

    except OSError as e:
        issues.append({"type": "error", "msg": f"磁盘检查失败: {e}"})

    return issues


def check_audit_log() -> list:
    """检查审计日志完整性。"""
    issues = []
    if not os.path.exists(AUDIT_LOG):
        issues.append({"type": "warning", "msg": "审计日志不存在，审计管道未生效"})
        return issues

    try:
        size_mb = os.path.getsize(AUDIT_LOG) / 1024**2
        issues.append({"type": "info", "msg": f"审计日志大小: {size_mb:.2f}MB"})

        if size_mb > 10:
            issues.append({"type": "warning", "msg": "审计日志超过 10MB，建议清理"})

        with open(AUDIT_LOG) as f:
            count = sum(1 for line in f if line.strip())

        issues.append({"type": "info", "msg": f"审计日志条目: {count}"})

        # 检查最近一条记录
        with open(AUDIT_LOG) as f:
            last_line = ""
            for line in f:
                if line.strip():
                    last_line = line
        if last_line:
            entry = json.loads(last_line)
            issues.append({
                "type": "info",
                "msg": f"最近审计: [{entry.get('ts','?')[:19]}] {entry.get('tool','?')} → {entry.get('verdict','?')}",
            })

    except (OSError, json.JSONDecodeError) as e:
        issues.append({"type": "error", "msg": f"审计日志读取失败: {e}"})

    return issues


def check_skill_compliance(limit: int = 10) -> list:
    """随机抽样检查 skill 目录结构。"""
    issues = []
    try:
        all_skills = []
        for root, dirs, files in os.walk(SKILLS_DIR):
            if "SKILL.md" in files:
                all_skills.append(root)
                dirs.clear()  # 不递归进入子目录

        sample = random.sample(all_skills, min(limit, len(all_skills)))
        issues.append({
            "type": "info",
            "msg": f"Skill 总数: {len(all_skills)}, 抽查 {len(sample)} 个",
        })

        for skill_dir in sample:
            rel = skill_dir[len(HERMES_HOME):]
            has_ref = os.path.isdir(os.path.join(skill_dir, "references"))
            has_scripts = os.path.isdir(os.path.join(skill_dir, "scripts"))

            flags = []
            if has_ref:
                flags.append("references/")
            if has_scripts:
                flags.append("scripts/")

            status = "✅" if flags else "⚠️ （无子目录）"
            issues.append({
                "type": "info",
                "msg": f"  {status} {rel}: {', '.join(flags) if flags else '基础结构'}",
            })

    except OSError as e:
        issues.append({"type": "error", "msg": f"Skill 检查失败: {e}"})

    return issues


# ── 报告生成 ──────────────────────────────────────────────────────────

def generate_report() -> str:
    """生成 Markdown 格式的健康报告。"""
    lines = []
    lines.append(f"# 🏥 Hermes 文件系统健康报告")
    lines.append(f"")
    lines.append(f"**检查时间**: {NOW}")
    lines.append(f"**检查范围**: {HERMES_HOME}")
    lines.append(f"")
    lines.append("---")
    lines.append("")

    checks = [
        ("📁 根目录散乱文件", check_root_clutter()),
        ("🛡️ 保护路径完整性", check_protected_paths()),
        ("💾 磁盘使用率", check_disk_usage()),
        ("📋 审计日志", check_audit_log()),
        ("🏷️ 命名规范（随机抽样）", check_naming_sample(20)),
        ("📦 Skill 结构（随机抽样）", check_skill_compliance(10)),
    ]

    total_warnings = 0
    total_errors = 0

    for title, issues in checks:
        lines.append(f"## {title}")
        lines.append("")
        if not issues:
            lines.append("_无数据_")
            lines.append("")
            continue

        for issue in issues:
            t = issue["type"]
            msg = issue["msg"]
            if t == "error":
                lines.append(f"- ❌ **错误**: {msg}")
                total_errors += 1
            elif t == "warning":
                lines.append(f"- ⚠️  **警告**: {msg}")
                total_warnings += 1
            else:
                lines.append(f"- ℹ️   {msg}")

        lines.append("")

    # 总结
    lines.append("---")
    lines.append("")
    if total_errors == 0 and total_warnings == 0:
        lines.append("## 🟢 文件系统状态健康！")
    else:
        if total_errors > 0:
            lines.append(f"## 🔴 发现 {total_errors} 个错误，{total_warnings} 个警告")
        elif total_warnings > 0:
            lines.append(f"## 🟡 发现 {total_warnings} 个警告（无错误）")

    lines.append("")
    lines.append(f"_自动生成 by fs-enforce | {NOW}_")

    return "\n".join(lines)


def main():
    report = generate_report()

    if "--html" in sys.argv:
        # 简单 HTML 包装
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Hermes 文件系统健康报告</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 2em auto; padding: 0 1em; }}
h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }}
h2 {{ color: #555; margin-top: 1.5em; }}
pre {{ background: #f5f5f5; padding: 1em; border-radius: 4px; }}
.error {{ color: #d32f2f; }}
.warning {{ color: #f57c00; }}
.info {{ color: #1976d2; }}
</style></head><body>
<pre>{report}</pre>
</body></html>"""
        print(html)
    else:
        print(report)


if __name__ == "__main__":
    main()
