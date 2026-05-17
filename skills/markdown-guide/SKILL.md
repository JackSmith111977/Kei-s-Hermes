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
depends_on:
  - pandoc
  - web-access

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

> 💡 本 skill 已降级为 doc-engine 包的 experience。直接用法见 packs/doc-engine/EXPERIENCES/markdown-quick-ref.md

## Verification Checklist

- [ ] Read the full content to ensure understanding
- [ ] Verify all code examples are syntactically correct
- [ ] Check that all referenced files exist
- [ ] Test the workflow with a simple input

## Common Pitfalls

1. **Missing dependencies**: Ensure all required tools are installed before starting.
2. **Wrong input format**: Verify input matches the expected format before processing.
3. **Version mismatch**: Check version compatibility between tools.
