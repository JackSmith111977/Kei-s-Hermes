---
name: hy3-model-guide
description: "Hy3 模型（混元 3 预览版）完整指南 — 涵盖架构解析、性能基准、API 使用、成本优化、Agent 工作流设计。基于腾讯官方文档和实战验证数据。当用户询问 Hy3/混元3/tencent hy3/hy3-preview 时使用此 skill。"
version: 1.0.0
triggers:
- Hy3
- hy3
- 混元3
- Hunyuan 3
- tencent hy3
- hy3-preview
- 腾讯混元3
- hy3 模型
- 混元3.0
- 腾讯混元3.0
- 混元3预览版
- Hy3 preview
- hunyuan3
author: 小喵 (Emma)
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- patch
- web_search
- web_extract
- skill_manage
- skills_list
- skill_view
metadata:
  hermes:
    tags:
    - hy3
    - hunyuan
    - model-guide
    - tencent
    - moe-architecture
    - agent
    category: reference
    skill_type: library-reference
    design_pattern: tool-wrapper
  depends_on:
    - web-access
    - skill-creator
depends_on: []

---

# 🧠 Hy3 模型完整指南 v1.0

> **核心定位**：Hy3 preview（混元 3 预览版）是腾讯混元团队开发的**快慢思考融合的混合专家（MoE）语言模型**，总参数 295B 但每次仅激活 21B 参数，通过 192 个专家中 top-8 激活 + 1 个共享专家的机制，在保持大参数规模的同时实现极致成本效率。

---

## 一、快速参考表格

### 1.1 模型规格速查

| 属性 | 值 |
|------|-----|
| **架构** | Mixture-of-Experts (MoE) + Dense-MoE 混合 |
| **总参数量** | 295B（2950 亿） |
| **激活参数量** | 21B（210 亿，仅 7.1% 总参数） |
| **MTP 层参数** | 3.8B（用于推测解码加速） |
| **上下文长度** | 256K tokens（约 20 万字） |
| **专家数量** | 192 个专家，top-8 激活 + 1 个共享专家 |
| **注意力机制** | GQA（64 注意力头，8 个 KV 头，head dim 128） |
| **隐藏层维度** | 4096 |
| **FFN 中间层维度** | 13312 |
| **层数** | 80（不含 MTP 层） |
| **词表大小** | 120832（支持中英日韩等多语言） |
| **支持精度** | BF16 |
| **推理模式** | 三档可配置：no_think / think_low / think_high |

### 1.2 性能亮点速查

| 领域 | 基准测试 | Hy3 preview | 对比模型最佳 |
|------|----------|--------------|-----------|
| **数学** | MATH (4-shot) | **76.28** ✅ | DeepSeek-V3 (59.37) |
| **数学** | GSM8K (4-shot) | **95.37** ✅ | Kimi-K2 (93.46) |
| **代码** | LiveCodeBench-v6 (1-shot) | **34.86** ✅ | Kimi-K2 (30.86) |
| **多语言** | MMMLU (5-shot) | **80.15** ✅ | GLM-4.5 (79.26) |
| **Agent (代码)** | SWE-bench Verified | **74.4%** | Claude Opus 4.6 (80.8%) |
| **Agent (终端)** | Terminal-Bench 2.0 | **54.4%** | - |
| **Agent (搜索)** | WideSearch | **70.2%** | GLM-5 (~70%) |

### 1.3 定价速查（腾讯云 TokenHub）

| Token 类型 | 价格（RMB/百万 tokens） | 约美元等价 |
|-----------|---------------------|------------|
| 输入（0, 16k） | 1.2 元 | ~$0.18 |
| 输入（16k, 32k） | 1.6 元 | ~$0.24 |
| 输入（32k+） | **0.8 元** ✅（长文本更便宜！） | ~$0.12 |
| 缓存输入 | 0.4 元 | ~$0.06 |
| 输出 | 4.0 元 | ~$0.59 |
| **个人套餐** | **RMB 28 / 月** ✅（最低档） | ~$4.10 / 月 |

