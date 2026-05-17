---
name: pdf-layout
description: 专业 PDF 排版与生成 — 双引擎（ReportLab + WeasyPrint）覆盖所有 PDF 场景。合并自 pdf-layout-weasyprint(v2.0) + pdf-layout-reportlab(v1.0) + pdf-layout(v2.0)
version: 3.0.0
triggers:
- pdf
- 生成 pdf
- pdf layout
- pdf 排版
- weasyprint
- reportlab
- 中文 PDF
- 生成 PDF
- PDF 生成
- PDF 排版
author: 小喵
license: MIT
allowed-tools:
- write_file
- patch
- read_file
- terminal
- execute_code
metadata:
  hermes:
    tags:
    - pdf
    - reportlab
    - weasyprint
    - layout
    - typography
    - chinese
    - pdf-generation
    - html-to-pdf
    - css-print
    related_skills:
    - doc-design
    - mermaid-guide
    - pdf-pro-design
    - pdf-render-comparison
    category: productivity
    skill_type: doc-generation
    design_pattern: generator
    merged_from: [pdf-layout-weasyprint, pdf-layout-reportlab]
depends_on: []

---

# PDF 排版与生成（合并版 v3.0）

> 🚨 **本 skill v3.0 合并了 `pdf-layout-weasyprint`、`pdf-layout-reportlab` 和原 `pdf-layout` 三个技能。**
> 统一入口，双引擎覆盖。旧技能已标记弃用，请勿再使用。

## 🚨 语言检查（绝对优先！）

**在开始任何 PDF 生成任务前，必须先检查语言偏好！**

1. **默认中文**：除非主人明确指定使用其他语言（如"用英文"），否则**所有文本必须使用中文**。
2. **禁止私自切换**：绝对禁止在没有指令的情况下生成英文内容。
3. **自我检查**：生成前自检，如果内容是英文，立即重写为中文。

---

## 🔀 引擎选择决策

```text
需要生成 PDF？
    │
    ├─ 文字为主、格式简单 → WeasyPrint（HTML+CSS → PDF）
    │   └─ 优点：CSS 熟悉、模板友好
    │
    ├─ 复杂排版、精确控制 → ReportLab
    │   └─ 优点：像素级控制、图表嵌入
    │
    ├─ 已有 HTML 页面 → WeasyPrint（直接转换）
    │
    └─ 数据可视化报告 → ReportLab（内置图表）
```

### 引擎对比

| 特性 | WeasyPrint | ReportLab |
|:-----|:----------:|:---------:|
| 学习曲线 | 🟢 低 (CSS) | 🔴 高 (Flowables) |
| 中文支持 | ✅ 系统字体 | ✅ TTFont 注册 |
| 表格 | 🟡 中等 | ✅ 强大 |
| 图表 | ❌ 无 | ✅ 内置 LinePlot/PiePlot |
| 分页控制 | 🟡 @page | ✅ 精确 |
| 大文件 | 🟡 内存高 | ✅ 稳定 |
| 印刷级 CMYK | ❌ | ✅ |

---

## 方案 A：WeasyPrint（推荐给 Web 开发者）

### 安装

```bash
pip install weasyprint
# 中文支持
sudo apt install fonts-wqy-zenhei fonts-wqy-microhei
```

### 基本用法

```python
from weasyprint import HTML

# 从 HTML 字符串生成
HTML(string='<h1 style="color:red">Hello</h1><p>中文内容</p>') \
    .write_pdf('output.pdf')

# 从文件生成
HTML(filename='report.html').write_pdf('report.pdf')

# 带 CSS 样式表
HTML(string='<h1>标题</h1>').write_pdf('styled.pdf', stylesheets=['style.css'])
```

### CSS 打印样式关键点

```css
@page {
  size: A4;
  margin: 2.5cm 2cm;
  @top-center { content: element(pageHeader); }
}

body {
  font-family: 'WenQuanYi Zen Hei', 'Noto Sans CJK SC', serif;
  font-size: 11pt;
  line-height: 1.8;
  color: #333;
}

/* 避免分页断裂 */
h1, h2, h3, h4 { page-break-after: avoid; }
table { page-break-inside: avoid; }
img { page-break-inside: avoid; }

/* 代码块换行 */
pre {
  white-space: pre-wrap;
  word-break: break-all;
  background: #f5f5f5;
  padding: 12px;
  font-size: 9pt;
}
```

