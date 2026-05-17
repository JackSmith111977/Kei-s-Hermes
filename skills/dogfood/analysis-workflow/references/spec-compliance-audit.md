# 规格符合性审计 — Spec Compliance Audit

> **适用场景**: 独立审计一个项目，检查其实际实现是否兑现了已承诺的规格/EPIC 愿景。
> **与技术债审计的区别**: 技术债审计检查代码质量（坏味道、覆盖缺口）; 规格符合性审计检查"做的 vs 承诺的"差距。
> **实战验证**: Hermes-Cap-Pack 项目审计 (2026-05-17)

---

## 核心问题

审计回答的是三个问题：
1. **承诺了什么？** — EPIC / Spec / AC 中声明的目标
2. **实现了多少？** — 代码 + 运行时 + 文档中实际存在的
3. **差距在哪里？** — 系统化找出"承诺未兑现"的部分

---

## 五步审计法

### 步骤 1: 全景扫描 — 理解项目结构

首先绘制项目全貌，不要从单一入口进入。

```bash
# 1. 获取完整文件清单
find . -type f ! -path './.git/*' | sort

# 2. 识别关键目录
ls -d */                     # 顶层模块
ls packs/*/cap-pack.yaml     # 能力包清单
ls docs/EPIC-*.md            # EPIC 文档

# 3. 统计规模
find . -name '*.py' ! -path './.git/*' | wc -l
find . -name 'test_*.py' ! -path './.git/*' | wc -l
```

**产出**: 项目结构脑图 + 规模基线数据。

---

### 步骤 2: 读取所有 EPIC/Spec 文档 — 理解承诺

阅读每一个 EPIC，提取以下内容为结构化清单：

| EPIC | 状态 | AC 列表 | 交付物列表 | 质量目标 |
|:-----|:----:|:--------|:-----------|:--------:|
| EPIC-001 | approved | AC1-AC4 | Schema + 适配层设计 | — |
| EPIC-002 | approved | AC1-AC7 | 树索引 + SQS + 审计 | — |

**关键提取点**:
- **AC (Acceptance Criteria)**: 逐条记录，每项是"可验证的承诺"
- **成功画面**: 描述了愿景终点
- **SC 指标**: 用数字标明的质量目标（如 CHI ≥ 85）
- **交付物清单**: 规划了要产出的文件/工具

**产出**: `promises.md` — 所有 EPIC 承诺的结构化表格。

---

### 步骤 3: 运行时验证 — 检查代码真能跑

**不要只看代码，要运行它们来验证。**

```bash
# 3a. CLI 功能测试
python -m cli.main inspect     # 检查 CLI 是否可用
python -m cli.main status      # 状态命令
python -m cli.main search pdf  # 搜索功能

# 3b. 核心库导入测试
python -c "from scanner.base import RuleLoader; print('OK')"
python -c "from fixer.dispatcher import FixDispatcher; print('OK')"

# 3c. 测试套件运行
python -m pytest tests/ --tb=short -q
python -m pytest packages/*/tests/ --tb=short -q

# 3d. 扫描器/修复器实际执行
python -c "checker = ComplianceChecker(); checker.scan('packs/doc-engine')"
```

**关键检查点**:
- **CLI 确实有输出** — 不是只有 `argparse` 架子，命令能跑
- **Import 链完整** — `__init__.py` 正确导出所有类
- **测试确实通过** — 而不是"收集了但没跑"
- **扫描器返回真实结果** — 不是全部 100% pass（那可能是有 pass-by-default bug）

**产出**: `runtime-report.md` — 每个组件的可运行性证据。

---

### 步骤 4: 文档-代码一致性检查 — 检查漂移

这是最核心的一步。项目文档中声称的 vs 实际存在的。

```python
# 4a. 状态文件交叉比对
# 检查 project-state.yaml, chain-state.json, README 三处状态是否一致
# 同一个 EPIC 在三处可能声称不同的 stage/status

# 4b. 交付物清单比对
# EPIC 中说要产出的文件是否实际存在于文件系统中？
# 规则: "交付物清单中的每个条目 → 对应文件必须存在"

# 4c. 数量声明验证
# README 说"17 packs, 202 tests" → 实际数一下
# 用 find/wc 验证所有数字声明

# 4d. 质量目标对比
# EPIC-004 声称 CHI≥85 → 实际 chi-baseline.json 是多少
# AC 声称"17/17 packs have L2" → 实际每个 pack 的 EXPERIENCES/ 目录数
```

**常见漂移发现**:
| 类型 | 例子 | 严重度 |
|:-----|:-----|:------:|
| 状态漂移 | EPIC-004 在 project-state="approved", chain-state="DEV" | 🔴 中 |
| 数量漂移 | README 说 "202 tests" 但 test 文件数不对 | 🟡 低 |
| 质量虚标 | EPIC 目标 CHI≥85, 实际 67.92 | 🔴 高 |
| 空框架 | .governance-fingerprints.json 只有 {} | 🟡 中 |
| 类名混乱 | xxxFixRule vs xxxScanner 不统一 | 🟢 低 |

**产出**: `drift-report.md` — 文档-代码不一致清单。

---

### 步骤 5: 结构化报告 — 给出评分与建议

最终报告结构：

```markdown
## 🔍 审计报告: 项目名

### 一、全景数据
| 指标 | 数值 |
|:-----|:----:|

### 二、EPIC 实现状态矩阵
| EPIC | 愿景 | 实际 | 完成度 |
|:-----|:-----|:----|:------:|

### 三、关键发现（按严重度排序）
#### 🔴 高 — 核心差距
#### 🟡 中 — 需要改进
#### 🟢 低 — 建议项

### 四、建设性发现（亮点）

### 五、综合评分
> **X/100** — 一句话总结
```

---

## 检查清单

- [ ] 步骤 1: 全景扫描完成（文件树 + 规模数据）
- [ ] 步骤 2: 所有 EPIC/Spec 阅读完毕（承诺提取）
- [ ] 步骤 3: CLI + 导入 + 测试运行时验证
- [ ] 步骤 3: 扫描器/修复器实际执行验证
- [ ] 步骤 4: 状态文件交叉比对
- [ ] 步骤 4: 交付物清单 vs 实际文件
- [ ] 步骤 4: 数量声明验证（用 `find`/`wc` 计数）
- [ ] 步骤 4: 质量目标 vs 实际值
- [ ] 步骤 5: 报告包含严格等级排序
- [ ] 步骤 5: 报告既包含不足也包含亮点

---

## 实战套路速查 (Hermes-Cap-Pack 案例)

| 审计动作 | 命令/代码片段 |
|:---------|:--------------|
| 统计 Python 文件数 | `find . -name "*.py" ! -path './.git/*' \| wc -l` |
| 统计测试数 | `python -m pytest --collect-only -q \| tail -1` |
| 扫描包结构 | 实例化 `PackParser` 逐个解析 |
| 检查 L2/L3 覆盖 | `find packs/* -path "*/EXPERIENCES/*.md" \| wc` |
| 导入测试 | `python -c "from module import Class; print('OK')"` |
| 状态对比 | `cat docs/project-state.yaml + docs/chain-state.json` |
| 质量基线 | `cat reports/chi-baseline.json` |
