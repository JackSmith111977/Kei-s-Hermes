# 2025-2026 Python 生态更新速查

> 来源：KDnuggets, Anaconda, Tryolabs, Git Connected (2025-2026)

## 🆕 值得关注的 Python 新库

| 库名 | 用途 | 亮点 |
|:---|:---|:---|
| **FastMCP** | MCP 服务端/客户端框架 | 构建 Model Context Protocol 服务器的轻量框架，适合扩展 Hermes MCP 能力 |
| **Polars** | DataFrame 库 | Rust 编写，比 pandas 快数倍，支持懒加载和流式处理 |
| **Pixi** | 包/环境管理器 | conda/pip 的替代品，跨平台、可复现的环境管理 |
| **Dramatiq** | 分布式任务队列 | Celery 的轻量替代，基于 Redis/RabbitMQ，API 更简洁 |
| **Scrapling** | 网页抓取 | 现代爬虫库，内置反检测能力，API 友好 |
| **pydoll** | 浏览器自动化 | 轻量级浏览器控制库 |
| **Maliang** | 绘图/可视化 | 轻量可视化库 |
| **Pyecharts** | 数据可视化 | ECharts 的 Python 封装，适合生成交互式图表 |
| **opentemplate** | 项目模板 | 全功能 Python 项目脚手架，内置代码质量/安全/自动化工具链 |
| **GeoAI** | 地理空间 AI | 集成 PyTorch/Transformers/Segmentation Models，处理遥感影像搜索/下载/训练/推理，Leafmap 可视化 |

## 🤖 AI Agent 框架

| 框架 | 来源 | 特点 |
|:---|:---|:---|
| **Google ADK** (Agent Development Kit) | Google | 代码优先的 Agent 构建框架，强调软件工程最佳实践 |
| **OpenAI Agents SDK** | OpenAI | 多 Agent 工作流框架，支持 OpenAI API + 100+ 其他 LLM，provider-agnostic |
| **Data Formulator** | Microsoft Research | AI 驱动的数据探索工具，自动生成可视化 |

## 📄 文档/LLM 工具

| 工具 | 用途 |
|:---|:---|
| **markitdown** | 将各种格式（PDF、PPT、Excel、图片 OCR）转为 Markdown，保留标题/表格/列表结构，专为 LLM 工作流设计 |
| **Python Testing Tools MCP Server** | MCP 服务器，提供 AI 驱动的 Python 测试能力（单元测试生成、模糊测试、覆盖率分析、变异测试） |

## 🦀 Rust 标准库新增（Rust 1.85+）

- `slice.array_windows` — 滑动窗口返回数组引用
- `slice.element_offset` — 安全的元素偏移计算
- `LazyCell::get` / `LazyLock::get` — 惰性初始化值的非变异访问
- `LazyCell::force_mut` / `LazyLock::force_mut` — 强制初始化并获取可变引用
- `String::into_raw_parts` / `Vec::into_raw_parts` — 分解为原始指针/长度/容量
- `Peekable::next_if_map` — peek 后条件消费并映射

## 🔮 2026 前端框架趋势（了解即可）

- **React 19** — Server Components 已生产就绪（19.2 验证），68% 大型企业使用 React
- **Svelte 5** — 当前版本，最佳性能/DX 平衡，细粒度响应式
- **Vue 4** — 当前版本，快速启动 + 强生产力平衡
- **Astro** — 框架无关，支持混用 React/Vue/Svelte，Islands 架构，只发送 HTML 到浏览器
- **Angular Signals** — v17 起提供细粒度响应式
- **Qwik** — 可恢复性架构，慢网络下 TTI 快 4 倍
- **Solid.js** — 极致运行时性能，bundle 极小
- **Ripple** — 🆕 全新 TypeScript UI 框架，融合 React/Solid/Svelte 优点。使用 `.tsrx` 编译语法，信号式细粒度响应式核心（`track` + lazy destructuring），`RippleSet/RippleArray/RippleMap/RippleObject` 响应式数据结构。早期开发阶段
- **Next.js 16** — React 生态 SSR/SSG 元框架，SEO 最佳选择
- **Nuxt** — Vue 生态 SSR 元框架

### 📊 Stack Overflow 2025 前端框架使用率
React 44.7% | Angular 18.2% | Vue.js 17.6% | AngularJS 7.2% | Svelte 7.2%

## 🛠️ 2026 DevOps 工具更新

### Terraform 生态（HashiConf 2025）
- **Terraform Stacks** — GA 发布，基础设施编排层，统一管理多模块大规模基础设施
- **Terraform MCP Server** — 连接 HCP Terraform 到 AI 助手，支持自然语言基础设施管理
- **Terraform HYOK** (Hold Your Own Key) — 用户自控加密密钥，保护 HCP Terraform 敏感数据
- **Terraform Actions** — Day-2 自动化，编排多模块工作流
- **IBM 收购 HashiCorp 后许可变更** — BUSL 许可证影响，OpenTofu 作为开源替代方案崛起

### HashiCorp 生态趋势
- HCP Terraform 从"运行计划"演进为"运行平台"，Stacks 编排多模块
- Vault 扩展 SPIFFE 认证和合规改进
- Project InfraGraph (IBM/HashiCorp) — 智能基础设施自动化预览，向 Agentic 运维演进
