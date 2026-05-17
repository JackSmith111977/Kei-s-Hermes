---
name: checklist-skill
version: 1.0.0
description: "Use when ..."
author: "boku (Emma)"
license: MIT
design_pattern: External-Gate
skill_type: Checklist
category: dogfood
tags:
  - checklist
  - quality
  - verification
triggers:
  - 检查清单
  - 验收
  - 质量检查
depends_on: []
related_skills:
  - another-skill
date_created: 2026-05-17
date_updated: 2026-05-17
sqs_target: 80
---
# Checklist Name

## Overview

A structured checklist to ensure quality and completeness when performing a specific task.

## When to Use

- Before releasing/deploying
- After completing a complex task
- As part of a review process

## Pre-requisites

- [ ] Environment is ready
- [ ] Required tools installed
- [ ] Previous steps completed

## Checklist

### Section 1: Preparation

- [ ] Task 1: Description of what to check
  - Command: `verify-command-1`
- [ ] Task 2: Description of what to check
  - Command: `verify-command-2`

### Section 2: Execution

- [ ] Task 3: Description
  - Expected: specific output or behavior
- [ ] Task 4: Description
  - Expected: specific output or behavior

### Section 3: Verification

- [ ] Task 5: Description
  - Verify by: `verification-command`
- [ ] Task 6: Description
  - Verify by: manual inspection

## Scoring

| Items Passed | Verdict |
|:------------:|:--------|
| 6/6 | ✅ Pass |
| 4-5/6 | ⚠️ Needs Review |
| < 4/6 | ❌ Fail |

## Common Pitfalls

1. **Skipping pre-requisites**: Results in false negatives → Always complete pre-reqs first

2. **Assuming pass without verification**: Trust but verify → Run each check explicitly

## Results Log

```json
{
  "checklist": "checklist-name",
  "date": "2026-05-17",
  "passed": 0,
  "total": 6,
  "verdict": "PENDING"
}
```
