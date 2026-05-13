# Spec 分解实战案例：CAP Pack 适配器方案 (SPEC-004)

> **来源**: 2026-05-13 会话 — 主人要求「开始分解story并计划实施流程」
> **关联 Spec**: [SPEC-004-adaptation.md](../../docs/SPEC-004-adaptation.md)（跨 Agent 适配层方案）

---

## 1. 输入：SPEC-004 的 6 个验收标准

| AC# | 描述 | 优先级 |
|:---:|:-----|:------:|
| AC-1 | AgentAdapter Protocol 可被 3 个适配器实现 | P0 |
| AC-2 | Hermes 适配器可完整安装/卸载/更新能力包 | P0 |
| AC-3 | Claude Code 适配器可安装技能和 MCP 配置 | P1 |
| AC-4 | Codex CLI 适配器可使用 rules 系统加载技能 | P1 |
| AC-5 | 能力对等性测试可至少覆盖 Hermes 和 Codex CLI | P1 |
| AC-6 | 第三方适配器集成文档可指引新适配器开发 | P2 |

---

## 2. 分解过程

### Step 1: AC 提取 → Story 映射

| AC | 建议 Story | 理由 |
|:---|:-----------|:------|
| AC-1 | S-018 uca-core | 定义 `AgentAdapter` Protocol + pack_parser + verifier |
| AC-1 | S-019 uca-cli | `cap-pack` CLI（install/remove/verify/list） |
| AC-2 | S-020 hermes-adapter | Hermes 适配器（skill 安装 + MCP 注入 + verify） |
| AC-2 | S-021 hermes-rollback | 快照/回滚/状态报告（AC-2 的可靠性保障） |
| AC-3 | S-022 claude-adapter | Claude Code 适配器 |
| AC-4 | S-023 codex-adapter | Codex CLI 适配器 |
| AC-5 | S-024 parity-testing | 跨 Agent 对等性测试 |
| AC-6 | S-025 dev-docs | 第三方适配器开发指南 |

### Step 2: AC 聚类 → Phase 分组

按依赖关系聚类：

```
Phase 0: UCA Core (S-018, S-019)
  → 没有 UCA Core，任何适配器都无法工作
  → 出口门禁：uca-core 单元测试全绿 + CLI 可用

Phase 1: Hermes 适配器 (S-020, S-021)
  → 依赖 Phase 0（使用 AgentAdapter Protocol）
  → 出口门禁：doc-engine pack 可完整 install/verify/remove 循环

Phase 2: 扩展适配器 (S-022, S-023)
  → 依赖 Phase 0（使用 AgentAdapter Protocol）
  → 可并行于 Phase 1（独立于 Hermes 细节）
  → 出口门禁：3 个适配器均可安装同一 pack

Phase 2.5: 质量保障 (S-024, S-025)
  → 依赖前序 Phase（需要所有适配器就绪）
  → 出口门禁：SPEC-004 全部 6 个 AC 通过
```

### Step 3: 架构蓝图

```
scripts/
├── __init__.py
├── uca/                          ← UCA Core (Phase 0)
│   ├── __init__.py
│   ├── protocol.py               ← AgentAdapter Protocol
│   ├── parser.py                 ← cap-pack.yaml 解析器
│   ├── dependency.py             ← 依赖检查
│   └── verifier.py               ← 安装后验证器
├── adapters/                     ← 各 Agent 适配器 (Phase 1+2)
│   ├── __init__.py
│   ├── base.py                   ← BaseAdapter（共享逻辑）
│   ├── hermes.py                 ← Hermes 适配器
│   ├── claude_code.py            ← Claude Code 适配器
│   └── codex.py                  ← Codex CLI 适配器
├── cli/
│   └── main.py                   ← cap-pack CLI (Phase 0)
└── tests/
    ├── test_uca_parser.py
    ├── test_hermes_adapter.py
    ├── test_claude_adapter.py
    ├── test_codex_adapter.py
    └── test_parity.py
```

### Step 4: Story 生成

每个 Story 按标准模板生成（含用户故事 + AC + 技术方案 + 不做的范围 + 引用链）。

**示例：S-018 uca-core**

```yaml
story: S-018
title: UCA Core — AgentAdapter Protocol + 解析器 + 验证器
priority: P0
dependencies: []
```

| 字段 | 内容 |
|:-----|:------|
| **用户故事** | As a 适配器开发者, I want 一个清晰的 `AgentAdapter` Protocol + CapPack 解析器, So that 我可以为不同 Agent 实现适配器而不重复解析逻辑 |
| **AC-1** | `AgentAdapter` Protocol 定义 install/uninstall/update/list_installed/verify 方法 |
| **AC-2** | pack_parser 可正确解析 doc-engine 和 quality-assurance 两个包的 cap-pack.yaml |
| **AC-3** | verifier 可检查安装后文件存在性 |
| **技术方案** | 新建 `uca/` 包，`protocol.py` 用 `typing.Protocol`，`parser.py` 用 `yaml.safe_load` + JSON Schema 验证 |
| **不做的范围** | ❌ 不实现任何具体适配器 ❌ 不实现 CLI |
| **出口门禁** | `pytest tests/test_uca_parser.py` 全绿 |

### Step 5: Phase 排序

```text
Phase 0 ──→ Phase 1 ──→ Phase 2 ──→ Phase 2.5
  S-018       S-020       S-022       S-024
  S-019       S-021       S-023       S-025
                          (可并行 Phase 1)
```

---

## 3. 关键决策记录

| 决策 | 选项 | 选择 | 理由 |
|:-----|:------|:------|:------|
| UCA Core 粒度 | 一个 Story vs 两个 Story | 两个（S-018 Core + S-019 CLI） | CLI 涉及 argparse+6 个子命令，单独验证更清晰 |
| Hermes 适配器拆分 | 一个 Story vs 两个 Story | 两个（S-020 功能 + S-021 回滚） | 回滚逻辑可独立测试，不影响核心功能 |
| Phase 2 并行策略 | 串行 vs 并行 | 可并行于 Phase 1 | Claude 和 Codex 适配器不依赖 Hermes 适配器细节 |
| install-pack.py 处理 | 改造 vs 替代 | 替代（退役 → 由 cap-pack CLI 接管） | 旧脚本没有 Protocol，重构不如重写 |

---

## 4. 分解产物清单

| 类型 | 数量 | 说明 |
|:-----|:----:|:------|
| Story | 8 个 | S-018 ~ S-025 |
| Phase | 4 个 | P0 UCA Core → P1 Hermes → P2 扩展 → P2.5 质量 |
| 门禁 | 4 个 | 每个 Phase 一个出口门禁 |
| 架构蓝图 | 1 个 | 6 个目录/包的完整文件结构 |

---

## 5. 检查清单

- [x] 每个 AC 至少对应一个 Story
- [x] 基础设施（UCA Core）排在最前
- [x] 每个 Phase 有明确的出口门禁
- [x] 架构蓝图在分解时已画出
- [x] 每个 Story 可独立验证
- [x] 依赖关系显式标注（前序 Story）
- [x] 不做的范围明确记录
- [x] 关键决策有 ADR
