# 🔧 FixRule 引擎实战经验 — 自动发现 & 路径 Bug & Git 管理

> **来源**: 2026-05-16 治理修复实战（doc-engine / developer-workflow / financial-analysis 三包修复）  
> **适用**: 任何 `skill-governance fix` 命令开发或修复规则调试场景  
> **核心问题**: FixRule 写好了却不生效？F001 总说 SKILL.md 找不到？.bak 文件污染 git？

---

## 一、FixRule 自动发现模式

### 问题

`skill_governance/cli/main.py` 的 `_setup_fix_dispatcher()` 函数是**空壳**——有 8 个 FixRule 子类在 `fixer/rules/` 目录下，但 dispatcher 完全不知道。

```python
# ❌ 原代码 — 空壳
def _setup_fix_dispatcher() -> FixDispatcher:
    dispatcher = FixDispatcher()
    # TODO: auto-discover concrete FixRule subclasses from
    #       skill_governance.fixer.rules package (future stories).
    return dispatcher
```

`skill-governance fix packs/doc-engine/ --dry-run` 输出：
```
Warning: No fix rules are registered yet. Results will be empty until fix rules are implemented.
```

### 修复方案

使用 `importlib` + `inspect` + `pkgutil.walk_packages()` 自动发现并注册：

```python
def _setup_fix_dispatcher() -> FixDispatcher:
    import importlib
    import inspect
    import pkgutil

    dispatcher = FixDispatcher()
    rules_pkg = importlib.import_module("skill_governance.fixer.rules")

    for importer, modname, ispkg in pkgutil.walk_packages(
        rules_pkg.__path__, rules_pkg.__name__ + "."
    ):
        try:
            mod = importlib.import_module(modname)
        except Exception:
            continue
        for name, obj in inspect.getmembers(mod):
            if (
                inspect.isclass(obj)
                and issubclass(obj, FixRule)
                and obj is not FixRule
            ):
                try:
                    instance = obj()
                    dispatcher.register(instance)
                except Exception as e:
                    print(f"  ⚠️  Failed to register {name}: {e}")
    return dispatcher
```

### 关键注意事项

| 注意点 | 说明 |
|:-------|:------|
| **FixRule 必须从 `__init__.py` 导出** | 确保 `from skill_governance.fixer import FixRule` 可工作 |
| **抽象类不会被注册** | `LLMAssistRule` 有 `abstractmethod` → 自动跳过（`Can't instantiate abstract class`） |
| **walk_packages 递归扫描** | 会扫描 `rules/` 下所有子模块，包括 `__init__` |
| **`inspect` + `issubclass`** | 只注册 `FixRule` 的直接/间接子类 |
| **运行时错误不阻断** | 异常时 `print` 警告 + 继续注册其他规则 |

---

## 二、F001 路径解析 Bug（双重 SKILL.md）

### 问题

当一个 skill 在 `cap-pack.yaml` 中用**完整文件路径**声明时：

```yaml
skills:
  - id: plan
    path: SKILLS/plan/SKILL.md  # ← 包含文件名
    version: 1.0.0
```

扫描器的 `_load_skills_from_pack()` 解析后得到正确路径：
```
.../packs/developer-workflow/SKILLS/plan/SKILL.md
```

但 F001 checker 在那个路径上**再次追加** `/SKILL.md`：
```
.../packs/developer-workflow/SKILLS/plan/SKILL.md/SKILL.md
#                                             ↑ 多出来的！
```

### 根因

扫描器假设 skill `path` 字段是**目录路径**，但某些 skill 用了**完整文件路径**。`_load_skills_from_pack()` 中没有处理尾部 `SKILL.md` 检测：

```python
# ❌ 原代码：无条件追加 /SKILL.md
skill_path = pack_dir / skill_path  # 用户路径原样保留
# 后来 F001 checker 又加了一次 SKILL.md
```

### 修复方案

统一路径解析，检测是否已以 `SKILL.md` 结尾：

```python
def _resolve_skill_path(pack_dir: Path, skill: dict) -> Path:
    skill_path = skill.get("path", "")
    sid = skill.get("id", "")
    if not skill_path:
        return pack_dir / "SKILLS" / sid / "SKILL.md"
    resolved = pack_dir / skill_path
    if resolved.name == "SKILL.md" or resolved.suffix == ".md":
        return resolved
    return resolved / "SKILL.md"
```