### 1.4 API 调用速查

| 平台 | 模型标识 | 定价 | 上下文 |
|------|---------|------|---------|
| **OpenRouter (免费)** | `tencent/hy3-review:free` | **$0.00 / 1M** ✅（至 2026-05-08） | 262K |
| **OpenRouter (标准)** | `tencent/hy3-review` | 按量计费 | 262K |
| **腾讯云 TokenHub** | `hy3-review` | 见上表 1.3 | 256K |
| **自托管 (vLLM)** | `tencent/Hy3-review-Base` | 硬件成本 | 256K |

---

## 二、核心概念（用自己的话解释）

### 2.1 MoE 架构的效率魔法
Hy3 preview 使用混合专家架构，就像一个有 192 个专家的团队，但每次任务只让 8 个最合适的专家工作，外加 1 个始终在线的共享专家。这样既保持了 295B 参数的知识广度，又控制了实际计算量（只激活 21B 参数），实现高效率。

### 2.2 参数效率的冠军
Hy3 preview 的总参数（295B）虽然小于 Kimi-K2（1043B）和 DeepSeek-V3（671B），但激活参数（21B）更少，性能却持平或超越。这证明不是"越大越好"，而是"越高效越好"。

### 2.3 快慢思考融合的创新
模型支持三种推理模式（no_think / think_low / think_high），可以根据任务复杂度灵活切换：
- 简单问答用**快速模式**（极速响应）
- 复杂编程用**深度推理模式**（高质量但稍慢）
这是腾讯混元团队的创新设计。

### 2.4 "以战养技"的战略
腾讯不追求单纯刷榜，而是将模型部署到元宝、CodeBuddy、QQ、微信读书等真实产品中，通过用户反馈和实际应用来迭代改进模型。这是"在战争中学习战争"的实践智慧。

### 2.5 300B 最优平衡点
腾讯首席 AI 科学家姚顺宇提出：300B（295B）是能力与效率的最优平衡点。复杂推理、长上下文理解、指令遵循等能力在 300B 级别已经充分释放，继续扩大参数规模的边际收益显著递减（投入翻倍，能力提升往往只在个位数百分点）。

---

## 三、关键特性与用法

### 3.1 三档推理模式选择

| 模式 | 适用场景 | API 参数 | 速度 | 质量 |
|------|---------|-----------|------|------|
| **no_think** | 简单问答、闲聊、API 调用 | `reasoning: "disabled"` | 🚀🚀🚀 极速 | ⭐⭐ |
| **think_low** | 代码调试、文档分析、中等复杂度 | `reasoning: "low"` | 🚀🚀 快速 | ⭐⭐⭐ |
| **think_high** | 数学证明、算法设计、多步 Agent 规划 | `reasoning: "high"` | 🚀 较慢 | ⭐⭐⭐⭐ 最佳 |

### 3.2 256K 超长上下文用法

| 场景 | 示例 | 优势 |
|------|------|------|
| **跨文件代码重构** | 一次性输入完整代码仓库（10+ 文件） | 理解全局依赖关系 |
| **长文档分析** | 法律合同、学术论文（20 万字） | 避免分块导致的上下文丢失 |
| **多轮对话历史** | 保持 495 步 Agent 工作流状态 | 已验证可稳定支撑 |
| **知识检索增强** | 结合 MCP 协议，注入大量参考文档 | 提升回答准确性 |

### 3.3 工具调用与 MCP 支持

Hy3 preview 支持：
- **Function Calling**（函数调用）
- **Tool Use**（工具使用）
- **MCP**（Model Context Protocol，模型上下文协议）

