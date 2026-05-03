#!/bin/bash
# validate-skill.sh — 验证 Skill 目录结构和文件格式
# 用法: ./validate-skill.sh <skill-dir>
#
# 检查项：
#   - SKILL.md 存在且格式正确
#   - YAML frontmatter 完整
#   - 目录结构符合规范
#   - 无敏感信息泄露

set -euo pipefail

SKILL_DIR="${1:?Usage: $0 <skill-dir>}"
ERRORS=0
WARNINGS=0

# 颜色
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🔍 验证 Skill: ${SKILL_DIR}"
echo ""

# 1. 检查 SKILL.md 存在
if [[ ! -f "${SKILL_DIR}/SKILL.md" ]]; then
    echo -e "${RED}❌ SKILL.md 不存在${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ SKILL.md 存在${NC}"
fi

# 2. 检查 YAML frontmatter
if [[ -f "${SKILL_DIR}/SKILL.md" ]]; then
    # 检查是否有 YAML frontmatter
    if ! head -1 "${SKILL_DIR}/SKILL.md" | grep -q '^---$'; then
        echo -e "${RED}❌ 缺少 YAML frontmatter (---)${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ YAML frontmatter 存在${NC}"

        # 检查 name 字段
        if ! grep -q '^name:' "${SKILL_DIR}/SKILL.md"; then
            echo -e "${RED}❌ 缺少 name 字段${NC}"
            ERRORS=$((ERRORS + 1))
        else
            SKILL_NAME=$(grep '^name:' "${SKILL_DIR}/SKILL.md" | head -1 | sed 's/name: *//')
            echo -e "${GREEN}✅ name: ${SKILL_NAME}${NC}"
        fi

        # 检查 description 字段
        if ! grep -q '^description:' "${SKILL_DIR}/SKILL.md"; then
            echo -e "${RED}❌ 缺少 description 字段${NC}"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN}✅ description 存在${NC}"
        fi
    fi

    # 检查文件大小
    LINE_COUNT=$(wc -l < "${SKILL_DIR}/SKILL.md")
    if [[ $LINE_COUNT -gt 500 ]]; then
        echo -e "${YELLOW}⚠️  SKILL.md 超过 500 行 (${LINE_COUNT} 行)，建议拆分${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✅ SKILL.md 大小合理 (${LINE_COUNT} 行)${NC}"
    fi
fi

# 3. 检查目录结构
EXPECTED_DIRS=("references" "templates" "assets" "scripts")
for dir in "${EXPECTED_DIRS[@]}"; do
    if [[ -d "${SKILL_DIR}/${dir}" ]]; then
        FILE_COUNT=$(find "${SKILL_DIR}/${dir}" -type f ! -name '.gitkeep' | wc -l)
        if [[ $FILE_COUNT -gt 0 ]]; then
            echo -e "${GREEN}✅ ${dir}/ 存在 (${FILE_COUNT} 个文件)${NC}"
        else
            echo -e "${YELLOW}⚠️  ${dir}/ 存在但为空${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  ${dir}/ 目录不存在（可选）${NC}"
    fi
done

# 4. 检查敏感信息
echo ""
echo "🔒 安全检查："

# 检查硬编码密钥
SENSITIVE_PATTERNS=("api_key" "apikey" "secret" "password" "token" "private_key")
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if grep -ri "$pattern" "${SKILL_DIR}" --include="*.md" --include="*.sh" --include="*.py" --include="*.json" 2>/dev/null | grep -v "template\|example\|\.gitkeep" | head -1 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  发现可能的敏感信息: ${pattern}${NC}"
        grep -rn "$pattern" "${SKILL_DIR}" --include="*.md" --include="*.sh" --include="*.py" --include="*.json" 2>/dev/null | grep -v "template\|example\|\.gitkeep" | head -3
        WARNINGS=$((WARNINGS + 1))
    fi
done

# 检查绝对路径
if grep -rn "/home/" "${SKILL_DIR}" --include="*.md" --include="*.sh" 2>/dev/null | grep -v ".gitkeep" | head -1 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  发现绝对路径引用${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 5. 检查 evals
if [[ -f "${SKILL_DIR}/evals/evals.json" ]]; then
    echo -e "${GREEN}✅ evals/evals.json 存在${NC}"
    EVAL_COUNT=$(python3 -c "import json; d=json.load(open('${SKILL_DIR}/evals/evals.json')); print(len(d.get('evals',[])))" 2>/dev/null || echo "?")
    echo -e "${GREEN}✅ 测试用例数: ${EVAL_COUNT}${NC}"
else
    echo -e "${YELLOW}⚠️  evals/evals.json 不存在（可选）${NC}"
fi

# 总结
echo ""
echo "=============================="
if [[ $ERRORS -eq 0 && $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✅ 验证通过！无问题。${NC}"
elif [[ $ERRORS -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  验证通过，有 ${WARNINGS} 个警告。${NC}"
else
    echo -e "${RED}❌ 验证失败：${ERRORS} 个错误，${WARNINGS} 个警告。${NC}"
fi
echo "=============================="

exit $ERRORS
