---
name: architecture-trilemma
description: "运行时(Runtime) vs 技能(Skill) vs 工具(Tool) — 三种Agent扩展机制的架构决策模式。当你需要在系统中设计一个新的组件时，先判断它属于三者中的哪一种，再决定它的集成方式、文档格式和安装流程。"
version: 1.1.0
triggers:
- 运行时
- runtime
- 技能
- skill
- 工具
- tool
- 架构设计
- 组件分类
- 决策模式
- 设计哲学迁移
author: Emma (小喵)
license: MIT
metadata:
  hermes:
    tags:
    - architecture
    - design-pattern
    - decision-making
    - runtime
    - skill
    - tool
    category: meta
    skill_type: methodology
    design_pattern: decision-tree
depends_on: []

---

# 🔱 架构三难抉择：运行时 vs 技能 vs 工具

> **真正的架构决策，是搞清楚"这个东西属于哪一层"。**

## 一、核心定义

### 技能（Skill）

**定义**：Agent 可以按需加载的知识单元。一份说明"怎么做"的文档+配套脚本。

**特征**：
- **按需加载**：Agent 在需要时才 `skill_view` 加载
- **消费方式**：被 Agent 读取并理解后执行
- **典型的 SKILL.md**：设计哲学 + 命令参考 + 技术事实
- **生命周期**：随 Agent 会话开始/结束
- **失败影响**：局部——该技能相关的任务无法完成

**例子**：`web-access`, `pdf-layout`, `mermaid-guide`, `linux-ops-guide`

**信号词**：教我、帮我做、使用 XX 工具、加载 XX 技能

### 运行时（Runtime）

**定义**：后台常驻的服务进程，为 Agent 的消息管道提供基础设施能力。

**特征**：
- **常驻运行**：7x24 守护进程，独立于 Agent 存在
- **消费方式**：Agent 通过 API（HTTP/Socket）调用，与 Agent 进程分离
- **集成方式**：消息前置拦截（Proxy 模式）或系统 prompt 注入
- **生命周期**：独立于 Agent 会话启动/停止
- **失败影响**：全局——Agent 失去某项基础设施能力
- **不占用 Agent 上下文**：不在 SKILL.md 中，是 Agent 平台的一部分

**例子**：SRA (Skill Runtime Advisor), CDP Proxy, RAG 检索服务

**信号词**：后台服务、守护进程、常驻、中间件、消息拦截、基础设施

### 工具（Tool）

**定义**：Agent 可以调用的原子操作。一个函数、一个 API 端点、一个 CLI 命令。

**特征**：
- **单次调用**：一次请求，一次响应
- **消费方式**：Agent 通过 Hermes Agent 的 built-in tool 机制调用
- **集成方式**：Hermes Agent 原生提供，不需要额外交互
- **生命周期**：瞬时
- **Agent 知道它的存在**：在 tool 列表中

**例子**：`terminal`, `read_file`, `write_file`, `browser_navigate`, `image_generate`

---

## 二、架构决策树

```
你要设计一个新的 Agent 组件：
  ↓
  是常驻服务，需要 7x24 运行？
  ├─ ✅ → 运行时（Runtime）
  │   - 设计为守护进程
  │   - 通过 HTTP API 暴露能力
  │   - 属于 Agent 基础设施，不写 SKILL.md
  │   - 集成方式：Proxy 模式 / 系统注入
  │   - 例：SRA、RAG服务、CDP Proxy
  │
  └─ ❌ → Agent 按需使用？
      ├─ 是原子操作（一个函数/一个命令）？
      │  ├─ ✅ → 工具（Tool）
      │  │   - Hermes Agent 内置
      │  │   - 无需额外文档
      │  │   - 例：terminal, read_file
      │  │
      │  └─ ❌ → 技能（Skill）
      │      - 设计为 SKILL.md
      │      - 包含哲学层 + 命令参考 + 技术事实
      │      - Agent 按需 skill_view 加载
      │      - 例：web-access, pdf-layout
```

---

## 三、三种模式的集成差异对比

