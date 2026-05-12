# AC 审计方法论 — Epic 文档验收标准同步指南

> 来源: SRA EPIC-003 文档对齐实战 (2026-05-12)
> 问题: 文档声称完成度 ~40%，代码实际 ~95% — 55% 的漂移

---

## 一、五层根因模型

文档-代码不同步的深层原因，从表层到根源：

```
L5: 哲学层 — 「完成」定义不一致
    代码完成 ≠ 文档完成 ≠ 所有 AC 通过
     
L4: 门禁层 — 无 AC 完成率自动化检查
    CI 不检查「文档声称的完成度 vs 代码实际完成度」
    doc-alignment --verify 只检查版本号和测试数，不检查 Story AC
    
L3: 流程层 — AC 更新未纳入 Definition of Done
    Story 完成的 checklist 中没有「更新 Epic AC」这一项
    Spec 生命周期（sdd-workflow）与 Epic 文档脱节
    
L2: 工具层 — Epic 文档 AC 是静态 markdown，无版本追踪
    无法知道「这个 AC 是何时过时的」
    没有 AC 完成率的量化指标
    
L1: 行为层 — 开发者只关注代码，不更新文档
    功能实现提交 vs 文档提交在 git 历史中分离
    合并 PR 时没有强制检查文档同步
```

---

## 二、AC 审计脚本：ac-audit.py

项目级脚本，放在项目根目录的 `scripts/ac-audit.py`。

### 三种模式

| 模式 | 命令 | 功能 |
|:-----|:------|:------|
| **check** | `python3 scripts/ac-audit.py check <epic_file>` | 分析 AC 完成率，检测代码已实现但文档未勾选的项 |
| **sync** | `python3 scripts/ac-audit.py sync <epic_file> --apply` | 自动勾选可验证的 AC（文件/函数/测试/CLI/端点存在性） |
| **dashboard** | `python3 scripts/ac-audit.py dashboard <epic_file>` | 输出 Story 维度完成率表格 |

### 可自动验证的 AC 类型

| 验证器 | AC 文本模式 | 验证方式 |
|:-------|:------------|:---------|
| 文件存在 | "创建了 XX.py""新增 XX 文件" | `os.path.exists` + glob 递归 |
| 函数存在 | "XX() 方法" | `grep "def XX" *.py` |
| CLI 命令 | "sra xx CLI 命令" | `grep "cmd_xx" cli.py` |
| 测试存在 | "测试 test_xx.py" | `os.path.exists tests/test_xx.py` |
| 端点存在 | "GET/POST /xx 端点" | `grep "/xx" daemon.py` |
| 目录存在 | "创建了 XX 目录" | `os.path.isdir` |
| Import 存在 | "from X import Y" | `grep "from X import Y" *.py` |

---

## 三、三重加固工作流

防止文档漂移复发，需要自动化工具 + 流程门禁 + 行为规范三层同时加固：

### 层 1: 自动化工具 (ac-audit.py)

每次 Story 完成后：
```bash
python3 scripts/ac-audit.py check docs/EPIC-*.md   # 检查漂移
python3 scripts/ac-audit.py sync docs/EPIC-*.md --apply  # 同步 AC
python3 scripts/ac-audit.py dashboard docs/EPIC-*.md  # 确认完成率
```

### 层 2: 流程门禁 (DoD 纳入)

在开发工作流的 Phase 3 (提交前对齐) 中新增 AC 审计步骤：
```
Phase 3: 提交前对齐
  ├── 🎯 AC 审计 ← 新增
  │   ├── 运行 python3 scripts/ac-audit.py check docs/EPIC-*.md
  │   ├── 检查是否有「代码已实现但文档未勾选」的 AC
  │   ├── 如有 → 勾选
  │   └── 确认 dashboard 显示 100%
  ├── doc-alignment 5步协议
  ├── project-report.json + HTML 更新
  └── ...
```

### 层 3: 行为规范 (铁律)

- **铁律 #6**: Story 完成时自动同步 Epic AC — Story Spec 完成 → 运行 ac-audit sync 更新 Epic 文档中对应 AC
- Sprint 结束检查清单中新增「AC 审计」项

---

## 四、常见 AC 模式与验证

### AC 文本中的可验证信号

当阅读 Epic 文档中的验收标准时，以下文本模式代表可自动验证：

| 信号词 | 示例 | 可验证 |
|:-------|:------|:------:|
| "创建/新增/添加" + 文件路径 | "创建 `scripts/ac-audit.py`" | ✅ 文件存在 |
| "增加" + 函数名 + "方法" | "增加 `record_skip()` 方法" | ✅ grep 函数定义 |
| "`cmd_xxx`" + CLI | "`sra compliance` CLI 命令" | ✅ grep 命令注册 |
| "测试" + test_*.py | "测试 `test_singleton.py`" | ✅ 测试文件存在 |
| "`GET/POST /xxx`" | "`GET /stats/compliance`" | ✅ 路由注册 |
| "`from X import Y`" | "`from ..skill_map import ...`" | ✅ 模块导入存在 |

### 不可自动验证的 AC（需人工判断）

- 非阻塞设计 / 优雅降级 / 可配置性
- 某功能「可工作」「行为正确」
- 性能指标（延迟 < 50ms）
- 文档已「同步」「更新」
