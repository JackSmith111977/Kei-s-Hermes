# Detailed Reference

## 三、表格样式

### 3.1 紧凑表格模板（v2.0推荐）

```python
def T(data, cw, hc=PRI, fs=8):
    """紧凑表格：更小的 padding + 斑马纹"""
    bs = ParagraphStyle('Tb', fontName=FONT, fontSize=fs, leading=fs*1.4, textColor=DK)
    hs = ParagraphStyle('Th', fontName=FONT, fontSize=fs, leading=fs*1.4, textColor=white)
    pd = [[Paragraph(esc(c), hs) if r==0 else Paragraph(esc(c), bs) for c in row]
          for r,row in enumerate(data)]
    st = [
        ('BACKGROUND',(0,0),(-1,0),hc),
        ('TEXTCOLOR',(0,0),(-1,0),white),
        ('BOX',(0,0),(-1,-1),0.5,BDR),
        ('INNERGRID',(0,0),(-1,-1),0.3,BDR),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),2*mm),    # 紧凑 padding
        ('BOTTOMPADDING',(0,0),(-1,-1),2*mm),
        ('LEFTPADDING',(0,0),(-1,-1),2*mm),
        ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[white, BG]),
    ]
    t = Table(pd, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(st))
    return t
```

---

## 四、页眉页脚

### 4.1 紧凑版页眉页脚（v2.0推荐）

```python
def HF(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 7)
    canvas.setFillColor(GRAY)
    # 页眉
    canvas.drawString(15*mm, A4[1]-10*mm, "文档标题")
    canvas.drawRightString(A4[0]-15*mm, A4[1]-10*mm, "日期")
    canvas.setStrokeColor(BDR)
    canvas.setLineWidth(0.3)
    canvas.line(15*mm, A4[1]-12*mm, A4[0]-15*mm, A4[1]-12*mm)
    # 页脚
    canvas.line(15*mm, 12*mm, A4[0]-15*mm, 12*mm)
    pn = canvas.getPageNumber()
    canvas.drawCentredString(A4[0]/2, 7*mm, f"— {pn} —")
    canvas.restoreState()

def FP(canvas, doc):
    """首页：只有页脚"""
    canvas.saveState()
    canvas.setFont(FONT, 7)
    canvas.setFillColor(GRAY)
    canvas.line(15*mm, 12*mm, A4[0]-15*mm, 12*mm)
    pn = canvas.getPageNumber()
    canvas.drawCentredString(A4[0]/2, 7*mm, f"— {pn} —")
    canvas.restoreState()

# 使用时传入
doc.build(story, onFirstPage=FP, onLaterPages=HF)
```

### 4.2 NextPageTemplate 不兼容 SimpleDocTemplate

```python
# 错误：SimpleDocTemplate 是单模板，不支持 NextPageTemplate
story.append(NextPageTemplate('normal'))  # → ValueError!

# 正确：SimpleDocTemplate 只有一个默认模板，无需切换
# 直接用 onFirstPage / onLaterPages 区分首页和正文页即可
```

---

## 五、Mermaid 图嵌入 PDF（v2.0新增）

### 5.1 环境准备

```bash
# 安装 mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# 确保 Chrome 可用（Linux 服务器常见问题）
which google-chrome google-chrome-stable chromium
```

### 5.2 PDF 中嵌入 Mermaid 图片

```python
from reportlab.platypus import Image, Table, TableStyle
from reportlab.lib.units import mm

def add_mermaid_figure(png_path, caption, img_width=145*mm):
    """自适应缩放 + 居中 + 图注"""
    elements = []
    if not os.path.exists(png_path):
        elements.append(Paragraph(f'<i>[图片缺失: {os.path.basename(png_path)}]</i>', ...))
        return elements

    img = Image(png_path)
    aspect = img.imageWidth / img.imageHeight
    if aspect > 1:  # 横图
        img.drawWidth = img_width
        img.drawHeight = img_width / aspect
    else:           # 竖图
        img.drawHeight = img_width * 0.65
        img.drawWidth = img.drawHeight * aspect

    # 用 Table 居中
    ct = Table([[img]], colWidths=[170*mm])
    ct.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    elements += [Spacer(1,2*mm), ct]
    if caption:
        elements.append(Paragraph(
            f'图：{esc(caption)}',
            ParagraphStyle('Cap', fontSize=7.5, textColor=GRAY, alignment=TA_CENTER)))
    elements.append(Spacer(1,2*mm))
    return elements
```

---

## 六、超长脚本安全编写策略（v2.0新增）

### 6.1 问题背景
PDF 生成脚本经常超过 500 行。使用 `write_file` 一次性写入可能因上下文截断导致数据丢失。

### 6.2 推荐策略

