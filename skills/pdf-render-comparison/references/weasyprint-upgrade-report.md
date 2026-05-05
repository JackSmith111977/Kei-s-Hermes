# WeasyPrint v61.1 → v68.1 升级验证报告

## 结论：✅ 无 Breaking Changes，安全升级

### Breaking Changes 清单

| 版本 | Breaking Change | 对我们影响 |
|------|----------------|-----------|
| v62 | Python 3.9+（放弃 3.7/3.8） | ✅ 无影响（我们用 3.12） |
| v63 | pydyf 0.11.0+, tinyhtml5 替代 html5lib | ✅ 自动升级，API 不变 |
| v64 | 无破坏性变更 | ✅ |
| v65 | CSSSelect2 0.8.0+ | ✅ 自动升级 |
| v67 | Python 3.10+（放弃 3.9） | ✅ 无影响（我们用 3.12） |
| v68 | URL fetcher API 重构 | ⚠️ 仅影响自定义 URL fetcher |

### 核心 API 兼容性

| API | v61.1 | v68.1 | 状态 |
|-----|-------|-------|------|
| `HTML(string=...)` | ✅ | ✅ | 兼容 |
| `HTML.write_pdf(font_config=...)` | ✅ | ✅ | 兼容 |
| `CSS()` | ✅ | ✅ | 兼容 |
| `FontConfiguration()` | ✅ | ✅ | 兼容 |
| `@font-face` | ✅ | ✅ | 兼容 |
| `@page` | ✅ | ✅ | 兼容 |

### 新增特性（已验证可用）

| 特性 | 版本 | 状态 |
|------|------|------|
| CSS Grid 布局 | v62+ | ✅ 可用 |
| CSS Nesting | v62+ | ✅ 可用 |
| Flexbox gap | v65+ | ✅ 可用 |
| CSS Color Level 4 | v63+ | ✅ 可用 |
| PDF/A 支持增强 | v62+ | ✅ 可用 |

### 安全更新

| CVE | 版本 | 说明 |
|-----|------|------|
| CVE-2025-68616 | v68.0 | URL fetcher 安全修复 |
| 安全更新 | v61.2 | 默认 URL fetcher 加固 |

### 建议

1. **升级安全**：所有核心 API 兼容，无 breaking changes 影响我们的使用方式
2. **推荐升级**：获得 CSS Grid、Flexbox gap、CSS Nesting 等新特性
3. **唯一注意**：如果使用了自定义 `url_fetcher`，需检查 v68 的 API 变更
