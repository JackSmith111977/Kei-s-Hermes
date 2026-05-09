---
name: ai-trends
description: AI前沿技术趋势追踪 — 开源模型、AI Agent、LLM新特性、ML论文动态。定期更新，保持对AI领域最新进展的知识同步。
version: 1.7.0
triggers:
- ai trends
- ai前沿
- llm news
- open source models
- ai agents
- machine learning papers
metadata:
  hermes:
    tags:
    - AI趋势
    - 开源模型
    - LLM
    - AI Agent
    - 论文追踪
---

# AI 前沿技术趋势

追踪 AI/ML 领域的最新进展：开源模型发布、架构创新、Agent 生态、训练范式演变。

## 当前格局（2025-2026）

### 开源模型排名（开放权重社区热度）

1. **Qwen 系列** — 已超越 Llama 成为开放权重社区最受欢迎的模型家族（下载量和衍生品数量）
   - Qwen3 系列：推理与编码能力突出
   - Qwen3-Next：混合架构，注重成本效率
   - **Qwen3.6 系列**（2026.05）：Qwen3.6-27B、Qwen3.6-35B-A3B（MoE），延续高性能推理与编码能力
2. **DeepSeek 系列**
   - DeepSeek-V3.2 / V3.2-Speciale：稀疏注意力架构，128K 上下文，在精英数学测试中达 99.2%
   - DeepSeek-V4：面向长上下文推理、编码和 Agent 工作流，两大 MoE 模型
   - **DeepSeek-V4-Pro-Max / V4-Flash-Max**（2026.05）：最新推理优化变体
3. **其他竞争者**：Kimi K2.6、GLM-4.7、MiniMax、Yi
   - **Kimi K2.6 GA**（2026.04.21）：1T/32B MoE（384 experts），262K 上下文，12 小时自治运行，300-agent 群协调
     - SWE-Bench Pro **58.6%**，Terminal-Bench 2.0 **66.7%**，MathVision **93.2%**
     - Partner 验证：Vercel >50% Next.js 提升，Factory.ai +15%，CodeBuddy +12% accuracy
     - Anthropic API 兼容，Apache 2.0 基础权重开源
   - **Zyphra ZAYA1-8B**（2026.05.06）：8B MoE 语言模型，<1B active parameters，Apache 2.0 开源。在 AMD MI300X 集群（1024 GPU）上训练。匹配/超越 Nemotron-3-Nano-30B-A3B、Mistral-Small-4-119B，与 DeepSeek-R1-0528、Gemini-2.5-Pro 竞争。引入 Compressed Convolutional Attention (CCA) + MLP-based 专家路由器 + Markovian RSA 测试时计算方法（无限推理恒定内存成本）。体现"智能密度"趋势
4. **Mistral 3**（2025.12）：采用 DeepSeek V3 架构
5. **Llama 4 系列**（Meta，2025.10）：Llama 4 Scout（17B active/109B total，16 experts，10M token 上下文）、Llama 4 Maverick（17B active/400B total，128 experts，1M 上下文），单卡 H100 可跑 Scout。截至 2026.05 已被 Qwen3.6/DeepSeek-V4 部分超越

### 闭源/专有模型

- **OpenAI GPT-5.5 系列**（2026.05 更新）：
  - **GPT-5.5 Instant**（5/5 发布）：幻觉减少 **52.5%**（高风险领域），37.3% 错误声明减少
    - **Memory Sources** 功能：透明度控制，可查看个性化响应使用的上下文（过去聊天、连接文件）
    - 响应更简洁：30.2% 更少词汇，29.2% 更少行数，减少不必要追问
    - 自我错误恢复能力：能在问题解决过程中发现并纠正自身错误
    - API 端点：`chat-latest`，替换 GPT-5.3 Instant 作为默认模型
  - GPT-5.5 Pro：$3000/M 输入价格，最大上下文 1.1M tokens，擅长代理编码（Terminal-Bench 82.7%）
  - **GPT-5.5-Cyber**（2026.05.08）：安全专用变体。Trusted Access for Cyber 身份验证框架下有限预览。针对防御性安全任务更宽松的权限（授权红队、渗透测试、漏洞验证）。对 Anthropic Claude Mythos 的直接回应。不作为主要能力升级，而是"更愿意做安全任务"
  - **GPT-Realtime-2**（2026.05.07）：首个 GPT-5-class 推理语音模型。上下文 128K（agent 工作流），可调节推理力度（minimal/xhigh），Big Bench Audio +15.2%。定价 $32/$64 per 1M audio tokens
  - **GPT-Realtime-Translate**（2026.05.07）：实时翻译模型，70+ 输入语言→13 输出语言，$0.034/分钟
  - **GPT-Realtime-Whisper**（2026.05.07）：流式语音转文字，$0.017/分钟。三大语音 AI 模式：Voice-to-action / Systems-to-voice / Voice-to-voice
  - OpenAI 还在探索基于 AI Agent 的手机概念（替代传统 App）