| 策略 | 方法 | 适用场景 |
|------|------|----------|
| **分步写入法** | 先写框架 → 用 `patch` 追加章节 | 500-800行 |
| **尾部追加法** | `terminal("cat >> script.py")` 追加 | 简单追加 |
| **子代理恢复法** | 委托子 agent 通过 session_search 找回覆盖内容 | 灾难恢复 |
| **模块拆分法** | 拆为 `base.py` + `content.py` | >1000行 |

### 6.3 安全模式流程

```
1. 写框架（import + helpers + 样式 + 页眉页脚 + build_pdf入口）
2. 用 patch 逐个追加 build_chapterX() 函数（一次1-2个）
3. 验证：python3 -c "import ast; ast.parse(open('script.py').read())"
4. 执行：python3 script.py
```

---

## 关键经验：分页策略与信息密度（v2.0新增）

### 7.0 核心原则：流式排版，智能分页

PDF 排版中最常见的错误是"强制每章换页"，导致短章节只有半页内容，大量留白。
正确做法是**让内容自然流动，仅在关键节点分页**。

### 7.0.1 判断标准

设计分页策略时，boku 遵循以下判断流程：

```
开始
↓
这是封面/目录/附录？        → 是 → 单独一页（PageBreak）
↓ 否
这是正文第一部分（第1章）？   → 是 → 正文开始，新页
↓ 否
本章节内容量 > 半页？        → 否 → 接续上一章，不主动分页
↓ 是
本章与上一章是否同主题板块？  → 是 → 可以接续
↓ 否（主题切换）
新板块开始 → 分页（PageBreak）
```

### 7.0.2 实际案例：16章文档的分页决策

以下是一次真实的16章文档分页决策记录：

```
封面      → PageBreak (新文档开始)
目录      → PageBreak (正文开始)
第1章     → PageBreak (内容多：2个表格+4段正文，约一页半)
第2章     → PageBreak (含架构图，自然占满一页)
第3章     → (与第4章连续，核心循环→Provider是同一主题)
第4章     → (含fallback流程图，内容量大，自动分到下一页)
第5章     → (工具→记忆→技能，连续3章短内容，不需要分页)
第6章     → (接续第5章)
第7章     → (接续第6章，7→8之间分页：技能→网关是主题切换)
第8章     → (网关→定时→子代理→安全，连续4章短内容)
第9章     → (接续)
第10章    → (接续)
第11章    → PageBreak (安全→配置是主题板块切换)
第12章    → (配置→Aux→Token→开发→部署，连续5章)
第13章    → (接续)
第14章    → (接续)
第15章    → (接续)
第16章    → PageBreak (正文→附录)
附录      → (结束)
```

**结果**：16章 + 附录 共 **12页**(含封面目录)，章节间自然接续。
对比"每章强制分页"：约22页，效率提升45%。

### 7.1 大忌：每章强制换页

```python
# ❌ 错误——短章节（3-4行内容）独占一页，大量留白
story.extend(CH1()); story.append(PageBreak())
story.extend(CH2()); story.append(PageBreak())
```

**后果**：12章内容可能膨胀到18-22页，有效利用率仅60-70%。

### 7.2 正确策略：流式接续 + 关键位置分页

```python
def build():
    story = []
    story.extend(COVER())     # 封面 = 单独分页
    story.extend(TOC())       # 目录 = 单独分页
    # 正文：连续内容不分页，短的章节自然接续
    story.extend(CH1()); story.extend(CH2())
    story.extend(CH3()); story.extend(CH4())
    story.extend(CH5()); story.extend(CH6())
    # 仅以下位置主动分页：
    #   - 封面 → 目录
    #   - 目录 → 正文
    #   - 不同主题板块间（如安全→配置）
    #   - 正文 → 附录
    story.extend(APPENDIX())
    doc.build(story, ...)
```

### 7.3 分页决策矩阵

| 场景 | 是否 PageBreak | 理由 |
|------|:-:|------|
| 封面 → 目录 | ✅ 是 | 视觉隔离 |
| 目录 → 正文第1章 | ✅ 是 | 正文开始 |
| 第1章（内容多） | ✅ 是 | 开篇 + 2个表格，约一页半 |
| 第2章（含大图） | ✅ 是 | Mermaid 架构图自然占一页 |
| 短章节间（3-4章连续） | ❌ 否 | 核心循环 → Provider 同主题 |
| 短章节间（5-7章连续） | ❌ 否 | 工具 → 记忆 → 技能 连续接续 |
| 主题板块切换（7→8章） | ✅ 是 | 技能 → 网关，主题变换 |
| 短章节间（8-11章连续） | ❌ 否 | 网关→定时→子代理→安全 |
| 主题板块切换（11→12章） | ✅ 是 | 安全 → 配置系统，新板块 |
| 连续章节（12-16章） | ❌ 否 | 配置→Aux→Token→开发→部署 |
| 正文 → 附录 | ✅ 是 | 附录单独一页 |

### 7.4 紧凑排版检查清单

