---
name: notion
description: Notion API for creating and managing pages, databases, and blocks via curl....
version: 1.0.0
triggers:
- notion
- notion
author: community
license: MIT
metadata:
  hermes:
    tags:
    - Notion
    - Productivity
    - Notes
    - Database
    - API
    homepage: https://developers.notion.com
prerequisites:
  env_vars:
  - NOTION_API_KEY
---
# Notion API

Use the Notion API via curl to create, read, update pages, databases (data sources), and blocks. No extra tools needed — just curl and a Notion API key.

## Prerequisites

1. Create an integration at https://notion.so/my-integrations
2. Copy the API key (starts with `ntn_` or `secret_`)
3. Store it in `~/.hermes/.env`:
   ```
   NOTION_API_KEY=ntn_your_key_here
   ```
4. **Important:** Share target pages/databases with your integration in Notion (click "..." → "Connect to" → your integration name)

## API Basics

All requests use this pattern:

```bash
curl -s -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

The `Notion-Version` header is required. This skill uses `2025-09-03` (latest). In this version, databases are called "data sources" in the API.

## Common Operations

### Search

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'
```

### Get Page

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Get Page Content (blocks)

```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Create Page in a Database

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }'
```

### Query a Database

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

### Create a Database

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
      "Date": {"date": {}}
    }
  }'
```

### Update Page Properties

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

### Add Content to a Page

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello from Hermes!"}}]}}
    ]
  }'
```

## Property Types

Common property formats for database items:

- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}`
- **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **Date:** `{"date": {"start": "2026-01-15", "end": "2026-01-16"}}`
- **Checkbox:** `{"checkbox": true}`
- **Number:** `{"number": 42}`
- **URL:** `{"url": "https://..."}`
- **Email:** `{"email": "user@example.com"}`
- **Relation:** `{"relation": [{"id": "page_id"}]}`

## Key Differences in API Version 2025-09-03

- **Databases → Data Sources:** Use `/data_sources/` endpoints for queries and retrieval
- **Two IDs:** Each database has both a `database_id` and a `data_source_id`
  - Use `database_id` when creating pages (`parent: {"database_id": "..."}`)
  - Use `data_source_id` when querying (`POST /v1/data_sources/{id}/query`)
- **Search results:** Databases return as `"object": "data_source"` with their `data_source_id`

## Notes

- Page/database IDs are UUIDs (with or without dashes)
- Rate limit: ~3 requests/second average
- The API cannot set database view filters — that's UI-only
- Use `is_inline: true` when creating data sources to embed them in pages
- Add `-s` flag to curl to suppress progress bars (cleaner output for Hermes)
- Pipe output through `jq` for readable JSON: `... | jq '.results[0].properties'`


> 🔍 **详细参考**: 更多内容请查阅 [block-types.md](block-types.md)

## Common Workflow Patterns (2026)

### Architectural Decision Records (ADR)

Use a Notion database to track technical decisions:

**Properties:** `Title` (title), `Status` (select: Proposed/Accepted/Deprecated), `Date` (date), `Decision Makers` (multi-select), `Context` (rich text), `Related Project` (relation).

This pattern optimizes for **browsing and filtering** structured decisions across projects — great for team visibility.

### Content Calendar / Editorial Workflow

A typical content creator's Notion workspace:
- **Master content database** with properties: title, status, publish date, target keyword, word count, assigned writer
- **Connected databases** for social media repurposing
- **Embedded calendar views** showing publication schedule across all platforms
- **Automation**: Use the API + Zapier/Make/n8n to auto-create pages from form submissions or update statuses from Slack

### Team Wiki / Knowledge Base

- Use nested pages with a clear hierarchy
- Link related docs using `@mentions` and page links
- Use database views (Table, Board, Calendar, Gallery, Timeline) to present the same data differently
- AI features within documents can summarize, edit, and generate content

## Notion vs Obsidian — When to Use Which

| Criterion | Notion | Obsidian |
| --- | --- | --- |
| **Optimizes for** | Browsing and filtering structured lists | Following associative links through a knowledge graph |
| **Collaboration** | Real-time multi-user editing | No real-time collaboration |
| **AI Integration** | Built-in, closed AI within documents | Open, composable AI via plugins/agents |
| **Data portability** | Export required (proprietary format) | Plain Markdown files (always portable) |
| **External API** | Full REST API for automation | Plugin API only (internal) |
| **Best use case** | Team wikis, project tracking, content calendars | Personal knowledge, research, writing |

## 2026 Productivity Trends

- **Unified AI workspaces**: Teams are moving away from scattered tool stacks toward central intelligence hubs that combine knowledge management, collaboration, and AI
- **Async-first communication**: Remote teams prioritize written async updates over meetings; weekly written check-ins (what moved forward, what's blocked, what needs a decision) replace status meetings
- **Onboarding as a product**: Knowledge bases with clear ownership and regular updates are the #1 productivity lever for remote team onboarding
- **AI-powered task prioritization**: Tools now intelligently prioritize tasks and suggest optimal scheduling, transforming task management from manual chore to automated process
- **Raycast + Superhuman**: Power users combine Raycast (launcher/automation) with Superhuman (email) for speed-centric workflows
- **Capacities**: Emerging knowledge management tool alongside Obsidian, with object-based note organization
