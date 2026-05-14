#!/usr/bin/env python3
"""
sqs-sync.py v1.0 — SQS 评分同步器

将 SQS 数据库中的 skill 质量分同步到 SRA 可读取的 JSON 文件。
由 cron 每 6 小时自动调用。

用法:
  python3 sqs-sync.py                        # 同步到默认路径
  python3 sqs-sync.py --output /path/to.json  # 指定输出路径
  python3 sqs-sync.py --dry-run              # 只预览不同步
  python3 sqs-sync.py --no-quality           # 禁用质量加权（写入空文件）
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".hermes" / "data" / "skill-quality.db"
DEFAULT_OUTPUT = Path.home() / ".sra" / "data" / "sqs-scores.json"


def quality_modifier(sqs: float) -> float:
    """
    SQS → 质量权重映射函数。

    SQS ≥ 80:  权重 1.0 （不降权）
    SQS ≥ 60:  权重 0.9 （轻度降权）
    SQS ≥ 40:  权重 0.7 （中度降权）
    SQS < 40:  权重 0.4 （严重降权）
    无评分:    权重 0.5 （中性降权，默认值）
    """
    if sqs >= 80:
        return 1.0
    elif sqs >= 60:
        return 0.9
    elif sqs >= 40:
        return 0.7
    else:
        return 0.4


def sync_to_sra(output_path=None, dry_run=False, no_quality=False):
    """同步 SQS 评分到 SRA 可读 JSON"""
    out = Path(output_path) if output_path else DEFAULT_OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)

    if no_quality:
        data = {"enabled": False, "source": "sqs-sync.py", "synced_at": datetime.now().isoformat()[:19], "scores": {}}
        if not dry_run:
            out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            print(f"✅ 已写入空 SQS 配置 (quality disabled): {out}")
        return data

    # 读取 SQS 数据库
    if not DB_PATH.exists():
        print(f"⚠️  SQS 数据库不存在: {DB_PATH}")
        data = {"enabled": True, "source": "sqs-sync.py", "synced_at": datetime.now().isoformat()[:19], "scores": {}}
        if not dry_run:
            out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        return data

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.execute("SELECT skill_name, sqs_total, scored_at FROM scores ORDER BY skill_name")
    rows = cur.fetchall()
    conn.close()

    scores = {}
    for row in rows:
        skill_name = row[0]
        sqs = row[1]
        modifier = quality_modifier(sqs)
        scores[skill_name] = {
            "sqs_score": round(sqs, 1),
            "quality_modifier": modifier,
            "scored_at": row[2],
        }

    data = {
        "enabled": True,
        "source": "sqs-sync.py",
        "synced_at": datetime.now().isoformat()[:19],
        "total_skills": len(scores),
        "avg_sqs": round(sum(s["sqs_score"] for s in scores.values()) / len(scores), 1) if scores else 0,
        "scores": scores,
    }

    if dry_run:
        print(f"\n📊 SQS 同步预览 ({len(scores)} skills)")
        print(f"   平均 SQS: {data['avg_sqs']}")
        print(f"   输出路径: {out}")
        print(f"\n   质量修饰分布:")
        modifiers = {}
        for s in scores.values():
            m = s["quality_modifier"]
            modifiers[m] = modifiers.get(m, 0) + 1
        for m in sorted(modifiers.keys(), reverse=True):
            cnt = modifiers[m]
            bar = "█" * (cnt // 3)
            print(f"     ×{m:.1f}: {cnt:4d} {bar}")
        print()
    else:
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"✅ 已同步 {len(scores)} 个 SQS 评分到 {out}")
        print(f"   平均 SQS: {data['avg_sqs']}")

    return data


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    output_path = None
    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]

    dry_run = "--dry-run" in sys.argv
    no_quality = "--no-quality" in sys.argv

    sync_to_sra(output_path, dry_run, no_quality)


if __name__ == "__main__":
    main()
