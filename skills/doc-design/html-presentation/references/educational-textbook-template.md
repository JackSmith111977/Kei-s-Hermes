# 教育类教材 HTML 幻灯片生成指南

> **来源**: 2026-05-17 创新思维方法教材制作实战
> **项目**: `/home/ubuntu/creative_thinking_textbook/`
> **产出**: 11 章 64 页完整教材，66KB 纯 HTML

---

## 适用场景

制作**多章节教育类网页教材**（非单次演讲），需要：
- 章节导航 + 章节内多页幻灯片
- 标准化的每章教学结构（定义→概念→方法→总结）
- 深色专注主题，适合学习者长时间浏览
- 零依赖，单 HTML 文件即可打开

---

## 核心方法：数据驱动生成

### 架构

```
Python 结构化数据 (chapters list)
     ↓
模板引擎 (f-string template)
     ↓
完整 HTML 文件
```

### 章节数据结构

每个章节包含 6 种幻灯片类型：

| 幻灯片类型 | 用途 | 内容字段 |
|:----------|:-----|:---------|
| `chapter-title` | 章节开篇 | `icon/title/subtitle/quote` |
| `definition` | 核心定义 | `title/body/key_points` |
| `concept` | 概念卡片 | `title/body/items[]`(卡片网格) |
| `process` | 方法步骤 | `title/body/steps[]`(步骤序列) |
| `summary` | 章节总结 | `title/points[]`(要点列表) + `practice`(实操练习) |

### 6 种幻灯片模板

详见 `generate_textbook.py` 中的 `generate_slide()` 函数，每种类型对应一个模板函数，从结构化数据自动生成 HTML。

---

## 设计系统

### 配色
```css
--bg-primary: #0f1117;     /* 主背景 */
--bg-secondary: #161822;   /* 侧边栏背景 */
--bg-card: #1c1f2e;        /* 卡片背景 */
--text-primary: #e8eaed;   /* 主文字 */
--text-secondary: #9aa0a6; /* 次要文字 */
--border-color: #2c2f3e;   /* 边框 */
```

### 布局
- **左侧导航栏** (260px): 固定定位，显示所有章节目录
- **右侧主内容**: scroll-snap 垂直分页
- 每章一个 id (如 `#ch1`)，导航栏通过 `href="#ch1"` 跳转

### 结构组件

| 组件 | CSS 类 | 说明 |
|:----|:-------|:-----|
| 导航栏 | `.nav-item` | 固定左侧，每章图标+编号+标题 |
| 封面 | `.cover-slide` | 渐变背景，11 个方法标签 |
| 章节标题 | `.chapter-title` | 渐变 `var(--ch-color)`，引文 |
| 定义页 | `.definition-slide` | 左栏蓝色竖线标题 + 关键点卡片 |
| 概念卡片 | `.concept-slide` | 响应式网格 `.cards > .card` |
| 方法步骤 | `.process-slide` | 弹性盒子 `.process-steps > .process-step` |
| 总结页 | `.summary-slide` | 要点列表 + 实操练习框 |
| 对比表 | `.comparison-table` | 全宽表格，hover 高亮 |
| 致谢页 | `.thankyou-slide` | 居中渐变文字 |

### 印刷适配
```css
@media print {
  .sidebar { display:none; }
  .main { margin-left:0; }
  .deck { overflow:visible; height:auto; }
  .slide {
    min-height:100vh;
    page-break-after:always;
    break-inside:avoid;
  }
  @page { size:A4 landscape; margin:1.2cm; }
}
```

---

## 生成流程

```bash
# 1. 编写 Python 生成器脚本
python3 generate_textbook.py

# 2. 输出 index.html（可双击打开）
# 3. 浏览器验证（browser_navigate + browser_vision）
```

---

## 实战教训：CSS 花括号转义

在 Python f-string 中嵌入 CSS 时，**所有 `{` 和 `}` 必须用 `{{` 和 `}}` 转义**。

**错误示例**（会导致 Python 解释器报错 `NameError`）：
```python
f'''
.definition-slide { align-items:flex-start; }  # ← {align...} 被当作 f-string 表达式
'''
```

**正确写法**：
```python
f'''
.definition-slide {{ align-items:flex-start; }}  # ← 双花括号
'''
```

**检测方法**：运行脚本时报 `NameError`，提示某个 CSS 属性名未定义（如 `align`）——说明花括号未转义。在包含大量 CSS 的长模板中，单行声明是最容易遗漏的地方。

---

## 设计决策

1. **纯 CSS scroll-snap > reveal.js**: 教材需要学生按自己节奏滚动浏览，而非逐页翻动。scroll-snap 同时支持两种模式。
2. **深色主题**: 减少长时间阅读的视觉疲劳，营造沉浸感。
3. **左侧固定导航**: 让学习者随时知道自己的位置，快速跳转到任意章节。
4. **每章标准化结构**: 降低认知负荷，学习者熟悉一种模式后就能快速理解所有章节。
5. **实操练习框**: 区别于总结，用 `practice-box` 独立呈现，鼓励学以致用。

---

## 可复用的起点

如果需要生成新的教材：
1. 复制 `generate_textbook.py` 中的 `chapters` 数据结构
2. 替换 `chapters` 中的字段
3. 调整设计系统（颜色/字体/间距）
4. 运行 `python3 generate_textbook.py`

完整参考：`/home/ubuntu/creative_thinking_textbook/generate_textbook.py`
