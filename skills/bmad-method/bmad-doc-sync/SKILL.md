---
name: bmad-doc-sync
description: 在 BMad 工作流中同步 Epics/Stories 文档与实际实现。检测并修复文档漂移——避免"文档说A，代码做B"的不一致状态。
version: 1.0.0
triggers:
- 同步文档
- 文档漂移
- 文档不一致
- doc sync
- implementation drift
- 文档审计
- sync docs
- 更新文档
- 提交仓库
author: Emma (小喵)
license: MIT
metadata:
  hermes:
    tags:
    - bmad-method
    - documentation
    - epic
    - story
    - sync
    - implementation-drift
    category: bmad-method
    skill_type: workflow
    design_pattern: verification
---

# BMad Doc Sync — 文档-实现一致性校验

> **在 BMad 工作流的每个实现阶段结束后，自动审计 Epics/Stories 文档是否与实际实现一致。**

## 为什么需要这个 skill？

BMad 的工作流是：`Epic → Story → Task → Implementation → Delivery`

但在实践中，**实现经常偏离原始设计**：
- 原本计划用 Hook 方案，实际用了代码注入
- 原本说 Gateway-only，后来 CLI 也支持了
- patch 文件包含无关改动（weixin.py, image_gen 等）被混入

如果不修复文档，就会出现**文档漂移（Documentation Drift）**：
```
原始设计: Hook 拦截 → agent:start 事件
             ↓  实现后发现 Hook 是非阻塞的，不可行
实际实现: run_agent.py 注入 → run_conversation()
             ↓  但文档没更新，写着 Hook 方案
文档说 A，代码做 B → 下一个开发者大迷惑
```

## 核心模式：三阶校验

每次实现完毕后，按以下三步检查文档一致性：

### Step 1: 检出所有文档文件

```bash
# 列出项目中的文档文件
find docs/ -name "*.md" -type f | sort

# 列出项目的 README 和 CONTRIBUTING 等
ls *.md 2>/dev/null | grep -i -E "readme|contributing|changelog"
```

### Step 2: 对照实现，逐项检查每个文档的"核心断言"

对每个文档文件，问自己这些问题：

**针对 Epic 文档：**
- [ ] 架构图/文字描述与实际实现一致吗？
- [ ] 验收标准中的每项是否都已实际完成？
- [ ] 设计决策的理由是否反映了实际遇到的限制？
- [ ] 状态标记（规划中/进行中/已完成）是否正确？

**针对 Story 文档：**
- [ ] 技术方案描述与实际代码一致吗？
- [ ] 验收标准全部达成且标注为已实现？
- [ ] 如果中途改变了方案，是否记录了原因？
- [ ] 示例代码是否与实际注入的代码匹配？

**针对 README / INTEGRATION 文档：**
- [ ] 安装步骤是否测试过？
- [ ] 架构图是否反映最新状态？
- [ ] FAQ 中的恢复路径是否仍然有效？
- [ ] 环境变量、配置项是否准确？

**针对 Patch 文件：**
- [ ] Patch 是否只包含目标文件的改动？（不要混入无关改动）
- [ ] Patch 能否通过 `patch --dry-run` 验证？
- [ ] Patch 是否基于当前版本生成？（git diff HEAD -- file）

### Step 3: 修复 + 提交

发现不一致后，按优先级修复：

```
高优先级：架构描述、安装步骤、核心 API（影响使用）
中优先级：验收标准状态、代码示例（影响认知）
低优先级：措辞、排版、过时代码注释（影响阅读体验）
```

最后提交时在 commit message 中标注"同步说明文档"。

## 实战经验：常见文档漂移场景

| 场景 | 发现迹象 | 修复方法 |
|------|---------|---------|
| Hook 方案改代码注入 | 文档写 `hooks.emit("agent:start")`，代码里没有 Hook | 全文替换方案描述，更新架构图 |
| 新增支持模式（如 CLI） | 文档只说 "Gateway" | 补充"Gateway + CLI 都能生效" |
| 降级策略变化 | 文档写 A，实际 try/except 走 B | 用实际代码生成降级表 |
| Patch 混入无关改动 | `git diff` 显示多个文件 | 用 `git diff HEAD -- target_file` 重生成 |
| Epic 状态漂移 | 标记"📋 规划中"但代码已实现 | 改为"✅ 已实现"，补充实现版本和日期 |

## Patch 文件最佳实践

### 生成干净的 patch

```bash
# ✅ 正确：只包含 target_file 的改动
git diff HEAD -- run_agent.py > patches/hermes-sra-integration.patch

# ❌ 错误：包含全部工作区改动
git diff HEAD > patches/hermes-sra-integration.patch

# ❌ 错误：包含非目标文件的改动
git diff HEAD -- run_agent.py weixin.py image_gen.py > patch.patch
```

### 验证 patch

```bash
# 在干净副本上 dry-run 验证
cd /tmp
git clone file:///path/to/original/repo test-verify
cd test-verify
git checkout -- run_agent.py
patch --dry-run -p1 < /path/to/patch.patch
# → "checking file run_agent.py" ✅
# → "Hunk #1 FAILED" ❌（需要重新生成）
```

## 扩展阅读

- [`references/operational-reliability-story-pattern.md`](references/operational-reliability-story-pattern.md) — 从运行时观察发现可靠性问题后，编写 BMAD Story 并追加到 Epic 的完整模式。包含模板、案例（SRA-003-12）和与需求驱动 Story 的差异对比。

## 检查清单

提交前最后确认：

- [ ] 所有文档的状态标记与实现一致
- [ ] 架构图/流程图描述准确
- [ ] 代码示例与实际代码匹配
- [ ] FAQ/降级表格反映真实行为
- [ ] Patch 文件只包含目标改动
- [ ] Patch 通过 `--dry-run` 验证
- [ ] 38/38 测试通过（或对应项目全部测试通过）
- [ ] commit message 包含"同步说明文档"标记
