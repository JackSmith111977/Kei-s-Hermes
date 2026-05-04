#!/usr/bin/env python3
"""
File Organizer for Hermes Agent System
按规则自动分类整理文件

用法:
    python3 file-organize.py --dry-run   # 预览（不执行）
    python3 file-organize.py --apply     # 执行整理
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

HERMES_DIR = os.path.expanduser('~/.hermes')

# 文件类型 -> 目标目录
FILE_RULES = {
    # 输出文件
    '.pdf': 'output/pdf',
    '.docx': 'output/documents',
    '.pptx': 'output/documents',
    '.xlsx': 'output/documents',
    '.png': 'output/images',
    '.jpg': 'output/images',
    '.jpeg': 'output/images',
    '.gif': 'output/images',
    '.svg': 'output/images',
    '.html': 'output/html',
    '.htm': 'output/html',
    # 脚本
    '.py': 'scripts',
    '.sh': 'scripts',
}

# 始终保留在根目录的文件
KEEP_IN_ROOT = {
    'SOUL.md', 'MEMORY.md', 'FILE_INDEX.md', 'FILE_INDEX.json',
    'TASK_QUEUE.md', '.env', '.gitignore',
    'config.yaml', 'learning_state.json',
    'auth.json', 'auth.lock', 'state.db', 'state.db-wal', 'state.db-shm',
    'gateway.pid', 'gateway_state.json', 'channel_directory.json',
    'feishu_seen_message_ids.json', 'processes.json', 'models_dev_cache.json',
    # 核心配置文件（最高优先级，绝对不可移动）
    '.hermes.md', 'AGENTS.md', 'CLAUDE.md', '.cursorrules',
    # 根目录 .md 文件（可能是重要文档或中间产物，保留不动）
    'hackathon_report.md', 'hackathon_report_final.md', 'hackathon_report_part1.md',
    'hackathon_full_v2.md', 'hackathon_full_v2_clean.md',
    'pdf_design_plan.md',
}

# 归档关键词（文件名包含这些应移入 archive/）
ARCHIVE_KEYWORDS = ['_v', '_backup', '_old', '_temp', '_copy']

# 要跳过的目录
SKIP_DIRS = {
    '__pycache__', '.git', 'node_modules', '.venv', 'venv',
    'cache', '.cache', 'audio_cache', 'sessions', 'logs',
    'skills', 'scripts', 'config', 'cron', 'learning', 'archive', 'output'
}


def should_archive(filename):
    """判断文件是否应归档"""
    name_lower = filename.lower()
    return any(kw in name_lower for kw in ARCHIVE_KEYWORDS)


def get_target_dir(filename, extension):
    """获取目标目录
    如果文件包含版本标记（_v, _v2等），优先归入 archive/
    """
    ext = extension.lower()
    # 版本标记文件优先归档
    if should_archive(filename):
        return 'archive'
    return FILE_RULES.get(ext)


def scan_root_files():
    """扫描根目录下需要整理的文件"""
    files = []
    for item in os.listdir(HERMES_DIR):
        if item in KEEP_IN_ROOT:
            continue
        if item.startswith('.'):
            continue

        filepath = os.path.join(HERMES_DIR, item)
        if not os.path.isfile(filepath):
            continue

        ext = Path(item).suffix
        if ext:
            files.append({
                'name': item,
                'path': filepath,
                'ext': ext,
                'archive': should_archive(item),
            })

    return files


def organize(dry_run=True):
    """执行整理"""
    files = scan_root_files()

    if not files:
        print("✅ 根目录没有需要整理的文件！")
        return

    print(f"{'🔍 预览模式' if dry_run else '📦 执行模式'} - 找到 {len(files)} 个待整理文件\n")

    moves = []

    for f in files:
        # archive 检查优先（包含版本标记的文件直接归档）
        target = get_target_dir(f['name'], f['ext'])
        if not target:
            target = 'archive' if f['archive'] else 'other'

        src = f['path']
        dest_dir = os.path.join(HERMES_DIR, target)
        dest = os.path.join(dest_dir, f['name'])

        # 处理重名
        if os.path.exists(dest):
            base = Path(f['name']).stem
            ext = Path(f['name']).suffix
            counter = 1
            while os.path.exists(dest):
                dest = os.path.join(dest_dir, f"{base}-{counter}{ext}")
                counter += 1

        moves.append({
            'src': src,
            'dest': dest,
            'name': f['name'],
            'target_dir': target,
        })

    # 打印整理计划
    for m in moves:
        action = "📦 移动" if not dry_run else "➡️  计划移动"
        print(f"  {action}: {m['name']}")
        print(f"    从: {m['src']}")
        print(f"    到: {m['dest']}")
        print()

    # 执行移动
    if not dry_run:
        for m in moves:
            dest_dir = os.path.dirname(m['dest'])
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(m['src'], m['dest'])
            print(f"  ✅ 已移动: {m['name']} → {m['target_dir']}/")

        print(f"\n✅ 整理完成！移动了 {len(moves)} 个文件。")
        print(f"💡 建议运行 file-index.py 更新索引。")
    else:
        print(f"\n💡 以上是整理预览。使用 --apply 执行。")


def main():
    dry_run = '--apply' not in sys.argv

    if not os.path.isdir(HERMES_DIR):
        print(f"❌ Hermes 目录不存在: {HERMES_DIR}")
        sys.exit(1)

    organize(dry_run=dry_run)


if __name__ == '__main__':
    main()