- **OpenAI gpt-oss**：发布开放权重模型
- **Google Gemini 3.1**（2026.02 发布，2026.05 企业集成）：
  - Gemini 3.1 Pro：ARC-AGI-2 达 **77.1%**（推理能力翻倍）
  - Gemini 3.1 Flash-Lite 等变体，最大上下文 2.1M tokens
  - **Gemini 3.1 Flash-Lite GA**（2026.05.07）：Gemini 3 系列最快、最具成本效益模型。比同类 thinking-tier 模型低 ~60% 成本，p95 延迟 ~1.8s，~99.6% 可靠性。设计用于极低延迟、高吞吐量 agent 任务（工具调用、编排）。已集成 JetBrains IDE AI 助手、Gladly（数百万周呼叫）、OffDeal Archie Agent（投行实时研究）、Ramp 高吞吐量特性
  - **Gemini API File Search 多模态化**（5/5）：支持图像+文本，自定义元数据过滤，页级引用提高透明度
  - Gemini Robotics-ER 1.6：空间推理、多视图理解、成功检测，与 Boston Dynamics 合作
- **Anthropic Claude Opus 4.7**（2026.04 发布）：
  - 编码能力提升 **13%**，解决 4 个 Opus 4.6/Sonnet 4.6 无法完成的任务
  - 支持 **2,576px** 高分辨率图像（化学结构、技术图表）
  - 新增 Effort Control（`xhigh` 级别），Cyber Verification Program
  - 定价不变：$5/M 输入，$25/M 输出
- **MiniMax M2.7**：角色一致性与情感深度增强，开源 OpenRoom（基于 Web 的实时视觉反馈环境）
- **xAI Grok 4.3**（2026.05.06）：xAI 最新发布，延续 Grok 系列推理能力
- **MiniMax-M1**（2026.05）：**全球首个开源大规模混合注意力推理模型**，1M token 上下文窗口（与 Gemini 2.5 Pro 并列行业领先），80K 推理 token 输出
  - 专有 Lightning Attention 机制，80K 深度推理仅需约 DeepSeek R1 30% 算力
  - SWE-bench 验证集 56.0%（接近 DeepSeek-R1-0528 57.6%，大幅超越其他开源模型）
  - 长上下文理解超 OpenAI o3 和 Claude 4 Opus，全球第二仅次于 Gemini 2.5 Pro
  - Agent 工具使用（TAU-bench）领先所有开源模型，超 Gemini-2.5 Pro
  - 开源权重 + 技术报告已发布

### 架构趋势

| 趋势 | 说明 |
|------|------|
| 混合架构崛起 | Qwen3-Next、Kimi Linear、Nemotron 3 — 低成本高效率优先 |
| 缩放墙（Scaling Wall） | NeurIPS 2025 观察到单纯扩大规模的收益递减 |
| RLVR 扩展 | 强化学习+可验证奖励从数学/编码扩展到化学、生物等领域 |
| 多模态统一 | EBind（1.8B 参数）绑定图像/文本/视频/音频/3D 嵌入，超越 4-17× 更大模型 |
| 通用 Agent | Nvidia NitroGen 可玩 1000+ 视频游戏，未见过的任务成功率高 52% |
| 边缘 ML (Edge ML) | 模型从云端推到设备端运行，实时处理语音/视频/传感器数据，减少延迟和隐私风险，6G 设备结合 TinyML |
| ParaRNN (ICLR 2026) | Apple 提出并行 RNN 训练框架，实现 665× 加速，首次训练出 7B 参数 RNN 达到 Transformer 级别语言建模性能 |
| TurboQuant (ICLR 2026) | Google 提出 KV 缓存 3-bit 量化，6 倍内存压缩、8 倍注意力加速，解决长上下文推理的内存瓶颈 |
| **混合注意力推理** (MiniMax-M1) | MiniMax 推出全球首个开源大规模混合注意力推理模型，Lightning Attention 机制实现 80K 推理 token 仅需 30% 算力 |
| **Subquadratic Scaling** (SubQ) | SubQ 1M-Preview 使用 Sparse Subquadratic Attention（O(n) 线性缩放），在 12M token 时相比标准架构减少 ~1,000× 注意力计算，可能使向量数据库和 RAG 分块策略过时 |