**OpenAI Chat API 兼容调用示例**（Python）：
```python
import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",  # 或腾讯云 TokenHub 端点
    api_key="<YOUR_API_KEY>"
)

response = client.chat.completions.create(
    model="tencent/hy3-review:free",  # 或 hy3-review
    messages=[
        {"role": "system", "content": "你是一个专业的代码助手。"},
        {"role": "user", "content": "用 Python 实现快速排序，并分析时间复杂度。"}
    ],
    reasoning="high",  # no_think / low / high
    max_tokens=2048,
    temperature=0.7
)

print(response.choices[0].message.content)
```

### 3.4 推测解码加速（MTP）

Hy3 preview 包含 3.8B MTP（Multi-Token Prediction）层参数，可与 EAGLE 算法协同工作，加速推理：

**vLLM 部署命令**（推荐 8×H20-3e GPU）：
```bash
vllm serve tencent/Hy3-review-Base \
    --tensor-parallel-size 8 \
    --speculative-config.method mtp \
    --speculative-config.num_speculative_tokens 1 \
    --tool-call-parser hy_v3 \
    --reasoning-parser hy_v3 \
    --enable-auto-tool-choice \
    --served-model-name hy3-review-Base
```

**SGLang 部署命令**（支持 EAGLE 推测解码）：
```bash
python3 -m sglang.launch_server \
    --model tencent/Hy3-review-Base \
    --tp 8 \
    --tool-call-parser hunyuan \
    --reasoning-parser hunyuan \
    --speculative-num-steps 1 \
    --speculative-eagle-topk 1 \
    --speculative-num-draft-tokens 2 \
    --speculative-algorithm EAGLE \
    --served-model-name hy3-review-Base
```

---

## 四、最佳实践

### ✅ 推荐做法

1. **根据任务复杂度选择推理模式**：
   - 简单问答 → `no_think`（极速响应）
   - 代码调试 → `think_low`（平衡速度与质量）
   - 复杂数学推理 → `think_high`（深度思考，质量优先）

2. **充分利用 256K 上下文**：
   - 一次性输入完整代码仓库（跨文件重构）
   - 长文档分析（法律合同、学术论文）
   - 多轮对话历史保持（495 步 Agent 工作流已验证）

3. **使用缓存降低成本和延迟**：
   - 腾讯云 TokenHub：缓存输入 RMB 0.4/百万 tokens（仅为普通输入的 1/3）
   - OpenRouter：缓存命中率 79.2%，自动管理
   - **技巧**：重复使用的系统提示、文档片段会自动缓存

4. **部署选择建议**：
   - **开发测试**：OpenRouter `tencent/hy3-review:free`（2026-05-08 前免费）
   - **生产环境**：腾讯云 TokenHub（国内低延迟，支持个人套餐 $4.10/月）
   - **自托管**：vLLM（8×H20-3e GPU）或 SGLang（支持 EAGLE 推测解码）

5. **Agent 场景优化**：
   - 代码任务：SWE-bench Verified 74.4%，已验证支持 495 步复杂工作流
   - 搜索任务：BrowseComp 67.1%，WideSearch 70.2%
   - **建议**：结合 OpenClaw、OpenCode、KiloCode 等框架使用

### ❌ 反模式（避免）

1. **盲目使用最大上下文**：
   - 虽然支持 256K，但长文本（32k+）输入反而更便宜（RMB 0.8 vs RMB 1.2）
   - **原因**：腾讯云促销策略，鼓励使用长上下文

2. **忽视模型定位**：
   - Hy3 preview 专注于**推理、代码、Agent**，英文知识问答（MMLU 87.42）弱于 Kimi-K2（88.24）
   - **建议**：中英双语推理任务选 Hy3，纯英文知识问答选 Kimi-K2 或 Claude

3. **忘记"快慢思考"切换**：
   - 默认可能是快速模式，复杂任务必须显式设置 `reasoning: "high"`
   - **示例**：数学证明、算法设计 → `think_high`；简单 API 调用 → `no_think`

4. **忽略缓存机制**：
   - 首次请求无缓存，后续相同前缀请求自动命中缓存（成本降低 67%）
   - **技巧**：将不变的文档/代码放在提示前缀，动态指令放在后缀

