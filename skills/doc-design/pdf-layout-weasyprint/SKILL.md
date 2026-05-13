---
name: pdf-layout-weasyprint
description: WeasyPrint 引擎快速参考 — 内容已整合到 pdf-layout v3.0，本 skill 保留 CSS 打印要点
version: 2.0.0
type: redirect
redirect_to: pdf-layout
triggers:
- weasyprint
- css 打印
- html 转 pdf
metadata:
  hermes:
    tags:
    - weasyprint
    - pdf
    - css-print
    - html-to-pdf
    - redirect
    category: productivity
    skill_type: engine-quickref
---

# WeasyPrint 快速参考

> 💡 **完整 PDF 排版请用 `pdf-layout` v3.0**（双引擎统一入口）。
> 本 skill 保留 WeasyPrint 独有的 CSS 打印要点。

## CSS 打印关键点

```css
@page {
  size: A4;
  margin: 2cm;
  @top-center { content: "页眉"; }
  @bottom-center { content: "第 " counter(page) " 页"; }
}

body { font-family: 'WenQuanYi Zen Hei', sans-serif; font-size: 11pt; line-height: 1.8; }
h1, h2, h3 { page-break-after: avoid; }
table { page-break-inside: avoid; }
pre { white-space: pre-wrap; word-break: break-all; }
```

## WeasyPrint 独有特性

| 特性 | 说明 |
|:-----|:------|
| `string()` | 从 HTML 元素提取内容到页眉页脚 |
| `target-counter()` | 交叉引用（如「详见第 X 页」） |
| `element()` | 将指定元素渲染到页眉区域 |
| 多列布局 | CSS `columns` 支持良好 |
| SVG 支持 | 原生嵌入，不依赖外部工具 |

## 常见问题

| 问题 | 解决 |
|:-----|:------|
| 中文白页 | 安装中文字体: `apt install fonts-wqy-zenhei` |
| 大文件 OOM | 分块生成后用 `pdfunite` 合并 |
| 自定义字体不生效 | 在 CSS 中用 `@font-face` 指定绝对路径 |