### AI Agent 生态

- **MCP（Model Context Protocol）** 已加入 Agentic AI Foundation（从 Linux Foundation 分出），成为 Agent 式 LLM 系统中工具/数据访问的标准。截至 2025 年底已有 10,000+ 公开 MCP 服务器部署
- **Google Gemini Enterprise Agent Platform**（2026.04 发布）：整合 Gemini 3.1 Pro、Claude Opus 4.7 等，通过 MCP 协议实现跨 GCP/Workspace 系统集成，Agent Studio 低代码构建，Simulation Environment 压力测试
- **NVIDIA Nemotron 3 Nano Omni**（2026.05 发布）：**30B-A3B MoE 架构**，统一视觉/音频/语言
  - **9x 效率提升**（相比其他开放 omni 模型），1920×1080 原生分辨率
  - 用于计算机使用 Agent（H Company 实测 OSWorld 显著提升）、文档智能、音视频理解
  - 开源权重、数据集、训练技术，**50M+ 下载**，Hugging Face/OpenRouter/build.nvidia.com 可用
  - 支持 Jetson、DGX Spark/Station 本地部署，满足合规/数据主权要求
- **Google DeepMind SIMA 2**（2025.11 发布）：Gemini 集成的游戏 Agent，支持自改进循环（无需人类示范即可在 Genie 3 新环境中学习），多语言、emoji、草图理解，为机器人路径奠定基础
- **Cloudflare + Stripe Agent 协议**：让 AI Agent 自主创建账户、购买域名、部署应用，实现开发到生产的全自动管线
- **Salesforce Agentforce 2.0**：将 LLM 调用从 4 次减至 2 次输出首 token，引入 HyperClassifier（专有小模型替代通用模型进行主题分类，速度提升 30 倍），整体延迟降低 70%
- **Agent Script 语言**：由 Salesforce 推出，允许开发者定义显式 if/then 工作流，确保 Agent 在关键任务中 100% 达到预期结果
- **企业 Agent 选型框架**：
  - 单 Agent 复杂控制流 → LangGraph
  - 多 Agent 角色分离 → CrewAI
  - 多 Agent 推理/辩论/代码生成 → AutoGen
  - 知识密集型/RAG Agent → LlamaIndex
  - 快速原型（单 Agent）→ LangChain 或原生 SDK
  - 生产级严格管控 → LangGraph + 自定义编排
- **PwC 2025 Agent 采用调查**：35% 组织广泛采用，27% 有限采用，17% 全公司实施
- 安全问题：unrestricted tool use 仍存在安全隐患（工具投毒攻击 — 恶意 MCP 服务器通过注入指令操纵 Agent 行为）。Salesforce 通过可信网关模型（Trusted Gateway）允许管理员定义 Agent 可访问的 MCP 服务器

### Agent 基础设施发展（2026.05 新增）

