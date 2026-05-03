# Pipeline 进度追踪格式规范
> 基于 BMAD step-file architecture 的进度追踪标准

**适用模式：** Pipeline（流水线/管道）模式

---

## 核心原则

1. **Just-In-Time Loading** — 只加载当前 step 文件，不预加载后续
2. **Sequential Enforcement** — 禁止跳步，必须按顺序完成
3. **State Tracking** — 通过 progress.yaml 追踪进度
4. **Append-Only Building** — 逐步构建，每步完成后追加到 stepsCompleted
5. **Cleanup After Completion** — 任务完成后清除 temp/ 目录

---

## progress.yaml 格式

```yaml
# 进度追踪文件
# 存放位置：temp/progress.yaml
# 任务完成后连同 temp/ 目录一并清除

stepsCompleted:          # 已完成步骤列表（追加式）
  - step-01-init         # 第一步完成
  - step-02-discovery    # 第二步完成
currentStep: step-03-generate   # 当前正在执行的步骤
nextStep: step-04-validate      # 下一步（完成当前后加载）
checkpoint: user-confirm        # 当前步骤的检查点类型
status: in-progress             # in-progress | completed | failed | halted
createdAt: 2026-04-27T10:00:00 # 任务开始时间
updatedAt: 2026-04-27T10:30:00 # 最后更新时间

# 可选：任务元数据
metadata:
  skillName: prd-creator
  outputTarget: docs/prd.md
  userRequest: "创建 PRD"
```

---

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `stepsCompleted` | array | 是 | 已完成步骤 ID 列表，追加式记录 |
| `currentStep` | string | 是 | 当前执行的步骤 ID |
| `nextStep` | string | 是 | 下一步 ID（用于检查点后加载） |
| `checkpoint` | enum | 是 | 检查点类型：`user-confirm` / `self-check` / `auto-verify` |
| `status` | enum | 是 | `in-progress` / `completed` / `failed` / `halted` |
| `createdAt` | datetime | 是 | 任务创建时间（ISO 8601） |
| `updatedAt` | datetime | 是 | 最后更新时间（ISO 8601） |
| `metadata` | object | 否 | 任务相关元数据 |

---

## 检查点类型

| 类型 | 触发条件 | 执行方式 |
|------|----------|----------|
| `user-confirm` | 需要用户确认下一步 | 停止执行，等待用户输入 |
| `self-check` | Agent 自检 | 执行自检逻辑，通过后自动继续 |
| `auto-verify` | 脚本/工具验证 | 运行验证脚本，通过后自动继续 |

---

## Step 文件格式

每个步骤独立文件，存放在 `temp/steps/`：

```yaml
---
stepId: step-03-generate
stepName: 生成草稿
checkpoint: user-confirm
requires:           # 前序依赖（硬性门控）
  - step-01-init
  - step-02-discovery
produces:           # 本步骤产出
  - draft: string
nextStep: step-04-validate
---

# 步骤 3：生成草稿

## 前置检查
验证 progress.yaml 中 `stepsCompleted` 包含：
- step-01-init
- step-02-discovery

如果缺失，**HALT** 并提示："前序步骤未完成，请先完成 [缺失步骤]"

## 执行内容
[具体执行指令...]

## 完成条件
- [ ] 草稿已生成
- [ ] 用户已确认草稿内容

## 完成后操作
1. 更新 progress.yaml：
   - 将 `step-03-generate` 追加到 `stepsCompleted`
   - 设置 `currentStep: step-04-validate`
   - 更新 `updatedAt`
2. 如果 `checkpoint: user-confirm`：
   - 停止执行
   - 输出："草稿已生成，等待确认后继续下一步"
   - 等待用户确认
3. 用户确认后：
   - 加载 `step-04-validate.md`
   - 继续执行
```

---

## 硬性门控规则

### 启动检查

**每个步骤开始前必须验证：**

