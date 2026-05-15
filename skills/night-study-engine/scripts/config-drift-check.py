#!/usr/bin/env python3
"""
config-drift-check.py — Config-KB Drift Detection & Quality Score Format Fix

Detects and optionally fixes two classes of data integrity issues:
  1. QUALITY_SCORE_FORMAT: session_log quality_score stored as 0-1 float vs 0-100 int
  2. CONFIG_KB_DRIFT: night_study_config_v2.json learning_history out of sync with KB session_log

Usage:
  # Check all domains (read-only)
  python3 config-drift-check.py

  # Fix quality_score format only
  python3 config-drift-check.py --fix-format

  # Full sync: fix format + sync learning_history + update freshness
  python3 config-drift-check.py --fix-all

  # Single domain
  python3 config-drift-check.py --domain ai_tech --fix-all

Exit code: 0 if clean, 1 if drift/issues found (read-only mode), 0 after --fix
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

HOME = Path.home()
CONFIG_PATH = HOME / ".hermes" / "config" / "night_study_config_v2.json"
KB_DIR = HOME / ".hermes" / "night_study" / "knowledge_base"


def load_json(path):
    try:
        return json.load(open(path))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  Cannot load {path}: {e}")
        return None


def check_quality_format(session_log):
    """Return list of (index, old_value) for sessions with 0-1 float format."""
    issues = []
    for i, s in enumerate(session_log):
        q = s.get("quality_score", 0)
        if isinstance(q, float) and 0 < q < 1:
            issues.append((i, q))
    return issues


def fix_quality_format(session_log):
    """Normalize 0-1 floats to 0-100 ints in-place. Return count fixed."""
    count = 0
    for s in session_log:
        q = s.get("quality_score", 0)
        if isinstance(q, float) and 0 < q < 1:
            s["quality_score"] = int(round(q * 100))
            count += 1
    return count


def compute_kb_stats(session_log):
    """Return (total_sessions, avg_quality_0_1) from KB session_log."""
    scores = [s.get("quality_score", 0) for s in session_log if s.get("quality_score")]
    total = len(session_log)
    if not scores:
        return total, 0.5
    normalized = [s * 100 if isinstance(s, float) and s < 1 else s for s in scores]
    avg = round(sum(normalized) / len(normalized) / 100, 2)
    return total, avg


def check_drift(domain_cfg, domain_kb):
    """Compare config learning_history with KB session_log. Return list of drift messages."""
    msgs = []
    cfg_lh = domain_cfg.get("learning_history", {})
    cfg_sessions = cfg_lh.get("total_sessions", 0)
    cfg_quality = cfg_lh.get("avg_quality", 0)

    sl = domain_kb.get("session_log", [])
    kb_sessions, kb_avg_q = compute_kb_stats(sl)

    if cfg_sessions != kb_sessions:
        msgs.append(f"total_sessions: config={cfg_sessions} vs KB={kb_sessions}")

    if kb_sessions > 0 and abs(cfg_quality - kb_avg_q) > 0.05:
        msgs.append(f"avg_quality: config={cfg_quality} vs KB={kb_avg_q}")

    return msgs


def main():
    args = set(sys.argv[1:])
    fix_format = "--fix-format" in args or "--fix-all" in args
    fix_sync = "--fix-all" in args
    target_domain = None
    for a in sys.argv[1:]:
        if a.startswith("--domain="):
            target_domain = a.split("=", 1)[1]

    config = load_json(CONFIG_PATH)
    if config is None:
        sys.exit(1)

    domains = config.get("domains", [])
    if target_domain:
        domains = [d for d in domains if d["id"] == target_domain]
        if not domains:
            print(f"Domain '{target_domain}' not found in config")
            sys.exit(1)

    any_issue = False
    now_iso = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds") + "+08:00"

    for d in domains:
        uid = d["id"]
        kb_path = KB_DIR / f"{uid}.json"
        kb = load_json(kb_path)
        if kb is None:
            continue

        sl = kb.get("session_log", [])
        fmt_issues = check_quality_format(sl)
        drift_msgs = check_drift(d, kb)

        if not fmt_issues and not drift_msgs:
            print(f"OK {uid}: clean")
            continue

        any_issue = True
        print(f"\nWARN {uid}:")

        if fmt_issues:
            print(f"  quality_score format: {len(fmt_issues)} sessions with 0-1 float")
            for idx, val in fmt_issues[:3]:
                print(f"    session {idx}: {val}")
            if len(fmt_issues) > 3:
                print(f"    ... and {len(fmt_issues) - 3} more")

        if drift_msgs:
            for m in drift_msgs:
                print(f"  config-KB drift: {m}")

        if fix_format and fmt_issues:
            n = fix_quality_format(sl)
            print(f"  Fixed {n} quality_score entries")
            json.dump(kb, open(kb_path, "w"), ensure_ascii=False, indent=2)

        if fix_sync and (drift_msgs or fmt_issues):
            kb_sessions, kb_avg_q = compute_kb_stats(sl)
            d["learning_history"]["total_sessions"] = kb_sessions
            d["learning_history"]["avg_quality"] = kb_avg_q
            d["learning_history"]["consecutive_failures"] = 0
            d["learning_history"]["last_loop_count"] = 1
            d["last_updated"] = now_iso
            print(f"  Synced learning_history: sessions={kb_sessions}, avg_q={kb_avg_q}")

        if fix_sync:
            json.dump(config, open(CONFIG_PATH, "w"), ensure_ascii=False, indent=2)

    if any_issue and not fix_format and not fix_sync:
        print("\nRun with --fix-format or --fix-all to auto-repair")
        sys.exit(1)
    elif any_issue:
        print("\nIssues fixed")
    else:
        print("All domains clean")


if __name__ == "__main__":
    main()
