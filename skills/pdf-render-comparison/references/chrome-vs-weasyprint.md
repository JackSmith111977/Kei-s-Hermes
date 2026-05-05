# Headless Chrome vs WeasyPrint PDF 渲染对比报告

## 测试环境

- 操作系统: Ubuntu
- Chrome: Google Chrome 147.0.7727.137
- WeasyPrint: 68.1（已从 61.1 升级）
- Python: 3.12

## 测试内容

包含：中文渲染、多语言混合、表格（表头背景+斑马纹）、代码块（深色背景）、Flexbox 三列布局、提示块。

## 对比结果

| 维度 | WeasyPrint 68.1 | Headless Chrome 147 |
|------|-----------------|---------------------|
| **文件大小** | 164.7 KB | 236.7 KB (+44%) |
| **渲染时间** | ~2s | ~5s |
| **中文渲染** | ⭐⭐⭐⭐ 正常 | ⭐⭐⭐⭐⭐ 完美 |
| **表格** | ⭐⭐⭐⭐ 正常 | ⭐⭐⭐⭐⭐ 完美 |
| **代码块** | ⭐⭐⭐⭐ 正常 | ⭐⭐⭐⭐⭐ 完美 |
| **Flexbox** | ⭐⭐⭐⭐ 正常 | ⭐⭐⭐⭐⭐ 完美 |
| **分页控制** | ⭐⭐⭐⭐ 优秀 | ⭐⭐⭐ 一般 |
| **页眉页脚** | ⭐⭐⭐⭐ @page 规则 | ⭐⭐⭐ Chrome flags |
| **CSS 覆盖率** | ~95% | 100%（完整浏览器） |

## 各自优劣

### WeasyPrint 优势
1. **分页控制精细**：`page-break-before/inside/after`、`widows/orphans` 完美支持
2. **动态页眉页脚**：`@top-center { content: string(chapter-title); }` 动态章节名
3. **命名页面**：`@page cover { }` / `@page chapter { }` 不同页面不同样式
4. **文件更小**：输出 PDF 比 Chrome 小 44%
5. **渲染更快**：无需启动浏览器进程
6. **Python 原生**：可直接在代码中控制，无需 subprocess

### Headless Chrome 优势
1. **渲染质量最高**：100% CSS 支持，Flexbox/Grid/动画/阴影全部完美
2. **所见即所得**：和浏览器中看到的完全一致
3. **字体渲染**：抗锯齿和字距调整更精细
4. **无需学习新 API**：会写 HTML/CSS 就行

### WeasyPrint 劣势
1. Flexbox 部分特性支持不完整（v65+ 已大幅改善）
2. CSS Grid 支持较晚（v62+ 才支持）
3. 某些 CSS3 特性（如 `box-shadow`）渲染不如 Chrome

### Headless Chrome 劣势
1. **分页控制弱**：长表格/代码块可能被生硬切断
2. **无法动态页眉页脚**：不能根据章节变化
3. **需要 Chrome 二进制**：依赖系统安装 Chrome
4. **文件更大、速度更慢**

## 选型建议

- **技术文档/报告/论文** → WeasyPrint（分页控制最重要）
- **复杂网页/PWA/营销页** → Headless Chrome（渲染保真度最重要）
- **证书/票据/发票** → ReportLab（像素级精确控制）
- **简单文本 PDF** → fpdf2（最轻量）

## 命令参考

```bash
# WeasyPrint
python3 -c "from weasyprint import HTML; HTML(filename='input.html').write_pdf('output.pdf')"

# Headless Chrome
google-chrome --headless --disable-gpu --no-sandbox \
  --print-to-pdf=output.pdf \
  --paper-type=A4 \
  --print-to-pdf-no-header \
  "file:///path/to/input.html"
```
