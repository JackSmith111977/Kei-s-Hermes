---
name: markdown-guide
description: Markdown 写作与转换快速入口 — pandoc 转换命令速查
version: 1.0.0
type: redirect
redirect_to: pdf-layout
triggers:
- markdown guide
- markdown-guide
- .md 转换
- pandoc 转换
metadata:
  hermes:
    tags:
    - markdown
    - pandoc
    - quick-ref
    - redirect
    category: productivity
    skill_type: experience-quickref
---

# Markdown 快速入口

> 💡 **文档生成请用 `pdf-layout` skill**。本 skill 保留 pandoc 转换核心命令。

## pandoc 转换

```bash
pandoc input.md -o output.pdf --pdf-engine=xelatex
pandoc input.md -o output.docx
pandoc input.md -o output.html -s
pandoc input.md -o output.epub
```
