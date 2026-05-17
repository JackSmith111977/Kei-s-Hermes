---
name: reference-skill
version: 1.0.0
description: "Use when ..."
author: "boku (Emma)"
license: MIT
design_pattern: Tool-Wrapper
skill_type: Reference
category: dogfood
tags:
  - reference
  - api
triggers:
  - 参考
  - API
  - 速查
depends_on:
  - web-access
related_skills:
  - another-skill
date_created: 2026-05-17
date_updated: 2026-05-17
sqs_target: 80
---
# Reference Title

## Overview

What this reference covers and when to consult it.

## When to Use

- Need to look up X
- Need to configure Y
- Need to debug Z

## Quick Reference Table

| Parameter | Type | Default | Description |
|:----------|:----:|:-------:|:------------|
| `param1` | string | `"default"` | Description 1 |
| `param2` | int | `0` | Description 2 |
| `param3` | bool | `false` | Description 3 |

## Common Patterns

### Pattern 1: Name

```bash
command --option value
```

### Pattern 2: Name

```python
function_name(param1="value")
```

## Common Pitfalls

1. **Wrong parameter**: Using X instead of Y → Use Y for correct behavior

2. **Version mismatch**: Feature Z not available in version < 2.0 → Upgrade to 2.0+

## Verification Checklist

- [ ] All parameters are documented
- [ ] At least 3 usage examples
- [ ] Cross-reference links verified
