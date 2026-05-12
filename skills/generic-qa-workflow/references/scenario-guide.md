# 通用 QA 场景指南

> 4 种常见开发场景的 QA 执行路径

---

## 场景 1: 快速修 Bug

**变更类型**: bugfix
**QA 门禁**: L0 + L1

```text
时间线:
  [0:00] L0: ruff check . → 确认 lint 通过
  [0:01] L0: ast.parse → 确认语法兼容
  [0:02] L1: pytest tests/ -q → 全量通过
  [0:04] ✅ 完成，提交

常见陷阱:
  - 修 Bug 时引入了新的 lint 问题 → L0 阻断
  - 修 Bug 破坏了已有测试 → L1 阻断
```

## 场景 2: 新增功能

**变更类型**: feature
**QA 门禁**: L0 + L1 + L2

```text
时间线:
  [0:00] L0: ruff + syntax + mypy
  [0:03] L1: pytest tests/ -q (需新测试通过)
  [0:08] L2: pytest tests/test_api*.py tests/test_cli*.py -q
  [0:12] ✅ 完成，提交/提 PR

关键检查:
  - 新功能是否有对应的单元测试？（L1 屏障）
  - 是否涉及外部接口？→ 必须跑 L2
  - 是否影响现有 API 契约？→ 检查 test_contract*.py
```

## 场景 3: 架构重构

**变更类型**: arch
**QA 门禁**: L0 + L1 + L2 + L3

```text
时间线:
  [0:00] L0: ruff + syntax + mypy
  [0:05] L1: pytest tests/ -q (全量)
  [0:15] L2: pytest tests/test_api* test_cli* test_contract* -q
  [0:20] L3: 并发测试 + 跨版本 (tox/nox)
  [0:30] ✅ 完成

风险控制:
  - 架构变更容易引入竞态 → L3 并发测试必跑
  - 跨版本兼容性可能断裂 → L3 tox 必跑
  - 重构不改外部行为 → L0 应零新增错误
```

## 场景 4: 版本发布

**变更类型**: release
**QA 门禁**: L0 + L1 + L2 + L3 + L4

```text
时间线:
  [0:00] 确保 CI 主分支绿
  [0:05] L0-L3 全量（同上架构重构）
  [0:25] L4-1: 检查版本号对齐 git tag
  [0:26] L4-2: 检查 CHANGELOG 有当前版本
  [0:28] L4-3: python -m build → 确认构建
  [0:30] L4-4: 冒烟测试
  [0:32] L4-5: gh run list 确认 CI 绿
  [0:35] git tag + push → 发布

发布清单:
  - [ ] 版本号与 git tag 一致
  - [ ] CHANGELOG 已更新当前版本
  - [ ] build 生成 wheel + sdist
  - [ ] 冒烟测试通过
  - [ ] CI 主分支全绿
  - [ ] 已知 flaky 已记录
  - [ ] 依赖项无已知漏洞（如有 safety/bandit 配置）
```
