---
name: outlines
description: Guarantee valid JSON/XML/code structure during generation, use Pydantic mod...
version: 1.0.0
triggers:
- outlines
- outlines
author: Orchestra Research
license: MIT
dependencies:
- outlines
- transformers
- vllm
- pydantic
metadata:
  hermes:
    tags:
    - Prompt Engineering
    - Outlines
    - Structured Generation
    - JSON Schema
    - Pydantic
    - Local Models
    - Grammar-Based Generation
    - vLLM
    - Transformers
    - Type Safety
---
# Outlines: Structured Text Generation

## When to Use This Skill

Use Outlines when you need to:
- **Guarantee valid JSON/XML/code** structure during generation
- **Use Pydantic models** for type-safe outputs
- **Support local models** (Transformers, llama.cpp, vLLM)
- **Maximize inference speed** with zero-overhead structured generation
- **Generate against JSON schemas** automatically
- **Control token sampling** at the grammar level

**GitHub Stars**: 8,000+ | **From**: dottxt.ai (formerly .txt)

## Installation

```bash
# Base installation
pip install outlines

# With specific backends
pip install outlines transformers  # Hugging Face models
pip install outlines llama-cpp-python  # llama.cpp
pip install outlines vllm  # vLLM for high-throughput
```

## Quick Start

### Basic Example: Classification

```python
import outlines
from typing import Literal

# Load model
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Generate with type constraint
prompt = "Sentiment of 'This product is amazing!': "
generator = outlines.generate.choice(model, ["positive", "negative", "neutral"])
sentiment = generator(prompt)

print(sentiment)  # "positive" (guaranteed one of these)
```

### With Pydantic Models

```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Generate structured output
prompt = "Extract user: John Doe, 30 years old, john@example.com"
generator = outlines.generate.json(model, User)
user = generator(prompt)

print(user.name)   # "John Doe"
print(user.age)    # 30
print(user.email)  # "john@example.com"
```


> 🔍 **## Core Concepts** moved to [references/detailed.md](references/detailed.md)