| 事件 | 日期 | 重要性 | 详情 |
|------|------|--------|------|
| **AWS Agent Toolkit + MCP Server GA** | 2026.05.06 | 🔴 高 | AWS 推出生产级 Agent 工具包，含 40+ agent skills、全托管 MCP 服务器（IAM 护栏 + CloudWatch/CloudTrail 可观测性 + 沙箱代码执行），三个开箱即用 Agent 插件（Core/Data Analytics/Agents） |
| **Google 50+ 托管 MCP 服务器 GA** | 2026.04.28 | 🔴 高 | Google Cloud 推出 50+ 全托管 MCP 服务器，覆盖 Spanner/AlloyDB/BigQuery/Cloud Storage/Workspace/Gmail/Pay/Wallet 等，原生 IAM Deny 策略 + Agent Registry + Model Armor（防注入攻击），支持 Gemini CLI/Claude/ChatGPT/VS Code/LangChain/CrewAI |
| **Microsoft Agent Governance Toolkit (AGT)** | 2026.04 | 🟡 中 | 开源 MCP 安全治理层，Ed25519 + 量子安全 ML-DSA-65 身份体系，覆盖 OWASP MCP Top 10 中 7/10，支持 LangChain/AutoGen/CrewAI/Semantic Kernel/OpenAI Agents SDK/Google ADK 等 20+ 框架，Python/TS/.NET/Rust/Go SDK |
| **MCP 2026 路线图发布** | 2026.03 | 🟡 中 | 四大方向：Streamable HTTP 无状态传输（6 月规范周期）、Agent-to-Agent 通信、企业认证（OAuth 2.1 PKCE）+ 审计合规、MCP Apps（工具返回交互式 HTML）、SSE 即将废弃 |
| **MCPRated 索引上线** | 2026.05 | 🟢 低 | Agent 可读的 MCP 服务器质量索引，每天更新，4 轴评分（可靠性/文档/信任/社区），Agent 可在运行时发现和筛选 MCP 服务器 |
| **MCP v2 Beta (@ai-sdk/mcp)** | 2026.03.13 | 🟡 中 | Vercel AI SDK MCP v2：独立稳定包，OAuth 2.0 内置，Structured Output（outputSchema），Elicitation 支持，Resources/Prompts 原语 |
| **Claude Mythos + Project Glasswing** | 2026.05 | 🔴 高 | Anthropic "超级黑客"模型仅限 40 家合作伙伴使用，Amazon/Google/Microsoft/NVIDIA/Cisco 组成的 Project Glasswing 联盟，$100M 安全 credits + $4M 捐赠开源安全组织 |
| **Claude Managed Agents: Dreaming/Outcomes/Multiagent** | 2026.05.08 | 🔴 高 | Dreaming（研究预览）：计划性复盘+跨 session 记忆演化。Harvey 法律 AI 测试完成率提升 ~6x。Outcomes（公测）：定义成功标准+独立评分器，编码成功率 +10pts。Multiagent Orchestration（公测）：主 agent 拆解任务分派专业子 agent 并行。Netflix 已用于平台团队。Webhooks 同时发布 |

**MCP 生态关键趋势**：
- 81% 远程 MCP 服务器已使用 OAuth 2.1 PKCE
- MCP 注册中心 9,400+ 条目（2025.09 以来增长 407%）
- Streamable HTTP 取代 SSE 成为主要传输协议 
- MCP Apps（2026.01.26）首次扩展协议，工具可返回交互式 HTML UI（沙箱 iframe），已在 Claude/ChatGPT/Goose/VS Code 中支持
- Microsoft Fabric MCP（Local GA + Remote Preview）将数据平台变为 AI 原生操作系统

### Multi-Agent Orchestrator 框架（2026.05 新增）

| 框架 | GitHub Stars | 适用场景 | 核心特性 | 最新版本 |
|------|--------------|----------|----------|----------|
| **Microsoft Agent Framework** | ~9,947 | 企业级多语言(.NET/Python) | Graph-based workflows, DevUI, OTEL observability | python-1.2.2 (2026-04-29) |
| **Google Cloud Scion** | 实验性 | 容器化 agent 并行实验 | True isolation + git worktree, 支持 Claude Code/Gemini CLI/Codex | 早期实验阶段 |
| **Agentspan** | - | 持久化执行引擎 | 基于 Netflix Conductor, 8 种协调策略, Human approval | - |
| **Orloj** | - | 生产级治理 | YAML-defined workflows, Fail-closed governance, Kubernetes 风格 apply/rollback | v0.13.0 (2026-05-05) |

**选型决策树**：
```
企业级 .NET/Python 团队 → Microsoft Agent Framework
实验/原型多 agent → Scion (注意：仍在实验阶段)
需要持久化执行 → Agentspan
生产级治理需求 → Orloj
```

### CLI Coding Agents 对比（2026.05）

| Agent | Stars | 开源 | 价格 | SWE-bench | Terminal-Bench | Context | MCP | 最佳场景 |
|-------|-------|------|------|-----------|----------------|---------|-----|----------|
| **Claude Code** | ~71K | 否 | $20-200/mo | 87.6% | 65.4% | 1M | 深度(3000+ hooks) | 架构设计、多文件重构、Frontend/UI |
| **Codex CLI** | ~65K | Apache 2.0 | $20-200/mo | 78-80% | **82.7%** | 192-400K | 支持 | DevOps、终端自动化、批处理任务 |
| **Gemini CLI** | ~102K | Apache 2.0 | 免费(1000 req/day) | N/A | N/A | 1M | 支持 | 免费/评估、低成本原型 |
| **OpenCode** | ~117K | Go | BYOK | 模型依赖 | 模型依赖 | 模型依赖 | Yes | 多模型自由(75+ models) |
| **Twill** | 新 | Various | - | - | - | - | Yes | "始终在线"自主工程 |