| 维度 | 技能（Skill） | 运行时（Runtime） | 工具（Tool） |
|------|-------------|------------------|-------------|
| 需要 SKILL.md？ | ✅ 核心文件 | ❌ 不需要 | ❌ 不需要 |
| 安装方式 | 放入技能目录即可 | pip + daemon + 启动脚本 | Hermes Agent 内置 |
| 用户感知 | Agent 自动加载 | 用户可能需 `sra start` | 用户无感 |
| 依赖关系 | 可能依赖运行时 | 独立运行 | 无依赖 |
| 出错影响 | 局部 | 全局 | 局部 |
| 文档密度 | 中 | 高（API+部署+运维） | 低 |
| 是否在 Agent 上下文中 | 是（加载后） | 否（通过 API 调用） | 是（内置在工具列表） |

---

## 四、反模式（踩坑记录）

### 反模式 1：把运行时当成技能来设计

**表现**：给一个运行时写 SKILL.md，期望 Agent 通过 `skill_view` 加载它

**后果**：
- Agent 加载后不知道"该做什么"——运行时是后台常驻的，不是按需操作的
- 运行时需要 systemd 管理生命周期，不是 Agent 会话
- 前置检查在每次会话时执行，但运行时应在机器启动时就运行

**已踩坑案例**：给 SRA 创建 SKILL.md，期望 Agent 把它当技能使用

**修正方案**：运行时以独立项目存在，不放在 skills/ 目录下。源码统一存放于 `~/projects/<name>/`。

### 反模式 2：照抄另一个模式的设计哲学

**表现**：把 common patterns 从一个模式直接套用到另一个模式

**后果**：运行时需要的不是"前置检查→哲学→命令参考"，而是"部署→API 参考→运维指南"

**已踩坑案例**：照抄 web-access 的 SKILL.md 结构来写 SRA 的文档

**修正方案**：每种模式有自己的文档范式，不要跨模式照抄

### 反模式 3：先照抄后验证

**表现**：看到一个成功的项目，不假思索地把它的设计模式照搬到自己的项目，没有验证"这个设计适不适合我的场景"

**后果**：花了时间做错了方向的改动，需要通过验证测试才发现根本问题

**已踩坑案例**：给 SRA 创建 SKILL.md、.claude-plugin/——直到验证测试才发现 SRA 的本质是运行时

**修正方案**：**先验证，再设计**——任何设计决策前，先跑验证测试确认核心假设

---

## 五、验证驱动的设计修正流程

当怀疑"当前设计方向错了"时：

```
1. 停止当前工作，回顾核心需求
2. 评估当前设计属于哪个模式
3. 设计验证测试（至少 3 个核心测试）
4. 执行测试，收集证据
5. 根据证据修正设计
```

### 核心验证指标

| 模式 | 核心验证指标 |
|------|------------|
| 运行时 | daemon 是否常驻？API 是否可用？自动恢复？ |
| 技能 | Agent 能否加载后执行？命令是否可用？ |
| 工具 | 单次调用立即有结果？出错可恢复？ |

---

## 六、一句话原则

> **技能告诉 Agent "怎么做"，运行时告诉 Agent "去哪问"，工具替 Agent "直接做"。**

---

## 七、存放位置规范

决定了一个组件属于哪种模式后，源码应该放在哪里？

| 模式 | 存放位置 | 原因 |
|:-----|:---------|:------|
| 🏃 **运行时 (Runtime)** | `~/projects/<name>/` | 独立项目，有自己 Git 仓库和生命周期。通过 editable pip install 关联到 Hermes venv。运行时数据放在 `~/.<name>/`（如 `~/.sra/`）。 |
| 📜 **技能 (Skill)** | `~/.hermes/skills/<category>/<name>/` | 技能是 Hermes 内部的知识单元，放在 SKILL.md + references/ 结构内。 |
| 🔧 **工具 (Tool)** | Hermes Agent 内置 | 工具是 Hermes Agent 代码库的一部分，由工具注册机制管理。 |

### 运行时项目目录示例

```
~/projects/
├── sra/            # SRA 运行时（editable 安装）
└── ...             # 未来的独立运行时项目
~/.sra/             # SRA 运行时数据（配置、日志、PID）
```

### ⚠️ 原则

- ❌ **不要放 `/tmp/`** — 临时目录，重启可能被清
- ❌ **不要放 `~/.hermes/`** — 那是 Hermes Agent 自身领地
- ❌ **不要放 `~/`** — 家目录会变杂乱
- ✅ **统一放 `~/projects/`** — 标准、持久、可维护
