# OpenCode Config Schema Reference

> Collected from official docs at https://opencode.ai/docs/ and live CLI inspection.
> Last verified: 2026-05-13 (opencode v1.14.41)

## Paths (from `opencode debug paths`)

```
home       ~/
data       ~/.local/share/opencode
bin        ~/.cache/opencode/bin
log        ~/.local/share/opencode/log
cache      ~/.cache/opencode
config     ~/.config/opencode
state      ~/.local/state/opencode
tmp        /tmp/opencode
```

## Database

Skills, MCP servers, sessions, and agents are stored in SQLite:
`~/.local/share/opencode/opencode.db`

## CLI Diagnostics

```bash
opencode debug paths       # 全局路径
opencode debug config      # 解析后的配置 JSON
opencode debug skill       # 已发现的 skill 列表
opencode debug agent <name>  # Agent 配置详情
opencode debug scrap       # 已知项目列表
opencode debug startup     # 启动时序
opencode debug info        # 完整调试信息
```

## SKILL.md Frontmatter

Only these fields recognized (others silently ignored):

| Field | Required | Validation |
|:------|:--------:|:-----------|
| `name` | ✅ | 1-64 chars, `^[a-z0-9]+(-[a-z0-9]+)*$`, must match dir name |
| `description` | ✅ | 1-1024 chars |
| `license` | ❌ | Free text |
| `compatibility` | ❌ | Free text (e.g. `opencode`) |
| `metadata` | ❌ | String-to-string map |

## MCP Config Format (in opencode.json)

```json
{
  "mcp": {
    "server-name": {
      "type": "local",
      "command": ["npx", "-y", "@package"],
      "environment": { "KEY": "value" }
    }
  }
}
```

- `type`: `"local"` (stdio) or omitted (defaults to local)
- `command`: array of strings. If string given, wrapped as `["bash", "-c", "..."]`
- `environment`: optional env vars

## Environment Variables

| Variable | Effect |
|:---------|:-------|
| `OPENCODE_CONFIG` | Custom config path |
| `OPENCODE_CONFIG_CONTENT` | Inline JSON config |
| `OPENCODE_CONFIG_DIR` | Custom config directory |
| `OPENCODE_DISABLE_CLAUDE_CODE` | Disable all `.claude` support |
| `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT` | Disable `~/.claude/CLAUDE.md` |
| `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` | Disable `.claude/skills` |
| `OPENCODE_DISABLE_MODELS_FETCH` | Disable remote model fetching |
| `OPENCODE_ENABLE_EXA` | Enable Exa web search |
| `OPENCODE_SERVER_PASSWORD` | Basic auth for serve/web mode |
| `OPENCODE_SERVER_USERNAME` | Override basic auth username |
| `OPENCODE_MODELS_URL` | Custom models config URL |
| `OPENCODE_CLIENT` | Client identifier (default: `cli`) |
| `OPENCODE_FAKE_VCS` | Fake VCS provider for testing |