**关键洞察**：
- **Claude Code** 代码质量最高 (87.6% SWE-bench Verified)，1M context window，Agent Teams 多 agent 协作
- **Codex CLI** 更新后 Terminal-Bench 达 **82.7%**（GPT-5.5 驱动），Token 效率 4x fewer tokens，Kernel-level sandboxing 安全
- **最佳组合**: Claude Code → Architecture + Frontend; Codex CLI → DevOps + Autonomous batch work
- **openai-agents-python v0.16.0**（2026.05.07）：默认模型从 gpt-4.1 切换为 gpt-5.4-mini，新增 max_turns=None 禁用限制、工具并发配置、MCP 服务器前缀工具名

**避坑指南**：
- Claude Code $20 Pro plan rate limit (5小时限制，复杂任务可能用完 50-70%)
- Codex CLI 不适合 Frontend/UI（视觉理解弱于 Claude）
- Gemini CLI Pro 已付费化（仅 Flash 免费，3月25日变更）

### 重要论文/模型

| 模型/论文 | 机构 | 亮点 |
|-----------|------|------|
| MMaDA-8B | Gen-Verse AI | 多模态扩散，超越 LLaMA-3-7B 和 Qwen2-7B 文本推理，优于 SDXL/Janus 图像生成 |
| EBind | Broadbent et al. | 1.8B 多模态嵌入，绑定图像/文本/视频/音频/3D |
| NitroGen | Nvidia | 通用 Agent，1000+ 游戏，未见任务 +52% 成功率 |
| ParaRNN | Apple (ICLR 2026) | 并行 RNN 训练框架，665× 加速，首个 7B RNN 达到 Transformer 水平 |
| TurboQuant | Google (ICLR 2026) | KV 缓存 3-bit 量化零精度损失，6 倍内存压缩，8 倍注意力加速 |
| AI Scientist-v2 | Sakana AI | 全自动假设生成与论文撰写，加速药物发现与材料科学研究 |
| VibeGen | MIT | 首个以运动而非静态结构设计蛋白质的 AI，用于适应性治疗与生物材料 |
| **MoGA** | ICLR 2026 | Mixture-of-Groups Attention，精确 token 路由替代块级估计，支持 ~580K 上下文长视频生成 |
| **GRAM** | ICLR 2026 Workshop | Generative Recursive reAsoning Models，概率递归推理，ARC-AGI 强竞争力，宽度扩展推理 |
| **Drifting Models** | Kaiming He et al. | 一步生成范式，ImageNet FID 1.54，训练时演化 pushforward 分布 |
| **DR-Venus-4B** | inclusionAI (2026.04) | 纯开源数据训练的 4B 深度研究 Agent，SFT + IGPO RL，超越 2-3x 更大模型。BrowseComp **29.1%**，arXiv:2604.19859 |
| **OpenSeeker-v2** | 学术团队 (2026.05) | 开源搜索 Agent，BrowseComp **46.0%** SOTA，仅 **10.6K 数据点**纯 SFT 训练，30B 参数 |
| **Zyphra ZAYA1-8B** | Zyphra (2026.05) | 开源 8B MoE 推理模型，<1B active params，Apache 2.0。CCA 注意力 + MLP 路由器 + Markovian RSA 测试时计算。AMD MI300X 1024 GPU 训练。匹配 Nemotron-3-Nano/Mistral-Small，与 DeepSeek-R1/Gemini-2.5-Pro 竞争 |
| **Google DeepMind Gemma 4** | Google (2026.05) | Apache 2.0 开源。26B-A4B MoE 达 31B Dense 旗舰 **97% 质量**，8 倍少算力。4 种规格：E2B/E4B/26B-MoE/31B，支持多模态 + 音频输入 |

### 2026 趋势观察（2026.05 更新）

