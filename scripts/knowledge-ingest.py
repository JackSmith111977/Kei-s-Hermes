#!/usr/bin/env python3
"""
knowledge-ingest.py — 知识路由自动执行器 v1.1

基于 knowledge-routing v3.0 的决策树，自动完成知识沉淀的写入+索引更新。
一条命令替代三步手动操作。

用法:
  # 沉淀经验
  python3 knowledge-ingest.py --type experience --title "xxx" --content "..." --reusability high

  # 沉淀到 L3 Brain
  python3 knowledge-ingest.py --type concept --name "xxx" --content "..."
  python3 knowledge-ingest.py --type entity --name "xxx" --content "..."
  python3 knowledge-ingest.py --type summary --name "xxx" --content "..."

  # 自动检测最新的未处理学习总结
  python3 knowledge-ingest.py --auto-detect
"""

import os
import sys
import json
import re
import hashlib
import argparse
import textwrap
from datetime import datetime, date
from pathlib import Path

HOME = os.path.expanduser("~")
EXPERIENCES_DIR = os.path.join(HOME, ".hermes", "experiences", "active")
BRAIN_WIKI_DIR = os.path.join(HOME, ".hermes", "brain", "wiki")
BRAIN_INDEX = os.path.join(HOME, ".hermes", "brain", "index.md")
BRAIN_LOG = os.path.join(HOME, ".hermes", "brain", "log.md")
EXPERIENCES_INDEX = os.path.join(HOME, ".hermes", "experiences", "index.md")
KNOWLEDGE_INDEX = os.path.join(HOME, ".hermes", "KNOWLEDGE_INDEX.md")
LEARNING_REVIEWS = os.path.join(HOME, ".hermes", "learning", "reviews")

# ── L2→L3 升级阈值 ─────────────────────────
MIN_PROMOTION_AGE = 7  # 经验创建 ≥ 7 天才可升级到 L3
PROMOTED_MARKER = "promoted_to_l3"  # frontmatter 中标记已升级的字段


# ── 辅助函数 ──────────────────────────────

def slugify(text):
    """将文本转为文件名友好的 slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:60]


def today():
    return date.today().isoformat()


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def read_file(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def write_file(path, content):
    ensure_dir(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def append_file(path, line):
    ensure_dir(os.path.dirname(path))
    with open(path, 'a', encoding='utf-8') as f:
        f.write(line + "\n")


def parse_frontmatter(content):
    """从 markdown 内容中解析 YAML frontmatter，返回 dict"""
    if not content.startswith('---'):
        return {}
    end = content.find('---', 3)
    if end == -1:
        return {}
    yaml_block = content[3:end].strip()
    meta = {}
    for line in yaml_block.split('\n'):
        line = line.strip()
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            # 处理 bool/数字
            if val.lower() == 'true':
                val = True
            elif val.lower() == 'false':
                val = False
            else:
                try:
                    val = int(val)
                except ValueError:
                    val = val.strip('"\'')
            meta[key] = val
    return meta


def extract_title(content):
    """从 markdown 内容中提取第一个 h1 标题"""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# ') and not line.startswith('##'):
            return line[2:].strip()
    return "未命名"


# ── L2: Experience ────────────────────────

def ingest_experience(title, content, reusability="medium", confidence=3, source="manual", domain="general"):
    """写入经验文件 + 更新索引"""
    today_str = today()
    exp_id = f"exp-{today_str.replace('-', '')}-{slugify(title)[:20]}"

    frontmatter = f"""---
type: experience
reusability: {reusability}
confidence: {confidence}
source: {source}
domain: {domain}
created: {today_str}
next_review: {(date.today().replace(day=min(date.today().day + 7, 28))).isoformat()}
---"""
    body = f"\n# {title}\n\n{content.strip()}\n"

    full = frontmatter + body
    filepath = os.path.join(EXPERIENCES_DIR, f"{exp_id}.md")
    write_file(filepath, full)

    # 更新 experiences/index.md
    _update_experiences_index(exp_id, title, source, reusability, confidence)

    print(f"✅ L2 Experience 已沉淀: {filepath}")
    return filepath


def _update_experiences_index(exp_id, title, source, reusability, confidence):
    """在 experiences/index.md 中追加条目"""
    if not os.path.exists(EXPERIENCES_INDEX):
        # 创建索引文件
        write_file(EXPERIENCES_INDEX, """# 经验档案索引

