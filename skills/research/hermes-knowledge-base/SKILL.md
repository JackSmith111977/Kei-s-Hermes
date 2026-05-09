---
name: hermes-knowledge-base
description: Hermes 知识库构建方案——基于 Karpathy LLM Wiki + GBrain 的集成设计
version: 1.0.0
triggers:
  - 知识库
  - 知识管理
  - knowledge base
  - RAG
  - knowledge graph
  - 知识图谱
  - GBrain
  - LLM Wiki
  - brain
  - memory
depends_on:
  - file-classification
  - file-system-manager
  - learning-workflow
design_pattern: Architecture-Design
skill_type: Plan
---

# 🧠 Hermes 知识库构建方案

> 基于 Karpathy LLM Wiki 模式 + Garry Tan GBrain 架构

---

## 一、核心设计理念

| 原则 | 来源 | 说明 |
|:----|:-----|:------|
| **Compiled Truth** | Karpathy + GBrain | 知识编译一次，持续更新，非每次查询重新推导 |
| **复利效应** | Karpathy | 每次新资料和问答让知识库更丰富 |
| **关注点分离** | Karpathy | 人类策展/LLM维护 |
| **Schema 驱动** | Karpathy | AGENTS.md 定义知识库结构和行为 |
| **Thin Harness, Fat Skills** | GBrain | 运行时尽量薄，智能全在 Skill 文件中 |
| **Human Always Wins** | GBrain | 可直接编辑 Markdown，同步即可 |
| **Bounded Autonomy** | Karpathy | 约束使自主成为可能 |

---

## 二、推荐架构：三层知识系统

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Hermes 知识系统架构
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L1: 操作级知识 ─── Hermes Skills 系统（已就绪）
    技能库 ~90+ 个 skill
    SKILL.md + references/ + scripts/
    用于：代码、脚本、工具链、工作流

L2: 经验级知识 ─── Experiences + Learning（已就绪）
    ~/.hermes/experiences/active/ + skills/
    ~/.hermes/learning/ + archive/
    用于：疑难解决方案、最佳实践、学习笔记

L3: 实体级知识 ─── GBrain / LLM Wiki（待建设 🏗️）
    人、公司、概念、项目、会议的结构化知识
    混合检索（向量+关键词+图谱）
    用于：跨会话记忆、实体查询、关系推理
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 三、方案对比

| 方案 | 复杂度 | 依赖 | 适合规模 | 启动成本 |
|:----|:------:|:----|:--------:|:--------:|
| **A: GBrain 集成** ⭐ | 中 | Bun + PGLite | 100K+ 页面 | 30分钟 |
| **B: 纯 Markdown Wiki** | 低 | 无 | ~500 页面 | 5分钟 |
| **C: 混合 (A+B)** 🏆 | 中 | Bun | 不限 | 30分钟 |

### 🏆 推荐：方案 C（混合架构）

```
GBrain (实体级)          LLM Wiki (上下文级)       Hermes Skills (操作级)
    │                         │                         │
    │ 人物/公司/概念          │ 文档摘要/研究报告        │ 代码/脚本/工作流
    │ 混合检索                │ 永久性 Markdown          │ 即用即加载
    │ MCP 协议接入            │ 进化式 Schema            │ 独立版本管理
    └─────────────────────────┼─────────────────────────────┘
                              │
                    统一通过 Hermes Agent 调度
```

---

## 四、实施路线图

### Phase 1: GBrain 安装（1-2 小时）
```bash
# 1. 安装 Bun（如未安装）
curl -fsSL https://bun.sh/install | bash

# 2. 安装 GBrain
bun install -g github:garrytan/gbrain

# 3. 初始化 brain 仓库
mkdir -p ~/brain && cd ~/brain
git init
gbrain init   # 默认 PGLite

# 4. 导入现有知识
gbrain import ~/.hermes/learning/ --tag hermes-learning
gbrain import ~/.hermes/experiences/active/ --tag hermes-experience

# 5. 生成嵌入
gbrain embed --stale

# 6. 验证
gbrain query "my knowledge base contains what?"
```

### Phase 2: Hermes 集成（30 分钟）
```yaml
# ~/.hermes/config.yaml
mcp_servers:
  gbrain:
    command: gbrain
    args: ["serve"]
```

### Phase 3: 自动 Ingestion Pipeline（2-3 小时）
创建 cron 任务实现自动知识摄入：
```bash
# 每日自动导入学习记录到 GBrain
cronjob create --name "daily-brain-ingest" \
  --schedule "0 4 * * *" \
  --prompt "导入新的学习记录到 GBrain 知识库"
```

### Phase 4: Dream Cycle（4+ 小时后持续）
```bash
# 每晚自动执行实体丰富 + 引用修复 + 记忆整合
cronjob create --name "dream-cycle" \
  --schedule "0 2 * * *" \
  --prompt "执行 GBrain 夜间维护：实体丰富、引用修复、记忆整合"
```

---

## 五、与现有系统的融合

| 现有机制 | 与知识库的关系 |
|:---------|:---------------|
| Skills (~90+) | 操作级知识，直接可用 |
| Learning Workflow | 学习产出的知识自动导入知识库 |
| Experiences | 经验级知识，索引到知识库 |
| file-system-manager | 文件清理保护，避免误删知识库文件 |
| file-classification | 分类标准，指导知识库内容组织 |
| Night Study Engine | 学到的知识沉淀到知识库 |

---

## 六、关键参考资源

| 资源 | 链接 | 说明 |
|:----|:-----|:------|
| Karpathy LLM Wiki | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f | 核心模式 |
| GBrain | https://github.com/garrytan/gbrain | Hermes 知识库参考实现 |
| Karpathy autoresearch | https://github.com/karpathy/autoresearch | Bounded Autonomy 实践 |
| AgentKnowledgeHub | https://github.com/bcefghj/agent-knowledge-hub | 多Agent知识管理参考 |
| Context Patterns | https://contextpatterns.com/ | 上下文工程模式 |
