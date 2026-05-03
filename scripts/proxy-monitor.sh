#!/bin/bash
# ~/.hermes/scripts/proxy-monitor.sh
# 代理节点健康监控 + 自动告警
# 用法: bash ~/.hermes/scripts/proxy-monitor.sh

set -euo pipefail

PROXY_HOST="127.0.0.1"
PROXY_PORT="7890"
CONTROL_PORT="9090"
LOG_FILE="$HOME/.hermes/logs/proxy-monitor.log"
ALERT_SCRIPT="$HOME/.hermes/scripts/proxy-alert.sh"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

echo "🔍 === 代理节点健康监控 ==="
echo ""

# 1. 检查 mihomo 进程
log "检查 mihomo 进程..."
if pgrep -f "mihomo" > /dev/null 2>&1; then
    PID=$(pgrep -f "mihomo" | head -1)
    echo -e "✅ mihomo 运行中 (PID: $PID)"
    # 检查运行时间
    UPTIME=$(ps -o etime= -p $PID 2>/dev/null | xargs)
    echo "   运行时长: $UPTIME"
else
    echo -e "❌ mihomo 未运行!"
    log "ALERT: mihomo process not found"
    # 尝试重启
    if [ -f "$HOME/.config/mihomo/config.yaml" ]; then
        echo "   尝试重启 mihomo..."
        nohup mihomo -f "$HOME/.config/mihomo/config.yaml" > /tmp/mihomo.log 2>&1 &
        sleep 2
        if pgrep -f "mihomo" > /dev/null 2>&1; then
            echo -e "✅ mihomo 重启成功"
        else
            echo -e "❌ mihomo 重启失败! 检查 /tmp/mihomo.log"
        fi
    fi
fi

echo ""

# 2. 检查端口
log "检查端口状态..."
for port in "$PROXY_PORT" "$CONTROL_PORT"; do
    if ss -tlnp | grep -q ":${port} "; then
        echo -e "✅ 端口 $port: 监听中"
    else
        echo -e "❌ 端口 $port: 未监听!"
        log "ALERT: port $port not listening"
    fi
done

echo ""

# 3. 代理连通性测试
log "测试代理连通性..."
TEST_URLS=(
    "https://httpbin.org/ip"
    "https://api.github.com"
    "https://www.google.com"
)

PROXY_URL="http://${PROXY_HOST}:${PROXY_PORT}"

for url in "${TEST_URLS[@]}"; do
    DOMAIN=$(echo "$url" | sed 's|https\?://||' | cut -d'/' -f1)
    # 使用 curl 通过代理测试，5秒超时
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        --proxy "$PROXY_URL" \
        --connect-timeout 5 \
        --max-time 8 \
        "$url" 2>/dev/null || echo "000")
    
    if [ "$STATUS" = "200" ]; then
        echo -e "✅ $DOMAIN: 连通 (HTTP $STATUS)"
    elif [ "$STATUS" = "000" ]; then
        echo -e "❌ $DOMAIN: 连接失败 (超时或被拒)"
        log "ALERT: $DOMAIN unreachable via proxy"
    else
        echo -e "⚠️ $DOMAIN: 异常 (HTTP $STATUS)"
        log "WARN: $DOMAIN returned HTTP $STATUS"
    fi
done

echo ""

# 4. 延迟测试（对关键域名）
log "测试关键节点延迟..."
for url in "https://api.github.com" "https://httpbin.org/ip"; do
    DOMAIN=$(echo "$url" | sed 's|https\?://||' | cut -d'/' -f1)
    # 测量连接时间
    TIME_MS=$(curl -s -o /dev/null -w "%{time_connect}" \
        --proxy "$PROXY_URL" \
        --connect-timeout 5 \
        "$url" 2>/dev/null || echo "-1")
    
    if [ "$TIME_MS" != "-1" ] && [ "$TIME_MS" != "0.000000" ]; then
        TIME_MS_INT=$(echo "$TIME_MS * 1000" | bc 2>/dev/null | cut -d'.' -f1)
        if [ -n "$TIME_MS_INT" ] && [ "$TIME_MS_INT" -lt 500 ]; then
            echo -e "✅ $DOMAIN: ${TIME_MS_INT}ms (良好)"
        elif [ -n "$TIME_MS_INT" ] && [ "$TIME_MS_INT" -lt 1500 ]; then
            echo -e "⚠️ $DOMAIN: ${TIME_MS_INT}ms (偏慢)"
        elif [ -n "$TIME_MS_INT" ]; then
            echo -e "❌ $DOMAIN: ${TIME_MS_INT}ms (太慢!)"
        fi
    else
        echo -e "❌ $DOMAIN: 无法测量延迟"
    fi
done

echo ""

# 5. 代理配置检查
log "检查代理配置..."
CONFIG_FILE="$HOME/.config/mihomo/config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    SIZE=$(wc -c < "$CONFIG_FILE")
    echo -e "✅ 配置文件: $CONFIG_FILE ($SIZE bytes)"
    
    # 检查是否有节点配置
    if grep -q "proxies:" "$CONFIG_FILE" 2>/dev/null; then
        PROXY_COUNT=$(grep -c "- name:" "$CONFIG_FILE" 2>/dev/null || echo 0)
        echo "   节点数量: $PROXY_COUNT"
    else
        echo "   ⚠️ 未检测到 proxies 配置"
    fi
    
    # 检查端口配置
    if grep -q "mixed-port: 7890" "$CONFIG_FILE" 2>/dev/null; then
        echo "   混合端口: 7890 ✅"
    fi
else
    echo -e "❌ 配置文件不存在: $CONFIG_FILE"
    log "ALERT: mihomo config not found"
fi

echo ""

# 6. 环境变量检查
log "检查代理环境变量..."
for var in HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy; do
    val=$(eval echo \$$var 2>/dev/null || echo "")
    if [ -n "$val" ]; then
        echo "   $var=$val"
    fi
done
# 检查 .env 中的代理设置
if [ -f "$HOME/.hermes/.env" ]; then
    PROXY_SETTING=$(grep -i "PROXY\|proxy" "$HOME/.hermes/.env" 2>/dev/null | head -3)
    if [ -n "$PROXY_SETTING" ]; then
        echo "   .env 中的代理配置:"
        echo "$PROXY_SETTING" | sed 's/^/     /'
    fi
fi

echo ""
echo "=== ✅ 监控完成 ==="
log "Health check completed"