### WeasyPrint 局限与绕过

| 问题 | 绕过方案 |
|:-----|:---------|
| 复杂表格渲染不稳定 | 改用 ReportLab |
| 不支持 CMYK | 改用 ReportLab |
| 大文件 OOM | 分块生成后合并 |
| 自定义字体不生效 | 检查 fc-list + 指定绝对路径 |

---

## 方案 B：ReportLab（推荐给精确控制需求）

### 字体配置

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 方案1（最佳）：WQY ZenHei TTF — 无黑块，中英文混排完美
pdfmetrics.registerFont(TTFont(
    'WQY', "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", subfontIndex=0))

# 方案2（备选）：UnicodeCIDFont — 内置CJK支持
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

FONT = 'WQY'  # 全局字体变量
```

### 紧凑排版原则

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether)

doc = SimpleDocTemplate(
    'output.pdf', pagesize=A4,
    topMargin=15*mm, bottomMargin=15*mm,
    leftMargin=15*mm, rightMargin=15*mm)

# 字号层级（紧凑版）
# 封面标题: 28pt | H1: 16pt | H2: 12pt | H3: 10pt
# 正文: 8.5pt | 表格/代码: 7-8pt | 注释: 7-7.5pt

# 配色方案（深色科技风）
PRI = colors.HexColor('#1a1a2e')   # 标题/表头
ACC = colors.HexColor('#0f3460')   # 子标题
HIG = colors.HexColor('#e94560')   # 强调色
BG  = colors.HexColor('#f5f5f7')   # 表格交替行
DK  = colors.HexColor('#222222')   # 正文
```

### 表格最佳实践

```python
# 所有单元格必须用 Paragraph 包装（否则中文显示方块）
from reportlab.lib.styles import getSampleStyleSheet
styles = getSampleStyleSheet()
cell_style = ParagraphStyle('CellBody', parent=styles['Normal'],
    fontName=FONT, fontSize=8, leading=12, spaceAfter=0)

def esc(text):
    """XML 转义（表格单元格必须）"""
    if not text: return ""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# 组装表格
headers = [Paragraph(esc(h), header_style) for h in ['列1', '列2', '列3']]
rows = [[Paragraph(esc(c), cell_style) for c in row] for row in data]
table = Table([headers] + rows, colWidths=[4*cm, 4*cm, 4*cm])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), PRI),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), FONT),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG]),
]))
```

### TTC 文件 CFF 检测

```python
import struct
def is_cff_ttc(filepath):
    """检测 TTC 是否包含 CFF 轮廓（reportlab 不支持 CFF）"""
    try:
        with open(filepath, 'rb') as f:
            if f.read(4) != b'ttcf':
                return False
            num_fonts = struct.unpack('>I', f.read(4))[0]
            f.seek(struct.unpack('>I', f.read(4))[0])
            return f.read(4) == b'OTTO'
    except:
        return False
```

> ⚠️ **已知问题**：NotoSansCJK-*.ttc 虽然是 ttcf 格式，但内部是 CFF 轮廓，reportlab 不支持。WQY ZenHei 是 TrueType 轮廓，支持良好。

### 字符串转义（必须！）

```python
def esc(text):
    if not text: return ""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
```

---

## 常见陷阱速查

| 陷阱 | 症状 | 解决方案 |
|:-----|:-----|:---------|
| WeasyPrint 中文白页 | 输出空白 PDF | 检查 font_config，安装中文字体 |
| ReportLab 中文方块 | □□□ | 注册 TTFont，确认字体路径 |
| 表格内容溢出 | 文字超出单元格 | Paragraph 包装 + fontSize 缩小 |
| TTC CFF 错误 | 字体注册失败 | 检测 CFF 轮廓，改用 WQY |
| `S()` 函数冲突 | TypeError | 等宽样式直接用 ParagraphStyle |
| WeasyPrint OOM | 内存不足 | 分块生成 + pdfunite 合并 |
| 图片模糊 | 像素化 | 使用 SVG 矢量图 |

---

## 参考资源

- [references/detailed.md](references/detailed.md) — 完整排版模板、Mermaid 嵌入、页眉页脚、水印
- [references/code-examples.md](references/code-examples.md) — 高级代码示例
- [references/typography-notes.md](references/typography-notes.md) — 排版理论
- [checklists/pdf-checklist.md](checklists/pdf-checklist.md) — PDF 质量检查清单
