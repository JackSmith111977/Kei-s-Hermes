# PDF 完整操作指南

> 库：`fpdf2` | 安装：`pip install fpdf2`
> 备选：`reportlab`（更强大但更复杂）

## fpdf2 基础

```python
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'Document Title', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

pdf = PDF()
pdf.alias_nb_pages()
pdf.add_page()

# 中文支持（需要中文字体）
pdf.add_font('SimSun', '', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', uni=True)
pdf.set_font('SimSun', '', 12)

pdf.cell(0, 10, 'Hello World', 0, 1)
pdf.ln(5)

pdf.output('output.pdf')
```

## 表格

```python
# 简单表格
pdf.set_font('Helvetica', 'B', 10)
col_widths = [60, 60, 60]
for header in ['Col1', 'Col2', 'Col3']:
    pdf.cell(col_widths[0], 8, header, 1, 0, 'C')
pdf.ln()
pdf.set_font('Helvetica', '', 10)
for i in range(10):
    for j, width in enumerate(col_widths):
        pdf.cell(width, 7, f'Data {i}-{j}', 1)
    pdf.ln()
```

## 多列布局

```python
# 双列
pdf.set_left_margin(25)
pdf.set_right_margin(25)
pdf.add_page()

# 列 1
pdf.set_x(25)
pdf.set_y(40)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(75, 5, 'Left column text...', 0, 'L')
pdf.ln(10)

# 列 2
pdf.set_x(110)
pdf.set_y(40)
pdf.multi_cell(75, 5, 'Right column text...', 0, 'L')
```

## 图片

```python
pdf.image('chart.png', x=10, y=30, w=150)
pdf.image('logo.png', x=10, y=10, w=30)
```

## 链接

```python
pdf.set_text_color(0, 0, 255)
pdf.set_font('', 'U')
pdf.cell(0, 10, 'Click here', 0, 1, '', False, 'https://example.com')
pdf.set_text_color(0, 0, 0)
```

## ReportLab（高级）

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib import colors

doc = SimpleDocTemplate("output.pdf", pagesize=A4,
                        leftMargin=25*mm, rightMargin=25*mm,
                        topMargin=25*mm, bottomMargin=25*mm)

styles = getSampleStyleSheet()
story = []

# 标题
story.append(Paragraph("Title", styles['Title']))
story.append(Spacer(1, 12))

# 正文
story.append(Paragraph("Body text content...", styles['Normal']))

# 表格
data = [['Col1', 'Col2', 'Col3'],
        ['A', 'B', 'C']]
table = Table(data, colWidths=[50*mm, 50*mm, 50*mm])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))
story.append(table)

doc.build(story)
```

## PDF 转换

```bash
# HTML → PDF
wkhtmltopdf --page-size A4 --margin-top 20mm input.html output.pdf

# Python
import pdfkit
pdfkit.from_file('input.html', 'output.pdf')

# LibreOffice
libreoffice --headless --convert-to pdf input.docx
```
