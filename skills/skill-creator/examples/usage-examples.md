# Skill 使用示例
> 展示 skill-creator 的完整使用流程

## 示例 1：创建一个简单的 Tool Wrapper Skill

**需求：** 创建 `pandas-helper` Skill，教 Claude 正确使用 pandas 常见操作。

### Step 1：构思

\`\`\`
用户：我想创建一个 Skill，让我在使用 pandas 时能自动应用最佳实践。
\`\`\`

### Step 2：定义用例

1. 用户说"用 pandas 读取 CSV 并分析" → 触发
2. 用户说"pandas 数据清洗" → 触发
3. 用户说"用 SQL 查询数据库" → 不触发

### Step 3：选择模式

**Tool Wrapper** — 封装 pandas 最佳实践

### Step 4：生成 SKILL.md

\`\`\`markdown
---
name: pandas-helper
description: 使用 pandas 进行数据分析时自动应用最佳实践。触发词：pandas、数据分析、CSV处理、DataFrame
---

# Pandas Helper

## 快速入门
...
## 常用操作
...
## 踩坑清单
...
\`\`\`

### Step 5：测试

\`\`\`json
{
  "skill_name": "pandas-helper",
  "evals": [
    {
      "id": "eval-001",
      "prompt": "用 pandas 读取 data.csv 并统计每列的缺失值",
      "expected_output": "使用 pd.read_csv() 读取，用 isna().sum() 统计缺失值",
      "expectations": [
        "使用 pd.read_csv() 读取文件",
        "使用 isna().sum() 而非手动循环",
        "输出包含缺失值统计"
      ]
    }
  ]
}
\`\`\`

### Step 6：评估

运行测试，Grader 评分：
- eval-001: 3/4 通过（75%）
- 失败项：未使用 isna().sum()，用了手动循环

### Step 7：改进

修改 SKILL.md，加强"使用向量化操作"的指令。

### Step 8：重测

通过率提升到 100%，完成。

---

## 示例 2：创建一个 Pipeline 模式的部署 Skill

**需求：** 创建 `deploy-webapp` Skill，自动化部署 Web 应用。

### Step 1：定义 Pipeline 步骤

1. 部署前检查（self-check）
2. 备份（auto-verify）
3. 部署（user-confirm）
4. 验证（auto-verify）
5. 监控（self-check）

### Step 2：创建 progress.yaml 模板

\`\`\`yaml
stepsCompleted: []
currentStep: step-01-preflight
nextStep: step-02-backup
checkpoint: self-check
status: in-progress
createdAt: {{timestamp}}
updatedAt: {{timestamp}}
\`\`\`

### Step 3：创建 Step 文件

每个步骤独立文件：\`temp/steps/step-01-preflight.md\` ...

### Step 4：测试 Pipeline

执行完整流程，验证每个检查点正常工作。

---

## 示例 3：创建一个调研 Skill

**需求：** 创建 `tech-research` Skill，调研技术选型。

### Step 1：逆向定义

先定义"好的调研报告"标准：
- 覆盖面广
- 有数据支持
- 有时效性
- 来源可信

### Step 2：创建调研模板

\`\`\`markdown
# {{主题}} 调研报告
## 执行摘要
## 背景
## 核心发现
## 对比分析
## 结论与建议
## 参考资料
\`\`\`

### Step 3：测试

用 3 个不同主题测试，验证输出质量。

---

*示例版本：1.0.0 | skill-creator v10.1.0*
