---
name: pdf-layout-weasyprint
description: 使用 WeasyPrint（HTML+CSS→PDF）生成中文 PDF 的完整指南。WeasyPrint 比 ReportLab 更适合文字为主的 P...
version: 2.0.0
triggers:
- pdf
- weasyprint
- 生成 pdf
allowed-tools:
- terminal
- read_file
- write_file
- patch
metadata:
  hermes:
    tags:
    - pdf
    - weasyprint
    - html
    - css
    - chinese
    - layout
    category: doc-design
    related_skills: ["pdf-layout-reportlab", "doc-design", "web-ui-ux-design"]
    skill_type: library-reference
    design_pattern: tool-wrapper
    related_skills:
    - pdf-layout-reportlab
    - doc-design
---
# PDF 排版无痛指南：WeasyPrint 篇 🔥

## 🚨 语言检查（绝对优先！）

**在开始任何 PDF 生成任务前，必须先检查语言偏好！**

1. **默认中文**：除非主人明确指定使用其他语言（如"用英文"），否则**所有文本必须使用中文**。
2. **禁止私自切换**：绝对禁止在没有指令的情况下生成英文内容（包括标题、正文、图表文字）。
3. **自我检查**：生成前自检，如果内容是英文，立即重写为中文。

---

## 概述

**WeasyPrint** 是一个把 HTML+CSS 转成 PDF 的 Python 库。相比 ReportLab，它的核心优势是 **CSS 控制布局**——你不用在 Python 代码里一个个定位元素，写 HTML 模板就行了。

### 什么时候用 WeasyPrint

| 场景 | 推荐 |
|:---|:---:|
| 文字为主、有表格、中文 | ⭐ **WeasyPrint**（首选） |
| 从零开始的 PDF 项目 | ⭐ **WeasyPrint** |
| 复杂排版（多列、灵活布局） | ⭐ **WeasyPrint**（CSS 完胜） |
| 需要精确坐标绘图 | ReportLab |
| 已有大量 reportlab 代码 | 继续 ReportLab |

## 一、安装

```bash
# 方式 A：系统包安装（推荐，包含所有系统依赖）
sudo apt install weasyprint -y

# 方式 B：pip 安装（需先安装系统依赖）
sudo apt install python3-pip libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libharfbuzz-subset0

# 然后在 venv 里用 pip
pip install weasyprint

# 验证 CLI
weasyprint --version
# 验证 Python 模块（可能在系统 Python 或 venv 中）
python3 -c "from weasyprint import HTML; print('OK')"
```

### 依赖说明
- 需要 `libpango-1.0-0`、`libpangoft2-1.0-0`、`libharfbuzz0b`（系统包，apt 自动处理）
- Python >= 3.10（最新版）| Python >= 3.9（旧版）
- **系统安装版（apt）最稳定**，pip 版需手动处理系统依赖

### CLI 用法
```bash
# 从 URL 生成 PDF
weasyprint "https://example.com" output.pdf

# 从本地 HTML 文件生成
weasyprint input.html output.pdf

# 附加自定义 CSS
weasyprint input.html output.pdf -s style.css

# 从标准输入
weasyprint - output.pdf < input.html
```

## 二、Hello World

```python
from weasyprint import HTML

HTML(string="""
<html>
<head><meta charset="utf-8"><title>我的 PDF</title></head>
<body>
  <h1>Hello, PDF!</h1>
  <p>这是用 WeasyPrint 生成的第一份 PDF 文档喵～</p>
</body>
</html>
""").write_pdf("hello.pdf")
```

### 从 HTML 文件
```python
HTML(filename="template.html").write_pdf("output.pdf")
```

### 设置参数
```python
HTML(string="...").write_pdf("output.pdf", 
    zoom=1.0,           # 缩放
    presentational_hints=True  # 允许 HTML 属性控制样式
)
```


> 🔍 **## 三、中文支持** moved to [references/detailed.md](references/detailed.md)
