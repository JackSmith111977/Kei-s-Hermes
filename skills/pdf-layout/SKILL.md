---
name: pdf-layout
version: "1.0.0"
author: 小喵
license: MIT
description: |
  专业 PDF 排版设计与生成技能。涵盖 reportlab 高级排版技巧、中文 PDF 生成、
  页眉页脚、目录、表格样式、代码块、多栏布局、水印、元数据管理等。
  当用户需要生成高质量 PDF 文档、中文 PDF、技术文档 PDF、报告 PDF 时使用此技能。
metadata:
  hermes:
    tags: [pdf, reportlab, layout, typography, chinese, toc, header-footer, table-style]
    related_skills: [doc-design]
    category: productivity
    skill_type: doc-generation
    design_pattern: generator
---

# 专业 PDF 排版设计技能（reportlab 高级）

## 触发条件（When to Use）

**使用此 skill 当：**
- 用户需要生成高质量 PDF 文档（技术文档、报告、指南）
- 用户需要中文 PDF（含 CJK 字符）
- 涉及页眉页脚、目录、书签、多栏布局、水印等高级排版
- 需要表格样式优化（斑马纹、表头底色、单元格内边距）
- 需要代码块样式（等宽字体、背景色、语法高亮）
- 需要 PDF 元数据管理（版本号、作者、关键词）

**不使用此 skill 当：**
- 简单文本 PDF（直接用 fpdf2）
- 非 PDF 格式文档（用 doc-design skill）

---

## 一、核心排版原则

### 1.1 字体规则
```python
# ✅ 正确：中文使用 CIDFont（避免黑色方块）
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
BODY_FONT = "STSong-Light"

# ❌ 错误：TTFont 不支持完整 CJK 字符集
# pdfmetrics.registerFont(TTFont('WQY', '/path/to/wqy.ttc'))
```

### 1.2 字号层级（A4 页面）
| 层级 | 字号 | 行高 | 用途 |
|------|------|------|------|
| 封面标题 | 28-36pt | 34-42pt | 文档名称 |
| H1 章节 | 18-22pt | 24-28pt | 一级标题 |
| H2 小节 | 14-16pt | 18-22pt | 二级标题 |
| H3 细分 | 11-13pt | 15-17pt | 三级标题 |
| 正文 | 9-11pt | 14-16pt | 正文内容 |
| 代码 | 8-9pt | 12-14pt | 代码片段 |
| 注释 | 7-8pt | 10-12pt | 图表注释 |

### 1.3 配色方案（60-30-10 法则）
```
深色科技风（推荐）：
  背景: #FFFFFF      文字: #212529      标题: #1a1a2e
  强调: #e94560      辅助: #0f3460      边框: #dee2e6
  代码背景: #f4f4f4  表格交替: #f8f9fa

经典商务风：
  背景: #FFFFFF      文字: #333333      标题: #2B579A
  强调: #ED7D31      辅助: #4472C4      边框: #D9E2F3
```

### 1.4 间距规则
- **段前距**：H1=12mm, H2=8mm, H3=5mm, 正文=0mm
- **段后距**：H1=4mm, H2=3mm, H3=2mm, 正文=3mm
- **行高**：字号 × 1.4-1.6（中文需要更大行高）
- **页边距**：20-25mm（A4）
- **单元格内边距**：3-4mm

---

## 二、中文 PDF 渲染

### 2.1 字体选择优先级
```python
# 方案1（最佳）：UnicodeCIDFont - 内置 CJK 支持
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# 方案2（备选）：TrueType 字体（需要系统安装）
from reportlab.pdfbase.ttfonts import TTFont
# 注意：wqy-zenhei.ttc 是 CFF 轮廓，reportlab 不支持！
# 需要检测 TTC 是否为 CFF 轮廓（见 2.2）

# 方案3（兜底）：DejaVuSans（不支持中文，仅英文）
```

