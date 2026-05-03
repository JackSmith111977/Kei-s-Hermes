---
name: markdown-guide
description: Markdown 写作与转换原子技能。语法指南 + pandoc 转换 + 最佳实践。
metadata:
  hermes:
    tags: [markdown, pandoc, writing, documentation]
    category: productivity
    skill_type: doc-generation
    format: markdown
---

# Markdown 原子操作技能

> 默认使用中文，除非用户特意说明。

## 基础语法

```markdown
---
title: 文档标题
author: 作者
date: 2026-05-02
---

# 一级标题
## 二级标题
### 三级标题

**粗体** *斜体* ~~删除行~~ `行内代码`

> 引用内容

- 无序列表
- 项目二

1. 有序列表
2. 项目二

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A   | B   | C   |

```python
code block
```

[链接](https://example.com)
![图片](image.png)
```

## 最佳实践

- **标题**：只用 ATX 风格（`#`）
- **列表**：无序用 `-`，有序用 `1.`
- **嵌套**：2 或 4 空格缩进
- **代码**：行内用反引号，块用三个反引号 + 语言名
- **空行**：标题、列表、代码块前后必须有空行

## 高级功能

```markdown
<!-- 折叠内容 -->
<details>
<summary>点击展开</summary>
隐藏的内容
</details>

<!-- 任务列表 -->
- [x] 已完成
- [ ] 未完成

<!-- 数学公式 -->
行内：$E=mc^2$

块级：
$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$

<!-- 脚注 -->
正文内容[^1]。
[^1]: 脚注内容
```

## 转换命令（pandoc）

```bash
# → PDF（需要 xelatex）
pandoc input.md -o output.pdf --pdf-engine=xelatex -V mainfont="PingFang SC" --toc

# → Word
pandoc input.md -o output.docx

# → HTML
pandoc input.md -o output.html --standalone --css=style.css

# → EPUB
pandoc input.md -o output.epub --epub-cover-image=cover.jpg

# → PPTX
pandoc input.md -o output.pptx

# 学术引用
pandoc input.md -o output.pdf --citeproc --bibliography=refs.bib --csl=apa.csl
```