```yaml
# 门控验证逻辑
validate_gate:
  check: progress.yaml exists
  if_not: HALT "progress.yaml 不存在，请先初始化"
  check: currentStep == this.stepId
  if_not: HALT "当前步骤不匹配，请按顺序执行"
  check: all requires in stepsCompleted
  if_not: HALT "前序步骤未完成: [missing_steps]"
```

### 禁止事项

```markdown
🛑 **NEVER** 加载多个 step 文件同时执行
🛑 **NEVER** 跳过任何步骤
🛑 **NEVER** 在未通过检查点时继续
🛑 **NEVER** 合并多个步骤为一个
🛑 **NEVER** 修改 stepsCompleted 的历史记录
🛑 **NEVER** 在未验证前序步骤完成时开始新步骤
```

---

## 初始化流程

```yaml
# 步骤 1：初始化
---
stepId: step-01-init
stepName: 初始化任务
checkpoint: self-check
requires: []        # 无前序依赖
produces:
  - progress.yaml
  - configLoaded: boolean
nextStep: step-02-discovery
---

# 步骤 1：初始化

## 执行内容
1. 创建 `temp/` 目录
2. 创建 `temp/progress.yaml`：
```yaml
stepsCompleted: []
currentStep: step-01-init
nextStep: step-02-discovery
checkpoint: self-check
status: in-progress
createdAt: [current_time]
updatedAt: [current_time]
```
3. 加载配置（如 config.yaml）

## 完成后操作
更新 progress.yaml：
- 追加 `step-01-init` 到 `stepsCompleted`
- 设置 `currentStep: step-02-discovery`
- 加载并执行 `step-02-discovery.md`
```

---

## 完成流程

```yaml
# 最后步骤完成后
---
stepId: step-final-complete
stepName: 任务完成
checkpoint: self-check
requires:
  - step-01-init
  - step-02-xxx
  - step-03-xxx
produces:
  - finalOutput: file
nextStep: null      # 无下一步
---

# 步骤 N：任务完成

## 执行内容
1. 生成最终输出
2. 验证所有产出完整

## 完成后操作
更新 progress.yaml：
- 追加 `step-final-complete` 到 `stepsCompleted`
- 设置 `status: completed`
- 设置 `currentStep: null`

## 清理操作
任务完成后：
1. 删除 `temp/steps/` 目录
2. 删除 `temp/progress.yaml`
3. 可选：保留 `temp/` 作为任务记录（用户决定）
```

---

## 异常处理

### HALT 状态

```yaml
# 任务暂停
status: halted
haltReason: "前序步骤未完成"
missingSteps: [step-01-init]
resumable: true     # 是否可恢复
```

### 失败状态

```yaml
# 任务失败
status: failed
failedStep: step-03-generate
failureReason: "草稿生成失败"
errorDetails: "..."
```

---

## 目录结构

```
skill-name/
├── SKILL.md           # 主文件（含硬性门控指令）
├── temp/              # 临时目录（任务完成清除）
│   ├── steps/         # Step 文件目录
│   │   ├── step-01-init.md
│   │   ├── step-02-discovery.md
│   │   ├── step-03-generate.md
│   │   └── step-04-validate.md
│   └── progress.yaml  # 进度追踪文件
├── references/        # 持久化资源
│   ├── pipeline-progress-format.md
│   └── ...
└── outputs/           # 输出目录（持久化）
    └── final-output.md
```

---

## 适用 Skill 类型

| Skill 类型 | 设计模式组合 | 是否需要 Pipeline 进度追踪 |
|-----------|-------------|---------------------------|
| **产品验证** | Pipeline + Reviewer | **是** |
| **部署流程** | Pipeline + Reviewer | **是** |
| **代码生成** | Generator + Pipeline | **是** |
| **文档生成** | Generator + Inversion | 否（使用 Inversion 门控） |
| **代码审查** | Reviewer + Tool Wrapper | 否 |
| **调研整理** | Inversion + Generator | 否 |

---

*格式版本：1.0.0 | 基于 BMAD step-file architecture*
