# 🧬 AKU → Hermes Skill 进化路径 — 实操参考

> **来源**: arXiv:2603.14805 (Knowledge Activation, Mar 2026) 🥇 + arXiv:2604.11623v2 (Context Kubernetes, Apr 2026) 🥇 + TMFNK/Enterprise-Context-Layer (Andy Chen, May 2026) 🥈  
> **提炼日期**: 2026-05-12  
> **用途**: 为夜间自习引擎 / 所有 skill 创建/更新提供 AKU 字段设计规约

---

## 一、AKU 7 组件 → Hermes SKILL.md 对照

| AKU 组件 | Hermes 已有 | Hermes 缺失 | 优先级 |
|:---------|:-----------|:-----------|:------:|
| ① Intent Declaration | `description` + `triggers` 字段 | — | ✅ |
| ② Procedural Knowledge | SKILL.md body（步骤+细则） | — | ✅ |
| ③ Tool Bindings | `allowed-tools` 字段 | — | ✅ |
| ④ Organizational Metadata | `metadata` + `tags` | 缺 `owner`/`service_tier`/`on_call` | 🟡 中 |
| ⑤ Governance Constraints | `AGENTS.md` + `pre_flight.py` | 缺结构化 `governance` frontmatter | 🟡 中 |
| ⑥ **Continuation Paths** | `depends_on`（仅依赖，非流向） | 缺 `continuations` 字段 | 🔴 **高** |
| ⑦ **Validators** | `scripts/` 目录（无语义化） | 缺 `validators` frontmatter | 🔴 **高** |

### 1.1 关键发现：Hermes 缺失了最高优先级的两个组件

| 组件 | 缺失影响 | 建议 |
|:----|:--------|:----|
| **⑥ Continuation Paths** | 技能孤立，代理不知下一步做什么 | 新增 `continuations` frontmatter 字段 |
| **⑦ Validators** | 无自动化治理门禁 | 新增 `validators` frontmatter 字段 |

---

## 二、Continuation Paths — SKILL.md frontmatter 设计

### 2.1 YAML 字段规约

```yaml
# 在 SKILL.md frontmatter 中新增
continuations:
  # 成功路径 — 当前技能执行完成后推荐的下一个技能
  on_success:
    - skill: next-skill-name
      condition: optional_condition_expression
      label: "Reason/purpose for this follow-up"
  
  # 失败路径 — 当前技能执行失败时升级到谁/什么
  on_failure:
    - action: escalate
      to: human
      conditions: [error_type == "permission_denied", retry_count > 3]
    - action: load_skill
      skill: fallback-skill
      conditions: [error_type == "resource_unavailable"]

  # 回退路径 — 当主路径不可用时的兜底方案
  fallback:
    - skill: basic-workflow
      note: "Run when primary resources are unavailable"
```

### 2.2 设计原则

- **最少侵入**: 字段是可选的，不破坏现有 SKILL.md 兼容性
- **条件驱动**: 每条路径可以绑定 `condition`，使导航逻辑可表达
- **三路径覆盖**: 成功/失败/回退构成完整导航拓扑
- **引用现有**: `condition` 引用 Hermes 的 `pre_flight.py` exit code 约定

### 2.3 现有 skill 中的天然典范

`night-study-engine` SKILL.md 的 `depends_on` 字段已包含此模式雏形：

```yaml
depends_on:
  - learning-workflow
  - learning
  - learning-review-cycle
```

升级为 `continuations` 后可表达：

```yaml
continuations:
  on_success:
    - skill: learning-review-cycle
      label: "Review new knowledge with spaced repetition"
  on_failure:
    - action: escalate
      to: human
      conditions: [loop_count > 3]
```

---

## 三、Validators — SKILL.md frontmatter 设计

### 3.1 YAML 字段规约

AKU 定义三种验证器类型（arXiv 2603.14805 §5）：