### 2.2 TTC 文件 CFF 检测
```python
import struct

def _is_cff_ttc(filepath):
    """检测 TTC 文件是否包含 CFF 轮廓（reportlab 不支持）"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(4)
            if header != b'ttcf':
                return False
            f.read(4)  # numFonts
            first_offset = struct.unpack('>I', f.read(4))[0]
            f.seek(first_offset)
            sf_version = f.read(4)
            return sf_version == b'OTTO'  # CFF 轮廓
    except:
        return False
```

### 2.3 字符串转义（必须！）
```python
def esc(text):
    """XML 转义，防止 reportlab Paragraph 解析错误"""
    if not text: return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
```

### 2.4 Table 单元格必须用 Paragraph 包装
```python
# ✅ 正确：所有字符串单元格转为 Paragraph
processed_row = [Paragraph(esc(cell), font_style) if isinstance(cell, str) else cell for cell in row]

# ❌ 错误：直接传字符串（使用默认字体，中文显示方块）
```

---

## 三、表格高级样式

### 3.1 斑马纹 + 表头底色
```python
def make_table(data, col_widths, header_color=PRIMARY, row_colors=None):
    # 所有单元格转为 Paragraph
    processed = [[Paragraph(esc(c), body_style) if isinstance(c, str) else c for c in row] for row in data]
    
    style = [
        # 表头底色
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        # 表头白字
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        # 外框 + 内框
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        # 垂直居中
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # 字号
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        # 内边距
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 3*mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3*mm),
    ]
    
    # 斑马纹
    if row_colors:
        for i, c in enumerate(row_colors):
            style.append(('BACKGROUND', (0, i+1), (-1, i+1), c))
    else:
        style.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]))
    
    table = Table(processed, colWidths=col_widths)
    table.setStyle(TableStyle(style))
    return table
```

### 3.2 单元格合并
```python
# 跨列合并
('SPAN', (0, 0), (2, 0))  # 合并第0行的0-2列

# 跨行合并
('SPAN', (0, 1), (0, 3))  # 合并第0列的1-3行
```

### 3.3 条件格式
```python
# 根据内容动态设置颜色
for i, row in enumerate(data[1:], 1):
    if '失败' in str(row[1]) or 'FAIL' in str(row[1]):
        style.append(('BACKGROUND', (1, i), (1, i), HexColor('#ffebee')))
        style.append(('TEXTCOLOR', (1, i), (1, i), HexColor('#c62828')))
```

---

## 四、页眉页脚

### 4.1 使用 onPage 回调
```python
def header_footer(canvas, doc):
    canvas.saveState()
    
    # ── 页眉 ──
    # 左侧：书名
    canvas.setFont(BODY_FONT, 8)
    canvas.setFillColor(HexColor('#6c757d'))
    canvas.drawString(20*mm, A4[1] - 12*mm, "Hermes Agent 架构指南")
    
    # 右侧：日期
    canvas.drawRightString(A4[0] - 20*mm, A4[1] - 12*mm, "2026-05-03")
    
    # 页眉分隔线
    canvas.setStrokeColor(HexColor('#dee2e6'))
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, A4[1] - 16*mm, A4[0] - 20*mm, A4[1] - 16*mm)
    
    # ── 页脚 ──
    # 页脚分隔线
    canvas.line(20*mm, 14*mm, A4[0] - 20*mm, 14*mm)
    
    # 居中页码
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(A4[0] / 2, 8*mm, f"— {page_num} —")
    
    # 右侧版本
    canvas.drawRightString(A4[0] - 20*mm, 8*mm, "v5.0.0")
    
    canvas.restoreState()

# 构建时传入
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
```

### 4.2 首页不同页眉页脚
```python
def first_page(canvas, doc):
    # 首页：无页眉，只有页脚
    canvas.saveState()
    canvas.setFont(BODY_FONT, 8)
    canvas.drawCentredString(A4[0] / 2, 8*mm, f"— {canvas.getPageNumber()} —")
    canvas.restoreState()

def later_pages(canvas, doc):
    # 后续页：完整页眉页脚
    header_footer(canvas, doc)

doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
```

---

## 五、目录与书签

