---
name: doc-design
description: '文档排版设计索引技能。根据文档格式路由到对应的原子 skill。

  当用户需要创建、编辑、美化任何格式的文档时使用此技能，

  本 skill 负责识别格式...'
version: 5.1.0
triggers:
- 文档
- 排版
- doc
- 排版设计
depends_on:
- pdf-layout-reportlab
- pdf-layout-weasyprint
- docx-guide
- pptx-guide
- markdown-guide
- html-guide
- latex-guide
- epub-guide
author: 小喵
license: MIT
metadata:
  hermes:
    tags:
    - document
    - design
    - formatting
    - index
    related_skills:
    - pdf-layout-reportlab
    - pdf-layout-weasyprint
    - docx-guide
    - pptx-guide
    - markdown-guide
    - html-guide
    - latex-guide
    - epub-guide
    category: productivity
    skill_type: doc-generation
    design_pattern: index
---
# 文档排版设计索引技能

> **原子化原则**：本 skill 是索引入口，不包含具体实现。每种文档格式有独立的原子 skill。

## 触发条件

**使用此 skill 当：**
- 用户要求创建、编辑、美化任何格式的文档
- 用户要求文档格式转换
- 用户提到排版、布局、字体、配色等设计需求

**路由规则：**

| 格式 | 路由到 | 说明 |
|------|--------|------|
| PDF（ReportLab） | → `pdf-layout-reportlab` skill | ReportLab 中文排版——字体/分页/表格/封面/Mermaid |
| PDF（WeasyPrint） | → `pdf-layout-weasyprint` skill | HTML+CSS→PDF，CSS 布局中文，比 ReportLab 更适合文字文档 |\n| Word (.docx) | → `docx-guide` skill | python-docx 完整操作 |
| PPT (.pptx) | → `pptx-guide` skill | python-pptx 完整操作 + 2025-2026 设计趋势 |
| Excel (.xlsx) | → `xlsx-guide` skill | openpyxl 完整操作 |
| Markdown | → `markdown-guide` skill | 语法、pandoc 转换 |
| HTML/CSS | → `html-guide` skill | 网页排版、打印优化 |
| LaTeX | → `latex-guide` skill | 学术论文排版 |
| EPUB | → `epub-guide` skill | 电子书生成 |
| 格式转换 | → 见下方转换速查表 | pandoc / LibreOffice |

## 核心设计原则（所有格式通用）

### CRAP 原则

| 原则 | 说明 |
|------|------|
| **C**ontrast 对比 | 通过大小、颜色、粗细区分层次 |
| **R**epetition 重复 | 统一视觉元素（字体、颜色、间距） |
| **A**lignment 对齐 | 元素不随意放置，对齐到网格 |
| **P**roximity 亲密性 | 相关元素靠近，段落间距 > 行间距 |

### 设计速查

- **字体**：≤ 2 种（推荐 1 种字体 + 字重变化）
- **配色**：60-30-10 法则（60% 主色/中性色 + 30% 辅助色 + 10% 强调色）
- **留白**：内容不超过页面 50%（现代设计标准）
- **对比度**：文字/背景对比度 ≥ 4.5:1
- **2025-2026 趋势**：大胆排版、编辑风、克制配色、极简留白

## 格式转换速查

### 万能转换工具：pandoc

```bash
pandoc input.md -o output.docx
pandoc input.md -o output.pdf --pdf-engine=xelatex -V mainfont="PingFang SC"
pandoc input.docx -o output.md
pandoc input.html -o output.pdf
pandoc input.md -o output.pdf --toc --citeproc --bibliography=refs.bib
```

### LibreOffice 命令行

```bash
libreoffice --headless --convert-to pdf input.docx
libreoffice --headless --convert-to docx input.odt
```

### 转换矩阵

| 从 \ 到 | Word | PPT | PDF | HTML | Markdown | LaTeX | EPUB |
|---------|------|-----|-----|------|----------|-------|------|
| **Word** | — | — | pandoc/lo | pandoc | pandoc | pandoc | pandoc |
| **HTML** | pandoc | — | wkhtmltopdf | — | pandoc | pandoc | pandoc |
| **Markdown** | pandoc | pandoc | pandoc | 内置 | — | pandoc | pandoc |
| **LaTeX** | pandoc | — | pdflatex | pandoc | pandoc | — | pandoc |
| **PDF** | pdf2docx | — | — | — | — | — | — |

## Red Flags（常见错误）

- 使用超过 3 种字体
- 颜色对比度不足（< 4.5:1）
- 段落间距 < 行间距
- 中英文混排时不加空格
- 不处理中文字体导致乱码
- 直接在代码中硬编码路径

## 设计工具推荐

| 用途 | 工具 |
|------|------|
| 配色 | Adobe Color、Coolors、Realtime Colors |
| 字体 | Google Fonts、思源系列、HarmonyOS Sans |
| 图表 | Matplotlib、Plotly、ECharts |
| 图标 | Font Awesome、Iconfont、Flaticon |
| 灵感 | Pinterest、Behance、Dribbble |
| 转换 | pandoc（万能）、LibreOffice |
| 图库 | Unsplash、Pexels（免费高清） |


> 🔍 **详细参考**: 更多内容请查阅 [latex-guide.md](latex-guide.md)
