#!/bin/bash
# create-skill-dir.sh — 创建新 Skill 的标准目录结构
# 用法: ./create-skill-dir.sh <skill-name> [--path <base-path>]
#
# 示例:
#   ./create-skill-dir.sh my-new-skill
#   ./create-skill-dir.sh my-new-skill --path ~/.hermes/skills

set -euo pipefail

# 解析参数
SKILL_NAME="${1:?Usage: $0 <skill-name> [--path <base-path>]}"
BASE_PATH="${HOME}/.hermes/skills"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --path)
            BASE_PATH="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

SKILL_DIR="${BASE_PATH}/${SKILL_NAME}"

# 检查是否已存在
if [[ -d "$SKILL_DIR" ]]; then
    echo "⚠️  Skill 目录已存在: ${SKILL_DIR}"
    read -p "是否覆盖？[y/N] " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "取消创建。"
        exit 0
    fi
fi

# 创建目录结构
echo "📁 创建 Skill 目录结构: ${SKILL_DIR}"
mkdir -p "${SKILL_DIR}"/{references,templates,assets,scripts,checklists,examples,evals}

# 创建基础 SKILL.md
cat > "${SKILL_DIR}/SKILL.md" << 'SKILLEOF'
---
name: SKILL_NAME_PLACEHOLDER
description: [描述此 Skill 的用途和触发条件]
---

# SKILL_NAME_PLACEHOLDER

## 用途
[详细描述]

**触发词：** [列出触发词]

---

## 核心内容

[在此添加 Skill 的核心指令]

---

## 示例

### 输入
\`\`\`
[示例输入]
\`\`\`

### 输出
\`\`\`
[示例输出]
\`\`\`

---

## 踩坑清单

### 陷阱 1：[名称]
❌ **错误：** [错误做法]
✅ **正确：** [正确做法]
**原因：** [解释]

---

*版本：1.0.0 | 创建日期：DATE_PLACEHOLDER*
SKILLEOF

# 替换占位符
sed -i "s/SKILL_NAME_PLACEHOLDER/${SKILL_NAME}/g" "${SKILL_DIR}/SKILL.md"
sed -i "s/DATE_PLACEHOLDER/$(date +%Y-%m-%d)/g" "${SKILL_DIR}/SKILL.md"

# 创建 .gitkeep
touch "${SKILL_DIR}/references/.gitkeep"
touch "${SKILL_DIR}/templates/.gitkeep"
touch "${SKILL_DIR}/assets/.gitkeep"
touch "${SKILL_DIR}/scripts/.gitkeep"

# 创建 evals.json 模板
cat > "${SKILL_DIR}/evals/evals.json" << 'EVALSEOF'
{
  "skill_name": "SKILL_NAME_PLACEHOLDER",
  "evals": [
    {
      "id": "eval-001",
      "prompt": "[测试 prompt]",
      "expected_output": "[预期输出]",
      "expectations": [
        "[期望 1]",
        "[期望 2]"
      ]
    }
  ]
}
EVALSEOF

sed -i "s/SKILL_NAME_PLACEHOLDER/${SKILL_NAME}/g" "${SKILL_DIR}/evals/evals.json"

echo "✅ Skill 目录创建完成！"
echo ""
echo "📂 目录结构："
find "$SKILL_DIR" -type f -o -type d | sort | sed 's|^|  |'
echo ""
echo "📝 下一步："
echo "  1. 编辑 SKILL.md 添加核心指令"
echo "  2. 添加模板到 templates/ 或 assets/"
echo "  3. 添加参考文档到 references/"
echo "  4. 编写测试用例到 evals/evals.json"
echo "  5. 运行测试评估"
