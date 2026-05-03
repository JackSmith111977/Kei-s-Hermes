# Detailed Reference

## 六、Mermaid 图片嵌入

### 生成图片
```bash
mmdc -i input.mmd -o output.png -w 800 --backgroundColor transparent \
  --puppeteerConfigFile ~/.mmdc.json
```

### ~/.mmdc.json
```json
{ "executablePath": "/usr/bin/google-chrome", "args": ["--no-sandbox"] }
```

### 嵌入 PDF
```python
from reportlab.lib.utils import ImageReader
img = ImageReader("diagram.png")
img_width = 160 * mm
img_height = img_width * img.getSize()[1] / img.getSize()[0]
story.append(Image("diagram.png", width=img_width, height=img_height))
```

## 七、页眉页脚

```python
def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    # 页眉
    canvas.setFont("WQY", 8)
    canvas.setFillColor(HexColor('#888888'))
    canvas.drawString(20*mm, h - 12*mm, "文档标题")
    canvas.drawRightString(w - 20*mm, h - 12*mm, "子标题")
    # 分隔线
    canvas.setStrokeColor(HexColor('#DDDDDD'))
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, h - 15*mm, w - 20*mm, h - 15*mm)
    # 页脚
    canvas.drawCentredString(w/2, 12*mm, f"— {canvas.getPageNumber()} —")
    canvas.line(20*mm, 18*mm, w - 20*mm, 18*mm)
    canvas.restoreState()
```

## 八、完整骨架

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("WQY", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"))

MARGIN = 20 * mm
doc = SimpleDocTemplate(output_path, pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=20*mm, bottomMargin=20*mm)

BODY = ParagraphStyle("body", fontName="WQY", fontSize=9.5, leading=14, spaceAfter=3*mm)
H1 = ParagraphStyle("h1", fontName="WQY", fontSize=20, leading=26, spaceBefore=6*mm, spaceAfter=4*mm)

story = []
# ... 构建内容 ...
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
```

## 九、经验教训

1. **黑块 = Helvetica 渲染中文** → 第一时间注册中文字体
2. **每章 PageBreak = 空旷** → 用智能分页矩阵
3. **手动计算 rowHeights = 灾难** → 让 reportlab 自动计算
4. **patch 改大段代码 = 污染** → 用 write_file 重写
