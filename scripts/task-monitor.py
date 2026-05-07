#!/usr/bin/env python3
"""
Hermes 长任务监控脚本
检查运行中的 Hermes 后台进程，生成状态报告
配合 cron 定时执行，通过飞书卡片推送状态
"""

import json
import os
import subprocess
import sys
from datetime import datetime


def get_hermes_processes():
    """获取所有 Hermes 相关进程信息"""
    try:
        result = subprocess.run(
            ["pgrep", "-af", "hermes"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        processes = []
        for line in lines:
            parts = line.strip().split(None, 1)
            if len(parts) >= 2:
                pid, cmd = parts[0], parts[1]
                try:
                    # Get process uptime
                    with open(f"/proc/{pid}/stat") as f:
                        stat_parts = f.read().split()
                        start_ticks = int(stat_parts[21])
                    clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
                    uptime_seconds = os.times()[4] - (start_ticks / clock_ticks)
                except (OSError, ValueError, IndexError):
                    uptime_seconds = 0

                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)

                processes.append({
                    "pid": pid,
                    "cmd": cmd[:100],
                    "uptime": f"{hours}h{minutes:02d}m",
                    "uptime_seconds": int(uptime_seconds),
                })
        return processes
    except subprocess.TimeoutExpired:
        return []
    except FileNotFoundError:
        return []


def get_log_stats():
    """获取最近日志统计"""
    log_path = os.path.expanduser("~/.hermes/logs/agent.log")
    if not os.path.exists(log_path):
        return {}

    try:
        result = subprocess.run(
            ["tail", "-1000", log_path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        recent_logs = result.stdout

        return {
            "error_count": recent_logs.count("ERROR"),
            "warn_count": recent_logs.count("WARN"),
            "total_lines": int(
                subprocess.run(
                    ["wc", "-l", log_path], capture_output=True, text=True, timeout=5
                ).stdout.split()[0]
            ),
            "last_error": _get_last(recent_logs, "ERROR"),
        }
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        return {}


def _get_last(text, keyword):
    """Get the last line containing keyword"""
    for line in text.split("\n")[::-1]:
        if keyword in line:
            return line.strip()[:150]
    return None


def get_cron_status():
    """获取 cron 任务状态（通过 hermes cron 命令）"""
    try:
        result = subprocess.run(
            ["hermes", "cron", "list"],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PATH": os.environ.get("PATH", "")},
        )
        return result.stdout.strip()[:500] if result.stdout.strip() else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def get_resource_usage():
    """获取系统资源使用情况"""
    try:
        cpu = subprocess.run(
            ["uptime"], capture_output=True, text=True, timeout=5
        ).stdout.strip()
        mem = subprocess.run(
            ["free", "-h"], capture_output=True, text=True, timeout=5
        ).stdout.strip().split("\n")[1] if os.path.exists("/usr/bin/free") else ""
        disk = subprocess.run(
            ["df", "-h", os.path.expanduser("~")], capture_output=True, text=True, timeout=5
        ).stdout.strip().split("\n")[1] if os.path.exists("/usr/bin/df") else ""
        return {"cpu": cpu, "mem": mem, "disk": disk}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {}


def generate_card_report(processes, log_stats, resources, cron_status):
    """生成飞书进度卡片格式的报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build status report
    lines = [f"## 📊 Hermes 系统状态报告", f"", f"**时间**: 🕐 {now}", f""]

    # Process section
    if processes:
        lines.append(f"### ⚙️ 运行中的进程 ({len(processes)} 个)")
        lines.append(f"")
        for p in processes:
            lines.append(f"- PID {p['pid']} | 运行 {p['uptime']}")
            lines.append(f"  `{p['cmd'][:120]}`")
        lines.append(f"")
    else:
        lines.append(f"### ⚙️ 运行中的进程")
        lines.append(f"没有运行中的 Hermes 进程喵～")
        lines.append(f"")

    # Log stats
    if log_stats:
        errs = log_stats.get("error_count", 0)
        warns = log_stats.get("warn_count", 0)
        status_icon = "✅" if errs == 0 else ("⚠️" if errs < 3 else "❌")
        lines.append(f"### {status_icon} 日志状态 (最近 1000 行)")
        lines.append(f"")
        lines.append(f"- 错误: {errs} 次")
        lines.append(f"- 警告: {warns} 次")
        lines.append(f"- 总行数: {log_stats.get('total_lines', '?')}")
        if log_stats.get("last_error"):
            last_err = log_stats["last_error"]
            lines.append(f"- 最近错误: `{last_err[:120]}`")
        lines.append(f"")

    # Resource usage
    if resources:
        lines.append(f"### 💻 系统资源")
        lines.append(f"")
        lines.append(f"- CPU: {resources.get('cpu', 'N/A')}")
        if resources.get("mem"):
            lines.append(f"- 内存: {resources['mem']}")
        if resources.get("disk"):
            lines.append(f"- 磁盘: {resources['disk']}")
        lines.append(f"")

    # Cron status
    if cron_status:
        lines.append(f"### ⏰ 定时任务")
        lines.append(f"")
        lines.append(f"```")
        lines.append(cron_status[:400])
        lines.append(f"```")
        lines.append(f"")

    return "\n".join(lines)


def main():
    processes = get_hermes_processes()
    log_stats = get_log_stats()
    resources = get_resource_usage()
    cron_status = get_cron_status()

    report = generate_card_report(processes, log_stats, resources, cron_status)

    # Output with card type hint for the gateway
    print(f"<!-- card:dashboard -->")
    print(report)


if __name__ == "__main__":
    main()