```yaml
# 在 SKILL.md frontmatter 中新增
validators:
  # 前置验证 — 执行前检查（precondition check）
  pre:
    - script: scripts/pre-check.sh
      description: "Verify prerequisites before execution"
      args: [--domain, "{domain}"]
  
  # 后置验证 — 执行后检查（postcondition check）
  post:
    - script: scripts/post-validate.sh  
      description: "Verify output quality and completeness"
      args: [--output, "{artifact_path}"]

  # 不变性验证 — 任意时刻可运行的独立性检查
  invariant:
    - script: scripts/check-invariants.sh
      description: "Verify no invariant has been violated"
```

### 3.2 实现原则

| 验证器类型 | 运行时机 | pass/fail 信号 | 遵循约定 |
|:---------|:--------|:--------------|:--------|
| `pre` | 技能加载后、执行前 | exit code 0=通过 | 复用 `pre_flight.py` |
| `post` | 主要步骤完成后 | exit code 0=通过 | 复用 `reflection-gate.py` |
| `invariant` | 任意时刻 | exit code 0=通过 | 新增通用检查脚本 |

### 3.3 Hermes 已有基础设施映射

```text
pre_validator  → pre_flight.py（已有，增加 YAML 驱动即可）
post_validator → reflection-gate.py（已有，增加 frontmatter 加载即可）
invariant      → 新增概念：可周期性运行的检查（如 knowledge_base 完整性）
```

---

## 四、Context Kubernetes 7 服务 → Hermes 映射（完整版）

| CK 服务 | 功能 | Hermes 组件 | 状态 | 备注 |
|:-------|:----|:-----------|:----:|:----|
| **Registry** | 知识元数据注册/发现 | `skill_view` + `skill_finder.py` + `skills_list` | ✅ | 技能发现+元数据匹配 |
| **Router** | 根据请求类型路由到正确知识源 | `select_domain.py` + `adaptive_scheduler.py` | ✅ | 领域选择=上下文路由 |
| **Permission Engine** | 权限边界/访问控制 | `pre_flight.py` + `Bounded Autonomy` 七层约束 | 🟡 | 有约束框架但无 RBAC |
| **Freshness Manager** | 新鲜度监控/过期检测 | `freshness_score` + `learning-review-cycle` | ✅ | 四维新鲜度+间隔复习 |
| **Trust Policy Engine** | 安全护栏/策略执行 | `pre_flight.py` + `AGENTS.md` + `.hermes.md` | 🟡 | 有文件级规则无运行时策略引擎 |
| **Context Operators** | 领域控制器（知识操作） | 各 `SKILL.md` + `skill_manage` + `terminal` | ✅ | 每个 skill = 一个 Context Operator |
| **LLM Gateway** | 模型接口/计量/访问 | Hermes model provider + config.yaml | ✅ | 多模型+fallback+重试 |

### 4.1 缺失组件的 Hermes 实现建议

| 组件 | 实现路径 | 优先级 |
|:----|:--------|:------:|
| Permission Engine (RBAC) | 在 `pre_flight.py` 中加入角色-权限矩阵 | 🟡 中 |
| Trust Policy Engine | 将 `AGENTS.md` 规则转化为可编程策略 | 🟡 中 |

### 4.2 关键采纳点：三层审批模型

CK 的 T1(无审批)/T2(软审批)/T3(强审批) 模型可直接应用于 Hermes 的 Bounded Autonomy:

| 自治级别 | Hermes 对应 | 审批要求 |
|:--------|:-----------|:--------|
| T1 自主执行 | 普通 skill 调用 `terminal` | 无 |
| T2 软审批 | 高风险操作（删文件/改配置） | `pre_flight.py` exit code 检查 |
| T3 强审批 | 特权操作（环境变更/敏感数据） | 外部通道不可被 agent 读写 |

---

## 五、ECL 设计哲学 — Hermes Skill 基础设施参考

### 5.1 ECL 三文件分众设计

