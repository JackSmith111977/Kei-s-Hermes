---
name: html-css-rendering-qa
description: HTML/CSS 文档创建与浏览器渲染调试完整技能。涵盖 CSS 类名规范、命名空间隔离、浏览器工具调试流程、渲染异常排查清单。任何涉及生成 HTML 文档后的质量保障场景自动加载。
version: 1.0.0
triggers:
  - html 渲染
  - css 冲突
  - css 类名
  - 浏览器调试
  - 渲染异常
  - HTML QA
  - layout bug
  - 样式问题
  - 排版问题
  - 视觉验证
  - HTML review
metadata:
  hermes:
    tags: [html, css, browser, qa, debugging, rendering]
    category: documentation
    skill_type: qa
    design_pattern: checklist
depends_on: []

---

# HTML/CSS 渲染质量保障 (Rendering QA)

> **核心理念**: 每次生成 HTML 文档后，先用浏览器工具验证再交付，不凭猜测修问题。
> **核心教训**: `.app { min-height: 100vh }` 也会匹配 `.layer-title.app` —— 类名冲突可以静默破坏布局。

---

## 一、CSS 类名规范（防冲突）

### 1.1 类名冲突根因

CSS 中一个简单的类选择器 `.app` 会匹配**任何**带有 `class="app"` 的元素。
当外层容器 `class="app"` 与标题 `class="layer-title app"` 共享同一个类名时，
`.app` 的样式（如 `min-height: 100vh`）会意外地渗透到 `.layer-title.app` 上。

**典型案例**:

```css
/* 这个 .app 规则会匹配任何带 app 的元素 */
.app { display: flex; min-height: 100vh; }

/* .layer-title.app 也被 .app 匹配，继承了 min-height: 100vh */
.layer-title.app {
  background: var(--green-dim);
  color: var(--green);
  border-left: 4px solid var(--green);
}
/* ❌ 没有设置 min-height 来覆盖！所以获得了 720px 的诡异高度 */
```

### 1.2 命名空间化（推荐方案）

采用**命名空间前缀**隔离不同层级的类名，避免通用词污染：

| 层级 | 命名空间 | 示例 | 说明 |
|:-----|:---------|:-----|:------|
| **布局容器** | `ly-` | `ly-app`, `ly-main`, `ly-sidebar` | Layout 层，定义页面骨架 |
| **模块区块** | `bl-` | `bl-layer`, `bl-section` | Block 层，独立内容区块 |
| **组件** | `cp-` | `cp-card`, `cp-title` | Component 层，可复用组件 |
| **状态** | `is-` | `is-active`, `is-open` | State 层，用 `--` 连接 |
| **工具** | `u-` | `u-hidden`, `u-flex` | Utility 层，单一功能 |

**改造后的示例**:

```css
/* ✅ 布局容器 */
.ly-app { display: flex; min-height: 100vh; }

/* ✅ 区块标题 */
.bl-title {
  padding: 12px 18px;
  font-weight: 700;
  font-size: 1rem;
  display: flex;
  align-items: center;
}
.bl-title--meta { background: var(--purple-dim); border-left: 4px solid var(--purple); }
.bl-title--app  { background: var(--green-dim);  border-left: 4px solid var(--green); }
.bl-title--infra{ background: var(--cyan-dim);   border-left: 4px solid var(--cyan); }
.bl-title--growth{background: var(--orange-dim); border-left: 4px solid var(--orange); }
```

### 1.3 当名冲突不可避免时的兜底

如果必须使用通用类名（如历史原因），**显式覆盖所有可能冲突的属性**：

```css
/* 安全做法：所有可能被父级渗透的属性都显式覆盖 */
.section-title.app {
  background: var(--green-dim);
  color: var(--green);
  border-left: 4px solid var(--green);
  min-height: unset;       /* 🔴 关键：覆盖 .app 的 min-height */
  height: auto;            /* 覆盖可能的 height */
  max-height: none;        /* 覆盖可能的 max-height */
  overflow: visible;       /* 覆盖可能的 overflow */
}

/* 更安全：用更具体的父级选择器隔离 */
.layout-app > .section-title.app { /* ... */ }
```

### 1.4 CSS @scope 现代方案

现代浏览器支持 `@scope` 规则，从根本上隔离样式：

```css
@scope (.ly-app) {
  /* 这些样式只作用于 .ly-app 内部 */
  .title { font-weight: 700; }
  /* 不会泄漏到 .ly-app 外部的 .title */
}
```

