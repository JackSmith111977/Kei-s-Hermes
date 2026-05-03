# 扩展格式学习笔记

> 整理时间：2026-05-02
> 覆盖格式：Markdown、LaTeX、HTML/CSS、EPUB、CSV/JSON/YAML/TOML、ODT/RTF、XML/XSLT

---

## 七、Markdown 深度指南

### 最佳实践
- **标题**：只用 ATX 风格（`#`），不用底线风格
- **列表**：无序用 `-`，有序用 `1.`
- **嵌套**：2 或 4 空格缩进（保持一致）
- **加粗**：`**bold**`，斜体：`*italic*`
- **链接**：超过 5 个链接时用引用式 `[text][id]` + `[id]: url`
- **代码**：行内用反引号，块用三个反引号 + 语言名
- **表格**：用 `:` 控制对齐（左/右/中）
- **空行**：标题、列表、代码块、表格前后必须有空行

### 目录（TOC）
- iA Writer：`{{TOC}}`
- GitHub：自动生成（基于标题）
- Pandoc：`--toc` 参数

### 脚注与引用
```markdown
正文内容[^1]。

[^1]: 脚注内容

# 学术引用（Pandoc citeproc）
正文 @author2024 说...

# references.bib（BibTeX）
@article{author2024,
  title={标题},
  author={作者},
  journal={期刊},
  year={2024}
}
```
```bash
pandoc input.md -o output.docx --citeproc --bibliography=references.bib --csl=apa.csl
```

### 高级技巧
- 折叠内容：`<details><summary>标题</summary>内容</details>`
- 任务列表：`- [x] 已完成` / `- [ ] 未完成`
- 数学公式：`$行内$` / `$$块级$$`
- HTML 嵌入：Markdown 不支持的格式可用 HTML
- 注释：`<!-- 注释 -->`

---

## 八、LaTeX 深度指南

### 文档结构
```latex
\documentclass[12pt,a4paper]{article}
% 导言区
\usepackage[UTF8]{ctex}          % 中文
\usepackage{geometry}            % 页面
\usepackage{graphicx}            % 图片
\usepackage{hyperref}            % 超链接
\usepackage{xcolor}              % 颜色
\usepackage{listings}            % 代码
\usepackage{booktabs}            % 专业表格
\usepackage{amsmath}             % 数学

\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}

% 自定义颜色
\definecolor{codebg}{RGB}{245,245,245}
\definecolor{codegreen}{RGB}{0,128,0}

% 代码样式
\lstset{
    backgroundcolor=\color{codebg},
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single
}

\begin{document}
\title{标题}
\author{作者}
\date{\today}
\maketitle
\tableofcontents
\newpage

\section{第一节}
\subsection{小节}
正文 $E=mc^2$。

\begin{lstlisting}[language=Python]
print("Hello")
\end{lstlisting}

\begin{table}[h]
\centering
\caption{表格标题}
\begin{tabular}{lcc}
\toprule
列1 & 列2 & 列3 \\
\midrule
A & B & C \\
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{image.png}
\caption{图片标题}
\end{figure}

\bibliographystyle{plain}
\bibliography{references}

\end{document}
```

### 编译命令
```bash
# 中文文档
xelatex document.tex
bibtex document
xelatex document.tex
xelatex document.tex

# 或使用 latexmk 自动编译
latexmk -xelatex document.tex
```

### 学位论文模板结构
```
thesis/
├── main.tex              # 根文件
├── preamble.tex          # 宏包和设置
├── chapters/
│   ├── 01-intro.tex
│   ├── 02-related.tex
│   ├── 03-method.tex
│   ├── 04-results.tex
│   └── 05-conclusion.tex
├── front-matter/
│   ├── abstract.tex
│   ├── acknowledgments.tex
│   └── title-page.tex
├── back-matter/
│   ├── appendices.tex
│   └── glossary.tex
├── figures/
└── references.bib
```

---

## 九、HTML/CSS 排版指南

