# 文档排版设计学习笔记

> 整理时间：2026-05-02
> 来源：多平台设计理论 + 实际案例研究

---

## 一、核心设计原则（CRAP）

### 1. Contrast（对比）
- **目的**：突出重点，创造视觉层次，引导读者视线
- **字体对比**：大小、粗细、颜色、字重
  - 标题用 Bold/Heavy，正文用 Regular/Light
  - 字号差异至少 4pt 才能形成有效对比
- **颜色对比**：深色文字 + 浅色背景（投影场景最安全）
- **避免**：灰色文字在灰色背景上（对比度不足）

### 2. Repetition（重复）
- **目的**：创造一致性、品牌识别、统一感
- **可重复元素**：字体、字号、颜色、装饰元素、页码位置、导航栏位置
- **实践**：建立设计系统，所有页面共用同一套样式

### 3. Alignment（对齐）
- **目的**：创造秩序、组织元素、建立视觉连接
- **规则**：每个元素必须与另一个元素对齐，不可随意放置
- **推荐**：使用网格系统（Grid System）
  - 4pt 网格（Material Design）或 8pt 网格
- **对齐方式**：左对齐（正文）、居中（标题）、右对齐（少量场景）

### 4. Proximity（亲密性）
- **目的**：组织相关信息，区分不同组
- **规则**：相关元素靠近，不相关元素远离
- **段落间距 > 行间距**（让读者知道这是新段落）

---

## 二、排版基础理论

### 字体搭配原则
- **不超过 3 种字体**（推荐 2 种）
- **正文字体**：
  - 中文：宋体、思源黑体、苹方（PingFang SC）
  - 英文：Arial、Calibri、Georgia、Times New Roman
- **标题字体**：可用装饰性更强的字体
- **中英文混排**：中文字体 + 英文字体搭配，英文前后加半角空格
- **字号层级**（以 4 为基数）：
  - 大标题：24-32pt（Ultra Light/Thin）
  - 标题：18-24pt（Light）
  - 副标题：14-18pt（Regular）
  - 正文：10-14pt（Regular）
  - 注释：8-10pt（Light）

### 行距与间距
- **行距**：
  - 单倍行距（1.0）：紧凑
  - 1.5 倍：学位论文标准
  - 1.15-1.5 倍：商业文档推荐
- **段落间距**：通常是行距的 1.5-2 倍
- **字距**：正文保持 normal，标题可适当加大（字号的 20-25%）
- **页边距**：0.5-1 英寸（2.54-2.54cm），简历建议 0.5-1 英寸

### 配色方案
- **主色 + 辅助色 + 强调色**（不超过 5 种颜色）
- **60-30-10 法则**：
  - 60% 主色（背景/大面积）
  - 30% 辅助色（次要元素）
  - 10% 强调色（CTA/重点）
- **配色工具**：Adobe Color、Coolors
- **对比度**：确保文字与背景对比度 ≥ 4.5:1（WCAG AA 标准）
- **商业文档**：蓝、灰、白为主，少量橙色/绿色点缀
- **创意文档**：可大胆使用渐变色、对比色

### 网格系统
- **基础单位**：4pt 或 8pt
- **列数**：12 列网格最灵活
- **栏间距**：20-40px
- **作用**：统一布局、减少决策、团队协作

---

## 三、中文排版规范（GB/T 15834）

### 字体选择
- **正文**：宋体（衬线体，印刷可读性好）
- **标题**：黑体（无衬线体，醒目）
- **屏幕阅读**：思源黑体、苹方

### 标点符号
- 中文标点占全角宽度
- 行首禁排：句号、逗号、顿号等不能出现在行首
- 行尾禁排：前括号、前引号不能出现在行尾

### 段落格式
- **首行缩进**：2 个字符（约 0.74 英寸 / 1.88cm，12pt 字体）
- **行距**：1.5 倍或 2 倍（学位论文）
- **段前段后**：可适当增加段后间距

### 数字与英文
- 阿拉伯数字和英文前后加半角空格
- 完整的英文句子用半角标点
- 数字可用全角（对齐场景）或半角（正文场景）

### 中英文混排
- 中文字体：宋体/黑体/思源黑体
- 英文字体：Arial/Times New Roman
- 英文前后加半角空格
- 字号保持一致

---

## 四、各场景排版规范

### 📊 商业报告
**结构**：
1. 封面（标题、日期、作者）
2. 目录
3. 执行摘要（1 页以内）
4. 正文（引言、方法、结果、讨论）
5. 结论与建议
6. 附录

**排版要点**：
- 字体：Arial/Calibri/Georgia，正文 11-12pt
- 行距：1.15-1.5 倍
- 颜色：蓝灰白为主 + 数据高亮色
- 数据可视化：
  - 趋势 → 折线图
  - 占比 → 饼图/环形图
  - 对比 → 柱状图
  - 分布 → 散点图
  - 流程 → 桑基图/流程图
- 每页一个核心观点
- 大量使用图表而非纯文字
- 页码、页眉（公司 logo）

**优秀案例参考**：
- Visme 44 个商业报告模板
- Venngage 50+ 报告模板
- Canva 年度报告模板

---

### 📄 简历（CV/Resume）
**ATS 友好要求**：
- 格式：.docx 或 .pdf（.docx 兼容性最好）
- 布局：单列布局（多列会导致 ATS 解析失败 70%+）
- 避免：表格、文本框、图片、图形、多栏
- 字体：Arial/Calibri/Georgia/Times New Roman，10-12pt
- 标题：14-16pt
- 页边距：0.5-1 英寸
- 保存来源：Word 或 Google Docs（不要用 Canva/InDesign）