---

## 二、HTML 文件内 CSS 组织规范

### 2.1 样式书写顺序

单一 HTML 文件的内联样式按此顺序组织：

```css
/* ═══ 1. 全局变量与重置 ═══ */
:root { --pink: #ff6b9d; --radius: 12px; }
* { margin: 0; padding: 0; box-sizing: border-box; }

/* ═══ 2. 布局层 (Layout) ═══ */
.ly-app { display: flex; }
.ly-sidebar { width: 280px; }
.ly-main { flex: 1; }

/* ═══ 3. 区块层 (Block) ═══ */
.bl-section { margin-bottom: 40px; }
.bl-title { padding: 12px; display: flex; align-items: center; }

/* ═══ 4. 组件层 (Component) ═══ */
.cp-card { background: var(--bg-card); border-radius: var(--radius); }
.cp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); }

/* ═══ 5. 修饰/状态层 (Modifier/State) ═══ */
.is-active { border-color: var(--pink); }
.is-hidden { display: none; }

/* ═══ 6. 工具/辅助层 (Utility) ═══ */
.u-flex { display: flex; }
.u-gap-sm { gap: 8px; }

/* ═══ 7. 响应式适配 (Responsive) ═══ */
@media (max-width: 768px) { /* ... */ }
```

### 2.2 类名冲突自查清单

写每个类名前问自己：

- [ ] 这个类名是否太短太通用？（`.box`, `.title`, `.app` → 需要命名空间）
- [ ] 这个类名在 HTML 中和其他元素共享了相同的词？（`.layer-title.app` 和 `.app`）
- [ ] 是否可能被其他同名类继承样式？（检查所有 `.xxx` 选择器）
- [ ] 父级选择器的 `min-height`, `height`, `max-height`, `overflow` 是否渗透？

---

## 三、浏览器调试工作流（强制流程）

### 3.1 每次生成 HTML 后的标准调试流程

```text
[生成 HTML 文件]
    ↓
┌─────────────────────────────────────────────┐
│ Step 1: 打开页面                             │
│ browser_navigate(url="file:///path/to.html") │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Step 2: 截图+视觉检查                        │
│ browser_vision(question="整体布局是否正常？   │
│  各容器高度是否一致？有没有异常间距/溢出？")   │
│ → 发现异常？进入 Step 3                      │
│ → OK？进入 Step 8                            │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Step 3: 用精确数值定位问题                    │
│ browser_console(expression="querySelector    │
│  获取目标元素的 offsetHeight/scrollHeight    │
│  与预期值对比")                              │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Step 4: 检查 Computed Style 找到异常来源      │
│ browser_console(expression="getComputedStyle │
│  获取目标元素的所有关键属性：min-height,      │
│  height, overflow, display, line-height")    │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Step 5: 追踪 min-height/value 的来源         │
│ browser_console(expression="遍历 styleSheets │
│  找到所有匹配目标元素的 CSS 规则，显示       │
│  每个规则中可能造成异常的属性")              │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Step 6: 修复后重新导航验证                    │
│ browser_navigate(url) → 重新加载             │
│ browser_console(检查修复后的高度)            │
│ browser_vision(截图确认视觉正常)             │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Step 7: 确认所有同类元素一致                  │
│ browser_console(批量检查所有同类元素的高度)   │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ ✅ Step 8: 发送给主人                        │
│ send_message(附带 MEDIA: 截图)              │
└─────────────────────────────────────────────┘
```

### 3.2 关键调试命令速查

```javascript
// 1. 批量检查高度一致性
const el = document.querySelectorAll('.target-class');
Array.from(el).map(e => ({ text: e.textContent.slice(0,20), height: e.offsetHeight }));

// 2. 查看元素所有生效的 CSS 属性
const cs = getComputedStyle(document.querySelector('.target'));
['min-height','height','max-height','overflow','display','line-height',
 'padding-top','padding-bottom','margin-top','margin-bottom','box-sizing']
  .forEach(p => console.log(p, ':', cs.getPropertyValue(p)));

// 3. 追踪样式来源（遍历样式表）
for (let s of document.styleSheets) {
  try {
    for (let r of s.cssRules) {
      if (r.selectorText && r.style.minHeight) {
        console.log(r.selectorText, '→ minHeight:', r.style.minHeight);
      }
    }
  } catch(e) {}
}

// 4. 检查父级链 min-height 渗透
let p = document.querySelector('.target');
while (p && p !== document.body) {
  const cs = getComputedStyle(p);
  if (cs.minHeight && cs.minHeight !== 'auto' && cs.minHeight !== '0px' && cs.minHeight !== 'none') {
    console.log('🟡 ANOMALY:', p.className, 'minHeight:', cs.minHeight);
  }
  p = p.parentElement;
}

// 5. 快速检查所有节点的布局信息
const all = document.querySelectorAll('*');
const issues = [];
all.forEach(el => {
  const cs = getComputedStyle(el);
  if (cs.minHeight !== 'auto' && parseInt(cs.minHeight) > 200 && !el.matches('body, html')) {
    issues.push({tag: el.className || el.tagName, minH: cs.minHeight, h: el.offsetHeight});
  }
});
console.table(issues);
```

