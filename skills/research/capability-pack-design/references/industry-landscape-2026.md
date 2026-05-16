# Agent Skill 治理工具行业生态报告 (2025-2026)

> **创建**: 2026-05-16 | **来源**: 深度调研（3 轮搜索 + 深度阅读 + 交叉验证）
> **用途**: cap-pack 项目战略参考 — 了解已有工具、发现差异化空间

---

## 一、工具全景图

截至 2026 年 5 月，Agent Skill 治理工具赛道已出现 **12+ 款工具**，可按功能分为 5 类：

### 1.1 质量验证类 (Quality Validators)

| 工具 | 语言 | 关注度 | 核心能力 | 独特之处 |
|:-----|:-----|:------:|:---------|:---------|
| **skill-validator** | Go | ⭐102 | 结构验证/链接检查/内容分析/污染检测/LLM评分 | 基于训练数据的 novelty 评分；参考文献可追溯图 |
| **skill-guard** | Python | ⭐3 | 验证/安全/冲突检测/测试/监控 | CI 集成最完善（pre-commit/GitHub Actions）；支持 eval 测试环 |
| **SkillCompass** | — | 插件 | 6维度评分/改进环/使用追踪 | 「找最弱维→自动修复→再评估」闭环；passive usage tracking |
| **skills-check** | — | — | 新鲜度/安全/Lint/Token预算/semver/策略/测试 | 10 条命令覆盖最全；支持 staleness 检测 |

### 1.2 安全扫描类 (Security Scanners)

| 工具 | 语言 | 核心能力 | 独特之处 |
|:-----|:-----|:---------|:---------|
| **AgentVerus** | — | 6风险类别+信任评分+信任徽章 | 概念最完整（permission/injection/dependency/behavioral） |
| **Cisco skill-scanner** | Python | 注入/泄露/恶意代码 | 企业级：LLM-as-judge + YARA + AST 数据流 + VirusTotal |
| **skills-guard** (npm) | TS | 安全扫描 CLI | `sg scan` 命令含 5 层检测 |

### 1.3 包管理类 (Package Managers)

| 工具 | 语言 | 核心能力 | 独特之处 |
|:-----|:-----|:---------|:---------|
| **Skilldex** 🎓 | TS | 包管理+格式合规评分+skillset+三作用域+MCP | 学术论文出身；skillset 跨 skill 一致性保障；MCP 原生接入 |
| **skilltree** | Rust | 传递依赖+锁定文件+注册中心 | 类 npm 设计；`skilltree scan` 检测未声明依赖 |
| **skm** | TS | 锁文件+可复现安装 | 类 lockfile + commit pinning |
| **skillctl** | — | 搜索/安装/lint/指南 | 8项质量检查；唯一支持多注册中心搜索 |

### 1.4 结构管理类 (Structure Managers)

| 工具 | 语言 | 核心能力 | 独特之处 |
|:-----|:-----|:---------|:---------|
| **skill-tree** | Python | 双跳聚类路由+跨平台+沙箱 | `manifest.json` 单一真相来源；manifest 不变/聚类脚本可升级；跨 4 平台 |

### 1.5 能力平台类 (Capability Platforms)

| 工具 | 语言 | 核心能力 | 独特之处 |
|:-----|:-----|:---------|:---------|
| **CAPA** | Go | Skills+Tools+Credentials+MCP | `capa.yaml` 声明式配置；支持动态按需加载 |
| **Skillware** | Python | 能力框架+注册中心 | 三元素（Logic+Cognition+Governance）；多模型原生适配 |
| **Skilgen** | — | 代码库→skills 自动生成+质量评分 | repo 级技能系统；变更检测自动刷新 |

---

## 二、学术论文参考

