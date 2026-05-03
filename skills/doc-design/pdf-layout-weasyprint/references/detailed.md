# Detailed Reference

## 三、中文支持（@font-face）

关键一步：用 CSS `@font-face` 注册中文字体。**注意：使用 @font-face 时必须创建 FontConfiguration 对象。**

```python
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

font_config = FontConfiguration()

css = CSS(string="""
@font-face {
  font-family: 'WQY';
  src: url('file:///usr/share/fonts/truetype/wqy/wqy-zenhei.ttc');
}
body { 
  font-family: 'WQY', sans-serif; 
  font-size: 10pt;
  margin: 20mm;
}
""", font_config=font_config)

html = HTML(string="""<html>
<head><meta charset="utf-8"></head>
<body>
  <h1>中文标题</h1>
  <p>这是中文正文内容～</p>
</body>
</html>""")

html.write_pdf("output.pdf", stylesheets=[css], font_config=font_config)
```

### 多字体配置
```css
@font-face {
  font-family: 'WQY';
  src: url('file:///usr/share/fonts/truetype/wqy/wqy-zenhei.ttc');
}
/* 等宽字体 */
@font-face {
  font-family: 'Mono';
  src: url('file:///usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf');
}
body { font-family: 'WQY', serif; }
code, pre { font-family: 'Mono', monospace; }
```

> ⚠️ `@font-face` 的 `src` 必须是 `file://` 绝对路径，不能是系统字体名
> ⚠️ 使用 `@font-face` 时必须将 `font_config` 同时传给 CSS 和 write_pdf
> ⚠️ 如果不使用 `@font-face`（系统字体即可），可以省略 FontConfiguration

## 四、布局与 CSS

### 页边距
```css
@page {
  size: A4;
  margin: 20mm 25mm;
}

/* 不同页面不同的边距 */
@page :first {
  margin: 0;  /* 首页无边距（适合封面） */
}
```

### 分页控制
```css
/* 每章新的一页 */
h1 { 
  page-break-before: always; 
}
h1:first-of-type { 
  page-break-before: avoid; /* 首页不提前分页 */
}

/* 不分页的内容 */
.no-break {
  page-break-inside: avoid;
}

/* 元素在一起（表头+表格） */
table {
  page-break-inside: avoid;
}
```

### 表格
```css
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #CCCCCC;
  padding: 6px 8px;
  text-align: left;
}
th {
  background-color: #2C3E50;
  color: white;
}
/* 斑马纹 */
tr:nth-child(even) {
  background-color: #F8F9FA;
}
/* 跨页重复表头 */
thead { 
  display: table-header-group; 
}
tfoot { 
  display: table-footer-group; 
}
```

## 五、页眉页脚（Running Elements）

```css
@page {
  @top-left {
    content: "我的文档";
    font-size: 8pt;
    color: #888;
    font-family: 'WQY';
  }
  @top-right {
    content: "第 " counter(page) " 页";
    font-size: 8pt;
    color: #888;
    font-family: 'WQY';
  }
  @bottom-center {
    content: "— " counter(page) " —";
    font-size: 8pt;
    color: #AAA;
    font-family: 'WQY';
  }
}
```

### 第一页不同的页眉
```css
@page :first {
  @top-left { content: none; }
  @top-right { content: none; }
  @bottom-center { content: none; }
}
```

## 六、Jinja2 模板集成（推荐做法）

对于复杂文档，推荐用 Jinja2 模板 + 单独 CSS 文件的方式：

### 目录结构
```
project/
├── template.html    # Jinja2 HTML 模板
├── style.css        # 单独 CSS 文件
├── generate.py      # 生成脚本
└── output.pdf       # 生成的 PDF
```

### template.html
```html
<html>
<head><meta charset="utf-8"><title>{{ title }}</title></head>
<body>
<div class="cover">
  <h1>{{ title }}</h1>
  <p>{{ subtitle }}</p>
</div>
{% for chapter in chapters %}
<h1>{{ chapter.title }}</h1>
{% for para in chapter.paragraphs %}
<p>{{ para }}</p>
{% endfor %}
{% if chapter.table %}
<table>
<thead><tr>{% for col in chapter.table.headers %}<th>{{ col }}</th>{% endfor %}</tr></thead>
<tbody>
{% for row in chapter.table.rows %}
<tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}</tr>
{% endfor %}
</tbody>
</table>
{% endif %}
{% endfor %}
</body>
</html>
```

### generate.py
```python
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, FileSystemLoader
import json

# 加载模板
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

# 渲染 HTML
html_str = template.render(
    title="项目文档",
    subtitle="使用 WeasyPrint 生成",
    chapters=[
        {"title": "第一章", "paragraphs": ["内容..."]},
    ]
)

# 加载 CSS
font_config = FontConfiguration()
css = CSS(filename="style.css", font_config=font_config)

# 生成 PDF
HTML(string=html_str).write_pdf(
    "output.pdf",
    stylesheets=[css],
    font_config=font_config
)
```

### style.css
```css
@font-face {
  font-family: 'WQY';
  src: url('file:///usr/share/fonts/truetype/wqy/wqy-zenhei.ttc');
}
@page { size: A4; margin: 20mm; }
@page :first { margin: 0; }
body { font-family: 'WQY', sans-serif; font-size: 10pt; line-height: 1.6; color: #333; }
.cover { text-align: center; padding-top: 25%; }
.cover h1 { font-size: 28pt; color: #1a1a2e; page-break-before: avoid; }
h1 { font-size: 18pt; color: #2C3E50; page-break-before: always; margin-top: 15mm; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; color: #34495E; page-break-after: avoid; }
p { text-indent: 2em; margin: 0.3em 0; }
table { width: 100%; border-collapse: collapse; margin: 1em 0; }
th, td { border: 1px solid #CCC; padding: 6px 8px; }
th { background: #2C3E50; color: white; }
tr:nth-child(even) { background: #F8F9FA; }
thead { display: table-header-group; }
```

