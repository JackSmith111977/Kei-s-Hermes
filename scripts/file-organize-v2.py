#!/usr/bin/env python3
"""
Hermes File Organizer (v2.0 - Config Driven)
Batch organize files in the root directory based on governance.yaml rules.

Usage:
    python3 file-organize-v2.py [--dry-run]
"""

import os
import sys
import yaml
import re
import shutil
import json
import time
from pathlib import Path
from datetime import datetime

HERMES_DIR = os.path.expanduser("~/.hermes")
CONFIG_PATH = os.path.join(HERMES_DIR, "governance.yaml")

# 根目录必须保留的文件（无论规则如何匹配，都不移动）
ROOT_KEEP_LIST = {
    "SOUL.md", "MEMORY.md", "FILE_INDEX.md", "FILE_INDEX.json",
    "TASK_QUEUE.md", ".env", ".gitignore",
    "config.yaml", "learning_state.json",
    "auth.json", "auth.lock", "state.db", "state.db-wal", "state.db-shm",
    "gateway.pid", "gateway_state.json", "channel_directory.json",
    "feishu_seen_message_ids.json", "processes.json", "models_dev_cache.json",
    "governance.yaml",
    "hackathon_report.md", "hackathon_report_final.md", "hackathon_report_part1.md",
    "pdf_design_plan.md",
    "FILE_INDEX.md", "FILE_INDEX.json"
}

def load_config():
    """加载配置"""
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ 配置文件不存在：{CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def match_rule(filename, rules):
    """匹配规则"""
    ext = Path(filename).suffix.lower()
    
    for rule in rules:
        if rule.get('enabled') is False:
            continue
        
        filter_conf = rule.get('filter', {})
        action = rule.get('action')
        
        # 1. 检查类型
        allowed_types = filter_conf.get('types', [])
        if allowed_types and allowed_types != ["*"]:
            if ext not in [t.lower() for t in allowed_types]:
                continue

        # 2. 检查正则
        name_regex = filter_conf.get('name_regex')
        if name_regex:
            if not re.match(name_regex, filename):
                continue

        return action
    
    return None

def organize(dry_run=True):
    """执行整理"""
    config = load_config()
    rules = config.get('rules', [])
    
    print(f"📂 扫描目录：{HERMES_DIR}")
    print(f"⚙️  加载规则：{len(rules)} 条")
    print(f"{'🔍 预览模式' if dry_run else '📦 执行模式'}\n")

    moves = 0
    skipped = 0

    # 只扫描根目录的文件
    for item in os.listdir(HERMES_DIR):
        filepath = os.path.join(HERMES_DIR, item)
        if not os.path.isfile(filepath):
            continue
        
        if item in ROOT_KEEP_LIST:
            skipped += 1
            continue
        
        action = match_rule(item, rules)
        if action:
            dest = action.get('destination')
            dest_path = os.path.join(HERMES_DIR, dest, item)
            
            # 重名处理
            if os.path.exists(dest_path):
                base = Path(item).stem
                ext = Path(item).suffix
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(HERMES_DIR, dest, f"{base}-{counter}{ext}")
                    counter += 1

            moves += 1
            print(f"  ➡️ {'计划移动' if dry_run else '已移动'}: {item}")
            print(f"     目标: {dest}/")

            if not dry_run:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                try:
                    shutil.move(filepath, dest_path)
                except Exception as e:
                    print(f"     ❌ 错误: {e}")

    print(f"\n✅ 整理完成：移动 {moves} 个，跳过 {skipped} 个保护文件。")
    if dry_run and moves > 0:
        print("💡 使用 --apply 执行移动。")

if __name__ == '__main__':
    dry_run = '--apply' not in sys.argv
    organize(dry_run=dry_run)
