---
name: workflow-skill
version: 1.0.0
description: "Use when ..."
author: "boku (Emma)"
license: MIT
design_pattern: Pipeline
skill_type: Workflow
category: dogfood
tags:
  - workflow
  - automation
triggers:
  - 流程
  - 工作流
  - 步骤
depends_on:
  - web-access
related_skills:
  - another-skill
date_created: 2026-05-17
date_updated: 2026-05-17
sqs_target: 80
---
# Workflow Name

## Overview

1-2 paragraphs explaining what this workflow does and why it's needed.

## When to Use

- Trigger scenario 1
- Trigger scenario 2
- Trigger scenario 3

**Don't use for:**
- Anti-pattern 1
- Anti-pattern 2

## Workflow Steps

### Step 1: Step Name

```bash
# Concrete command
command --option value
```

**Expected output**: ...

### Step 2: Step Name

```python
# Code example
def example():
    pass
```

**Expected output**: ...

## Common Pitfalls

1. **Pitfall description**: Consequence → Solution

2. **Pitfall description**: Consequence → Solution

3. **Pitfall description**: Consequence → Solution

## Verification Checklist

- [ ] Run `command` — should output X
- [ ] Check file Y exists and contains Z
- [ ] Verify step 2 result matches expected output

## Eval Cases

- **Case 1**: Input X → Expected: command Y succeeds
- **Case 2**: Input Z → Expected: error message W
