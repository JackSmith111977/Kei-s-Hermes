# LaTeX 完整指南

## 基础文档结构

```latex
\documentclass[12pt,a4paper]{article}

% === 宏包 ===
\usepackage[UTF8]{ctex}          % 中文支持
\usepackage{geometry}            % 页面设置
\usepackage{graphicx}            % 图片
\usepackage{hyperref}            % 超链接
\usepackage{xcolor}              % 颜色
\usepackage{listings}            % 代码
\usepackage{booktabs}            % 专业表格
\usepackage{amsmath}             % 数学
\usepackage{fancyhdr}            % 页眉页脚

\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}

% === 代码样式 ===
\lstset{
    backgroundcolor=\color{gray!10},
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    numbers=left,
    numberstyle=\tiny\color{gray},
}

\title{文档标题}
\author{作者}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage

\section{第一节}
正文内容，中英文混排 English text。

\subsection{小节}
\begin{itemize}
    \item 列表项一
    \item 列表项二
\end{itemize}

\begin{enumerate}
    \item 有序列表
    \item 第二项
\end{enumerate}

\begin{table}[h]
\centering
\caption{表格标题}
\begin{tabular}{lcc}
\toprule
列1 & 列2 & 列3 \\
\midrule
A & B & C \\
D & E & F \\
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{image.png}
\caption{图片标题}
\end{figure}

\begin{lstlisting}[language=Python]
print("Hello World")
\end{lstlisting}

\bibliographystyle{plain}
\bibliography{references}

\end{document}
```

## 编译命令

```bash
# 中文文档（推荐 xelatex）
xelatex document.tex
bibtex document      # 如果有参考文献
xelatex document.tex # 编译两次以生成目录和引用
xelatex document.tex

# 或使用 latexmk 自动编译
latexmk -xelatex document.tex

# 中文支持检查
fc-list :lang=zh    # 查看系统中文字体
```

## 学位论文模板结构

```
thesis/
├── main.tex              # 根文件
├── preamble.tex          # 宏包和设置
├── chapters/
│   ├── 01-intro.tex
│   ├── 02-related.tex
│   ├── 03-method.tex
│   ├── 04-results.tex
│   └── 05-conclusion.tex
├── front-matter/
│   ├── abstract.tex
│   ├── acknowledgments.tex
│   └── title-page.tex
├── back-matter/
│   ├── appendices.tex
│   └── glossary.tex
├── figures/
└── references.bib
```

## 常用宏包速查

| 用途 | 宏包 |
|------|------|
| 中文 | `ctex` |
| 页面 | `geometry` |
| 图片 | `graphicx` |
| 表格 | `booktabs`, `longtable`, `multirow` |
| 代码 | `listings`, `minted` |
| 数学 | `amsmath`, `amssymb` |
| 算法 | `algorithm2e`, `algorithmicx` |
| 参考文献 | `biblatex`, `natbib` |
| 颜色 | `xcolor` |
| 超链接 | `hyperref` |
| 页眉页脚 | `fancyhdr` |
| 目录 | `titletoc` |
| 列表 | `enumitem` |
