# 代码库技术债审计方法论

> **适用场景**: 对任意 Python 代码库进行系统性技术债分析，产出分类分级的问题清单 + 整改规划
> **来源**: SRA 项目代码审计实践 (2026-05-10)
> **核心**: 分四层扫描 → 按四维度分类 → 成本收益排序 → 纳入迭代规划

---

## 〇、方法论总览

```
Phase 0: 库存清点 ──→ 扫描项目结构、文件行数、模块依赖
    ↓
Phase 1: 代码扫描 ──→ 逐模块读取核心源码，查找特定反模式
    ↓
Phase 2: 测试审计 ──→ 统计测试覆盖率、识别零测试模块
    ↓
Phase 3: 分类分级 ──→ 按 4 维度 + 3 优先级分类问题
    ↓
Phase 4: 规划整合 ──→ 成本收益排序 + 纳入现有 Epic/Sprint
```

---

## Phase 0: 库存清点

**目标**: 了解代码库全貌，确定分析范围

```bash
# 1. 完整源文件清单
find . -type f -name "*.py" | grep -v __pycache__ | grep -v .git | sort

# 2. 按文件行数排序（快速定位胖模块）
find . -name "*.py" -not -path "./.git/*" -not -path "./__pycache__/*" \
  -exec wc -l {} + | sort -n

# 3. 识别入口点和主要模块
#    - setup.py/pyproject.toml → 包结构
#    - __init__.py → 导出哪些类
#    - main() 函数位置 → 入口
```

**输出**: `module_list.md` — 包含每个模块的路径、行数、职责描述

---

## Phase 1: 代码扫描 — 四层扫描法

### Layer 1: 架构层扫描

| 检查项 | 工具/方法 | 风险信号 |
|:---|:---|:---|
| 模块职责分离 | 看 import 关系 + 文件行数 | 单文件 > 500 行混入多职责 |
| 单例/状态管理 | grep `PID_FILE\|lock\|singleton` | 无原子锁的竞态条件 |
| 服务器/网络层 | grep `http.server\|socketserver\|handle_request` | ThreadingMixIn + handle_request 错误组合 |
| 配置系统 | grep `DEFAULT_CONFIG\|load_config\|config.json` | 硬编码路径、无 schema 验证 |

**常见反模式**:
- CLI 函数在 daemon 模块中定义（职责耦合）
- `except: pass` 吞噬异常（静默失败）
- 双协议路由逻辑重复（Socket + HTTP 两套）

### Layer 2: 代码质量层扫描

```bash
# 1. except: pass 统计
grep -rn "except:" --include="*.py" . | grep -v ".git/" | grep -v "__pycache__"

# 2. 魔法数字统计
grep -n "score +=" skill_advisor/matcher.py

# 3. 无类型标注函数
python3 -c "
import ast
for f in ['file1.py', 'file2.py']:
    with open(f) as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            no_types = sum(1 for a in node.args.args if a.annotation is None)
            total = len(node.args.args)
            if total > 0 and no_types == total:
                print(f'  {f}:{node.lineno} {node.name}({total} params, no types)')
"

# 4. 日志不统一
grep -rn "^    print\|^        print" --include="*.py" . | grep -v test | grep -v ".git"
```

| 检查项 | 风险信号 |
|:---|:---|
| `except: pass` | ≥ 5 处即为严重 |
| 魔法数字 | ≥ 10 个硬编码分值 |
| 类型标注缺失 | ≥ 30% 的函数无类型 |
| print/logging 混用 | 主力模块中两者同时存在 |

### Layer 3: 测试覆盖审计

```bash
# 1. 识别所有测试文件
ls tests/test_*.py

# 2. 对照源文件看覆盖
src_modules = set(f.replace('.py', '') for f in os.listdir('skill_advisor'))
tested = set(f.replace('test_', '').replace('.py', '') for f in os.listdir('tests'))
missing = src_modules - tested

# 3. 统计每个测试文件的断言数量（了解深度）
grep -c "assert\|def test_" tests/test_*.py

# 4. 检查 fixture 依赖（是否只用固定数据）
```

| 覆盖度 | 评级 | 行动 |
|:---|:---:|:---|
| 所有模块有测试 | 🟢 良 | 无需额外行动 |
| 1-2 个模块缺测试 | 🟡 中 | 增加核心模块测试 |
| ≥3 个模块缺测试 | 🔴 差 | 必须优先补充 |

### Layer 4: 文档与基础设施

```bash
# 1. README 时效性检查
head -5 README.md

# 2. CHANGELOG vs 实际版本一致性
grep __version__ skill_advisor/__init__.py

# 3. 架构文档存在性
ls docs/ | grep -v EPIC | grep -v TECHDEBT

# 4. CI/CD 配置
cat .github/workflows/*.yml 2>/dev/null || echo "❌ 无 CI"
```

