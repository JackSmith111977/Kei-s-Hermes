# Knowledge Base: 开发工具与语言 (dev_tools)

## Go 1.24 Features

### go1.24_swiss_tables
**状态**: mastered | **复习日期**: 2026-05-07

**核心内容**:
- Go 1.24 使用 Swiss Table 重构 map 实现，基于 Google Abseil 设计
- 8-slot group + control word（每 slot 1 byte 存 h2 低 7 位 hash）
- SIMD/SWAR 并行探测：单指令检查 8 个候选匹配
- 多表架构：单表上限 1024 entries，超出后 split 为多表（extendible hashing）

**性能数据**:
- 微基准：map 操作最高提升 60%
- 全应用基准：CPU 时间几何平均提升 ~1.5%

**来源**: go.dev/blog/swisstable (2025-02)

---

### go1.24_weak_pointer
**状态**: developing | **复习日期**: 2026-05-07

**核心内容**:
- 新 `weak` 包提供 `weak.Pointer[T]` 类型
- GC 时忽略 weak pointer 引用，允许对象被回收
- 配合 runtime.AddCleanup 使用

**来源**: go.dev/blog/cleanups-and-weak (2025-02)

---

### go1.24_tool_directive
**状态**: mastered | **复习日期**: 2026-05-07

**核心内容**:
- `go get -tool <path>` 添加 tool directive 到 go.mod
- `go tool <name>` 执行版本化的工具

**来源**: rednafi.com/go/tool_directive (2025-04)

---

## TypeScript 5.8 Features

### ts5.8_erasable_syntax
**状态**: developing | **复习日期**: 2026-05-07

**核心内容**:
- `--erasableSyntaxOnly` 禁用有运行时语义的 TS 语法
- 配合 Node.js 23.6+ `--experimental-strip-types`

**来源**: devblogs.microsoft.com/typescript (2025-02)

---

### ts5.8_require_esm
**状态**: developing | **复习日期**: 2026-05-07

**核心内容**:
- Node.js 22+ 支持 `require("esm")`
- `--module nodenext` 支持此行为

**来源**: typescriptlang.org/tsconfig/module.html

---

## Python 3.14 Features

### python3.14_free_threaded
**状态**: developing | **复习日期**: 2026-05-07

**核心内容**:
- PEP 779：Free-threaded Python 正式支持（Phase II）
- 性能损失降至 5-10%（单线程）

**来源**: docs.python.org/3.14/howto/free-threading-python.html

---

### python3.14_deferred_annotations
**状态**: developing | **复习日期**: 2026-05-07

**核心内容**:
- PEP 649/749：注解延迟评估
- annotationlib 模块

**来源**: docs.python.org/3.14/library/annotationlib.html

---

### python3.14_t_strings
**状态**: developing | **复习日期**: 2026-05-07

**核心内容**:
- PEP 750：Template string literals（t-strings）
- `t` 前缀，返回 Template 对象

**来源**: docs.python.org/3.14/library/string.templatelib.html

---

### python3.14_subinterpreters
**状态**: developing | **复习日期**: 2026-05-07

**核心内容**:
- PEP 734：`concurrent.interpreters` 模块
- 多解释器同进程，隔离执行上下文

**来源**: docs.python.org/3.14/library/concurrent.interpreters.html
