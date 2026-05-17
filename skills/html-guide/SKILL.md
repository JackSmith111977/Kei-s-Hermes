---
name: html-guide
description: HTML 文档排版快速入口 — 核心模板速查，完整演示文稿请用 html-presentation skill
version: 1.0.0
type: redirect
redirect_to: html-presentation
triggers:
- html guide
- html-guide
- 网页排版
metadata:
  hermes:
    tags:
    - html
    - quick-ref
    - redirect
    category: productivity
    skill_type: experience-quickref
depends_on: []

---

# HTML 文档排版快速入口

> 💡 **完整 HTML 演示文稿请用 `html-presentation` skill**（reveal.js/Slidev/Marp 四大方案）。

## 快速模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>文档</title>
<style>
  body { max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.8; }
  code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }
  @media print { body { font-size: 12pt; } }
</style>
</head>
<body>
<h1>标题</h1>
<p>正文</p>
</body>
</html>
```

> 💡 本 skill 已降级为 doc-engine 包的 experience。直接用法见 packs/doc-engine/EXPERIENCES/html-quick-ref.md
