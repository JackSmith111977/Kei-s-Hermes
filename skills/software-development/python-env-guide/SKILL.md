---
name: python-env-guide
description: Hermes 环境下的 Python 使用最佳实践指南。涵盖 venv 管理、pip 用法、路径解析、错误处理、pathlib、if __name__...
version: 2.0.0
triggers:
- python
- venv
- pip
- 环境
- logging
allowed-tools:
- terminal
- read_file
- write_file
- execute_code
- patch
metadata:
  hermes:
    tags:
    - python
    - venv
    - pip
    - environment
    - best-practices
    category: software-development
    skill_type: library-reference
    design_pattern: tool-wrapper
---
# Python 环境与脚本最佳实践 🐍

## Hermes 环境的特殊之处

Hermes Agent 在 **venv 内的 Python 3.11** 运行，但系统还有 **Python 3.12**：

```
终端 which python3    → /home/ubuntu/.hermes/hermes-agent/venv/bin/python3  (3.11.15)
系统 python3          → /usr/bin/python3  (3.12.3)
apt 安装的包          → 在系统 Python 3.12 的 site-packages 中
pip 安装的包          → 在 venv 3.11 的 site-packages 中
```

### 后果
```bash
python3 script.py            # 用 venv 的 3.11 → 包可能不全
/usr/bin/python3 script.py   # 用系统的 3.12 → 包可能全但版本不对
sudo apt install weasyprint  # 装到系统 3.12 → venv 3.11 找不到！
```

### 正确做法

| 场景 | 用什么 Python | 原因 |
|:---|:---|:---|
| 运行 Hermes 相关脚本 | `python3` (venv) | hermes 的依赖在这里 |
| 运行 PDF/PPT 生成脚本 | `/usr/bin/python3` | reportlab/weasyprint 装在这里 |
| pip install 新包 | `python3 -m pip install` (venv) 或 `/usr/bin/python3 -m pip install` (系统) | 明确指定目标环境 |
| execute_code 环境 | venv 3.11 | 继承 Hermes venv |
| apt 安装 | `sudo apt install` | 系统级，两个 Python 都能用 |

## 一、虚拟环境管理

### 创建 venv
```bash
# 创建
python3 -m venv venv

# 激活
source venv/bin/activate

# 确认
which python   # 应该指向 venv/bin/python
```

### Hermes 的 venv 路径
```
~/.hermes/hermes-agent/venv/    # Hermes 自己的 venv
```

### pip 安装的正确姿势
```bash
# ✅ 在 venv 里装
python3 -m pip install requests

# ✅ 在系统装（用系统 Python）
/usr/bin/python3 -m pip install weasyprint

# ❌ 错误：pip install 不加 -m
pip install requests   # 可能装了错误的地方

# ❌ 错误：混用
python3 -m pip install weasyprint   # venv 里装，但 weasyprint 需要系统依赖
```

### 查看包在哪里
```bash
# 查看包是否已装
python3 -c "import requests; print(requests.__file__)"

# 列出所有包
python3 -m pip list

# 查看特定包
python3 -m pip show requests
```

## 二、Pathlib（现代路径操作）

**`pathlib` > `os.path`** — Python 3.4+ 推荐的路径操作方式。

```python
from pathlib import Path

# ❌ 旧写法
import os
path = os.path.join(os.path.expanduser("~"), "docs", "file.txt")
exists = os.path.exists(path)

# ✅ 新写法
path = Path.home() / "docs" / "file.txt"
exists = path.exists()

# 更多用法
path = Path("/home/ubuntu/docs/file.txt")
path.parent            # /home/ubuntu/docs
path.stem              # file
path.suffix            # .txt
path.name              # file.txt
path.with_suffix(".pdf")  # /home/ubuntu/docs/file.pdf
path.exists()          # 是否存在
path.is_file()         # 是否是文件
path.is_dir()          # 是否是目录
path.mkdir(parents=True, exist_ok=True)  # 创建目录（递归）
path.read_text()       # 读取文本
path.write_text("内容")  # 写入文本
path.read_bytes()      # 读取二进制
path.iterdir()         # 遍历目录
```


> 🔍 **## 三、if __name__** moved to [references/detailed.md](references/detailed.md)
