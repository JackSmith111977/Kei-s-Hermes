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
