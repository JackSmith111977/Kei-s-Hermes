---
name: vision-qc-patterns
description: PDF 排版错误模式库。涵盖粘连、错位、溢出、截断、字体回退失败等常见排版问题的视觉特征、根因分析和修复方案。
  配合 vision_analyze 工具自动识别 PDF 渲染质量问题。
version: 1.0.0
triggers:
  - 排版错误
  - 排版问题
  - 视觉质检
  - vision qc
  - pdf 错误模式
  - 文字粘连
  - 文字溢出
  - 文字错位
  - 排版检查
  - layout error
depends_on:
  - pdf-layout
  - pdf-pro-design
design_pattern: Reviewer
skill_type: pipeline
---

# 排版错误模式库 v1.0

> 当使用 vision_analyze 检查 PDF 渲染质量时，参照此模式库识别问题。

## 一、错误模式分类

### 1.1 文字粘连 (Text Overlap /粘连)

**视觉特征**：
- 两行或多行文字互相重叠、覆盖
- 字符之间没有正常间距，挤在一起
- 行间距过小或为零

**根因**：
- `line-height` 设置过小
- WeasyPrint 中 `@page` margin 不足导致内容挤压
- ReportLab 的 leading（行间距）参数设置错误
- 字体 TTC 的 subfontIndex 错误导致行距计算异常

**修复**：
```css
/* WeasyPrint */
body { line-height: 1.6; }  /* 中文至少 1.5 */
```
```python
# ReportLab
style = ParagraphStyle('Body', leading=13)  # 字号8.5pt × 1.5 ≈ 13
```

### 1.2 文字错位 (Misalignment)

**视觉特征**：
- 标题与正文不对齐
- 表格单元格内容偏移
- 左侧装饰线（border-left）与文字位置不匹配
- 列表缩进不一致

**根因**：
- `padding` / `margin` 计算错误
- CSS `box-sizing` 未考虑
- WeasyPrint 对某些 CSS 属性解析差异
- 表格列宽自动计算导致偏移

**修复**：
```css
/* 统一盒模型 */
* { box-sizing: border-box; }
/* 固定列宽表格 */
table { table-layout: fixed; }
```

### 1.3 内容溢出 / 截断 (Overflow / Truncation)

**视觉特征**：
- 文字超出容器边界被截断
- 表格行被分页切断
- 代码块最后一行看不见
- 图片只显示一半

**根因**：
- 容器 `height` 固定但内容过长
- 缺少 `page-break-inside: avoid`
- WeasyPrint 分页算法切断了不可分割的元素

**修复**：
```css
table, pre, img, .callout { page-break-inside: avoid; }
p { widows: 2; orphans: 2; }
h1, h2, h3 { page-break-after: avoid; }
```

### 1.4 字体回退失败 / 方块字 (Font Fallback Failure)

**视觉特征**：
- 中文显示为 □□□（豆腐块）
- 英文正常但中文方块
- 部分字符正常部分方块

**根因**：
- 未注册中文字体
- `@font-face` src 路径错误（相对路径 vs 绝对路径）
- ReportLab 直接传字符串给 Table 而非 Paragraph
- TTC 文件的 subfontIndex 错误
- CFF 轮廓字体不被 reportlab 支持

**修复**：
```css
/* WeasyPrint - 必须用 file:/// 绝对路径 */
@font-face {
    font-family: "Noto Sans CJK SC";
    src: url("file:///usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc");
}
```
```python
# ReportLab - 表格单元格必须用 Paragraph
from reportlab.platypus import Paragraph
cell = Paragraph(esc(text), cell_style)
```

### 1.5 表格渲染异常 (Table Rendering Issues)

**视觉特征**：
- 表格边框缺失或双线
- 表头背景色丢失
- 单元格内边距不一致
- 斑马纹交替错误

**根因**：
- WeasyPrint 对 `border-collapse` 的支持差异
- CSS `:nth-child()` 选择器在分页后失效
- ReportLab Table 样式定义不完整

**修复**：
```css
table { border-collapse: collapse; }
th { background-color: #2C3E50 !important; }  /* 用 !important 确保覆盖 */
tr:nth-child(even) { background-color: #f8f9fa; }
```

### 1.6 页眉页脚异常 (Header/Footer Issues)

**视觉特征**：
- 页眉覆盖正文
- 页码缺失或错误
- 章节名没有动态更新
- 首页有不该有的页眉

**根因**：
- `@page` margin-top 太小
- `string-set` 未正确设置
- 缺少 `@page :first` 规则

**修复**：
```css
@page {
    margin-top: 25mm;  /* 留出页眉空间 */
    @top-center { content: string(chapter-title); font-size: 9pt; color: #999; }
    @bottom-center { content: counter(page); }
}
@page :first {
    @top-center { content: none; }  /* 首页无页眉 */
}
h1 { string-set: chapter-title content(); }
```

## 二、Vision QC 检查清单

使用 `vision_analyze` 时，按以下顺序检查：

1. **封面**：标题居中、副标题、作者信息完整
2. **目录**：页码对齐、层级缩进正确
3. **正文页**：
   - [ ] 文字无粘连（行距正常）
   - [ ] 无方块字（中文正常显示）
   - [ ] 表格无错位
   - [ ] 代码块无截断
   - [ ] 图片完整显示
4. **页眉页脚**：页码连续、章节名正确
5. **分页处**：无表格/代码块被腰斩

## 三、自动化检查 Prompt 模板

```
请检查这份 PDF 预览图，按照以下错误模式逐一排查：

1. 文字粘连：是否有行间距过小、文字重叠？
2. 方块字：是否有中文显示为 □□□？
3. 内容截断：是否有文字/表格/代码块被页面边界切断？
4. 表格异常：边框、背景色、内边距是否正常？
5. 对齐问题：标题、正文、列表缩进是否一致？

对每个问题，给出：是否存在、严重程度（高/中/低）、具体位置。
```

## 四、自动化脚本

使用 `scripts/vision_qc.py` 自动提取页面进行检查：

```bash
# 检查关键页（首页+中间+最后）
python3 scripts/vision_qc.py --pdf output.pdf --sample key

# 检查所有页
python3 scripts/vision_qc.py --pdf output.pdf --sample all

# 检查指定页
python3 scripts/vision_qc.py --pdf output.pdf --pages 1,3,5

# 高分辨率
python3 scripts/vision_qc.py --pdf output.pdf --sample key --dpi 200
```
