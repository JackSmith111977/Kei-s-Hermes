---
name: library-skill
version: 1.0.0
description: "Use when ..."
author: "boku (Emma)"
license: MIT
design_pattern: Tool-Wrapper
skill_type: Research
category: research
tags:
  - library
  - index
triggers:
  - 库
  - 索引
  - 资源
depends_on: []
related_skills:
  - another-skill
date_created: 2026-05-17
date_updated: 2026-05-17
sqs_target: 80
---
# Library Name

## Overview

A curated collection of resources, references, and tools related to a specific domain. This skill serves as an index — load it first to find what you need, then drill into specific sub-skills.

## When to Use

- Exploring a new domain
- Need an overview of available resources
- Looking for the right tool for a specific task

## Index

### Category A

| Resource | Description | Location |
|:---------|:------------|:---------|
| Resource 1 | What it does | `skills/{cat}/{name}/` |
| Resource 2 | What it does | `skills/{cat}/{name}/` |
| Resource 3 | What it does | `skills/{cat}/{name}/` |

### Category B

| Resource | Description | Location |
|:---------|:------------|:---------|
| Resource 4 | What it does | `skills/{cat}/{name}/` |
| Resource 5 | What it does | `skills/{cat}/{name}/` |

## Quick Reference

### Tool A

```bash
tool-a command --option value
```

### Tool B

```python
from library import module
module.function(param="value")
```

## Common Pitfalls

1. **Outdated index**: Resources may have moved → Check `date_updated` before relying on paths

2. **Missing context**: Loading sub-skill without reading this index first → Always start here

## Verification Checklist

- [ ] All indexed resources exist at specified paths
- [ ] Each sub-skill has accurate description
- [ ] `date_updated` reflects last index audit