### 打印/PDF 优化 CSS
```css
/* 打印样式 */
@media print {
  /* 基础排版 */
  body {
    font-family: "PingFang SC", "Noto Serif SC", serif;
    font-size: 12pt;
    line-height: 1.8;
    color: #000;
    max-width: 100%;
    margin: 0;
    padding: 0;
  }

  /* 页面设置 */
  @page {
    size: A4;
    margin: 2cm 2.5cm;
    @bottom-center {
      content: counter(page);
      font-size: 10pt;
    }
  }

  /* 分页控制 */
  h1, h2, h3 {
    page-break-after: avoid;
  }
  table, figure, pre {
    page-break-inside: avoid;
  }
  .new-page {
    page-break-before: always;
  }

  /* 隐藏不必要元素 */
  .no-print, nav, footer, .sidebar {
    display: none !important;
  }

  /* 链接显示 URL */
  a[href]::after {
    content: " (" attr(href) ")";
    font-size: 0.8em;
    color: #666;
  }

  /* 表格打印优化 */
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th {
    background: #eee !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* 图片 */
  img {
    max-width: 100%;
    height: auto;
  }

  /* 代码块 */
  pre {
    border: 1px solid #ddd;
    padding: 12px;
    font-size: 9pt;
    white-space: pre-wrap;
  }
}
```

### HTML → PDF 工具
```bash
# wkhtmltopdf（最常用）
wkhtmltopdf --page-size A4 --margin-top 20mm input.html output.pdf

# WeasyPrint（CSS 支持更好）
weasyprint input.html output.pdf

# Prince（商业，质量最高）
prince input.html -o output.pdf

# Python
import pdfkit
pdfkit.from_file('input.html', 'output.pdf')
```

---

## 十、EPUB 深度指南

### EPUB 结构
```
book.epub (ZIP 包)
├── mimetype                  # 必须是第一个文件
├── META-INF/
│   └── container.xml         # 指向 OPF
├── OEBPS/
│   ├── content.opf           # 清单文件
│   ├── toc.ncx               # 目录
│   ├── stylesheet.css        # CSS
│   ├── cover.xhtml           # 封面
│   ├── title-page.xhtml      # 书名页
│   ├── chapter01.xhtml       # 章节
│   └── images/
│       └── cover.jpg
```

### EPUB CSS 最佳实践
```css
/* 电子书排版 */
body {
  font-family: "Noto Serif SC", serif;
  font-size: 1em;
  line-height: 1.8;
  margin: 0;
  padding: 0;
  text-align: justify;
}

h1 {
  font-size: 1.8em;
  text-align: center;
  margin-top: 3em;
  margin-bottom: 1em;
  page-break-before: always;
}

h2 {
  font-size: 1.4em;
  margin-top: 2em;
  margin-bottom: 0.8em;
}

p {
  text-indent: 2em;
  margin: 0;
  orphans: 2;
  widows: 2;
}

.no-indent {
  text-indent: 0;
}

/* 封面 */
.cover {
  text-align: center;
  page-break-after: always;
}
.cover img {
  max-width: 100%;
  max-height: 100%;
}

/* 目录 */
.toc a {
  text-decoration: none;
  color: inherit;
}

/* 图片 */
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1em auto;
}

/* 代码 */
pre {
  font-size: 0.85em;
  background: #f5f5f5;
  padding: 1em;
  overflow-x: auto;
  white-space: pre-wrap;
}

/* 引用 */
blockquote {
  margin: 1em 2em;
  padding-left: 1em;
  border-left: 3px solid #ccc;
  color: #555;
}
```

