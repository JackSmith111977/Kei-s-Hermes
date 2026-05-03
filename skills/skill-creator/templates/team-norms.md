---
template-type: team-norms
name: 团队规范模板
description: 用于创建团队编码规范类 Skill 的 Tool Wrapper 模式模板
---

# [团队/项目] 编码规范

## 用途
当用户在 [团队/项目] 中编写代码时，自动应用本规范。

**适用场景：**
- 编写 [语言] 代码
- Code Review
- 新项目初始化

---

## 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | camelCase | \`userName\` |
| 函数 | camelCase | \`getUserInfo()\` |
| 类 | PascalCase | \`UserService\` |
| 常量 | UPPER_SNAKE | \`MAX_COUNT\` |
| 文件 | kebab-case | \`user-service.ts\` |
| 组件 | PascalCase | \`UserCard\` |

---

## 代码风格

### 格式
- 缩进：[2/4] 空格
- 行宽：[80/120] 字符
- 分号：[要/不要]
- 引号：[单引号/双引号]

### 注释
\`\`\`[语言]
/**
 * 函数说明
 * @param {类型} 参数名 - 说明
 * @returns {类型} 说明
 */
\`\`\`

---

## 提交规范

### Commit Message 格式
\`\`\`
<type>(<scope>): <description>

[optional body]

[optional footer]
\`\`\`

**Type 列表：**
| Type | 用途 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档变更 |
| style | 代码格式 |
| refactor | 重构 |
| test | 测试 |
| chore | 构建/工具 |

---

## 分支策略

| 分支 | 用途 | 命名 |
|------|------|------|
| main | 生产代码 | \`main\` |
| develop | 开发集成 | \`develop\` |
| feature | 功能开发 | \`feature/xxx\` |
| fix | Bug 修复 | \`fix/xxx\` |
| release | 发布准备 | \`release/vX.Y.Z\` |

---

## 代码审查要求

- 所有变更必须经过 PR
- 至少 1 人 Approve
- CI 必须通过
- 无冲突

---

## 禁止事项

🛑 不要提交密钥/密码到代码库
🛑 不要直接 push 到 main
🛑 不要忽略编译警告
🛑 不要提交未测试的代码

---
*模板版本：1.0.0*
