---
name: obliteratus
description: Remove refusal behaviors from open-weight LLMs using OBLITERATUS — mechanis...
version: 2.0.0
triggers:
- obliteratus
- obliteratus
author: Hermes Agent
license: MIT
dependencies:
- obliteratus
- torch
- transformers
- bitsandbytes
- accelerate
- safetensors
metadata:
  hermes:
    tags:
    - Abliteration
    - Uncensoring
    - Refusal-Removal
    - LLM
    - Weight-Projection
    - SVD
    - Mechanistic-Interpretability
    - HuggingFace
    - Model-Surgery
    related_skills:
    - vllm
    - gguf
    - huggingface-tokenizers
---
# OBLITERATUS Skill

Remove refusal behaviors (guardrails) from open-weight LLMs without retraining or fine-tuning. Uses mechanistic interpretability techniques — including diff-in-means, SVD, whitened SVD, LEACE concept erasure, SAE decomposition, Bayesian kernel projection, and more — to identify and surgically excise refusal directions from model weights while preserving reasoning capabilities.

**License warning:** OBLITERATUS is AGPL-3.0. NEVER import it as a Python library. Always invoke via CLI (`obliteratus` command) or subprocess. This keeps Hermes Agent's MIT license clean.

## When to Use This Skill

Trigger when the user:
- Wants to "uncensor" or "abliterate" an LLM
- Asks about removing refusal/guardrails from a model
- Wants to create an uncensored version of Llama, Qwen, Mistral, etc.
- Mentions "refusal removal", "abliteration", "weight projection"
- Wants to analyze how a model's refusal mechanism works
- References OBLITERATUS, abliterator, or refusal directions

## Step 1: Installation

Check if already installed:
```bash
obliteratus --version 2>/dev/null && echo "INSTALLED" || echo "NOT INSTALLED"
```

If not installed, clone and install from GitHub:
```bash
git clone https://github.com/elder-plinius/OBLITERATUS.git
cd OBLITERATUS
pip install -e .
# For Gradio web UI support:
# pip install -e ".[spaces]"
```

**IMPORTANT:** Confirm with user before installing. This pulls in ~5-10GB of dependencies (PyTorch, Transformers, bitsandbytes, etc.).

## Step 2: Check Hardware

Before anything, check what GPU is available:
```bash
python3 -c "
import torch
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'GPU: {gpu}')
    print(f'VRAM: {vram:.1f} GB')
    if vram < 4: print('TIER: tiny (models under 1B)')
    elif vram < 8: print('TIER: small (models 1-4B)')
    elif vram < 16: print('TIER: medium (models 4-9B with 4bit quant)')
    elif vram < 32: print('TIER: large (models 8-32B with 4bit quant)')
    else: print('TIER: frontier (models 32B+)')
else:
    print('NO GPU - only tiny models (under 1B) on CPU')
"
```

### VRAM Requirements (with 4-bit quantization)

| VRAM     | Max Model Size  | Example Models                              |
|:---------|:----------------|:--------------------------------------------|
| CPU only | ~1B params      | GPT-2, TinyLlama, SmolLM                    |
| 4-8 GB   | ~4B params      | Qwen2.5-1.5B, Phi-3.5 mini, Llama 3.2 3B   |
| 8-16 GB  | ~9B params      | Llama 3.1 8B, Mistral 7B, Gemma 2 9B       |
| 24 GB    | ~32B params     | Qwen3-32B, Llama 3.1 70B (tight), Command-R |
| 48 GB+   | ~72B+ params    | Qwen2.5-72B, DeepSeek-R1                    |
| Multi-GPU| 200B+ params    | Llama 3.1 405B, DeepSeek-V3 (685B MoE)      |


> 🔍 **## Step 3: Browse Available Models** moved to [references/detailed.md](references/detailed.md)