1. 行业级消费级扩散模型将出现（Gemini Diffusion 可能率先），实现廉价、可靠、低延迟推理
2. 开放权重社区将逐步采用带本地工具使用和更强 Agent 能力的 LLM
3. RLVR 将扩展到数学和编码之外的领域（化学、生物等）
4. **AI Agent 正从原型走向企业级部署**：PwC 调查显示 35% 组织已广泛采用，Cloudflare+Stripe 实现全自动 Agent 部署管线
5. **ICLR 2026 关键信号**：RNN 复兴（ParaRNN 让 7B RNN 达到 Transformer 水平）和 KV 缓存压缩（TurboQuant 3-bit 零损失）是两个重要方向
6. **边缘推理加速**：模型向设备端迁移成为主流趋势，TinyML 与 6G 结合
7. **三大云厂商 MCP 基础设施竞争**（2026.05 关键转折）：AWS（Agent Toolkit + MCP Server GA）、Google（50+ 托管 MCP 服务器）、Microsoft（MCP Fabric + AGT）均在本月推出生产级 Agent 基础设施
8. **开源深度研究 Agent 突破**：DR-Venus-4B（纯开源数据 4B，超 2-3x 更大模型）和 OpenSeeker-v2（46.0% BrowseComp SOTA，仅 10.6K 数据点 SFT）证明小模型+优质数据可超越大模型+海量数据
9. **混合注意力推理成为新趋势**：MiniMax-M1 全球首个开源大规模混合注意力模型，SubQ 线性缩放注意力（~1,000× 计算减少）可能改变 RAG 范式
10. **"智能每参数"成为新前沿**：GPT-5.5 Instant 不再追求参数规模，而是"高保真可靠性"（52.5% 幻觉减少）；Gemma 4 26B MoE 达 31B 旗舰 97% 质量仅需 1/8 算力
11. **语音智能进入推理时代**（2026.05.07）：GPT-Realtime-2 为首次 GPT-5-class 推理语音模型。Voice-to-action/Systems-to-voice/Voice-to-voice 三大模式确立。音频上下文 128K，agent 工具调用成为语音交互标准
12. **Agent 跨会话演化成为产品功能**（2026.05.08）：Claude Dreaming 让 agent 在会话间自我改进（Harvey 6x 提升）。独立评分器（Outcomes）替代 prompt 工程作为质量保证手段。多 Agent 编排从框架实验正式产品化
13. **三大云厂商 MCP 基础设施全面产品化**（2026.04-05）：AWS Agent Toolkit + MCP Server GA（40+ skills）、Google 50+ 托管 MCP GA、Salesforce Hosted MCP GA、Azure MCP 2.0。MCP 从开发者工具升级为企业基础设施

---

### LLM 2026 Flagship 对比（2026.05 新增）

| 模型 | MMLU | HumanEval | MATH | MT-Bench | 价格 Input/Output | Context | 最佳场景 |
|------|------|-----------|------|----------|-------------------|---------|----------|
| **DeepSeek R1** | 90.8 | 85.3 | 97.3 | — | $0.55/$2.19 | 128K | 数学/推理、成本敏感 |
| **Claude Opus 4.5** | 89.5 | 91.0 | 76.0 | 9.3 | $5/$25 | 200K | 关键任务、编码 |
| **Claude Sonnet 4.5** | 89.0 | 93.0 | 78.5 | 9.2 | $3/$15 | 200K | 复杂推理、编码 |
| **Claude 4.6 Opus** | — | — | — | — | $15/$75 | 500K | 编码质量、Agent Tool-Use |
| **o3** | 87.5 | 95.2 | 96.7 | — | $2/$8 | 200K | 最难推理、Agent 工作流 |
| **o4-mini** | 83.2 | 93.4 | 96.7 | — | $1.1/$4.4 | 200K | 成本优化推理 |
| **Gemini 2.5 Pro** | 87.2 | 84.0 | 78.0 | 9.0 | $1.25/$10 | 1M | 长文档、RAG、视频分析 |
| **Gemini 2.5 Flash** | 83.6 | 82.0 | 73.1 | 8.6 | $0.30/$2.50 | 1M | 成本敏感批处理 |
| **GPT-4.1** | 86.5 | 90.2 | 80.4 | 9.2 | $2/$8 | 1M | 企业级、工具使用 |
| **GPT-4.1 mini** | 83.5 | 87.5 | 72.0 | 8.8 | $0.4/$1.6 | 1M | 高吞吐量、成本优化 |
| **Llama 4 Scout** | 79.6 | 82.0 | 70.5 | 8.3 | $0.11/$0.34 | 10M | 大上下文、开源、自托管 |
| **Llama 4 Maverick** | 85.5 | 88.0 | 78.5 | 8.7 | $0.20/$0.60 | 10M | 开源全能、数据主权 |

