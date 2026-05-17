---
name: visual-aesthetics
description: boku 的视觉审美指南——判断美与丑的核心标准。涵盖信息层级、认知负荷、色彩语义、Dieter Rams 十原则。帮助 boku 在生成图片、排版文...
version: 1.0.0
triggers:
- 评价这个好看吗
- 审美分析
- 美丑判断
- 设计原则
- 视觉分析
- 设计太乱了
- Dieter Rams
allowed-tools:
- vision_analyze
- terminal
- mcp_tavily_tavily_search
metadata:
  hermes:
    tags:
    - aesthetics
    - design
    - beauty
    - visual-judgment
    - criteria
    related_skills: ["web-ui-ux-design"]
    category: creative
    skill_type: library-reference
    design_pattern: tool-wrapper
depends_on: []

---
# boku 的视觉审美指南 🔍✨

## 核心定义

**美不仅仅是装饰，美是清晰的秩序。**
> "Good design is as little design as possible." —— Dieter Rams

## 一、美与丑的判断标准（实战维度）

通过多模态视觉分析实战，boku 总结出判断设计美丑的 5 个核心维度：

### 1. 信息层级 (Hierarchy) 👁️
- **美**：有明确的视觉重心，视线流动自然（先看标题，再看重点，最后看细节）。
- **丑**：信息堆砌，没有主次，所有元素都在"抢眼球"（如：乱七八糟的 LA 停车牌）。

### 2. 认知负荷 (Cognitive Load) 🧠
- **美**：一目了然，不需要大脑费力处理。"好设计是看不见的"（Invisible）。
- **丑**：像解谜一样，用户需要花时间去理解"这是什么？"（如：满屏文字没有图解）。

### 3. 色彩语义 (Semantic Color) 🎨
- **美**：颜色有明确含义（如：绿色=安全/通过，红色=禁止/警告），且颜色数量克制（通常 < 3 种主色）。
- **丑**：颜色滥用、刺眼的高饱和度配色，或者颜色与功能不符。

### 4. 留白与呼吸感 (Whitespace) 🌬️
- **美**：元素之间有适当的间距，不拥挤，给人从容的感觉。
- **丑**：元素挤压在一起，密密麻麻，给人压迫感和焦虑感。

### 5. 一致性 (Consistency) 🧩
- **美**：字体、圆角、图标风格统一，像是一个整体。
- **丑**：各种风格的大杂烩（如：衬线体配无衬线体，扁平图标配拟物按钮）。

---

## 二、Dieter Rams 的好设计十原则（经典准则）

当 boku 需要严肃评价一个设计是否"好"时，以此为标准：

1.  **Good design is innovative** (创新的)
2.  **Good design makes a product useful** (实用的)
3.  **Good design is aesthetic** (美观的)
4.  **Good design makes a product understandable** (易懂的) —— *这是核心！*
5.  **Good design is unobtrusive** (克制的/不引人注目的)
6.  **Good design is honest** (诚实的)
7.  **Good design is long-lasting** (耐用的/不过时的)
8.  **Good design is thorough down to the last detail** (细节完美的)
9.  **Good design is environmentally-friendly** (环保的)
10. **Good design is as little design as possible** (极简的)

---

## 三、多模态审美练习（实战案例）

### 案例：LA 停车标志对比

| 维度 | ❌ **丑（旧标志）** | ✅ **美（Nikki 的设计）** |
| :--- | :--- | :--- |
| **视觉表现** | 4 个牌子叠在一起，红白黑白混杂 | 一个牌子，网格布局，色块清晰 |
| **阅读体验** | 必须逐字阅读，还要脑补时间线 | 扫一眼颜色就知道能不能停 |
| **情绪反应** | 焦虑、困惑、压抑 | 轻松、确定、高效 |
| **核心问题** | 信息过载 (Information Overload) | 信息可视化 (Data Visualization) |
| **审美结论** | **丑**：因为它不解决问题，还制造混乱 | **美**：因为它优雅地解决了复杂问题 |

---

## 四、特殊场景："丑"也是美？

有时候，**刻意设计的丑**也是一种风格（如：Brutalism 粗野主义、朋克风格、酸性设计）。

**如何区分"难看的丑"和"风格的丑"？**
1.  **意图性**：是故意为之（风格化）还是无意搞砸了？
2.  **功能性**：虽然丑，但是否达到了目的（如引起注意、表达叛逆）？
3.  **一致性**：丑得有逻辑、有系统，还是单纯的乱？

**结论**：无意图的混乱是丑，有意图的打破规则可能是艺术。

---

## 六、关联参考

当需要分析具体 UI 设计风格或选择交互方案时，查阅配套参考文件：

- `references/ui-ux-styles-reference.md` — UI 设计风格全景、UX 七大定律、无障碍基线、风格陷阱速查、情感化设计三层模型

---

## 五、boku 的自我修炼

当 boku 生成图片或排版文档时，应用此流程：

1.  **检查层级**：重点突出了吗？
2.  **检查负荷**：用户一眼能看懂吗？
3.  **检查对齐**：元素对齐了吗？（对齐是治愈丑的良药）
4.  **做减法**：能不能去掉一些不重要的元素？

> **品味 (Taste) 的本质**：不是发现美的能力，而是对丑的**零容忍**。 —— Ira Glass
