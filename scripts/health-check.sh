#!/bin/bash
# Hermes Agent 一键健康检查
# 用法: bash ~/.hermes/scripts/health-check.sh

LOG=~/.hermes/logs/agent.log
ENV=~/.hermes/.env

echo "🔍 === Hermes Agent Health Check ==="
echo ""

# 1. 检查日志文件
echo "📋 1. 日志状态:"
if [ -f "$LOG" ]; then
  echo "   agent.log: $(wc -l < $LOG) 行, $(du -h $LOG | cut -f1)"
else
  echo "   ⚠️ agent.log: 不存在!"
fi
if [ -f "$ENV" ]; then
  echo "   .env: 存在"
else
  echo "   ⚠️ .env: 不存在!"
fi

# 2. 关键告警统计
echo ""
echo "🚨 2. 告警统计 (全部历史):"
COUNT_429=$(grep -c '429' "$LOG" 2>/dev/null || echo 0)
echo "   429 限流: $COUNT_429 次"
COUNT_FB=$(grep -c 'Fallback activated' "$LOG" 2>/dev/null || echo 0)
echo "   Fallback 触发: $COUNT_FB 次"
COUNT_401=$(grep -c '401\|Authentication Fails' "$LOG" 2>/dev/null || echo 0)
echo "   认证失败(401): $COUNT_401 次"
COUNT_AUX=$(grep -c 'no fallback available' "$LOG" 2>/dev/null || echo 0)
echo "   辅助模型无 fallback: $COUNT_AUX 次"
COUNT_WX=$(grep -c 'Weixin.*failed' "$LOG" 2>/dev/null || echo 0)
echo "   微信发送失败: $COUNT_WX 次"

# 3. 最近 10 条错误
echo ""
echo "📝 3. 最近 10 条错误:"
grep 'ERROR\|WARN' "$LOG" 2>/dev/null | tail -10 | while read line; do
  echo "   $line"
done

# 4. 环境变量检查
echo ""
echo "🔑 4. 关键环境变量:"
for key in QWENCODE_API_KEY CUSTOM_LONGCAT_API_KEY DEEPSEEK_API_KEY TAVILY_API_KEY FEISHU_APP_ID FEISHU_APP_SECRET; do
  val=$(grep "^${key}=" "$ENV" 2>/dev/null | cut -d= -f2)
  if [ -n "$val" ] && [ "$val" != "" ]; then
    echo "   ✅ $key: 已配置 (${val:0:4}****)"
  else
    # 也检查 shell 环境变量
    shell_val=$(eval echo \$$key 2>/dev/null)
    if [ -n "$shell_val" ]; then
      echo "   ✅ $key (shell): 已配置"
    else
      echo "   ❌ $key: 未配置!"
    fi
  fi
done

# 5. 进程状态
echo ""
echo "⚙️ 5. 进程状态:"
if pgrep -f "hermes" > /dev/null 2>&1; then
  echo "   ✅ Hermes 进程运行中:"
  pgrep -af "hermes" | head -3 | sed 's/^/      /'
else
  echo "   ⚠️ 无运行中的 Hermes 进程"
fi
if pgrep -f "mihomo" > /dev/null 2>&1; then
  echo "   ✅ mihomo 代理运行中"
else
  echo "   ⚠️ mihomo 代理未运行"
fi

# 6. 端口检查
echo ""
echo "🔌 6. 端口状态:"
for port in 7890 7899 9222 3456; do
  if ss -tlnp | grep -q ":${port} "; then
    echo "   ✅ 端口 $port: 监听中"
  else
    echo "   ⚠️ 端口 $port: 未监听"
  fi
done

# 7. Skill 统计
echo ""
echo "📚 7. Skill 统计:"
SKILL_COUNT=$(find ~/.hermes/skills -name 'SKILL.md' 2>/dev/null | wc -l)
echo "   已安装 skill: $SKILL_COUNT 个"

echo ""
echo "=== ✅ Check Complete ==="
