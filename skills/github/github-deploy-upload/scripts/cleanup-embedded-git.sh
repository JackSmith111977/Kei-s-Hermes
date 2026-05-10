#!/bin/bash
# =============================================================================
# cleanup-embedded-git.sh — 清理 rsync 同步后混入的内嵌 .git 目录
# =============================================================================
# 用途: 在 deploy-upload.sh 的 rsync 同步步骤之后调用，清理从 skill 目录
#       rsync 过来的内嵌 .git/ 目录，防止 git 检测为子模块变更。
#
# 问题: web-access 等 skill 目录自身包含 .git/（用于版本管理），rsync
#       同步时会将这些 .git/ 一并复制到部署目录，导致部署目录的 git
#       将其检测为 "modified content, untracked content"（子模块检测）。
#
# 用法: bash scripts/cleanup-embedded-git.sh /tmp/hermes-catgirl-deploy
#       或在 deploy-upload.sh 中作为 post-rsync 步骤调用
# =============================================================================

set -e

DEPLOY_DIR="${1:-/tmp/hermes-catgirl-deploy}"

if [ ! -d "$DEPLOY_DIR" ]; then
    echo "错误：部署目录不存在: $DEPLOY_DIR"
    exit 1
fi

echo "🔍 扫描 $DEPLOY_DIR/skills/ 中的内嵌 .git 目录..."

FOUND_COUNT=0
while IFS= read -r -d '' GIT_DIR; do
    REL_PATH="${GIT_DIR#$DEPLOY_DIR/}"
    echo "   🗑️  清理: $REL_PATH"
    rm -rf "$GIT_DIR"
    FOUND_COUNT=$((FOUND_COUNT + 1))
done < <(find "$DEPLOY_DIR/skills/" -maxdepth 2 -name '.git' -type d -print0 2>/dev/null)

if [ "$FOUND_COUNT" -eq 0 ]; then
    echo "✅ 未发现内嵌 .git 目录，无需清理"
else
    echo "✅ 已清理 $FOUND_COUNT 个内嵌 .git 目录"
fi

# 验证 git 状态
cd "$DEPLOY_DIR"
if git status --short 2>/dev/null | grep -q '.'; then
    echo "⚠️  注意：清理后仍有未暂存变更，请检查 git status"
else
    echo "✅ git 状态干净"
fi
