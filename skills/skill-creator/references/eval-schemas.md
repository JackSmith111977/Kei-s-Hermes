# Eval 评估体系 — JSON Schema 与数据格式
> 基于官方 skill-creator 的评估体系，适配本地 Skill 创建流程

**版本：** 1.0.0 | **来源：** anthropics/skills/skill-creator/references/schemas.md

---

## 1. evals.json — 测试用例定义

**存放位置：** `[skill-name]/evals/evals.json`
**用途：** 定义 Skill 的测试用例，每个用例包含输入 prompt、预期输出和验证期望。

### 结构

```json
{
  "skill_name": "my-skill-name",
  "evals": [
    {
      "id": "eval-001",
      "prompt": "帮我调研 TypeScript 5.0 的新特性",
      "expected_output": "一份 Markdown 格式的调研报告，包含新特性列表、代码示例、迁移建议",
      "files": ["output/report.md"],
      "expectations": [
        "输出包含 Markdown 格式的调研报告",
        "报告包含至少 3 个新特性的代码示例",
        "报告包含迁移建议章节",
        "Skill 执行了网络搜索获取最新信息"
      ]
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `skill_name` | string | 是 | 被测试的 Skill 名称 |
| `evals[]` | array | 是 | 测试用例列表 |
| `evals[].id` | string | 是 | 唯一标识，格式 `eval-NNN` |
| `evals[].prompt` | string | 是 | 触发 Skill 的输入 |
| `evals[].expected_output` | string | 是 | 预期输出描述 |
| `evals[].files` | string[] | 否 | 预期生成的文件路径 |
| `evals[].expectations` | string[] | 是 | 验证期望列表，用于 Grader 评分 |

### 编写原则

1. **期望要可验证** — 不要写"输出质量好"，要写"输出包含 X 章节"
2. **期望要区分** — 好的期望在 Skill 真正成功时通过，失败时不通过
3. **覆盖多种场景** — 正常路径、边界情况、错误输入
4. **先写 prompt，后写期望** — 不要一开始就写断言，先定义输入

---

## 2. grading.json — 评分结果

**存放位置：** `[skill-name]/evals/runs/<run-id>/grading.json`
**用途：** Grader Agent 对一次执行结果的评分输出。

### 结构

```json
{
  "expectations": [
    {
      "text": "输出包含 Markdown 格式的调研报告",
      "passed": true,
      "evidence": "Found in output/report.md: '# TypeScript 5.0 新特性调研报告'"
    },
    {
      "text": "报告包含至少 3 个新特性的代码示例",
      "passed": true,
      "evidence": "Found 5 code blocks with TypeScript 5.0 features"
    },
    {
      "text": "Skill 执行了网络搜索",
      "passed": false,
      "evidence": "No WebSearch/WebFetch tool calls found in transcript"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Write": 2,
      "Glob": 1
    },
    "total_tool_calls": 8,
    "total_steps": 4,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "报告覆盖了 5 个新特性",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 5 distinct feature sections"
    },
    {
      "claim": "所有代码示例都可运行",
      "type": "quality",
      "verified": false,
      "evidence": "Decorator 示例缺少 import 语句"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["使用了 2023 年数据，可能过时"],
    "needs_review": [],
    "workarounds": ["降级使用了文本覆盖方案"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "输出包含 Markdown 格式的调研报告",
        "reason": "一个文件名正确但内容为空的文档也会通过 — 建议增加内容验证"
      }
    ],
    "overall": "期望检查了存在性但未检查正确性。建议增加内容验证。"
  }
}
```

### 评分标准

| 结果 | 条件 |
|------|------|
| **PASS** | 转录或输出清楚证明期望为真，且有具体证据 |
| **FAIL** | 无证据、证据矛盾、或证据仅为表面合规 |
| **不确定** | 举证责任在期望方，无法验证则判 FAIL |

### Claims 验证

Grader 不仅检查预定义期望，还会：
1. 从输出中**提取隐含声明**（如"报告覆盖了 5 个特性"）
2. **验证声明** — 事实类查输出，过程类查转录，质量类做判断
3. **标记不可验证的声明**

---

## 3. metrics.json — 执行指标

**存放位置：** `[skill-name]/evals/runs/<run-id>/outputs/metrics.json`
**用途：** 记录执行过程中的工具调用、文件生成、错误等指标。

### 结构

```json
{
  "tool_calls": {
    "Read": 5,
    "Write": 2,
    "Glob": 1,
    "Grep": 3
  },
  "total_tool_calls": 11,
  "total_steps": 6,
  "files_created": ["output/report.md", "output/summary.md"],
  "errors_encountered": [],
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

---

## 4. timing.json — 时间记录

**存放位置：** `[skill-name]/evals/runs/<run-id>/timing.json`
**用途：** 记录每次运行的 Wall Clock 时间。

### 结构

```json
{
  "total_tokens": 45000,
  "executor": {
    "start": "2026-04-10T10:00:00Z",
    "end": "2026-04-10T10:02:45Z",
    "duration_ms": 165000
  },
  "grader": {
    "start": "2026-04-10T10:02:45Z",
    "end": "2026-04-10T10:03:11Z",
    "duration_ms": 26000
  }
}
```

> **注意：** 时间数据需要立即保存，不会被持久化到其他位置。

---

## 5. history.json — 版本追踪

**存放位置：** `[skill-name]/evals/history.json`
**用途：** 追踪 Skill 在改进过程中的版本演进。

### 结构

```json
{
  "started_at": "2026-04-10T09:00:00Z",
  "skill_name": "research",
  "current_best": "v3",
  "iterations": [
    {
      "version": "v1",
      "parent": null,
      "expectation_pass_rate": 0.50,
      "grading_result": "grading-v1.json",
      "changes": "初始版本"
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.75,
      "grading_result": "grading-v2.json",
      "changes": "增加网络搜索步骤，优化触发词"
    },
    {
      "version": "v3",
      "parent": "v2",
      "expectation_pass_rate": 0.92,
      "grading_result": "grading-v3.json",
      "changes": "补充调研结果验证，优化输出模板"
    }
  ]
}
```

---

## 6. 盲对比（可选高级评估）

**适用场景：** 需要严谨验证 Skill 是否真正有效。

### 方法

对每个测试用例，**同时运行两次**：
- **有 Skill 版本** — Claude 加载了该 Skill
- **无 Skill 版本** — Claude 不加载该 Skill

然后由 Comparator Agent 对比两者的输出质量，判定哪个更好。

### 对比维度

| 维度 | 说明 |
|------|------|
| **内容完整性** | 是否覆盖了所有期望的内容 |
| **结构一致性** | 输出结构是否符合模板 |
| **指令遵循** | 是否遵循了 Skill 的特殊指令 |
| **效率** | 工具调用次数、Token 消耗、执行时间 |

---

## 7. benchmark.json — 基准测试（可选）

**存放位置：** `benchmarks/<timestamp>/benchmark.json`

### 结构

```json
{
  "metadata": {
    "skill_name": "research",
    "timestamp": "2026-04-10T10:00:00Z",
    "num_evals": 5
  },
  "runs": [
    {
      "configuration": "with_skill",
      "eval_id": "eval-001",
      "pass_rate": 0.92,
      "duration_seconds": 165,
      "tokens": 45000
    },
    {
      "configuration": "without_skill",
      "eval_id": "eval-001",
      "pass_rate": 0.60,
      "duration_seconds": 120,
      "tokens": 38000
    }
  ],
  "run_summary": {
    "with_skill": {
      "avg_pass_rate": 0.88,
      "avg_duration_seconds": 155,
      "avg_tokens": 42000
    },
    "without_skill": {
      "avg_pass_rate": 0.55,
      "avg_duration_seconds": 110,
      "avg_tokens": 35000
    },
    "improvement": {
      "pass_rate": "+33%",
      "duration": "+41s",
      "tokens": "+7k"
    }
  }
}
```

---

*本文档定义了完整的评估数据格式，供 Stage 9: 自动化评估 使用。*
