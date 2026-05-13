---
name: latex-guide
description: LaTeX 排版快速入口 — 核心命令速查，完整排版请用 pdf-layout skill
version: 1.0.0
type: redirect
redirect_to: pdf-layout
triggers:
- latex guide
- latex-guide
- .tex 文件
- xelatex 编译
metadata:
  hermes:
    tags:
    - latex
    - academic
    - quick-ref
    - redirect
    category: productivity
    skill_type: experience-quickref
---

# LaTeX 快速入口

> 💡 **完整 PDF 排版请用 `pdf-layout` skill**（支持 ReportLab + WeasyPrint 双引擎）。
> 本 skill 仅保留 LaTeX 最核心的速查信息。

## 快速模板

```latex
\documentclass[12pt,a4paper]{article}
\usepackage[UTF8]{ctex}          % 中文支持
\usepackage{geometry}
\usepackage{graphicx, hyperref, booktabs, amsmath}

\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}
\title{标题}\author{作者}\date{\today}

\begin{document}
\maketitle
\tableofcontents
\section{第一节}
正文内容。
\end{document}
```

## 编译命令

```bash
xelatex document.tex                          # 中文文档
latexmk -xelatex document.tex                 # 自动编译
fc-list :lang=zh                              # 查看中文字体
```

## 常用宏包

| 用途 | 宏包 |
|------|------|
| 中文 | `ctex` |
| 表格 | `booktabs`, `longtable` |
| 代码 | `listings`, `minted` |
| 数学 | `amsmath`, `amssymb` |
| 参考文献 | `biblatex`, `natbib` |
