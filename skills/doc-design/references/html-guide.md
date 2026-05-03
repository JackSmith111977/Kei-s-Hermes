# HTML/CSS 排版指南

## 基础文档模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>文档标题</title>
<style>
  /* === 基础排版 === */
  body {
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 20px;
  }

  /* === 标题 === */
  h1 { font-size: 2em; border-bottom: 2px solid #4472C4; padding-bottom: 10px; }
  h2 { font-size: 1.5em; color: #4472C4; }
  h3 { font-size: 1.2em; }

  /* === 段落 === */
  p { margin: 1em 0; text-indent: 2em; }

  /* === 代码 === */
  code {
    font-family: "Fira Code", Consolas, "Source Code Pro", monospace;
    background: #f5f5f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.9em;
  }
  pre {
    background: #2d2d2d;
    color: #f8f8f2;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
  }
  pre code { background: none; padding: 0; color: inherit; }

  /* === 引用 === */
  blockquote {
    border-left: 4px solid #4472C4;
    padding-left: 16px;
    color: #666;
    margin: 1em 0;
  }

  /* === 表格 === */
  table { border-collapse: collapse; width: 100%; margin: 1em 0; }
  th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
  th { background: #4472C4; color: white; }
  tr:nth-child(even) { background: #f9f9f9; }

  /* === 图片 === */
  img { max-width: 100%; height: auto; }

  /* === 打印优化 === */
  @media print {
    body { padding: 0; max-width: 100%; }
    .no-print { display: none; }

    @page {
      size: A4;
      margin: 2cm 2.5cm;
      @bottom-center {
        content: counter(page);
        font-size: 10pt;
      }
    }

    h1, h2, h3 { page-break-after: avoid; }
    table, figure, pre { page-break-inside: avoid; }
    .new-page { page-break-before: always; }

    a[href]::after {
      content: " (" attr(href) ")";
      font-size: 0.8em;
      color: #666;
    }
  }
</style>
</head>
<body>
  <h1>文档标题</h1>
  <p>正文内容...</p>
</body>
</html>
```

## 网格系统

```css
/* 12 列网格 */
.container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.col-6 { grid-column: span 6; }
.col-4 { grid-column: span 4; }
.col-3 { grid-column: span 3; }
```

## Flexbox 布局

```css
/* 居中 */
.center {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 等分列 */
.row {
  display: flex;
  gap: 20px;
}
.row > * {
  flex: 1;
}
```

## HTML → PDF 工具

```bash
# wkhtmltopdf（最常用）
wkhtmltopdf --page-size A4 --margin-top 20mm --margin-bottom 20mm input.html output.pdf

# WeasyPrint（CSS 支持更好）
weasyprint input.html output.pdf

# Python
import pdfkit
pdfkit.from_file('input.html', 'output.pdf')
```
