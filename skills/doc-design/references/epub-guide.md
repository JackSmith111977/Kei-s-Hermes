# EPUB 完整指南

> 库：`ebooklib` | 安装：`pip install ebooklib`

## EPUB 文件结构

```
book.epub (ZIP 包)
├── mimetype                  # 必须是第一个文件，内容：application/epub+zip
├── META-INF/
│   └── container.xml         # 指向 OPF 文件
└── OEBPS/
    ├── content.opf           # 清单文件（所有资源列表）
    ├── toc.ncx               # 目录（旧版）
    ├── nav.xhtml             # 导航（EPUB3）
    ├── stylesheet.css        # CSS 样式
    ├── cover.xhtml           # 封面
    ├── title-page.xhtml      # 书名页
    ├── chapter01.xhtml       # 章节内容
    ├── chapter02.xhtml
    └── images/
        └── cover.jpg
```

## CSS 最佳实践

```css
/* 电子书排版 */
body {
  font-family: "Noto Serif SC", "PingFang SC", serif;
  font-size: 1em;
  line-height: 1.8;
  margin: 0;
  padding: 0;
  text-align: justify;
}

h1 {
  font-size: 1.8em;
  text-align: center;
  margin-top: 3em;
  margin-bottom: 1em;
  page-break-before: always;
}

h2 {
  font-size: 1.4em;
  margin-top: 2em;
  margin-bottom: 0.8em;
}

p {
  text-indent: 2em;
  margin: 0;
  orphans: 2;
  widows: 2;
}

.no-indent { text-indent: 0; }
.center { text-align: center; }

/* 封面 */
.cover {
  text-align: center;
  page-break-after: always;
}
.cover img {
  max-width: 100%;
  max-height: 100%;
}

/* 目录 */
.toc a {
  text-decoration: none;
  color: inherit;
}

/* 图片 */
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1em auto;
}

/* 代码 */
pre {
  font-size: 0.85em;
  background: #f5f5f5;
  padding: 1em;
  overflow-x: auto;
  white-space: pre-wrap;
}

code {
  font-family: "Fira Code", Consolas, monospace;
  font-size: 0.9em;
}

/* 引用 */
blockquote {
  margin: 1em 2em;
  padding-left: 1em;
  border-left: 3px solid #ccc;
  color: #555;
}
```

## Python 生成 EPUB

```python
from ebooklib import epub

book = epub.EpubBook()
book.set_identifier('book-001')
book.set_title('书名')
book.set_language('zh-CN')
book.add_author('作者')
book.add_metadata('DC', 'description', '书籍描述')

# 添加封面
with open('cover.jpg', 'rb') as f:
    book.set_cover('cover.jpg', f.read())

# CSS 样式
style = '''
body { font-family: serif; font-size: 1em; line-height: 1.8; }
h1 { text-align: center; font-size: 1.8em; margin-top: 3em; }
p { text-indent: 2em; margin: 0; }
'''
nav_css = epub.EpubItem(
    uid="style_nav",
    file_name="style/nav.css",
    media_type="text/css",
    content=style
)
book.add_item(nav_css)

# 章节
chapters = []
for i, (title, content) in enumerate([
    ('第一章', '<h1>第一章</h1><p>正文内容...</p>'),
    ('第二章', '<h1>第二章</h1><p>正文内容...</p>'),
], 1):
    chapter = epub.EpubHtml(
        title=title,
        file_name=f'chap{i:02d}.xhtml',
        lang='zh-CN'
    )
    chapter.content = content
    chapter.add_link(href='style/nav.css', rel='stylesheet', type='text/css')
    book.add_item(chapter)
    chapters.append(chapter)

# 目录
book.toc = tuple(chapters)
book.spine = ['nav'] + chapters

# 添加导航文件
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# 写入
epub.write_epub('book.epub', book)
print("EPUB 生成成功!")
```

## 验证 EPUB

```bash
# 使用 epubcheck
java -jar epubcheck.jar book.epub

# Python 验证
python -m ebooklib validate book.epub
```
