---
name: html-presentation
description: 用 HTML/CSS 制作演示文稿的完整指南 — 替代传统 PPTX 的新思路。涵盖 reveal.js、Slidev、Marp、纯 CSS 四大方案，从选型到实操的全流程指导。v2.0 新增 7 种网页 UX/UI 设计风格实现（Glassmorphism/Neumorphism/Neubrutalism/Material You/日式侘寂/Mesh Gradient/赛博霓虹），可直接用于幻灯片设计。
version: 2.0.0
triggers:
  - HTML 做 PPT
  - 网页幻灯片
  - html presentation
  - reveal.js
  - Slidev
  - Marp
  - 演示文稿
  - 网页做 PPT
  - slides
  - slide deck
  - HTML slide
  - 前端演示
  - UI 设计风格
  - Glassmorphism
  - Neumorphism
  - Neubrutalism
  - Material You
  - 毛玻璃效果
  - 网页设计风格
  - 侘寂
  - Wabi-Sabi
  - Mesh Gradient
  - 赛博朋克设计
  - 霓虹风格
metadata:
  hermes:
    tags:
    - html
    - css
    - presentation
    - slides
    - revealjs
    - slidev
    - marp
    category: doc-design
    skill_type: reference
    design_pattern: tool-wrapper
depends_on:
  - html-guide
  - weasyprint
---

# HTML Presentation — 用网页技术做演示文稿

> **核心思想**：演示文稿本质上是网页。用 HTML+CSS 替代 PPTX，获得版本控制、跨平台、无限自定义和原生交互能力。
>
> **适用场景**：技术演讲、代码演示、开源项目介绍、在线课程、自动化批量生成幻灯片

---

## 一、快速选型指南

| 场景 | 推荐方案 | 一句话理由 |
|------|---------|-----------|
| 🎤 技术演讲/代码演示 | **Slidev** | Shiki 代码高亮 + live coding + 热重载 |
| 🎨 需要最大自定义 | **reveal.js** | 69k stars 插件生态，HTML 完全控制 |
| 📄 快速输出多种格式 | **Marp** | 一行命令出 HTML/PDF/PPTX 三种格式 |
| 🪶 极简零依赖 | **纯 CSS + WeasyPrint** | 一个 HTML 文件搞定 |
| 🤖 批量自动化生成 | **Marp CLI** | 脚本化管道，最简 API |

---

## 二、四大方案详解

### 方案 A：reveal.js — 最成熟的 HTML 演示框架

**GitHub**：69k+ stars | **编写方式**：HTML/Markdown | **输出**：HTML、PDF

**CDN 快速开始（一个 HTML 文件搞定）**：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>reveal.js 演示</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css">
  <style>
    /* 中文支持 */
    .reveal { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; }
    .reveal h1, .reveal h2, .reveal h3 { font-family: inherit; }
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>
        <h1>标题</h1>
        <p>副标题</p>
      </section>
      <section>
        <h2>第二页</h2>
        <ul>
          <li class="fragment">逐步出现 1</li>
          <li class="fragment">逐步出现 2</li>
        </ul>
      </section>
      <!-- 嵌套垂直幻灯片 -->
      <section>
        <section>垂直 1</section>
        <section>垂直 2</section>
      </section>
      <!-- Markdown 写法 -->
      <section data-markdown>
        <textarea data-template>
          ## Markdown 标题
          - 要点一
          - 要点二
          ```python
          print("Hello reveal.js!")
          ```
        </textarea>
      </section>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/markdown/markdown.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/highlight/highlight.js"></script>
  <script>
    Reveal.initialize({
      plugins: [RevealMarkdown, RevealHighlight],
      transition: 'slide',
      hash: true,
    });
  </script>
