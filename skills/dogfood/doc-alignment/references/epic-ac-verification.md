# Epic Story AC 验证方法论 — 代码 vs 文档深度审计

> **适用场景**: 接手 EPIC-003 这类文档声称 ~40% 完成但代码实际 ~95% 的情况。  
> **核心问题**: 文档验收标准标记为 [ ] 但代码已经实现。  
> **根本原因**: 文档在代码实现后未同步更新，导致漂移。

## 审计流程

### Phase 1: 代码结构全景扫描

在读取任何文档前，先构建代码地图：

```bash
# 1. 文件树
find . -type f -name "*.py" | sort

# 2. 关键文件定位 — 哪些文件与文档中提到的 Story 对应？
#    检查 runtime/ 目录（daemon 核心）、tests/ 目录（测试覆盖）
#    特别关注文档声称「缺失/未完成」的文件

# 3. 测试文件列表
find tests/ -name "*.py" | sort
```

### Phase 2: 逐 Story AC 核查

对每个 Story，逐一检查每项 AC：

```bash
# 模式 A: 文件存在性检查（文档声称文件不存在）
ls -la skill_advisor/runtime/lock.py        # Story 12 的文件锁
ls -la tests/test_singleton.py              # Story 12 的测试

# 模式 B: 关键实现检查（grep 特定函数/类/字符串）
grep -n "serve_forever\|ThreadingMixIn" skill_advisor/runtime/daemon.py
grep -n "fcntl.flock\|FileLock" skill_advisor/runtime/lock.py

# 模式 C: 项目级 except:pass 普查
grep -rn "except.*:\s*pass" skill_advisor/ --include="*.py"
```

验收标准分类:

| 标记 | 含义 | 操作 |
|:----:|:-----|:-----|
| ✅ | 代码完整实现 | `[x]` |
| ⏳ | 部分实现（有注释说明） | `[x]` + 括号注明剩余 |
| ❌ | 未实现 | 保持 `[ ]` |

### Phase 3: 依赖链验证

文档有时声称 Story B 依赖 Story A（B 未完成因为 A 未完成）。  
验证方法：检查 B 的代码是否确实依赖 A 的代码。

```bash
# 检查 import 链
grep "from.*lock\|from.*validate" skill_advisor/runtime/daemon.py
grep "skill_map\|validate_core" skill_advisor/runtime/endpoints/validate.py
```

### Phase 4: 测试验证

```bash
# 完整测试运行
python -m pytest tests/ -x --tb=short -q

# 与文档声明的测试数对比
# 若实际 > 文档 → 文档过时（测试已增加但未同步）
# 若实际 < 文档 → 测试可能被删除或文档虚报
```

### Phase 5: 批量文档更新

当多个 Story 需要更新时，逐一 patch 效率低且易出错。  
推荐方案：使用 `execute_code` 调用 `hermes_tools.patch` 批量更新。

```python
from hermes_tools import patch

# 批量更新多个 AC
# 注意: old_string 必须精确匹配文件中的文本
# 不要对 " 进行转义（patch 检测到 escape-drift 会拒绝）
patch(path="docs/EPIC-XXX.md",
      old_string="- [ ] 某项验收标准",
      new_string="- [x] 某项验收标准")
```

### Phase 6: 最终验证

```bash
# 统计最终状态
grep -c "\[x\]" docs/EPIC-003-*.md   # 完成项数
grep -c "\[ \]" docs/EPIC-003-*.md   # 剩余未完成项
grep -n "\[ \]" docs/EPIC-003-*.md   # 列出未完成项

# 回归测试（确保文档修改不破坏任何代码）
python -m pytest tests/ -x --tb=short -q
```

## Known Pitfalls

| 陷阱 | 说明 | 缓解 |
|:-----|:------|:-----|
| **patch 换行符转义** | 多行 old_string 中的 `\n` 被转义为字面 `\\n` | 用 `execute_code` + `hermes_tools.patch()` 替代直接 patch |
| **动态版本误报** | setuptools-scm 项目无静态 `__init__.py` 版本号，`--verify` 误报 | 以 `git describe --tags` 为准 |
| **文档完成标记虚高** | Epic header 标「全部完成」但 AC 未实现 | 以 AC 条目为准，非 header |
| **文件名变更** | 实现文件路径 vs 文档中写的路径不同 | 以实际文件路径为准，更新文档 |
