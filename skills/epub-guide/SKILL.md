---
name: epub-guide
description: EPUB 电子书生成原子技能。使用 ebooklib 创建标准 EPUB 电子书。
metadata:
  hermes:
    tags: [epub, ebook, publishing]
    category: productivity
    skill_type: doc-generation
    format: epub
---

# EPUB 原子操作技能

> 库：`ebooklib` | 安装：`pip install ebooklib`
> 默认使用中文，除非用户特意说明。

## EPUB 文件结构

```
book.epub (ZIP 包)
├── mimetype                  # application/epub+zip
├── META-INF/
│   └── container.xml
└── OEBPS/
    ├── content.opf           # 清单文件
    ├── nav.xhtml             # 导航（EPUB3）
    ├── stylesheet.css        # CSS 样式
    ├── cover.xhtml           # 封面
    ├── chapter01.xhtml       # 章节
    └── images/
        └── cover.jpg
```

## CSS 样式

```css
body {
  font-family: "Noto Serif SC", "PingFang SC", serif;
  font-size: 1em; line-height: 1.8;
  text-align: justify;
}
h1 { font-size: 1.8em; text-align: center; margin-top: 3em; page-break-before: always; }
p { text-indent: 2em; margin: 0; }
.cover { text-align: center; page-break-after: always; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
```

## Python 生成 EPUB

```python
from ebooklib import epub

book = epub.EpubBook()
book.set_identifier('book-001')
book.set_title('书名')
book.set_language('zh-CN')
book.add_author('作者')

# 封面
with open('cover.jpg', 'rb') as f:
    book.set_cover('cover.jpg', f.read())

# CSS
style = 'body { font-family: serif; line-height: 1.8; } p { text-indent: 2em; }'
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css",
                         media_type="text/css", content=style)
book.add_item(nav_css)

# 章节
chapters = []
for i, (title, html) in enumerate([('第一章', '<h1>第一章</h1><p>内容...</p>')], 1):
    ch = epub.EpubHtml(title=title, file_name=f'chap{i:02d}.xhtml', lang='zh-CN')
    ch.content = html
    ch.add_link(href='style/nav.css', rel='stylesheet', type='text/css')
    book.add_item(ch)
    chapters.append(ch)

book.toc = tuple(chapters)
book.spine = ['nav'] + chapters
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

epub.write_epub('book.epub', book)
```

## 验证

```bash
# epubcheck
java -jar epubcheck.jar book.epub
```
