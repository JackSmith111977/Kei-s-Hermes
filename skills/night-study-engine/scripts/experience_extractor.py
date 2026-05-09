#!/usr/bin/env python3
"""
夜间自习引擎 v3.0 - 经验提取器
每次学习完成后自动检查是否有可复用的经验，按标准格式归档。

判断标准（至少满足一项）：
1. 发现可复用的方法/流程/模式
2. 解决了之前卡住的问题，找到了可靠方案
3. 验证/推翻了假设

用法：
  python3 experience_extractor.py --check                 # 检查当前学习产出是否有经验
  python3 experience_extractor.py --save                   # 交互式保存经验
  python3 experience_extractor.py --list                   # 列出所有经验
  python3 experience_extractor.py --list --domain ai_tech  # 按领域列出
  python3 experience_extractor.py --due                    # 列出到期复习的经验
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

EXPERIENCES_DIR = Path.home() / ".hermes" / "experiences" / "active"
INDEX_PATH = Path.home() / ".hermes" / "experiences" / "index.md"
SKILLS_DIR = Path.home() / ".hermes" / "skills"

REVIEW_INTERVALS = [7, 30, 90]


def ensure_dirs():
    EXPERIENCES_DIR.mkdir(parents=True, exist_ok=True)


def generate_experience_id():
    """生成唯一经验 ID"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"exp_{ts}"


def save_experience(exp_type, reusability, confidence, source, domain, description, skill_ref=None):
    """保存经验到文件"""
    ensure_dirs()
    exp_id = generate_experience_id()
    today = datetime.now().strftime("%Y-%m-%d")
    next_review = (datetime.now() + timedelta(days=REVIEW_INTERVALS[0])).strftime("%Y-%m-%d")

    content = f"""---
type: {exp_type}
reusability: {reusability}
confidence: {confidence}
source: {source}
domain: {domain}
created: {today}
next_review: {next_review}
review_interval: {REVIEW_INTERVALS[0]}
---
{description}
"""
    if skill_ref:
        content += f"\n相关 Skill：`{skill_ref}`"

    filepath = EXPERIENCES_DIR / f"{exp_id}.md"
    with open(filepath, "w") as f:
        f.write(content)

    # 更新 index.md
    update_index(exp_id, exp_type, reusability, confidence, domain, today, description[:60])

    # 如果 reusability=high → 自动更新对应 skill 的 references/
    if reusability == "high" and skill_ref:
        update_skill_references(skill_ref, filepath, description)

    print(f"✅ 经验已保存: {filepath}")
    return filepath


def update_index(exp_id, exp_type, reusability, confidence, domain, created, desc_short):
    """更新经验索引"""
    ensure_dirs()
    entry = f"| {exp_id} | {exp_type:<12} | {reusability:<8} | {confidence} | {domain:<10} | {created} | {desc_short} |\n"

    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            content = f.read()
    else:
        content = """# 经验索引

> 自动生成的全局经验目录。每次有新经验时自动更新。

| ID | 类型 | 可复用性 | 置信度 | 领域 | 创建日期 | 描述 |
|:---|:---:|:--------:|:-----:|:----:|:--------:|:-----|\n"""

    # 在表格后追加新行
    if "| ---" in content:
        # 找到表格末尾
        content += entry
    else:
        content += entry

    with open(INDEX_PATH, "w") as f:
        f.write(content)


