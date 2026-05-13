# pre_flight v2.0 — SDD 门禁集成架构

> **更新**: 2026-05-13 — SDD 状态机 + 门禁脚本正式上线

## 架构概览

```
pre_flight.py v2.0 (Gate 1→2→3 顺序执行)
  │
  ├── Gate 1: 学习状态检查
  │   └── learning_state.json
  │
  ├── Gate 2: SDD 门禁 (本文件)
  │   ├── 检测是否为复杂任务（关键词匹配）
  │   ├── 是 → 调用 spec-gate.py check "<task>"
  │   │   ├── PASS → Story 存在且状态允许开发
  │   │   └── BLOCKED → 无 Story / 状态不允许
  │   └── 否 → 简单任务，跳过
  │
  └── Gate 3: 技能/包操作检测
      ├── 检测 skill 操作 → 自动跑 dependency-scan --target
      └── 检测 cap-pack 操作 → 引导使用 pack 工具链
```

## 三类任务的门禁行为

| 任务类型 | Gate 1 | Gate 2 | Gate 3 | 结果 |
|:---------|:------:|:------:|:------:|:-----|
| "修复错别字" | ✅ | ✅ 跳过 | ✅ 无 | ✅ PASS |
| "实现新功能" | ✅ | ❌ SDD拦截 | ✅ 无 | ❌ BLOCKED |
| "更新skill" | ✅ | ✅ 跳过(技能操作) | ✅ 提示加载 | ✅ PASS |
| "提取能力包" | ✅ | ❌ SDD拦截 | ✅ 提示工具链 | ❌ BLOCKED |

## 关键文件

| 文件 | 作用 |
|:-----|:------|
| `~/.hermes/scripts/pre_flight.py` | 通用守门员入口 v2.0 |
| `~/.hermes/skills/sdd-workflow/scripts/spec-state.py` | SDD 9 状态状态机 |
| `~/.hermes/skills/sdd-workflow/scripts/spec-gate.py` | SDD 门禁检查器 |
| `~/.hermes/sdd_state.json` | SDD 状态持久化 |
| `~/.hermes/AGENTS.md` | 工作流规则 v2.0 |

## 实操例子

```bash
# 当 pre_flight 报 SDD BLOCKED 时：

# 1. 创建 Story
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py create "CAP-001" "能力包格式设计"

# 2. 创建文档（用模板）
# 模板路径: ~/.hermes/skills/sdd-workflow/templates/story-template.md

# 3. 提交审阅
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py submit "CAP-001"

# 4. 等主人批准
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py approve "CAP-001"

# 5. 走三段式实现
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py architect "CAP-001"
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py plan "CAP-001"
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py implement "CAP-001"
# ... 开发 ...
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py complete "CAP-001"
python3 ~/.hermes/skills/sdd-workflow/scripts/spec-state.py archive "CAP-001"
```
