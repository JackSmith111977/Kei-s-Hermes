---
name: opencode
description: "OpenCode CLI Agent — platform architecture, skill system, MCP configuration, rules/instructions, and task delegation. Covers all aspects of the OpenCode ecosystem: how to USE it as a coding worker AND how to CONFIGURE it (skills, MCP, rules, agents)."
version: 2.0.0
triggers:
  - opencode
  - opencode-ai
  - opencode skill
  - opencode mcp
  - opencode config
  - opencode agent
  - opencode rules
  - opencode architecture
  - skill discovery
  - opencode debug skill
author: boku (Emma)
license: MIT
metadata:
  hermes:
    tags:
      - Coding-Agent
      - OpenCode
      - Autonomous
      - Platform
      - Skills
      - MCP
      - Config
    category: autonomous-ai-agents
    skill_type: platform-guide
    design_pattern: reference
    related_skills:
      - claude-code
      - codex
      - hermes-agent
      - native-mcp
depends_on: []

---

# OpenCode CLI 平台指南

> OpenCode 是一个 provider-agnostic 的开源 AI coding agent，支持 TUI/CLI/Server 三种运行模式。
> 本 skill 覆盖 OpenCode 的完整架构：技能系统、MCP 集成、配置管理、规则系统、Agent 管理。

---

## 一、架构总览

### 关键路径

| 用途 | 路径 | 说明 |
|:-----|:------|:------|
| 配置目录 | `~/.config/opencode/` | 全局配置、skills、agents |
| 数据目录 | `~/.local/share/opencode/` | SQLite 数据库 (opencode.db) |
| 缓存 | `~/.cache/opencode/bin` | 二进制缓存 |
| 日志 | `~/.local/share/opencode/log/` | 运行日志 |
| 临时文件 | `/tmp/opencode/` | 运行时临时文件 |
| 状态 | `~/.local/state/opencode/` | 持久化状态 |
| 二进制 | `~/.cache/opencode/bin/` | 下载的二进制文件 |

可用 `opencode debug paths` 快速查看当前环境的全部路径。

### 版本验证

```bash
opencode --version
which -a opencode           # 检查多个安装路径
opencode debug info         # 完整的调试信息
```

---

## 二、Skill 系统（Agent Skills）

OpenCode **原生支持 SKILL.md 标准**，与 Claude Code / Codex CLI 格式兼容。

### Skill 发现机制

OpenCode 自动扫描以下位置（无需手动注册）：

| 优先级 | 路径 | 作用域 |
|:------:|:-----|:-------|
| 1 | `.opencode/skills/{name}/SKILL.md` | 项目级 |
| 2 | `.claude/skills/{name}/SKILL.md` | 项目级（兼容） |
| 3 | `.agents/skills/{name}/SKILL.md` | 项目级（兼容） |
| 4 | `~/.config/opencode/skills/{name}/SKILL.md` | **全局级** |
| 5 | `~/.claude/skills/{name}/SKILL.md` | 全局级（兼容） |
| 6 | `~/.agents/skills/{name}/SKILL.md` | 全局级（兼容） |

> **注意**: OpenCode 会从当前目录向上遍历到 git worktree root，沿途加载所有 `skills/*/SKILL.md`。
> 全局 skill 始终加载。OpenCode 默认读取 `~/.claude/skills/`，除非设置 `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`。

### SKILL.md 格式

```markdown
---
name: skill-name          # 必须。1-64 字符，小写字母数字+连字符，匹配目录名
description: "..."        # 必须。1-1024 字符，用于 agent 选择
license: MIT              # 可选
compatibility: opencode   # 可选
metadata:                 # 可选，string-to-string map
  key: value
---

# Skill body here
Agent sees this full content when loading the skill via `skill({ name: "..." })`.
```

**Frontmatter 规则**:
- OpenCode **只识别**上述 5 个字段，其余被忽略
- `name` 必须匹配目录名，正则: `^[a-z0-9]+(-[a-z0-9]+)*$`
- 不满足规则的 skill 静默跳过（不会报错）

### Skill 权限控制

在 `opencode.json` 中配置 pattern-based 权限:

```json
{
  "permission": {
    "skill": {
      "*": "allow",
      "internal-*": "deny",
      "experimental-*": "ask"
    }
  }
}
```

| 值 | 行为 |
|:---|:-----|
| `allow` | 立即加载 |
| `deny` | 隐藏且不可访问 |
| `ask` | 需用户确认 |

### 诊断 Skill 加载

```bash
opencode debug skill               # 列出所有已发现的 skill
opencode debug skill | jq '.[].name'  # 仅查看名称
```

如果 skill 不出现:
1. 确认文件名是 `SKILL.md`（全大写）
2. 检查 frontmatter 包含 `name` 和 `description`
3. 检查名称唯一性
4. 检查权限规则

