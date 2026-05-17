#!/usr/bin/env python3
"""
File Health Check for Hermes Agent System
检测文件系统的健康问题，生成整理建议报告

用法:
    python3 file-health-check.py
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERMES_DIR = os.path.expanduser('~/.hermes')

# 健康规则
EXPECTED_ROOT_DIRS = {
    'config', 'skills', 'scripts', 'output', 'archive',
    'cron', 'logs', 'cache', 'learning'
}

EXPECTED_ROOT_FILES = {
    'SOUL.md', 'MEMORY.md', 'FILE_INDEX.md', 'FILE_INDEX.json',
    'config.yaml', '.gitignore',
    # 运行时状态文件（软链接到 state/ data/ cache/）—— 用 os.path.exists 自动追踪
    'learning_state.json', 'channel_directory.json',
    'state.db', 'state.db-wal', 'state.db-shm',
    'gateway.pid', 'gateway_state.json',
    'feishu_seen_message_ids.json', 'processes.json',
    'models_dev_cache.json',
    'auth.json', 'auth.lock',
}

# 文件类型
OUTPUT_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.html', '.htm'}
SCRIPT_EXTENSIONS = {'.py', '.sh'}
ARCHIVE_KEYWORDS = ['_v', '_v2', '_v3', '_v4', '_v5', '_backup', '_old', '_temp', '_copy']


def check_root_clutter():
    """检查根目录散乱文件"""
    issues = []
    files_in_root = os.listdir(HERMES_DIR)

    for item in files_in_root:
        if item.startswith('.'):
            continue
        if item in EXPECTED_ROOT_FILES:
            continue
        if item in EXPECTED_ROOT_DIRS and os.path.isdir(os.path.join(HERMES_DIR, item)):
            continue

        filepath = os.path.join(HERMES_DIR, item)
        if os.path.isfile(filepath):
            ext = Path(item).suffix.lower()
            if ext in OUTPUT_EXTENSIONS:
                issues.append({
                    'type': 'warning',
                    'message': f"输出文件在根目录: {item}",
                    'suggestion': f"移动到 output/ 对应子目录"
                })
            elif ext in SCRIPT_EXTENSIONS:
                issues.append({
                    'type': 'warning',
                    'message': f"脚本文件在根目录: {item}",
                    'suggestion': f"移动到 scripts/"
                })
            elif any(kw in item.lower() for kw in ARCHIVE_KEYWORDS):
                issues.append({
                    'type': 'info',
                    'message': f"中间产物在根目录: {item}",
                    'suggestion': f"移动到 archive/ 或删除"
                })
            else:
                issues.append({
                    'type': 'info',
                    'message': f"未知文件在根目录: {item}",
                    'suggestion': f"检查是否应该保留"
                })

    return issues


def check_missing_dirs():
    """检查缺失的目录"""
    issues = []
    for dir_name in EXPECTED_ROOT_DIRS:
        dir_path = os.path.join(HERMES_DIR, dir_name)
        if not os.path.exists(dir_path):
            issues.append({
                'type': 'warning',
                'message': f"缺失目录: {dir_name}/",
                'suggestion': f"运行 mkdir -p ~/.hermes/{dir_name} 创建"
            })
    return issues


def check_missing_files():
    """检查缺失的重要文件"""
    issues = []
    for file_name in EXPECTED_ROOT_FILES:
        file_path = os.path.join(HERMES_DIR, file_name)
        # MEMORY.md 和 FILE_INDEX.md 可能还不存在
        if file_name in ('MEMORY.md', 'FILE_INDEX.md', 'FILE_INDEX.json'):
            continue
        if not os.path.exists(file_path):
            issues.append({
                'type': 'warning',
                'message': f"缺失重要文件: {file_name}",
                'suggestion': f"检查是否被意外删除"
            })
    return issues


def check_output_structure():
    """检查 output 目录结构"""
    issues = []
    output_dir = os.path.join(HERMES_DIR, 'output')
    if not os.path.exists(output_dir):
        return issues

    expected_subdirs = {'pdf', 'images', 'html', 'documents'}
    actual_subdirs = set()

    for item in os.listdir(output_dir):
        if os.path.isdir(os.path.join(output_dir, item)):
            actual_subdirs.add(item)

    missing = expected_subdirs - actual_subdirs
    if missing:
        issues.append({
            'type': 'info',
            'message': f"output/ 缺失子目录: {', '.join(missing)}",
            'suggestion': f"运行 mkdir -p ~/.hermes/output/{{{','.join(missing)}}}"
        })

    return issues


def check_file_count():
    """检查文件数量"""
    issues = []
    total_files = 0
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(HERMES_DIR):
        # 排除目录
        dirnames[:] = [d for d in dirnames if d not in {'__pycache__', '.git', 'node_modules', 'cache', '.cache'}]
        total_files += len(filenames)
        for f in filenames:
            try:
                total_size += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass

    if total_files > 50000:
        issues.append({
            'type': 'warning',
            'message': f"文件数量过多: {total_files} 个",
            'suggestion': f"检查 node_modules/ 和 cache/ 是否需要清理"
        })

    size_mb = total_size / 1024 / 1024
    issues.append({
        'type': 'info',
        'message': f"总文件数: {total_files}，总大小: {size_mb:.1f} MB",
        'suggestion': None
    })

    return issues


def run_health_check():
    """运行所有检查"""
    print(f"🏥 Hermes 文件系统健康检查")
    print(f"📁 目录: {HERMES_DIR}")
    print(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    all_issues = []

    print("\n🔍 检查根目录散乱文件...")
    issues = check_root_clutter()
    all_issues.extend(issues)
    print(f"  找到 {len(issues)} 个问题")

    print("\n🔍 检查缺失目录...")
    issues = check_missing_dirs()
    all_issues.extend(issues)
    print(f"  找到 {len(issues)} 个问题")

    print("\n🔍 检查缺失重要文件...")
    issues = check_missing_files()
    all_issues.extend(issues)
    print(f"  找到 {len(issues)} 个问题")

    print("\n🔍 检查 output 目录结构...")
    issues = check_output_structure()
    all_issues.extend(issues)
    print(f"  找到 {len(issues)} 个问题")

    print("\n🔍 检查文件统计...")
    issues = check_file_count()
    all_issues.extend(issues)
    print(f"  完成")

    # 打印报告
    print("\n" + "=" * 50)
    print("📋 检查报告")
    print("=" * 50)

    warnings = [i for i in all_issues if i['type'] == 'warning']
    infos = [i for i in all_issues if i['type'] == 'info']

    if warnings:
        print(f"\n⚠️  警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  • {w['message']}")
            if w.get('suggestion'):
                print(f"    建议: {w['suggestion']}")

    if infos:
        print(f"\nℹ️  信息 ({len(infos)}):")
        for i in infos:
            print(f"  • {i['message']}")
            if i.get('suggestion'):
                print(f"    建议: {i['suggestion']}")

    if not warnings:
        print("\n✅ 文件系统状态良好！")

    print(f"\n{'=' * 50}")
    print(f"总计: {len(warnings)} 个警告, {len(infos)} 条信息")

    if warnings:
        print(f"\n💡 建议运行: python3 ~/.hermes/skills/file-system-manager/scripts/file-organize.py --dry-run")


def main():
    if not os.path.isdir(HERMES_DIR):
        print(f"❌ Hermes 目录不存在: {HERMES_DIR}")
        sys.exit(1)

    run_health_check()


if __name__ == '__main__':
    main()
