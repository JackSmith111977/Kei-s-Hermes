---
name: pptx-guide
description: PowerPoint (.pptx) 演示文稿操作原子技能。使用 python-pptx 创建专业 PPT，含 2025-2026 设计趋势。
triggers:
- pptx guide
- pptx-guide
metadata:
  hermes:
    tags:
    - powerpoint
    - pptx
    - presentation
    - slides
    category: productivity
    skill_type: doc-generation
    format: pptx
depends_on: []

---
# PowerPoint (.pptx) 原子操作技能

> 库：`python-pptx` | 安装：`pip install python-pptx`
> 默认使用中文，除非用户特意说明。

## 设计趋势（2025-2026）

- **编辑风**：大字体标题 + 高质量图片 + 精简文字
- **大胆排版**：超大标题（48-72pt）占据页面 30-50%
- **克制配色**：主色 1-2 种 + 中性色 + 1 个强调色
- **极简留白**：内容不超过页面 50%

## 配色方案

| 方案 | 主色 | 辅助色 | 强调色 | 背景 |
|------|------|--------|--------|------|
| 经典商务蓝 | #2B579A | #4472C4 | #ED7D31 | #FFFFFF |
| 现代渐变紫 | #667eea | #764ba2 | #f093fb | #FFFFFF |
| 深色科技风 | #4FD1C5 | #81E6D9 | #F6AD55 | #1A202C |
| 莫兰迪高级灰 | #8B9DC3 | #D4A5A5 | #C9B99A | #FAFAFA |

## 快速开始

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)  # 宽屏 16:9
prs.slide_height = Inches(7.5)
```

## 标题页

```python
slide = prs.slides.add_slide(prs.slide_layouts[0])
title = slide.shapes.title
title.text = "演示标题"
title.text_frame.paragraphs[0].font.size = Pt(44)
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
```

## 自定义文本框

```python
txBox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(4))
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "标题"
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = RGBColor(0x44, 0x72, 0xC4)
```

## 表格

```python
table = slide.shapes.add_table(4, 3, Inches(2), Inches(2), Inches(9), Inches(3)).table
# 标题行样式
for col in range(3):
    cell = table.cell(0, col)
    cell.text_frame.paragraphs[0].font.bold = True
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0x44, 0x72, 0xC4)
    cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
```

## 形状与装饰

```python
# 圆角矩形卡片
shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(3), Inches(2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x44, 0x72, 0xC4)

# 渐变背景
background = slide.background
fill = background.fill
fill.gradient()
fill.gradient_stops[0].color.rgb = RGBColor(0x44, 0x72, 0xC4)
fill.gradient_stops[1].color.rgb = RGBColor(0x63, 0xBE, 0x7B)
```

## 辅助函数

```python
def add_rounded_card(slide, left, top, width, height, fill_color):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape

def add_gradient_background(slide, color1, color2):
    fill = slide.background.fill
    fill.gradient()
    fill.gradient_stops[0].color.rgb = color1
    fill.gradient_stops[1].color.rgb = color2
```

## 保存

```python
prs.save('output.pptx')
```

## 设计原则速查

### CRAP 四大原则
| 原则 | 含义 | 实战 |
|------|------|------|
| **C**ontrast 对比 | 要素不同要显著不同 | 字号/颜色/粗细制造差异 |
| **R**epetition 重复 | 跨页统一视觉元素 | 配色/字体/卡片风格贯穿 |
| **A**lignment 对齐 | 无随意放置元素 | 8pt网格系统，间距8倍数 |
| **P**roximity 亲密性 | 相关就近、不相关远离 | 卡片分组，组间留白 |

### 每页检查清单
- [ ] 一个核心想法？（5秒测试）
- [ ] 强视觉层级？（最重要的最大最突出）
- [ ] ≤3种颜色？（不含黑白灰）
- [ ] ≤2种字体？
- [ ] 留白足够？（内容<50%页面）
- [ ] 对齐整洁？（网格感）

## ⚠️ 避坑指南（实战经验）

### 1. Python 字符串中文引号陷阱
在 python-pptx 代码中使用中文双引号（""）会导致 SyntaxError：
```python
# ❌ 语法错误
desc = "对齐是治愈"丑"的良药"
# ✅ 正确
desc = "对齐是治愈「丑」的良药"
desc = '对齐是治愈"丑"的良药'
```

### 2. PPT 转图片检查流程
```bash
# 步骤1：PPT → PDF（使用 LibreOffice）
libreoffice --headless --convert-to pdf input.pptx

# 步骤2：PDF → 图片
pdftoppm -jpeg -r 150 input.pdf slide  # 生成 slide-01.jpg ...

# 注意：DeepSeek vision API 不支持本地图片路径
# 如需要视觉检查，先用 Python 压缩图片：
python3 -c "
from PIL import Image
img = Image.open('slide-01.jpg')
img = img.resize((800, 450), Image.LANCZOS)
img.save('slide-01_small.jpg', 'JPEG', quality=75)
"
```

### 3. Python-pptx 卡片布局标准结构
一个经典的 PPT 页通常包含：
- 标题 + 分隔线（上方）
- 多个圆角矩形卡片（中部）
- 每个卡片内：图标 + 标题 + 描述

### 4. 生成 PPT 的推荐环境
```bash
# 检查可用环境
pip show python-pptx 2>/dev/null || python3 -m venv /tmp/ppt_venv

# 如果系统 pip 被 external-managed-environment 拦截：
python3 -m venv /tmp/ppt_venv
/tmp/ppt_venv/bin/pip install python-pptx
/tmp/ppt_venv/bin/python your_script.py
```

### 5. 6页标准学习成果PPT结构
| 页码 | 内容 | 设计 |
|:---:|------|------|
| 1 | 封面 | 渐变背景 + 大标题 + 标签 |
| 2 | 核心框架（如 CRAP） | 2×2 卡片布局 |
| 3 | 原则速览 | 两栏布局（编号列表 + 趋势） |
| 4 | 配色与字体 | 色块展示 + 字体配对 |
| 5 | 检查清单 | 三栏（设计前/每页/整体） |
| 6 | 总结 | 产出卡片 + 核心收获列表 |

## 详细参考

完整设计指南和高级技巧见：
- `references/pptx-design-handbook.md` — 完整 PPT 设计指南（配色、字体、版式、数据可视化、叙事结构）
- `references/pptx-guide.md` — 完整 API 操作指南
- `references/pptx-design-guide.md` — 设计美学指南（配色、字体、布局系统）
