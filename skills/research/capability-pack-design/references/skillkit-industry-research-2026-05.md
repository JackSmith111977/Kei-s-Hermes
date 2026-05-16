# SkillKit & Agent Skill Porter 行业调研 (2026-05-16)

> **来源**: 2026-05-16 深度联网搜索 + 交叉验证
> **用途**: EPIC-007 设计参考 — 了解现有工具能力边界，定位差异化空间

---

## SkillKit — 跨 46 Agent Skill 包管理器

| 属性 | 值 |
|:-----|:----|
| 仓库 | https://github.com/rohitg00/skillkit |
| Stars | ⭐935 |
| 语言 | TypeScript (99.2%) |
| 许可证 | Apache 2.0 |
| 最新版本 | v1.24.0 (2026-04-21) |
| 发布数 | 46 |

### 核心能力

| 命令 | 功能 |
|:-----|:------|
| `skillkit add <source>` | 从市场安装 skill |
| `skillkit translate <skill> --to <agent>` | 跨 Agent 格式转换 |
| `skillkit sync` | 部署到 Agent 配置 |
| `skillkit recommend` | 栈感知技能推荐 |
| `skillkit generate` | AI 技能生成（支持 Claude/GPT-4/Gemini/Ollama） |
| `skillkit serve` | REST API 服务器 |

### 支持 Agent (46 个)

**Top 11**: Claude Code, Cursor, Codex, Gemini CLI, OpenCode, GitHub Copilot, Windsurf, Devin, Aider, Cody, Amazon Q

**支持 Hermes Agent**：在完整 Agent 列表中明确列出。

### 对我们项目的启示

1. **格式标准已统一**: 46 个 Agent 共用 SKILL.md 格式，验证了我们的方向——我们不需要做格式翻译
2. **我们的空白区**: SkillKit 不做语义分组、不做治理闭环、不做经验提取
3. **Hermes 已在生态中**: 说明 Hermes 的 SKILL.md 标准与其他 Agent 互操作
4. **`skillkit translate` 模式**: 格式转换已有成熟工具，我们在 EPIC-007 中不需要重复造轮子

---

## Agent Skill Porter — 7 Agent 格式互转

| 属性 | 值 |
|:-----|:----|
| npm | `agent-skill-porter` |
| 最新版本 | v8.0.0 (2026-04-01) |
| 许可证 | MIT |
| 作者 | hatappo |

### 核心命令

| 命令 | 功能 |
|:-----|:------|
| `sk add` | 从 GitHub 安装 skill |
| `sk update` | 从上游更新 skill |
| `sk list` | 列出所有 skill |
| `sk sync <src> <dst>` | Agent 间直接转换 |

### 关键特性

- **Chimera Hub**: 无损往返转换（保留各 Agent 特有设置）
- **Provenance Tracking**: 追踪 skill 来源（owner/repo@SHA）
- **Cross-Agent 占位符转换**: `$ARGUMENTS` ↔ `{{args}}` 自动转换
- **Dry-Run**: `-n` 预览

### 对我们项目的启示

1. **Chimera Hub 模式**: 中间格式 + 编解码器的解耦设计与我们的 converter 架构一致
2. **Provenance 追踪**: 值得在 EPIC-007 的 manifest_builder 中参考

---

## 差异化总结

| 能力 | SkillKit | Agent Skill Porter | EPIC-007 (目标) |
|:-----|:--------:|:-----------------:|:--------------:|
| 格式翻译 | ✅ 46 Agent | ✅ 7 Agent | ❌ 不做（复用标准） |
| 语义分组 | ❌ | ❌ | ✅ LLM 驱动 |
| 经验提取 | ❌ | ❌ | ✅ LLM 驱动 |
| 治理闭环 | ❌ | ❌ | ✅ scan+fix |
| 包管理 | ✅ | ✅ | ✅ 已有 |

**结论**: EPIC-007 的独特价值不在于「格式转换」，而在于「将扁平 skill 目录组织成语义能力包」——这是 SkillKit 和 Agent Skill Porter 都不做的事。
