# 🏗️ Hermes ↔ Context Kubernetes: 架构映射指南

> **创建日期**: 2026-05-14 | **来源**: arXiv:2604.11623 (Mouzouni, April 2026)  
> **用途**: Context K8s 是企业知识编排的参考架构；本文件列出 Hermes 各组件与 7 服务的对应关系、实现状态和缺口  
> **关联参考**: `references/aku-hermes-skill-evolution.md` (AKU Continuations/Validators)

---

## 一、Context K8s 概述

Context K8s 将企业知识编排类比容器编排问题，核心论点是：
> "每次计算时代都产生一个主导原语和一个规模危机。虚拟机需要 VMware。容器需要 Kubernetes。AI Agent 需要一个尚不存在的东西：组织知识的编排层。"

**支持数据**：
- 无治理时 26.5% 查询产生幻影内容/矛盾信息/跨域数据泄露
- 治理后：0% 幻影内容，噪声降低 14 个百分点
- 三层权限模型阻止全部 5 个攻击场景（flat RBAC 只阻止 4/5）
- 5 个企业平台调研：无一强制执行带外强审批隔离

知识编排比容器编排更难的四维属性：异质性 (H)、语义性 (S)、敏感性 (S)、学习性 (L)

---

## 二、7 服务 → Hermes 完整映射

### 1. Context Registry (元数据存储, 类比 etcd)

| 维度 | Context K8s | Hermes 对应 |
|:---|:---|:---|
| **功能** | 存储 Context Units 的元数据、类型、版本、嵌入向量、授权角色 | `skill_view`/`skill_manage` + `knowledge_base/*.json` |
| **查询** | 按 intent/domain/role 发现上下文 | `skills_list` 按 category 过滤 |
| **版本** | 每次变更创建新版本 | `skill_manage(edit)` 覆盖原文件，无自动版本链 |
| **实现状态** | ⚠️ 部分 | 元数据存储 ✅；版本对比/回滚 ❌ |
| **缺口** | 无元数据发现 API（"所有 context unit of type X"），无版本链 |

### 2. Context Router (调度智能, 类比 kube-scheduler + Ingress)

| 维度 | Context K8s | Hermes 对应 |
|:---|:---|:---|
| **功能** | 将 agent 请求路由到正确的 Context Store | `select_domain.py` (包装 `adaptive_scheduler.py`) |
| **模式** | 意图路由：agent 说"what"，不问"where" | 优先级路由：按 `priority × freshness` 公式 |
| **实现状态** | ⚠️ 部分 | 优先级调度 ✅；意图路由 ❌ |
| **缺口** | 无语义意图→Context Store 映射，只有定时调度 |

### 3. Permission Engine (三层 Agent 权限模型)

| 维度 | Context K8s | Hermes 对应 |
|:---|:---|:---|
| **模型** | T1 Autonomous → T2 Soft Approval → T3 Strong Approval | `AGENTS.md` 门禁规则 + `pre_flight.py` 阻塞 |
| **不变量 3.7** | `P_agent ⊂ P_user` (严格子集) | 未显式区分 user/agent 权限 |
| **不变量 3.8** | 强审批通道：带外 + 独立因子 + agent 不可读写 | 无。所有审批在 agent 执行环境中 |
| **实现状态** | ⚠️ 部分 | 基本门禁 ✅；三层模型 ❌；不变量 3.8 ❌ |
| **缺口** | 无 user/agent 权限分离，无带外强审批隔离，无三级审批 |

### 4. Freshness Manager (健康监控)

| 维度 | Context K8s | Hermes 对应 |
|:---|:---|:---|
| **状态** | 四状态监测：fresh / stale / expired / conflicted | `freshness_score` (0-1 浮点数) |
| **监控** | 连续监测，过期 < 1ms 可检测 | 夜间自习引擎轮次驱动，非实时 |
| **动作** | TTL 过期自动标记 stale，触发刷新 | 无自动过期；间隔复习（1d/3d/7d/30d）手动推进 |
| **实现状态** | ⚠️ 部分 | 新鲜度评分 ✅；四状态模型 ❌；自动过期 ❌ |
| **缺口** | KB 概念无 `expires_at` 字段，无 auto-refresh 管线 |

### 5. Trust Policy Engine (声明式护栏评估)

