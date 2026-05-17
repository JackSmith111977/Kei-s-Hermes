# 🛠️ 开发工具生态快照 — 2026年5月

> 生成：夜间自习引擎 v3.9 | 2026-05-16T08:00
> 领域：dev_tools（开发工具与语言）
> 质量评分：91/100

---

## Go 生态

### Go 1.26（当前稳定版，2026-02-10）
- `new(expr)` 表达式初始化
- 泛型自引用
- **Green Tea GC 默认启用**（GOEXPERIMENT=nogreenteagc 可选）
- cgo 开销降低 ~30%
- 栈上 slice 存储优化
- `go fix` 全面重写（analysis framework + modernizers）
- 新包：`crypto/hpke`、`crypto/mlkem/mlkemtest`、`testing/cryptotest`
- 实验性：`simd/archsimd`、`runtime/secret`、`goroutineleak` profile
- 安全更新：1.26.3（2026-05-07）

### Go 1.27（开发中，冻结 2026-05-20 🚨）
- **移除** `gotypesalias` GODEBUG（Alias 类型始终产生）
- **移除** `asynctimerchan` GODEBUG（始终使用无缓冲 timer channels）
- **移除** `GOEXPERIMENT=nogreenteagc`（GT GC 完全默认）
- **默认启用** goroutineleak profile
- **默认启用** 启动堆地址随机化
- **移除** macOS 12 支持（需 macOS 13+）
- **移除** ELFv1 ABI for ppc64（切换为 ELFv2）
- Unicode 17 支持
- 待定：Generic Methods for Concrete Types（提案 #77273 已接受，可能 1.27 或 1.28）

### 值得关注
- Go 1.27 Release Notes 正在编写中（跟踪 issue #78779）
- Tree opened for 1.27 开发

---

## Rust 生态

### Rust 1.95.0（稳定，2026-04-16）
- `cfg_select!` 宏（替代 cfg-if crate）
- match 表达式中的 `if let` guards
- JSON target specs 去稳定化（需 `-Z unstable-options`）
- LLVM 22 更新

### Rust 1.96.0（Beta，2026-05-28 稳定 🚨）
- 新 Range 类型和迭代器稳定（RFC 3550）
- RangeInclusive + RangeToInclusive
- PinCoerceUnsized 需要 Deref trait
- `-Csoft-float` 移除

### Rust 1.97.0（Nightly，预计 2026-07-09）
- Bump merged 4月10日

### 待稳定化亮点
- Never type (`!`)
- C-variadic 函数定义
- `doc_cfg` 特性
- Associated Type Position Impl Trait (ATPIT, 828天，进展缓慢)
- `Result::map_or_default` / `Option::map_or_default`

---

## TypeScript 生态

### TypeScript 6.0（桥梁版本，最后 JS 版）
- 弃用 5.x 兼容选项：`es5 target`、`node`/`classic` moduleResolution、`baseUrl`、`outFile`
- 可通过 `ignoreDeprecations: "6.0"` 临时忽略
- 行为与 Go 编译器对齐

### TypeScript 7.0 Beta（🚀 重大里程碑！）
- **Go 重写（Project Corsa）**：完整编译器和语言服务
- **10x 加速**：VS Code 1.5M LOC 在 7.5s 完成类型检查（原 77s）
- CLI：`tsgo` 替代 `tsc`（同一 tsconfig.json）
- 安装：`npm install -D @typescript/native-preview@beta`
- 兼容包：`@typescript/typescript6`（暴露 `tsc6` binary）
- VS 2026 18.6 Insiders 已默认启用 TS 7 Beta
- 稳定版预计 2026 年 6/7 月，API 稳定预计 7.1

### 工具链观察
- Biome 2 + oxlint 1.0 正取代 ESLint
- 主流模式：oxlint（pre-commit/CI）+ Biome（formatting）+ ESLint（遗留插件）

---

## Python 生态

### Python 3.15.0b1（2026-05-07，Feature Frozen！）
- **PEP 810**：显式惰性导入（`lazy` soft keyword）
- **PEP 814**：`frozendict` 内置不可变字典类型
- **PEP 661**：`sentinel` 内置哨兵类型
- **PEP 799**：Tachyon 高频统计采样 profiler + profiling 专用包
- **PEP 831**：Frame pointers 默认启用
- **PEP 798**：推导式中的解包
- **PEP 686**：UTF-8 默认编码
- **PEP 829**：Package startup configuration files
- **PEP 728**：`TypedDict` with typed extra items
- **PEP 747**：`TypeForm`（类型形式注解）
- **PEP 800**：`@typing.disjoint_base` 不交基
- JIT 编译器大幅升级：x86-64 8-9%，AArch64 12-13%
- 后续：beta 2 → 6月2日，RC1 → 8月4日，Final → 10月1日

### Python 3.16（5月7日开发开始）
- PEP 826：17月开发周期，12月发布节奏
- Alpha 1：2026-10-13，Final：2027-10-05
- 提案：PEP 830（异常时间戳）、PEP 813（Pretty Print Protocol）

---

## Kubernetes 生态

