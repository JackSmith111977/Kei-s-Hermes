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


def check_timestamp_format(lu_str, domain_id):
    """Check last_updated timestamp for format issues. Return list of warnings."""
    issues = []
    if not lu_str:
        return issues
    if lu_str.count('+') > 1 or lu_str.count('-') > 3:
        issues.append(f"timestamp format issue: '{lu_str}' (possible double timezone)")
    try:
        clean = lu_str.replace('+08:00', '').replace('Z', '')
        datetime.fromisoformat(clean)
    except Exception:
        issues.append(f"timestamp unparseable: '{lu_str}'")
    return issues


def compute_kb_stats(session_log):
    """Return (total_sessions, avg_quality) from KB session_log."""
    scores = []
    for s in session_log:
        q = s.get("quality_score", 0)
        if isinstance(q, (int, float)):
            if isinstance(q, float) and 0 < q < 1:
                q = q * 100
            scores.append(float(q))
    n = len(session_log)
    avg_q = round(sum(scores) / len(scores) / 100, 2) if scores else 0.5
    return n, avg_q


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
        ts_issues = check_timestamp_format(kb.get("last_updated", ""), uid)
        drift_msgs = check_drift(d, kb)
        cfg_ts_issues = check_timestamp_format(d.get("last_updated", ""), uid + "_config")

        if not fmt_issues and not ts_issues and not drift_msgs and not cfg_ts_issues:
            print(f"OK {uid}: clean")
            continue

        any_issue = True
        print(f"\nWARN {uid}:")

        if cfg_ts_issues:
            for m in cfg_ts_issues:
                print(f"  config timestamp: {m}")
            if fix_sync:
                d["last_updated"] = now_iso
                print(f"  Fixed config timestamp: set to {now_iso[:19]}")

        if fmt_issues:
            print(f"  quality_score format: {len(fmt_issues)} sessions with 0-1 float")
            for idx, val in fmt_issues[:3]:
                print(f"    session {idx}: {val}")
            if len(fmt_issues) > 3:
                print(f"    ... and {len(fmt_issues) - 3} more")

        if ts_issues:
            for m in ts_issues:
                print(f"  timestamp: {m}")

        if drift_msgs:
            for m in drift_msgs:
                print(f"  config-KB drift: {m}")

        if fix_format and fmt_issues:
            n = fix_quality_format(sl)
            print(f"  Fixed {n} quality_score entries")
            json.dump(kb, open(kb_path, "w"), ensure_ascii=False, indent=2)

        if fix_sync and (drift_msgs or fmt_issues or ts_issues or cfg_ts_issues):
            kb_sessions, kb_avg_q = compute_kb_stats(sl)
            d["learning_history"]["total_sessions"] = kb_sessions
            d["learning_history"]["avg_quality"] = kb_avg_q
            d["learning_history"]["consecutive_failures"] = 0
            d["learning_history"]["last_loop_count"] = 1
            d["last_updated"] = now_iso
            print(f"  Synced learning_history: sessions={kb_sessions}, avg_q={kb_avg_q}")

        if ts_issues:
            kb["last_updated"] = now_iso
            print(f"  Fixed KB timestamp: set to {now_iso[:19]}")

        if fix_sync:
            json.dump(config, open(CONFIG_PATH, "w"), ensure_ascii=False, indent=2)

    if any_issue and not fix_format and not fix_sync:
        print("\nRun with --fix-format or --fix-all to auto-repair")
        sys.exit(1)
    elif any_issue and (fix_format or fix_sync):
        print("\nIssues fixed")
    else:
        print("All domains clean")


if __name__ == "__main__":
    main()