### 验证方法

```bash
# 对有完整路径声明的包运行 F001
skill-governance fix packs/developer-workflow/ --rules F001 --dry-run
# ❌ 修复前: 3 个缺失 skill（路径误判）
# ✅ 修复后: 无缺失
```

---

## 三、.bak 备份文件与 Git 管理

### 问题

`FixRule._backup()` 在 `apply()` 前自动创建 `.bak` 文件。这些文件显示为 git **未跟踪文件**，污染工作目录：

```
?? packs/doc-engine/SKILLS/pdf-layout/SKILL.md.bak
?? packs/developer-workflow/cap-pack.yaml.bak
?? packs/developer-workflow/SKILLS/plan/SKILL.md.bak
```

### 修复方案

在 `.gitignore` 中添加 `*.bak`：

```gitignore
# Backup files
*.bak
```

### 恢复步骤（如果已误提交）

```bash
git rm --cached '*.bak'
git commit -m "chore: 移除 .bak 备份文件跟踪"
```

### 设计决策

| 选项 | 结论 | 理由 |
|:-----|:----:|:------|
| 保留 .bak 在 git 跟踪中 | ❌ | 每次 fix 产生大量脏文件 |
| .bak 被 .gitignore 排除 | ✅ | 本地有备份，git 不跟踪 |
| fix 成功后自动清理 .bak | 可选 | 灾难恢复需本地保留 |

---

## 四、常见修复模式的实际效果

### E002 跨平台兼容性 — 性价比最高的修复

| 包 | 修复前 L3 | 修复后 L3 | 提升 | 修复动作 |
|:---|:---------:|:---------:|:----:|:---------|
| doc-engine | 50.0% | 70.0% | **+20%** | 9 个技能加 `agent_types` |
| developer-workflow | 60.0% | 80.0% | **+20%** | 11 个技能加 `agent_types` |
| financial-analysis | 60.0% | 80.0% | **+20%** | 1 个技能加 `agent_types` |

**规律**: E002 修复几乎总是带来 **L3 +20%** 的提升，是单次修复中性价比最高的规则。

### F006/F007 包级 vs 技能级错位

```
Scanner 报告的 F006 违规在 skill 级别:
  violations: [{skill_id: 'plan', classification: ''}]

FixRule F006 修复的是 pack 级别:
  data["classification"] = inferred  # 包级 classification
```

**排查步骤**:
1. `scan --format json` 查看违规发生层级（`details` 字段）
2. skill 数组内的字段 → 需 skill 级 fixer
3. cap-pack.yaml 顶层字段 → pack 级 fixer 可用
4. 当前 FixRule 只实现了 pack 级修复，skill 级修复需新增

### 包扫描的典型分布

17 个能力包扫描显示高度一致的分数分布：

| Layer | 典型分 | 常见违规 |
|:------|:------:|:---------|
| L0 | 100% | 无 |
| L1 | 57.14% | F001 路径 / F006 分类 / F007 triggers |
| L2 | 80.00% | H001 无簇 / H002 簇过小 |
| L3 | 60.00% | E001 SRA 发现性 / E002 跨平台 |
| L4 | 100% | 无 |

**启示**: 相同模式 → 批量修复策略有效。

---

## 五、批量修复工作流（17 包实战）

### 问题

17 个能力包逐个手动扫描 + 修复需要 3+ 小时。需要一种可重复的批量操作模式。

### 批量修复两步法

```
Phase A: 安全规则快速扫描 (E001 + E002)
  ── 确定性最高，无破坏性
  ── 每包 ~30s，可并行
  ── 典型提升 L3: 60% → 80%

Phase B: 结构性规则深度修复 (F006 + F007 + H001)
  ── 需包级 vs skill 级模式判断
  ── 需人工程序确认簇合并
  ── 可预计算但不可全自动 apply
```

### 执行步骤