---

## Phase 2: 分类分级体系

### 四维度分类法

| 维度 | 缩写 | 典型问题 | 严重倾向 |
|:---|:---:|:---|:---:|
| 架构层面 | 🏗️ A | 模块耦合、设计反模式、配置缺陷 | 通常 🔴~🟡 |
| 代码质量 | 💻 C | except:pass、魔法数字、无类型 | 通常 🟡~🟢 |
| 测试问题 | 🧪 T | 零覆盖、缺集成测试、死代码 | 🔴~🟡 |
| 文档问题 | 📝 D | README 过时、缺架构文档 | 🟢 |

### 三级严重程度

| 级别 | 标签 | 定义 | 行动时限 |
|:---:|:---:|:---|:---:|
| 🔴 P0 | Critical | 影响系统稳定性/数据安全/不可忽视 | 当前 Sprint |
| 🟡 P1 | Important | 影响开发效率/可维护性/扩展性 | 下个 Sprint |
| 🟢 P2 | Nice-to-have | 代码优雅性/文档完善 | 排期外 |

### 分类模板

```markdown
### #{序号} — {问题标题} (严重度)

**严重程度:** 🔴 P0 / 🟡 P1 / 🟢 P2
**位置:** 文件:行号
**代码片段:**
```python
# 问题代码
```
**影响分析:**
- 直接影响: ...
- 技术债务: ...
- 修复成本: ~X 小时
**预期修复:**
- ...
```

---

## Phase 3: 成本收益排序

### 修复优先级矩阵

```
                   高收益
                     │
        P1 高成本高收益     P0 低成本高收益
         │                 │
   高成本 ──────────────┼────────────── 低成本
         │                 │
        P2 高成本低收益     P1 低成本低收益
         │                 │
                    低收益
```

| 优先级 | 特征 | 举例 | 建议行动 |
|:---:|:---|:---|:---:|
| 🏆 **立即** | 低成本 + 高收益 | HTTP 架构修复 (0.5h) | 当前 Sprint 必做 |
| 📋 **安排** | 高成本 + 高收益 | 测试覆盖增强 (2d) | 规划到下个 Sprint |
| ⏳ **远期** | 低成本 + 低收益 | 魔法数字命名化 (0.5h) | 排入技术债 Sprint |
| ❌ **暂缓** | 高成本 + 低收益 | CLI/Daemon 完全解耦 (3d) | v2.1+ 考虑 |

### 估算方法

| 类型 | 估时 | 精度 |
|:---|:---:|:---:|
| 单文件修复 (如 except:pass) | 0.5-1h | 🟢 准 |
| 模块级重构 (如 HTTP 服务器) | 1-3h | 🟡 估 |
| 测试覆盖 (无测试模块) | 2-4h/模块 | 🟡 估 |
| 跨模块架构重构 | 3-8h | 🔴 粗估 |

---

## Phase 4: 纳入迭代规划

### 最佳实践：功能开发与技术债修复并行

```
Sprint 规划原则:
  每个 Sprint = 60-70% 功能 Story + 30-40% 技术债 Story
  🔴 P0 技术债 → 和 🔴 P0 功能一样优先
  🟡 P1 技术债 → 穿插在功能 Sprint 之间
  🟢 P2 技术债 → 单独的技术债 Sprint
```

### 技术债 Story 模板

```markdown
### Story N: {标题} (SRA-003-XX)

> **作为** {角色}
> **我希望** {期望行为}
> **以便** {业务价值}

**问题背景：** {触发此 Story 的现实问题}

**验收标准：**
- [ ] {关键验收点 1}
- [ ] {关键验收点 2}
- [ ] 新增: tests/{测试文件}

**实现文件：**
- 修改: {文件路径}（{改动说明}）
- 新增: {文件路径}
```

---

## 完整执行检查清单

### 分析前
- [ ] 获取完整文件清单 + 行数
- [ ] 识别所有入口点和核心模块
- [ ] 明确分析边界（哪些目录/文件在范围内）

### 分析中
- [ ] 架构层：模块依赖、设计模式、并发安全
- [ ] 代码层：except:pass、魔法数字、类型标注、日志
- [ ] 测试层：覆盖缺口、死代码、Fixture 依赖
- [ ] 文档层：README、CHANGELOG、架构图

### 分析后
- [ ] 按 4 维度分类所有问题
- [ ] 标注 3 级严重程度
- [ ] 成本收益排序
- [ ] 集成到 Epic 迭代规划
- [ ] 生成分析报告文档（`docs/TECHDEBT-ANALYSIS.md`）
