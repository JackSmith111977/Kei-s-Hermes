#!/usr/bin/env python3
"""
KB Field Type & Quality Score Fixer — 修复 Knowledge Base JSON 的数据完整性。

发现的问题类型:
  A. session_log 中 concepts_updated/new_concepts_added 存储为 int(0) 而非 list([])
     → 导致 TypeError: object of type 'int' has no len()
     → 影响: avg_quality 计算崩溃、状态报告生成失败

  B. session_log 中 quality_score 混合 0-1 浮点和 0-100 整数格式
     → 导致 avg_quality 偏差可达 60+ 分
     → 影响: 自适应调度排序错误、可能误触发 consecutive_failure_penalty

  C. Config/KB 配置漂移 — learning_history 未从 session_log 同步
     → 调度器使用过期数据推荐领域
     → 影响: 推荐最近刚学过的领域而非真正需要的领域

  D. last_updated timestamp 重复时区 (+08:00+08:00)
     → 非标准 ISO 8601，可能影响外部工具解析

用法:
  python3 kb-field-type-fixer.py                    # 只检测，不修改
  python3 kb-field-type-fixer.py --fix              # 修复所有问题
  python3 kb-field-type-fixer.py --fix --domain ai_tech  # 只修复指定领域
  python3 kb-field-type-fixer.py --fix --sync-config     # 修复+同步配置

建议: 每月运行一次全量修复，或在每一个 cron 学习轮次前运行 `--fix`
      以确保数据一致性。
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ==== Config ====
KB_DIR = Path.home() / ".hermes" / "night_study" / "knowledge_base"
CONFIG_PATH = Path.home() / ".hermes" / "config" / "night_study_config_v2.json"
TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ)

# ==== Stats ====
stats = {
    "files_checked": 0,
    "field_type_fixes": {"concepts_updated": 0, "new_concepts_added": 0},
    "quality_score_fixes": 0,
    "timestamp_fixes": 0,
    "config_syncs": 0,
    "total_fixes": 0,
}


def add_fix(repair_type: str):
    stats["total_fixes"] += 1


def needs_repair(value):
    """Check if a session_log field value has the wrong type."""
    return not isinstance(value, list) and value is not None


def safe_field(val):
    """Normalize field value to empty list if it's the wrong type."""
    if isinstance(val, list):
        return val
    if val is None:
        return []
    # e.g., int 0 → [], str "foo" → [str(val)]
    if val == 0 or val == "" or val is None:
        return []
    return [str(val)]


def check_and_fix_session_log(kb: dict, domain_id: str, do_fix: bool) -> int:
    """Check/fix session_log field type issues. Returns fix count."""
    fixes = 0
    sl = kb.get("session_log", [])
    for i, s in enumerate(sl):
        for field in ("new_concepts_added", "concepts_updated"):
            val = s.get(field)
            if needs_repair(val):
                if do_fix:
                    s[field] = safe_field(val)
                    stats["field_type_fixes"][field] += 1
                    add_fix(f"session_log[{i}].{field} type fix")
                fixes += 1
                print(f"  {'FIX' if do_fix else 'DETECT'}: {domain_id}: "
                      f"session_log[{i}].{field} = {val!r} (type={type(val).__name__}) "
                      f"{'→ []' if do_fix else ''}")
    return fixes


def check_and_fix_quality_scores(kb: dict, domain_id: str, do_fix: bool) -> int:
    """Normalize quality_score to 0-100 int format. Returns fix count."""
    fixes = 0
    sl = kb.get("session_log", [])
    for i, s in enumerate(sl):
        q = s.get("quality_score", 0)
        if q is None:
            continue
        # Detect 0-1 float format
        if isinstance(q, float) and q < 1:
            new_q = int(round(q * 100))
            if do_fix:
                s["quality_score"] = new_q
                stats["quality_score_fixes"] += 1
                add_fix(f"session_log[{i}].quality_score norm: {q} → {new_q}")
            fixes += 1
            print(f"  {'FIX' if do_fix else 'DETECT'}: {domain_id}: "
                  f"session_log[{i}].quality_score = {q!r} → {new_q if do_fix else ''} "
                  f"(归一化)")
        # Also fix 0 < q < 1 as int (e.g., 0→if it's 0 we leave it)
        elif isinstance(q, float) and q == int(q) and q > 0:
            new_q = int(q)
            if do_fix:
                s["quality_score"] = new_q
                stats["quality_score_fixes"] += 1
                add_fix(f"session_log[{i}].quality_score type: {q} → {new_q}")
            fixes += 1
    return fixes


def check_and_fix_timestamps(kb: dict, domain_id: str, do_fix: bool) -> int:
    """Fix duplicate timezone in last_updated (+08:00+08:00)."""
    fixes = 0
    lu = kb.get("last_updated", "")
    if isinstance(lu, str) and lu.count("+") > 1:
        # Find and fix double timezone
        fixed_lu = re.sub(r'(\+[\d:]{5})\+[\d:]{5}$', r'\1', lu)
        if do_fix:
            kb["last_updated"] = fixed_lu
            stats["timestamp_fixes"] += 1
            add_fix(f"last_updated timestamp: {lu} → {fixed_lu}")
        fixes += 1
        print(f"  {'FIX' if do_fix else 'DETECT'}: {domain_id}: "
              f"last_updated duplicate tz: {lu} → {fixed_lu if do_fix else ''}")
    return fixes


