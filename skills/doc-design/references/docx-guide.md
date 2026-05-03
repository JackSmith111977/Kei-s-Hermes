# Word (.docx) 完整操作指南

> 库：`python-docx` | 安装：`pip install python-docx`

## 基础操作

```python
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# === 页面设置（A4） ===
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.left_margin = Inches(1)
section.right_margin = Inches(1)
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)

# === 默认样式 ===
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')  # 中文字体
```

## 标题与段落

```python
doc.add_heading('一级标题', level=0)
doc.add_heading('二级标题', level=1)

p = doc.add_paragraph()
p.paragraph_format.line_spacing = 1.5
p.paragraph_format.space_after = Pt(6)
p.paragraph_format.first_line_indent = Cm(0.74)
p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

run = p.add_run('正文内容')
run.bold = True
run.italic = True
run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
```

## 表格

```python
table = doc.add_table(rows=3, cols=4, style='Table Grid')
for i, row in enumerate(table.rows):
    for j, cell in enumerate(row.cells):
        cell.text = f'({i},{j})'
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 单元格合并
table.cell(0, 0).merge(table.cell(0, 1))

# 表格样式
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_table_border(table):
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        element = OxmlElement(f'w:{edge}')
        element.set(qn('w:val'), 'single')
        element.set(qn('w:sz'), '4')
        borders.append(element)
    tblPr.append(borders)
```

## 图片

```python
doc.add_picture('image.png', width=Inches(4))
# 居中
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run()
run.add_picture('image.png', width=Inches(4))
```

## 页眉页脚

```python
# 页眉
header = section.header
p = header.paragraphs[0]
p.text = '页眉内容'
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 页脚（含页码）
footer = section.footer
p = footer.paragraphs[0]
p.text = '第 '
run = p.add_run()
fldChar = OxmlElement('w:fldChar')
fldChar.set(qn('w:fldCharType'), 'begin')
run._r.append(fldChar)
instrText = OxmlElement('w:instrText')
instrText.text = 'PAGE'
run._r.append(instrText)
fldChar2 = OxmlElement('w:fldChar')
fldChar2.set(qn('w:fldCharType'), 'end')
run._r.append(fldChar2)
run2 = p.add_run(' 页 / 共 ')
run3 = p.add_run()
# ... 类似添加 NUMPAGES
```

## 目录

```python
# 使用标题样式后，插入目录
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn

paragraph = doc.add_paragraph()
run = paragraph.add_run()
fldChar = OxmlElement('w:fldChar')
fldChar.set(qn('w:fldCharType'), 'begin')
run._r.append(fldChar)
instrText = OxmlElement('w:instrText')
instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
instrText.set(qn('xml:space'), 'preserve')
run._r.append(instrText)
fldChar2 = OxmlElement('w:fldChar')
fldChar2.set(qn('w:fldCharType'), 'end')
run._r.append(fldChar2)
```

## 常用样式模板

```python
# 代码块样式
from docx.shared import RGBColor

def add_code_block(doc, code_text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    for line in code_text.split('\n'):
        run = p.add_run(line + '\n')
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    # 背景色（通过段落底纹）
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), 'F5F5F5')
    shading.set(qn('w:val'), 'clear')
    p._p.get_or_add_pPr().append(shading)

# 引用块样式
def add_quote(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.5)
    run = p.add_run(text)
    run.italic = True
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
```

## 保存

```python
doc.save('output.docx')
```

## 读取与修改

```python
doc = Document('existing.docx')

# 遍历段落
for para in doc.paragraphs:
    print(para.text)
    print(para.style.name)

# 遍历表格
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)

# 修改段落
for para in doc.paragraphs:
    if '关键词' in para.text:
        for run in para.runs:
            run.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)

doc.save('modified.docx')
```
