---
name: pdf-render-comparison
description: PDF 渲染工具选型决策树。根据需求特征（中文支持、排版复杂度、安装状态）推荐最佳工具链。
  涵盖 WeasyPrint、ReportLab、fpdf2、Headless Chrome、Pandoc 五大工具的对比矩阵、安装检测脚本和选型流程图。
version: 1.0.0
triggers:
  - pdf render comparison
  - pdf 工具选型
  - pdf 渲染对比
  - pdf toolchain
  - 选择pdf工具
  - 用什么生成pdf
  - pdf renderer
  - weasyprint vs reportlab
depends_on:
  - pdf-layout
  - pdf-pro-design
design_pattern: Tool Wrapper
skill_type: generator
---

# PDF 渲染工具选型决策树 v1.0

> **目标**：当需要生成 PDF 时，快速判断用哪个工具最合适。
> 不要盲目选择——根据需求特征走决策树。

## 〇、安装状态检测（第一步！）

**每次任务开始先跑检测脚本**：

```bash
python3 -c "
import importlib
tools = {}
for pkg in ['weasyprint', 'reportlab', 'fpdf']:
    try:
        m = importlib.import_module(pkg)
        ver = getattr(m, '__version__', getattr(m, 'Version', '?'))
        tools[pkg] = ver
    except ImportError:
        tools[pkg] = None
print('已安装:', {k:v for k,v in tools.items() if v})
print('未安装:', {k:v for k,v in tools.items() if not v})
"
```

### 当前环境状态（2026-05-05）

| 工具 | 版本 | 状态 |
|------|------|------|
| ReportLab | 4.5.0 | ✅ 已安装 |
| WeasyPrint | 61.1 | ✅ 已安装（非 v62！） |
| fpdf2 | 2.8.7 | ✅ 已安装 |
| Google Chrome | 147.0 | ✅ 已安装（无 Playwright Python 包） |
| Pandoc | - | ❌ 未安装 |
| Playwright | - | ❌ Python 包未安装 |

---

## 一、工具对比矩阵

| 维度 | WeasyPrint | ReportLab | fpdf2 | Headless Chrome | Pandoc |
|------|-----------|-----------|-------|----------------|--------|
| **核心原理** | HTML+CSS→PDF | Python API 逐元素绘制 | Python API 简易绘制 | 浏览器渲染→打印PDF | Markdown→各种格式 |
| **中文支持** | ⭐⭐⭐⭐⭐ @font-face | ⭐⭐⭐⭐ TTFont/CIDFont | ⭐⭐⭐ 需 add_font | ⭐⭐⭐⭐⭐ 原生 | ⭐⭐⭐⭐ 需 xeLaTeX |
| **CSS 支持** | 完整（95%） | ❌ 无 | ❌ 无 | 完整（100%） | 有限 |
| **Flexbox/Grid** | ⚠️ 部分支持 | ❌ | ❌ | ✅ 完整 | ❌ |
| **页眉页脚** | ⭐⭐⭐⭐ @page | ⭐⭐⭐⭐⭐ template | ⭐⭐ 手动 | ⭐⭐⭐ Chrome flags | ⭐⭐⭐ 模板 |
| **智能分页** | ⭐⭐⭐⭐ page-break | ⭐⭐⭐⭐ keepWithNext | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **表格** | HTML table | Table 对象 | 手动 | HTML table | Markdown/Pipe |
| **代码块** | `<pre>` CSS | 手动绘制 | cell() | `<pre>` CSS | 代码块语法 |
| **学习曲线** | 低（会 HTML 即可） | 高（需学 API） | 中 | 低 | 中 |
| **适合场景** | 报告/文档/文章 | 证书/票据/发票 | 简单报告 | 复杂网页/PWA | 学术论文 |
| **输出质量** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 二、选型决策树