- [ ] 边距从 20mm 缩小到 15mm（信息密度+30%）
- [ ] 正文字号 8.5-9pt（不是 10-11pt）
- [ ] H1 字号 16pt（不是 20-22pt）
- [ ] 表格 cell padding 2mm（不是 3-4mm）
- [ ] 仅在封面/目录/附录/板块边界分页
- [ ] 去掉短章节末尾的 PageBreak()
- [ ] 页眉页脚线宽 0.3pt 更柔和

### 7.5 效果对比

| 版本 | 页数 | 信息密度 |
|------|:----:|:--------:|
| 每章强制分页 + 20mm边距 | 22页 | ❌ 稀疏 |
| 每章强制分页 + 15mm边距 | 19页 | ⚠️ 改善但仍分散 |
| 流式接续 + 关键分页 + 15mm边距 | **12页** | ✅ 紧凑 + 阅读舒适 |

---

## 八、完整紧凑脚本模板（v2.0推荐）

```python
#!/usr/bin/env python3
"""PDF 生成脚本 v2.0 — 紧凑版"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('WQY',
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", subfontIndex=0))
FONT = 'WQY'

PRI, HIG, BDR, GRAY, DK, BG = [
    HexColor(c) for c in ('#1a1a2e', '#e94560', '#cccccc',
                          '#666666', '#222222', '#f5f5f7')
]

def esc(t):
    return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def S(n, **kw):
    return ParagraphStyle(n, fontName=FONT, **kw)

H1 = S('H1', fontSize=16, leading=21, textColor=PRI, spaceBefore=5*mm, spaceAfter=1.5*mm)
H2 = S('H2', fontSize=12, leading=16, textColor=PRI, spaceBefore=4*mm, spaceAfter=1*mm)
B = S('Bd', fontSize=8.5, leading=13, textColor=DK, spaceAfter=1.5*mm)

def HF(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(15*mm, A4[1]-10*mm, "文档标题")
    canvas.drawRightString(A4[0]-15*mm, A4[1]-10*mm, "日期")
    canvas.setStrokeColor(BDR)
    canvas.setLineWidth(0.3)
    canvas.line(15*mm, A4[1]-12*mm, A4[0]-15*mm, A4[1]-12*mm)
    canvas.line(15*mm, 12*mm, A4[0]-15*mm, 12*mm)
    canvas.drawCentredString(A4[0]/2, 7*mm, f"— {canvas.getPageNumber()} —")
    canvas.restoreState()

def FP(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 7)
    canvas.setFillColor(GRAY)
    canvas.line(15*mm, 12*mm, A4[0]-15*mm, 12*mm)
    canvas.drawCentredString(A4[0]/2, 7*mm, f"— {canvas.getPageNumber()} —")
    canvas.restoreState()

def build():
    doc = SimpleDocTemplate("output.pdf", pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=16*mm, bottomMargin=16*mm,
        title='文档标题', author='小喵 AI')
    story = []
    story.append(Paragraph('<b>第 1 章　标题</b>', H1))
    story.append(HRFlowable(width="15%", thickness=1, color=HIG,
                             spaceBefore=1*mm, spaceAfter=2*mm))
    story.append(Paragraph('正文内容...', B))
    doc.build(story, onFirstPage=FP, onLaterPages=HF)
    print(f"✅ PDF 生成成功！({doc.page}页)")

if __name__ == "__main__":
    build()
```

---

## 八、常见错误与解决方案（v2.0扩展）

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 中文显示黑色方块 | 字体不支持 CJK | 用 `TTFont('WQY', path, subfontIndex=0)` 代替 CIDFont |
| `multiple values for fontName` | `S()` 默认有 fontName，又传了一次 | 代码块/等宽直接 `ParagraphStyle(name, fontName=...)` |
| `can't find template` | SimpleDocTemplate + NextPageTemplate | 删除 `NextPageTemplate()`，用 onFirstPage/onLaterPages |
| TTF 注册失败 | TTC 是 CFF 轮廓 | 用 `_is_cff_ttc()` 检测，换 WQY 等 TrueType |
| XML 解析错误 | `&` `<` `>` 未转义 | 使用 `esc()` 函数 |
| 标题被分页截断 | 默认允许分页 | 用 `KeepTogether` 包裹 |
| 页眉页脚被裁切 | 边距不足 | `topMargin ≥ 16mm` |
| 图片超出页面 | 太高未缩放 | 用 `add_image()` 自适应 |
| Mermaid 图空白 | 语法错误/Chrome缺失 | 先在线验证，再配 puppeteer |

---

## 九、参考资源

- ReportLab 官方文档: https://docs.reportlab.com/
- ReportLab 用户指南 PDF: https://www.reportlab.com/docs/reportlab-userguide.pdf
- Mermaid Live Editor: https://mermaid.live/
- WQY ZenHei 字体: `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`
