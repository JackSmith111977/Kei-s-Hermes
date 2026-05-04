#!/usr/bin/env python3
"""
Hermes Single File Organizer
处理单个文件的治理规则匹配和执行。

Usage:
    python3 file-organize-single.py <filepath>
"""

import os
import sys
import yaml
import re
import shutil
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [SINGLE] %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger()

HERMES_DIR = os.path.expanduser("~/.hermes")
CONFIG_PATH = os.path.join(HERMES_DIR, "governance.yaml")

# 根目录保护列表
ROOT_KEEP_LIST = {
    "SOUL.md", "MEMORY.md", "FILE_INDEX.md", "FILE_INDEX.json",
    "TASK_QUEUE.md", ".env", ".gitignore", "config.yaml", "learning_state.json",
    "auth.json", "auth.lock", "state.db", "state.db-wal", "state.db-shm",
    "gateway.pid", "gateway_state.json", "channel_directory.json",
    "feishu_seen_message_ids.json", "processes.json", "models_dev_cache.json",
    "governance.yaml",
    "hackathon_report.md", "hackathon_report_final.md", "hackathon_report_part1.md",
    "pdf_design_plan.md",
    "AGENTS.md", "agents.md", "CLAUDE.md", "claude.md", ".hermes.md", "HERMES.md" # Critical config files
}

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def match_rule(filename, rules):
    ext = Path(filename).suffix.lower()
    for rule in rules:
        if rule.get('enabled') is False:
            continue
        
        filter_conf = rule.get('filter', {})
        allowed_types = filter_conf.get('types', [])
        if allowed_types and allowed_types != ["*"]:
            if ext not in [t.lower() for t in allowed_types]:
                continue
        
        name_regex = filter_conf.get('name_regex')
        if name_regex:
            if not re.match(name_regex, filename):
                continue
                
        return rule.get('action')
    return None

def main():
    if len(sys.argv) < 2:
        logger.error("用法: python3 file-organize-single.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    filename = os.path.basename(filepath)

    # 检查保护
    if filename in ROOT_KEEP_LIST:
        return # 静默跳过

    config = load_config()
    rules = config.get('rules', [])
    action = match_rule(filename, rules)

    if action:
        dest = action.get('destination')
        dest_dir = os.path.join(HERMES_DIR, dest)
        dest_path = os.path.join(dest_dir, filename)

        # 重名处理
        if os.path.exists(dest_path):
            base = Path(filename).stem
            ext = Path(filename).suffix
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_dir, f"{base}-{counter}{ext}")
                counter += 1
            dest_dir = os.path.dirname(dest_path)

        try:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(filepath, dest_path)
            logger.info(f"✅ 移动: {filename} → {dest}/")
        except Exception as e:
            logger.error(f"❌ 移动失败: {filename} - {e}")
    else:
        logger.debug(f"🤷 未匹配: {filename}")

if __name__ == '__main__':
    main()
