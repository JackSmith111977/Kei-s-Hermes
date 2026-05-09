# 知识路由自动执行引擎

> `~/.hermes/scripts/knowledge-ingest.py` — 决策树的执行器
> 自动完成：文件创建 + 索引更新 + 交叉引用维护

## 安装

脚本已内置在 `~/.hermes/scripts/knowledge-ingest.py`，零依赖（纯 Python 标准库）。

## 用法

### 沉淀经验 (L2)

```bash
python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type experience \
  --title "从XX问题中总结的调试方法" \
  --content "具体内容..." \
  --reusability high \
  --confidence 4
```

自动完成：
- 创建 `experiences/active/exp-{date}-{slug}.md`
- 追加到 `experiences/index.md`
- 追加到 `KNOWLEDGE_INDEX.md`

### 沉淀核心概念 (L3 Brain)

```bash
python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type concept \
  --name "概念名称" \
  --content "概念定义和详细说明..."
```

自动完成：
- 创建 `brain/wiki/concepts/{slug}.md`
- 追加到 `brain/index.md`
- 追加到 `brain/log.md`
- 追加到 `KNOWLEDGE_INDEX.md`

### 其他 L3 类型

```bash
# 实体（人/工具/项目）
python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type entity --name "实体名" --content "..."

# 摘要（文档提炼）
python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type summary --name "标题" --content "..."
  --source "原文链接"

# 分析（对比/推演）
python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type analysis --name "主题" --content "..."
```

### 自动检测

扫描 `learning/reviews/` 中未处理的学习总结：

```bash
python3 ~/.hermes/scripts/knowledge-ingest.py --auto-detect
```

## 与 knowledge-routing 决策树的对应

| 决策树输出 | 脚本命令 |
|:----------|:---------|
| L2 Experience (复用低/深度浅) | `--type experience --reusability medium/low` |
| L2 Experience (复用高/已验证) | `--type experience --reusability high` |
| L3 Brain/concepts/ | `--type concept --name "..." --content "..."` |
| L3 Brain/entities/ | `--type entity --name "..." --content "..."` |
| L3 Brain/summaries/ | `--type summary --name "..." --content "..."` |
| L3 Brain/analyses/ | `--type analysis --name "..." --content "..."` |

## 最佳实践

### 何时用 `--auto-detect` vs 直接模式

| 场景 | 推荐 | 原因 |
|:----|:-----|:-----|
| 刚完成学习/调研 | `--auto-detect` 优先 | 自动扫描未处理总结，避免遗漏 |
| 用户明确说"记下来" | 直接模式 | 内容已明确，无需扫描 |
| Review 触发 | `--auto-detect` 优先 | 检查是否有积压的未处理知识 |
| 开发中踩坑 | 直接模式 | 即时沉淀，用 `--type experience` |

### 典型错误

| ❌ 错误做法 | ✅ 正确做法 |
|:-----------|:-----------|
| `--type experience` 不给 `--reusability` | 总是给 `--reusability high/medium/low` |
| `--type concept` 不给 `--name` | `--name` 必填，作为文件名和索引标题 |
| 把具体操作步骤塞进 `--type concept` | 步骤用 `--type experience`，概念才用 concept |
| 手动写 brain 页面后再跑脚本 | **脚本代替手动**——它自动维护索引 |
| 先 `--auto-detect` 再直接模式 | 二选一——auto-detect 本身就会执行沉淀 |
| **`--content @-` heredoc 传内容** | **用 `--content @/path/to/file` 传物理文件** —— `@-` stdin 模式不支持 |

---

*最后更新: 2026-05-09 · 对应 knowledge-routing v3.2*