> 标准化经验积累系统。
> 自动由 knowledge-ingest.py 维护。

## 活跃经验

| ID | 来源 | 可复用性 | 置信度 | 创建时间 |
|:---|:----|:--------:|:------:|:--------:|
""")

    today_str = today()
    tags = slugify(title)
    new_line = f"| {exp_id} | {source} | {tags} | {reusability} | {confidence}/5 | {today_str} |\n"

    # 在表格末尾（--- 之前）插入新行
    content = read_file(EXPERIENCES_INDEX)
    marker = "|:---|:----|:--------:|:------:|:--------:|"
    if marker in content:
        # 在分隔行后追加
        lines = content.split('\n')
        insert_pos = None
        for i, line in enumerate(lines):
            if marker in line:
                insert_pos = i + 1
                break
        if insert_pos and insert_pos < len(lines):
            lines.insert(insert_pos, new_line.strip())
        else:
            lines.append(new_line.strip())
        write_file(EXPERIENCES_INDEX, '\n'.join(lines))
    else:
        append_file(EXPERIENCES_INDEX, new_line.strip())

    # 同时更新 KNOWLEDGE_INDEX
    _update_knowledge_index("L2", title, exp_id)


# ── L3: Brain ─────────────────────────────

BRAIN_TYPES = {
    "concept": {"dir": "concepts", "emoji": "📖"},
    "entity": {"dir": "entities", "emoji": "👤"},
    "summary": {"dir": "summaries", "emoji": "📝"},
    "analysis": {"dir": "analyses", "emoji": "🔬"},
}

BRAIN_TYPE_LABELS = {
    "concept": "概念",
    "entity": "实体",
    "summary": "摘要",
    "analysis": "分析",
}


def ingest_brain(brain_type, name, content, source=""):
    """写入 L3 Brain 页面 + 更新 index.md + 追加 log.md"""
    t = BRAIN_TYPES.get(brain_type)
    if not t:
        print(f"❌ 未知 brain 类型: {brain_type}，可选: {list(BRAIN_TYPES.keys())}")
        sys.exit(1)

    filename = f"{slugify(name)}.md"
    dir_path = os.path.join(BRAIN_WIKI_DIR, t["dir"])
    filepath = os.path.join(dir_path, filename)

    # 根据类型生成内容
    full_content = _render_brain_page(brain_type, name, content, source)
    write_file(filepath, full_content)

    # 更新 brain/index.md
    _update_brain_index(brain_type, name, filename)

    # 追加 brain/log.md
    append_file(BRAIN_LOG, f"- {timestamp()} | {t['emoji']} 新增 {BRAIN_TYPE_LABELS[brain_type]}: [[{name}]]")

    # 更新 KNOWLEDGE_INDEX
    _update_knowledge_index("L3", name, f"brain/wiki/{t['dir']}/{filename}")

    print(f"✅ L3 Brain/{t['dir']}/{filename} 已创建")
    return filepath


def _render_brain_page(brain_type, name, content, source=""):
    """根据类型渲染 brain 页面"""
    header = f"# {name}\n\n"
    source_section = f"\n## 来源\n{source}\n" if source else ""
    footer = f"\n---\n更新: {today()} | 由 knowledge-ingest.py 创建\n"

    if brain_type == "concept":
        return header + content.strip() + source_section + footer
    elif brain_type == "entity":
        return header + content.strip() + source_section + footer
    elif brain_type == "summary":
        return header + f"## 来源\n{source}\n\n## 核心观点\n\n{content.strip()}\n" + footer
    elif brain_type == "analysis":
        return header + f"## 背景\n\n## 发现\n\n{content.strip()}\n" + footer
    return header + content.strip() + footer


def _update_brain_index(brain_type, name, filename):
    """在 brain/index.md 中添加条目"""
    t = BRAIN_TYPES[brain_type]
    label = BRAIN_TYPE_LABELS[brain_type]

    if not os.path.exists(BRAIN_INDEX):
        write_file(BRAIN_INDEX, f"# 🌐 Hermes Knowledge Brain — 知识索引\n\n> 自动由 knowledge-ingest.py 维护\n> 最后更新: {today()}\n\n")

    content = read_file(BRAIN_INDEX)

    # 找到对应类型的表格
    section_header = f"## {t['emoji']} {label}"
    if section_header not in content:
        # 追加新章节
        append_file(BRAIN_INDEX, f"\n{section_header}\n\n| 页面 | 描述 | 创建日期 |\n|:----|:-----|:--------:|\n")

    # 追加行
    new_row = f"| [[{name}]] | {name} | {today()} |\n"
    # 在对应章节表格末尾插入
    lines = content.split('\n')
    found_section = False
    marker_found = False
    insert_pos = None
    for i, line in enumerate(lines):
        if section_header in line:
            found_section = True
        if found_section and '|:----|:-----|:--------:|' in line:
            marker_found = True
            insert_pos = i + 1
        if found_section and marker_found and i > insert_pos:
            # 找到下一个章节或空行
            if line.startswith('##') or line.strip() == '':
                insert_pos = i
                break

    if insert_pos is not None:
        lines.insert(insert_pos, new_row.strip())
        write_file(BRAIN_INDEX, '\n'.join(lines))
    else:
        append_file(BRAIN_INDEX, new_row.strip())

    # 更新总页面数
    content = read_file(BRAIN_INDEX)
    total = _count_brain_pages()
    content = re.sub(r'总页面数: \d+', f'总页面数: {total}', content)
    write_file(BRAIN_INDEX, content)


def _count_brain_pages():
    total = 0
    for t in BRAIN_TYPES.values():
        d = os.path.join(BRAIN_WIKI_DIR, t["dir"])
        if os.path.exists(d):
            total += len([f for f in os.listdir(d) if f.endswith('.md')])
    return total


# ── KNOWLEDGE_INDEX 更新 ──────────────────

def _update_knowledge_index(layer, title, ref_path):
    """在 KNOWLEDGE_INDEX.md 的按主题索引中添加条目"""
    if not os.path.exists(KNOWLEDGE_INDEX):
        return

    content = read_file(KNOWLEDGE_INDEX)
    section = "## 📖 按主题索引"
    if section not in content:
        return

    new_row = f"| {title} | {layer} | {ref_path} | {today()} |\n"

    # 如果还没有表头，先加
    if "| 主题" not in content:
        # 在 section 后加表格
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if section in line:
                table_header = "\n| 主题 | 层级 | 路径 | 创建时间 |\n|:---|:---|:---|:---:|\n"
                lines.insert(i + 1, table_header)
                lines.insert(i + 2, new_row.strip())
                write_file(KNOWLEDGE_INDEX, '\n'.join(lines))
                return

    # 已有表格，追加行
    marker = "|:---|:---|:---|:---:|"
    if marker in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if marker in line:
                lines.insert(i + 1, new_row.strip())
                write_file(KNOWLEDGE_INDEX, '\n'.join(lines))
                return

    append_file(KNOWLEDGE_INDEX, new_row.strip())


# ── Auto-detect: 从学习总结中提炼 ────────

def auto_detect():
    """全量自动检测：扫描 learning/reviews/ + experiences/active/ 升级候选"""
    print("🔍 === 知识自动检测 ===\n")

    # Part 1: 检测未处理的学习总结
    print("── 学习总结 ──")
    found_any = False
    if os.path.exists(LEARNING_REVIEWS):
        md_files = [f for f in os.listdir(LEARNING_REVIEWS) if f.endswith('.md')]
        md_files.sort(key=lambda f: os.path.getmtime(os.path.join(LEARNING_REVIEWS, f)), reverse=True)

        processed_log = os.path.join(HOME, ".hermes", "learning", ".ingested_reviews")
        processed = set()
        if os.path.exists(processed_log):
            with open(processed_log) as f:
                processed = set(line.strip() for line in f if line.strip())

        pending = [f for f in md_files if f not in processed]
        if pending:
            found_any = True
            print(f"📚 发现 {len(pending)} 篇未处理的学习总结:")
            for f in pending[:5]:
                print(f"   📄 {f}")
            if len(pending) > 5:
                print(f"   ... 还有 {len(pending)-5} 篇")
            print()
            print("💡 使用 --from-review 处理指定总结")
        else:
            print("📭 没有未处理的学习总结")
    else:
        print("📭 learning/reviews/ 不存在")

    print()

    # Part 2: 检测 L2→L3 升级候选
    print("── L2→L3 升级候选 ──")
    candidates = list_promotion_candidates()
    if candidates:
        found_any = True
        print(f"📊 发现 {len(candidates)} 个可升级到 L3 的经验:\n")
        for f, fp, title, meta, age in candidates:
            print(f"   📁 {f}")
            print(f"     标题: {title} | 置信度: {meta.get('confidence')}/5 | 已存在: {age}天")
            print()
        print(f"💡 使用 python3 {__file__} --promote 执行升级")
        print(f"   或 python3 {__file__} --promote --dry-run 预览")
    else:
        print("📭 没有符合条件的 L2→L3 升级候选")
        print(f"   条件: reusability=high, confidence≥4, 创建≥{MIN_PROMOTION_AGE}天, 未升级")

    if not found_any:
        print("\n✨ 一切正常！没有待处理的知识任务。")

    print()


def from_review(filename):
    """从指定学习总结中自动提炼知识"""
    filepath = os.path.join(LEARNING_REVIEWS, filename)
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    content = read_file(filepath)

    # 从文件名提取主题
    base = filename.replace('.md', '')
    # 去除 summary_20260509_ 前缀
    name_match = re.search(r'\d{8}_(.+)', base)
    topic = name_match.group(1) if name_match else base
    topic = topic.replace('-', ' ').replace('_', ' ').strip()

    print(f"🔍 从 {filename} 中提炼知识...")
    print(f"   主题: {topic}")
    print()
    print("⚠️ 自动提炼需要人工确认分类。请使用 --type 参数指定目标类型:")  # noqa: E501
    print(f"   python3 knowledge-ingest.py --from-review {filename} --type experience --reusability high")  # noqa: E501
    print(f"   python3 knowledge-ingest.py --from-review {filename} --type concept --name \"{topic}\"")  # noqa: E501

    # 标记为已处理
    processed_log = os.path.join(HOME, ".hermes", "learning", ".ingested_reviews")
    append_file(processed_log, filename)


# ── L2→L3 自动升级 ─────────────────────────

def list_promotion_candidates():
    """扫描 experiences/active/ 返回满足条件的升级候选列表"""
    if not os.path.exists(EXPERIENCES_DIR):
        return []

    candidates = []
    for f in sorted(os.listdir(EXPERIENCES_DIR)):
        if not f.endswith('.md'):
            continue
        filepath = os.path.join(EXPERIENCES_DIR, f)
        content = read_file(filepath)
        meta = parse_frontmatter(content)
        if not meta:
            continue

        # 1. reusability=high
        if meta.get('reusability') != 'high':
            continue
        # 2. confidence >= 4
        if int(meta.get('confidence', 0)) < 4:
            continue
        # 3. 未升级过
        if meta.get(PROMOTED_MARKER):
            continue
        # 4. 创建时间 >= MIN_PROMOTION_AGE 天
        created = meta.get('created', '')
        age = 0
        if created:
            try:
                created_date = datetime.strptime(str(created), '%Y-%m-%d').date()
                age = (date.today() - created_date).days
            except ValueError:
                pass
        if age < MIN_PROMOTION_AGE:
            continue

        title = extract_title(content)
        candidates.append((f, filepath, title, meta, age))

    return candidates


def promote_l2_to_l3(filepath, filename, title, meta):
    """将一条 L2 Experience 升级到 L3 Brain（作为分析或概念）"""
    content = read_file(filepath)
    body_start = content.find('---', 3)
    if body_start == -1:
        return False
    body_start = content.find('\n', body_start + 3)
    if body_start == -1:
        return False
    body = content[body_start:].strip()

    # 判断最适合的 L3 类型
    btype = meta.get('domain', 'general')
    # domain 包含 concept/entity/summary/analysis 则用对应类型
    l3_type = 'analysis'  # 默认
    if btype in ('concept', 'entity', 'summary', 'analysis'):
        l3_type = btype

    # 生成 L3 页面内容（加上来源引用）
    l3_content = f"{body}\n\n## 来源\n本页面由 L2→L3 自动升级生成，源自经验 `{filename}`。\n"

    try:
        ingest_brain(l3_type, title, l3_content, source=f"L2 auto-promote: {filename}")

        # 在经验 frontmatter 中标记已升级
        updated = content.replace(
            f"created: {meta.get('created', '')}",
            f"created: {meta.get('created', '')}\n{PROMOTED_MARKER}: {l3_type}/{slugify(title)}.md"
        )
        if updated != content:
            write_file(filepath, updated)

        print(f"   → ✅ 升级为 L3 Brain/{l3_type}/{slugify(title)}.md")
        return True
    except Exception as e:
        print(f"   → ❌ 升级失败: {e}")
        return False


def auto_promote(dry_run=False):
    """自动扫描并升级符合条件的 L2 Experience 到 L3 Brain"""
    candidates = list_promotion_candidates()

    if not candidates:
        print("📭 没有符合条件的 L2→L3 升级候选")
        print(f"   条件: reusability=high, confidence≥4, 创建≥{MIN_PROMOTION_AGE}天, 未升级")
        return

    print(f"📊 发现 {len(candidates)} 个 L2→L3 升级候选:\n")
    for f, fp, title, meta, age in candidates:
        print(f"   📁 {f}")
        print(f"     标题: {title}")
        print(f"     置信度: {meta.get('confidence')}/5 | 已存在: {age}天")
        print()

    if dry_run:
        print(f"🔍 Dry-run 模式: 共 {len(candidates)} 个候选可升级")
        print(f"   使用 python3 {__file__} --promote 执行升级")
        return

    # 执行升级
    print("── 开始升级 ──")
    promoted = 0
    for f, fp, title, meta, age in candidates:
        print(f"   🔼 {f} ({title})...")
        if promote_l2_to_l3(fp, f, title, meta):
            promoted += 1

    print(f"\n✅ 升级完成: {promoted}/{len(candidates)} 个经验已升级到 L3 Brain")


# ── 主入口 ─────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="知识路由自动执行器")
    parser.add_argument("--type", choices=["experience", "concept", "entity", "summary", "analysis"],
                        help="知识类型")
    parser.add_argument("--title", help="经验标题 (for --type experience)")
    parser.add_argument("--name", help="知识页面名称 (for L3 Brain types)")
    parser.add_argument("--content", help="知识内容 (文本或文件路径，以 @ 开头)")
    parser.add_argument("--reusability", choices=["high", "medium", "low"], default="medium")
    parser.add_argument("--confidence", type=int, default=3, choices=range(1, 6))
    parser.add_argument("--source", default="manual", help="来源标识")
    parser.add_argument("--domain", default="general", help="领域分类")
    parser.add_argument("--auto-detect", action="store_true", help="自动检测未处理的学习总结 + L2→L3 升级候选")
    parser.add_argument("--from-review", help="从指定学习总结文件提炼")
    parser.add_argument("--promote", action="store_true", help="将符合条件的 L2 Experience 自动升级到 L3 Brain")
    parser.add_argument("--dry-run", action="store_true", help="配合 --promote 使用，只预览不执行")

    args = parser.parse_args()

    # 处理 --auto-detect
    if args.auto_detect:
        auto_detect()
        return

    # 处理 --promote
    if args.promote:
        auto_promote(dry_run=args.dry_run)
        return

    # 处理 --from-review
    if args.from_review:
        from_review(args.from_review)
        return

    # 处理 --type experience
    if args.type == "experience":
        if not args.title or not args.content:
            print("❌ --type experience 需要 --title 和 --content 参数")
            sys.exit(1)
        content = args.content
        if content.startswith('@'):
            # 从文件读取
            fpath = content[1:]
            if os.path.exists(fpath):
                with open(fpath) as f:
                    content = f.read()
            else:
                print(f"❌ 文件不存在: {fpath}")
                sys.exit(1)
        ingest_experience(args.title, content, args.reusability, args.confidence, args.source, args.domain)
        return

    # 处理 L3 Brain 类型
    if args.type in BRAIN_TYPES:
        if not args.name or not args.content:
            print(f"❌ --type {args.type} 需要 --name 和 --content 参数")
            sys.exit(1)
        content = args.content
        if content.startswith('@'):
            fpath = content[1:]
            if os.path.exists(fpath):
                with open(fpath) as f:
                    content = f.read()
            else:
                print(f"❌ 文件不存在: {fpath}")
                sys.exit(1)
        ingest_brain(args.type, args.name, content, args.source)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