---

## 四、常见渲染异常速查表

| 症状 | 可能的根因 | 诊断方法 | 修复 |
|:-----|:-----------|:---------|:-----|
| **容器异常高** | 父级 `min-height` 通过通用类名渗透 | 查 computed min-height → 查 styleSheets | `min-height: unset` 或重命名 |
| **卡片高度不一致** | grid items 内容不同 + 无 `grid-auto-rows: 1fr` | `browser_vision` 看布局 | `grid-auto-rows: 1fr` |
| **幽灵列** | `auto-fill` vs `auto-fit` 混淆 | 12 个 item 只有 10 个显示？某些列为空 | 用 `auto-fit` 替代 `auto-fill` |
| **文本换行容器变高** | 长文本 + `white-space: normal` | 截图可见文本换了两行 | `white-space: nowrap` + `overflow: hidden` + `text-overflow: ellipsis` |
| **元素缺失/渲染不全** | `overflow: hidden` 截断 | browser_snapshot 看是否存在 | 调整 overflow 或 max-height |
| **flex 子项溢出** | `flex-shrink: 0` + 内容过多 | 子项超出容器边界 | `min-width: 0` 或 `overflow: hidden` |
| **响应式断点错位** | @media 未覆盖所有设备 | browser_vision 在不同窗口大小 | 添加缺失断点 |

---

## 五、Post-Creation QA 清单

每次生成 HTML 文档后，逐项检查：

### 🟢 功能完整性
- [ ] 所有链接/导航可点击（browser 测试）
- [ ] 折叠/展开功能正常（如 js 控制）
- [ ] 所有内容可见（无截断/溢出）

### 🎨 视觉一致性
- [ ] 同类元素高度一致（browser_console 批量检查）
- [ ] 颜色/字体/间距一致
- [ ] 无异常空白或重叠

### 📱 响应式
- [ ] 桌面宽度（1200px）正常
- [ ] 平板宽度（768px）正常
- [ ] 手机宽度（375px）无严重破损

### 🔒 CSS 健壮性
- [ ] 无通用类名冲突（`.app`, `.title`, `.box` 等已命名空间化）
- [ ] 无 `min-height` 意外渗透
- [ ] 无 `overflow: hidden` 误截断
- [ ] grid 使用 `auto-fit` 而非 `auto-fill`（除非有意保留空位）

---

## 六、经验教训（2026-05-12）

### 案例：`.layer-title.app` 被 `.app` 污染

**经过**：boku 创建 HTML 报告，外层容器用 `class="app"`，应用层标题用 `class="layer-title app"`。
CSS 规则 `.app { min-height: 100vh }` 意外匹配了 `.layer-title.app`，使其获得 `min-height: 720px`。
其他层标题（`.layer-title.meta`, `.layer-title.infra`, `.layer-title.growth`）不含 `app` 类，不受影响。

**代价**：3 轮错误修复（改了卡片样式、flex 布局、grid 布局），最终才用浏览器工具定位到真正原因。

**教训**：
1. ❌ 不要「凭猜测」修渲染问题——**先用浏览器看，再用 console 测**
2. ❌ 不要假设问题在「最近改动的地方」——可能是一个无关的 CSS 规则
3. ✅ 用 `browser_console` 检查元素的 computed style 定位异常值
4. ✅ 用 `getComputedStyle` + `styleSheets` 遍历追踪样式来源
5. ✅ 通用类名（`.app`, `.title`, `.box`）一定要命名空间化

### 经验公式

```
渲染异常排查时间 ≈ 盲猜时间 × 3 + 浏览器调试时间 × 0.5
```

**所以**: 先花 2 分钟用浏览器看、测、定位，比花 10 分钟猜来猜去快得多。
