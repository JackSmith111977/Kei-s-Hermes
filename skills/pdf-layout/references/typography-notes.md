# PDF 排版经验总结

> 基于 Hermes Agent 架构指南 PDF 生成实践（V1→V5），总结 reportlab 中文排版的核心经验。

## 一、版本演进

| 版本 | 主要改进 | 问题 |
|------|----------|------|
| V1 | 基础排版 + Pollinations 配图 | 中文方块、排版粗糙 |
| V2 | 改进 Prompt + 7张配图 | 字体警告（CIDFont 无 bold） |
| V3 | DashScope 高清配图 | 页眉页脚缺失、无目录 |
| V4 | 彻底重构排版引擎 | 版本号未标注、元数据不完整 |
| V5 | 完善元数据 + 应用全部排版经验 | 进行中 |

## 二、核心经验

### 2.1 中文渲染
1. **必须用 `UnicodeCIDFont('STSong-Light')`**，不能用 `TTFont` 加载 `.ttc`（CFF 轮廓不支持）
2. **CIDFont 没有 bold/italic**，通过字号和颜色区分层次
3. **所有字符串必须 `esc()` 转义**，否则 `&` `<` `>` 导致 XML 解析崩溃
4. **Table 单元格必须用 Paragraph 包装**，直接传字符串使用默认字体（无中文支持）

### 2.2 排版布局
1. **紧凑排版**：现代科技文档风格，减少 spaceBefore/After，无缩进
2. **段后距 = 3mm**（正文），**段前距 = 8-12mm**（标题）
3. **行高 = 字号 × 1.6**（中文需要更大行高）
4. **KeepTogether** 包裹标题 + 首段，防止标题单独在页尾
5. **HRFlowable** 作为分隔线，比 Spacer 更有设计感

### 2.3 表格
1. **斑马纹**：使用 `ROWBACKGROUNDS` 指令，`[white, LIGHT_BG]` 交替
2. **表头底色**：`BACKGROUND (0,0) (-1,0) PRIMARY_COLOR` + 白字
3. **内边距 3-4mm**：太小拥挤，太大浪费空间
4. **FONTSIZE 8pt**：A4 页面表格内容推荐 8pt
5. **VALIGN MIDDLE**：垂直居中更美观

### 2.4 图片
1. **自适应缩放**：保持宽高比，限制最大宽度 160mm
2. **添加标题**：图片下方居中显示 caption（8pt 灰色）
3. **检查文件存在**：`os.path.exists()` 避免崩溃
4. **配图生成**：DashScope wanx2.1-t2i-turbo 效果最好

### 2.5 页眉页脚
1. **使用 onPage 回调**：`doc.build(story, onFirstPage=fn, onLaterPages=fn)`
2. **首页不同**：封面页无页眉，后续页有完整页眉
3. **canvas.saveState()/restoreState()**：必须配对使用
4. **页码居中**：`canvas.drawCentredString(A4[0]/2, 8*mm, str(page_num))`

### 2.6 元数据
1. **SimpleDocTemplate 参数**：title, author, subject, creator, producer
2. **脚本内版本管理**：`__version__` 变量，封面显示，文件名包含
3. **pypdf 后处理**：可修改已有 PDF 的元数据

## 三、踩过的坑

| 坑 | 解决方案 |
|----|----------|
| `TTFError: postscript outlines not supported` | wqy-zenhei.ttc 是 CFF 轮廓，改用 CIDFont |
| `AttributeError: 'str' has no attribute 'getKeepWithNext'` | story 中混入了字符串，应全是 Flowable 对象 |
| `IndexError: list index out of range` | Table 数据行列数与 colWidths 不匹配 |
| 图片撑破页面 | 未设置 max_width 或 max_height |
| 目录页码不准 | 静态页码需手动维护，或用 TableOfContents |
| 封面信息表边框缺失 | Table 的 BOX 指令需要正确的坐标范围 |

## 四、设计模式

### 4.1 Helper 函数模式
```python
# 封装常用元素为函数，保持 story 构建代码简洁
def h1(t): return Paragraph(esc(t), h1_style)
def h2(t): return Paragraph(esc(t), h2_style)
def body(t): return Paragraph(esc(t), body_style)
def bullet(t): return Paragraph(f'&#8222; {esc(t)}', bullet_style)
def sp(h=3*mm): return Spacer(1, h)
def hr(color=BORDER_COLOR, thickness=1): return HRFlowable(...)
```

### 4.2 样式集中管理
```python
# 在 build_pdf 开头统一定义所有样式
# 全局变量方式，helper 函数直接引用
global title_style, h1_style, h2_style, body_style, bullet_style
title_style = SB('Title', fontSize=28, ...)
h1_style = SB('H1', fontSize=20, ...)
```

### 4.3 数据驱动表格
```python
# 表格数据和样式分离
data = [
    [hp("列1", header_style), hp("列2", header_style)],
    ["数据1", "数据2"],
]
table = make_table(data, col_widths=[50*mm, 110*mm])
```
