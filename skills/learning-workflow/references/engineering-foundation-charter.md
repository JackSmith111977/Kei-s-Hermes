# Engineering Foundation Charter (EFC) — 工程化基础建设工作流

> **适用场景:** 对现有代码库进行重大迭代前，先建立完整的工程化基础
> **核心原则:** 「先规范，后开发」— 不打好地基不建楼
> **来源实践:** SRA v2.0 EPIC-003 前置工程化整改 (2026-05-10)

---

## 为什么需要 EFC？

在进入功能开发前，代码库通常存在以下问题：

| 问题 | 如果没有 EFC | 有 EFC 后 |
|:---|:---|:---|
| 架构不清晰 | 开发到一半发现模块职责耦合 | 提前解耦，分工明确 |
| 技术债累积 | 新功能在坏代码上叠加 | 先还债再添新功能 |
| 无API规范 | 接口设计不一致，反复改 | 一次设计好，调用者明确 |
| 无测试覆盖 | 改一处崩一片 | 有测试兜底，放心改 |
| 无版本规约 | 依赖版本冲突 | 统一基线，避免兼容问题 |

---

## EFC 双阶段流程

```
┌─────────────────────────────────────────────────────────┐
│  Phase 1: 深度分析 + 标准制定 (Analysis & Standards)    │
├─────────────────────────────────────────────────────────┤
│  Step 1.1: 代码库全景扫描                                │
│  Step 1.2: 模块依赖分析                                  │
│  Step 1.3: 技术债识别与分级                               │
│  Step 1.4: 架构标准定义（分层/职责/通信/模式）               │
│  Step 1.5: 技术版本规约（Python/依赖/工具链/兼容性）         │
├─────────────────────────────────────────────────────────┤
│  Phase 2: 深度学习 + 规范建立 (Learning & Standards)     │
├─────────────────────────────────────────────────────────┤
│  Step 2.1: 核心技术栈深度学习（使用 learning-workflow）    │
│  Step 2.2: API 参考文档编写                               │
│  Step 2.3: 编码规范/测试规范/文档规范制定                    │
│  Step 2.4: Git 规范 / PR 审查清单制定                      │
│  Step 2.5: 产出物完整性验证                                │
├─────────────────────────────────────────────────────────┤
│  → GATE: 所有文档就绪、规范发布 → 进入开发                  │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1 关键步骤

### 1.1 代码库全景扫描

```bash
# 项目结构
find . -type f -name "*.py" | grep -v __pycache__ | sort

# 文件行数统计
find . -name "*.py" -not -path "./.git/*" -exec wc -l {} + | sort -n

# 模块依赖分析
python3 -c "
import ast, os
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path) as fh:
                tree = ast.parse(fh.read())
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
            print(f'{os.path.relpath(path)}: {sorted(imports)}')
"
```

### 1.2 技术债识别清单

| 检查项 | 检查方法 | 严重程度依据 |
|:---|:---|:---:|
| `except: pass` | `grep -rn "except:" --include="*.py" \| grep -v ".git/"` | 🔴 隐藏错误 |
| 魔法数字 | 搜索 hardcoded numeric values in scoring/comparison | 🟡 维护困难 |
| 缺少类型标注 | AST 扫描函数定义 | 🟡 可读性低 |
| 测试覆盖率 | 对比源模块 vs 测试文件 | 🔴 回归风险 |
| 模块行数过大 | `wc -l` 超过 500 行 | 🟡 职责过重 |
| 线程安全 | 检查无锁的共享状态读写 | 🟡 数据竞争 |
| 配置硬编码 | 检查 hardcoded paths / magic strings | 🟢 可配置性差 |

### 1.3 架构标准文档模板

```markdown
# {Project} 架构标准

## 1. 架构总览（ASCII 架构图）
## 2. 分层职责（Layer 1/2/3）
## 3. 模块边界与通信协议
## 4. 设计模式约定（已使用 + 禁止的反模式）
## 5. 错误处理规范（异常层级 + 级别）
## 6. 配置规范（层级 + schema）
## 7. 并发与安全策略
## 8. 模块演化规则
```

### 1.4 版本规约文档模板

```markdown
# {Project} 技术版本规约

## 1. 版本策略（SemVer + 分支策略）
## 2. 运行环境版本（Python / Node 等）
## 3. 依赖管理（核心/开发/可选 + 铁律）
## 4. 工具链版本
## 5. 兼容性策略（API/数据格式/HTTP）
## 6. 发布流程（检查清单 + 版本号速查）
```

---

## Phase 2 关键步骤

### 2.1 API 参考文档模板

```markdown
# {Project} API 参考

## 1. HTTP API（端点/参数/响应/状态码）
## 2. Socket / RPC API（协议/动作/示例）
## 3. CLI 命令（管理/查询/配置）
## 4. Python / SDK API（类/方法/参数）
## 5. 内部模块 API
## 6. 错误码大全
```

### 2.2 技术规范文档模板（CONTRIBUTING.md）

```markdown
# 贡献指南

## 编码规范
- 命名约定（类/函数/常量/变量）
- 类型标注要求
- 异常处理铁律
- 魔法数字禁令
- 日志/dotstring 规范

## 测试规范
- 测试类型（单元/集成/覆盖率/基准）
- 覆盖率目标
- 编写方法（tmp_path / monkeypatch）
- 命名规范

## 文档规范
- 文件体系（README/ARCHITECTURE/API/CHANGELOG）
- 更新规则

## Git 规范
- Conventional Commits 格式
- 分支命名
- PR 审查清单
```

### 2.3 深度循环学习技巧

当 Phase 2 需要学习项目涉及的技术栈时：

1. **优先读源码** — 项目的代码本身就是最好的学习材料
2. **外部资料补充** — 只针对不熟悉的技术栈联网搜索
3. **学完即输出** — 每学一个模块，立即输出到 API 参考或技术规范
4. **循环递进** — 第 1 轮广度（所有模块概览）→ 第 2 轮深度（每个模块细节）→ 第 3 轮精炼（交叉验证一致性）

---

## 🚨 质量门禁

在进入开发前，必须通过以下检查：

| 检查项 | 通过标准 |
|:---|:---|
| 架构文档 | 定义了分层、模块职责、通信协议、设计模式 |
| 版本规约 | 明确了版本策略、依赖管理、兼容性 |
| API 参考 | 覆盖所有对外接口（HTTP/Socket/CLI/Python） |
| 技术规范 | 编码/测试/文档/Git 规范完整 |
| 技术债基线 | P0 问题已修复或已规划修复路径 |
| 产出一致性 | 文档内容与代码库实际结构一致 |

---

## 产出物清单

| 文件 | 必需？ | 说明 |
|:---|:---:|:---|
| `docs/ARCHITECTURE.md` | ✅ | 架构标准 |
| `docs/VERSIONING.md` | ✅ | 版本规约 |
| `docs/API-REFERENCE.md` | ✅ | API 参考 |
| `docs/TECHDEBT-ANALYSIS.md` | ✅ | 技术债分析 |
| `CONTRIBUTING.md` | ✅ | 技术规范 |
| `CHANGELOG.md` | ✅ | 已更新 |

---

> **本工作流与 learning-workflow 的关系：**
> - EFC 的 **Phase 1** 对应 learning-workflow 的「深度分析」模式
> - EFC 的 **Phase 2** 对应 learning-workflow 的「深度循环学习」模式（L2 深度挖掘）
> - 整体是 learning-workflow 在「工程准备」场景下的特化应用
