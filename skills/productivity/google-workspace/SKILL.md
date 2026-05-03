---
name: google-workspace
description: Gmail, Calendar, Drive, Contacts, Sheets, and Docs integration for Hermes. ...
version: 1.0.0
triggers:
- google workspace
- google-workspace
author: Nous Research
license: MIT
metadata:
  hermes:
    tags:
    - Google
    - Gmail
    - Calendar
    - Drive
    - Sheets
    - Docs
    - Contacts
    - Email
    - OAuth
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills:
    - himalaya
---
# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, and Docs — through Hermes-managed OAuth and a thin CLI wrapper. When `gws` is installed, the skill uses it as the execution backend for broader Google Workspace coverage; otherwise it falls back to the bundled Python client implementation.

## References

- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)


> 🔍 **## Scripts** moved to [references/detailed.md](references/detailed.md)