| 论文 | 年份 | 核心贡献 | 对 cap-pack 的启示 |
|:-----|:----:|:---------|:-------------------|
| **Skilldex** (arXiv 2604.16911) | 2026 | 格式合规评分 + skillset 抽象 + 三作用域 | 技能集一致性验证 + MCP 集成模式 |
| **SkillRouter** (arXiv 2603.22455) | 2026 | 1.2B 全文本技能路由，74% Hit@1 at 80K | 大规模技能库需要树状结构；全文本 > 仅元数据 |
| **SkillOrchestra** (arXiv 2602.19672) | 2026 | 技能感知编排 + Skill Handbook | Skill Handbook 概念可复用为 cap-pack 的 governance catalog |
| **Agent-Kernel** (arXiv 2512.01610) | 2025 | 微内核多智能体架构 | cap-pack §①-α 的三支柱融合模型参考来源 |

---

## 三、核心差距分析

### 3.1 七维覆盖矩阵

```
需求                           skill-validator   skill-guard   skill-tree   Skilldex   cap-pack 项目
──────────────────────────────────────────────────────────────────────────────────────────────
① 原子性扫描                      ⚠️ 部分          ⚠️ 部分        ❌          ❌         ❌
② 树状结构管理                    ❌               ❌            ✅ 聚类      ❌         ⚠️ 有工具
③ 工作流编排检测                  ❌               ❌            ❌          ❌         ❌
④ Cap-Pack 合规                  ❌               ❌            ❌          ❌         ❌     ← USP
⑤ 自动新增检测                    ❌               ⚠️ pre-commit  ⚠️ /fetch   ❌         ❌
⑥ 自动质量测试                    ⚠️ on-demand     ⚠️ on-demand   ❌          ⚠️ 安装时   ❌
⑦ 自动适配改造                    ❌               ❌            ❌          ❌         ❌     ← USP
```

### 3.2 关键洞察

1. **③④⑦ 是完全空白领域** — 没有任何现有工具覆盖工作流编排检测、Cap-Pack 合规、自动适配改造
2. **现有工具全在「发现问题→报告问题」阶段** — 没人做「发现问题→自动适配到 Cap-Pack」
3. **最大复用机会** — skill-guard 的冲突检测 + skill-validator 的 LLM 评分 + skill-tree 的聚类，可作为治理引擎的上游数据源
4. **最远发展** — 学术论文已证明大规模技能库需要树状结构（SkillRouter: 80K 技能时全文本检索必备）

---

## 四、来源索引

### 质量验证
- skill-validator: https://github.com/agent-ecosystem/skill-validator
- skill-guard: https://github.com/vaibhavtupe/skill-guard (pypi: skill-guard)
- SkillCompass: https://skillsllm.com/skill/skillcompass
- skills-check: https://skillscheck.ai/

### 安全扫描
- AgentVerus: https://agentverus.ai/ + https://github.com/agentverus/agentverus-scanner
- Cisco skill-scanner: https://github.com/cisco-ai-defense/skill-scanner (pypi: cisco-ai-skill-scanner)
- skills-guard (npm): https://registry.npmjs.org/skills-guard

### 包管理
- Skilldex: https://github.com/Pandemonium-Research/Skilldex + arxiv 2604.16911
- skilltree: https://github.com/imarios/skilltree
- skm: https://github.com/stefafafan/skm + https://getskm.dev/
- skillctl: https://skillctl.xyz/

### 结构管理
- skill-tree: https://github.com/danielbrodie/skill-tree

### 能力平台
- CAPA: https://github.com/infragate/capa
- Skillware: https://github.com/rosspeili/skillware
- Skilgen: https://github.com/skilgen/skilgen
- agent-skills: https://github.com/datalayer/agent-skills
- skillpacks: https://github.com/agentsea/skillpacks

### 学术论文
- Skilldex (arXiv 2604.16911): https://arxiv.org/abs/2604.16911
- SkillRouter (arXiv 2603.22455): https://arxiv.org/html/2603.22455v2
- SkillOrchestra (arXiv 2602.19672): https://arxiv.org/abs/2602.19672
- Vercel Skills CLI Research: agent skills passive context vs active retrieval (53% → 100% pass rate)

### 行业综述
- Repello AI comparison: https://repello.ai/blog/ai-agent-skill-scanner
- MCP Registry official: https://registry.modelcontextprotocol.io/