### ⚠️ 常见陷阱

1. **OpenRouter 免费期结束**：
   - `tencent/hy3-review:free` 将于 **2026-05-08 结束免费**
   - **应对**：提前切换到标准版 `tencent/hy3-review`（按量计费）或腾讯云 TokenHub

2. **部署硬件要求高**：
   - 295B 模型需要 8 张 GPU（推荐 H20-3e 或更大显存卡型）
   - **替代方案**：使用 OpenRouter 或腾讯云 API（无需自部署）

3. **词表超大导致 token 数增加**：
   - Hy3 preview 使用 120832 词表（vs Llama 3 的 128256），但 Claude Opus 4.7 新 tokenizer "可能使用多达 35% 更多 tokens"
   - **影响**：按 token 计费时，同样文本可能比 Llama 3 更多 tokens

4. **多模态能力暂未上线**：
   - 前代 Hy2 是多模态模型，但 Hy3 preview 当前仅文本型
   - **等待**：多模态版本（支持图像、视频理解）预计后续发布

---

## 五、与其他方案对比

### 5.1 同尺寸级别对比（预训练基础模型）

| 基准测试 (Metric) | Kimi-K2 BASE (32B/1043B) | DeepSeek-V3 BASE (37B/671B) | GLM-4.5 BASE (32B/355B) | **Hy3 preview-Base (21B/295B)** |
|---|---|---|---|---|
| **英语知识** | | | | |
| MMLU | **88.24** ✅ | 87.68 | 87.73 | 87.42 |
| MMLU-Pro | **65.98** ✅ | 63.98 | 63.67 | 65.76 |
| **代码能力** | | | | |
| LiveCodeBench-v6 | 30.86 | 29.31 | 27.43 | **34.86** ✅ |
| MBPP-plus | **81.35** ✅ | 75.47 | 78.05 | 78.71 |
| **数学推理** | | | | |
| MATH | 71.20 | 59.37 | 61.00 | **76.28** ✅ |
| GSM8K | 93.46 | 88.15 | 90.06 | **95.37** ✅ |
| **中文能力** | | | | |
| C-Eval | **91.51** ✅ | 90.35 | 85.84 | 89.80 |
| **多语言** | | | | |
| MMMLU | 77.63 | 79.54 | 79.26 | **80.15** ✅ |

**关键洞察**：
- ✅ **Hy3 preview 最强领域**：数学（MATH 76.28）、代码（LiveCodeBench-v6 34.86）、多语言（MMMLU 80.15）
- ⚠️ **相对较弱**：英语知识（MMLU 87.42 vs Kimi-K2 88.24），但差距极小（<1%）
- 🏆 **参数效率冠军**：激活参数最少（21B），但多项基准领先，证明 MoE 架构极致效率

### 5.2 指令模型对比（真实场景与 Agent）

| 基准测试 | **Hy3 preview** | GLM-5 | Kimi-K2.5 | Claude Opus 4.6 | GPT-5.4 |
|---|---|---|---|---|---|
| **SWE-bench Verified** (代码) | 74.4% | ~74.4% | 76.8% | **80.8%** ✅ | 78.6% |
| **Terminal-Bench 2.0** (终端) | **54.4%** ✅ | - | - | ? | - |
| **BrowseComp** (搜索) | 67.1% | < 67.1% | < 67.1% | **77.2%** ✅ | - |
| **WideSearch** (广泛搜索) | 70.2% | < 70.2% | < 70.2% | **?** | - |
| **上下文长度** | 256K | 256K | 1M | **1M** ✅ | 1M |
| **激活参数** | **21B** ✅ | 32B | 32B | ? | ? |
| **成本（输入/输出）** | $0.18 / $0.59 | 类似 | 类似 | $5 / $25 | $5 / $30 |