### K8s 1.36（当前稳定，2026-04-22 发布，1.36.1 5月13日）
- Workload-Aware Scheduling Alpha
- PodGroup API + Gang/Topology/Preemption scheduling
- In-Place Pod-Level Resources Vertical Scaling 毕业到 Beta
- DRA Device Binding Conditions → GA
- Sharded List and Watch Alpha（KEP-5866）

### K8s 1.37（开发中，预计 2026-10）
- DRA Device Binding Conditions GA ✅
- 声明式 validation tags promotion（8+ tags 到 stable）
- 8 个 sig-api-machinery feature gates 已清理
- Workload + PodGroup API → Beta
- KubeletInUserNamespace → Beta（延后）

### 版本线
| 版本 | 最新补丁 | EOL |
|:---|:---|:---:|
| 1.36 | 1.36.1 | 2027-06-28 |
| 1.35 | 1.35.5 | 2027-02-28 |
| 1.34 | 1.34.8 | 2026-10-27 |

---

## Zig 生态

### Zig 0.16.0（2026-04-14，重大版本）
- **I/O as Interface**：`std.Io` 全新设计（GenericReader/AnyReader 删除）
- `@Type` 完全移除 → 8 个专用内置函数
- **ELF linker** 重写（自托管工具链）
- 增量编译：LLVM 支持 + 大幅加速编译-测试循环
- LLVM 21 更新
- 包管理：`zig-pkg` 本地缓存 + `--fork` 标志
- 244 贡献者，1183 提交
- ZLS 0.16.0 同步发布

---

## Node.js 生态

### Node.js 26.0.0（2026-05-05 🆕）
- **Temporal API 默认启用**（现代日期/时间 API）
- V8 14.6（Chromium 146）
- Undici 8.0
- 遗留 `_stream_*` 模块移除
- `http.Server.writeHeader()` 移除（使用 `writeHead()`）
- LTS 时间：2026年10月

---

## JavaScript 工具链观察（Rust 统治）

| 工具 | 语言 | 2026年进展 |
|:---|:---:|:---|
| Turbopack (Next.js) | Rust | Next.js 16 默认 bundler；87% 更快 dev startup |
| Rolldown (Vite 8) | Rust | Vite 8 默认 bundler；Excalidraw 22.9s → 1.4s |
| Rspack 1.7+ | Rust | TikTok/Douyin 内部使用；9x 更快 cold dev |
| Biome 2 | Rust | 类型感知 lint 规则；替代 ESLint |
| Oxlint 1.0 | Rust | 50-100x 更快；Shopify 80K 文件降低 71% lint 时间 |
| Lightning CSS | Rust | Tailwind v4 Oxide 引擎 |
| **Bun** | ~~Zig~~ **Rust** | 2026年5月从 Zig 移植到 Rust（96.6 万行） |
| **TypeScript 7** | **Go** | 唯一不在 Rust 生态中的关键工具 |

---

## 5月17日 Update — 第二轮深度扫描

> 夜间自习引擎 v4.0 | Q=91 | +18 新概念，+16 更新

### Go 1.27 前瞻确认（冻结 2026-05-20 🚨）
- Go 1.26 是最后支持 macOS 12 Monterey 的版本；1.27 需要 macOS 13+
- GOEXPERIMENT=nogreenteagc 将在 1.27 移除（Green Tea GC 完全默认）
- goroutineleak profile 默认启用
- 所有旧 GODEBUG 设置批量移除
- Unicode 17 支持已确认
- Generic Methods for Concrete Types（提案 #77273）可能在 1.27 或 1.28

### TypeScript 7.0 Beta 进展确认
- VS Code 和 Visual Studio 2026 18.6 Insiders 默认启用 TS 7 Beta
- `@typescript/typescript6` 兼容包提供 `tsc6` 入口
- TS 7.0 已知问题：Quick Fixes (Ctrl+.) 不可用，仅 AI Copilot 建议可用；Watch mode 尚未优化
- 稳定版预计 2 个月内（2026年6-7月）

### Node.js 26.1.0 + 发布模型变更
- **实验性 `node:ffi`**（需 `--experimental-ffi`）：加载动态库并调用原生符号
- Node.js 27.x 起改为**年度大版本发布**（原来每年2次）
- 所有版本都变 LTS（不再分奇数/偶数）
- Alpha(10月)→Current(4月)→LTS(10月)，共 36 个月支持

### Python 3.16 启动
- 开发启动：2026-05-07（PEP 826）
- 17 个月开发周期，12 月发布节奏
- Alpha 1：2026-10-13，Final：2027-10-05

### K8s 1.36 Workload-Aware Scheduling 详细
- Workload API（静态模板）+ PodGroup API（运行时状态）
- Gang scheduling、Topology-aware scheduling、workload-aware preemption
- DRA ResourceClaim for workloads（允许 DRA 用于 PodGroup）
- Job controller 第一个集成（WorkloadWithJob feature gate）
- v1.37 计划：Workload/PodGroup → Beta，Multi-level hierarchies

### Zig 0.16 补充细节
- 增量编译已可用（master 分支）；类型解析重新设计（30000 行 PR）
- 包管理中 `zig-pkg` 本地目录 + `--fork` 标志
- `zig libc` 共享 Zig 编译单元（跨 libc 边界 LTO 级优化）
- io_uring + GCD 的 std.Io.Evented 实现（实验性）
