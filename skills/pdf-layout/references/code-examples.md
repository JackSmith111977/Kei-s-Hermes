# ReportLab 高级排版代码示例

## 一、页眉页脚完整实现

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor

def make_header_footer(doc_title, version, date):
    """创建页眉页脚回调函数工厂"""
    
    def header_footer(canvas, doc):
        canvas.saveState()
        w = A4[0]
        
        # ── 页眉 ──
        canvas.setFont('STSong-Light', 8)
        canvas.setFillColor(HexColor('#6c757d'))
        canvas.drawString(20*mm, A4[1] - 12*mm, doc_title)
        canvas.drawRightString(w - 20*mm, A4[1] - 12*mm, date)
        
        # 页眉分隔线
        canvas.setStrokeColor(HexColor('#dee2e6'))
        canvas.setLineWidth(0.5)
        canvas.line(20*mm, A4[1] - 16*mm, w - 20*mm, A4[1] - 16*mm)
        
        # ── 页脚 ──
        canvas.line(20*mm, 14*mm, w - 20*mm, 14*mm)
        
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(w / 2, 8*mm, f"— {page_num} —")
        canvas.drawRightString(w - 20*mm, 8*mm, f"v{version}")
        
        canvas.restoreState()
    
    return header_footer

# 使用
hf = make_header_footer("Hermes Agent 架构指南", "5.0.0", "2026-05-03")
doc.build(story, onFirstPage=hf, onLaterPages=hf)
```

## 二、带书签的目录

```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

def toc_entry(text, level=0):
    """生成目录条目（带 PDF 书签跳转）"""
    style = ParagraphStyle(
        f'TOC{level}',
        fontSize=12 - level * 2,
        leading=18 - level * 2,
        leftIndent=level * 15,
        spaceAfter=2,
    )
    return Paragraph(
        f'<b>{text}</b>',
        style
    )

def bookmark_heading(text, bookmark_key, style):
    """带书签的标题"""
    return Paragraph(
        f'<a name="{bookmark_key}"/>{text}',
        style
    )

# 在 onPage 回调中添加书签
def add_bookmarks(canvas, doc):
    canvas.addOutlineEntry('第1章', 'chapter_1', level=0)
    canvas.bookmarkPage('chapter_1')
```

## 三、高级表格样式

```python
from reportlab.platypus import Table, TableStyle
from reportlab.lib.colors import HexColor, white

def professional_table(data, col_widths, header_color, row_colors=None, 
                       font_name='STSong-Light', font_size=8):
    """专业表格：斑马纹 + 表头 + 圆角效果"""
    
    # 转义所有单元格
    processed = []
    for row in data:
        processed.append([
            Paragraph(str(cell).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'),
                      ParagraphStyle('cell', fontName=font_name, fontSize=font_size))
            for cell in row
        ])
    
    table = Table(processed, colWidths=col_widths)
    
    style_commands = [
        # 表头
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTSIZE', (0, 0), (-1, 0), font_size + 1),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4*mm),
        ('TOPPADDING', (0, 0), (-1, 0), 4*mm),
        
        # 数据行
        ('FONTSIZE', (0, 1), (-1, -1), font_size),
        ('TOPPADDING', (0, 1), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 3*mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3*mm),
        
        # 网格线
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#dee2e6')),
        
        # 对齐
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # 第一列左对齐
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),   # 其余左对齐
    ]
    
    # 斑马纹
    if row_colors:
        for i, color in enumerate(row_colors):
            style_commands.append(('BACKGROUND', (0, i+1), (-1, i+1), color))
    else:
        style_commands.append(
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')])
        )
    
    table.setStyle(TableStyle(style_commands))
    return table