def update_skill_references(skill_name, experience_path, description):
    """自动更新对应 skill 的 references/"""
    skill_refs_dir = SKILLS_DIR / skill_name / "references"
    if not skill_refs_dir.exists():
        print(f"  ⚠️  Skill '{skill_name}' 没有 references/ 目录，跳过自动更新")
        return

    # 创建链接文件
    link_path = skill_refs_dir / f"experience_{datetime.now().strftime('%Y%m%d')}.md"
    link_content = f"""# 经验引用 — 自动注入

> 来源: [{experience_path.name}]({experience_path})

{description}

*自动注入于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    with open(link_path, "w") as f:
        f.write(link_content)
    print(f"  ✅ 已注入 skill '{skill_name}' 的 references/ 目录")


def check_for_experience(domain, learning_output_files=None):
    """检查是否有可复用的经验（基于学习产出）"""
    print(f"\n🔍 检查领域 '{domain}' 的学习产出是否有可复用经验...")
    print()
    print("判断标准（至少满足一项）：")
    print("  1️⃣  发现可复用的方法/流程/模式")
    print("  2️⃣  解决了之前卡住的问题，找到了可靠方案")
    print("  3️⃣  验证/推翻了假设")
    print()
    print("📝 请参考学习产出回答以下问题：")
    print("  - 这个流程能在其他领域用吗？")
    print("  - 之前为什么失败？现在怎么解决了？")
    print("  - 之前猜对了吗？")
    return None  # 由调用者判断


def list_experiences(domain_filter=None):
    """列出所有经验"""
    ensure_dirs()
    files = sorted(EXPERIENCES_DIR.glob("*.md"))
    if not files:
        print("📭 没有保存的经验")
        return

    count = 0
    for filepath in files:
        if filepath.name == "index.md":
            continue
        with open(filepath) as f:
            content = f.read()
        # 简单解析 frontmatter
        lines = content.split("\n")
        meta = {}
        in_front = False
        for line in lines:
            if line == "---":
                in_front = not in_front
                continue
            if in_front and ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()

        if domain_filter and meta.get("domain") != domain_filter:
            continue

        print(f"\n📄 {filepath.name}")
        print(f"  类型: {meta.get('type', '?')}")
        print(f"  可复用性: {meta.get('reusability', '?')}")
        print(f"  置信度: {meta.get('confidence', '?')}")
        print(f"  领域: {meta.get('domain', '?')}")
        print(f"  创建: {meta.get('created', '?')}")
        print(f"  下次复习: {meta.get('next_review', '?')}")
        count += 1

    print(f"\n共 {count} 条经验")


def list_due_reviews():
    """列出到期复习的经验"""
    ensure_dirs()
    today = datetime.now().strftime("%Y-%m-%d")
    files = sorted(EXPERIENCES_DIR.glob("*.md"))
    due = []

    for filepath in files:
        if filepath.name == "index.md":
            continue
        with open(filepath) as f:
            content = f.read()
        lines = content.split("\n")
        meta = {}
        in_front = False
        for line in lines:
            if line == "---":
                in_front = not in_front
                continue
            if in_front and ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()

        next_review = meta.get("next_review")
        if next_review and next_review <= today:
            due.append((filepath.name, meta))

    if not due:
        print("✅ 没有到期复习的经验")
        return

    print(f"\n📋 到期复习的经验 ({len(due)} 条):\n")
    for name, meta in due:
        print(f"  📄 {name}")
        print(f"    类型: {meta.get('type', '?')} | 可复用性: {meta.get('reusability', '?')}")
        print(f"    领域: {meta.get('domain', '?')} | 创建: {meta.get('created', '?')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="经验提取器 v3.0")
    parser.add_argument("--check", action="store_true", help="检查学习产出")
    parser.add_argument("--save", action="store_true", help="保存经验（交互式）")
    parser.add_argument("--list", action="store_true", help="列出经验")
    parser.add_argument("--domain", help="按领域过滤")
    parser.add_argument("--due", action="store_true", help="列出到期复习经验")
    parser.add_argument("--type", choices=["experience", "skill", "rule"], help="经验类型")
    parser.add_argument("--reusability", choices=["high", "medium", "low"], help="可复用性")
    parser.add_argument("--confidence", type=int, choices=range(1, 6), help="置信度(1-5)")
    parser.add_argument("--source", default="night-study", help="来源")
    parser.add_argument("--description", help="经验描述")
    parser.add_argument("--skill-ref", help="相关 Skill 名称")

    args = parser.parse_args()

    if args.list:
        list_experiences(args.domain)
    elif args.due:
        list_due_reviews()
    elif args.check:
        check_for_experience(args.domain or "unknown")
    elif args.save:
        if not all([args.type, args.reusability, args.confidence, args.description]):
            parser.print_help()
            print("\n❌ --save 需要 --type, --reusability, --confidence, --description")
            sys.exit(1)
        save_experience(
            args.type, args.reusability, args.confidence,
            args.source, args.domain or "general",
            args.description, args.skill_ref
        )
    else:
        # 默认：检查是否有经验可提取
        check_for_experience(args.domain or "unknown")
