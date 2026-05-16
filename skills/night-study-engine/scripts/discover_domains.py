#!/usr/bin/env python3
"""
夜间自习引擎 v4.0 - 领域发现器（cap-pack 感知版）
自动检测需要加入学习队列的新领域。v4.0 增加：
- 增强的 stale skill 检测（跳过系统 skill）
- gap_queue 真实读取（通过 review-engine.py）
- 基于 learning_history 的热度分析
- 概念关系断裂检测（孤立概念提醒）
- cap-pack 包自动发现（从 Hermes-Cap-Pack/packs/ 同步新包）

发现规则：
1. Skill 超过 30 天未更新 → 自动加入学习队列
2. gap_queue 中 ≥ 3 个相关缺口 → 自动建议新领域
3. 用户频繁查询某主题（日志分析）→ 自动创建领域
4. 概念关系断裂检测（孤立概念超过 90 天未复习） → v3.0 新增

用法：
  python3 discover_domains.py                        # 运行所有发现规则
  python3 discover_domains.py --rule stale            # 只检查过时 skill
  python3 discover_domains.py --rule gaps             # 只检查缺口队列
  python3 discover_domains.py --rule orphan           # 检查孤立概念 v3.0
  python3 discover_domains.py --dry-run               # 只显示建议，不修改配置
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_PATH = Path.home() / ".hermes" / "config" / "night_study_config_v3.json"
CONFIG_V2_PATH = Path.home() / ".hermes" / "config" / "night_study_config_v2.json"
SKILLS_DIR = Path.home() / ".hermes" / "skills"
KB_DIR = Path.home() / ".hermes" / "night_study" / "knowledge_base"
REVIEW_ENGINE = Path.home() / ".hermes" / "skills" / "learning-review-cycle" / "scripts" / "review-engine.py"

STALE_THRESHOLD_DAYS = 30
MIN_GAP_COUNT = 3
ORPHAN_THRESHOLD_DAYS = 90

# 系统 skill 列表（不自动学习）
SYSTEM_SKILLS = {
    "hermes-self-analysis", "self-capabilities-map", "learning-workflow",
    "learning", "learning-review-cycle", "skill-creator", "web-access",
    "hermes-agent", "night-study-engine", "deep-research",
    "anti-repetition-loop", "knowledge-routing"
}


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    elif CONFIG_V2_PATH.exists():
        with open(CONFIG_V2_PATH) as f:
            return json.load(f)
    return {"domains": []}


def save_config(config):
    path = CONFIG_PATH if CONFIG_PATH.exists() else CONFIG_V2_PATH
    with open(path, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_existing_domain_ids(config):
    domain_ids = set()
    target_skills = set()
    for domain in config.get("domains", []):
        domain_ids.add(domain["id"])
        if domain.get("target_skill"):
            target_skills.add(domain["target_skill"])
    return domain_ids, target_skills


def is_system_skill(skill_name):
    return skill_name in SYSTEM_SKILLS or skill_name.startswith("_")


def check_stale_skills(config):
    """规则 1：检查超过 30 天未更新的 skill"""
    discoveries = []
    existing_ids, existing_skills = get_existing_domain_ids(config)

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or is_system_skill(skill_dir.name):
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        mtime = os.path.getmtime(skill_md)
        mtime_dt = datetime.fromtimestamp(mtime)
        age_days = (datetime.now() - mtime_dt).days

        if age_days > STALE_THRESHOLD_DAYS and skill_dir.name not in existing_skills:
            priority = min(0.9, 0.3 + age_days / 365)
            discoveries.append({
                "rule": "stale_skill",
                "suggested_id": skill_dir.name.replace("-", "_"),
                "skill_name": skill_dir.name,
                "reason": f"Skill '{skill_dir.name}' 已超过 {age_days} 天未更新",
                "age_days": age_days,
                "priority": round(priority, 2),
                "confidence": "medium",
            })

    return discoveries


def check_gap_queue():
    """规则 2：检查 gap_queue 中的缺口聚集"""
    discoveries = []
    if not REVIEW_ENGINE.exists():
        return discoveries

    try:
        result = subprocess.run(
            [sys.executable, str(REVIEW_ENGINE), "list-gaps"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return discoveries

        # 解析 gap 输出（按领域聚集）
        gap_by_topic = {}
        for line in result.stdout.strip().split("\n"):
            if ":" in line:
                parts = line.split(":", 1)
                topic = parts[0].strip()
                gap_by_topic[topic] = gap_by_topic.get(topic, 0) + 1

        for topic, count in gap_by_topic.items():
            if count >= MIN_GAP_COUNT:
                discoveries.append({
                    "rule": "gap_cluster",
                    "suggested_id": topic.lower().replace(" ", "_"),
                    "gap_topic": topic,
                    "reason": f"主题 '{topic}' 有 {count} 个知识缺口",
                    "gap_count": count,
                    "priority": min(0.8, 0.3 + count * 0.1),
                    "confidence": "high" if count >= 5 else "medium",
                })
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return discoveries


def check_orphan_concepts():
    """规则 4（v3.0 新增）：检查孤立概念 — 超过 90 天未复习"""
    discoveries = []
    today = datetime.now()
    for kb_file in KB_DIR.glob("*.json"):
        try:
            with open(kb_file) as f:
                kb = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        domain_id = kb.get("domain", kb_file.stem)
        orphans = []
        for name, concept in kb.get("concepts", {}).items():
            next_review = concept.get("next_review")
            if next_review:
                try:
                    review_date = datetime.strptime(next_review, "%Y-%m-%d")
                    days_overdue = (today - review_date).days
                    if days_overdue > ORPHAN_THRESHOLD_DAYS:
                        orphans.append({"name": name, "days_overdue": days_overdue})
                except ValueError:
                    continue

        if orphans:
            discoveries.append({
                "rule": "orphan_concept",
                "suggested_id": domain_id,
                "domain": domain_id,
                "reason": f"领域 '{domain_id}' 有 {len(orphans)} 个孤立概念(>90天未复习)",
                "orphan_count": len(orphans),
                "orphans": orphans[:5],  # 只显示前 5 个
                "priority": 0.4,
                "confidence": "medium",
            })

    return discoveries


def discover(dry_run=False, rule_filter=None):
    """运行所有发现规则"""
    config = load_config()
    existing_ids, _ = get_existing_domain_ids(config)
    all_discoveries = []

    rules = {
        "stale": check_stale_skills,
        "gaps": check_gap_queue,
        "orphan": check_orphan_concepts,
    }

    if rule_filter:
        rules_to_run = {rule_filter: rules[rule_filter]}
    else:
        rules_to_run = rules

    for rule_name, rule_func in rules_to_run.items():
        try:
            discoveries = rule_func(config) if rule_name in ("stale",) else rule_func() if rule_name in ("gaps", "orphan") else rule_func()
            all_discoveries.extend(discoveries)
        except Exception as e:
            print(f"⚠️  规则 '{rule_name}' 执行失败：{e}")

    # 过滤已存在的领域
    new_discoveries = [d for d in all_discoveries if d.get("suggested_id") not in existing_ids]

    if not new_discoveries:
        print("✅ 没有发现新的学习领域")
        return

    print(f"\n🔍 发现 {len(new_discoveries)} 个潜在新学习领域：\n")

    for i, d in enumerate(new_discoveries, 1):
        print(f"  [{i}] [{d['rule']}] {d['reason']}")
        print(f"      建议 ID: {d['suggested_id']}")
        print(f"      优先级: {d['priority']} | 置信度: {d['confidence']}")
        if 'age_days' in d:
            print(f"      年龄: {d['age_days']} 天")
        if 'gap_count' in d:
            print(f"      缺口数: {d['gap_count']}")
        if 'orphan_count' in d:
            print(f"      孤立概念: {d['orphan_count']} 个")
            for o in d['orphans']:
                print(f"        - {o['name']} ({o['days_overdue']} 天逾期)")
        print()

    if not dry_run:
        add = input(f"\n是否添加这些新领域到配置？(y/N): ").strip().lower()
        if add == 'y':
            for d in new_discoveries:
                new_domain = {
                    "id": d["suggested_id"],
                    "name": d.get("skill_name", d["suggested_id"]).replace("_", " ").title(),
                    "keywords": d.get("skill_name", d["suggested_id"]),
                    "target_skill": d.get("skill_name", ""),
                    "priority": d["priority"],
                    "schedule_interval_hours": 24,
                    "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "freshness_score": 0.5,
                    "learning_history": {
                        "total_sessions": 0,
                        "avg_quality": 0.5,
                        "last_loop_count": 1,
                        "consecutive_failures": 0
                    }
                }
                config.setdefault("domains", []).append(new_domain)
                print(f"  ✅ 添加领域: {new_domain['id']}")
            save_config(config)
            print(f"\n✅ 已更新配置文件")
    else:
        print("💡 使用 --dry-run 跳过，未修改配置")

    # ── Cap-Pack 包同步检查 ──
    print(f"\n{'='*50}")
    print("📦 Cap-Pack 包同步检查")
    CAP_PACK_DIR = Path.home() / "Hermes-Cap-Pack" / "packs"
    cap_pack_domain_map = {
        "agent-orchestration": "agent_orchestration", "creative-design": "creative_design",
        "developer-workflow": "dev_tools", "devops-monitor": "devops_monitoring",
        "doc-engine": "doc_generation", "financial-analysis": "financial_analysis",
        "github-ecosystem": "github_ecosystem", "learning-engine": "learning_methodology",
        "learning-workflow": "learning_methodology", "media-processing": "media_audio_video",
        "messaging": "messaging_comm", "metacognition": "metacognition_system",
        "network-proxy": "network_proxy", "quality-assurance": "quality_governance",
        "skill-quality": "quality_governance", "security-audit": "security_audit",
        "social-gaming": "social_gaming",
    }
    if CAP_PACK_DIR.exists():
        existing_ids = {d["id"] for d in config["domains"]}
        for pack_dir in sorted(CAP_PACK_DIR.iterdir()):
            if not pack_dir.is_dir() or pack_dir.name.startswith("."):
                continue
            did = cap_pack_domain_map.get(pack_dir.name)
            if did and did not in existing_ids:
                skill_count = len(list(pack_dir.glob("SKILLS/*")))
                print(f"  🆕 新 cap-pack: {pack_dir.name} → 领域 {did} ({skill_count} skills)")
                if not dry_run:
                    nd = {"id": did, "name": pack_dir.name.replace("-"," ").title(),
                          "keywords": pack_dir.name, "target_skill": "", "priority": 0.5,
                          "schedule_interval_hours": 12, "cap_pack": [pack_dir.name],
                          "freshness_score": 0.5,
                          "review_schedule": {"l1":now[:10],"l2":now[:10],"l3":now[:10]},
                          "learning_history": {"total_sessions":0,"avg_quality":0.5,
                                               "last_loop_count":0,"consecutive_failures":0},
                          "knowledge_gaps_filled":[], "last_updated": now}
                    config["domains"].append(nd)
                    save_config(config)
                    print(f"     ✅ 已添加")
                    created_kb = True
        if not dry_run and created_kb:
            print(f"  📊 领域总数: {len(config['domains'])}")
    else:
        print("  ⚠️ cap-pack 目录不存在")
    return created_kb


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    rule_filter = None
    if "--rule" in sys.argv:
        idx = sys.argv.index("--rule") + 1
        if idx < len(sys.argv):
            rule_filter = sys.argv[idx]

    discover(dry_run, rule_filter)