def recalc_learning_history(kb: dict):
    """Recalculate learning_history from session_log (no side effects)."""
    sl = kb.get("session_log", [])
    scores = []
    for s in sl:
        q = s.get("quality_score", 0)
        if q and isinstance(q, (int, float)):
            if q < 1:
                q = q * 100
            if 1 <= q <= 100:
                scores.append(int(round(q)))
    hist = kb.setdefault("learning_history", {})
    hist["total_sessions"] = len(scores)
    hist["avg_quality"] = round(sum(scores) / len(scores), 2) if scores else 0.5
    hist["last_loop_count"] = 1
    hist["consecutive_failures"] = 0
    return scores


def sync_config(kb, domain_id: str):
    """Sync learning_history to config file."""
    if not CONFIG_PATH.exists():
        print(f"  SKIP: config not found at {CONFIG_PATH}")
        return False

    hist = kb.get("learning_history", {})
    avg_raw = hist.get("avg_quality", 50)  # 0-100 format in KB
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    synced = False
    for d in config.get("domains", []):
        if d["id"] == domain_id:
            d["learning_history"]["total_sessions"] = hist.get("total_sessions", 0)
            d["learning_history"]["avg_quality"] = round(avg_raw / 100, 4)  # config uses 0-1
            d["learning_history"]["last_loop_count"] = 1
            d["learning_history"]["consecutive_failures"] = 0
            d["freshness_score"] = max(0.1, min(0.8, avg_raw / 100 * 0.6))
            d["last_updated"] = kb.get("last_updated", "")
            synced = True
            break

    if synced:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        stats["config_syncs"] += 1
        add_fix(f"config sync: {domain_id} (avg={avg_raw}/100)")
        print(f"  SYNC: config night_study_config_v2.json → {domain_id} "
              f"(sessions={hist['total_sessions']}, avg={avg_raw}/100)")
    else:
        print(f"  SKIP: domain {domain_id} not found in config")
    return synced


def main():
    do_fix = "--fix" in sys.argv
    do_sync = "--sync-config" in sys.argv or do_fix
    target_domain = None

    # Check for --domain flag
    for i, arg in enumerate(sys.argv):
        if arg == "--domain" and i + 1 < len(sys.argv):
            target_domain = sys.argv[i + 1]

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    mode_label = "FIX" if do_fix else "DRY-RUN (no changes)"
    print(f"🔍 KB Field Type Fixer — {mode_label}")
    print(f"   KB directory: {KB_DIR}")
    print(f"   Target domain: {target_domain or 'ALL'}")
    print()

    kb_files = sorted(KB_DIR.glob("*.json"))
    if not kb_files:
        print("❌ No KB files found")
        return

    for kb_path in kb_files:
        domain_id = kb_path.stem
        if target_domain and domain_id != target_domain:
            continue

        stats["files_checked"] += 1
        print(f"── {domain_id} ──")

        with open(kb_path) as f:
            kb = json.load(f)

        concepts = kb.get("concepts", {})
        print(f"   Concepts: {len(concepts)}")

        # 1. Fix session_log field types
        f1 = check_and_fix_session_log(kb, domain_id, do_fix)

        # 2. Fix quality_score formats
        f2 = check_and_fix_quality_scores(kb, domain_id, do_fix)

        # 3. Fix timestamps
        f3 = check_and_fix_timestamps(kb, domain_id, do_fix)

        total_file_fixes = f1 + f2 + f3

        # 4. Recalc learning_history if any fixes applied
        if total_file_fixes > 0:
            scores = recalc_learning_history(kb)
            print(f"   Recalc learning_history: {len(scores)} sessions, "
                  f"avg={kb['learning_history']['avg_quality']}/100")

        if total_file_fixes > 0:
            if do_fix:
                with open(kb_path, "w") as f:
                    json.dump(kb, f, indent=2, ensure_ascii=False)
                print(f"   ✅ Written: {kb_path.name} ({total_file_fixes} fixes)")
            else:
                print(f"   ⚠️  Would fix: {total_file_fixes} issues (re-run with --fix)")

            # 5. Sync config if requested
            if do_sync and do_fix and total_file_fixes > 0:
                sync_config(kb, domain_id)
        else:
            print(f"   ✅ Clean — no issues found")

    # ==== Report ====
    print()
    print("=" * 55)
    print("📊 修复报告")
    print(f"   检查文件:  {stats['files_checked']}")
    print(f"   字段类型修复 (concepts_updated): {stats['field_type_fixes']['concepts_updated']}")
    print(f"   字段类型修复 (new_concepts_added): {stats['field_type_fixes']['new_concepts_added']}")
    print(f"   质量分归一化:  {stats['quality_score_fixes']}")
    print(f"   Timestamp 修复: {stats['timestamp_fixes']}")
    print(f"   Config 同步: {stats['config_syncs']}")
    print(f"   {'✅ ' if do_fix else '⚠️ DRY-RUN — '}总计修复: {stats['total_fixes']}")
    print()
    if not do_fix:
        print("💡 重新运行 `kb-field-type-fixer.py --fix` 以应用修复。")


if __name__ == "__main__":
    main()