---

## 三、MCP 配置

### 通过 CLI 管理

```bash
opencode mcp add                  # 交互式添加（本地或远程）
opencode mcp list                 # 列出已配置的 MCP 服务器
opencode mcp auth <name>          # OAuth 认证
opencode mcp debug <name>         # 调试连接
opencode mcp logout <name>        # 清除 OAuth 凭据
```

### 通过 opencode.json 配置

```json
{
  "mcp": {
    "my-server": {
      "type": "local",
      "command": ["npx", "-y", "@org/package"],
      "environment": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

**格式说明**:
- `type`: `"local"`（stdio）或 `"remote"`（SSE）
- `command`: 数组形式，字符串会被包装为 `["bash", "-c", "..."]`
- `environment`: 环境变量映射

---

## 四、规则/指令系统

### AGENTS.md（主要方式）

OpenCode 按以下优先级加载指令文件：

1. **项目级**: `AGENTS.md` > `CLAUDE.md` > `CONTEXT.md`（从当前目录向上到 git root）
2. **全局级**: `~/.config/opencode/AGENTS.md` > `~/.claude/CLAUDE.md`

> 一旦找到某个类型的文件，同类型其他文件被忽略。
> 全局级和项目级会合并加载。

### opencode.json instructions 字段

```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md"
  ]
}
```

支持 glob 模式。与 AGENTS.md 文件叠加加载。

### 环境变量控制

```bash
OPENCODE_DISABLE_CLAUDE_CODE=1            # 禁用所有 .claude 读取
OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1     # 禁用 ~/.claude/CLAUDE.md
OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1     # 禁用 .claude/skills
```

---

## 五、Agent 管理

### CLI 命令

```bash
opencode agent list                          # 列出 agent
opencode agent create --path <dir> \         # 创建 agent
  --description "what it does" \
  --mode all|primary|subagent \
  --permissions "bash,read,edit,glob,grep,webfetch,task,skill" \
  --model provider/model
```

### Agent 配置（在 opencode.json 中）

```json
{
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices",
      "model": "anthropic/claude-sonnet-4-5",
      "prompt": "You are a code reviewer...",
      "tools": { "write": false, "edit": false },
      "permission": {
        "skill": { "*": "allow", "internal-*": "deny" }
      }
    }
  }
}
```

### 自定义 Agent 文件（markdown + YAML frontmatter）

创建 `~/.config/opencode/agents/my-agent.md`:

```markdown
---
permission:
  skill:
    "documents-*": allow
    "experimental-*": ask
tools:
  skill: true
---

# System prompt here
```

---

## 六、Config 文件格式

`opencode.json` 顶层结构：

```json
{
  "$schema": "https://opencode.ai/config.json",

  "model": "provider/model-id",
  "small_model": "provider/model-id",
  "provider": {},
  "disabled_providers": [],

  "theme": "opencode",
  "autoupdate": true,
  "tui": { "scroll_speed": 3 },
  "keybinds": {},

  "share": "manual",

  "tools": {},
  "permission": {},
  "agent": {},
  "command": {},

  "instructions": [],
  "mcp": {},

  "formatter": {}
}
```

### 配置搜索顺序

1. Remote config (`.well-known/opencode`)
2. Global config (`~/.config/opencode/opencode.json`)
3. Custom config (`OPENCODE_CONFIG` env var)
4. Project config (`opencode.json` in project)
5. `.opencode` directory (agents, commands, plugins)
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var)

---

## 七、任务委托（原有内容）

### 单次任务

```bash
opencode run 'Add retry logic to API calls and update tests' --workdir ~/project
opencode run 'Review config' -f config.yaml -f .env.example
opencode run 'Debug tests' --thinking
opencode run 'Refactor auth' --model openrouter/anthropic/claude-sonnet-4
```

### 交互式会话（后台）

```bash
# 启动
terminal(command="opencode", workdir="~/project", background=true, pty=true)

# 发送指令
process(action="submit", session_id="<id>", data="Implement OAuth refresh")

# 监控
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 安全退出 (不要用 /exit — 会触发 agent 选择器)
process(action="write", session_id="<id>", data="\x03")
# 或
process(action="kill", session_id="<id>")
```

### 二进制解析

```bash
which -a opencode            # 检查多路径
opencode --version           # 验证版本
$HOME/.opencode/bin/opencode # 固定路径（当默认 shell 路径不一致时）
```

---

## 八、参考资料

- 官方文档: https://opencode.ai/docs/skills/
- Rules 系统: https://dev.opencode.ai/docs/rules/
- Config 配置: https://open-code.ai/en/docs/config
- CLI 命令: https://dev.opencode.ai/docs/cli/
- Agent 配置: https://opencodeguide.com/en/docs/configure/agents/
