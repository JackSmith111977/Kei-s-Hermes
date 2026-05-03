---
name: latex-guide
description: LaTeX 学术论文排版原子技能。学位论文、期刊文章、技术报告。
triggers:
- latex guide
- latex-guide
metadata:
  hermes:
    tags:
    - latex
    - academic
    - paper
    - thesis
    category: productivity
    skill_type: doc-generation
    format: latex
---
# LaTeX 原子操作技能

> 默认使用中文，除非用户特意说明。

## 基础文档结构

```latex
\documentclass[12pt,a4paper]{article}
\usepackage[UTF8]{ctex}          % 中文支持
\usepackage{geometry}            % 页面设置
\usepackage{graphicx}            % 图片
\usepackage{hyperref}            % 超链接
\usepackage{listings}            % 代码
\usepackage{booktabs}            % 专业表格
\usepackage{amsmath}             % 数学

\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}

\title{文档标题}
\author{作者}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage

\section{第一节}
正文内容。

\subsection{小节}
\begin{itemize}
    \item 列表项一
    \item 列表项二
\end{itemize}

\begin{table}[h]
\centering
\caption{表格标题}
\begin{tabular}{lcc}
\toprule
列1 & 列2 & 列3 \\
\midrule
A & B & C \\
\bottomrule
\end{tabular}
\end{table}

\begin{lstlisting}[language=Python]
print("Hello World")
\end{lstlisting}

\end{document}
```

## 编译命令

```bash
# 中文文档（推荐 xelatex）
xelatex document.tex
latexmk -xelatex document.tex  # 自动编译

# 查看系统中文字体
fc-list :lang=zh
```

## 常用宏包速查

| 用途 | 宏包 |
|------|------|
| 中文 | `ctex` |
| 表格 | `booktabs`, `longtable` |
| 代码 | `listings`, `minted` |
| 数学 | `amsmath`, `amssymb` |
| 算法 | `algorithm2e` |
| 参考文献 | `biblatex`, `natbib` |
