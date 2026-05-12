# 能力模块化可行性研究 — 实战记录 (2026-05-12)

> 从 boku 能力库提取 18 个模块 + 3 个扩展槽的完整研究过程。
> 涵盖：遗漏领域分析、三层架构设计、扩展性机制、业界对比数据。

---

## 一、研究背景

目标：将 boku（Hermes Agent）的 Agent 能力拆分为标准化「能力包」，通过适配器在其他 Agent（Claude Code / Codex CLI）上快速复用。

## 二、初始遗漏分析

| 原始版本（8 模块） | 遗漏了 | 严重性 |
|:-----------------|:-------|:------:|
| doc-engine, developer-workflow, security-audit, financial-analysis, learning-engine, devops-monitor, creative-design, mcp-hub | ❌ 知识库系统 | 🔴 致命 |
| — | ❌ 元认知系统 | 🔴 致命 |
| — | ❌ 质量保障 | 🔴 致命 |
| — | ❌ 消息平台 | 🟡 重要 |
| — | ❌ 音视频媒体 | 🟡 重要 |
| — | ❌ GitHub 生态 | 🟡 重要 |
| — | ❌ 网络代理 | 🟢 中等 |
| — | ❌ 新闻研究 | 🟢 中等 |
| — | ❌ Agent 协作 | 🟢 中等 |
| — | ❌ 社交娱乐 | 🟢 中等 |
| — | ❌ 框架成长性 | 🔴 致命 |

**根因**：仅依赖 `self-capabilities-map` 的领域列表，未做穷举扫描 + 手动归类。

## 三、最终分类（18 模块 + 3 扩展槽）

### 三层架构

```
🪞 元能力层（5 模块）
  knowledge-base | learning-engine | metacognition
  quality-assurance | agent-orchestration

⚡ 应用层（9 模块）
  doc-engine | developer-workflow | security-audit
  github-ecosystem | financial-analysis | creative-design
  media-processing | news-research | social-gaming

🏗️ 基础设施层（4 模块）
  devops-monitor | network-proxy | messaging | mcp-integration

🟡 扩展槽（3 个）
  hermes-new-features | custom-plugin | future-domain
```

### 完整分类详表

| # | 模块 ID | 技能数 | 核心 Skills |
|:-:|:--------|:------:|:-----------|
| 1 | knowledge-base | ~6 | knowledge-precipitation, knowledge-routing, hermes-knowledge-base, file-classification, file-system-manager, llm-wiki |
| 2 | learning-engine | ~7 | learning-workflow, learning, learning-review-cycle, night-study-engine, deep-research, skill-creator, information-decomposition |
| 3 | metacognition | ~6 | hermes-self-analysis, self-capabilities-map, anti-repetition-loop, memory-management, self-review, problem-solving-sherlock |
| 4 | quality-assurance | ~10 | sra-qa-workflow, generic-qa-workflow, skill-eval-cranfield, doc-alignment, adversarial-ux-test, dogfood, requesting-code-review |
| 5 | agent-orchestration | ~12 | hermes-agent, claude-code, codex, opencode, blackbox, honcho, bmad-method, bmad-party-mode-orchestration, kanban-orchestrator |
| 6 | doc-engine | ~12 | pdf-layout, pdf-pro-design, pdf-render-comparison, pptx-guide, docx-guide, markdown-guide, html-guide, latex-guide, epub-guide, vision-qc-patterns, readme-for-ai, doc-design |
| 7 | developer-workflow | ~16 | writing-plans, plan, systematic-debugging, tdd, subagent-driven-development, spike, sdd-workflow, generic-dev-workflow |
| 8 | security-audit | ~5 | delete-safety, commit-quality-check, 1password, sherlock, godmode |
| 9 | github-ecosystem | ~10 | github-repo-management, github-pr-workflow, github-code-review, github-issues, github-auth, git-advanced-ops |
| 10 | financial-analysis | ~2 | financial-analyst (akshare + ta + matplotlib) |
| 11 | creative-design | ~18 | architecture-diagram, mermaid-guide, concept-diagrams, excalidraw, p5js, pixel-art, creative skills |
| 12 | media-processing | ~9 | text-to-speech, heartmula, songsee, gif-search, comfyui, image-generation, image-prompt-guide |
| 13 | news-research | ~7 | news-briefing, blogwatcher, ai-trends, arxiv, polymarket, duckduckgo-search, searxng-search |
| 14 | social-gaming | ~6 | minecraft-modpack-server, pokemon-player, fitness-nutrition, yuanbao, bangumi-recommender |
| 15 | devops-monitor | ~8 | linux-ops-guide, proxy-monitor, system-health-check, docker-management, process-management |
| 16 | network-proxy | ~5 | clash-config, proxy-finder, web-access, browser-automation, web-ui |
| 17 | messaging | ~8 | feishu, feishu-send-file, feishu-batch-send, feishu-card-merge-streaming, agentmail, himalaya |
| 18 | mcp-integration | ~5 | native-mcp, fastmcp, mcporter, hermes-message-injection, smart-broadcast |

## 四、扩展性设计

### 自动分类机制

```python
def classify_skill(skill_tags):
    tag_to_module = {
        "文档": "doc-engine", "pdf": "doc-engine",
        "测试": "quality-assurance", "qa": "quality-assurance",
        "安全": "security-audit",
        "知识": "knowledge-base",
        "学习": "learning-engine",
        "git": "github-ecosystem",
        "代理": "network-proxy",
        "飞书": "messaging", "feishu": "messaging",
        # 映射表可扩展
    }
    for tag in skill_tags:
        if tag in tag_to_module:
            return tag_to_module[tag]
    return "hermes-new-features"
```

### 分类决策树

```
新能力 → 已有领域？→ 归入对应模块
      → 多领域？→ 主模块 + 交叉引用
      → 全新领域 ≥3 技能？→ 创建新模块
      → 否则暂存到 hermes-new-features
```

## 五、业界调研数据

### MCP 协议现状（2026 年 3 月）

- 97M+ 月 SDK 下载量
- 10,000+ 公开 MCP Server
- 已获 OpenAI / Google / Anthropic 全部采用
- 13,000+ 社区贡献的 MCP 服务器

### 主流框架模块化对比

| 框架 | 模块化粒度 | 跨 Agent 移植 | 成熟度 |
|:-----|:----------|:--------------|:------:|
| Hermes Agent | SKILL.md / Profile / Plugin / MCP | Profile 导出 + MCP Serve | 成熟 |
| LangChain / LangGraph | Tool / Chain / Agent | 需 Adapter | 非常成熟 |
| CrewAI | Role / Task / Tool | 相对封闭 | 快速成熟 |
| AutoGen (MS) | Agent / Tool / Workflow | 需自定义适配 | 发展中 |
| STEM Agent | Protocol / Skill / Memory | MCP 标准化 | 研究原型 |
| Agency | Primitive (NL building block) | 跨项目复用 | 概念验证 |

## 六、Hermes 已有模块化桥接

| 桥接机制 | 示例 | 状态 |
|:---------|:-----|:----:|
| `hermes mcp serve` | Claude Code 调用 boku 能力 | 存在 |
| Profile 导出/导入 | 移植到另一台机器 | 存在 |
| 外部 Skills 目录 | 团队共享技能库 | 存在 |
| SRA 多 Agent 适配 | Hermes/Claude/Codex | 存在 |
| Skills Hub / Registry | 安装社区共享技能 | 存在（待完善） |
| Honcho / Mem0 | 跨 Agent 记忆共享 | 可选插件 |
