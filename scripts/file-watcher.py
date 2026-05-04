#!/usr/bin/env python3 -u
"""
Hermes File Watcher Daemon (v2.1)
Real-time file governance based on governance.yaml rules.

Usage:
    python3 -u file-watcher.py [--config governance.yaml]
"""

import os
import sys
import time
import yaml
import re
import shutil
import logging
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置日志 - 强制 flush
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
    force=True
)
logging.getLogger().handlers[0].flush = sys.stdout.flush
logger = logging.getLogger("HermesWatcher")

HERMES_DIR = os.path.expanduser("~/.hermes")
CONFIG_PATH = os.path.join(HERMES_DIR, "governance.yaml")
LOCK_FILE = os.path.join(HERMES_DIR, ".hermes_watcher.lock")

# 根目录必须保留的文件（无论规则如何匹配，都不移动）
ROOT_KEEP_LIST = {
    "SOUL.md", "MEMORY.md", "FILE_INDEX.md", "FILE_INDEX.json",
    "TASK_QUEUE.md", ".env", ".gitignore",
    "config.yaml", "learning_state.json",
    "auth.json", "auth.lock", "state.db", "state.db-wal", "state.db-shm",
    "gateway.pid", "gateway_state.json", "channel_directory.json",
    "feishu_seen_message_ids.json", "processes.json", "models_dev_cache.json",
    "governance.yaml",
    # 根目录文档（保留）
    "hackathon_report.md", "hackathon_report_final.md", "hackathon_report_part1.md",
    "pdf_design_plan.md"
}


def load_config(config_path):
    """加载治理配置"""
    if not os.path.exists(config_path):
        logger.error(f"配置文件不存在：{config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            config = yaml.safe_load(f)
            logger.info(f"已加载配置：{len(config.get('rules', []))} 条规则，{len(config.get('policies', []))} 个策略")
            return config
        except yaml.YAMLError as e:
            logger.error(f"配置文件格式错误：{e}")
            sys.exit(1)


def match_rule(filename, rules):
    """
    匹配文件到规则。
    返回匹配的规则，如果没有匹配则返回 None。
    """
    ext = Path(filename).suffix.lower()

    for rule in rules:
        # 检查规则是否启用
        if rule.get('enabled') is False:
            continue

        filter_conf = rule.get('filter', {})
        action = rule.get('action')

        # 1. 检查类型匹配
        allowed_types = filter_conf.get('types', [])
        if allowed_types and allowed_types != ["*"]:
            if ext not in [t.lower() for t in allowed_types]:
                continue  # 类型不匹配

        # 2. 检查正则匹配
        name_regex = filter_conf.get('name_regex')
        if name_regex:
            if not re.match(name_regex, filename):
                continue  # 正则不匹配

        # 规则匹配成功
        logger.debug(f"文件 {filename} 匹配规则：{rule['name']}")
        return action

    return None


def execute_action(filepath, action, config):
    """执行规则动作"""
    if not action:
        return False

    action_type = action.get('type', 'move')
    destination = action.get('destination')

    if not destination:
        logger.warning(f"规则缺少 destination 配置")
        return False

    # 处理目标路径
    dest_dir = os.path.join(HERMES_DIR, destination)
    dest_path = os.path.join(dest_dir, os.path.basename(filepath))

    # 如果目标文件已存在，添加后缀避免覆盖
    if os.path.exists(dest_path):
        base = Path(dest_path).stem
        ext = Path(dest_path).suffix
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_dir, f"{base}-{counter}{ext}")
            counter += 1
        dest_dir = os.path.dirname(dest_path)

    # 确保目录存在
    os.makedirs(dest_dir, exist_ok=True)

    try:
        if action_type == 'move':
            # 稍微等待一下，确保文件写入完成
            time.sleep(0.5)
            shutil.move(filepath, dest_path)
            logger.info(f"✅ 移动：{os.path.basename(filepath)} → {destination}/")
            return True
        elif action_type == 'copy':
            shutil.copy2(filepath, dest_path)
            logger.info(f"📋 复制：{os.path.basename(filepath)} → {destination}/")
            return True
        elif action_type == 'delete':
            os.remove(filepath)
            logger.info(f"🗑️ 删除：{os.path.basename(filepath)}")
            return True
    except Exception as e:
        logger.error(f"❌ 执行动作失败：{e}")
        return False

    return False


class HermesFileHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.rules = config.get('rules', [])
        self.ignore_dirs = set(config.get('watcher', {}).get('ignore_directories', []))
        self.ignore_patterns = config.get('watcher', {}).get('ignore_patterns', [])
        
        # Debounce 机制
        self._timers = {}
        self._lock = threading.Lock()

    def _process_file(self, filepath, filename):
        """实际执行文件处理的逻辑"""
        # 1. 检查保护列表
        if filename in ROOT_KEEP_LIST:
            logger.debug(f"🔒 保护文件不移动：{filename}")
            return

        # 2. 匹配规则
        action = match_rule(filename, self.rules)
        if action:
            execute_action(filepath, action, self.config)
        else:
            logger.debug(f"🤷 未匹配任何规则：{filename}")

    def _debounce(self, filepath, filename):
        """防抖逻辑：等待文件不再变化后再处理"""
        with self._lock:
            # 取消之前的定时器
            if filepath in self._timers:
                self._timers[filepath].cancel()
            
            # 设置新的定时器（延迟 2 秒）
            timer = threading.Timer(2.0, self._process_file, args=[filepath, filename])
            self._timers[filepath] = timer
            timer.start()

    def on_created(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        
        # 忽略模式
        for pattern in self.ignore_patterns:
            if re.match(pattern, filename):
                return
        
        self._debounce(event.src_path, filename)

    def on_modified(self, event):
        # 修改事件也触发防抖，确保文件写完
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        
        # 忽略模式
        for pattern in self.ignore_patterns:
            if re.match(pattern, filename):
                return

        self._debounce(event.src_path, filename)

    def on_moved(self, event):
        self.on_created(event)


def start_watcher():
    """启动文件监听守护进程"""
    logger.info("=" * 50)
    logger.info("🚀 Hermes 文件治理守护者已启动")
    logger.info(f"📁 监控目录：{HERMES_DIR}")
    logger.info(f"📄 配置文件：{CONFIG_PATH}")
    logger.info("=" * 50)

    # 创建锁文件
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

    config = load_config(CONFIG_PATH)
    event_handler = HermesFileHandler(config)

    observer = Observer()
    # 只监控根目录，不递归（避免监控子目录内部变化）
    observer.schedule(event_handler, HERMES_DIR, recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 收到停止信号，正在关闭...")
        observer.stop()
    except Exception as e:
        logger.error(f"💥 运行异常：{e}")
        observer.stop()

    observer.join()

    # 清理锁文件
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    logger.info("👋 守护者已停止")


if __name__ == "__main__":
    start_watcher()
