---
name: pdf-layout-reportlab
description: ReportLab 引擎快速参考 — 内容已整合到 pdf-layout v3.0，本 skill 保留 ReportLab 要点
version: 1.0.0
type: redirect
redirect_to: pdf-layout
triggers:
- PDF 黑块
- PDF 排版问题
- ReportLab 字体
metadata:
  hermes:
    tags:
    - reportlab
    - pdf
    - chinese-font
    - redirect
    category: productivity
    skill_type: engine-quickref
depends_on:
  - reportlab
  - pdf-layout

---

# ReportLab 快速参考

> 💡 **完整 PDF 排版请用 `pdf-layout` v3.0**（双引擎统一入口）。
> 本 skill 保留 ReportLab 独有的中文排版要点。

## 字体配置

```python
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('WQY', "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", subfontIndex=0))
FONT = 'WQY'
```

## 中文排版三要素

| 要素 | 做法 |
|:-----|:------|
| 字体 | WQY ZenHei TTF（不要用 Noto CJK CFF） |
| 表格单元格 | 必须用 Paragraph 包装，否则中文方块 |
| 字符串转义 | `esc()` 函数转义 XML 特殊字符 |

## 核心代码框架

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

doc = SimpleDocTemplate('output.pdf', pagesize=A4,
    topMargin=15*mm, bottomMargin=15*mm,
    leftMargin=15*mm, rightMargin=15*mm)

# 所有文本内容 → Paragraph + esc()
story = [
    Paragraph('标题', ParagraphStyle('T', fontName=FONT, fontSize=16)),
    Paragraph('正文', ParagraphStyle('B', fontName=FONT, fontSize=8.5)),
]
doc.build(story)
```

## Verification Checklist

- [ ] Read the full content to ensure understanding
- [ ] Verify all code examples are syntactically correct
- [ ] Check that all referenced files exist
- [ ] Test the workflow with a simple input

## Common Pitfalls

1. **Missing dependencies**: Ensure all required tools are installed before starting.
2. **Wrong input format**: Verify input matches the expected format before processing.
3. **Version mismatch**: Check version compatibility between tools.
