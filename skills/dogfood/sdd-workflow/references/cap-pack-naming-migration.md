# CAP Pack 命名迁移实战记录

> **日期**: 2026-05-13 ~ 2026-05-14
> **项目**: hermes-cap-pack
> **迁移目标**: 从旧式 `STORY-001-desc.md` / `SPEC-001-desc.md` 统一为层级归属格式 `STORY-{epic}-{spec}-{seq}` / `SPEC-{epic}-{seq}`

---

## 迁移步骤

### Phase 1: 定义规范

先在 SDD 工作流 skill 中定义命名规范（SKILL.md 7.1 节），涵盖：
- 所有文档类型的命名格式（EPIC/SPEC/STORY/ARCH/TECH/PLAN）
- 目录结构
- 归属关系可视化示例
- 禁止的旧格式清单

### Phase 2: 创建门禁脚本

创建 `scripts/validate-sdd-naming.py`，自动检查：
- 新格式合规性（正则匹配）
- 旧格式残留检测
- 文件内部 ID 一致性（story_id ↔ 文件名）
- SPEC→EPIC、STORY→SPEC 归属一致性
- 支持 `--ci` 严格模式（exit code 控制）

### Phase 3: 批量文件重命名

分两轮执行：

**第一轮**（旧式 → 临时格式）：
- `STORY-001-splitting-analysis.md` → `STORY-1-1.md`
- `SPEC-001-splitting.md` → `SPEC-1-1.md`

**第二轮**（临时格式 → 完整三层格式）：
- `STORY-1-1.md` → `STORY-1-1-1.md`
- `STORY-1-10.md` → `STORY-1-4-3.md`

### Phase 4: 内部字段更新

更新每个文件的 frontmatter：
- `story_id` 字段
- `epic` 引用
- `spec_ref` 引用
- 标题行

### Phase 5: 交叉引用更新

对所有非 Story 文件执行批量替换：
- EPIC 中的 Story 列表
- SPEC 文件中的引用
- README/CHANGELOG 中的路径引用
- 其他文档中的链接

### Phase 6: 验证

```bash
python3 validate-sdd-naming.py --dir <project> --ci
# 期望: 全部文档命名规范合规
```

---

## 实战陷阱

### 陷阱 1：字符串子串替换错误 ⚠️

**问题**：用 `str.replace()` 批量替换时，`STORY-1-1` 作为 `STORY-1-10` 的子串被提前匹配，导致 `STORY-1-10` 变成 `STORY-1-1-10`。

**修复**：按字符串长度降序排列后再替换（最长优先）。

**详见**：`patch-file-safety` skill 的实战陷阱 7。

### 陷阱 2：git 无法追踪双重重命名

**现象**：文件在两次重命名后（A→B→C），git 无法自动检测 rename（因为第一次 rename 未被提交），导致被显示为 A + C（delete + create）而非 rename。

**建议**：如果分多轮重命名，每轮完成后提交一次，让 git 逐轮追踪。

### 陷阱 3：批量替换脚本的范围遗漏

**现象**：对 EPIC 文件做了替换，但对 README 和 CHANGELOG 中的引用未同步更新，导致文档不一致。

**建议**：替换前先 grep 搜索所有引用点，建立完整清单再执行。

---

## 迁移清单

- [ ] 定义命名规范到对应 skill
- [ ] 创建验证门禁脚本
- [ ] 文件重命名（git mv 或 os.rename）
- [ ] 更新文件内部字段
- [ ] 更新交叉引用（EPIC / SPEC / README / CHANGELOG 等）
- [ ] 门禁脚本验证通过
- [ ] git commit + push