```bash
# 1. 先对最复杂/最稳定的包单独测试
PYTHONPATH=packages/skill-governance:$PYTHONPATH \
  python3 -m skill_governance.cli.main fix packs/doc-engine/ \
  --rules E001,E002 --dry-run

# 2. 确认 dry-run 输出后 apply
#    — 确保 .bak 已加入 .gitignore
#    — 检查 .bak 文件是否被误创建

# 3. 批量并行执行剩余包（用 background terminal）
source ~/projects/hermes-cap-pack/.env  # 如有需要
for pack in packs/*/; do
  name=$(basename "$pack")
  [ -f "$pack/cap-pack.yaml" ] || continue
  # 用 notify_on_complete=true 避免阻塞
  PYTHONPATH=packages/skill-governance:$PYTHONPATH \
    python3 -m skill_governance.cli.main fix "$pack" \
    --rules E001,E002 --apply
done

# 4. 每轮完整 commit（含 .gitignore 检查）
git add -A
git checkout -- '*.bak'           # 排除 .bak
git rm --cached '*.bak' 2>/dev/null  # 清理已跟踪的
git status                         # 确认无 .bak
git commit -m "fix(batch): N 包 E001+E002 修复"

# 5. 推送到远程 + 等待 CI
git push origin main
gh run watch                       # 或等通知
```

### Phase A 实战数据（2026-05-16）

| 维度 | 数据 |
|:-----|:-----|
| 包数 | 14 包 (3 预修复 + 11 批量) |
| 总修复数 | 174 |
| 总耗时 | ~8 分钟 (并行) |
| L3 提升 | 每包 +20% (60% → 80%) |
| CI 通过 | ✅ 首次 |
| 发现的工程问题 | 3 个 (空壳dispatcher / 双重path / .bak污染) |

### Phase A 适用条件

| 条件 | 判定 | 不适用时的替代方案 |
|:-----|:-----|:-----------------|
| 修复规则是确定性的 (E001/E002) | `dry-run` 输出无警告 | 先用人眼审阅 dry-run diff |
| 无文件创建（只修改元数据） | 无 `CREATE` 动作 | 逐个 apply，逐包 review |
| 幂等性检查已实现 | `_is_already_fixed()` 存在 | 先手动确认不会重复修改 |
| 有回滚机制 | `.gitignore` 含 `*.bak` | 先 fix `.gitignore` |

## 六、修复后文档对齐清单（Post-Fix Doc Alignment）

> **关键洞察**: 修复引擎自动修改了元数据，但**不会自动更新项目文档**。修复完成后必须手动对齐以下文档，否则下次迭代出现系统性漂移。

### 必须更新的文档

| # | 文档 | 更新内容 | 示例 |
|:-:|:-----|:---------|:-----|
| 1 | **CHANGELOG.md** | 新增修复版本条目（包数/修复数/L3 提升） | `fix(batch): 11 个包 E001+E002 修复 (80 fixes)` |
| 2 | **README.md** | 更新头部 badge（如有 repair badges） | `**治理修复**：174 fixes ✅ · L3 Score 60% → 80% ↑` |
| 3 | **project-report.json** | 更新 tests passing / overview cards | 修复前后对比数据 |
| 4 | **PROJECT-PANORAMA.html** | 新增修复统计节点 | `🔧 全量治理修复 — 17 包 × 174 fixes` |
| 5 | **docs/project-state.yaml** | 如有相关 Story/EPIC 状态变化 | `verify` 确认通过 |
| 6 | **用 `project-state.py verify` 验证** | 一致性检查 | `✅ 通过 (1 warning)` |

### 对齐顺序（从底向上）

```text
修复后文件修改 (cap-pack.yaml / SKILL.md)
    ↓
CHANGELOG.md ── 记录修复统计
README.md ── 更新 badges
project-report.json ── 同步测试/版本数据
PROJECT-PANORAMA.html ── 新增修复节点
    ↓
git add -A && git checkout -- '*.bak'
git commit -m "fix(batch): N 包 E001+E002 修复 + 文档对齐"
git push origin main
    ↓
gh run list --limit 1  // 确认 CI 通过
```

### 典型对齐耗时

| 文件数 | 耗时 | 说明 |
|:------:|:----:|:------|
| 1-2 | ~2min | 仅 CHANGELOG + README |
| 3-5 | ~5min | 含 project-report + HTML |
| 6+ | ~10min | 含 project-state 同步 + verify |

### 实战案例（2026-05-16）

修复 14 包后，对齐了以下文档：
- CHANGELOG.md: 新增治理修复 Bug 修复 + 174 fixes 条目
- README.md: 新增 badge `治理修复：174 fixes ✅ · L3 60%→80% ↑`
- project-report.json: version badge 0.9.1→1.0.0
- PROJECT-PANORAMA.html: 新增 `🔧 全量治理修复 — 17 包 × 174 fixes` 节点
