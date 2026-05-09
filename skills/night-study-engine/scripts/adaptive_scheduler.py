#!/usr/bin/env python3
"""
夜间自习引擎 v3.0 - 自适应调度器
根据领域优先级、新鲜度、历史表现动态选择最需要学习的领域。
支持递进权重、失败惩罚、时段感知。

用法：
  python3 adaptive_scheduler.py                            # 选择最需要的领域
  python3 adaptive_scheduler.py --list                     # 列出所有领域排序
  python3 adaptive_scheduler.py --domain ai_tech           # 指定领域
  python3 adaptive_scheduler.py --skip ai_tech             # 跳过指定领域
  python3 adaptive_scheduler.py --review                   # 检查间隔复习
  python3 adaptive_scheduler.py --status                   # 显示调度统计
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_PATH = Path.home() / ".hermes" / "config" / "night_study_config_v3.json"
CONFIG_V2_FALLBACK = Path.home() / ".hermes" / "config" / "night_study_config_v2.json"
KB_DIR = Path.home() / ".hermes" / "night_study" / "knowledge_base"


def load_config():
    """加载配置，优先 v3，fallback 到 v2"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    elif CONFIG_V2_FALLBACK.exists():
        with open(CONFIG_V2_FALLBACK) as f:
            config = json.load(f)
            # v2→v3 迁移：添加默认的自适应调度字段
            for domain in config.get("domains", []):
                if "learning_history" not in domain:
                    domain["learning_history"] = {
                        "total_sessions": 0,
                        "avg_quality": 0.5,
                        "last_loop_count": 1,
                        "consecutive_failures": 0
                    }
            if "adaptive_scheduling" not in config:
                config["adaptive_scheduling"] = {
                    "enabled": True,
                    "max_domains_per_session": 3,
                    "history_window_days": 30,
                    "performance_weight": 0.4,
                    "freshness_weight": 0.6,
                    "consecutive_failure_penalty": 0.2
                }
            return config
    else:
        print("❌ 未找到配置文件")
        sys.exit(1)


def load_knowledge_base(domain_id):
    kb_path = KB_DIR / f"{domain_id}.json"
    if kb_path.exists():
        with open(kb_path) as f:
            return json.load(f)
    return None


def calculate_domain_score(domain, adaptive_config):
    """v3.0 自适应调度评分算法"""
    priority = domain.get("priority", 0.5)
    freshness = domain.get("freshness_score", 0.5)
    history = domain.get("learning_history", {})

    fw = adaptive_config.get("freshness_weight", 0.6)
    pw = adaptive_config.get("performance_weight", 0.4)
    fail_penalty = adaptive_config.get("consecutive_failure_penalty", 0.2)

    avg_quality = history.get("avg_quality", 0.5)
    consecutive_failures = history.get("consecutive_failures", 0)

    # 基础分：高优先级 + 低新鲜度 → 该学了
    base_score = priority * fw * (1 - freshness)

    # 质量惩罚：质量差的需要更频繁学
    quality_boost = (1 - pw) * (1 - avg_quality)

    # 连续失败惩罚：避免在困难领域浪费太多轮次
    failure_penalty = consecutive_failures * fail_penalty

    score = base_score + quality_boost - failure_penalty
    return round(max(0, min(1, score)), 3)


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
                "relationships": concept.get("relationships", []),
            })
    return due_concepts


def select_domain(skip_ids=None, review_mode=False, domain_id=None):
    """选择下一个要学习的领域"""
    if skip_ids is None:
        skip_ids = set()

    config = load_config()
    domains = config.get("domains", [])
    adaptive_config = config.get("adaptive_scheduling", {})

    if domain_id:
        # 指定领域
        for domain in domains:
            if domain["id"] == domain_id:
                return domain
        print(f"❌ 未找到领域: {domain_id}")
        return None

    if review_mode:
        # 复习模式
        results = []
        for domain in domains:
            if domain["id"] in skip_ids:
                continue
            kb = load_knowledge_base(domain["id"])
            due = check_review_due(kb)
            if due:
                results.append({
                    "domain": domain,
                    "due_concepts": due,
                    "score": calculate_domain_score(domain, adaptive_config),
                })
        if not results:
            print("✅ 没有到期的复习概念")
            return None
        # 按紧急度排序
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[0]["domain"]

    # 正常学习模式
    scored = []
    for domain in domains:
        if domain["id"] in skip_ids:
            continue
        score = calculate_domain_score(domain, adaptive_config)
        scored.append((score, domain))

    if not scored:
        print("⚠️ 没有可学习的领域（全部跳过）")
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


def list_domains():
    """列出所有领域及其调度评分"""
    config = load_config()
    domains = config.get("domains", [])
    adaptive_config = config.get("adaptive_scheduling", {})

    print(f"\n{'领域名称':<20} {'优先级':<8} {'新鲜度':<8} {'质量分':<8} {'失败数':<8} {'调度分':<8}")
    print("-" * 70)
    for domain in sorted(domains, key=lambda d: calculate_domain_score(d, adaptive_config), reverse=True):
        score = calculate_domain_score(domain, adaptive_config)
        history = domain.get("learning_history", {})
        print(f"{domain['name']:<20} "
              f"{domain.get('priority', '-'):<8} "
              f"{domain.get('freshness_score', '-'):<8.1f} "
              f"{history.get('avg_quality', '-'):<8} "
              f"{history.get('consecutive_failures', 0):<8} "
              f"{score:<8.3f}")
    print()


def show_status():
    """显示调度统计"""
    config = load_config()
    domains = config.get("domains", [])
    adaptive_config = config.get("adaptive_scheduling", {})
    total_sessions = sum(d.get("learning_history", {}).get("total_sessions", 0) for d in domains)
    total_quality = sum(d.get("learning_history", {}).get("avg_quality", 0) * d.get("learning_history", {}).get("total_sessions", 0) for d in domains)
    total_sessions_weighted = sum(d.get("learning_history", {}).get("total_sessions", 0) for d in domains)

    print(f"🌙 自适应调度统计")
    print(f"{'领域数':<12}{len(domains)}")
    print(f"{'总学习次数':<12}{total_sessions}")
    print(f"{'平均质量分':<12}{round(total_quality / total_sessions_weighted, 2) if total_sessions_weighted > 0 else 'N/A'}")
    print(f"{'最大并发':<12}{adaptive_config.get('max_domains_per_session', 3)}")
    print(f"{'新鲜度权重':<12}{adaptive_config.get('freshness_weight', 0.6)}")
    print(f"{'表现权重':<12}{adaptive_config.get('performance_weight', 0.4)}")
    print(f"{'失败惩罚':<12}{adaptive_config.get('consecutive_failure_penalty', 0.2)}")
    print()


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_domains()
    elif "--status" in sys.argv:
        show_status()
    elif "--review" in sys.argv:
        skip = []
        if "--skip" in sys.argv:
            idx = sys.argv.index("--skip") + 1
            if idx < len(sys.argv):
                skip = [sys.argv[idx]]
        result = select_domain(review_mode=True, skip_ids=set(skip))
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    elif "--domain" in sys.argv:
        idx = sys.argv.index("--domain") + 1
        if idx < len(sys.argv):
            result = select_domain(domain_id=sys.argv[idx])
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
    elif "--skip" in sys.argv:
        idx = sys.argv.index("--skip") + 1
        if idx < len(sys.argv):
            result = select_domain(skip_ids={sys.argv[idx]})
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = select_domain()
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
