#!/usr/bin/env python3
"""
Cache Cleanup for Hermes Agent System
安全清理构建工具缓存

用法:
    python3 cache-cleanup.py --dry-run   # 预览（不执行）
    python3 cache-cleanup.py --apply     # 执行清理
    python3 cache-cleanup.py --report    # 仅报告缓存大小
"""

import os
import subprocess
import sys
from pathlib import Path


HOME = Path.home()


def fmt_size(bytes_val: int) -> str:
    """格式化字节大小为人类可读"""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if bytes_val < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}TB"


def get_dir_size(path: Path) -> int:
    """获取目录大小"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
    except (PermissionError, FileNotFoundError):
        pass
    return total


class CacheItem:
    """缓存项定义"""
    def __init__(self, name: str, path: Path, cleanup_cmd: str, 
                 risk: str = "low", description: str = ""):
        self.name = name
        self.path = path
        self.cleanup_cmd = cleanup_cmd
        self.risk = risk  # low / medium / high
        self.description = description

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def size(self) -> int:
        if not self.exists:
            return 0
        if self.path.is_dir():
            return get_dir_size(self.path)
        return self.path.stat().st_size

    @property
    def size_str(self) -> str:
        return fmt_size(self.size)


def get_cache_items() -> list[CacheItem]:
    """获取所有缓存项"""
    return [
        CacheItem(
            "pip cache", HOME / ".cache" / "pip",
            "pip cache purge",
            risk="low",
            description="Python 包下载缓存，清理后 pip install 会重新下载"
        ),
        CacheItem(
            "npm cache", HOME / ".npm",
            "npm cache clean --force",
            risk="low",
            description="Node.js 包缓存，清理后 npm install 会重新下载"
        ),
        CacheItem(
            "uv cache", HOME / ".cache" / "uv",
            "uv cache clean",
            risk="low",
            description="uv 包管理器缓存，清理后 uv add 会重新下载"
        ),
        CacheItem(
            "pip cache (local)", HOME / ".local" / "share" / "pip",
            "rm -rf ~/.local/share/pip/cache",
            risk="low",
            description="本地 pip 共享缓存"
        ),
        CacheItem(
            "matplotlib cache", HOME / ".cache" / "matplotlib",
            "rm -rf ~/.cache/matplotlib",
            risk="low",
            description="matplotlib 字体/配置缓存"
        ),
        CacheItem(
            "pip thumbnails", HOME / ".cache" / "thumbnails",
            "rm -rf ~/.cache/thumbnails/*",
            risk="low",
            description="缩略图缓存"
        ),
        CacheItem(
            "hermes-agent old version", HOME / ".hermes" / "hermes-agent_old_v0.10.0",
            "rm -rf ~/.hermes/hermes-agent_old_v0.10.0",
            risk="medium",
            description="旧版 Hermes Agent 备份（确认新版运行正常后清理）"
        ),
    ]


def run_cmd(cmd: str, dry_run: bool = True) -> str:
    """执行命令（dry-run 模式只打印不执行）"""
    if dry_run:
        return f"[DRY-RUN] $ {cmd}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return f"✅ {result.stdout.strip() or '成功'}"
        else:
            return f"⚠️ 错误: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "⏰ 超时"
    except Exception as e:
        return f"❌ 失败: {e}"


def report_only():
    """仅报告缓存大小"""
    print("=" * 60)
    print("📊 Hermes 缓存大小报告")
    print("=" * 60)

    total = 0
    items = get_cache_items()
    for item in items:
        if item.exists and item.size > 0:
            print(f"  {item.name:30s} {item.size_str:>8s}  [{item.risk}] {item.description}")
            total += item.size
        else:
            print(f"  {item.name:30s} {'N/A':>8s}  [{item.risk}] (不存在)")

    print("-" * 60)
    print(f"  {'总计':30s} {fmt_size(total):>8s}")
    print()


def cleanup(dry_run: bool = True):
    """执行清理"""
    if dry_run:
        print("🔍 预览模式 — 不会删除任何文件\n")
    else:
        print("🧹 执行清理模式\n")

    items = get_cache_items()
    total_freed = 0

    for item in items:
        if not item.exists:
            continue

        size = item.size
        if size == 0:
            continue

        total_freed += size
        action = "🔍 发现" if dry_run else "🧹 清理"
        print(f"  {action}: {item.name} ({fmt_size(size)})")
        print(f"    命令: {item.cleanup_cmd}")
        
        if not dry_run:
            # 风险中等以上需要确认
            if item.risk == "medium":
                print(f"     ⚠️  风险等级: {item.risk} — 已跳过（需要手动确认）")
                print(f"     请手动运行: {item.cleanup_cmd}")
                continue

            result = run_cmd(item.cleanup_cmd, dry_run=False)
            print(f"    结果: {result}")
        
        print()

    total_freed_str = fmt_size(total_freed)

    if dry_run:
        print(f"\n💡 可释放空间: {total_freed_str}")
        print(f"   使用 --apply 执行清理")
    else:
        print(f"\n✅ 清理完成！释放空间: {total_freed_str}")
        print(f"   如需清理高风险项目，请手动运行对应命令")


def main():
    if '--apply' in sys.argv and '--dry-run' in sys.argv:
        print("❌ 不能同时使用 --apply 和 --dry-run")
        sys.exit(1)

    if '--report' in sys.argv:
        report_only()
        return

    dry_run = '--apply' not in sys.argv
    cleanup(dry_run=dry_run)


if __name__ == '__main__':
    main()
