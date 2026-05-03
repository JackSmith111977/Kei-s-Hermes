#!/bin/bash
# Pre-flight 检查清单：在调用 skill_manage 前必须运行
# 用途：确保 skill-manage 操作经过 skill-creator 流程

echo "🔒 Skill Pre-flight 检查清单"
echo "=========================="

# 检查 1: 是否已声明依赖关系
check_depends_on() {
    local skill_name=$1
    local skill_file="$HOME/.hermes/skills/$skill_name/SKILL.md"
    
    if [ -f "$skill_file" ]; then
        if grep -q "depends_on:" "$skill_file"; then
            echo "✅ [$skill_name] 已声明依赖关系"
            return 0
        else
            echo "⚠️  [$skill_name] 未声明 depends_on，建议添加"
            return 1
        fi
    else
        echo "❌ [$skill_name] SKILL.md 不存在"
        return 2
    fi
}

# 检查 2: 检查引用链是否完整
check_references() {
    local skill_name=$1
    echo "🔍 扫描引用链..."
    python3 "$HOME/.hermes/skills/skill-creator/scripts/dependency-scan.py" 2>/dev/null | grep -A 5 "断裂引用"
}

# 主流程
if [ -z "$1" ]; then
    echo "用法: $0 <skill-name>"
    echo "示例: $0 pdf-layout"
    exit 1
fi

SKILL_NAME=$1

echo ""
echo "📦 检查目标: $SKILL_NAME"
echo ""

# 执行检查
check_depends_on "$SKILL_NAME"
echo ""
check_references "$SKILL_NAME"

echo ""
echo "✅ Pre-flight 检查完成！"
echo "💡 若无报错，可安全调用 skill_manage"