**关键洞察**：
- Claude 4.6: **99.2% tool-call reliability** (500-call stress test)，SWE-bench 72.4%，编码首选
- GPT-5: **97.1% tool-call reliability**，最佳 ecosystem，Agent 通用
- Gemini 2.5 Flash: **80% capability at 8% cost**，成本敏感首选
- DeepSeek R1: **MATH 97.3** 最高，开源最优

**LLM 选型决策树**：
```
任务类型 →
├─ 编码/重构 → Claude 4.6 Opus (99.2% tool reliability) → Claude Sonnet 4.5 (性价比)
├─ Agent Tool-Use → GPT-5 (best ecosystem, 97.1%) → Claude 4.6
├─ 成本敏感批处理 → Gemini 2.5 Flash ($0.30/$2.50) → DeepSeek V3
├─ 长文档分析 → Gemini 2.5 Ultra (1M+, 质量在 300K 后优于 Claude)
├─ 复杂推理 → DeepSeek R1/o3 → o4-mini (成本优化)
└─ 隐私/离线 → Llama 4 Scout (10M context, 开源)
```

### 新兴 Multi-Agent Orchestration 框架（2026.05 补充）

| 框架 | Stars | License | 核心特性 | 适用场景 |
|------|-------|---------|----------|----------|
| **Shannon** | 1,738 | MIT | Time-travel debugging (Temporal), WASI sandbox, 8 execution strategies, token budget management | 生产级 Agent，需要可靠性 |
| **MARSYS** | — | Apache 2.0 | 8 topology patterns (hub-and-spoke, pipeline, scatter-gather), 50+ parallel agents, branch-scoped state | 多拓扑、并行执行 |
| **REDEREF** | — | arxiv | Training-free Thompson sampling routing, 28% token reduction, 17% agent call reduction | 成本优化路由 |

**Shannon 架构**：
```
Gateway(Go:8080) → Orchestrator(Go:50052) → Agent Core(Rust:50051) → LLM Service(Python:8000)
                    ↓ Temporal workflows      ↓ WASI sandbox      ↓ Provider abstraction
                    ↓ Budget management       ↓ Token enforcement ↓ MCP tools
```

**Shannon 执行策略**：
| Strategy | Trigger | Use Case |
|----------|---------|----------|
| Simple | complexity < 0.3 | 单 Agent |
| DAG | 默认 | Fan-out/fan-in |
| ReAct | 迭代推理 | Reasoning + tool use |
| Research | 多步研究 | Tiered models (50-70% cost reduction) |
| Swarm | 自主团队 | Lead-orchestrated multi-agent |

**REDEREF 算法** (Training-Free Agent Routing):
```
REDEREF = Thompson Sampling + Reflection Judge + Memory-Aware Priors
效果: 28% token ↓, 17% agent calls ↓, 19% time-to-success ↓
适用: 冷启动、Agent Pool 动态变化、成本敏感
```

### ICLR 2026 重要论文补充（2026.05）

| 论文 | 领域 | 关键贡献 |
|------|------|----------|
| **LipNeXt** | Certified Robustness | 首个 convolution-free 1-Lipschitz，1-2B 参数，+8% CRA at ε=1 |
| **Newt** | Multi-Task RL | 200 任务基准，语言条件世界模型，Foundation Model recipe |
| **Cosmos Policy** | Robot Control | 视频模型 → 机器人策略，单阶段 post-training |
| **VideoMind** | Video Reasoning | Chain-of-LoRA agent，时序定位视频理解 |
| **Paper2Code** | ML Automation | 多 Agent LLM 从论文生成代码仓库 |

### 推理引擎与工具链更新（2026.05 新增）

| 项目 | 版本 | 日期 | 亮点 |
|------|------|------|------|
| **vLLM** | v0.20.1 | 2026.05.04 | DeepSeek V4 稳定性专注：Multi-stream pre-attention GEMM、attn GEMM knob 调优、all-to-all 通信优化 |
| **HuggingFace Transformers** | v5.7.0 | 2026.04.28 | 新模型：Laguna (Poolside MoE, sigmoid MoE router)、DEIMv2 (57.8 AP 目标检测)、SAM3-LiteText (88% 轻量化文本编码器)、QianfanOCR (Baidu 4B 端到端文档理解)；`transformers serve` 新增 `/v1/completions` 端点和多模态支持 |
| **AReaL** | v1.0.2 | 2026.03.17 | 快速 RL 框架，新增 Qwen3.5 支持（Dense + MoE）、Online Distillation、双语文档 |

