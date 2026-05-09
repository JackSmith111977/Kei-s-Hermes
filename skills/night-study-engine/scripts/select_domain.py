#!/usr/bin/env python3
"""
夜间自习引擎 v3.0 - 领域选择器（v2 兼容包装）
现委托给 adaptive_scheduler.py 实现。保留此脚本保持向后兼容。

用法（同 v2.0）：
  python3 select_domain.py                          # 选择最需要的领域
  python3 select_domain.py --skip ai_tech            # 跳过指定领域
  python3 select_domain.py --review                  # 检查间隔复习
  python3 select_domain.py --list                    # 列出所有领域
"""
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ADAPTIVE_SCHEDULER = SCRIPT_DIR / "adaptive_scheduler.py"


def main():
    if not ADAPTIVE_SCHEDULER.exists():
        print("❌ adaptive_scheduler.py 未找到，请先确保脚本完整安装")
        sys.exit(1)

    # 传递所有参数给 adaptive_scheduler.py
    cmd = [sys.executable, str(ADAPTIVE_SCHEDULER)] + sys.argv[1:]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
