# HTML 报告追溯性来源链接化 — 操作指南

> 当已有 HTML 报告中的来源是纯文本（不可点击），需要追溯添加 `<a>` 标签时的操作手法。

## 场景

HTML 报告中已有引用格式如下：

```html
<div class="src">— mofa.ai/mofa/concepts/microkernel.html</div>
<div class="src">— arxiv 2512.01610</div>
```

需要改为可点击链接：

```html
<div class="src">— <a href="https://mofa.ai/mofa/concepts/microkernel.html" target="_blank">mofa.ai/mofa/concepts/microkernel.html</a></div>
<div class="src">— <a href="https://arxiv.org/abs/2512.01610" target="_blank">arxiv 2512.01610</a></div>
```

## 推荐工具：patch

使用 `patch` 工具逐条替换。每次替换一个引用，确保 `old_string` 足够长以唯一匹配。

### 模式 1: 纯域名 URL

```text
old_string: mofa.ai/mofa/concepts/microkernel.html
new_string: <a href="https://mofa.ai/mofa/concepts/microkernel.html" target="_blank">mofa.ai/mofa/concepts/microkernel.html</a>
```

### 模式 2: arxiv 引用（引用块内）

```text
old_string: 📕 Agent-Kernel — arxiv 2512.01610
new_string: 📕 Agent-Kernel — <a href="https://arxiv.org/abs/2512.01610" target="_blank">arxiv 2512.01610</a>
```

### 模式 3: arxiv 引用（表格内）

```text
old_string: arxiv 2403.16971</span></td>
new_string: <a href="https://arxiv.org/abs/2403.16971" target="_blank" style="color:var(--cyan);">arxiv 2403.16971</a></span></td>
```

## 高频替换清单

| 原始文本 | 替换为 | URL |
|:---------|:-------|:----|
| `mofa.ai/mofa/concepts/microkernel.html` | `<a href="https://mofa.ai/..." target="_blank">mofa.ai/...</a>` | https://mofa.ai/mofa/concepts/microkernel.html |
| `arxiv NNNN.NNNNN` (引用块) | `<a href="https://arxiv.org/abs/NNNN.NNNNN" target="_blank">arxiv NNNN.NNNNN</a>` | https://arxiv.org/abs/NNNN.NNNNN |
| `arxiv NNNN.NNNNN` (表格) | `<a href="https://arxiv.org/abs/NNNN.NNNNN" target="_blank" style="color:var(--cyan);">arxiv NNNN.NNNNN</a>` | https://arxiv.org/abs/NNNN.NNNNN |
| `{domain}.com/...` | `<a href="https://{domain}.com/..." target="_blank">{domain}.com/...</a>` | https://{domain}.com/... |

## 注意事项

1. **patch 的旧文本必须唯一匹配**——如果有多处相同文本，需增加前后文使其唯一
2. **表格内 vs 引用块内需要不同处理**——表格内可能有 `style` 属性，引用块内没有
3. **一次只改一个引用**——不要尝试一次性改多个，容易匹配失败
4. **改完后用 `--health` 验证**——确认链接格式正确

## 验证

```bash
# 检查链接数量
grep -c 'href=' report.html

# 抽样检查链接格式
grep -oP 'href="https?://[^"]+' report.html | head -10
```