### Python 生成 EPUB
```python
from ebooklib import epub

book = epub.EpubBook()
book.set_identifier('book-001')
book.set_title('书名')
book.set_language('zh-CN')
book.add_author('作者')
book.add_metadata('DC', 'description', '书籍描述')

# CSS
style = '''
body { font-family: serif; font-size: 1em; line-height: 1.8; }
h1 { text-align: center; font-size: 1.8em; margin-top: 3em; }
p { text-indent: 2em; margin: 0; }
'''
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
book.add_item(nav_css)

# 章节
ch1 = epub.EpubHtml(title='第一章', file_name='chap01.xhtml', lang='zh-CN')
ch1.content = '<h1>第一章</h1><p>正文内容...</p>'
ch1.add_link(href='style/nav.css', rel='stylesheet', type='text/css')
book.add_item(ch1)

# 目录
book.toc = (epub.Link('chap01.xhtml', '第一章', 'ch1'),
            epub.Section('正文'))
book.spine = ['nav', ch1]

# 添加导航
book.add_item(epub.EpubNcx())
book.add_item(epub.Enav())

epub.write_epub('book.epub', book)
```

---

## 十一、数据格式（CSV/JSON/YAML/TOML）

### 格式选择指南

| 格式 | 特点 | 适用场景 |
|------|------|----------|
| **CSV** | 简单表格，无嵌套 | 数据交换、Excel 导入 |
| **JSON** | 层级结构，无注释 | API 配置、NoSQL |
| **YAML** | 可读性好，支持注释 | 配置文件、CI/CD |
| **TOML** | 简洁，强类型 | 项目配置（Cargo/pyproject） |
| **INI** | 最简单 | Windows 配置、简单设置 |

### YAML 最佳实践
```yaml
# 缩进用 2 空格
# 字符串一般不用引号，特殊字符用引号
name: 项目名称
version: "1.0.0"

# 列表
dependencies:
  - python>=3.10
  - nodejs>=20

# 字典
database:
  host: localhost
  port: 5432
  name: mydb

# 多行字符串
description: |
  这是多行文本
  保留换行符

description_fold: >
  这是折行文本
  会合并为一行

# 锚点和别名（避免重复)
default: &default
  adapter: postgresql
  encoding: unicode

development:
  <<: *default
  database: dev_db
```

### JSON 最佳实践
```json
{
  "name": "project",
  "version": "1.0.0",
  "description": "项目描述",
  "scripts": {
    "build": "npm run build",
    "test": "pytest"
  },
  "dependencies": {
    "lodash": "^4.17.21"
  },
  "config": {
    "debug": false,
    "timeout": 30
  }
}
```
- 不支持注释（用 `//` 需要 JSON5）
- 键名用双引号
- 不允许尾逗号
- 数字不补零

### CSV 最佳实践
```csv
id,name,email,department,salary
1,张三,zhangsan@example.com,研发,15000
2,李四,lisi@example.com,产品,12000
```
- 第一行必须是表头
- 包含逗号的字段用引号包裹
- UTF-8 编码
- 换行符：LF（Unix）或 CRLF（Windows）

### Python 操作
```python
import json, yaml, csv, tomllib

# JSON
data = json.load(open('config.json'))
json.dump(data, open('out.json', 'w'), indent=2, ensure_ascii=False)

# YAML
data = yaml.safe_load(open('config.yaml'))
yaml.dump(data, open('out.yaml', 'w'), allow_unicode=True)

# CSV
with open('data.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

with open('out.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['col1', 'col2'])
    writer.writeheader()
    writer.writerows(data)

# TOML
with open('config.toml', 'rb') as f:
    data = tomllib.load(f)
```

---

## 十二、ODT/RTF 格式

### ODT（Open Document Format）
- **推荐**：用 LibreOffice 原生编辑，避免转换
- **最佳实践**：编辑用 ODT，最终输出再转 DOCX
- **Python 操作**：`odfpy` 库
```python
from odf.opendocument import OpenDocumentText
from odf.text import P, H
from odf.teletype import addTextToElement

doc = OpenDocumentText()
h = H(outlinelevel=1, text="标题")
doc.text.addElement(h)
p = P(text="正文内容")
doc.text.addElement(p)
doc.save("output.odt")
```

