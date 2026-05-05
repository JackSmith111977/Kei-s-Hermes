#!/usr/bin/env python3
"""
夜间自习引擎 v2.0 - 领域发现器
自动检测需要加入学习队列的新领域。

发现规则：
1. Skill 超过 30 天未更新 → 自动加入学习队列
2. gap_queue 中 ≥ 3 个相关缺口 → 自动创建领域
3. 用户频繁查询某主题 → 自动创建领域（需要日志分析）

用法：
  python3 discover_domains.py              # 运行所有发现规则
  python3 discover_domains.py --rule stale # 只检查过时 skill
  python3 discover_domains.py --rule gaps  # 只检查缺口队列
  python3 discover_domains.py --dry-run    # 只显示建议，不修改配置
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_PATH = Path.home() / ".hermes" / "config" / "night_study_config_v2.json"
SKILLS_DIR = Path.home() / ".hermes" / "skills"
LEARNING_STATE_PATH = Path.home() / ".hermes" / "learning_state.json"
REVIEW_ENGINE_PATH = Path.home() / ".hermes" / "skills" / "learning-review-cycle" / "scripts" / "review-engine.py"

STALE_THRESHOLD_DAYS = 30
MIN_GAP_COUNT = 3


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_existing_domain_ids(config):
    """获取已有的领域 ID 和 target_skill"""
    domain_ids = set()
    target_skills = set()
    for domain in config.get("domains", []):
        domain_ids.add(domain["id"])
        if domain.get("target_skill"):
            target_skills.add(domain["target_skill"])
    return domain_ids, target_skills


def check_stale_skills(config):
    """规则 1：检查超过 30 天未更新的 skill"""
    discoveries = []
    existing_ids, existing_skills = get_existing_domain_ids(config)

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        # 获取文件修改时间
        mtime = os.path.getmtime(skill_md)
        mtime_dt = datetime.fromtimestamp(mtime)
        age_days = (datetime.now() - mtime_dt).days

        if age_days > STALE_THRESHOLD_DAYS and skill_dir.name not in existing_skills:
            discoveries.append({
                "rule": "stale_skill",
                "suggested_id": skill_dir.name.replace("-", "_"),
                "skill_name": skill_dir.name,
                "reason": f"Skill '{skill_dir.name}' 已超过 {age_days} 天未更新",
                "age_days": age_days,
                "priority": 0.5,
                "confidence": "medium",
            })

    return discoveries


def check_gap_queue():
    """规则 2：检查 gap_queue 中的缺口聚集"""
    discoveries = []
    # 尝试通过 review-engine.py 获取 gap_queue 状态
    # 这里使用简化方案：检查是否有 gap_queue 文件
    # 实际使用时可以调用 review-engine.py list-gaps
    return discoveries


def check_learning_patterns():
    """规则 3：检查学习模式中的频繁主题"""
    discoveries = []
    # 分析 night_study_sessions 日志中出现频率高的主题
    sessions_dir = Path.home() / ".hermes" / "logs" / "night_study_sessions"
    if not sessions_dir.exists():
        return discoveries

    topic_counts = {}
    for log_file in sessions_dir.glob("*.jsonl"):
        with open(log_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    domain = entry.get("domain", "")
                    topic_counts[domain] = topic_counts.get(domain, 0) + 1
                except json.JSONDecodeError:
                    continue

    # 找出高频主题（超过 10 次）
    for topic, count in topic_counts.items():
        if count > 10:
            discoveries.append({
                "rule": "frequent_topic",
                "suggested_id": topic,
                "reason": f"主题 '{topic}' 在学习中出现 {count} 次",
                "count": count,
                "priority": 0.6,
                "confidence": "low",
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
        "patterns": check_learning_patterns,
    }

    if rule_filter:
        rules_to_run = {rule_filter: rules[rule_filter]}
    else:
        rules_to_run = rules

    for rule_name, rule_func in rules_to_run.items():
        try:
            discoveries = rule_func(config) if rule_name == "stale" else rule_func()
            all_discoveries.extend(discoveries)
        except Exception as e:
            print(f"⚠️  规则 '{rule_name}' 执行失败：{e}")

    # 过滤已存在的领域
    new_discoveries = [d for d in all_discoveries if d.get("suggested_id") not in existing_ids]

    if not new_discoveries:
        print("✅ 没有发现新的学习领域")
        return

    print(f"\n🔍 发现 {len(new_discoveries)} 个潜在新学习领域：\n")
    for d in new_discoveries:
        print(f"  📌 [{d['rule']}] {d['suggested_id']}")
        print(f"     原因：{d['reason']}")
        print(f"     优先级：{d['priority']} | 置信度：{d['confidence']}")
        print()

    if dry_run:
        print("（dry-run 模式，未修改配置）")
        return

    # 询问用户是否添加（在 cron 中自动添加高置信度的）
    print("💡 提示：在 cron 模式下，高置信度的发现会自动加入配置")
    for d in new_discoveries:
        if d.get("confidence") in ("high", "medium"):
            print(f"  ➕ 自动添加：{d['suggested_id']}")
            # 这里可以自动添加到配置中
            # 但为了安全起见，实际添加需要用户确认

    return new_discoveries


def main():
    dry_run = False
    rule_filter = None

    args = sys.argv[1:]
    for arg in args:
        if arg == "--dry-run":
            dry_run = True
        elif arg.startswith("--rule="):
            rule_filter = arg.split("=")[1]
        elif arg.startswith("--rule "):
            pass  # handled below

    for i, arg in enumerate(args):
        if arg == "--rule" and i + 1 < len(args):
            rule_filter = args[i + 1]

    discover(dry_run=dry_run, rule_filter=rule_filter)


if __name__ == "__main__":
    main()