**关键洞察**：
- ✅ **Agent 场景性价比之王**：Hy3 preview 在 SWE-bench、BrowseComp、WideSearch 上接近或超越 GLM-5 和 Kimi-K2.5，成本仅为 Claude Opus 4.6 的 1/10
- ⚠️ **顶尖闭源模型仍领先**：Claude Opus 4.6 和 GPT-5.4 在部分基准上仍有优势，但成本差距巨大
- 🏆 **最佳选择场景**：高频率 Agent 工作流（代码、搜索、文档处理），成本敏感型项目

### 5.3 API 平台对比

| 平台 | 模型标识 | 定价（输入/输出） | 免费额度 | 上下文 | 工具调用 |
|---|---|---|---|---|---|
| **OpenRouter (免费)** | `tencent/hy3-review:free` | **$0.00 / $0.00** ✅ | 完全免费（至 2026-05-08） | 262K | ✅ |
| **OpenRouter (标准)** | `tencent/hy3-review` | 按量计费 | - | 262K | ✅ |
| **腾讯云 TokenHub** | `hy3-review` | $0.18 / $0.59 | 新用户赠送 | 256K | ✅ |
| **腾讯云 TokenHub** | 个人套餐 | **$4.10 / 月无限额** ✅ | - | 256K | ✅ |

**关键洞察**：
- ✅ **最佳入门选择**：OpenRouter `tencent/hy3-review:free`（2026-05-08 前完全免费）
- ✅ **最佳生产选择**：腾讯云 TokenHub 个人套餐（$4.10/月），支持 OpenClaw 等 Agent 框架
- ⚠️ **注意**：OpenRouter 免费版将于 2026-05-08 结束，需提前规划迁移

---

## 六、学习路径建议

### 🎯 目标：掌握 Hy3 模型并应用于 Agent 开发

| 阶段 | 学习内容 | 预计时间 | 关键产出 |
|---|---|---|---|
| **阶段 1：基础理解** | 阅读本文档（核心概念 + 关键特性） | 30 分钟 | 理解 MoE 架构、参数效率、三档推理模式 |
| **阶段 2：动手测试** | 在 OpenRouter 免费版测试不同推理模式 | 1 小时 | 体验 no_think / think_low / think_high 的速度与质量差异 |
| **阶段 3：基准对比** | 对比 Hy3 与 Kimi-K2、DeepSeek-V3 在 MATH、LiveCodeBench 上的表现 | 1 小时 | 明确 Hy3 的优势领域（数学、代码）与相对弱势（英文知识） |
| **阶段 4：API 集成** | 学习 OpenAI Chat API 兼容调用、工具调用（Function Calling）、MCP 协议 | 2 小时 | 编写调用 Hy3 的代码示例（Python/TypeScript） |
| **阶段 5：Agent 实战** | 集成到 OpenClaw/OpenCode/KiloCode，测试 495 步工作流 | 3 小时 | 完成一个完整的 Agent 项目（如代码调试、文档分析） |
| **阶段 6：生产部署** | 选择腾讯云 TokenHub 或自托管（vLLM/SGLang），配置缓存优化 | 2 小时 | 部署可对外服务的 API 端点，成本监控 |

**总预计时间**：~8.5 小时（可分 2-3 天完成）

### 🚀 快速上手（如果时间紧迫，仅需 2 小时）

| 步骤 | 内容 | 时间 |
|---|---|---|
| 1. 阅读本文档（核心概念 + 关键特性） | 30 分钟 |
| 2. 在 OpenRouter 免费版测试 `tencent/hy3-review:free` | 30 分钟 |
| 3. 编写简单的 Python 调用脚本（OpenAI 兼容） | 30 分钟 |
| 4. 尝试一个 Agent 框架（OpenClaw 官方示例） | 30 分钟 |

---

## 七、可复用模式/规则/流程

### 7.1 MoE 架构的优势模式

