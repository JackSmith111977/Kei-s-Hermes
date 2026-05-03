# Skill-manage 联动拦截指南

## 目标
确保所有 `skill_manage` 调用都经过 skill-creator 的检查流程，防止绕过流程的违规操作。

## 拦截机制

### 1. 调用前强制检查清单
在调用 `skill_manage` 前，必须按顺序执行：

```python
# ✅ 正确流程
1. skill_view(name='skill-creator')          # 加载 skill-creator
2. 执行依赖扫描 (dependency-scan.py)         # 检查引用链
3. 通过质量检查清单 (Quality Checklist)      # 确认符合标准
4. skill_manage(action='xxx', ...)           # 执行操作

# ❌ 错误流程（违规）
skill_manage(action='create', ...)           # 直接调用，未经检查
```

### 2. 操作类型与检查要求

| 操作类型 | 前置检查 | 额外要求 |
|:---|:---|:---|
| `create` | 完整 9 阶段流程 | 必须定义 triggers 和 evals |
| `patch` | 依赖扫描 + 影响范围评估 | 若修改 triggers 需通知引用者 |
| `edit` | 依赖扫描 + 版本升级检查 | 必须更新 version 字段 |
| `delete` | 依赖扫描 + 引用链检查 | 若有引用者需先更新它们 |
| `write_file` | 目录结构检查 | 文件必须在 references/scripts/checklists 下 |

### 3. 依赖断裂处理流程

当检测到依赖断裂时：
```
[发现断裂]
   ↓
[步骤 1] 列出所有受影响的 Skill
   ↓
[步骤 2] 评估影响范围（高/中/低）
   ↓
[步骤 3] 生成修复建议
   ↓
[步骤 4] 用户确认后执行修复
   ↓
[步骤 5] 更新依赖图谱
```

## 实际示例

### 示例 1: 安全地修改 pdf-layout
```
1. skill_view('skill-creator')                    # 加载检查器
2. python3 dependency-scan.py                     # 扫描依赖
   → 发现 doc-design 引用了 pdf-layout
3. 评估影响：修改字体配置不影响接口，安全
4. skill_manage(action='patch', name='pdf-layout', ...)
5. 更新 doc-design 的 references（如需）
```

### 示例 2: 危险地删除 web-access
```
1. skill_view('skill-creator')
2. python3 dependency-scan.py
   → 发现 15+ 个 Skill 依赖 web-access
3. 🚨 拦截！影响范围过高
4. 建议：标记为 deprecated，而非直接删除
5. 通知所有引用者迁移到新方案
```

## 自动化脚本

`pre-flight.sh` 脚本可集成到工作流中：
```bash
# 在执行 skill_manage 前运行
./pre-flight.sh <skill-name>
```

## 违规检测

若发现以下行为，立即停止并警告：
- 未加载 skill-creator 直接调用 skill_manage
- 跳过依赖扫描执行 delete/patch
- 修改后不更新 version 字段
- 删除被引用的 Skill 不提示
