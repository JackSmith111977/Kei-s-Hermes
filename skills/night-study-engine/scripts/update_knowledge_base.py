#!/usr/bin/env python3
"""
夜间自习引擎 v3.0 - 知识库更新器（增强版）
在学习完成后更新 Knowledge Base 中的概念状态和复习日期。
v3.0 新增：概念关系映射、跨领域引用、置信度追踪、来源 URL 记录。

用法：
  python3 update_knowledge_base.py --domain ai_tech --concept "qwen3.6" --status mastered
  python3 update_knowledge_base.py --domain ai_tech --concept "qwen3.6" --rel "supersedes:qwen3.5:1.0"
  python3 update_knowledge_base.py --domain ai_tech --concept "new" --status developing --notes "..."
  python3 update_knowledge_base.py --domain ai_tech --list
  python3 update_knowledge_base.py --domain ai_tech --due
  python3 update_knowledge_base.py --domain ai_tech --update-review
  python3 update_knowledge_base.py --domain ai_tech --graph          # v3.0 新增：显示关系图谱
  python3 update_knowledge_base.py --cross-domain                    # v3.0 新增：显示跨域引用
  python3 update_knowledge_base.py --concept-graph                   # v3.0 新增：生成全局概念关系图

间隔复习节奏：1天 → 3天 → 7天 → 30天（v3.0 不变）
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
    if current_interval_index >= len(REVIEW_INTERVALS) - 1:
        days = REVIEW_INTERVALS[-1]
    else:
        days = REVIEW_INTERVALS[current_interval_index + 1]
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d"), days


def add_or_update_concept(kb, concept_name, status, notes="", review_interval_index=0,
                           relationships=None, cross_domain_refs=None, source_urls=None):
    """v3.0 增强：增加关系、跨域引用、来源 URL 支持"""
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
        # v3.0: 合并关系
        if relationships:
            existing_rels = {r["target"]: r for r in concept.get("relationships", [])}
            for rel in relationships:
                existing_rels[rel["target"]] = rel
            concept["relationships"] = list(existing_rels.values())
        if cross_domain_refs:
            existing_refs = {r["concept"]: r for r in concept.get("cross_domain_refs", [])}
            for ref in cross_domain_refs:
                existing_refs[ref["concept"]] = ref
            concept["cross_domain_refs"] = list(existing_refs.values())
        if source_urls:
            existing_urls = set(concept.get("source_urls", []))
            existing_urls.update(source_urls)
            concept["source_urls"] = list(existing_urls)
        # v3.0: 增加置信度
        if status == "mastered":
            concept["confidence"] = min(1.0, concept.get("confidence", 0.5) + 0.1)
        elif status == "developing":
            concept["confidence"] = max(0.3, concept.get("confidence", 0.5) - 0.1)
    else:
        new_concept = {
            "status": status,
            "date_introduced": today,
            "last_reviewed": today,
            "next_review": next_review,
            "review_interval": interval_days,
            "confidence": 0.5,
            "source_urls": source_urls or [],
            "relationships": relationships or [],
            "cross_domain_refs": cross_domain_refs or [],
        }
        if notes:
            new_concept["notes"] = notes
        if status == "mastered":
            new_concept["date_mastered"] = today
        kb["concepts"][concept_name] = new_concept


def parse_relationship(rel_str):
    """解析关系字符串，格式：type:target:strength"""
    parts = rel_str.split(":")
    if len(parts) == 3:
        return {"type": parts[0], "target": parts[1], "strength": float(parts[2])}
    elif len(parts) == 2:
        return {"type": parts[0], "target": parts[1], "strength": 0.5}
    return None


def list_concepts(kb):
    """列出所有概念（含关系）"""
    concepts = kb.get("concepts", {})
    if not concepts:
        print("📭 该领域没有概念记录")
        return

    print(f"\n📚 领域: {kb.get('domain_name', kb['domain'])}")
    print(f"   最后更新: {kb.get('last_updated', '?')}")
    print(f"   概念数: {len(concepts)}")
    print()
    for name, concept in sorted(concepts.items()):
        rels = concept.get("relationships", [])
        refs = concept.get("cross_domain_refs", [])
        rel_str = ", ".join(f"{r['type']}→{r['target']}" for r in rels) if rels else "—"
        ref_str = ", ".join(f"{r['domain']}:{r['concept']}" for r in refs) if refs else "—"
        print(f"  📌 {name}")
        print(f"     状态: {concept['status']} | 置信度: {concept.get('confidence', '?')}")
        print(f"     复习: {concept.get('next_review', '?')} (每{concept.get('review_interval', '?')}天)")
        print(f"     关系: {rel_str}")
        print(f"     跨域: {ref_str}")
        if concept.get("notes"):
            print(f"     备注: {concept['notes']}")
        print()


def show_graph(kb):
    """v3.0 新增：显示领域内的概念关系图谱"""
    concepts = kb.get("concepts", {})
    if not concepts:
        print("📭 该领域没有概念")
        return

    print(f"\n🕸️  概念关系图谱: {kb.get('domain_name', kb['domain'])}\n")
    print("```")
    for name, concept in sorted(concepts.items()):
        status_mark = {"mastered": "●", "developing": "◌", "exploring": "○"}.get(concept["status"], "○")
        print(f"  {status_mark} {name} [{concept['status']}]")
        for rel in concept.get("relationships", []):
            arrow = {"supersedes": "→", "requires": "⇒", "related_to": "↔", "implements": "◀"}.get(rel["type"], "─")
            if rel["target"] in concepts:
                target_status = concepts[rel["target"]]["status"]
                print(f"      {arrow} {rel['target']} [{target_status}] (强度: {rel['strength']})")
    print("```")
    print()
    print("图例: ● 已掌握 ◌ 学习中 ○ 探索中")
    print("      → 取代  ⇒ 依赖  ↔ 相关  ◀ 实现")


def show_cross_domain():
    """v3.0 新增：显示所有跨领域引用"""
    all_refs = []
    for kb_file in sorted(KB_DIR.glob("*.json")):
        try:
            with open(kb_file) as f:
                kb = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        domain = kb.get("domain", kb_file.stem)
        for name, concept in kb.get("concepts", {}).items():
            for ref in concept.get("cross_domain_refs", []):
                all_refs.append({
                    "from_domain": domain,
                    "from_concept": name,
                    "to_domain": ref.get("domain"),
                    "to_concept": ref.get("concept"),
                })

    if not all_refs:
        print("📭 没有跨领域引用")
        return

    print(f"\n🔗 跨领域引用 ({len(all_refs)} 条):\n")
    for ref in sorted(all_refs, key=lambda r: (r["from_domain"], r["from_concept"])):
        print(f"  {ref['from_domain']}.{ref['from_concept']} → {ref['to_domain']}.{ref['to_concept']}")
    print()


def show_concept_graph():
    """v3.0 新增：生成全局概念关系图"""
    all_concepts = {}
    for kb_file in sorted(KB_DIR.glob("*.json")):
        try:
            with open(kb_file) as f:
                kb = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue
        domain = kb.get("domain", kb_file.stem)
        for name in kb.get("concepts", {}):
            key = f"{domain}.{name}"
            all_concepts[key] = {"domain": domain, "name": name}

    print(f"\n🌐 全局概念关系图 ({len(all_concepts)} 个概念)\n")
    print("所有概念列表（按领域分组）：\n")
    current_domain = None
    for key in sorted(all_concepts.keys()):
        c = all_concepts[key]
        if c["domain"] != current_domain:
            print(f"\n  📁 {c['domain']}:")
            current_domain = c["domain"]
        print(f"    📌 {c['name']}")
    print("\n💡 使用 --domain <id> --graph 查看单个领域的关系图")
    print("💡 使用 --cross-domain 查看所有跨域引用")


def update_reviews(kb):
    """更新所有到期概念的复习日期"""
    today = datetime.now().strftime("%Y-%m-%d")
    updated = 0
    for name, concept in kb.get("concepts", {}).items():
        next_review = concept.get("next_review")
        if next_review and next_review <= today:
            current_interval = REVIEW_INTERVALS.index(concept.get("review_interval", 1)) if concept.get("review_interval") in REVIEW_INTERVALS else 0
            next_review, interval_days = get_next_review_date(current_interval)
            concept["next_review"] = next_review
            concept["review_interval"] = interval_days
            concept["last_reviewed"] = today
            updated += 1
    return updated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="知识库更新器 v3.0")
    parser.add_argument("--domain", help="领域 ID")
    parser.add_argument("--concept", help="概念名称")
    parser.add_argument("--status", choices=["mastered", "developing", "exploring", "stale"], help="状态")
    parser.add_argument("--notes", help="备注")
    parser.add_argument("--rel", action="append", help="关系 (type:target:strength)")
    parser.add_argument("--cross-ref", action="append", help="跨域引用 (domain:concept)")
    parser.add_argument("--source-url", action="append", help="来源 URL")
    parser.add_argument("--list", action="store_true", help="列出所有概念")
    parser.add_argument("--due", action="store_true", help="列出到期复习概念")
    parser.add_argument("--update-review", action="store_true", help="更新所有到期概念的复习日期")
    parser.add_argument("--graph", action="store_true", help="显示概念关系图谱 v3.0")
    parser.add_argument("--cross-domain", action="store_true", help="显示跨域引用 v3.0")
    parser.add_argument("--concept-graph", action="store_true", help="显示全局概念图 v3.0")

    args = parser.parse_args()

    if args.concept_graph:
        show_concept_graph()
        sys.exit(0)

    if args.cross_domain:
        show_cross_domain()
        sys.exit(0)

    if not args.domain:
        # 如果没有指定领域，显示所有领域概览
        for kb_file in sorted(KB_DIR.glob("*.json")):
            try:
                with open(kb_file) as f:
                    kb = json.load(f)
                domain = kb.get("domain", kb_file.stem)
                concepts = kb.get("concepts", {})
                due_count = sum(
                    1 for c in concepts.values()
                    if c.get("next_review") and c["next_review"] <= datetime.now().strftime("%Y-%m-%d")
                )
                print(f"📁 {domain}: {len(concepts)} 概念, {due_count} 到期复习")
            except (json.JSONDecodeError, IOError):
                pass
        sys.exit(0)

    kb = load_kb(args.domain)

    if args.list:
        list_concepts(kb)
    elif args.due:
        due = []
        today = datetime.now().strftime("%Y-%m-%d")
        for name, concept in kb.get("concepts", {}).items():
            if concept.get("next_review") and concept["next_review"] <= today:
                due.append((name, concept))
        if due:
            print(f"\n📋 '{args.domain}' 到期复习概念 ({len(due)} 个):\n")
            for name, concept in due:
                print(f"  📌 {name} [{concept['status']}] — 下次: {concept['next_review']}")
            print()
        else:
            print(f"✅ '{args.domain}' 没有到期复习的概念")
    elif args.update_review:
        count = update_reviews(kb)
        save_kb(args.domain, kb)
        print(f"✅ 已更新 {count} 个概念的复习日期")
    elif args.graph:
        show_graph(kb)
    elif args.concept and args.status:
        relationships = []
        if args.rel:
            for rel_str in args.rel:
                rel = parse_relationship(rel_str)
                if rel:
                    relationships.append(rel)
        cross_domain_refs = []
        if args.cross_ref:
            for ref_str in args.cross_ref:
                parts = ref_str.split(":")
                if len(parts) >= 2:
                    cross_domain_refs.append({"domain": parts[0], "concept": parts[1]})
        add_or_update_concept(kb, args.concept, args.status, args.notes or "",
                               relationships=relationships,
                               cross_domain_refs=cross_domain_refs,
                               source_urls=args.source_url)
        save_kb(args.domain, kb)
        status_emoji = {"mastered": "✅", "developing": "🔄", "exploring": "🔍", "stale": "⚠️"}.get(args.status, "📝")
        rel_count = len(relationships)
        ref_count = len(cross_domain_refs)
        print(f"{status_emoji} 概念 '{args.concept}' 已更新为 '{args.status}'")
        if rel_count:
            print(f"  关系: {rel_count} 条")
        if ref_count:
            print(f"  跨域: {ref_count} 条")
    else:
        parser.print_help()
