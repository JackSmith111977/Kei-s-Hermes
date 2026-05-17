---
name: generator-skill
version: 1.0.0
description: "Use when ..."
author: "boku (Emma)"
license: MIT
design_pattern: Generator
skill_type: Generator
category: dogfood
tags:
  - generation
  - template
triggers:
  - 生成
  - 创建
  - 模板
depends_on:
  - web-access
related_skills:
  - another-skill
date_created: 2026-05-17
date_updated: 2026-05-17
sqs_target: 80
---
# Generator Name

## Overview

Generates structured output from input specifications. Follows the Generator design pattern: input → transformation → validated output.

## When to Use

- Generate standardized documents
- Create code from specifications
- Produce configuration files

## Input Specification

```yaml
input_field_1: "value"    # Required: Description
input_field_2: 42          # Optional: Default = 0
input_field_3: true        # Optional: Default = false
```

## Output Format

```json
{
  "output_1": "generated value",
  "output_2": 42,
  "metadata": {
    "generator": "generator-skill",
    "version": "1.0.0"
  }
}
```

## Generation Steps

### Step 1: Validate Input

```python
def validate(input):
    assert input.input_field_1 is not None
    return True
```

### Step 2: Transform

```python
def transform(input):
    output = {
        "output_1": process(input.input_field_1),
        "output_2": input.input_field_2 * 2
    }
    return output
```

### Step 3: Output

Return the generated result in the specified format.

## Examples

### Example 1: Basic Usage

Input: `{input_field_1: "hello", input_field_2: 21}`

Output: `{output_1: "HELLO", output_2: 42}`

## Common Pitfalls

1. **Missing required field**: Generator fails with unclear error → Always validate input first

2. **Output format mismatch**: Downstream consumer expects different schema → Check output format section

## Verification Checklist

- [ ] Input validation catches all required fields
- [ ] Output matches specified format
- [ ] Edge cases handled (empty input, extreme values)
