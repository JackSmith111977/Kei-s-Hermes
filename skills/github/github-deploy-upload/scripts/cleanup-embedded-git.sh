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
#       更严重的情况：如果内嵌 .git/ 曾经被提交过，index 中可能已经存在
#       mode 160000 的 gitlink（子模块）条目。此脚本也会检测并提示修复。
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

# ★ 额外检查：检测 index 中的子模块条目（mode 160000 gitlink）
#   这比磁盘 .git 更严重——子模块条目一旦提交，光靠 .gitignore 和
#   磁盘清理无法修复，必须 git rm --cached 移除后重新 git add
echo ""
echo "🔍 检查 index 中的子模块条目..."
cd "$DEPLOY_DIR"

SUBMODULE_ENTRIES=$(git ls-files --stage skills/ 2>/dev/null | grep '^160000' || true)
if [ -n "$SUBMODULE_ENTRIES" ]; then
    SUBMODULE_COUNT=$(echo "$SUBMODULE_ENTRIES" | wc -l)
    echo "⚠️  检测到 $SUBMODULE_COUNT 个子模块条目在 index 中！"
    echo "$SUBMODULE_ENTRIES"
    echo ""
    echo "📋 修复方法："
    echo "   git rm --cached <path>       # 移除子模块条目"
    echo "   rm -rf <path>/.git           # 清理内嵌仓库"
    echo "   git add <path>/              # 作为普通文件重新跟踪"
    echo ""
    echo "   示例:"
    echo "   git rm --cached skills/web-access"
    echo "   rm -rf skills/web-access/.git"
    echo "   git add skills/web-access/"
    FIX_NEEDED=true
else
    echo "✅ 无子模块条目残留"
    FIX_NEEDED=false
fi

# 验证 git 状态
echo ""
echo "📊 git 状态检查..."
if git status --short 2>/dev/null | grep -q '.'; then
    echo "⚠️  注意：以下未暂存变更需要处理："
    git status --short
    if [ "$FIX_NEEDED" = true ]; then
        echo "💡 提示：子模块条目可能导致 git status 显示 M（modified content），"
        echo "   即使磁盘文件未修改。请按上述方法修复子模块条目。"
    fi
else
    echo "✅ git 状态干净"
fi