### 5.1 手动目录（静态页码）
```python
# 在目录页列出章节和页码（需手动维护）
toc_items = [
    ("1", "项目概览", "3"),
    ("2", "架构设计", "5"),
    ("3", "核心模块", "8"),
]
for num, title, page in toc_items:
    story.append(Paragraph(f'<b>{num}. {esc(title)}</b>  ...........  {page}', toc_style))
```

### 5.2 动态目录（使用 TableOfContents flowable）
```python
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate

# 1. 创建 ToC flowable
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle('TOC Level 0', fontSize=12, leading=16, leftIndent=0),
    ParagraphStyle('TOC Level 1', fontSize=10, leading=14, leftIndent=15),
]
story.append(toc)

# 2. 在章节标题处添加书签
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

def h1_with_bookmark(text):
    """带书签的 H1 标题"""
    bookmark = f"chapter_{text.replace(' ', '_')}"
    return Paragraph(
        f'<b><a name="{bookmark}"/></b>{esc(text)}',
        h1_style
    )

# 3. 在 ToC 后添加 outline 条目
# canvas.bookmarkPage(key) + canvas.addOutlineEntry(title, key)
```

### 5.3 书签导航（PDF Outline）
```python
def add_bookmark(canvas, doc):
    """在特定位置添加书签"""
    canvas.bookmarkPage('chapter1')
    canvas.addOutlineEntry('第1章 项目概览', 'chapter1', level=0)

# 在 onPage 回调中根据页码判断添加书签
```

---

## 六、代码块样式

### 6.1 等宽字体代码块
```python
def code_block(code_text, language=""):
    """生成带背景色的代码块"""
    # 代码样式
    code_style = ParagraphStyle(
        'CodeBlock',
        fontName='Courier',  # reportlab 内置等宽字体
        fontSize=8,
        leading=12,
        textColor=HexColor('#212529'),
        backColor=HexColor('#f4f4f4'),
        borderPadding=(4*mm, 3*mm, 4*mm, 3*mm),
        leftIndent=5*mm,
        spaceBefore=3*mm,
        spaceAfter=3*mm,
    )
    
    # 语言标签
    if language:
        lang_style = ParagraphStyle('Lang', fontSize=7, textColor=HexColor('#6c757d'))
        elements = [
            Paragraph(esc(f"// {language}"), lang_style),
            Paragraph(esc(code_text), code_style),
        ]
    else:
        elements = [Paragraph(esc(code_text), code_style)]
    
    return elements

# 使用
story.extend(code_block("pip install reportlab", "bash"))
```

### 6.2 多行代码块
```python
def multiline_code_block(lines, language=""):
    """多行代码块，保持换行"""
    code_text = '\n'.join(lines)
    return code_block(code_text, language)
```

---

## 七、多栏布局

### 7.1 BaseDocTemplate + Frame
```python
from reportlab.platypus.doctemplate import BaseDocTemplate
from reportlab.lib.units import mm

class TwoColumnDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        
        # 定义两栏 Frame
        col_width = (self.width - 10*mm) / 2  # 5mm 间距
        frame1 = Frame(
            self.leftMargin, self.bottomMargin,
            col_width, self.height,
            id='col1', leftPadding=0, rightPadding=2.5*mm,
            topPadding=0, bottomPadding=0
        )
        frame2 = Frame(
            self.leftMargin + col_width + 5*mm, self.bottomMargin,
            col_width, self.height,
            id='col2', leftPadding=2.5*mm, rightPadding=0,
            topPadding=0, bottomPadding=0
        )
        
        # PageTemplate
        template = PageTemplate(
            id='TwoCol',
            frames=[frame1, frame2],
            onPage=header_footer
        )
        self.addPageTemplates(template)

# 使用
doc = TwoColumnDoc("output.pdf", pagesize=A4, leftMargin=20*mm, rightMargin=20*mm)
doc.build(story)
```

