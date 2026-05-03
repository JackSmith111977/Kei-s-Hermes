---
name: html-guide
description: HTML/CSS 网页排版原子技能。创建可打印的网页文档。
metadata:
  hermes:
    tags: [html, css, web, print]
    category: productivity
    skill_type: doc-generation
    format: html
---

# HTML/CSS 原子操作技能

> 默认使用中文，除非用户特意说明。

## 基础模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>文档标题</title>
<style>
  body {
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 16px; line-height: 1.8; color: #333;
    max-width: 800px; margin: 0 auto; padding: 40px 20px;
  }
  h1 { font-size: 2em; border-bottom: 2px solid #4472C4; padding-bottom: 10px; }
  h2 { font-size: 1.5em; color: #4472C4; }
  p { margin: 1em 0; text-indent: 2em; }
  code { font-family: "Fira Code", Consolas, monospace; background: #f5f5f5; padding: 2px 6px; }
  pre { background: #2d2d2d; color: #f8f8f2; padding: 16px; border-radius: 8px; overflow-x: auto; }
  blockquote { border-left: 4px solid #4472C4; padding-left: 16px; color: #666; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #ddd; padding: 8px 12px; }
  th { background: #4472C4; color: white; }

  @media print {
    body { padding: 0; max-width: 100%; }
    @page { size: A4; margin: 2cm 2.5cm; }
    h1, h2, h3 { page-break-after: avoid; }
    table, pre { page-break-inside: avoid; }
  }
</style>
</head>
<body>
  <h1>文档标题</h1>
  <p>正文内容...</p>
</body>
</html>
```

## HTML → PDF 工具

```bash
# wkhtmltopdf
wkhtmltopdf --page-size A4 input.html output.pdf

# WeasyPrint（CSS 支持更好）
weasyprint input.html output.pdf

# Python
import pdfkit
pdfkit.from_file('input.html', 'output.pdf')
```
