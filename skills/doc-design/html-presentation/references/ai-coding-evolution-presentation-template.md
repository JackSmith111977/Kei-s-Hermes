# AI 编程进化史演示文稿（reveal.js 实战模板）

## 概述

一份完整的 reveal.js 中文演示文稿，主题为「AI 编程进化史：从 Prompt Engineering 到 Context Engineering 再到 Harness Engineering」。

## 文件位置

```
~/.hermes/research/ai_coding_evolution_presentation.html
```

## 技术特点

| 特性 | 实现方式 |
|------|---------|
| **框架** | reveal.js v5 (CDN) |
| **主题** | Dracula 暗色主题 + 自定义 Cyber 风格 |
| **字体** | Noto Sans SC + JetBrains Mono |
| **动画** | CSS fragment 渐进 + 悬停效果 |
| **布局** | Grid 卡片 + 双栏 + 层次图 |
| **背景** | CSS radial-gradient 渐变 |
| **配色** | Dracula 调色板 (cyan/pink/green/red/orange) |

## 核心设计模式

### 1. 三级卡片 Grid
```html
<div class="phase-grid">
  <div class="phase-card fragment">...</div>
  ...
</div>
```
适用于：演进时间线、功能对比、分类展示

### 2. 数据指标行
```css
.metric-row { display: flex; gap: 30px; }
.metric-item .num { font-size: 2.5em; color: #ff79c6; }
```
适用于：统计数据展示、关键数字强调

### 3. 引语块
```css
.quote { border-left: 4px solid #ff79c6; 
         background: rgba(255, 121, 198, 0.08); }
```
适用于：名人名言的引用展示

### 4. 公式展示盒
```css
.formula-box { background: linear-gradient(...); 
               border: 2px solid #8be9fd; border-radius: 20px; }
```

### 5. 嵌套垂直幻灯片
reveal.js 支持 `<section>` 嵌套实现垂直分页，适合「总览→详情」模式。

### 6. 颜色标签系统
```css
.tag-blue  { background: rgba(139,233,253,0.15); color: #8be9fd; }
.tag-pink  { background: rgba(255,121,198,0.15); color: #ff79c6; }
.tag-green { background: rgba(80,250,123,0.15);  color: #50fa7b; }
```

## 幻灯片结构（21页）

```
封面 → 目录 → 
[1] 范式演进总览 (时间线 + 层次关系) →
[2] Prompt Engineering (经典技术) →
[3] Context Engineering (三层架构) →
[4] Harness Engineering →
[5] Agent 四大失败模式 (数据) →
[6] Harness 四大护栏 (Guides+Sensors) →
[7] Agent=Model+Harness (OS比喻+Software 3.0) →
[8] 关键论文与实战案例 →
[9] 总结展望
```

## 使用方式

直接在浏览器打开该 HTML 文件，使用方向键或空格翻页。

### 快捷键
- `←`/`→` 或 `Space`：水平翻页
- `↑`/`↓`：垂直翻页（同一水平页的子页）
- `ESC`：总览模式
- `F`：全屏
- `S`：演讲者模式

### 导出 PDF
在 URL 后加 `?print-pdf`，然后用浏览器打印（Ctrl+P）→ 另存为 PDF。

## 最佳实践总结

1. **行内 CSS 优于外部 CSS**：确保单 HTML 文件自包含，方便分发
2. **中文指定字体**：reveal.js 默认不含中文字体，必须用 CSS 显式指定
3. **fragment 控制信息密度**：每个 <div class="fragment"> 控制信息出现的时机
4. **data-background 属性**：可单独为每页设置背景色/渐变图
5. **section 嵌套实现二级导航**：适合「概览→细节」的内容结构
