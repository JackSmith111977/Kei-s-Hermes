# 通用开发工作流场景指南

> 关联: `generic-dev-workflow` SKILL.md

---

## 场景 1: 新功能开发（最常用）

```text
主人：「实现一个批量导出功能」

Step 1: 需求确认
  「要导出什么格式？CSV/Excel？数据量有多大？触发方式是什么？」

Step 2: 环境检查
  git log --oneline -5
  pytest --collect-only -q | tail -1

Step 3: 实施计划
  Task 1: 写 test_export_csv → 验证: pytest -k export
  Task 2: 实现 export_csv() → 验证: pytest -k export
  Task 3: 集成到 API 端点 → 验证: curl POST /api/export

Step 4: TDD 逐个 Task
Step 5: pytest -q 全量测试
Step 6: self-review 场景 F
Step 7: doc-alignment → commit-quality-check → git commit
```

## 场景 2: 修 Bug

```text
主人：「登录接口报 500」

→ 先走调试路径（development-workflow-index §5 或 systematic-debugging）
→ 找到根因后再加载本 skill 走修复流程

Step 1: 确认修复范围（只修根因，不 scope creep）
Step 2: 环境检查（确认当前基线）
Step 3: Task 1: 写重现 Bug 的测试 → 验证: 测试失败
         Task 2: 修代码 → 验证: 测试通过
Step 4-7: 同上
```

## 场景 3: 重构

```text
主人：「重构 daemon.py，拆分职责」

→ 先走审查路径（development-workflow-index §6 做代码分析）
→ 确认重构方案后再加载本 skill

Step 1: 确认重构范围（拆成几个文件？接口是否变？）
Step 2: 基线测试 + 确认无 pending 变更
Step 3: 按文件拆分 Task，每个 2-5 分钟
Step 4-7: 同上（注意：重构的测试是「行为不变」的验证）
```

## 场景 4: 快速修复（≤3 文件）

```text
主人：「把这个按钮颜色改掉」

Step 1: 确认新颜色值
Step 2: 跳过（简单不查环境）
Step 3: 直接改
Step 5: pytest -q 确保不炸
Step 6: 肉眼确认改了
Step 7: git commit
```

## 关键原则

| # | 原则 | 说明 |
|:-:|:-----|:------|
| 1 | Step 1-7 顺序固定 | 不要跳过需求确认直接写代码 |
| 2 | 基线对比 | 测试数不应低于基线，stash 做 baseline |
| 3 | 原子提交 | 每个 Task 独立 commit，可 revert |
| 4 | self-review 不可跳过 | 汇报前必须自检 |

## 铁律速查

- 🔴 没有测试不准写代码
- 🔴 没有自检不准汇报
- 🔴 代码改了文档必须同步
- 🔴 每个 Task ≤ 5 分钟