```
问题：如何在保持大模型能力的同时控制推理成本？
解决模式：Mixture-of-Experts (MoE)
  - 总参数（知识广度）：295B
  - 激活参数（实际计算）：21B（仅 7.1%）
  - 实现方式：192 个专家，每次 top-8 激活 + 1 个共享专家
  - 效果：性能持平或超越 671B 模型，成本仅为 1/3
```

### 7.2 三档推理模式选择规则

```
IF 任务复杂度 == "简单"（闲聊、简单问答、API 调用）:
    使用 no_think（极速响应，延迟最低）
ELIF 任务复杂度 == "中等"（代码调试、文档总结、数据分析）:
    使用 think_low（平衡速度与质量）
ELIF 任务复杂度 == "复杂"（数学证明、算法设计、多步 Agent 规划）:
    使用 think_high（深度思考，质量优先）
ELSE:
    从 think_low 开始，根据结果质量动态调整
```

### 7.3 成本优化流程

```
步骤 1：优先使用缓存
  - 腾讯云 TokenHub：缓存输入 $0.06/1M（仅为普通输入的 1/3）
  - 技巧：将不变的文档/代码放在提示前缀

步骤 2：根据上下文长度选择定价档位
  - 0-16K：RMB 1.2/百万 tokens
  - 16-32K：RMB 1.6/百万 tokens
  - 32K+：RMB 0.8/百万 tokens（**长文本反而更便宜！**）

步骤 3：选择合适的部署方式
  - 开发测试：OpenRouter 免费版（至 2026-05-08）
  - 生产环境：腾讯云 TokenHub 个人套餐（$4.10/月无限额）
  - 高频调用：自托管（8×H20-3e GPU + vLLM/SGLang）
```

### 7.4 Agent 工作流设计模式

```
模式：以战养技（通过真实场景迭代改进）
来源：腾讯混元团队实践（元宝、CodeBuddy、微信等）

步骤：
1. 模型部署到真实产品（如元宝、CodeBuddy）
2. 收集用户反馈与实际性能数据（成功率、延迟、成本）
3. 针对痛点优化（如首 token 延迟降低 54%、端到端时长减少 47%）
4. 将改进反馈到下一版本训练（Hy3 正式版）
5. 重复 1-4，形成正向循环

效果验证：
- 已验证可稳定支撑长达 **495 步**的复杂 Agent 工作流
- 覆盖文档处理、数据分析、知识检索、MCP 工具链编排
- 在 CodeBuddy/WorkBuddy 上成功率 >99.99%
```

### 7.5 避免"刷榜"的真实评估方法

```
问题：公开榜单容易被"特化训练"刷榜，无法反映真实能力
解决：腾讯混元团队的三大原则

1. 能力体系化（拒绝偏科）
   - 不只测代码，还要测推理、长文、指令、工具调用
   - 自建 50+ 个 Benchmarks（CL-bench、CL-bench-Life、Hy-Backend 等）

2. 评测真实性（跳出"刷榜"）
   - 使用最新真实考试（清华大学博士资格考试、全国中学生生物学联赛）
   - 人工评测和产品众测（用户盲评整体胜率 55%-56%）

3. 极致性价比（模型架构与推理设计融合）
   - 300B 最优平衡点理论（继续扩大参数规模的边际收益显著递减）
   - 深度协同模型架构与推理框架（整体推理效率提升 40%）
```

---

## 八、🚩 Red Flags（常见错误）

### 8.1 部署相关

1. **忽略硬件要求**：295B 模型需要 8 张 GPU（推荐 H20-3e），不要尝试在消费级 GPU 上部署
2. **忘记 MTP 加速**：3.8B MTP 层可与 EAGLE 算法协同，加速推理，不要忽略此功能
3. **缓存配置错误**：首次请求无缓存，后续相同前缀自动命中，确保将不变内容放在提示前缀

### 8.2 API 调用相关

