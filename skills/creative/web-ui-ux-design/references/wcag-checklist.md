# WCAG 2.2 合规清单

来源：W3C WCAG 22 官方 + WebAIM + AllAccessible（交叉验证 ✅）

## 三层合规级别
| 级别 | 标准数 | 含义 |
|:----|:-----:|:----|
| A | 25 | 最低可访问性 |
| AA | 38+25=63 | **推荐法律合规标准** |
| AAA | 23+63=86 | 增强可访问性 |

## 9 项 WCAG 2.2 新增标准

### 2.4.11 Focus Not Obscured (Minimum) — AA
- 键盘焦点不可被作者创建的内容完全遮挡
- 实现：`scroll-padding: 80px` 避免 sticky header 遮挡

### 2.4.12 Focus Not Obscured (Enhanced) — AAA
- 不可有任何部分被遮挡

### 2.4.13 Focus Appearance — AAA
- 焦点指示器面积 ≥ 2px 周长
- 聚焦/未聚焦之间对比度 ≥ 3:1

### 2.5.7 Dragging Movements — AA
- 拖拽操作必须可通过单次点击完成（除非拖拽是必需的）

### 2.5.8 Target Size (Minimum) — AA
- 触控目标 ≥ 24×24 CSS 像素
- 例外：行内链接、浏览器默认控件

### 3.2.6 Consistent Help — A
- 帮助机制（联系方式/帮助页面/聊天）在页面间位置一致

### 3.3.7 Redundant Entry — A
- 同一流程中已输入的数据自动填充/可选

### 3.3.8 Accessible Authentication (Minimum) — AA
- 认证流程支持密码管理器和复制粘贴

### 3.3.9 Accessible Authentication (Enhanced) — AAA
- 不依赖认知测试（如识别图片中的文字）

## 实施路线图

### 第 1 阶段：P0 — 基础合规（2-3 天）
```html
<!-- 1. 颜色对比度 ≥ 4.5:1（正文） 3:1（大字） -->
<!-- 使用 WebAIM Contrast Checker 验证 -->

<!-- 2. 全键盘可操作 -->
<button>可触达</button>
<a href="/">可触达</a>
<input>可触达</input>

<!-- 3. 语义 HTML -->
<header><nav><main><section><article><footer>
```

### 第 2 阶段：P1 — WCAG 2.2 新增（1-2 天）
```css
/* 焦点可见 (2.4.7) + 焦点不被遮挡 (2.4.11) */
*:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
html { scroll-padding-top: 80px; }

/* 触控目标 ≥ 24px (2.5.8) */
button, a { min-height: 24px; min-width: 24px; }
```

### 第 3 阶段：P2 — 增强（0.5-1 天）
```html
<!-- 拖拽替代方案 (2.5.7) -->
<div draggable="true" ondragend="handleDragEnd(event)"
     onclick="handleClick(event)" role="button" tabindex="0">
  可拖拽也可点击
</div>

<!-- 一致帮助 (3.2.6) -->
<footer>
  <a href="/help">帮助中心</a>  <!-- 每个页面相同位置 -->
</footer>

<!-- ARIA 标注 -->
<button aria-label="关闭对话框" onclick="closeModal()">×</button>
```