**结构**：
1. 姓名 + 联系方式（顶部居中或左对齐）
2. 个人简介（2-3 句话）
3. 工作经历（倒序，动词开头）
4. 教育背景
5. 技能（关键词匹配 JD）
6. 项目经验（可选）
7. 证书/奖项（可选）

**排版要点**：
- 黑白配色（最安全）
- 清晰的 section 标题
- 使用标准标题名（"Work Experience" 而非 "My Journey"）
- 关键词匹配职位描述
- 一页为佳（10 年以内经验）

---

### 📚 技术文档
**结构**：
1. 概述（What & Why）
2. 快速开始（Getting Started）
3. 安装指南
4. API 参考
5. 教程/示例
6. FAQ / 故障排除
7. Changelog

**排版要点**：
- 字体：代码用等宽字体（Monaco/Consolas）
- 代码块：语法高亮 + 可复制
- 标题层级清晰（H1-H4）
- 侧边栏导航
- 面包屑导航
- 版本标注
- 实时示例/沙盒
- 搜索功能

**优秀案例**：
- Stripe API 文档
- Twilio 文档
- GitHub README
- MDN Web Docs

**API 文档最佳实践**：
1. 了解受众（开发者水平）
2. 清晰的结构（Overview → Authentication → Endpoints → Examples）
3. 每个端点包含：描述、请求方法、参数、响应示例、错误码
4. 可运行的代码示例
5. 保持更新（版本控制）
6. Swagger/OpenAPI 自动生成

---

### 🎯 PPT/演示文稿
**设计原则**：
- **每页一个核心观点**
- **6×6 规则**：每行不超过 6 个词，每页不超过 6 个要点
- **少即是多**：文字越少越好，用图说话

**排版要点**：
- 字体：
  - 标题：24-36pt，无衬线体（Arial/Calibri/思源黑体）
  - 正文：18-24pt
  - 最小字号：18pt（投影可读性）
- 颜色：
  - 深色文字 + 浅色背景（投影最安全）
  - 整个演示不超过 3 种颜色
  - 主色 + 辅助色 + 强调色
- 对齐：使用 Slide Master 统一对齐
- 留白：内容不超过页面 60%
- 图片：高清大图 > 小图标拼贴
- 动画：简洁（淡入/擦除），避免花哨

**优秀案例参考**：
- McKinsey 咨询报告风格
- Apple Keynote 风格（极简）
- Pitch Deck 模板

---

## 五、Python 文档操作库速查

### python-docx（Word .docx）
```python
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 设置页面
section = doc.sections[0]
section.page_width = Inches(8.27)  # A4
section.page_height = Inches(11.69)
section.left_margin = Inches(1)
section.right_margin = Inches(1)
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)

# 添加标题
title = doc.add_heading('标题', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 添加段落
p = doc.add_paragraph()
run = p.add_run('正文内容')
run.font.size = Pt(12)
run.font.name = 'Times New Roman'
run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

# 添加表格
table = doc.add_table(rows=3, cols=3, style='Table Grid')

# 保存
doc.save('output.docx')
```

### openpyxl（Excel .xlsx）
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = Workbook()
ws = wb.active

# 写入数据
ws['A1'] = '标题'
ws['A1'].font = Font(name='Arial', size=14, bold=True, color='FFFFFF')
ws['A1'].fill = PatternFill(start_color='4472C4', fill_type='solid')
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

# 列宽行高
ws.column_dimensions['A'].width = 20
ws.row_dimensions[1].height = 30

# 合并单元格
ws.merge_cells('A1:D1')

wb.save('output.xlsx')
```

### python-pptx（PowerPoint .pptx）
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title + Content

title = slide.shapes.title
title.text = "标题"
title.text_frame.paragraphs[0].font.size = Pt(32)
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0x33, 0x33, 0x33)

# 添加文本框
txBox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(4))
tf = txBox.text_frame
tf.text = "正文内容"

prs.save('output.pptx')
```

### reportlab / fpdf2（PDF）
```python
# fpdf2 示例
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(text="Hello World")
pdf.output("output.pdf")
```

---

## 六、设计资源推荐

### 配色工具
- Adobe Color (color.adobe.com)
- Coolors (coolors.co)
- Material Design Color System

### 字体资源
- Google Fonts（免费）
- 思源黑体/宋体（Adobe + Google 开源）
- 方正字库（商业）
- 站酷字体（免费可商用）

### 模板资源
- Canva（在线设计）
- Visme（报告模板）
- Envato Elements（高质量模板）
- Slidesgo（PPT 模板）

### 设计灵感
- Pinterest（搜索 "document design"）
- Behance
- Dribbble
- Awwwards

---

## 七、快速检查清单

制作文档时，按以下清单检查：

- [ ] 字体不超过 3 种
- [ ] 字号层级清晰（标题 > 副标题 > 正文）
- [ ] 行距 1.15-1.5 倍
- [ ] 段落间距 > 行间距
- [ ] 所有元素对齐到网格
- [ ] 颜色不超过 5 种
- [ ] 文字与背景对比度足够
- [ ] 相关元素靠近（亲密性）
- [ ] 重复元素保持一致
- [ ] 重点内容通过对比突出
- [ ] 留白充足（内容不超过页面 60%）
- [ ] 页码、页眉/页脚完整
- [ ] 中英文标点正确
- [ ] 首行缩进（中文文档）
