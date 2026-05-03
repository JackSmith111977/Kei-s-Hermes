# Markdown 深度指南

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

- **标题**：只用 ATX 风格（`#`），不用底线风格
- **列表**：无序用 `-`，有序用 `1.`
- **嵌套**：2 或 4 空格缩进（保持一致）
- **链接**：超过 5 个链接时用引用式 `[text][id]` + `[id]: url`
- **代码**：行内用反引号，块用三个反引号 + 语言名
- **表格**：用 `:` 控制对齐（左/右/中）
- **空行**：标题、列表、代码块、表格前后必须有空行

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
行内公式：$E=mc^2$

块级公式：
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$

<!-- 脚注 -->
正文内容[^1]。

[^1]: 脚注内容

<!-- HTML 嵌入 -->
<div style="color: red;">红色文字</div>

<!-- 注释 -->
<!-- 这是注释 -->
```

## 目录（TOC）

```markdown
# GitHub
自动生成（基于标题）

# Pandoc
命令行：pandoc --toc input.md -o output.pdf

# iA Writer
{{TOC}}
```

## 学术引用

```markdown
正文 @author2024 说...

# references.bib
@article{author2024,
  title={标题},
  author={作者},
  journal={期刊},
  year={2024}
}
```

```bash
pandoc input.md -o output.docx --citeproc --bibliography=references.bib --csl=apa.csl
```

## 转换命令

```bash
# Markdown → PDF（需要 pandoc + xelatex）
pandoc input.md -o output.pdf --pdf-engine=xelatex -V mainfont="PingFang SC" --toc

# Markdown → Word
pandoc input.md -o output.docx

# Markdown → HTML
pandoc input.md -o output.html --standalone --css=style.css

# Markdown → LaTeX
pandoc input.md -o output.tex

# Markdown → EPUB
pandoc input.md -o output.epub --epub-cover-image=cover.jpg

# Markdown → PPTX
pandoc input.md -o output.pptx
```
