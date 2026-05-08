# Dracula 主题 reveal.js 演示模板

> 来源：2026-05-08 Gemini API 深度研究报告网页 PPT
> 适用场景：技术演讲、研究报告、能力全景展示

## 风格特征

| 特征 | 值 |
|------|-----|
| **主题** | reveal.js Dracula (暗色) |
| **配色** | 背景 #282a36 · 青 #8be9fd · 紫 #bd93f9 · 粉 #ff79c6 · 绿 #50fa7b · 黄 #f1fa8c |
| **布局** | 毛玻璃卡片 (Glassmorphism) + Mesh Gradient 渐变背景 |
| **字体** | PingFang SC / Microsoft YaHei (中文优先) |
| **特殊效果** | 渐变色标题文字、进度条、引用框、标签徽章 |
| **翻页** | 方向键 / 触屏滑动 · ESC 总览 · S 演讲者模式 |

## 核心 CSS 片段

```css
/* 毛玻璃卡片 */
.card {
  background: rgba(40, 42, 54, 0.7);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(8px);
}

/* Mesh Gradient 渐变背景（用于封面/结尾页） */
.slide-mesh {
  background:
    radial-gradient(ellipse 800px 500px at 20% 30%, rgba(98, 114, 164, 0.4), transparent),
    radial-gradient(ellipse 600px 400px at 80% 70%, rgba(255, 121, 198, 0.2), transparent),
    #282a36 !important;
}

/* 标签徽章 */
.tag-green { background: rgba(80, 250, 123, 0.2); color: #50fa7b; }
.tag-purple { background: rgba(189, 147, 249, 0.2); color: #bd93f9; }
.tag-pink { background: rgba(255, 121, 198, 0.2); color: #ff79c6; }
.tag-yellow { background: rgba(241, 250, 140, 0.2); color: #f1fa8c; }
.tag-blue { background: rgba(139, 233, 253, 0.2); color: #8be9fd; }
.tag-orange { background: rgba(255, 184, 108, 0.2); color: #ffb86c; }

/* 渐变标题文字 */
h1.gradient-title {
  background: linear-gradient(135deg, #8be9fd, #bd93f9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 卡片网格布局 */
.card-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
.card-grid-2 { grid-template-columns: 1fr 1fr; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
```

## reveal.js 初始化 (Dracula 主题)

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/dracula.css">

<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/markdown/markdown.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/highlight/highlight.js"></script>
<script>
  Reveal.initialize({
    plugins: [RevealMarkdown, RevealHighlight],
    transition: 'slide',
    hash: true,
    slideNumber: 'c/t',
    pdfSeparateFragments: false,
  });
</script>
```

## 使用方式

1. 复制 `gemini_api_presentation.html`（位于 `~/.hermes/learning/`）作为起点
2. 替换每个 `<section>` 中的内容
3. 在浏览器中直接打开 HTML 文件即可查看
4. 如需 PDF 导出：浏览器打开 → 打印 → 另存为 PDF（或 URL 加 `?print-pdf`）

## 注意事项

- 中文必须指定中文字体（`.reveal { font-family: "PingFang SC", "Microsoft YaHei", ... }`）
- CDN 引用 reveal.js v5，注意插件版本一致性
- 毛玻璃效果需 `backdrop-filter` 支持（现代浏览器均支持）
- Mesh Gradient 用 `radial-gradient` 叠加实现，零依赖
