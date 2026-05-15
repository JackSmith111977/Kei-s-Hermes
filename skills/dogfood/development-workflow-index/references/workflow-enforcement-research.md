# Workflow Enforcement Research — 业界方案汇总

> **来源**: 2026-05-14 深度研究，基于论文 + 主流实践检索
> **问题**: AI Agent 在开发中跳过工作流阶段（凭感觉开发），门禁系统失效
> **核心矛盾**: 现有门禁是「拉模式」(pull)——依赖 agent 自觉调用；业界方案转向「推模式」(push)——执行前自动拦截

---

## 方案对比总表

| 方案 | 类型 | 核心机制 | 防绕过强度 | 实现成本 |
|:-----|:-----|:---------|:----------:|:--------:|
| **ToolGuards** (IBM EMNLP 2025) | 论文 | Policy→Guard code→Pre-tool hook | 🟢 强 | 🔴 高 |
| **MI9** (arXiv 2508.03858) | 论文 | FSM conformance + drift detection | 🟢 强 | 🔴 高 |
| **ILION** (arXiv 2603.13247) | 论文 | 5-stage deterministic gate | 🟢 强 | 🟡 中 |
| **Authenticated Workflows** (arXiv 2602.10465) | 论文 | PEP + MAPL + 密码学 | 🟢 强 | 🔴 高 |
| **Claude Code Hooks** (SmartScope) | 工程实践 | Pre-tool hook + approved flags | 🟡 中 | 🟢 低 |
| **govctl** | 工程实践 | CLI gate + phase markers | 🟡 中 | 🟢 低 |
| **SpecGuard** (Node.js) | 工程实践 | Validator script + step order | 🟡 中 | 🟢 低 |
| **Codex Hooks** | 工程实践 | Pre-commit guard + evidence | 🟡 中 | 🟢 低 |
| **Phase Markers** (Hermes 当前方案) | 文件系统 | .phase/ 文件 + pre_flight 路径检测 | 🟡 中 | 🟢 低 |

---

## 模式 1: Pre-Tool Hooks（执行前拦截）

**代表作**: IBM ToolGuards · Claude Code Hooks · Codex hooks.json

```
agent 调用 tool
    ↓
Pre-Tool Hook 触发
  ├── 读取当前 phase 状态（从文件/环境变量）
  ├── 与「此 phase 允许的操作」对比
  ├── ALLOW → 放行
  └── BLOCK → 返回错误信息，agent 必须自省
```

**IBM ToolGuards** (EMNLP 2025):
- 两阶段：offline 编译 policy 文档 → guard code；runtime 在 tool invocation 前执行
- 每个 tool 有独立的 `guard_tool()` 函数
- 验证失败 → agent 被提示 self-reflect 后重试
- 论文评估：22/50 τ-bench Airlines 任务中有 policy violation，ToolGuards 全部拦截

**Claude Code Hooks** (SmartScope 实践):
- `.claude/hooks.json` 中定义 PreToolUse 规则
- Edit/Write 操作前跑 gatekeeper 脚本检查 `.approved` 文件
- `fail_on_error: true` 使其成为硬阻断
- 缺点：只能检查文件存在性，不能检查 phase 合法性

---

## 模式 2: 文件级 Phase Markers

**代表作**: govctl · SmartScope · Codex STRATEGY.md

**核心理念**: 所有状态存储在文件系统中，agent 读文件而非记忆

```text
.phase/EPIC-004/SPEC-4-3/
├── status              ← 当前阶段: spec_approved | dev_in_progress | ...
├── gates/
│   ├── spec_approval   ← 门禁结果
│   └── tdd_pass
└── history.log
```

**govctl** 模式:
- 所有 artifact 是 TOML 文件，存储在 `gov/` 目录
- CLI 命令 `govctl rfc advance` 推进阶段
- `govctl check` 在 session 结束前跑 gate
- 核心哲学：「文件即 API」— 状态存储在文件系统而非 agent 记忆

---

## 模式 3: FSM Conformance Engine（运行时状态机）

**代表作**: MI9 · Bayseian blog · Authenticated Workflows

```python
# FSM 引擎伪代码
engine = FSMEngine()
engine.set_initial_state('spec_approved')
engine.allowed_actions('spec_approved') = ['read_file', 'write_file(docs/*)']
engine.allowed_actions('dev_in_progress') = ['read_file', 'write_file(src/*)', 'terminal(pytest)']

# 每次 tool call 前检查
def before_tool_call(tool_name, args):
    current_state = engine.current_state
    allowed = engine.allowed_actions(current_state)
    action = f"{tool_name}({args.get('path','')})"
    if not allowed.match(action):
        return BLOCK(f"当前状态 {current_state} 不允许 {action}")
    return ALLOW
```

**Bayseian** 的核心理念：
- 引擎跑在 agent *外部* — 「orchestration runs around agents, not through them」
- 两阶段 review gate：Stage 1 确定性检查（文件存在/字段完整）→ Stage 2 Critic agent（判断式）
- 评估基于产物文件，而非对话回复

---

## 当前 Hermes 差距分析

| 需求 | 业界方案 | Hermes 现状 | 差距 |
|:-----|:---------|:-----------|:-----|
| 执行前阻断工具调用 | ToolGuards, Claude Hooks | ❌ 无 hooks 系统 | 需要 pre_flight 路径检测增强 |
| 阶段状态持久化 | govctl, Phase Markers | ⚠️ chain-state.json 已创建，但未被工具调用检查 | 需要 pre_flight 自动读取 |
| 运行时 FSM | MI9, Bayseian | ❌ 无运行时引擎 | 架构级投入 |
| post-step 验证 | SpecGuard validator | ⚠️ chain-gate.py 已创建但需手动调用 | 需要 pre_flight 自动触发 |

### 最可行的改进路径（按成本排序）

1. **🟢 低**: Phase Markers + pre_flight 路径检测 — 在 pre_flight.py 中检查当前操作文件路径是否匹配当前 phase 允许的路径集合
2. **🟡 中**: SRA 阈值调整 — 降低 THRESHOLD_WEAK 或为延续类关键词加 boost
3. **🔴 高**: FSM Engine — 构建运行时状态机包装工具调用

---

## 参考文献

- Nakash et al. (2025). "ToolGuards: End-to-End Pipeline for Proactive Policy Enforcement in Agentic Flows". EMNLP 2025 Industry Track.
- Wang et al. (2025). "MI9: An Integrated Runtime Governance Framework for Agentic AI". arXiv:2508.03858.
- ILION (2026). "Deterministic Execution Gate for Agentic AI Systems". arXiv:2603.13247.
- Authenticated Workflows (2026). "A Systems Approach to Protecting Agentic AI". arXiv:2602.10465.
- SmartScope (2025). "Enforcing Spec-Driven on AI Agents". https://smartscope.blog
- govctl (2025-2026). "Governance-as-code for AI-assisted development". https://github.com/govctl-org/govctl
- Bayseian (2026). "Why Your AI Coding Agent Keeps Going Off-Script". https://www.bayseian.com/blog
- SpecGuard (2026). "I Built a Spec-Driven Workflow for AI Agents". https://medium.com
