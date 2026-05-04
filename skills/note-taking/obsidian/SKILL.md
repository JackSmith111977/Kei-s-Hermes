---
name: obsidian
description: Read, search, and create notes in the Obsidian vault.
triggers:
- obsidian
- obsidian
metadata:
  hermes:
    tags: []
---
# Obsidian Vault

**Location:** Set via `OBSIDIAN_VAULT_PATH` environment variable (e.g. in `~/.hermes/.env`).

If unset, defaults to `~/Documents/Obsidian Vault`.

Note: Vault paths may contain spaces - always quote them.

## Read a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat "$VAULT/Note Name.md"
```

## List notes

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# All notes
find "$VAULT" -name "*.md" -type f

# In a specific folder
ls "$VAULT/Subfolder/"
```

## Search

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# By filename
find "$VAULT" -name "*.md" -iname "*keyword*"

# By content
grep -rli "keyword" "$VAULT" --include="*.md"
```

## Create a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat > "$VAULT/New Note.md" << 'ENDNOTE'
# Title

Content here.
ENDNOTE
```

## Append to a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
echo "
New content here." >> "$VAULT/Existing Note.md"
```

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Bases Core Plugin (New in 2026)

The **Bases** core plugin was released in early 2026 and adds built-in List, Table, and Card views powered by note properties (YAML frontmatter). The community describes it as the best addition to Obsidian ever. It eliminates the need for Dataview for basic database-like views.

Example: Create a table view of all books you've read:

```yaml
---
type: book
author: "Smith, J."
year: 2025
status: read
rating: 4
---
# Book Title
Notes here...
```

Bases can then filter, sort, and display these notes as a table, list, or kanban board — all built-in, no plugin needed.

## Essential Plugins for 2026 Workflows

| Plugin | Use Case |
| --- | --- |
| **Bases** (core) | List/Table/Card views from note properties — replaces basic Dataview queries |
| **Tasks** | Due dates, recurring tasks, task queries across the vault |
| **Dataview** | Advanced database-like queries (still needed for complex aggregations) |
| **Kanban** | Board views for project management |
| **Calendar** | Calendar-based note navigation and daily notes |
| **Excalidraw / Canvas** | Visual diagramming, whiteboards, mind maps |
| **Note Explorer** | Scroll-through note browser with content preview |
| **Project Browser** | Replaces default tab view with intuitive file explorer |
| **Advanced New File** | Create notes in specific folders with templates |
| **Zotero Integration** | Auto-sync academic paper metadata and highlights |
| **Readwise** | Auto-import highlights from Kindle, articles, tweets |

## Zettelkasten / PKM Workflow

Obsidian excels as a "second brain" using the Zettelkasten method:

1. **Fleeting notes** — quick captures of ideas
2. **Literature notes** — one note per source (book, paper, article) with YAML frontmatter:
   ```yaml
   ---
   author: "Smith, J."
   year: 2025
   source: "Journal of AI Research"
   status: read
   ---
   ```
3. **Concept notes** (permanent notes) — atomic ideas extracted from sources
4. **Project notes** — active work that links to concept and literature notes

Key advantage: `[[backlinks]]` show everywhere a concept is referenced, revealing unexpected connections. The **Graph View** visualizes knowledge clusters.

## AI Integration Patterns (2026)

Obsidian's approach to AI is **open and composable**:
- **Claude Agent SDK** (formerly Claude Code SDK) enables agents that can do research, write drafts, reorganize notes, and search the web
- Data stays local (plain Markdown files on device)
- Users choose their own AI model
- Custom MCP tools can extend agent capabilities
- Multiple agents can be combined for complex workflows

This contrasts with Notion's closed AI — Obsidian's agent approach keeps data sovereignty while enabling powerful automation.

## When to Use Obsidian vs Notion

| Criterion | Obsidian | Notion |
| --- | --- | --- |
| **Data format** | Plain Markdown (local files) | Proprietary database (cloud) |
| **Collaboration** | Weak (no real-time multi-user) | Strong (real-time editing) |
| **Structure** | Associative links (graph) | Structured databases (tables) |
| **API** | Plugin API (internal only) | REST API (external integrations) |
| **Best for** | Personal knowledge, research, writing | Team wikis, project tracking, content calendars |
| **AI approach** | Open, local, composable | Closed, cloud-based, integrated |
| **Offline** | Full offline support | Limited offline |

**Not ideal for:** Real-time collaborative editing, large binary file storage, highly structured databases with complex permissions, heavy transactional workflows requiring real-time sync.
