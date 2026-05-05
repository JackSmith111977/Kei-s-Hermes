---
name: pdf-pro-design
description: "PDF 专业排版设计与生成系统。涵盖场景自适应（技术/商务/学术）、顶级排版规范（CRAP 原则）、字体策略、高级 CSS (WeasyPrint/Chrome) 以及自动化视觉质检。目标是生成达到“网上优秀”标准的 PDF 文档。"
version: 2.0.0
triggers:
  - pdf pro
  - professional pdf
  - 高级排版
  - 排版设计
  - 优秀文档
  - design pdf
depends_on:
  - visual-aesthetics
  - web-access
design_pattern: Generator
skill_type: pipeline
---

# 🎨 PDF Pro Design System · 专业排版设计系统

> **核心理念**：不仅仅是生成 PDF，而是创造“视觉作品”。
> 严格遵循 CRAP 原则（对比、重复、对齐、亲密性），结合场景自适应技术，生成行业顶级水准的文档。

---

## 〇、场景判断与模板选择 (Scenario Detection)

在生成 PDF 前，必须先分析内容特征，选择最合适的模板：

| 场景特征 | 推荐模板 | 核心风格 |
|:---|:---|:---|
| **大量代码块、API 文档、技术栈** | **Tech Report (科技蓝)** | 极简、代码高亮、清晰的层级、深色侧边栏 |
| **市场分析、融资计划、大图** | **Business Plan (高级黑)** | 视觉冲击、全宽图片、大字报、60-30-10 配色 |
| **论文、参考文献、双栏需求** | **Academic Paper (学术棕)** | 严谨、Times New Roman 风格、脚注、紧凑行距 |

---

## 一、排版设计核心规范 (CRAP Principles)

### 1. 对比 (Contrast)
*   **标题**：`32pt Bold` + 品牌色（如 `#2C3E50`）。
*   **正文**：`10pt Regular` + 深灰（如 `#333333`）。
*   **辅助信息**：`8pt Italic` + 浅灰（如 `#7F8C8D`）。
*   **代码块**：深色背景 `#212529` + 亮色文字 + 语法高亮。

### 2. 重复 (Repetition)
*   **页眉页脚**：每页统一显示章节名、页码、品牌 Logo。
*   **配色方案**：全篇严格遵循一套 60-30-10 配色。
*   **元素样式**：所有 H2 标题左侧必须有 4px 宽的竖线强调。

### 3. 对齐 (Alignment)
*   **正文**：严格左对齐（除封面外，避免居中导致的阅读困难）。
*   **表格**：表头左对齐，数字列右对齐。
*   **代码块**：左对齐，带有行号时对齐行号。

### 4. 亲密性 (Proximity)
*   **间距规则**：
    *   标题与所属段落间距：< `10px`。
    *   段落与段落间距：`15px`。
    *   图片与说明文字间距：`5px`。

---

## 二、高级 CSS 技巧 (WeasyPrint)

### 1. 智能分页 (Smart Page Breaks)
*   **章节页**：`h1 { page-break-before: always; }`
*   **防切断**：`table, pre, img { page-break-inside: avoid; }`
*   ** widows/orphans 控制**：`p { widows: 2; orphans: 2; }` (防止段落首尾孤立行)

### 2. 动态页眉页脚 (Running Elements)
```css
@page {
    @top-center { content: string(chapter-title); font-size: 9pt; color: #999; }
    @bottom-center { content: "— " counter(page) " —"; font-size: 9pt; color: #999; }
}
h1 { string-set: chapter-title content(); }
```

### 3. 命名页面 (Named Pages)
用于封面、章节页等特殊页面，应用不同的边距或背景色。
```css
@page cover { margin: 0; background: #F5F7FA; }
.cover-page { page: cover; }

@page chapter { margin: 40mm; background: #2C3E50; color: white; }
.chapter-start { page: chapter; }
```

---

## 三、视觉质检流程 (Vision QC Pipeline)

**生成 PDF 不是结束，视觉确认才是！**

1.  **生成预览**：使用 WeasyPrint 的 `render()` 提取第一页生成 PNG。
2.  **视觉检查**：调用 Vision 工具，检查封面排版、文字重叠、字体回退。
3.  **判定**：
    *   **PASS**：生成最终 PDF 并发送。
    *   **FAIL**：根据错误反馈调整 CSS（如增加 padding、修改字体），重新生成。

---

## 四、字体策略 (Font Strategy)

*   **中文**：
    *   无衬线 (Sans)：`Noto Sans CJK SC`, `PingFang SC`, `Microsoft YaHei`。
    *   衬线 (Serif)：`Noto Serif CJK SC`, `Source Han Serif SC`, `SimSun`。
*   **英文**：
    *   无衬线：`Inter`, `Roboto`。
    *   衬线：`Merriweather`, `Lora`。
    *   代码：`Fira Code`, `Consolas`, `JetBrains Mono`。

> ⚠️ 必须使用 `@font-face` 指定 `file:///` 绝对路径，并配合 `FontConfiguration` 使用。

---

## 五、工具链决策 (Toolchain Decision)

| 需求 | 推荐工具 | 原因 |
|:---|:---|:---|
| **常规文档/报告** | **WeasyPrint** | HTML/CSS 最灵活，Python 原生，支持高级分页控制 |
| **复杂 Flexbox/Grid** | **Headless Chrome** | 渲染 100% 还原 Chrome 效果 |
| **像素级精确/发票** | **ReportLab** | 底层控制，适合证书、票据 |
| **学术/Markdown** | **Pandoc** | LaTeX 引擎，学术标准 |

---

**⚠️ Red Flags**：
- 不要使用 Flexbox 居中封面（WeasyPrint 兼容性差），使用 `padding-top`。
- 不要忽略 `page-break-inside: avoid`，这会导致表格被腰斩。
- 不要在没有视觉检查的情况下直接发送 PDF。
- 不要在 PDF 中使用系统默认字体（如 Arial），必须指定明确的字体栈。
