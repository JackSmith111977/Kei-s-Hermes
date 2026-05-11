#!/bin/bash
# web-access 环境启动脚本
# 用法: bash start-web-access.sh

set -e

SKILL_DIR="$HOME/.hermes/skills/web-access"
DISPLAY_NUM=":99"
CHROME_DEBUG_PORT=9222
PROXY_PORT=3456

echo "🐱 [web-access] 启动 Chrome + CDP Proxy 环境..."

# 1. 启动 Xvfb 虚拟显示
if ! pgrep -f "Xvfb $DISPLAY_NUM" > /dev/null 2>&1; then
    Xvfb $DISPLAY_NUM -screen 0 1280x1024x24 -ac &
    echo "  ✅ Xvfb 启动 (DISPLAY=$DISPLAY_NUM)"
else
    echo "  ✅ Xvfb 已在运行"
fi

sleep 2

# 2. 启动 Chrome Remote Debugging
if ! curl -s http://127.0.0.1:$CHROME_DEBUG_PORT/json/version > /dev/null 2>&1; then
    DISPLAY=$DISPLAY_NUM google-chrome \
        --no-first-run \
        --no-default-browser-check \
        --disable-gpu \
        --remote-debugging-port=$CHROME_DEBUG_PORT \
        --remote-debugging-address=127.0.0.1 \
        --disable-dev-shm-usage \
        --headless=new \
        --disable-extensions \
        --disable-background-networking \
        --user-data-dir=/tmp/chrome-debug \
        about:blank > /dev/null 2>&1 &
    sleep 3
    echo "  ✅ Chrome 启动 (port $CHROME_DEBUG_PORT)"
else
    echo "  ✅ Chrome 已在运行"
fi

# 3. 验证 Chrome 连接
if curl -s http://127.0.0.1:$CHROME_DEBUG_PORT/json/version > /dev/null 2>&1; then
    echo "  ✅ Chrome Remote Debugging 连接正常"
else
    echo "  ❌ Chrome 连接失败"
    exit 1
fi

# 4. 启动 CDP Proxy
if ! curl -s http://127.0.0.1:$PROXY_PORT/targets > /dev/null 2>&1; then
    echo "  ⏳ 启动 CDP Proxy..."
    node "$SKILL_DIR/scripts/check-deps.mjs"
    echo "  ✅ CDP Proxy 启动 (port $PROXY_PORT)"
else
    echo "  ✅ CDP Proxy 已在运行"
fi

echo ""
echo "🎉 web-access 环境就绪！"
echo "   Chrome:    http://127.0.0.1:$CHROME_DEBUG_PORT"
echo "   Proxy:     http://127.0.0.1:$PROXY_PORT"
echo "   Skill Dir: $SKILL_DIR"
