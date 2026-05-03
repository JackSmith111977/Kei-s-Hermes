---
name: docx-guide
description: Word (.docx) 文档操作原子技能。使用 python-docx 创建、编辑、美化 Word 文档。
triggers:
- docx guide
- docx-guide
metadata:
  hermes:
    tags:
    - word
    - docx
    - document
    - office
    category: productivity
    skill_type: doc-generation
    format: docx
---
# Word (.docx) 原子操作技能

> 库：`python-docx` | 安装：`pip install python-docx`
> 默认使用中文，除非用户特意说明。

## 快速开始

```python
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# 页面设置（A4）
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.left_margin = Inches(1)
section.right_margin = Inches(1)

# 默认样式（中文）
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
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
```

## 图片

```python
doc.add_picture('image.png', width=Inches(4))

# 居中图片
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

# 页脚（含页码）— 见 references/docx-guide.md 完整代码
```

## 目录

```python
# 使用标题样式后插入 TOC 字段
# 完整代码见 references/docx-guide.md
```

## 代码块与引用样式

```python
def add_code_block(doc, code_text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    for line in code_text.split('\n'):
        run = p.add_run(line + '\n')
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
    # 背景色通过段落底纹设置
    from docx.oxml import OxmlElement
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), 'F5F5F5')
    shading.set(qn('w:val'), 'clear')
    p._p.get_or_add_pPr().append(shading)

def add_quote(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.5)
    run = p.add_run(text)
    run.italic = True
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
```

## 读取与修改

```python
doc = Document('existing.docx')
for para in doc.paragraphs:
    print(para.text, para.style.name)
for table in doc.tables:
    for row in table.rows:
        print([cell.text for cell in row.cells])
doc.save('modified.docx')
```

## 详细参考

完整代码示例和高级技巧见 `references/docx-guide.md`（在 doc-design skill 目录中）。
