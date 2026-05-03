# PowerPoint (.pptx) 完整操作指南

> 库：`python-pptx` | 安装：`pip install python-pptx`

## 基础操作

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)  # 宽屏 16:9
prs.slide_height = Inches(7.5)
```

## 幻灯片布局

```python
# 可用布局
# 0 = 标题幻灯片
# 1 = 标题+内容
# 2 = 节标题
# 3 = 两栏内容
# 4 = 比较
# 5 = 仅标题
# 6 = 空白
# 7 = 标题+竖排文字
# 8 = 竖排标题+文字

slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(slide_layout)
```

## 标题页

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
title = slide.shapes.title
title.text = "演示标题"
title.text_frame.paragraphs[0].font.size = Pt(44)
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x33, 0x33, 0x33)
title.text_frame.paragraphs[0].font.bold = True

subtitle = slide.placeholders[1]
subtitle.text = "副标题 / 作者 / 日期"
```

## 内容页

```python
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "章节标题"

body = slide.placeholders[1]
tf = body.text_frame
tf.text = "要点一"
p = tf.add_paragraph()
p.text = "要点二"
p.level = 0
p = tf.add_paragraph()
p.text = "子要点"
p.level = 1
```

## 自定义文本框

```python
txBox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(4))
tf = txBox.text_frame
tf.word_wrap = True
tf.auto_size = True  # 自动调整大小

p = tf.paragraphs[0]
p.text = "标题"
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = RGBColor(0x44, 0x72, 0xC4)

p = tf.add_paragraph()
p.text = "正文内容..."
p.font.size = Pt(18)
p.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
p.space_after = Pt(12)
```

## 表格

```python
rows, cols = 4, 3
left = Inches(2)
top = Inches(2)
width = Inches(9)
height = Inches(3)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# 设置列宽
table.columns[0].width = Inches(3)
table.columns[1].width = Inches(3)
table.columns[2].width = Inches(3)

# 填充数据
table.cell(0, 0).text = "项目"
table.cell(0, 1).text = "数值"
table.cell(0, 2).text = "备注"

# 标题行样式
for col in range(cols):
    cell = table.cell(0, col)
    cell.text_frame.paragraphs[0].font.bold = True
    cell.text_frame.paragraphs[0].font.size = Pt(14)
    fill = cell.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0x44, 0x72, 0xC4)
    cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
```

## 图片

```python
# 添加图片
pic = slide.shapes.add_picture('chart.png', Inches(2), Inches(3), width=Inches(9))

# 圆角图片（通过裁剪）
from pptx.util import Emu
pic.crop_left = 0
pic.crop_right = 0
```

## 形状

```python
# 矩形
shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(3), Inches(2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x44, 0x72, 0xC4)
shape.line.color.rgb = RGBColor(0x2F, 0x54, 0x96)
shape.line.width = Pt(2)

# 添加文字
tf = shape.text_frame
tf.text = "标注文字"
tf.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
tf.paragraphs[0].font.size = Pt(14)
tf.paragraphs[0].alignment = PP_ALIGN.CENTER

# 箭头
connector = slide.shapes.add_connector(
    MSO_SHAPE.STRAIGHT_CONNECTOR,
    Inches(4), Inches(2), Inches(6), Inches(2)
)
connector.line.color.rgb = RGBColor(0x44, 0x72, 0xC4)
connector.line.width = Pt(3)
```

## 背景

```python
# 纯色背景
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0xF5, 0xF5, 0xF5)

# 渐变背景
fill.gradient()
fill.gradient_stops[0].color.rgb = RGBColor(0x44, 0x72, 0xC4)
fill.gradient_stops[1].color.rgb = RGBColor(0x63, 0xBE, 0x7B)
```

## 母版操作

```python
# 修改母版影响所有幻灯片
slide_master = prs.slide_masters[0]

# 在母版添加 Logo
logo = slide_master.shapes.add_picture(
    'logo.png',
    Inches(0.5), Inches(0.3), width=Inches(1.5)
)

# 修改母版标题样式
for shape in slide_master.placeholders:
    if shape.placeholder_format.idx == 0:  # 标题
        shape.text_frame.paragraphs[0].font.size = Pt(32)
        shape.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x44, 0x72, 0xC4)
```

## 保存

```python
prs.save('output.pptx')
```

## 读取与修改

```python
prs = Presentation('existing.pptx')

for i, slide in enumerate(prs.slides):
    print(f"Slide {i+1}:")
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(f"  {shape.text}")
        if shape.has_table:
            print(f"  Table: {shape.table.rows.__len__()} rows")

prs.save('modified.pptx')
```
