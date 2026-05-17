#!/usr/bin/env bash
# =============================================================================
# fs-audit.sh — 文件系统规范审计钩子脚本 (v2, pure Python)
#
# 被 Hermes Shell Hooks 系统调用。使用 Python 3 处理 JSON 协议。
# 接收 stdin JSON，输出结果到 stdout。
# =============================================================================

# 直接调用 Python 脚本处理所有逻辑
exec python3 "$(dirname "$0")/fs-audit.py"
