#!/bin/bash
# SRA 全套验证脚本 — L0 到 L4 全流程
# 用法: bash scripts/run-full-validation.sh
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $name"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}❌${NC} $name"
        FAIL=$((FAIL + 1))
    fi
}

echo -e "${CYAN}════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SRA 全套验证 v1.0                        ${NC}"
echo -e "${CYAN}════════════════════════════════════════════${NC}"

# ════════════════════════════════════════
# L0+L1: pytest 单元+集成测试
# ════════════════════════════════════════
echo -e "\n${YELLOW}📦 L0+L1: pytest 单元+集成测试${NC}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"
check "pytest 全量通过" "python3 -m pytest tests/ -q --tb=line 2>&1 | tail -1 | grep -q 'passed'"

# ════════════════════════════════════════
# L2: CLI 命令测试
# ════════════════════════════════════════
echo -e "\n${YELLOW}📟 L2: CLI 命令测试${NC}"

check "sra status" "sra status 2>&1 | grep -q '运行中'"
check "sra version" "sra version 2>&1 | grep -q '1.1.0'"
check "sra help" "sra help 2>&1 | grep -q '推荐匹配技能'"
check "sra refresh" "sra refresh 2>&1 | grep -q '已刷新'"
check "sra stats" "sra stats 2>&1 | grep -q '状态:'"
check "sra config show" "sra config show 2>&1 | grep -q 'skills_dir'"
check "sra adapters" "sra adapters 2>&1 | grep -q 'hermes'"
check "sra coverage" "sra coverage 2>&1 | grep -q '覆盖率'"

# ════════════════════════════════════════
# L2: CLI 场景推荐
# ════════════════════════════════════════
echo -e "\n${YELLOW}🔍 L2: CLI 场景推荐${NC}"

check "推荐: 画架构图 → architecture-diagram" \
    "sra recommend 画架构图 2>&1 | grep -q 'architecture-diagram'"
check "推荐: 生成PDF → pdf-layout" \
    "sra recommend 生成PDF文档 2>&1 | grep -q 'pdf-layout'"
check "推荐: 帮我做个PPT → pptx-guide" \
    "sra recommend 帮我做个PPT 2>&1 | grep -q 'pptx-guide'"
check "推荐: 飞书发送文件 → feishu-send-file" \
    "sra recommend 飞书发送文件 2>&1 | grep -q 'feishu-send-file'"
check "推荐: git操作 → git-advanced-ops" \
    "sra recommend git操作 2>&1 | grep -q 'git-advanced-ops'"
check "推荐: 用AI生成图片 → image-generation" \
    "sra recommend 用AI生成图片 2>&1 | grep -q 'image-generation'"

# ════════════════════════════════════════
# L3: HTTP API 测试
# ════════════════════════════════════════
echo -e "\n${YELLOW}🌐 L3: HTTP API 测试${NC}"

check "GET /status → 200 + JSON" \
    "curl -s http://localhost:8536/status | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d[\"status\"]==\"ok\"'"
check "POST /recommend → JSON + recommendations" \
    "curl -s -X POST http://localhost:8536/recommend -H 'Content-Type: application/json' -d '{\"message\":\"画架构图\"}' | python3 -c 'import sys,json; d=json.load(sys.stdin); assert len(d[\"recommendations\"])>0'"
check "GET /stats → JSON + skills_count" \
    "curl -s http://localhost:8536/stats | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d[\"skills_count\"]>=300'"

# ════════════════════════════════════════
# L4: 仿真 + 压力测试
# ════════════════════════════════════════
echo -e "\n${YELLOW}🧪 L4: 仿真 + 压力测试${NC}"

success=0
for i in $(seq 1 20); do
    http_code=$(curl -s -o /dev/null -w '%{http_code}' \
        -X POST http://localhost:8536/recommend \
        -H 'Content-Type: application/json' \
        -d '{"message":"画架构图"}' 2>/dev/null)
    if [ "$http_code" = "200" ]; then
        success=$((success + 1))
    fi
done
if [ "$success" -eq 20 ]; then
    echo -e "  ${GREEN}✅${NC} 压力测试: 20/20 成功"
    PASS=$((PASS + 1))
else
    echo -e "  ${RED}❌${NC} 压力测试: ${success}/20 成功"
    FAIL=$((FAIL + 1))
fi

# ════════════════════════════════════════
# 汇总
# ════════════════════════════════════════
TOTAL=$((PASS + FAIL))
echo -e "\n${CYAN}════════════════════════════════════════════${NC}"
echo -e "${CYAN}  验证完成: ${GREEN}${PASS}✅${NC} / ${RED}${FAIL}❌${NC} / ${TOTAL} 总计${NC}"
echo -e "${CYAN}════════════════════════════════════════════${NC}"

if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}🎉 全部通过！SRA 可以发布。${NC}"
    exit 0
else
    echo -e "${RED}⚠️  ${FAIL} 个测试失败，请检查后再发布。${NC}"
    exit 1
fi
