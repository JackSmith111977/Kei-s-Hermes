---
name: claude-code
description: Delegate coding tasks to Claude Code (Anthropic's CLI agent). Use for build...
version: 2.2.0
triggers:
- claude code
- codex
- agent
- 编程助手
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags:
    - Coding-Agent
    - Claude
    - Anthropic
    - Code-Review
    - Refactoring
    - PTY
    - Automation
    related_skills:
    - codex
    - hermes-agent
    - opencode
---
> 🔍 **Claude Code — Hermes Orchestration Guide**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Prerequisites**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Two Orchestration Modes**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Mode 1: Print Mode (`-p`) — Non-Interactive (PREFERRED for most tasks)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Mode 2: Interactive PTY via tmux — Multi-Turn Sessions**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Start a tmux session**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Launch Claude Code inside it**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Wait for startup, then send your task**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **(after ~3-5 seconds for the welcome screen)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Monitor progress by capturing the pane**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Send follow-up tasks**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Exit when done**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **PTY Dialog Handling (CRITICAL for Interactive Mode)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Dialog 1: Workspace Trust (first visit to a directory)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Dialog 2: Bypass Permissions Warning (only with --dangerously-skip-permissions)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Robust Dialog Handling Pattern**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Launch with permissions bypass**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Handle trust dialog (Enter for default "Yes")**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Handle permissions dialog (Down then Enter for "Yes, I accept")**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Now wait for Claude to work**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **CLI Subcommands**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Print Mode Deep Dive**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Structured JSON Output**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Streaming JSON Output**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Bidirectional Streaming**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Piped Input**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Pipe a file for analysis**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Pipe multiple files**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Pipe command output**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **JSON Schema for Structured Extraction**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Session Continuation**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Start a task**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Resume with session ID**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Or resume the most recent session in the same directory**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Fork a session (new ID, keeps history)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Bare Mode for CI/Scripting**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Fallback Model for Overload**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Complete CLI Flags Reference**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Session & Environment**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Model & Performance**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Permission & Safety**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Output & Input Format**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **System Prompt & Context**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Debugging**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Agent Teams**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Tool Name Syntax for --allowedTools / --disallowedTools**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Settings & Configuration**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Settings Hierarchy (highest to lowest priority)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Permissions in Settings**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Memory Files (CLAUDE.md) Hierarchy**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Interactive Session: Slash Commands**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Session & Context**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Development & Review**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **### Configuration & Tools**: Moved to [references/detailed.md](references/detailed.md)### Custom Slash Commands
> 🔍 **.claude/commands/deploy.md**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Skills (Natural Language Invocation)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **.claude/skills/database-migration.md**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Interactive Session: Keyboard Shortcuts**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **General Controls**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Mode Toggles**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Multiline Input**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Input Prefixes**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Pro Tip: "ultrathink"**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **PR Review Pattern**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Quick Review (Print Mode)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Deep Review (Interactive + Worktree)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **PR Review from Number**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Claude Worktree with tmux**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Parallel Claude Instances**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Task 1: Fix backend**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Task 2: Write tests**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Task 3: Update docs**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Monitor all**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **CLAUDE.md — Project Context File**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Project: My API**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Architecture**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Key Commands**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Code Standards**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Rules Directory (Modular CLAUDE.md)**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Auto-Memory**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Custom Subagents**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Agent Location Priority**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Creating an Agent**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **.claude/agents/security-reviewer.md**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Dynamic Agents via CLI**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Hooks — Automation on Events**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **All 8 Hook Types**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Hook Environment Variables**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **### Security Hook Examples**: Moved to [references/detailed.md](references/detailed.md)## MCP Integration
> 🔍 **GitHub integration**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **PostgreSQL queries**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Puppeteer for web testing**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **MCP Scopes**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **MCP in Print/CI Mode**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **MCP Limits & Tuning**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Monitoring Interactive Sessions**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Reading the TUI Status**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Periodic capture to check if Claude is still working or waiting for input**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Context Window Health**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Environment Variables**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Cost & Performance Tips**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Pitfalls & Gotchas**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Rules for Hermes Agents**: Moved to [references/advanced-usage.md](references/advanced-usage.md)
> 🔍 **Full Command Reference & Deep Dives**: Moved to [references/advanced-usage.md](references/advanced-usage.md)