1. **忘记设置推理模式**：默认可能是快速模式，复杂任务必须显式设置 `reasoning: "high"`
2. **混淆免费版和标准版**：`tencent/hy3-review:free` 将于 2026-05-08 结束，提前规划迁移
3. **忽视上下文长度定价差异**：长文本（32k+）反而更便宜（RMB 0.8 vs RMB 1.2），鼓励使用长上下文

### 8.3 模型选择相关

1. **盲目追求最大参数**：Hy3 preview 证明不是"越大越好"，而是"越高效越好"
2. **忽视模型定位**：Hy3 专注推理/代码/Agent，英文知识弱于 Kimi-K2，选模型要看任务类型
3. **忘记"快慢思考"切换**：简单任务用 `no_think`，复杂任务用 `think_high`，不要一刀切

### 8.4 成本控制相关

1. **忽略缓存机制**：缓存输入仅为普通输入的 1/3，充分利用可大幅降低成本
2. **不监控 token 用量**：个人套餐虽无限额，但需注意推理速度受限于硬件资源
3. **盲目选择自托管**：除非高频调用（>1000 万 tokens/月），否则 API 调用更划算

---

## 九、参考资源

### 9.1 官方文档

| 资源 | 链接 | 说明 |
|------|------|------|
| **Hugging Face** | https://huggingface.co/tencent/Hy3-preview-Base | 模型卡、权重下载、基准测试 |
| **GitHub** | https://github.com/Tencent-Hunyuan/Hy3-preview | 官方仓库、README、部署示例 |
| **腾讯官网（中文）** | https://www.tencent.com/zh-cn/articles/2202320.html | 官方新闻稿、设计理念 |
| **腾讯官网（英文）** | https://www.tencent.com/en-us/articles/2202320.html | 英文版官方新闻稿 |
| **腾讯云 TokenHub** | https://cloud.tencent.com/document/product/1823/130055 | 官方定价、API 文档 |

### 9.2 基准测试详情

- **预训练模型性能**：见 Hugging Face 模型卡或本文档"五、与其他方案对比"
- **指令模型性能**：SWE-bench Verified 74.4%、Terminal-Bench 2.0 54.4%、BrowseComp 67.1%、WideSearch 70.2%
- **真实考试表现**：清华大学博士资格考试 88.4 分（三次平均）、全国中学生生物学联赛 87.8 分

### 9.3 API 调用示例

- **OpenRouter API**：https://openrouter.ai/tencent/hy3-review:free/api
- **腾讯云 TokenHub API**：https://cloud.tencent.com/document/product/1823/130060
- **vLLM 部署**：见本文档"三、关键特性与用法 → 3.4 推测解码加速"
- **SGLang 部署**：见本文档"三、关键特性与用法 → 3.4 推测解码加速"

### 9.4 社区与生态

| 平台 | 链接 | 说明 |
|------|------|------|
| **ModelScope** | https://modelscope.cn/models/Tencent-Hunyuan/Hy3-preview | 国内镜像，快速下载 |
| **GitCode** | https://ai.gitcode.com/tencent_hunyuan/Hy3-preview | 国内代码托管平台 |
| **cnb.cool** | https://cnb.cool/ai-models/tencent/Hy3-preview | 国内 AI 模型平台 |
| **OpenRouter** | https://openrouter.ai/tencent/hy3-review | API 调用、排行榜、活动统计 |

### 9.5 相关 Skill 引用

- **web-access**：所有联网操作的统一入口（搜索、提取、浏览器自动化）
- **skill-creator**：创建、优化、评估 Skill 的完整工作流
- **learning-workflow**：所有学习/研究任务的强制流程拦截器
- **deep-research**：深度调研工作流（从需求理解到可交付报告）

---

## 十、更新记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-05-06 | 初始版本。基于腾讯官方文档、Hugging Face 模型卡、GitHub README、多家科技媒体报道。涵盖架构解析、性能基准、API 使用、成本优化、Agent 工作流设计。 |

---

**🔒 本 skill 为 Hy3 模型完整指南，任何相关问题应优先加载此 skill！**
