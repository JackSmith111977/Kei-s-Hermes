---
name: knowledge-routing
description: "Guide for classifying new knowledge: Memory vs Skills. Use when absorbing experience or updating knowledge base."
version: 1.0.0
triggers: ["经验吸收", "知识分类", "记忆管理", "skill更新", "knowledge routing", "经验沉淀", "总结", "复盘", "踩坑", "教训", "记下来", "存入Memory", "存入Skill", "知识路由"]
---

# 知识路由指南 (Knowledge Routing Guide)

## 目标
在吸收新经验/教训时，快速判断是将其持久化到 **Memory** 还是 **Skill** 中。

## 决策流程

### 1. 存入 Memory 的情况
适用于**事实、偏好、环境特征、一次性教训**。
- **特征**：
  - 陈述性知识（Declarative Knowledge）。
  - 不需要步骤说明，只需知道"是什么"。
  - 使用频率低或仅作为背景上下文。
  - 用户个人偏好/习惯。
- **示例**：
  - "`read_file` 工具返回内容带行号前缀"（工具特性）
  - "用户偏好猫娘语气"（用户偏好）
  - "mihomo 代理端口是 7890"（环境配置）
  - "DeepSeek API Key 偶尔 401"（环境状态）

### 2. 存入/更新 Skill 的情况
适用于**流程、规范、避坑指南、最佳实践**。
- **特征**：
  - 程序性知识（Procedural Knowledge）。
  - 需要步骤说明、代码示例、检查清单（Checklist）。
  - 在未来 3 次以上独立任务中会重复使用。
  - 涉及多个步骤或工具的协调。
- **示例**：
  - "PDF 生成前必须使用 `pdftoppm` + `vision` 预览"（工作流规范）
  - "Python markdown 库推荐配置组合"（技术最佳实践）
  - "飞书发文件需先上传获 file_key 再发 file 消息"（API 操作 SOP）

## 判断清单 (Checklist)

遇到问题/经验时，按顺序问自己：

1. **这是一个事实还是一个流程？**
   - 事实 → 倾向 Memory
   - 流程 → 倾向 Skill
2. **它需要结构化展示（步骤、代码、示例）吗？**
   - 需要 → Skill
   - 不需要 → Memory
3. **它在未来会被频繁复用吗？**
   - 是（>3 次） → Skill
   - 否（偶尔参考） → Memory
4. **它是关于"如何做某事"还是"某事是什么"？**
   - 如何做 → Skill
   - 是什么 → Memory

## 🚩 Red Flags (常见错误)

- **把长流程塞进 Memory**：Memory 容量有限（2200 chars），且是扁平注入。长篇大论的操作 SOP 会导致上下文被淹没，必须存入 Skill。
- **把琐碎事实写进 Skill**：例如“某个 API 报错 500"，这种一次性事件只需 Memory 记录，建 Skill 会造成 Skill 库臃肿。
- **绕过 skill-creator**：创建/更新 Skill 时，**严禁**直接调用 `skill_manage` 而不先加载 `skill-creator`！必须经过 skill-creator 的检查清单。

## 执行动作

- **写入 Memory**：使用 `memory` 工具，`target="memory"`（笔记）或 `target="user"`（偏好）。
- **写入 Skill**：
  - 若有相关 Skill → `skill_manage(action="patch")` 更新。
  - 若无相关 Skill → `skill_manage(action="create")` 创建新 Skill。

## 评估用例 (Eval Cases)

1. **Eval-001 (事实类)**：
   - *输入*："GitHub API 现在需要新的 Token 格式了。"
   - *预期*：存入 Memory，不创建 Skill。
2. **Eval-002 (流程类)**：
   - *输入*："每次部署前都要先扫描敏感文件，步骤是 1...2...3..."
   - *预期*：存入/更新部署类 Skill。
3. **Eval-003 (防呆测试)**：
   - *输入*："我要把这个 500 字的流程存到 Memory 里。"
   - *预期*：触发 Red Flag 警告，建议拆分或转存 Skill。