### RTF（Rich Text Format）
- **用途**：跨平台富文本交换
- **局限**：格式支持有限，不推荐用于复杂排版
- **转换**：
```bash
# LibreOffice 转换
libreoffice --headless --convert-to rtf input.odt
libreoffice --headless --convert-to odt input.rtf

# Python
import pypandoc
pypandoc.convert_file('input.md', 'rtf', outputfile='output.rtf')
```

---

## 十三、XML/XSLT

### XML 排版最佳实践
```xml
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="style"?>
<document>
  <metadata>
    <title>文档标题</title>
    <author>作者</author>
    <date>2026-05-02</date>
  </metadata>
  <chapter id="ch1">
    <title>第一章</title>
    <section>
      <title>小节</title>
      <p>正文内容</p>
      <p>包含<em>强调</em>和<strong>加粗</strong>。</p>
    </section>
  </chapter>
</document>
```

### XSLT 转换
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <html>
      <head><title><xsl:value-of select="document/metadata/title"/></title></head>
      <body>
        <xsl:apply-templates select="document/chapter"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="chapter">
    <h1><xsl:value-of select="title"/></h1>
    <xsl:apply-templates select="section"/>
  </xsl:template>

  <xsl:template match="section">
    <h2><xsl:value-of select="title"/></h2>
    <xsl:apply-templates select="p"/>
  </xsl:template>

  <xsl:template match="p">
    <p><xsl:apply-templates/></p>
  </xsl:template>

  <xsl:template match="em">
    <em><xsl:apply-templates/></em>
  </xsl:template>
</xsl:stylesheet>
```

```bash
# XSLT 转换
xsltproc style.xsl input.xml > output.html

# Python
from lxml import etree
xslt = etree.XSLT(etree.parse('style.xsl'))
result = xslt(etree.parse('input.xml'))
result.write_output('output.html')
```

---

## 十四、格式转换速查表（完整版）

### 命令行工具

```bash
# === Pandoc（万能转换器）===
pandoc input.md -o output.docx
pandoc input.md -o output.pdf --pdf-engine=xelatex -V mainfont="PingFang SC"
pandoc input.md -o output.html --standalone --css=style.css
pandoc input.md -o output.epub --epub-cover-image=cover.jpg
pandoc input.md -o output.tex
pandoc input.docx -o output.md
pandoc input.docx -o output.pdf
pandoc input.html -o output.pdf

# === LibreOffice ===
libreoffice --headless --convert-to pdf input.docx
libreoffice --headless --convert-to docx input.odt
libreoffice --headless --convert-to html input.docx
libreoffice --headless --convert-to rtf input.odt

# === wkhtmltopdf ===
wkhtmltopdf --page-size A4 input.html output.pdf

# === WeasyPrint ===
weasyprint input.html output.pdf

# === Python pypandoc ===
python3 -c "
import pypandoc
pypandoc.convert_file('input.md', 'docx', outputfile='output.docx')
pypandoc.convert_file('input.md', 'pdf', outputfile='output.pdf',
    extra_args=['--pdf-engine=xelatex', '-V', 'mainfont=PingFang SC'])
"
```

### Python 转换代码

```python
# Markdown → 任意格式
import pypandoc
pypandoc.convert_file('input.md', 'docx', outputfile='out.docx')
pypandoc.convert_file('input.md', 'pdf', outputfile='out.pdf',
    extra_args=['--pdf-engine=xelatex'])
pypandoc.convert_file('input.md', 'html', outputfile='out.html')
pypandoc.convert_file('input.md', 'epub', outputfile='out.epub')

# Word → Markdown
pypandoc.convert_file('input.docx', 'md', outputfile='out.md')

# HTML → PDF
import pdfkit
pdfkit.from_file('input.html', 'out.pdf')

# EPUB 生成
# 见上文 ebooklib 示例

# XML → HTML（XSLT）
from lxml import etree
xslt = etree.XSLT(etree.parse('style.xsl'))
result = xslt(etree.parse('input.xml'))
result.write_output('output.html')
```