```
需要生成 PDF？
  │
  ├─ 内容是 Markdown/学术格式？
  │   └─ Pandoc 已安装 → 用 Pandoc（xeLaTeX 引擎）
  │   └─ 未安装 → 转下面
  │
  ├─ 需要像素级精确控制（证书/票据/发票）？
  │   └─ 用 ReportLab（底层 API 精确到毫米）
  │
  ├─ 内容是复杂网页（Flexbox/Grid/动画）？
  │   └─ Chrome 可用 → 用 Headless Chrome
  │   └─ 否则 → WeasyPrint（接受 Flexbox 限制）
  │
  ├─ 内容是普通文档/报告/文章？
  │   └─ WeasyPrint 已安装 → 用 WeasyPrint（HTML+CSS 最灵活）
  │   └─ 否则 → ReportLab
  │
  ├─ 只需要简单 PDF（纯文本+少量格式）？
  │   └─ fpdf2 已安装 → 用 fpdf2（最轻量）
  │   └─ 否则 → WeasyPrint
  │
  └─ 兜底推荐：WeasyPrint > ReportLab > fpdf2
```

---

## 三、各工具快速上手模板

### 3.1 WeasyPrint（推荐默认选择）

```python
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

font_config = FontConfiguration()
html = HTML(string="""
<html><head><style>
@font-face {
    font-family: 'Noto Sans CJK SC';
    src: url('file:///usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');
}
body { font-family: 'Noto Sans CJK SC', sans-serif; font-size: 10pt; }
h1 { color: #2C3E50; border-left: 4px solid #2C3E50; padding-left: 10px; }
@page { size: A4; margin: 20mm; }
</style></head><body><h1>标题</h1><p>正文内容</p></body></html>
""")
html.write_pdf("/tmp/output.pdf", font_config=font_config)
```

**注意**：WeasyPrint 当前版本 61.1（非 v62），API 稳定无 breaking changes。

### 3.2 ReportLab（精确控制）

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pdfmetrics.registerFont(TTFont('WQY', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', subfontIndex=0))
doc = SimpleDocTemplate("/tmp/output.pdf", pagesize=A4)
story = [Paragraph("正文内容", styleN)]
doc.build(story)
```

### 3.3 fpdf2（轻量快速）

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.add_font('Noto', fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
pdf.set_font('Noto', size=12)
pdf.cell(0, 10, '正文内容', new_x="LMARGIN", new_y="NEXT")
pdf.output("/tmp/output.pdf")
```

### 3.4 Headless Chrome（复杂网页）

```bash
google-chrome --headless --disable-gpu --no-sandbox   --print-to-pdf=/tmp/output.pdf   --paper-type=A4   file:///tmp/input.html
```

或用 Python 的 selenium/subprocess 控制。

---

## 四、Red Flags（避坑指南）

1. **WeasyPrint Flexbox 陷阱**：不要依赖 `display: flex` 居中封面！用 `padding-top` 代替。
2. **ReportLab 中文陷阱**：直接传字符串给 Table 单元格会显示方块！必须用 `Paragraph` 包装。
3. **fpdf2 分页陷阱**：没有自动分页控制，长表格/代码块会被腰斩。
4. **Chrome 无 Playwright**：当前环境没有安装 playwright Python 包，只能用 subprocess 调用 chrome 命令。
5. **Pandoc 未安装**：当前环境没有 pandoc，需要 `sudo apt install pandoc` 才能用。
6. **WeasyPrint v61 vs v62**：当前是 v61.1，升级到 v62 前需验证 API 兼容性（见 P1-2 任务）。
7. **字体路径必须绝对**：WeasyPrint 的 `@font-face` 必须用 `file:///` 绝对路径，相对路径无效。

## 五、视觉质检通用流程

无论用哪个工具，生成后必须：
1. `pdftoppm -f 1 -l 1 -r 150 output.pdf /tmp/preview` → 生成第一页 PNG
2. 用 vision 工具检查排版
3. PASS → 交付；FAIL → 调整并重试
