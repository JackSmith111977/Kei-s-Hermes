---
name: doc-alignment
description: "文档对齐协议 — 开发流程完成后的文档一致性对齐，防止旧内容污染上下文。每个任务完成后必须运行此协议对齐所有相关文档。"
version: 1.1.0
triggers:
- 文档对齐
- 文档一致性
- 上下文污染
- 文档漂移
- 同步文档
- 文档陈旧
- documentation alignment
- doc drift
- 对齐文档
- 文档更新
- STALE_DOC
- OUTDATED_DOC
author: Emma (小玛)
license: MIT
allowed-tools:
- read_file
- patch
- write_file
- search_files
- terminal
- skill_view
- memory
metadata:
  hermes:
    tags:
    - documentation
    - workflow
    - quality
    - alignment
    category: dogfood
    skill_type: workflow
    design_pattern: protocol
---

# 📋 文档对齐协议 (Documentation Alignment Protocol)

> **防止文档漂移导致的上下文污染。** 每次完成开发工作流（story/sprint/bugfix）后，必须运行此协议。

## 核心问题

```text
代码变更 → 文档未同步 → 下次加载旧文档 → AI 基于错误上下文决策 → 产出质量问题
                              ↑
                         上下文污染！
```

## 触发时机

**强制性：** 每次完成以下操作后 **必须** 执行：

| 操作类型 | 示例 | 对齐优先级 |
|:---------|:-----|:----------:|
| 新增端点 | 添加 HTTP/Socket API | 🔴 立即 |
| 修改 CLI 命令 | 新增/修改 sra 子命令 | 🔴 立即 |
| 完成 Sprint | Sprint 结束交付 | 🔴 立即 |
| 修改核心模块 | advisor/memory/daemon 行为变更 | 🟡 高 |
| Bug 修复 | 修复功能性问题 | 🟡 高 |
| 日常提交 | 一般代码变更 | 🟢 可选 |

## 对齐协议（5 步法）

### Step 1: 识别变更域

回答以下问题，确定哪些文档可能受影响：

```text
1. [ ] 新增/修改了 API 端点？→ API-REFERENCE.md, PROJECT-PANORAMA.html
2. [ ] 新增/修改了 CLI 命令？→ API-REFERENCE.md §3, PROJECT-PANORAMA.html
3. [ ] 修改了核心架构？→ ARCHITECTURE.md, PROJECT-PANORAMA.html
4. [ ] 完成了 Epic Story？→ ROADMAP.md, EPIC-xxx.md
5. [ ] 新增/删除了文件/模块？→ PROJECT-PANORAMA.html 文件树
6. [ ] 修改了测试结构/数量？→ PROJECT-PANORAMA.html 测试章节
7. [ ] 完成了一个 Sprint？→ PROJECT-PANORAMA.html Sprint 历史章节
```

### Step 2: 定位漂移点

对 Step 1 确定的每个文档，执行精确比对：

```bash
# 查找 API-REFERENCE 是否缺少新端点
grep -c "/recheck" docs/API-REFERENCE.md    # 应为 > 0

# 查找 ARCHITECTURE 是否缺少新模块
grep -c "SceneMemory" docs/ARCHITECTURE.md

# 检查 ROADMAP 状态是否正确
grep "pending" ROADMAP.md                   # 确认已完成的不应出现
```

### Step 3: 逐文档对齐

对每个受影响的文档执行：

1. **打开文档** → `read_file`
2. **识别缺失/过时内容** → 与当前代码状态比对
3. **修改文档** → `patch`（精准替换）或 `write_file`（大幅更新）
4. **验证修改** → 重新读取确认修改正确

### Step 4: 跨文档一致性验证

确保多个文档之间信息一致：

| 检查项 | 方法 |
|:-------|:-----|
| API 端点列表 | API-REFERENCE.md §1 vs PROJECT-PANORAMA.html「全部端点」 |
| CLI 命令列表 | API-REFERENCE.md §3 vs PROJECT-PANORAMA.html「CLI 命令」 |
| Story 状态 | ROADMAP.md vs EPIC-xxx.md vs PROJECT-PANORAMA.html「EPIC 状态」 |
| 测试数量 | pytest 计数 vs PROJECT-PANORAMA.html「测试覆盖」 |
| 版本号 | pyproject.toml vs API-REFERENCE.md vs PROJECT-PANORAMA.html |

### Step 5: 提交并标记对齐完成

```bash
# 提交所有文档变更
git add docs/ PROJECT-PANORAMA.html ROADMAP.md
git commit -m "docs: align documentation after [概要]"
```

然后在 AGENTS.md 的 Pre-Flight 步骤中新增检查：

```markdown
## 任务后的强制对齐检查

完成任务后（提交前），**必须**运行 `skill_view(name="doc-alignment")`，
执行 5 步文档对齐协议。跳过此步骤 = FATAL ERROR。
```

## 文档漂移清单

### 高漂移风险文档

| 文档 | 漂移模式 | 检测方法 | 修复频率 |
|:-----|:---------|:---------|:--------:|
| `API-REFERENCE.md` | 端点描述过时 | `grep -c 新端点名` | 每次新增端点 |
| `ROADMAP.md` | Story 状态未更新 | 对比 EPIC 文档 | 每次完成 Story |
| `PROJECT-PANORAMA.html` | 整体过时 | 对比代码状态 | 每个 Sprint |
| `ARCHITECTURE.md` | 模块描述过时 | 检查 import 路径 | 架构变更时 |

### 低漂移风险文档

| 文档 | 说明 |
|:-----|:-----|
| `README.md` | 用户导向，只在发布时更新 |
| `CHANGELOG.md` | 只在版本发布时更新 |
| `CONTRIBUTING.md` | 基本不变 |
| `SECURITY.md` | 基本不变 |

## 典型案例

### 案例 1：新增 API 端点后未同步文档

**场景：** Sprint 2 新增了 `POST /recheck` 和 `GET /stats/compliance`
**漂移：** `API-REFERENCE.md` 完全未包含这两个端点 → 下次加载时 AI 不知道有这些端点
**修复：** 在 API-REFERENCE.md §1 中新增对应小节，更新 Socket §2 和 Python API §4

### 案例 2：Sprint 完成后 Story 状态未更新

**场景：** Sprint 2 完成了 3 个 Story
**漂移：** `ROADMAP.md` 中状态仍为 `pending`
**修复：** 更新 ROADMAP.md 状态为 `completed`，更新 Sprint 标记

## 实战参考

> 本 skill 包含实战参考文件，记录了 SRA 项目 Sprint 2 文档对齐的实操经验。

| 文件 | 内容 | 适用场景 |
|:-----|:-----|:---------|
| `references/sra-drift-detection.md` | 实际漂移检测命令、根因分析、修复流程 | SRA 项目文档对齐 |

## 反模式

- ❌ **「先提交代码，文档以后补」** — 文档永远不会「以后补」
- ❌ **「只更新一个文档就够了」** — 必须跨文档一致性验证
- ❌ **「小改动不需要更新文档」** — 最小的改动也可能产生最大的上下文污染
- ❌ **「文档在另一个 PR 中更新」** — 文档必须与代码在同一提交中

## 实战参考

> 本 skill 包含实战参考文件，记录了 SRA 项目 Sprint 2 文档对齐的实操经验。

| 文件 | 内容 | 适用场景 |
|:-----|:-----|:---------|
| `references/sra-drift-detection.md` | 实际漂移检测命令、根因分析、修复流程 | SRA 项目文档对齐 |