```

## 四、代码块样式

```python
def styled_code_block(code_lines, language="", max_width=160*mm):
    """生成带背景色的代码块"""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.colors import HexColor
    
    bg_color = HexColor('#f4f4f4')
    border_color = HexColor('#e0e0e0')
    
    # 代码文本
    code_text = '\n'.join(code_lines) if isinstance(code_lines, list) else code_lines
    
    code_para = Paragraph(
        code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
        ParagraphStyle(
            'CodeText',
            fontName='Courier',
            fontSize=7,
            leading=10,
            textColor=HexColor('#333333'),
        )
    )
    
    # 用 Table 实现背景色和内边距
    table = Table([[code_para]], colWidths=[max_width])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 4*mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4*mm),
    ]))
    
    return table
```

## 五、双栏布局

```python
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.units import mm

class TwoColumnPDF(BaseDocTemplate):
    """双栏 PDF 模板"""
    
    def __init__(self, filename, left_margin=20*mm, right_margin=20*mm,
                 top_margin=25*mm, bottom_margin=20*mm, gutter=5*mm, **kw):
        
        super().__init__(filename, pagesize=A4,
                        leftMargin=left_margin, rightMargin=right_margin,
                        topMargin=top_margin, bottomMargin=bottom_margin, **kw)
        
        available_width = self.width - gutter
        col_width = available_width / 2
        
        col1 = Frame(
            self.leftMargin, self.bottomMargin,
            col_width, self.height,
            id='col1',
            leftPadding=0, rightPadding=gutter/2,
            topPadding=0, bottomPadding=0
        )
        col2 = Frame(
            self.leftMargin + col_width + gutter, self.bottomMargin,
            col_width, self.height,
            id='col2',
            leftPadding=gutter/2, rightPadding=0,
            topPadding=0, bottomPadding=0
        )
        
        template = PageTemplate(
            id='TwoCol',
            frames=[col1, col2],
            onPage=self._header_footer
        )
        self.addPageTemplates(template)
    
    def _header_footer(self, canvas, doc):
        # 页眉页脚实现（同上文）
        pass

# 使用
doc = TwoColumnPDF("output.pdf")
doc.build(story)
```

## 六、水印实现

```python
def add_watermark(text="DRAFT", opacity=0.1, angle=45, font_size=60):
    """创建水印回调"""
    def watermark(canvas, doc):
        canvas.saveState()
        
        # 设置透明度（需要 PDF 1.4+）
        canvas.setFont('Helvetica-Bold', font_size)
        canvas.setFillColorRGB(0.9, 0.9, 0.9, alpha=opacity)
        canvas.setStrokeColorRGB(0.9, 0.9, 0.9, alpha=opacity)
        
        # 居中旋转
        canvas.translate(A4[0]/2, A4[1]/2)
        canvas.rotate(angle)
        canvas.drawCentredString(0, 0, text)
        
        canvas.restoreState()
    return watermark

# 使用
doc.build(story, onFirstPage=add_watermark("DRAFT"), onLaterPages=add_watermark("DRAFT"))
```

## 七、PDF 元数据完整设置

```python
from reportlab.platypus import SimpleDocTemplate

doc = SimpleDocTemplate(
    "output.pdf",
    pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm,
    topMargin=25*mm, bottomMargin=20*mm,
    
    # ── PDF 元数据 ──
    title="文档标题",
    author="作者名",
    subject="文档主题/描述",
    creator="创建工具（如 reportlab v4.x）",
    producer="PDF 生成器（如 ReportLab PDF Library）",
    keywords=["关键词1", "关键词2", "关键词3"],
)

# 构建后可用 pypdf 补充更多元数据
from pypdf import PdfReader, PdfWriter

def update_metadata(input_path, output_path, metadata):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata(metadata)
    with open(output_path, "wb") as f:
        writer.write(f)

update_metadata("output.pdf", "output_final.pdf", {
    "/Title": "文档标题",
    "/Author": "作者名",
    "/Subject": "文档描述",
    "/Keywords": "关键词1, 关键词2",
    "/Creator": "reportlab v4.2.0 + pdf-layout skill v1.0.0",
    "/Producer": "pdf-layout skill",
    "/Version": "5.0.0",
    "/Date": "2026-05-03",
})
```
