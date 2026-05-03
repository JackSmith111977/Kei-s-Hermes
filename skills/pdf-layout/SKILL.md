---
name: pdf-layout
description: 专业 PDF 排版设计与生成技能。涵盖 reportlab 高级排版技巧、中文 PDF 生成、 WQY ZenHei 字体方案、Mermaid 图嵌入...
version: 2.0.0
triggers:
- pdf layout
- pdf-layout
author: 小喵
license: MIT
allowed-tools:
- write_file
- patch
- read_file
- terminal
metadata:
  hermes:
    tags:
    - pdf
    - reportlab
    - layout
    - typography
    - chinese
    - toc
    - header-footer
    - table-style
    related_skills:
    - doc-design
    - mermaid-guide
    category: productivity
    skill_type: doc-generation
    design_pattern: generator
---
# 专业 PDF 排版设计技能（reportlab 高级）v2.0

> **版本历史**：v2.0 全面更新——字体方案反转（WQY > CIDFONT）、新增 Mermaid 嵌入、
> 紧凑排版策略、长脚本安全编写、常见错误扩展。

## 触发条件（When to Use）

**使用此 skill 当：**
- 用户需要生成高质量 PDF 文档（技术文档、报告、指南）
- 用户需要中文 PDF（含 CJK 字符）
- 涉及页眉页脚、目录、书签、多栏布局、水印等高级排版
- 需要表格样式优化（斑马纹、表头底色、单元格内边距）
- 需要代码块样式（等宽字体、背景色）
- 需要在 PDF 中嵌入 Mermaid 架构图

**不使用此 skill 当：**
- 简单文本 PDF（直接用 fpdf2）
- 非 PDF 格式文档（用 doc-design skill）

---

## 一、核心排版原则（v2.0 紧凑版）

### 1.1 字体规则（经验更新）

```python
# 最佳选择（v2.0推荐）：WQY ZenHei TTF —— 无黑块，中英文混排完美
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('WQY', "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", subfontIndex=0))
FONT = 'WQY'

# 备选：STSong-Light CIDFont（也能用，但部分PDF阅读器可能显示黑块）
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# 注意：Noto CJK TTC 是 CFF 轮廓，reportlab 不支持！
# wqy-zenhei.ttc 有3个字体索引：0=中日韩, 1=韩, 2=繁中
```

### 1.2 字号层级（紧凑版）

| 层级 | 字号 | 行高 | 用途 |
|------|------|------|------|
| 封面标题 | 28pt | 34pt | 文档名称 |
| H1 章节 | **16pt** | **21pt** | 一级标题（旧版20pt → 16pt 更紧凑） |
| H2 小节 | **12pt** | **16pt** | 二级标题 |
| H3 细分 | **10pt** | **14pt** | 三级标题 |
| 正文 | **8.5pt** | **13pt** | 正文内容（旧版10pt → 8.5pt 密度更高） |
| 表格 | **7-8pt** | **10-12pt** | 表格/代码（旧版8-9pt） |
| 注释 | 7-7.5pt | 10-11pt | 图注/页眉页脚 |

### 1.3 间距规则（紧凑版）

- **段前距**：H1=5mm, H2=4mm, H3=3mm, 正文=0mm
- **段后距**：H1=1.5mm, H2=1mm, H3=0.5mm, 正文=1.5mm
- **行高**：字号 × 1.5-1.6（中文需要更大行高）
- **页边距**：**15mm**（旧版20mm → 15mm 信息密度提升30%）
- **单元格内边距**：2mm（旧版3mm → 2mm）

### 1.4 配色方案（不变）

```python
# 深色科技风（推荐）
PRI = HexColor('#1a1a2e')          # 标题/表头
ACC = HexColor('#0f3460')          # 子标题/强调
HIG = HexColor('#e94560')          # 装饰线/链接
BG = HexColor('#f5f5f7')           # 表格交替行
BGC = HexColor('#eeeeee')          # 代码块背景
BDR = HexColor('#cccccc')          # 边框线
GRAY = HexColor('#666666')         # 辅助文字
DK = HexColor('#222222')           # 正文
```

---

## 二、中文 PDF 渲染

### 2.1 字体选择优先级（v2.0更新）

```python
# 方案1（最佳，v2.0推荐）：WQY ZenHei TTF — 无黑块，中英文混合良好
pdfmetrics.registerFont(TTFont('WQY',
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", subfontIndex=0))

# 方案2（备选）：UnicodeCIDFont — 内置CJK支持，轻量但部分阅读器有兼容问题
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# 方案3（兜底）：Helvetica（不支持中文，仅用于纯英文）
```

### 2.2 TTC 文件 CFF 检测（防止注册失败）

```python
import struct
def _is_cff_ttc(filepath):
    """检测 TTC 文件是否包含 CFF 轮廓（reportlab 不支持 CFF）"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(4)
            if header != b'ttcf':
                return False
            num_fonts = struct.unpack('>I', f.read(4))[0]
            first_offset = struct.unpack('>I', f.read(4))[0]
            f.seek(first_offset)
            sf_version = f.read(4)
            return sf_version == b'OTTO'  # CFF 轮廓
    except:
        return False
```

**已知问题**：`NotoSansCJK-*.ttc` 虽然文件头是 `ttcf`，但内部是 CFF 轮廓，reportlab 不支持。WQY ZenHei 是 TrueType 轮廓，支持良好。

### 2.3 字符串转义（必须！）

```python
def esc(text):
    if not text: return ""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
```

### 2.4 Table 单元格必须用 Paragraph 包装

```python
# 正确：所有单元格转为 Paragraph
processed_row = [Paragraph(esc(cell), cell_style) for cell in row]

# 错误：直接传字符串，中文显示方块
```

### 2.5 常见陷阱：`S()` 函数与 `fontName` 冲突

```python
# 错误——S() 默认设置了 fontName，再次传 fontName 会冲突
def S(name, **kw):
    return ParagraphStyle(name, fontName=FONT, **kw)

code_style = S('Code', fontName='Courier', ...)  # TypeError!

# 正确——代码块或等宽样式应直接用 ParagraphStyle
code_style = ParagraphStyle('Code', fontName='Courier', ...)
```

---


> 🔍 **## 三、表格样式** moved to [references/detailed.md](references/detailed.md)
