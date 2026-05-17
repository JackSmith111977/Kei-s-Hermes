#!/usr/bin/env bash
# daily-audit.sh — 每日文件系统规范审计报告
# 被 cronjob 调用，检查过去 24 小时的审计日志并生成报告
# Usage: bash daily-audit.sh [--deliver]

set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
AUDIT_LOG="$HERMES_HOME/data/fs-audit/audit.log"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
YESTERDAY=$(date -u -d "24 hours ago" +"%Y-%m-%dT%H:%M:%SZ")
DELIVER="${1:-}"

REPORT=$(
python3 << 'PYEOF'
import json, os, sys
from datetime import datetime, timedelta, timezone

audit_log = os.path.expanduser("~/.hermes/data/fs-audit/audit.log")
now = datetime.now(timezone.utc)
yesterday = now - timedelta(hours=24)

total = 0
passed = 0
blocked = 0
warned = 0
violations = []

if os.path.exists(audit_log):
    with open(audit_log) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            ts_str = entry.get("ts", "")
            try:
                ts = datetime.fromisoformat(ts_str)
            except (ValueError, TypeError):
                continue
            
            if ts < yesterday:
                continue
            
            total += 1
            verdict = entry.get("verdict", "?")
            if verdict == "PASS":
                passed += 1
            elif verdict == "BLOCKED":
                blocked += 1
                violations.append(entry)
            elif verdict == "WARN":
                warned += 1
                violations.append(entry)

# 生成报告
lines = []
lines.append("📁 文件系统规范审计日报")
lines.append(f"  报告时间: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
lines.append(f"  统计周期: 过去 24 小时")
lines.append("")
lines.append(f"  总审计记录: {total}")
lines.append(f"  ✅ 通过:    {passed}")
lines.append(f"  🛑 拦截:    {blocked}")
lines.append(f"  ⚠️  警告:   {warned}")

if violations:
    lines.append("")
    lines.append(f"  违规明细 ({len(violations)} 项):")
    for v in violations:
        icon = "🛑" if v.get("verdict") == "BLOCKED" else "⚠️"
        lines.append(f"    {icon} [{v.get('ts','')[:19]}] {v.get('tool','?')}: {v.get('path','?')}")
        reason = v.get("reason", "")
        if reason:
            lines.append(f"       原因: {reason}")
else:
    lines.append("")
    lines.append("  🟢 今日文件系统状态良好，无违规记录！")

lines.append("")
lines.append("---")
lines.append("自动生成 by fs-enforce daily audit")

sys.stdout.write("\n".join(lines))
PYEOF
)

echo "$REPORT"

# 如果指定 --deliver 模式，输出适合 cronjob 的格式
if [ "$DELIVER" = "--deliver" ]; then
    # 如果有违规，输出报告内容（会被 cronjob 发送）
    if echo "$REPORT" | grep -q "违规明细"; then
        echo ""
        echo "[ALERT] 文件系统规范违规！请及时处理。"
    fi
fi
