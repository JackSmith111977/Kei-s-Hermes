---
name: llama-cpp
description: Run LLM inference with llama.cpp on CPU, Apple Silicon, AMD/Intel GPUs, or ...
version: 2.0.0
triggers:
- llama cpp
- llama-cpp
author: Orchestra Research
license: MIT
dependencies:
- llama-cpp-python>=0.2.0
metadata:
  hermes:
    tags:
    - llama.cpp
    - GGUF
    - Quantization
    - CPU Inference
    - Apple Silicon
    - Edge Deployment
    - Non-NVIDIA
    - AMD GPUs
    - Intel GPUs
    - Embedded
    - Model Compression
---
# llama.cpp + GGUF

Pure C/C++ LLM inference with minimal dependencies, plus the GGUF (GPT-Generated Unified Format) standard used for quantized weights. One toolchain covers conversion, quantization, and serving.

## When to use

**Use llama.cpp + GGUF when:**
- Running on CPU-only machines or Apple Silicon (M1/M2/M3/M4) with Metal acceleration
- Using AMD (ROCm) or Intel GPUs where CUDA isn't available
- Edge deployment (Raspberry Pi, embedded systems, consumer laptops)
- Need flexible quantization (2–8 bit with K-quants)
- Want local AI tools (LM Studio, Ollama, text-generation-webui, koboldcpp)
- Want a single binary deploy without Docker/Python

**Key advantages:**
- Universal hardware: CPU, Apple Silicon, NVIDIA, AMD, Intel
- No Python runtime required (pure C/C++)
- K-quants + imatrix for better low-bit quality
- OpenAI-compatible server built in
- Rich ecosystem (Ollama, LM Studio, llama-cpp-python)

**Use alternatives instead:**
- **vLLM** — NVIDIA GPUs, PagedAttention, Python-first, max throughput
- **TensorRT-LLM** — Production NVIDIA (A100/H100), maximum speed
- **AWQ/GPTQ** — Calibrated quantization for NVIDIA-only deployments
- **bitsandbytes** — Simple HuggingFace transformers integration
- **HQQ** — Fast calibration-free quantization

## Quick start

### Install

```bash
# macOS / Linux (simplest)
brew install llama.cpp

# Or build from source
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
make                        # CPU
make GGML_METAL=1           # Apple Silicon
make GGML_CUDA=1            # NVIDIA CUDA
make LLAMA_HIP=1            # AMD ROCm

# Python bindings (optional)
pip install llama-cpp-python
# With CUDA:   CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
# With Metal:  CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

### Download a pre-quantized GGUF

```bash
# TheBloke hosts most popular models pre-quantized
huggingface-cli download \
    TheBloke/Llama-2-7B-Chat-GGUF \
    llama-2-7b-chat.Q4_K_M.gguf \
    --local-dir models/
```

### Or convert a HuggingFace model to GGUF

```bash
# 1. Download HF model
huggingface-cli download meta-llama/Llama-3.1-8B --local-dir ./llama-3.1-8b

# 2. Convert to FP16 GGUF
python convert_hf_to_gguf.py ./llama-3.1-8b \
    --outfile llama-3.1-8b-f16.gguf \
    --outtype f16

# 3. Quantize to Q4_K_M
./llama-quantize llama-3.1-8b-f16.gguf llama-3.1-8b-q4_k_m.gguf Q4_K_M
```

### Run inference

```bash
# One-shot prompt
./llama-cli -m model.Q4_K_M.gguf -p "Explain quantum computing" -n 256

# Interactive chat
./llama-cli -m model.Q4_K_M.gguf --interactive

# With GPU offload
./llama-cli -m model.Q4_K_M.gguf -ngl 35 -p "Hello!"
```

### Serve an OpenAI-compatible API

```bash
./llama-server \
    -m model.Q4_K_M.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -ngl 35 \
    -c 4096 \
    --parallel 4 \
    --cont-batching
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```


> 🔍 **## Quantization** moved to [references/detailed.md](references/detailed.md)