ECL 为每个组件创建三种用途不同的文件——Hermes 技能可借鉴此模式：

| 文件 | 受众 | 用途 | Hermes 映射 |
|:----|:----|:----|:-----------|
| `README.md` | 人类开发者 | 概述/如何使用/文件说明 | 已有的 `SKILL.md`（完整版） |
| `readme-for-agents.md` | LLM Agent | 完整构建规约+可运行代码 | 暂无等价物 — 应为 Agent 生成版 |
| `readme-for-humans.md` | 架构师/工程师 | 深层设计原理 | 暂无等价物 — 应为人补充背景 |

### 5.2 ECL 模式 vs CK 模式 — 选型框架

| 维度 | ECL 极简派 | CK 专有服务派 |
|:---|:---|:---|
| **存储** | Git + Markdown（原生 Agent 可读） | 图数据库 + 审批服务 |
| **分类法** | 文件夹结构 | 声明式 YAML Manifest |
| **知识图** | Markdown 回链 | Neo4j/Weaviate 图数据库 |
| **审批** | Git push-rejection 分布式互斥 | 三层审批模型(T1/T2/T3) |
| **审计** | Git commit 历史 | 不可变审计线索 + WORM |
| **运维** | 极低（git push/pull） | 中高（维护多服务） |
| **适合** | 中小团队/个人 | 企业级/多团队 |
| **Hermes 现状** | 已在 ECL 模式上 ✅ | 可借鉴审批模型 |

### 5.3 选择建议

- **中小团队/Hermes 原生场景** → 保持 ECL 模式，维持低运维成本
- **企业级部署** → 借鉴 CK 设计不变量：
  - DI 3.7: 代理权限 = 用户权限严格子集（`P_au ⊂ P_u`）
  - DI 3.8: 强审批隔离（通道在代理环境外 + 代理不可读写 + 独立认证因子）
- **Hermes 具体落地**：保持 ECL 文件系统模式，迁移 CK 的审批思维到 `pre_flight.py` 权限分级

---

## 六、Knowledge Activation 管线 — Hermes 映射

AKU 论文定义的 Knowledge Activation 三阶段，与夜间自习引擎的学习流程天然对齐：

| KA 阶段 | 描述 | Hermes 自习引擎映射 | 状态 |
|:-------|:----|:------------------|:----:|
| **Codification** | 隐性知识→结构化格式 | `extracted_knowledge.md` 知识提炼 | ✅ |
| **Compression** | 结构化→Token高效形式 | KB JSON 概念存储（关键信息 vs 原始来源） | ✅ |
| **Injection** | Token高效知识→代理上下文 | `skill_view()` + `pre_flight.py` + session 注入 | 🟡 部分 |

### 6.1 改进方向：从手动压缩到自动编译

当前 `extracted_knowledge.md` → JSON KB 是手工提炼。借鉴 AKF 的自动编译：

```text
当前: 人工提炼 → 手动写入 SKILL.md/KB JSON
未来: Agent 运行 → 自动提取概念卡 + 策略卡 → 组装最小可行上下文
```

优先级：🟢 低（当前手动流程质量已 >85%）

---

## 七、AKU Continuation Paths 和 Validators 在现有 skill 中的检查清单

创建/更新任何 skill 时，考虑：

- [ ] ❓ 该 skill 完成后是否应当建议下一个 skill？（→ 加 `continuations`）
- [ ] ❓ 执行前是否需要检查前置条件？（→ 加 `validators.pre`）
- [ ] ❓ 执行后是否需要验证输出质量？（→ 加 `validators.post`）
- [ ] ❓ 是否有跨 skill 不变的约束需要检查？（→ 加 `validators.invariant`）
- [ ] ❓ 该 skill 是否适合 ECL 三文件模式？（→ 加 `readme-for-agents.md`）
- [ ] ❓ 是否需要审批分级（T1/T2/T3）？（→ 调 Bounded Autonomy 级别）
