---
name: epub-guide
description: EPUB 电子书生成快速入口 — 核心代码速查
version: 1.0.0
type: redirect
redirect_to: pdf-layout
triggers:
- epub guide
- epub-guide
- 电子书
metadata:
  hermes:
    tags:
    - epub
    - quick-ref
    - redirect
    category: productivity
    skill_type: experience-quickref
depends_on:
  - pandoc
  - web-access

---

# EPUB 电子书快速入口

> 💡 **完整 PDF/文档排版请用 `pdf-layout` skill**。

## 快速代码

```python
from ebooklib import epub
book = epub.EpubBook()
book.set_identifier('id-001')
book.set_title('标题')
book.set_language('zh-CN')
book.add_author('作者')
ch = epub.EpubHtml(title='第1章', file_name='chap_1.xhtml', lang='zh-CN')
ch.content = '<h1>第1章</h1><p>内容</p>'
book.add_item(ch)
book.toc = [epub.Link('chap_1.xhtml', '第1章', 'chap_1')]
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
epub.write_epub('output.epub', book, {})
```

> 💡 本 skill 已降级为 doc-engine 包的 experience。直接用法见 packs/doc-engine/EXPERIENCES/epub-quick-ref.md

## Verification Checklist

- [ ] Read the full content to ensure understanding
- [ ] Verify all code examples are syntactically correct
- [ ] Check that all referenced files exist
- [ ] Test the workflow with a simple input

## Common Pitfalls

1. **Missing dependencies**: Ensure all required tools are installed before starting.
2. **Wrong input format**: Verify input matches the expected format before processing.
3. **Version mismatch**: Check version compatibility between tools.
