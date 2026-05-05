#!/usr/bin/env python3
"""
夜间自习引擎 v2.0 - 领域选择器
按优先级 × (1 - freshness_score) 排序，智能选择最需要的领域。
支持跳过已学习领域和检查复习到期。

用法：
  python3 select_domain.py                          # 选择最需要的领域
  python3 select_domain.py --skip ai_tech            # 跳过指定领域
  python3 select_domain.py --review                  # 选择间隔复习到期的概念
  python3 select_domain.py --list                    # 列出所有领域状态
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_PATH = Path.home() / ".hermes" / "config" / "night_study_config_v2.json"
KB_DIR = Path.home() / ".hermes" / "night_study" / "knowledge_base"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_knowledge_base(domain_id):
    kb_path = KB_DIR / f"{domain_id}.json"
    if kb_path.exists():
        with open(kb_path) as f:
            return json.load(f)
    return None


def calculate_urgency(domain):
    """计算领域紧急度 = priority × (1 - freshness_score)"""
    priority = domain.get("priority", 0.5)
    freshness = domain.get("freshness_score", 0.5)
    return round(priority * (1 - freshness), 3)


def check_review_due(kb):
    """检查是否有间隔复习到期的概念"""
    if not kb:
        return []
    today = datetime.now().strftime("%Y-%m-%d")
    due_concepts = []
    for name, concept in kb.get("concepts", {}).items():
        next_review = concept.get("next_review")
        if next_review and next_review <= today:
            due_concepts.append({
                "name": name,
                "status": concept.get("status"),
                "next_review": next_review,
                "review_interval": concept.get("review_interval"),
            })
    return due_concepts


def select_domain(skip_ids=None, review_mode=False):
    """选择下一个要学习的领域"""
    if skip_ids is None:
        skip_ids = set()

    config = load_config()
    domains = config.get("domains", [])

    if review_mode:
        # 复习模式：选择有到期概念的领域
        results = []
        for domain in domains:
            kb = load_knowledge_base(domain["id"])
            due = check_review_due(kb)
            if due:
                results.append({
                    "domain": domain,
                    "due_concepts": due,
                    "urgency": calculate_urgency(domain),
                })
        results.sort(key=lambda x: x["urgency"], reverse=True)
        return results

    # 正常模式：按紧急度排序
    candidates = []
    for domain in domains:
        if domain["id"] in skip_ids:
            continue
        urgency = calculate_urgency(domain)
        kb = load_knowledge_base(domain["id"])
        due_count = len(check_review_due(kb)) if kb else 0
        candidates.append({
            "domain": domain,
            "urgency": urgency,
            "due_concepts": due_count,
        })

    candidates.sort(key=lambda x: (x["urgency"], x["due_concepts"]), reverse=True)
    return candidates


def main():
    skip_ids = set()
    review_mode = False
    list_mode = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--skip" and i + 1 < len(args):
            skip_ids.add(args[i + 1])
            i += 2
        elif args[i] == "--review":
            review_mode = True
            i += 1
        elif args[i] == "--list":
            list_mode = True
            i += 1
        else:
            i += 1

    if list_mode:
        config = load_config()
        print("=== 夜间学习领域状态 ===\n")
        print(f"{'ID':<15} {'名称':<15} {'优先级':<8} {'新鲜度':<8} {'紧急度':<8} {'到期复习':<8}")
        print("-" * 70)
        for domain in config["domains"]:
            urgency = calculate_urgency(domain)
            kb = load_knowledge_base(domain["id"])
            due = check_review_due(kb) if kb else []
            print(f"{domain['id']:<15} {domain['name']:<15} {domain['priority']:<8.1f} "
                  f"{domain['freshness_score']:<8.2f} {urgency:<8.3f} {len(due):<8}")
        return

    if review_mode:
        results = select_domain(skip_ids, review_mode=True)
        if not results:
            print(json.dumps({"status": "no_review_due", "message": "没有到期的复习"}))
            return
        # 输出第一个有到期概念的领域
        r = results[0]
        output = {
            "mode": "review",
            "domain_id": r["domain"]["id"],
            "domain_name": r["domain"]["name"],
            "target_skill": r["domain"]["target_skill"],
            "due_concepts": r["due_concepts"],
            "urgency": r["urgency"],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 正常模式
    candidates = select_domain(skip_ids)
    if not candidates:
        print(json.dumps({"status": "no_domain", "message": "没有可选领域"}))
        return

    selected = candidates[0]
    output = {
        "mode": "study",
        "domain_id": selected["domain"]["id"],
        "domain_name": selected["domain"]["name"],
        "keywords": selected["domain"]["keywords"],
        "target_skill": selected["domain"]["target_skill"],
        "priority": selected["domain"]["priority"],
        "freshness_score": selected["domain"]["freshness_score"],
        "urgency": selected["urgency"],
        "due_concepts": selected["due_concepts"],
        "schedule_interval_hours": selected["domain"].get("schedule_interval_hours"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