| 维度 | Context K8s | Hermes 对应 |
|:---|:---|:---|
| **功能** | 异常检测、DLP 数据防泄漏、审计日志、护栏评估 | `pre_flight.py` 门禁 + `reflection-gate.py` 质量门禁 |
| **范围** | 全系统知识操作 | 仅学习任务的门禁检查 |
| **实现状态** | ⚠️ 部分 | 简单门禁 ✅；DLP/异常检测 ❌；全系统审计 ❌ |
| **缺口** | 无 DLP 功能，无跨 session 异常检测，审计范围有限 |

### 6. Context Operators (领域控制器, Def 3.6)

| 维度 | Context K8s | Hermes 对应 |
|:---|:---|:---|
| **功能** | 领域专用 controller：含知识存储 + LLM 推理 + 组织智能模块 + 护栏 | `skills/` 目录 + `scripts/` + `references/` |
| **模式** | 声明式期望状态 + Reconciliation Loop | 无 Reconciliation Loop，命令式执行 |
| **实现状态** | ✅ 基本 | skill 结构 ✅；Reconciliation ❌ |
| **缺口** | 无 K8s 风格的 reconciliation controller。每个 skill 是"被调用时执行"而非"持续确保状态" |

### 7. LLM Gateway (提示检查 + 成本计量)

| 维度 | Context K8s | Hermes 对应 |
|:---|:---|:---|
| **功能** | 提示注入检查、成本计量、速率限制 | 无直接对应 |
| **实现状态** | ❌ 缺失 | Hermes 的 provider 层处理部分(成本/速率)但无提示安全检查 |
| **缺口** | 完全缺失。Hermes provider config 只有 API key/endpoint 配置 |

---

## 三、7 个需求映射 (NIST AI RMF)

| # | 需求 | Context K8s | Hermes | 状态 |
|:---|:---|:---|:---|:---:|
| R1 | 供应商中立 | ✅ 任何LLM/框架/云/数据源 | ✅ 多 provider + 自定义 | ✅ |
| R2 | 声明式管理 | ✅ YAML manifest 版本管理 | ✅ 文件系统 + git | ✅ |
| R3 | Agent 权限分离 | ✅ 三层模型 + 不变量 3.7/3.8 | ⚠️ 基本门禁，无严格子集 | ⚠️ |
| R4 | 上下文新鲜度 | ✅ 连续监测 + TTL 策略 | ⚠️ 轮次驱动的新鲜度评分 | ⚠️ |
| R5 | 基于意图的访问 | ✅ agent 说"what"不问"where" | ❌ agent 必须知道技能路径 | ❌ |
| R6 | 完整可审计 | ✅ 不可变日志 | ⚠️ JSONL 日志但非不可变 | ⚠️ |
| R7 | 组织智能 | ✅ 跨领域模式提取 | ⚠️ experience_extractor 初版 | ⚠️ |

**综合状态**: 7 需求中 1 完全满足 (R1, R2)，2 部分满足 (R3, R4, R6, R7)，1 完全缺失 (R5)

---

## 四、知识编排比容器编排更难 — Hermes 视角

| 属性 | Context K8s 定义 | Hermes 现状 | 影响 |
|:---|:---|:---|:---|
| **异质性 H** | 容器标准化(OCI)；上下文跨 markdown/PDF/DB/Slack | skills/ + knowledge_base/ + references/ 多格式 | CxRI 标准化需求 |
| **语义性 S** | 调度容器是确定性的；路由上下文需要判断和消歧 | select_domain 用优先级公式，无语义理解 | 需要意图路由 |
| **敏感性 S** | 容器无"机密"属性；上下文天然含访问控制层级 | AGENTS.md 门禁，无 RBAC 矩阵 | 三层权限模型 |
| **学习性 L** | 容器不因被访问而改变；上下文使用模式隐含信息需求 | night_study_session_log 分析潜力未开发 | 组织智能操作器 |

---

## 五、升级路线图建议

### 短期 (可行性高，低风险)
1. **KB 概念添加 `expires_at` 字段** — 实现 Hermes R4 的 TTL 基础
2. **SKILL.md frontmatter 新增 `continuations:` 和 `validators:` 字段** — 实现 AKU 提议（见 `aku-hermes-skill-evolution.md`）

### 中期 (1-3 轮自习)
3. **Skill Registry 元数据发现 API** — 让 agent 可以"找所有 Category=X 的 skill"
4. **权限矩阵从 AGENTS.md 硬编码 → 结构化 JSON** — 允许 user/agent 权限分离

### 长期 (架构改进)
5. **Context Router 意图化** — 从 `select_domain.py` 的优先级路由升级为语义路由
6. **带外批准通道** — 实现不变量 3.8 的强审批隔离
7. **Freshness Manager TTL 自动过期管线** — 替代手动间隔复习
