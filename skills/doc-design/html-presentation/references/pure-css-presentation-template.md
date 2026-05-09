# 纯 CSS scroll-snap 演示模板（生产级）

## 概述

零依赖、完全可控的 HTML 演示文稿模板。基于 CSS `scroll-snap` + 极简 JavaScript（仅导航）
实现。2026-05-09 AI 编程进化史报告实战验证。

## 设计系统（CSS Custom Properties）

```css
:root {
  /* 背景与文字 */
  --bg-primary: #08080f;
  --text-primary: #e8e8f0;
  --text-secondary: #8888a0;
  --text-muted: #555;
  /* 强调色 */
  --accent-cyan: #00d4ff;
  --accent-pink: #ff5ea0;
  --accent-green: #00e676;
  --accent-red: #ff3d3d;
  /* 卡片 */
  --card-bg: rgba(255,255,255,0.03);
  --card-border: rgba(255,255,255,0.06);
  --radius-card: 16px;
  --radius-inner: 8px;
  /* 间距 (4px 网格) */
  --spacing-xs: 4px; --spacing-sm: 8px; --spacing-md: 16px;
  --spacing-lg: 24px; --spacing-xl: 32px; --spacing-2xl: 48px;
  /* 字号 */
  --font-body: 15px; --font-small: 13px; --font-micro: 12px;
  --font-h1: clamp(32px,4vw,56px); --font-h2: clamp(24px,2.8vw,40px);
  --max-content: 1000px;
}
```

**关键原则**：
- 使用 clamp() 实现响应式字号（无需媒体查询）
- 4px 网格确保所有间距成比例
- 用 CSS 变量做「设计 tokens」而非硬编码值

## 导航机制

### 浮动导航栏

```html
<nav class="slide-nav" aria-label="幻灯片导航">
  <button id="prevBtn">‹</button>
  <span class="counter">
    <span class="cur" id="curSlide">1</span>&ensp;/&ensp;<span id="totalSlides"></span>
  </span>
  <div class="dots" id="dots"></div>
  <button id="nextBtn">›</button>
</nav>
```

核心 CSS：`position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%);`
配合 `backdrop-filter: blur(12px)` 创造毛玻璃效果。

### IntersectionObserver 驱动状态

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const idx = parseInt(entry.target.dataset.index);
      curSpan.textContent = idx + 1;
      dots.forEach((dot, di) => dot.classList.toggle('active', di === idx));
      slides.forEach(s => s.classList.remove('active'));
      entry.target.classList.add('active'); // 触发 fade-up 动画
    }
  });
}, { threshold: 0.5 });
```

### 渐进动画系统

```css
.fade-up { opacity: 0; transform: translateY(24px); transition: opacity 0.6s ease, transform 0.6s ease; }
.slide.active .fade-up { opacity: 1; transform: translateY(0); }
.slide.active .d1 { transition-delay: 0.1s; }
.slide.active .d2 { transition-delay: 0.2s; }
```

## 布局组件

### 卡片系统

```html
<div class="card card-cyan" style="padding:18px 20px;">
  <h4>标题</h4>
  <p class="small">内容</p>
</div>
```

### 数据指标行

```html
<div class="metric-row">
  <div class="metric">
    <div class="num cyan">52.8% → 66.5%</div>
    <div class="lbl">LangChain Harness 提升</div>
  </div>
</div>
```

### Grid 系统

```css
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
```

## 已避免的常见错误

1. **不要跳框架** — 纯 CSS 是 reveal.js 之后更好的选择（当视觉质量是优先时）
2. **先定义 tokens** — 不要在 CSS 中硬编码颜色/间距值
3. **留白 60-80px** — 每页 padding 最小值，给人呼吸感
4. **页数控制在 15-20 页** — 每页承载 3-4 个信息块，不要挤满
5. **每页只有 1 个视觉重心** — 标题不是重心，内容才是
6. **先加载设计 skill** — `visual-aesthetics` + `web-ui-ux-design` 必须在写代码前加载

## 完整示例项目

见 `~/.hermes/research/ai_coding_evolution_v2.html`（18 页，AI 编程进化史报告）。