## 七、目录（使用 HTML 锚点）

```html
<div class="toc">
  <h2>目录</h2>
  <ul>
    <li><a href="#ch1">第一章：简介</a></li>
    <li><a href="#ch2">第二章：架构</a></li>
  </ul>
</div>

<h1 id="ch1">第一章：简介</h1>
...
<h1 id="ch2">第二章：架构</h1>
```

WeasyPrint 会自动根据锚点链接生成可点击的目录（PDF 书签）。

## 八、Python API 高级用法

### 逐页渲染
```python
from weasyprint import HTML

# 渲染后获取页面信息
doc = HTML(string=html).render()
print(f"总页数: {len(doc.pages)}")
print(f"页面大小: {doc.pages[0].page_size}")

# 导出子集（奇数页和偶数页分开）
doc.copy(doc.pages[::2]).write_pdf("odd_pages.pdf")
doc.copy(doc.pages[1::2]).write_pdf("even_pages.pdf")

# 获取 PDF 字节（不写文件）
pdf_bytes = HTML(string=html).write_pdf()
```

### 从 URL 生成
```python
# 从网址
HTML(url="https://example.com").write_pdf("page.pdf")

# 从本地文件
HTML(filename="template.html").write_pdf("output.pdf")

# 从文件对象
import sys
HTML(file_obj=sys.stdin).write_pdf("stdin.pdf")

# 内存中（返回 bytes）
data = HTML(string=html).write_pdf()
```

### 自定义 Stylesheet
```python
from weasyprint import CSS

# 从字符串
css1 = CSS(string="body { font-family: serif !important; }")

# 从文件
css2 = CSS(filename="print.css")

# 多个 stylesheet 叠加
html.write_pdf("output.pdf", stylesheets=[css1, css2])
```

### FontConfiguration 详解
```python
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

font_config = FontConfiguration()

# CSS 和 write_pdf 都必须传入同一个 font_config 对象
css = CSS(string="""@font-face {
  font-family: 'WQY';
  src: url('file:///path/to/wqy-zenhei.ttc');
}
body { font-family: 'WQY'; }
""", font_config=font_config)

HTML(string=html).write_pdf("out.pdf",
    stylesheets=[css],
    font_config=font_config
)
```

### URLFetcher（网络资源控制）
```python
from weasyprint import HTML
from weasyprint.urls import URLFetcher

# 设置超时
HTML(string="", url_fetcher=URLFetcher(timeout=20)).write_pdf("out.pdf")

# 自定义 Fetcher（拦截特定 URL）
class MyFetcher(URLFetcher):
    def fetch(self, url, headers=None):
        if url.startswith("http://internal/"):
            # 处理内部资源
            return super().fetch(url.replace("http://internal/", "file:///"))
        return super().fetch(url, headers)

HTML(string=html, url_fetcher=MyFetcher()).write_pdf("out.pdf")
```

## 八、ReportLab → WeasyPrint 迁移

| ReportLab | WeasyPrint 等价写法 |
|:---|:---|
| `PageBreak()` | `page-break-before: always` |
| `CondPageBreak(100)` | `page-break-before: avoid` + 内容够自然溢出 |
| `KeepTogether([...])` | `page-break-inside: avoid` |
| `ParagraphStyle(name, ...)` | CSS 类选择器 |
| `Table(data, ...)` | `<table>` 标签 |
| `Image("path", width, height)` | `<img src="..." style="width:...">` |
| `registerFont(TTFont(...))` | `@font-face { src: url('file://...') }` |
| `onFirstPage=header_footer` | `@page { @top-left { ... } }` |

## 九、边界情况

| 场景 | 处理方式 |
|:---|:---|
| 大表格跨页 | `thead { display: table-header-group; }` 自动重复表头 |
| 图片太大 | `img { max-width: 100%; }` |
| 长代码不换行 | `pre { word-break: break-all; }` |
| 中文标点溢出 | `p { overflow-wrap: break-word; }` |
| 打印版 vs 屏幕版 | 用 `@media print { ... }` 区分 |

## 十一、安全注意事项

在服务器上用 WeasyPrint 处理不可信的 HTML/CSS 时需要注意：

| 风险 | 说明 | 应对 |
|:---|:---|:---|
| 长时间渲染 | 恶意 HTML 可导致 CPU 和内存暴涨 | 用 `ulimit`、uWSGI 的 `harakiri` 限制 |
| 无限请求 | HTTP 资源可被用于慢速攻击 | 设置 URLFetcher timeout（默认 10s） |
| 本地文件泄露 | `file://` URI 可读取服务器文件 | 自定义 URLFetcher 拦截 file:// |
| 巨大值攻击 | 超大 font-size/page-size 可耗尽资源 | 限制进程内存使用 |
| SVG 安全问题 | SVG 渲染也存在类似风险 | 同 HTML/CSS 安全策略 |

## 十二、安装检查清单

- [ ] `sudo apt install weasyprint -y` 安装系统包
- [ ] `weasyprint --version` 验证 CLI 可用
- [ ] `python3 -c "from weasyprint import HTML; print('OK')"` 验证 Python 模块
- [ ] `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` 存在（WQY 字体）
- [ ] 先跑 Hello World 测试
- [ ] Jinja2 可用（`pip install jinja2`）

## 十三、参考资源

- [官方文档](https://doc.courtbouillon.org/weasyprint/latest/)
- [GitHub 仓库](https://github.com/Kozea/WeasyPrint)
- [示例项目](https://github.com/CourtBouillon/weasyprint-samples)
- [WeasyPrint 官网](https://weasyprint.org/)
