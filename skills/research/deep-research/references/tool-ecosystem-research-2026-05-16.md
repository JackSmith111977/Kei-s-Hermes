# Skill 治理工具生态研究（2026-05-16）— 七维差距分析实战案例

> **对应 deep-research Skill 的「工具生态研究 & 差距分析法」模式**
> **来源**: EPIC-005 技能治理引擎深度调研

## 一、需求矩阵：7 个评估维度

| 维度 | 说明 | 判断标准 |
|:-----|:------|:---------|
| ① 原子性扫描 | 判断 skill 是否粒度合理、职责单一 | 有四问测试或类似机制 → 完全 / 有结构检查但无原子性定义 → 部分 / 无 → 空白 |
| ② 树状结构管理 | 检查 skill 是否有簇归属/分类层级 | 有自动聚类+结构验证 → 完全 / 有手动分类 → 部分 / 无 → 空白 |
| ③ 工作流编排检测 | 检测 skill 是否包含编排声明（pipeline/DAG） | 有编排检测 → 完全 / SKILL.md 规范提及但不检测 → 部分 / 无 → 空白 |
| ④ Cap-Pack 合规 | 检查是否符合 cap-pack 格式与质量标准 | 有对照 schema 的自动检查 → 完全 / 有质量检查但不针对 cap-pack → 部分 / 无 → 空白 |
| ⑤ 新增检测 | 自动发现新增 skill 并触发检查链 | cron/event 持续 watcher → 完全 / pre-commit event 触发 → 部分 / 无 → 空白 |
| ⑥ 自动质量测试 | 自动运行质量评分 | 持续自动 + 门禁 → 完全 / on-demand CLI → 部分 / 无 → 空白 |
| ⑦ 自动适配改造 | 自动生成适配方案并执行 | dry-run + 确认 + 执行 → 完全 / 只报告不修复 → 部分 / 无 → 空白 |

## 二、工具目录（12+ 工具）

| 工具 | 类型 | 语言 | 关注度 | URL |
|:-----|:-----|:-----|:------:|:----|
| **skill-validator** | 质量验证 | Go | ⭐102 | github.com/agent-ecosystem/skill-validator |
| **skill-guard** | 质量门禁 | Python | ⭐3 | github.com/vaibhavtupe/skill-guard |
| **SkillCompass** | 质量评估 | Claude插件 | — | skillsllm.com/skill/skillcompass |
| **skills-check** | 工具包 | — | — | skillscheck.ai |
| **skillctl** | 包管理+lint | — | — | skillctl.xyz |
| **skill-tree** | 树状路由 | Python | — | github.com/danielbrodie/skill-tree |
| **Skilldex** | 包管理+验证 | TypeScript | 学术 | github.com/Pandemonium-Research/Skilldex |
| **AgentVerus** | 安全认证 | — | — | agentverus.ai |
| **Cisco skill-scanner** | 安全扫描 | Python | 企业 | github.com/cisco-ai-defense/skill-scanner |
| **CAPA** | 能力管理 | Go | — | github.com/infragate/capa |
| **Skilgen** | 自动生成 | — | — | skilgen/skilgen |
| **skilltree (npm)** | 依赖管理 | Rust | — | github.com/imarios/skilltree |

## 三、覆盖映射

| 需求 | skill-val | skill-guard | Compass | skill-tree | Skilldex | skillctl | 其他 |
|:-----|:---------:|:-----------:|:-------:|:----------:|:--------:|:--------:|:----:|
| ① 原子性 | ⚠️部分 | ⚠️部分 | ✅ | ❌ | ⚠️部分 | ⚠️部分 | ❌ |
| ② 树状 | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| ③ 工作流编排 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| ④ Cap-Pack合规 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| ⑤ 新增检测 | ❌ | ⚠️部分 | ❌ | ❌ | ❌ | ❌ | ❌ |
| ⑥ 质量测试 | ✅ | ✅ | ✅ | ❌ | ⚠️部分 | ✅ | ⚠️ |
| ⑦ 自动适配 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## 四、差距量化

| 需求 | 最佳覆盖 | 差距 | 等级 |
|:-----|:---------|:-----|:----:|
| ① 原子性 | skill-guard validate + skill-validator (检查结构但不判断原子粒度) | 缺四问测试和粒度阈值 | 🟡 |
| ② 树状 | skill-tree (做聚类路由但不关联质量和合规) | 树 + 质量 + cap-pack 三者割裂 | 🟡 |
| ③ 工作流编排 | **无任何工具** | 完全空白 | 🔴 |
| ④ Cap-Pack合规 | **无任何工具** | 完全空白 — **最大差异化** | 🔴 |
| ⑤ 新增检测 | skill-guard pre-commit (event 触发而非持续 watcher) | 缺持续 cron watcher | 🟡 |
| ⑥ 质量测试 | skill-guard test + skill-validator (on-demand 非自动) | 缺触发式自动测试 | 🟡 |
| ⑦ 自动适配 | **无任何工具** | 完全空白 — **第二大差异化** | 🔴 |

## 五、价值定位

```
现有工具做：「发现问题 → 报告问题」
本工具做：「发现问题 → 报告问题 → 自动适配到 Cap-Pack 标准」
```

**独特卖点 (USP)**：Cap-Pack 合规检测 + 工作流编排检测 + 自动适配改造 = 三个完全空白维度