</body>
</html>
```

**常用配置**：
```javascript
Reveal.initialize({
  controls: true,           // 显示控制箭头
  progress: true,           // 显示进度条
  hash: true,               // URL 哈希导航
  transition: 'slide',      // slide/convex/concave/zoom/fade
  autoSlide: 0,             // 自动翻页间隔（ms），0=关闭
  loop: false,              // 是否循环播放
  backgroundTransition: 'zoom',
  plugins: [RevealMarkdown, RevealHighlight, RevealNotes, RevealMath]
});
```

**快捷键**：
| 按键 | 功能 |
|------|------|
| `ESC` | 幻灯片总览 |
| `S` | 演讲者模式（笔记+计时+预览） |
| `B` / `.` | 暂停/黑屏 |
| `F` | 全屏 |
| `Space` | 下一张（含垂直子页） |
| `Alt+点击` | 放大元素 |

**PDF 导出**：浏览器 → 打印 → 另存为 PDF（或在 URL 加 `?print-pdf`）

---

### 方案 B：Slidev — 最快的 Markdown 开发体验

**GitHub**：38.5k+ stars | **编写方式**：Markdown | **输出**：HTML、PDF、PPTX、PNG

**技术栈**：Vue 3 + Vite + UnoCSS + Shiki + Monaco + KaTeX + Mermaid + RecordRTC

**安装并启动**：
```bash
# 方式一：项目模式（推荐）
npm init slidev@latest
cd my-slides
npm run dev     # → http://localhost:3030

# 方式二：单文件模式
npm i -g @slidev/cli
slidev slides.md
```

**slides.md 模板**：
```markdown
---
layout: cover
background: #f5f5f5
---

# 演示标题
### 副标题 / 作者 / 日期

---
# 第二页

- 要点一
- 要点二
- 要点三

---
# 代码演示

```python {2|3-4|all}
def hello():
    name = "Slidev"
    print(f"Hello, {name}!")
    return name
```

---
# 图表 + 数学

<v-clicks>

- Mermaid 图表：  ```mermaid
  graph LR
    A[开始] --> B[处理]
    B --> C[结束]
  ```

- KaTeX 公式： $\sqrt{3x-1}+(1+x)^2$

</v-clicks>

---
layout: center
---

# 谢谢！
```

**常用命令**：
```bash
slidev               # 启动开发服务器（热重载）
slidev build         # 构建静态站点
slidev export        # 导出 PDF/PPTX/PNG
slidev format        # 格式化 slides.md
```

---

### 方案 C：Marp — 最简 Markdown 多格式输出

**GitHub**：9k+ stars | **编写方式**：Markdown | **输出**：HTML、PDF、PPTX、图片

**安装**：`npm i -g @marp-team/marp-cli` 或直接 `npx`

**slides.md 模板**：
```markdown
---
marp: true
theme: uncover
class:
  - lead
  - invert
paginate: true
---

# 标题

副标题

---

## 内容页

- 按 `---` 分隔幻灯片
- 简洁优雅的 Markdown 语法
- 多格式输出一致渲染

---

## 代码展示

```python
print("Hello Marp!")
```

