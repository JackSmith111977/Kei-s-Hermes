#!/bin/bash
# =============================================================================
# Hermes Catgirl Deploy - 安全上传脚本
# =============================================================================
# 此脚本将指定的安全文件上传到 GitHub 仓库
# 自动排除所有敏感信息和运行时数据
# =============================================================================

set -e

DEPLOY_DIR="/tmp/hermes-catgirl-deploy"
HERMES_DIR="$HOME/.hermes"
PROXY_HOST="127.0.0.1"
PROXY_PORT="7890"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Hermes Catgirl Deploy 上传脚本 ===${NC}"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 检查部署目录
if [ ! -d "$DEPLOY_DIR" ]; then
    echo -e "${RED}错误：部署目录不存在: $DEPLOY_DIR${NC}"
    exit 1
fi

cd "$DEPLOY_DIR"

# 初始化 git 仓库（如果尚未初始化）
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}初始化 git 仓库...${NC}"
    git init
    git config user.email "hermes-catgirl@local"
    git config user.name "小喵"
fi

# 从安全文件读取部署 token（仅 root 可读，权限 600）
TOKEN_FILE="$HOME/.hermes/.deploy_token"
if [ -f "$TOKEN_FILE" ]; then
    GITHUB_TOKEN=$(cat "$TOKEN_FILE" | tr -d ' \n\r')
else
    GITHUB_TOKEN=""
fi

# 获取当前 remote origin URL，并剥离可能存在的 token
REMOTE_BASE=$(git remote get-url origin 2>/dev/null || echo "")
if echo "$REMOTE_BASE" | grep -q '@'; then
    # 如果 URL 中包含 @，说明可能嵌入了认证信息，只保留协议+域名+路径部分
    CLEAN_URL=$(echo "$REMOTE_BASE" | sed -E 's|https?://[^@]*@|https://|')
    git remote set-url origin "$CLEAN_URL"
    REMOTE_BASE="$CLEAN_URL"
fi

# 设置远程仓库 URL（用 token 注入认证）
if [ -z "$REMOTE_BASE" ]; then
    echo -e "${YELLOW}警告：无 git remote 配置，跳过推送步骤${NC}"
    PUSH_ENABLED=false
elif [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}警告：未找到部署 token（~/.hermes/.deploy_token），使用现有 remote URL${NC}"
    PUSH_ENABLED=true
else
    # 从 URL 中提取仓库路径（不含协议和域名）
    USER_REPO=$(echo "$REMOTE_BASE" | sed -E 's|https?://[^/]*/||' | sed -E 's|\.git$||' | sed -E 's|.*@github\.com/||')
    if [ -n "$USER_REPO" ]; then
        # 构建带 token 的认证 URL（仅在内存中，不写入 .git/config 长存）
        AUTH_URL="https://JackSmith111977:${GITHUB_TOKEN}@github.com/${USER_REPO}.git"
        git remote set-url origin "$AUTH_URL" 2>/dev/null || git remote add origin "$AUTH_URL"
        PUSH_ENABLED=true
        echo -e "${GREEN}已配置带 token 认证的 remote URL${NC}"
    else
        echo -e "${YELLOW}警告：无法从 remote URL 提取仓库路径${NC}"
        PUSH_ENABLED=true
    fi
fi

# 同步文件（从 ~/.hermes 到部署目录）
echo -e "${GREEN}同步文件...${NC}"

# 1. 同步 config 目录（排除敏感文件）
if [ -d "$HERMES_DIR/config" ]; then
    rsync -av --exclude='*.key' --exclude='*.pem' "$HERMES_DIR/config/" "$DEPLOY_DIR/config/" 2>/dev/null || true
fi

# 2. 同步 deploy.sh（如果有更新）
if [ -f "$HERMES_DIR/deploy.sh" ]; then
    cp "$HERMES_DIR/deploy.sh" "$DEPLOY_DIR/deploy.sh"
fi

# 3. 同步 scripts 目录
if [ -d "$HERMES_DIR/scripts" ]; then
    rsync -av "$HERMES_DIR/scripts/" "$DEPLOY_DIR/scripts/" 2>/dev/null || true
fi

# 4. 同步自定义 skills（排除 .bundled_manifest 等）
if [ -d "$HERMES_DIR/skills" ]; then
    rsync -av --exclude='.bundled_manifest' --exclude='node_modules' "$HERMES_DIR/skills/" "$DEPLOY_DIR/skills/" 2>/dev/null || true
fi

# 5. 同步 SOUL.md（如果有）
if [ -f "$HERMES_DIR/SOUL.md" ]; then
    cp "$HERMES_DIR/SOUL.md" "$DEPLOY_DIR/SOUL.md"
fi

# 6. 同步 TASK_QUEUE.md（任务队列模板）
if [ -f "$HERMES_DIR/TASK_QUEUE.md" ]; then
    cp "$HERMES_DIR/TASK_QUEUE.md" "$DEPLOY_DIR/TASK_QUEUE.md"
fi

# 7. 同步 task_queue.py
if [ -f "$HERMES_DIR/task_queue.py" ]; then
    cp "$HERMES_DIR/task_queue.py" "$DEPLOY_DIR/scripts/task_queue.py"
fi

echo -e "${GREEN}文件同步完成${NC}"

# 添加文件到 git（使用 .gitignore 排除敏感文件）
echo -e "${YELLOW}添加文件到 git...${NC}"
git add -A 2>/dev/null || true

# 检查是否有变更
if git diff --staged --quiet 2>/dev/null; then
    echo -e "${GREEN}没有变更，跳过提交${NC}"
    # 即使无变更也恢复 URL（防止之前失败遗留）
    git remote set-url origin "$REMOTE_BASE" 2>/dev/null || true
    exit 0
fi

# 提交变更
COMMIT_MSG="自动更新 - $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG" 2>/dev/null || {
    echo -e "${YELLOW}提交失败，可能是首次提交需要配置用户信息${NC}"
    git config user.email "hermes-catgirl@local" 2>/dev/null || true
    git config user.name "小喵" 2>/dev/null || true
    git commit -m "$COMMIT_MSG" 2>/dev/null || echo -e "${RED}提交仍然失败${NC}"
}
echo -e "${GREEN}提交完成: $COMMIT_MSG${NC}"

# 推送到远程仓库（如果启用）
if [ "$PUSH_ENABLED" = true ]; then
    echo -e "${YELLOW}推送到远程仓库（通过代理）...${NC}"
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "master")
    echo -e "${GREEN}推送到远程仓库（分支: $CURRENT_BRANCH，通过代理）...${NC}"
    git -c http.proxy="http://${PROXY_HOST}:${PROXY_PORT}" push -u origin "$CURRENT_BRANCH" 2>&1 || \
        echo -e "${RED}推送失败，请检查网络连接和仓库权限${NC}"
    echo -e "${GREEN}推送完成${NC}"

    # ★★★ 安全关键：推送后立即恢复 remote URL 为不带 token 的纯 URL ★★★
    git remote set-url origin "$REMOTE_BASE"
    echo -e "${GREEN}已清理 remote URL 中的认证信息${NC}"
else
    echo -e "${YELLOW}推送已跳过（未启用推送）${NC}"
fi

echo -e "${GREEN}=== 上传脚本执行完成 ===${NC}"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