### 7.2 混合布局（全宽 + 双栏）
```python
# 使用 NextPageTemplate 切换布局
from reportlab.platypus.doctemplate import PageTemplate, NextPageTemplate

# 首页模板（全宽）
front_template = PageTemplate(id='Front', frames=[full_frame], onPage=first_page)
# 正文模板（双列）
body_template = PageTemplate(id='Body', frames=[col1_frame, col2_frame], onPage=later_pages)

doc.addPageTemplates([front_template, body_template])

# 在 story 中切换
story.append(NextPageTemplate('Body'))
```

---

## 八、水印与背景

### 8.1 文字水印（每页）
```python
def watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 60)
    canvas.setFillColor(HexColor('#f0f0f0'))
    canvas.setStrokeColor(HexColor('#f0f0f0'))
    
    # 居中旋转水印
    canvas.translate(A4[0]/2, A4[1]/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "DRAFT")
    
    canvas.restoreState()

doc.build(story, onFirstPage=watermark, onLaterPages=watermark)
```

### 8.2 图片水印/背景
```python
def image_background(canvas, doc):
    canvas.saveState()
    # 绘制半透明背景图
    canvas.setFillAlpha(0.1)
    canvas.drawImage('/path/to/logo.png', 
                     x=A4[0]/2 - 50*mm, y=A4[1]/2 - 50*mm,
                     width=100*mm, height=100*mm,
                     mask='auto', preserveAspectRatio=True)
    canvas.setFillAlpha(1.0)
    canvas.restoreState()
```

---

## 九、PDF 元数据

### 9.1 基本元数据
```python
doc = SimpleDocTemplate(
    output_path, pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm,
    topMargin=20*mm, bottomMargin=20*mm,
    # ── 元数据 ──
    title='Hermes Agent 架构指南',
    author='小喵 AI',
    subject='Hermes Agent 深度架构解析与设计哲学',
    creator='reportlab + pdf-layout skill',
    producer='ReportLab PDF Library',
    keywords=['Hermes', 'AI Agent', '架构设计', 'Python', 'reportlab'],
)
```

### 9.2 版本号管理（脚本内）
```python
# 在脚本顶部定义版本
__version__ = "5.0.0"
__date__ = "2026-05-03"
__author__ = "小喵 AI"

# 封面显示版本
info_data = [
    [hp("版本", style), hp(f"v{__version__}", style)],
    [hp("日期", style), hp(__date__, style)],
]

# PDF 文件名包含版本
output_path = f'/path/to/Hermes_Architecture_Guide_v{__version__}.pdf'
```

### 9.3 使用 pypdf 修改已有 PDF 元数据
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# 修改元数据
writer.add_metadata({
    "/Title": "Hermes Agent 架构指南",
    "/Author": "小喵 AI",
    "/Subject": "架构深度解析",
    "/Keywords": "Hermes, AI Agent, 架构",
    "/Creator": f"reportlab v{reportlab.Version}",
    "/Producer": "pdf-layout skill v1.0.0",
    "/Version": "5.0.0",
})

with open("output.pdf", "wb") as f:
    writer.write(f)
```

---

## 十、图片处理

### 10.1 自适应缩放
```python
def add_image(filepath, max_width=160*mm, max_height=None, caption=None):
    """图片自适应缩放，保持比例"""
    elements = []
    if not os.path.exists(filepath):
        return elements
    
    img = Image(filepath)
    aspect = img.imageWidth / img.imageHeight
    
    if aspect > 1:  # 横图
        img.drawWidth = max_width
        img.drawHeight = max_width / aspect
    else:  # 竖图
        img.drawHeight = max_width
        img.drawWidth = max_width * aspect
    
    # 高度限制
    if max_height and img.drawHeight > max_height:
        img.drawHeight = max_height
        img.drawWidth = max_height * aspect
    
    elements.append(img)
    elements.append(Spacer(1, 2*mm))
    
    if caption:
        cap_style = S('Caption', fontSize=8, textColor=MEDIUM_GRAY, alignment=TA_CENTER)
        elements.append(Paragraph(esc(caption), cap_style))
    
    return elements