![bg right:40%](https://picsum.photos/400?random)
```

**一行命令转换**：
```bash
# HTML
npx @marp-team/marp-cli@latest slides.md

# PDF（需要 Chrome）
npx @marp-team/marp-cli@latest slides.md --pdf

# PPTX
npx @marp-team/marp-cli@latest slides.md --pptx

# 图片
npx @marp-team/marp-cli@latest slides.md --image png
```

**VS Code 扩展**：搜索「Marp for VS Code」，安装后实时预览 + 右键导出

---

### 方案 D：纯手工 HTML+CSS（零依赖）

**核心技巧**：用 `:target` 伪类或 `scroll-snap` 实现幻灯片切换

**scroll-snap 方案（推荐，可滚动浏览）**：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>纯 CSS 幻灯片</title>
<style>
  /* === 幻灯片布局 === */
  .deck {
    scroll-snap-type: y mandatory;
    overflow-y: scroll;
    height: 100vh;
    scroll-behavior: smooth;
  }
  .slide {
    height: 100vh;
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    box-sizing: border-box;
  }
  /* 配色 */
  .slide:nth-child(odd) { background: #f8f9fa; }
  .slide:nth-child(even) { background: #e9ecef; }

  /* === 打印样式 === */
  @media print {
    @page { size: A4 landscape; margin: 1.5cm; }
    .deck { overflow: visible; height: auto; }
    .slide {
      height: auto; min-height: 100vh;
      page-break-after: always;
      break-inside: avoid;
    }
  }
</style>
</head>
<body>
<div class="deck">
  <section class="slide">
    <h1 style="font-size:3rem; color:#2B579A;">标题</h1>
    <p style="font-size:1.5rem; color:#666;">副标题 / 作者</p>
  </section>
  <section class="slide">
    <h2>内容页</h2>
    <ul style="font-size:1.5rem; line-height:2.5;">
      <li>纯 CSS 零依赖</li>
      <li>滚动浏览或打印成 PDF</li>
      <li>完全自由自定义</li>
    </ul>
  </section>
  <section class="slide">
    <h2>第三页</h2>
    <p>用 WeasyPrint 输出 PDF</p>
  </section>
</div>
</body>
</html>
```

**:target 堆叠方案（翻页动画版）**：参考 [Pure CSS Slides](https://ondras.github.io/pure-css-slides/)

**WeasyPrint 输出 PDF**：
```bash
weasyprint slides.html output.pdf
```

---

## 三、方案对比矩阵

| 维度 | reveal.js | Slidev | Marp | 纯 CSS |
|------|-----------|--------|------|--------|
| 编写方式 | HTML/Markdown | Markdown | Markdown | HTML |
| 学习成本 | 中 | 低 | 最低 | 中偏高 |
| 自定义度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 热重载 | 需额外配置 | ✅ 原生支持 | ❌ | ❌ |
| 代码高亮 | highlight.js | Shiki ⭐ | highlight.js | 需自己加 |
| 交互组件 | 插件系统 | Vue 组件 | 有限 | 需自己写 |
| 输出格式 | HTML/PDF | HTML/PDF/PPTX/PNG | HTML/PDF/PPTX/Img | HTML/PDF |
| 文件大小 | 最小（单 HTML） | 中等（静态站点） | 最小 | 最小 |
| 包大小 (npm) | ~2.5MB | ~15MB | ~8MB | 0 |
| 社区 | 69k stars, 成熟 | 38.5k stars, 增长快 | 9k stars | N/A |

---

## 四、推荐的完整工作流

### 场景：技术演讲（推荐 Slidev）
```
Markdown 编写 → 热重载预览 → Mermaid 绘图
→ Shiki 代码高亮 → slidev export PDF/PPTX
→ 部署到 GitHub Pages
```

### 场景：快速多格式输出（推荐 Marp）
```
Markdown 编写 → marp --pdf → PDF 发听众
                       → --pptx → PPTX 给编辑
                       → HTML   → 在线分享
```

### 场景：完全控制（推荐 reveal.js）
```
HTML 编写 → CDN 启动 → 插件增强
→ 浏览器打印 PDF → 单 HTML 文件发布
```

---

## 五、避坑指南

1. **中文显示**：reveal.js 和 Marp 默认字体不含中文，必须指定中文字体
   ```css
   .reveal { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; }
   ```
2. **PDF 导出需要 Chrome**：Marp、reveal.js、Slidev 的 PDF 导出都依赖 Chromium
3. **Marp 图片路径**：CLI 工作目录影响相对路径，建议用绝对路径或 `--input-dir`
4. **Slidev 版本要求**：Node.js >= 20.12.0
5. **reveal.js v4 vs v5**：插件 API 有变化，CDN 引用时注意版本一致性
6. **纯 CSS 打印**：使用 `@media print` + `page-break-after: always` 控制分页

### 可复用模板

本 skill 的 `references/` 目录下提供了实战验证过的演示模板：

| 文件 | 风格 | 来源 |
|------|------|------|
| `references/dracula-revealjs-template.md` | Dracula 主题 + 毛玻璃卡片 + Mesh Gradient | 2026-05-08 Gemini API 研究报告 |

## 六、🎨 7 种网页 UX/UI 设计风格 — 直接用于 PPT

> 每种风格就是一组 CSS 变量 + 特定规则。切换到 reveal.js/Marp/纯 CSS PPT 中只需加一个 class。

### 1. Glassmorphism（玻璃拟态）✨ 最「高级感」
```css
.glass-slide {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
/* 配合渐变背景（推荐 Mesh Gradient） */
.mesh-bg {
  background:
    radial-gradient(at 20% 30%, #667eea, transparent 50%),
    radial-gradient(at 80% 70%, #764ba2, transparent 50%);
}
```
> **最佳场景**：产品介绍、SaaS 风格、技术演示封面
> **⚠️ 必须搭配丰富背景**，纯白背景看不出效果

### 2. Neumorphism（新拟态）🫧 最「温柔」
```css
.neumorph-slide {
  background: #e0e5ec;
  border-radius: 32px;
  box-shadow: 12px 12px 24px rgba(0,0,0,0.1),
              -12px -12px 24px rgba(255,255,255,0.9);
}
```
> **最佳场景**：健康/生活类主题、音乐分享
> **⚠️ 可访问性差**，文字需额外加深

### 3. Neubrutalism（粗野主义）💥 最「有个性」
```css
.brutal-slide {
  border: 4px solid #000;
  box-shadow: 8px 8px 0 #000;
  border-radius: 0;
  background: #FFE500;
}
h1 { font-size: 4rem; text-transform: uppercase; }
```
> **最佳场景**：创意作品集、个人品牌、前端分享
> **特点**：天然高可访问性（强对比）

### 4. Material You 🌈 最「完整」
直接引入开源 CSS 库：
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/hiratazx/material-you-css@latest/material-you.css">
```
使用 `md-card` / `md-btn` / `md-typography` 等 20+ 组件。
> **最佳场景**：标准公司汇报、教学课件
> **自动暗色模式**，零依赖

### 5. 日式侘寂 Wabi-Sabi 🍃 最「有灵魂」
```css
.wabi-slide {
  background: #f5f0e8;
  font-family: 'Georgia', 'Noto Serif SC', serif;
  padding: 4rem;
  line-height: 2;
  color: #3d3d3d;
  /* 不对称 corner — 模拟自然 */
  border-radius: 40% 20% 60% 20%;
}
```
> **最佳场景**：人文主题、内容写作、哲学分享
> **四大哲学**：Ma(留白) + Fukinsei(不对称) + Kanso(简洁) + Shibui(朴素)

### 6. Mesh Gradient（渐变流体）🌊 最「高级背景」
```css
.mesh-slide {
  background:
    radial-gradient(ellipse 600px 400px at 20% 30%, hsla(260, 80%, 65%, 0.7), transparent),
    radial-gradient(ellipse 500px 400px at 80% 70%, hsla(190, 80%, 60%, 0.6), transparent),
    #0f0c29;
}
/* 动画版（缓慢漂移） */
.mesh-animated { background-size: 200% 200%; animation: mesh-drift 12s ease-in-out infinite alternate; }
@keyframes mesh-drift { 0% { background-position: 0% 0%; } 100% { background-position: 100% 100%; } }
```
> **最佳场景**：PPT 封面/过渡页、品牌展示
> **性能**：纯 CSS GPU 渲染，零依赖

### 7. Cyber/Neon（赛博霓虹）⚡ 最「炫酷」
```css
.cyber-slide {
  background: #0a0a0f;
  color: #fff;
  border: 2px solid #0ff;
  box-shadow:
    inset 0 0 0.6em rgba(0, 255, 255, 0.4),
    0 0 0.6em rgba(0, 255, 255, 0.4),
    0 0 2em rgba(0, 255, 255, 0.2);
}
.cyber-pulse { animation: glow-pulse 2s ease-in-out infinite alternate; }
@keyframes glow-pulse {
  from { box-shadow: ...; }  /* 暗态 */
  to   { box-shadow: ...; }  /* 亮态 */
}
```
> **最佳场景**：游戏开发、音乐主题、极客分享
> **必须暗色背景**，浅色模式下失效

---

## 七、风格选型速查

| 风格 | 氛围 | CSS 量 | 可访问性 | 最佳 PPT 场景 |
|:----:|:----:|:------:|:--------:|--------------|
| Glassmorphism | 高级/未来感 | 5 行 | ⚠️ 中 | 封面、SaaS |
| Neumorphism | 温柔/触感 | 3 行 | ❌ 低 | 特定组件 |
| Neubrutalism | 大胆/个性 | 4 行 | ✅ 高 | 作品集、创意 |
| Material You | 专业/统一 | 1 行引用 | ✅ 高 | 公司汇报、教学 |
| Wabi-Sabi | 禅意/自然 | 6 行 | ✅ 中 | 人文、写作 |
| Mesh Gradient | 流动/A级 | 5 行 | ✅ 作为背景 | 封面、过渡页 |
| Cyber/Neon | 炫酷/赛博 | 6 行 | ⚠️ 中 | 游戏、音乐 |

### reveal.js 中切换风格示例
```html
<section class="glass-slide" data-background="mesh-bg">
  <h1>Glassmorphism 风格</h1>
</section>
<section class="brutal-slide">
  <h1>Neubrutalism 风格</h1>
</section>
<section class="wabi-slide">
  <h1>日式侘寂风格</h1>
</section>
```
每个 `<section>` 用不同的 class 展现不同设计风格，一个 PPT 展示全部 7 种风格！

