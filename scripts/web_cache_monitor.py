#!/usr/bin/env python3
"""
Web Cache Monitor Script

监控缓存状态、命中率、节省的 API 调用次数。
可以定时运行（cron）或手动调用。

用法：
    python ~/.hermes/scripts/web_cache_monitor.py
    python ~/.hermes/scripts/web_cache_monitor.py --cleanup  # 同时清理过期缓存
    python ~/.hermes/scripts/web_cache_monitor.py --report   # 生成详细报告
"""

import argparse
import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 缓存数据库路径
CACHE_DB_PATH = Path.home() / ".hermes" / "cache" / "web" / "request_cache.db"


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    if not CACHE_DB_PATH.exists():
        return {
            "status": "not_initialized",
            "message": "缓存数据库不存在，请先调用 web 工具创建缓存",
        }
    
    conn = sqlite3.connect(str(CACHE_DB_PATH))
    cursor = conn.cursor()
    
    # 总条目数
    cursor.execute("SELECT COUNT(*) FROM response_cache")
    total_entries = cursor.fetchone()[0]
    
    # 活跃条目数（未过期）
    current_time = int(time.time())
    cursor.execute("SELECT COUNT(*) FROM response_cache WHERE expires_at > ?", (current_time,))
    active_entries = cursor.fetchone()[0]
    
    # 过期条目数
    expired_entries = total_entries - active_entries
    
    # 按工具统计
    cursor.execute("""
        SELECT tool_name, COUNT(*), SUM(hit_count) 
        FROM response_cache 
        WHERE expires_at > ?
        GROUP BY tool_name
    """, (current_time,))
    
    tool_stats = {}
    total_hits = 0
    for row in cursor.fetchall():
        tool_name, count, hits = row
        tool_stats[tool_name] = {
            "entries": count,
            "hits": hits or 0,
        }
        total_hits += hits or 0
    
    # 计算节省的 API 调用次数（基于 hit_count）
    saved_calls = total_hits
    
    # 预估节省的成本（假设每次 API 调用成本 $0.01）
    # 实际成本因工具而异：Tavily ~$0.005/次，Brave ~$0.003/次
    estimated_cost_saved = saved_calls * 0.005  # 取 Tavily 的平均成本
    
    conn.close()
    
    return {
        "status": "ok",
        "total_entries": total_entries,
        "active_entries": active_entries,
        "expired_entries": expired_entries,
        "total_hits": total_hits,
        "saved_api_calls": saved_calls,
        "estimated_cost_saved_usd": round(estimated_cost_saved, 4),
        "tool_stats": tool_stats,
        "last_updated": datetime.now().isoformat(),
    }


def cleanup_expired() -> int:
    """清理过期缓存条目"""
    if not CACHE_DB_PATH.exists():
        return 0
    
    conn = sqlite3.connect(str(CACHE_DB_PATH))
    cursor = conn.cursor()
    
    current_time = int(time.time())
    cursor.execute("DELETE FROM response_cache WHERE expires_at < ?", (current_time,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted


def generate_report(stats: Dict[str, Any]) -> str:
    """生成详细报告"""
    if stats["status"] == "not_initialized":
        return f"⚠️  缓存状态：{stats['message']}"
    
    report = []
    report.append("=" * 50)
    report.append("Web Cache Monitor Report")
    report.append("=" * 50)
    report.append(f"📅 时间：{stats['last_updated']}")
    report.append("")
    
    report.append("📊 总体统计：")
    report.append(f"  ├─ 总条目数：{stats['total_entries']}")
    report.append(f"  ├─ 活跃条目：{stats['active_entries']}")
    report.append(f"  ├─ 过期条目：{stats['expired_entries']}")
    report.append(f"  ├─ 总命中次数：{stats['total_hits']}")
    report.append(f"  └─ 节省 API 调用：{stats['saved_api_calls']}")
    report.append("")
    
    report.append("💰 成本节省：")
    report.append(f"  └─ 预估节省：${stats['estimated_cost_saved_usd']}")
    report.append("")
    
    if stats["tool_stats"]:
        report.append("🔧 按工具统计：")
        for tool_name, tool_data in stats["tool_stats"].items():
            report.append(f"  ├─ {tool_name}")
            report.append(f"  │  ├─ 条目数：{tool_data['entries']}")
            report.append(f"  │  └─ 命中次数：{tool_data['hits']}")
        report.append("")
    
    report.append("=" * 50)
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Web Cache Monitor")
    parser.add_argument("--cleanup", action="store_true", help="清理过期缓存")
    parser.add_argument("--report", action="store_true", help="生成详细报告")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    
    args = parser.parse_args()
    
    # 清理过期缓存
    if args.cleanup:
        deleted = cleanup_expired()
        print(f"🧹 清理了 {deleted} 个过期缓存条目")
    
    # 获取统计
    stats = get_cache_stats()
    
    # 输出
    if args.json:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    elif args.report:
        print(generate_report(stats))
    else:
        # 简洁输出
        if stats["status"] == "not_initialized":
            print(f"⚠️  {stats['message']}")
        else:
            print(f"✅ 缓存状态：活跃 {stats['active_entries']} 条，过期 {stats['expired_entries']} 条")
            print(f"📊 命中次数：{stats['total_hits']}，节省 API 调用：{stats['saved_api_calls']}")
            print(f"💰 预估节省成本：${stats['estimated_cost_saved_usd']}")


if __name__ == "__main__":
    main()