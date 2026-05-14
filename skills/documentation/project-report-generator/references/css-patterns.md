# 项目报告 CSS 模式库

> 可复用的 CSS 模式和布局技巧，每次创作报告时可直接参考或调整。

---

## 1. 暗色主题设计系统 (Dark Theme Tokens)

```css
:root {
  /* ── 背景 ── */
  --bg-page: #0d1117;
  --bg-card: #161b22;
  --bg-elevated: #1c2128;
  --border: #30363d;

  /* ── 文字 ── */
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-tertiary: #6e7681;

  /* ── 语义色 ── */
  --accent: #58a6ff;
  --success: #3fb950;
  --warning: #d29922;
  --danger: #f85149;
  --purple: #bc8cff;
  --cyan: #39d2c0;

  /* ── 间距 ── */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* ── 圆角 ── */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* ── 字体 ── */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
  --font-mono: 'SF Mono', 'Fira Code', monospace;
}
```

---

## 2. KPI 卡片网格 (Stats Grid)

```css
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.kpi-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  text-align: center;
}

.kpi-card .value {
  font-size: 2em;
  font-weight: 700;
  line-height: 1.2;
}

.kpi-card .label {
  color: var(--text-secondary);
  font-size: 0.85em;
  margin-top: var(--space-xs);
}

.kpi-card .sub {
  color: var(--text-tertiary);
  font-size: 0.75em;
}
```

---

## 3. 两列和三列布局 (Responsive Grids)

```css
/* 双列布局 */
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
}

/* 三列布局 */
.three-col {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--space-lg);
}

/* 响应式 */
@media (max-width: 768px) {
  .two-col, .three-col {
    grid-template-columns: 1fr;
  }
}
```

---

## 4. Sprint 时间线 (Timeline)

```css
.timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.timeline-item {
  display: grid;
  grid-template-columns: 100px 100px 1fr 120px;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  align-items: center;
  font-size: 0.85em;
}

.timeline-sprint { font-weight: 600; color: var(--accent); }
.timeline-date   { color: var(--text-secondary); }
.timeline-desc   { color: var(--text-primary); }
.timeline-stats  { color: var(--text-secondary); text-align: right; }

@media (max-width: 768px) {
  .timeline-item {
    grid-template-columns: 1fr;
    gap: 2px;
  }
}
```

---

## 5. 进度条 (Progress Bar)

```css
.progress-bar {
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--success);
  border-radius: 3px;
  transition: width 0.3s ease;
}
```

---

## 6. 带色条的表 (Status Table)

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85em;
}

.data-table th {
  color: var(--text-secondary);
  font-weight: 500;
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.data-table td {
  padding: 7px 10px;
  border-bottom: 1px solid var(--border);
}

/* 状态色 */
.status-ok     { color: var(--success); }
.status-warn   { color: var(--warning); }
.status-bad    { color: var(--danger); }
.status-accent { color: var(--accent); }
.status-dim    { color: var(--text-secondary); }

/* 行悬停 */
.data-table tr:hover td {
  background: rgba(88, 166, 255, 0.05);
}
```

---

## 7. Epic 卡片 (Status Cards)

```css
.epic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-md);
}

.epic-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}

.epic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.epic-id { font-weight: 700; color: var(--accent); }

.epic-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75em;
  font-weight: 600;
}

.epic-tag.approved { background: rgba(63,185,80,0.15); color: var(--success); }
.epic-tag.active   { background: rgba(88,166,255,0.15); color: var(--accent); }
.epic-tag.draft    { background: rgba(139,148,158,0.15); color: var(--text-secondary); }
```

---

## 8. 打印样式 (Print)

```css
@media print {
  @page {
    size: A4 landscape;
    margin: 1.5cm;
  }

  body {
    background: white;
    color: black;
  }

  section {
    break-inside: avoid;
    page-break-after: always;
    border: none;
    background: none;
    padding: 0;
  }

  .kpi-card {
    border: 1px solid #ddd;
    background: none;
  }

  .no-print {
    display: none !important;
  }
}
```

---

## 9. Chart.js 容器

```css
.chart-container {
  height: 280px;
  margin: var(--space-md) 0;
  position: relative;
}

/* 暗色主题 Chart.js 文字颜色 */
.chart-container canvas {
  /* Chart.js 颜色通过 options.scales.x.ticks.color 控制，CSS 只控制容器 */
}
```

---

## 10. 页脚 (Footer)

```css
.report-footer {
  text-align: center;
  color: var(--text-tertiary);
  font-size: 0.8em;
  padding: var(--space-lg);
  border-top: 1px solid var(--border);
  margin-top: var(--space-xl);
}
```

---

## 使用方式

创作报告时，直接从本节中选择需要的 CSS 模式，粘贴到 `<style>` 标签中，修改变量值即可。不需要全部复制，按需取用。
