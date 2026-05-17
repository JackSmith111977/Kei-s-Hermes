#!/usr/bin/env python3
"""
skill-health-check.py — Skill 质量健康检查（集成到每日报告）

直接读取 SQS 评分数据，不依赖 --json 参数。
用法:
  python3 skill-health-check.py
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"
NOW = datetime.now(timezone.utc)

# 手动读取所有 SKILL.md 并快速计算基本统计
def collect_stats():
    total = 0
    has_frontmatter = 0
    has_depends = 0
    has_triggers_gt_3 = 0
    has_version = 0
    has_referenced_by = 0
    
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            total += 1
            sk_path = Path(root) / "SKILL.md"
            content = sk_path.read_text(encoding="utf-8")
            
            fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if fm_match:
                has_frontmatter += 1
                fm_text = fm_match.group(1)
                
                if re.search(r'^depends_on\s*:', fm_text, re.MULTILINE):
                    has_depends += 1
                if re.search(r'^referenced_by\s*:', fm_text, re.MULTILINE):
                    has_referenced_by += 1
                if re.search(r'^version\s*:', fm_text, re.MULTILINE):
                    has_version += 1
                    
                # Check triggers count
                triggers_match = re.search(r'^triggers\s*:\s*\[(.*?)\]', fm_text, re.DOTALL)
                if triggers_match:
                    items = [t.strip().strip("'\"") for t in triggers_match.group(1).split(",") if t.strip()]
                    if len(items) >= 3:
                        has_triggers_gt_3 += 1
    
    # Last modified check
    stale_count = 0
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            sk_path = Path(root) / "SKILL.md"
            mtime = datetime.fromtimestamp(sk_path.stat().st_mtime, tz=timezone.utc)
            days = (NOW - mtime).days
            if days > 180:
                stale_count += 1
    
    return {
        "total": total,
        "has_frontmatter": has_frontmatter,
        "has_depends": has_depends,
        "has_referenced_by": has_referenced_by,
        "has_triggers_gt_3": has_triggers_gt_3,
        "has_version": has_version,
        "stale_180d": stale_count,
    }


def main():
    stats = collect_stats()
    
    lines = []
    lines.append(f"## 📦 Skill 质量健康检查")
    lines.append(f"")
    lines.append(f"- **总 Skill 数**: {stats['total']}")
    lines.append(f"- ✅ 有 YAML frontmatter: {stats['has_frontmatter']}/{stats['total']}")
    lines.append(f"- ✅ 有版本号: {stats['has_version']}/{stats['total']}")
    lines.append(f"- ✅ 有 depends_on: {stats['has_depends']}/{stats['total']}")
    lines.append(f"- ✅ 有 referenced_by: {stats['has_referenced_by']}/{stats['total']}")
    lines.append(f"- ✅ triggers ≥ 3: {stats['has_triggers_gt_3']}/{stats['total']}")
    lines.append(f"- 🔴 超过 180 天未更新: {stats['stale_180d']}/{stats['total']}")
    lines.append(f"")
    
    # 健康评级
    health_pct = (
        (stats['has_frontmatter'] / max(stats['total'], 1)) * 0.25 +
        (stats['has_depends'] / max(stats['total'], 1)) * 0.20 +
        (stats['has_triggers_gt_3'] / max(stats['total'], 1)) * 0.20 +
        (stats['has_version'] / max(stats['total'], 1)) * 0.20 +
        (1 - stats['stale_180d'] / max(stats['total'], 1)) * 0.15
    ) * 100
    
    if health_pct >= 80:
        lines.append(f"🟢 **Skill 生态健康度: {health_pct:.0f}%** — 良好")
    elif health_pct >= 60:
        lines.append(f"🟡 **Skill 生态健康度: {health_pct:.0f}%** — 待改进")
    else:
        lines.append(f"🔴 **Skill 生态健康度: {health_pct:.0f}%** — 需关注")
    
    lines.append(f"")
    lines.append(f"_自动生成 | {NOW.strftime('%Y-%m-%d %H:%M')} UTC_")
    
    print("\n".join(lines))


if __name__ == "__main__":
    main()