```

### 10.2 图片居中
```python
# 使用 Table 居中图片
from reportlab.platypus import Table

img = Image(filepath, width=120*mm, height=80*mm)
center_table = Table([[img]], colWidths=[160*mm])
center_table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))
```

---

## 十一、KeepTogether 防分页截断

### 11.1 标题不分页
```python
from reportlab.platypus import KeepTogether

# 方法1：手动包裹
story.append(KeepTogether([
    h1("第1章 项目概览"),
    hr(HIGHLIGHT),
    body("第一章正文内容..."),
]))

# 方法2：在样式中设置（ParagraphStyle 无此属性，需用 KeepTogether）
```

### 11.2 表格不分页
```python
# 小表格用 KeepTogether
story.append(KeepTogether([table]))

# 大表格用 LongTable（自动跨页）
from reportlab.platypus import LongTable
# LongTable 支持表头在每页重复
```

---

## 十二、完整脚本模板

### 12.1 最小可运行模板
```python
#!/usr/bin/env python3
"""PDF 生成脚本模板 - 中文版"""

__version__ = "1.0.0"
__date__ = "2026-05-03"
__author__ = "小喵 AI"

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, Image, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os

# ── 字体 ──
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
BODY_FONT = "STSong-Light"

# ── 颜色 ──
PRIMARY = HexColor('#1a1a2e')
ACCENT = HexColor('#0f3460')
HIGHLIGHT = HexColor('#e94560')
LIGHT_BG = HexColor('#f8f9fa')
BORDER_COLOR = HexColor('#dee2e6')
MEDIUM_GRAY = HexColor('#6c757d')
DARK_TEXT = HexColor('#212529')

# ── 样式 ──
def S(name, **kw):
    return ParagraphStyle(name, fontName=BODY_FONT, **kw)

body_style = S('Body', fontSize=10, leading=16, textColor=DARK_TEXT, spaceAfter=3*mm)
h1_style = S('H1', fontSize=20, leading=26, textColor=PRIMARY, spaceBefore=12*mm, spaceAfter=4*mm)

def esc(text):
    if not text: return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# ── 生成 ──
def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title='文档标题',
        author=__author__,
        subject='文档描述',
        creator=f'reportlab + pdf-layout skill v{__version__}',
    )
    
    story = []
    story.append(Paragraph(esc("标题"), h1_style))
    story.append(Paragraph(esc("正文内容..."), body_style))
    
    doc.build(story)
    print(f"PDF 生成成功: {output_path}")

build_pdf(f'/path/to/output_v{__version__}.pdf')
```

---

## 十三、常见错误与解决方案

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 中文显示黑色方块 | 字体不支持 CJK | 使用 `UnicodeCIDFont('STSong-Light')` |
| Table 中文方块 | 单元格未用 Paragraph 包装 | 所有字符串转为 `Paragraph(esc(cell), style)` |
| `TTFError: postscript outlines not supported` | TTC 文件是 CFF 轮廓 | 检测并跳过 CFF TTC，或用 CIDFont |
| `&` `<` `>` 导致 XML 解析错误 | 特殊字符未转义 | 使用 `esc()` 函数转义 |
| 标题被分页截断 | 默认允许分页 | 用 `KeepTogether` 包裹标题+首段 |
| 图片超出页面 | 未缩放 | 使用 `add_image()` 自适应缩放 |
| 页眉页脚被裁切 | 边距不足 | 确保 `topMargin` ≥ 20mm |
| 目录页码不准确 | 静态页码 | 使用 `TableOfContents` flowable |

---

## 十四、参考资源

- ReportLab 官方文档: https://docs.reportlab.com/
- ReportLab 用户指南 PDF: https://www.reportlab.com/docs/reportlab-userguide.pdf
- RML 用户指南: https://www.reportlab.com/docs/rml2pdf-userguide.pdf
- GitHub 示例: https://github.com/MatthewWilkes/reportlab/tree/master/docs/userguide
- Stack Overflow: 搜索 `reportlab` 标签
