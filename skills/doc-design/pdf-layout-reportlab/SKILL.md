---
name: pdf-layout-reportlab
description: 使用 ReportLab 生成中文 PDF 的完整无痛指南。涵盖字体注册（WQY ZenHei/STSong-Light）、智能分页策略、表格最佳实践...
version: 1.0.0
triggers:
- 生成中文 PDF
- PDF 黑块
- PDF 排版问题
- ReportLab PDF
- 中文 PDF 字体
- 分页策略
- PDF 表格
allowed-tools:
- terminal
- read_file
- write_file
- patch
- execute_code
metadata:
  hermes:
    tags:
    - pdf
    - reportlab
    - chinese
    - typography
    - layout
    category: doc-design
    skill_type: library-reference
    design_pattern: tool-wrapper
    related_skills:
    - pdf-layout-weasyprint
    - doc-design
---
# PDF 排版无痛指南：ReportLab 篇 🐾

## 🚨 语言检查（绝对优先！）

**在开始任何 PDF 生成任务前，必须先检查语言偏好！**

1. **默认中文**：除非主人明确指定使用其他语言（如"用英文"），否则**所有文本必须使用中文**。
2. **禁止私自切换**：绝对禁止在没有指令的情况下生成英文内容（包括标题、正文、图表文字）。
3. **自我检查**：生成前自检，如果内容是英文，立即重写为中文。

---

## 一、字体选择（最关键的一步）

### Ubuntu 可用中文字体

| 字体 | 路径 | ReportLab 支持 | 中文渲染 | 推荐 |
|:---|:---|:---:|:---:|:---:|
| **WQY ZenHei TTC** | `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` | ✅ TTFont | ✅ 完美 | ⭐ **首推** |
| **STSong-Light** | reportlab 内置 CID 字体 | ✅ CIDFont | ✅ 宋体 | ⭐ 次选 |
| Helvetica | reportlab 内置 | ✅ | ❌ **黑块** | ❌❌ |

### 注册方式

```python
# 方式 A：TTFont（推荐 WQY ZenHei）
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("WQY", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"))

# 方式 B：UnicodeCIDFont（STSong-Light）
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
```

### ⚠️ 关键踩坑
- **永远不要用 Helvetica 渲染中文** → 会产生黑块
- **不要用 getSampleStyleSheet()** → 它内置 Helvetica，手动创建所有 ParagraphStyle
- NotoSansCJK 是 OTTO CFF 格式 → **TTFont 不支持**，无法使用

## 二、三套布局模板

| 参数 | 紧凑版 | 正常版 | 宽松版 |
|:---|:---:|:---:|:---:|
| 边距 | 15mm | 20mm | 25mm |
| 正文字号 | 8.5pt | 9.5pt | 10.5pt |
| 标题字号 | 16/12/10pt | 20/14/11pt | 22/16/12pt |
| 行距 | 13pt | 14pt | 16pt |
| 表格字号 | 7.5pt | 9pt | 10pt |
| 适用场景 | 资料手册 | 标准文档 | 阅读文档 |

## 三、智能分页（核心技能 💎）

### 分页决策矩阵

```
内容量              行为                           场景
─────────────────────────────────────────────────────────
0-15 行             自然接续（不插任何分页）         短章节、小说明
15-30 行            CondPageBreak(100)              普通章节
30+ 行              PageBreak()                     长章节、大块内容
新板块/附录         PageBreak()                     独立板块
封面/目录           PageBreak()                     必须独占
```

### 代码实现

```python
from reportlab.platypus import PageBreak, CondPageBreak, KeepTogether

def smart_section(story, heading, body_elements, estimated_lines=0, is_new_part=False):
    """智能添加章节"""
    if is_new_part or estimated_lines >= 30:
        story.append(PageBreak())
    elif estimated_lines >= 15:
        story.append(CondPageBreak(100))
    # 不足 15 行：自然接续
    story.append(heading)
    story.extend(body_elements)
```

### KeepTogether 用法

```python
# 确保表头+表格不在页面末尾被拆分
story.append(KeepTogether([
    heading,
    table,
    footnote,
]))
```

## 四、表格最佳实践

```python
from reportlab.platypus import Table, TableStyle, Paragraph

def make_table(data, col_widths=None, font_size=9):
    """创建美观表格"""
    wrapped = []
    for row in data:
        wrapped.append([
            Paragraph(str(cell), ParagraphStyle(..., fontName="WQY", fontSize=font_size))
            for cell in row
        ])
    
    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'WQY'),
        ('FONTSIZE', (0,0), (-1,-1), font_size),
        ('BACKGROUND', (0,0), (-1,0), '#2C3E50'),       # 表头深色
        ('TEXTCOLOR', (0,0), (-1,0), '#FFFFFF'),         # 表头白色
        ('GRID', (0,0), (-1,-1), 0.5, '#CCCCCC'),        # 网格线
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), ['#F8F9FA', '#FFFFFF']),  # 斑马纹
    ]))
    return t
```

**表格注意事项：**
- ❌ 不要手动指定 rowHeights → 让 reportlab 自动计算
- ✅ repeatRows=1 让表头跨页重复
- ✅ 表格内文字用 Paragraph 包裹（自动换行）
- ✅ 斑马纹用 ROWBACKGROUNDS 实现

## 五、封面设计

```python
def add_cover(story, pdf_h, title, subtitle, author=""):
    story.append(Spacer(1, pdf_h * 0.28))
    story.append(Paragraph(title, ParagraphStyle("ct", fontName="WQY", fontSize=28,
                  alignment=1, spaceAfter=10*mm)))
    if subtitle:
        story.append(Paragraph(subtitle, ParagraphStyle("cs", fontName="WQY", fontSize=16,
                  alignment=1, textColor=HexColor('#888888'))))
    story.append(Spacer(1, pdf_h * 0.25))
    if author:
        story.append(Paragraph(author, ParagraphStyle("ca", fontName="WQY", fontSize=11,
                  alignment=1, textColor=HexColor('#666666'))))
    story.append(PageBreak())
```


> 🔍 **## 六、Mermaid 图片嵌入** moved to [references/detailed.md](references/detailed.md)