---

> 📌 **更新日志**
> - 2026-05-04: 初始创建 — 整合 DeepSeek-V3.2/V4、Qwen 超越 Llama、MCP 加入 Linux Foundation、混合架构趋势、RLVR 扩展等
> - 2026-05-05: v1.1 更新 — Qwen3.6/DeepSeek-V4-Pro-Max/Llama 4 系列模型信息；ICLR 2026 突破（ParaRNN 665×, TurboQuant 3-bit）；AI Agent 企业级部署（Agentforce 延延降70%, Cloudflare+Stripe 协议, Agent Script）; 企业 Agent 选型框架；边缘 ML 趋势；更新闭源模型（GPT-5.5, Claude 4.7, Gemini 3.1）
> - 2026-05-06: v1.2 更新 — GPT-5.5 Instant 详细数据（52.5% 幻觉减少、Memory Sources）；Claude Opus 4.7 完整规格（13% 编码提升、xhigh effort、Cyber Verification）；Gemini 3.1 Pro ARC-AGI-2 77.1%；新增 Gemini Enterprise Agent Platform、Nemotron 3 Nano Omni（9x 效率）、SIMA 2（自改进循环）；Gemini Robotics-ER 1.6（Boston Dynamics 合作）
> - 2026-05-07: v1.3 更新 — 新增 Multi-Agent Orchestrator 框架对比（Microsoft Agent Framework、Scion、Agentspan、Orloj）；CLI Coding Agents 详细对比表（Claude Code/Codex CLI/Gemini CLI/OpenCode）；选型决策树和避坑指南；Token 效率对比（Codex 4x fewer tokens）；更新 SWE-bench 最新数据（Claude Code 87.6%）
> - 2026-05-07: v1.4 更新 — LLM 2026 Flagship 详细对比表（DeepSeek R1/Claude 4.5/Gemini 2.5/GPT-4.1 等 12 模型）；新增 Shannon/MARSYS/REDEREF 框架；LLM 选型决策树；ICLR 2026 补充论文（LipNeXt/Newt/Cosmos Policy/VideoMind/Paper2Code）
> - 2026-05-07: v1.5 更新 — GPT-5.5 Instant 完整规格（Memory Sources、自我错误恢复、API 端点）；Kimi K2.6 GA 详细规格（1T/32B MoE、12h 运行、300-agent 群、Partner 验证）；Nemotron 3 Nano Omni 扩展（部署路径、H Company 实测）；Gemini API File Search 多模态化；新增 ICLR 2026 论文（MoGA 长视频生成、GRAM 递归推理、Drifting Models 一步生成）
> - 2026-05-08: **v1.6 更新** — 新增 Agent 基础设施发展（AWS Agent Toolkit GA、Google 50+ 托管 MCP 服务器、Microsoft AGT、Claude Mythos+Project Glasswing、MCP 2026 路线图、MCP v2 Beta）；Gemma 4 开源（26B MoE 旗舰 97% 质量）；MiniMax-M1 混合注意力推理模型；DR-Venus-4B / OpenSeeker-v2 开源深度研究 Agent；Grok 4.3、SubQ 次二次缩放注意力；Codex CLI Terminal-Bench 82.7%；openai-agents-python v0.16.0 默认模型切换；vLLM v0.20.1 DeepSeek V4 稳定化；Transformers v5.7.0 新模型；更新 2026 趋势观察（10 条）
> - 2026-05-09: **v1.7 更新** — 新增 GPT-5.5-Cyber 安全变体（5/8）；GPT-Realtime-2/Translate/Whisper 语音三模型（5/7）及三大语音 AI 模式；Anthropic Claude Managed Agents Dreaming/Outcomes/Multiagent（5/8，Harvey 6x、Netflix）；Google Gemini 3.1 Flash-Lite GA（5/7，60% 成本降低、JetBrains/Gladly/Ramp 案例）；Zyphra ZAYA1-8B 开源推理模型（5/6，<1B active params，AMD 训练）；AWS Agent Toolkit GA（5/6，40+ skills）；Salesforce Hosted MCP GA（4/29）；Azure MCP Server 2.0（4/10）；OpenAI Agents SDK 沙箱/记忆/MCP 更新（4/15）；Hermes Agent v0.13.0 Tenacity；更新趋势观察至 13 条
