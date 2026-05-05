#!/usr/bin/env python3
"""
夜间自习引擎 v2.0 - 知识库更新器
在学习完成后更新 Knowledge Base 中的概念状态和复习日期。

用法：
  python3 update_knowledge_base.py --domain ai_tech --concept "qwen3.6" --status mastered
  python3 update_knowledge_base.py --domain ai_tech --concept "new_concept" --status developing --notes "描述"
  python3 update_knowledge_base.py --domain ai_tech --list              # 列出所有概念
  python3 update_knowledge_base.py --domain ai_tech --due               # 列出到期复习概念
  python3 update_knowledge_base.py --domain ai_tech --update-review     # 更新所有到期概念的复习日期

间隔复习节奏：1天 → 3天 → 7天 → 30天
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

KB_DIR = Path.home() / ".hermes" / "night_study" / "knowledge_base"

# 间隔复习节奏（天数）
REVIEW_INTERVALS = [1, 3, 7, 30]


def load_kb(domain_id):
    kb_path = KB_DIR / f"{domain_id}.json"
    if not kb_path.exists():
        # 创建新的知识库
        kb = {
            "domain": domain_id,
            "domain_name": domain_id,
            "last_updated": datetime.now().isoformat(),
            "concepts": {},
            "open_questions": [],
            "session_log": [],
        }
        save_kb(domain_id, kb)
        return kb
    with open(kb_path) as f:
        return json.load(f)


def save_kb(domain_id, kb):
    kb_path = KB_DIR / f"{domain_id}.json"
    kb["last_updated"] = datetime.now().isoformat()
    with open(kb_path, "w") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)


def get_next_review_date(current_interval_index):
    """根据当前复习间隔索引获取下次复习日期"""
    if current_interval_index >= len(REVIEW_INTERVALS) - 1:
        days = REVIEW_INTERVALS[-1]  # 保持最长间隔
    else:
        days = REVIEW_INTERVALS[current_interval_index + 1]
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d"), days


def add_or_update_concept(kb, concept_name, status, notes="", review_interval_index=0):
    """添加或更新概念"""
    today = datetime.now().strftime("%Y-%m-%d")
    next_review, interval_days = get_next_review_date(review_interval_index)

    if concept_name in kb["concepts"]:
        concept = kb["concepts"][concept_name]
        concept["status"] = status
        concept["last_reviewed"] = today
        concept["next_review"] = next_review
        concept["review_interval"] = interval_days
        if notes:
            concept["notes"] = notes
        if status == "mastered" and not concept.get("date_mastered"):
            concept["date_mastered"] = today
    else:
        kb["concepts"][concept_name] = {
            "status": status,
            "date_introduced": today,
            "date_mastered": today if status == "mastered" else None,
            "last_reviewed": today,
            "next_review": next_review,
            "review_interval": interval_days,
            "notes": notes,
        }


def list_concepts(kb, due_only=False):
    """列出概念"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n=== {kb.get('domain_name', kb['domain'])} 知识库 ===")
    print(f"{'概念':<30} {'状态':<12} {'上次复习':<12} {'下次复习':<12} {'间隔':<6}")
    print("-" * 75)

    for name, concept in kb.get("concepts", {}).items():
        next_review = concept.get("next_review", "")
        if due_only and next_review > today:
            continue
        print(f"{name:<30} {concept.get('status', ''):<12} "
              f"{concept.get('last_reviewed', ''):<12} "
              f"{next_review:<12} "
              f"{concept.get('review_interval', ''):<6}")

    if due_only:
        due_count = sum(1 for c in kb.get("concepts", {}).values()
                        if c.get("next_review", "9999") <= today)
        print(f"\n共 {due_count} 个概念到期需要复习")


def update_due_reviews(kb):
    """更新所有到期概念的复习日期"""
    today = datetime.now().strftime("%Y-%m-%d")
    updated = 0
    for name, concept in kb.get("concepts", {}).items():
        next_review = concept.get("next_review", "")
        if next_review <= today:
            current_interval = concept.get("review_interval", 1)
            # 找到当前间隔在 REVIEW_INTERVALS 中的索引
            try:
                idx = REVIEW_INTERVALS.index(current_interval)
            except ValueError:
                idx = 0
            new_review, new_interval = get_next_review_date(idx)
            concept["last_reviewed"] = today
            concept["next_review"] = new_review
            concept["review_interval"] = new_interval
            updated += 1
    return updated


def log_session(kb, session_id, coverage, quality_score):
    """记录学习会话"""
    session = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "session_id": session_id,
        "coverage": coverage,
        "quality_score": quality_score,
    }
    kb.setdefault("session_log", []).append(session)


def main():
    parser = argparse.ArgumentParser(description="夜间自习知识库更新器")
    parser.add_argument("--domain", required=True, help="领域 ID（如 ai_tech）")
    parser.add_argument("--concept", help="概念名称")
    parser.add_argument("--status", choices=["not_started", "developing", "mastered", "consolidated"],
                        help="概念状态")
    parser.add_argument("--notes", default="", help="概念备注")
    parser.add_argument("--list", action="store_true", dest="list_concepts", help="列出所有概念")
    parser.add_argument("--due", action="store_true", help="只列出到期复习的概念")
    parser.add_argument("--update-review", action="store_true", dest="update_review",
                        help="更新所有到期概念的复习日期")
    parser.add_argument("--session-id", help="学习会话 ID")
    parser.add_argument("--coverage", help="学习覆盖描述")
    parser.add_argument("--quality", type=float, help="质量评分 (0-1)")

    args = parser.parse_args()
    kb = load_kb(args.domain)

    if args.list_concepts or args.due:
        list_concepts(kb, due_only=args.due)
        return

    if args.update_review:
        updated = update_due_reviews(kb)
        save_kb(args.domain, kb)
        print(f"✅ 已更新 {updated} 个到期概念的复习日期")
        list_concepts(kb, due_only=True)
        return

    if args.concept and args.status:
        add_or_update_concept(kb, args.concept, args.status, args.notes)
        save_kb(args.domain, kb)
        print(f"✅ 概念 '{args.concept}' 已更新为 '{args.status}'")
        return

    if args.session_id and args.coverage:
        log_session(kb, args.session_id, args.coverage, args.quality or 0.0)
        save_kb(args.domain, kb)
        print(f"✅ 会话 '{args.session_id}' 已记录")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
