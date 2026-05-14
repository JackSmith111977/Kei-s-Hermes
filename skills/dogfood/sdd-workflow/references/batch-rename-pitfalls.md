# 批量重命名陷阱 & 安全模式

> 2026-05-13 实战记录 | cap-pack 项目命名规范统一迁移

## 问题：字符串包含导致的交叉引用损坏

当对文档 ID 进行批量替换时，`STORY-1-1` 是 `STORY-1-10` 的前缀子串。

### 错误示范

```python
# ❌ 有 Bug！STORY-1-10 会被错误替换为 STORY-1-1-10
replacements = {
    'STORY-1-1': 'STORY-1-1-1',   # ← 这也会匹配 STORY-1-10 中的 STORY-1-1 部分
    'STORY-1-10': 'STORY-1-4-3',
}
for old, new in replacements.items():
    content = content.replace(old, new)  # 先替换 STORY-1-1 → 再替换 STORY-1-10 就晚了
```

**结果**：`STORY-1-10` → `STORY-1-1-10`（错误！应为 `STORY-1-4-3`）

### 安全模式

```python
# ✅ 安全：按 key 长度降序替换，确保更长的匹配先处理
replacements = {
    'STORY-1-10': 'STORY-1-4-3',   # 较长的先替换
    'STORY-1-1': 'STORY-1-1-1',    # 较短的后替换
}
for old, new in sorted(replacements.items(), key=lambda x: -len(x[0])):
    content = content.replace(old, new)
```

### 正则模式（更安全）

```python
import re
# 使用完整词匹配，避免部分匹配
for old, new in replacements.items():
    content = re.sub(r'(?<![-\w])' + re.escape(old) + r'(?![-\w])', new, content)
```

## 文档迁移完整工作流

### 步骤

1. **先定义规则** — 更新 SDD skill 的 7.1 命名规范
2. **先建门禁** — 创建 `validate-sdd-naming.py` 脚本
3. **跑门禁摸底** — 确认当前违规数量和类型
4. **分步改名**：
   - 文件改名（`mv old new`）
   - 内部字段更新（`story_id` / `spec_ref` / title）
   - 交叉引用更新（按安全模式逐层替换）
5. **跑门禁复核** — 确认零违规
6. **验证** — `validate-sdd-naming.py --ci` exit 0

### 检查清单

- [ ] 文件重命名完成
- [ ] 内部 `story_id` / `epic` / `spec_ref` 同步更新
- [ ] Epic Stories 表格更新
- [ ] Spec 引用更新
- [ ] Story 之间交叉引用更新
- [ ] README / CHANGELOG / 其他文档引用更新
- [ ] 门禁脚本验证通过

### 实际案例

cap-pack 项目迁移：7 SPEC + 22 STORY 文件从 `STORY-{n}-{desc}` → `STORY-{epic}-{spec}-{seq}` 格式。详见 cap-pack 项目的 git log（commit 2488d8a 和 1888639）。
