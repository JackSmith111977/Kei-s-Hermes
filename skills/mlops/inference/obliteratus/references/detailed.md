# Detailed Reference

## Step 3: Browse Available Models & Get Recommendations

```bash
# Browse models by compute tier
obliteratus models --tier medium

# Get architecture info for a specific model
obliteratus info <model_name>

# Get telemetry-driven recommendation for best method & params
obliteratus recommend <model_name>
obliteratus recommend <model_name> --insights  # global cross-architecture rankings
```

## Step 4: Choose a Method

### Method Selection Guide
**Default / recommended for most cases: `advanced`.** It uses multi-direction SVD with norm-preserving projection and is well-tested.

| Situation                         | Recommended Method | Why                                      |
|:----------------------------------|:-------------------|:-----------------------------------------|
| Default / most models             | `advanced`         | Multi-direction SVD, norm-preserving, reliable |
| Quick test / prototyping          | `basic`            | Fast, simple, good enough to evaluate    |
| Dense model (Llama, Mistral)      | `advanced`         | Multi-direction, norm-preserving         |
| MoE model (DeepSeek, Mixtral)     | `nuclear`          | Expert-granular, handles MoE complexity  |
| Reasoning model (R1 distills)     | `surgical`         | CoT-aware, preserves chain-of-thought    |
| Stubborn refusals persist         | `aggressive`       | Whitened SVD + head surgery + jailbreak   |
| Want reversible changes           | Use steering vectors (see Analysis section) |
| Maximum quality, time no object   | `optimized`        | Bayesian search for best parameters      |
| Experimental auto-detection       | `informed`         | Auto-detects alignment type — experimental, may not always outperform advanced |

### 9 CLI Methods
- **basic** — Single refusal direction via diff-in-means. Fast (~5-10 min for 8B).
- **advanced** (DEFAULT, RECOMMENDED) — Multiple SVD directions, norm-preserving projection, 2 refinement passes. Medium speed (~10-20 min).
- **aggressive** — Whitened SVD + jailbreak-contrastive + attention head surgery. Higher risk of coherence damage.
- **spectral_cascade** — DCT frequency-domain decomposition. Research/novel approach.
- **informed** — Runs analysis DURING abliteration to auto-configure. Experimental — slower and less predictable than advanced.
- **surgical** — SAE features + neuron masking + head surgery + per-expert. Very slow (~1-2 hrs). Best for reasoning models.
- **optimized** — Bayesian hyperparameter search (Optuna TPE). Longest runtime but finds optimal parameters.
- **inverted** — Flips the refusal direction. Model becomes actively willing.
- **nuclear** — Maximum force combo for stubborn MoE models. Expert-granular.

### Direction Extraction Methods (--direction-method flag)
- **diff_means** (default) — Simple difference-in-means between refused/complied activations. Robust.
- **svd** — Multi-direction SVD extraction. Better for complex alignment.
- **leace** — LEACE (Linear Erasure via Closed-form Estimation). Optimal linear erasure.

### 4 Python-API-Only Methods
(NOT available via CLI — require Python import, which violates AGPL boundary. Mention to user only if they explicitly want to use OBLITERATUS as a library in their own AGPL project.)
- failspy, gabliteration, heretic, rdo

## Step 5: Run Abliteration

### Standard usage
```bash
# Default method (advanced) — recommended for most models
obliteratus obliterate <model_name> --method advanced --output-dir ./abliterated-models

# With 4-bit quantization (saves VRAM)
obliteratus obliterate <model_name> --method advanced --quantization 4bit --output-dir ./abliterated-models

# Large models (70B+) — conservative defaults
obliteratus obliterate <model_name> --method advanced --quantization 4bit --large-model --output-dir ./abliterated-models
```

### Fine-tuning parameters
```bash
obliteratus obliterate <model_name> \
  --method advanced \
  --direction-method diff_means \
  --n-directions 4 \
  --refinement-passes 2 \
  --regularization 0.1 \
  --quantization 4bit \
  --output-dir ./abliterated-models \
  --contribute  # opt-in telemetry for community research
```

### Key flags
| Flag | Description | Default |
|:-----|:------------|:--------|
| `--method` | Abliteration method | advanced |
| `--direction-method` | Direction extraction | diff_means |
| `--n-directions` | Number of refusal directions (1-32) | method-dependent |
| `--refinement-passes` | Iterative passes (1-5) | 2 |
| `--regularization` | Regularization strength (0.0-1.0) | 0.1 |
| `--quantization` | Load in 4bit or 8bit | none (full precision) |
| `--large-model` | Conservative defaults for 120B+ | false |
| `--output-dir` | Where to save the abliterated model | ./obliterated_model |
| `--contribute` | Share anonymized results for research | false |
| `--verify-sample-size` | Number of test prompts for refusal check | 20 |
| `--dtype` | Model dtype (float16, bfloat16) | auto |

### Other execution modes
```bash
# Interactive guided mode (hardware → model → preset)
obliteratus interactive

# Web UI (Gradio)
obliteratus ui --port 7860

# Run a full ablation study from YAML config
obliteratus run config.yaml --preset quick

# Tournament: pit all methods against each other
obliteratus tourney <model_name>
```

## Step 6: Verify Results

After abliteration, check the output metrics:

| Metric | Good Value | Warning |
|:-------|:-----------|:--------|
| Refusal rate | < 5% (ideally ~0%) | > 10% means refusals persist |
| Perplexity change | < 10% increase | > 15% means coherence damage |
| KL divergence | < 0.1 | > 0.5 means significant distribution shift |
| Coherence | High / passes qualitative check | Degraded responses, repetition |

### If refusals persist (> 10%)
1. Try `aggressive` method
2. Increase `--n-directions` (e.g., 8 or 16)
3. Add `--refinement-passes 3`
4. Try `--direction-method svd` instead of diff_means

### If coherence is damaged (perplexity > 15% increase)
1. Reduce `--n-directions` (try 2)
2. Increase `--regularization` (try 0.3)
3. Reduce `--refinement-passes` to 1
4. Try `basic` method (gentler)

## Step 7: Use the Abliterated Model

The output is a standard HuggingFace model directory.

```bash
# Test locally with transformers
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('./abliterated-models/<model>')
tokenizer = AutoTokenizer.from_pretrained('./abliterated-models/<model>')
inputs = tokenizer('How do I pick a lock?', return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
"

# Upload to HuggingFace Hub
huggingface-cli upload <username>/<model-name>-abliterated ./abliterated-models/<model>

# Serve with vLLM
vllm serve ./abliterated-models/<model>
```


> 🔍 **## CLI Command Reference** moved to [references/detailed.md](references/detailed.md)
