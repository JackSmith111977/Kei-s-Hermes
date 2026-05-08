---
name: knowledge-routing
description: "Multi-dimensional knowledge routing — decide where to store new knowledge: Memory, User profile, Experience archive, or Skill. Integrated with Hermes v0.12.0 Curator, SRA, Memory capacity management, and the experiences/ system."
version: 2.0.0
triggers:
  - 经验吸收
  - 知识分类
  - 记忆管理
  - skill更新
  - knowledge routing
  - 经验沉淀
  - 总结
  - 总结经验
  - 复盘
  - 踩坑
  - 教训
  - 经验教训
  - 记下来
  - 存入Memory
  - 存入User
  - 存入经验
  - 存入Skill
  - 知识路由
  - 学到的经验
  - 沉淀经验
metadata:
  hermes:
    tags: [knowledge-management, routing, memory, skills, curator]
    category: meta
---

# 知识路由指南 v2 — Hermes v0.12.0 适配版

## 核心原则

> **不是「放哪都行」，而是「根据知识类型与复用预期，选择最优存储位置」**

基于 **PlugMem** 的知识分类（命题知识 + 程序知识）和 **Experience Compression Spectrum**（经验→技能→规则三级压缩）设计。

---

## 四维路由决策树

### 决策流程

```
遇到新经验/知识/教训 ↓
第一维：判断知识类型
├─ 命题知识（事实/偏好/环境） → 第二维 A
└─ 程序知识（流程/方法/模式） → 第二维 B

第二维 A（命题知识）：
├─ 用户相关（偏好/习惯/风格） → User 存储
├─ 环境相关（OS/工具/配置） → Memory 存储
└─ 一次性事实（某 API 报错） → Memory 存储

第二维 B（程序知识）：
├─ 复用频率 ≤ 1 次？ → Experience 存储
├─ 复用频率 2-3 次？ → 根据置信度评分
│   ├─ 置信度高 → Skill（更新已有或创建）
│   └─ 置信度低 → Experience 暂存
└─ 复用频率 > 3 次？ → Skill 存储

第三维：Hermes 环境适配
├─ Memory 容量检查（>80% → 先 consolidate）
├─ 检查 Curator 状态 → 避免创建重复 skill
├─ 参考 SRA 推荐 → 了解上下文
└─ 检查 experiences/ 中是否有类似经验

第四维：质量评分
├─ 高（8-10分）→ 立刻存入目标
├─ 中（4-7分）→ 存入 + 标记待验证
└─ 低（0-3分）→ Experience 暂存不归档
```

---

## 四个存储目标

### 1. 🧠 Memory — Agent 笔记 (目标: memory)
- **用途**：环境事实、工具特性、工作流规范、一次性教训
- **容量**：2,200 chars
- **特点**：Frozen snapshot pattern — 当前 session 立即生效，但 system prompt 下次 session 才更新
- **操作**：`memory(action="add/replace/remove", target="memory")`
- **满时处理**：先 consolidate 或 replace 合并，再添加

### 2. 👤 User — 用户画像 (目标: user)
- **用途**：用户偏好、沟通风格、习惯、个人设定
- **容量**：1,375 chars
- **特点**：跨 session 持久化，每次 session 开头注入
- **操作**：`memory(action="add/replace/remove", target="user")`

### 3. 📁 Experience — 经验档案 (目标: ~/.hermes/experiences/)
- **用途**：具体情境下的可复用发现，含完整背景
- **三个子目录**：`active/` → `skills/` → `archive/`
- **格式**：YAML frontmatter + 结构化 body
- **操作**：`write_file("~/.hermes/experiences/active/exp-{date}-{id}.md")`
- **升级路径**：reusability=high 时 → 自动更新对应 skill

### 4. ⚙️ Skill — 程序知识 (目标: ~/.hermes/skills/)
- **用途**：可复用的流程、模式、避坑指南
- **三种操作**：
  - 有相关 skill → `skill_manage(action="patch")`
  - 无相关 skill → `skill_manage(action="create")`
  - 与旧 skill 重叠 → 先检查 curator 状态再 consolidate
- **前置检查**：
  - 加载 `skill-creator`（禁止直接调用 skill_manage 跳过流程）
  - 检查 curator 是否有 stale/archived 类似 skill

---

## Hermes v0.12.0 适配清单

| Hermes 特性 | 在路由中的角色 | 操作 |
|:-----------|:-------------|:-----|
| **Curator** | 避免重复创建 | 创建 skill 前用 `skills_list` 检查已有 skill，避免与 stale 重复 |
| **SRA** | 上下文感知 | 参考 SRA 推荐的 skill 决定路由方向 |
| **Memory (2200 chars)** | 容量管理 | >80% 时先 consolidate 再添加 |
| **Skills Hub** | 安装已有 skill | 如需新功能，先搜索 hub 有无现成 skill |
| **Personalities** | 沟通风格 | 根据 personality 调整通知语气 |
| **条件激活** | token 优化 | 利用 `fallback_for_toolsets` 减少冗余加载 |
| **experiences/** | 经验暂存 | 复用频率低/置信度低 → 先存 experience |

---

## 质量评分标准

| 分数 | 等级 | 标准 | 路由动作 |
|:---:|:----:|:----|:---------|
| 8-10 | 🟢 高 | 已验证 ≥2 次，有交叉验证，可复用性强 | 立即存入目标 |
| 4-7 | 🟡 中 | 已验证 1 次，需要进一步验证 | 存入 + 标记"待验证" |
| 0-3 | 🔴 低 | 未验证 / 仅单次观察 / 可能过时 | Experience 暂存 / 丢弃 |

---

## 执行清单

遇到新知识时，按顺序执行：

- [ ] 1. 判断知识类型（命题 vs 程序）
- [ ] 2. 判断复用频率（1次 vs 2-3次 vs 3次+）
- [ ] 3. 检查 Memory 容量（>80% 则先 consolidate）
- [ ] 4. 如需创建 Skill → 先检查 curator 状态
- [ ] 5. 质量评分（0-10）
- [ ] 6. 选择存储目标并执行
- [ ] 7. 更新 experiences/index.md（如存经验）
- [ ] 8. 通知用户存储结果

---

## 评估用例 (Eval Cases)

### Eval-001 (事实 → Memory)
- **输入**: "GitHub API 现在需要新的 Token 格式了"
- **预期**: 命题知识，一次性事实 → Memory 存储
- **检查**: 不使用 skill_manage

### Eval-002 (流程 → Skill)
- **输入**: "每次部署前都要先扫描敏感文件，步骤是 1...2...3..."
- **预期**: 程序知识，复用 >3 次 → Skill 更新/创建
- **检查**: 先加载 skill-creator

### Eval-003 (用户偏好 → User)
- **输入**: "karp 的 Hermes 系统默认使用 kawaii 人格"
- **预期**: 用户偏好 → User 存储
- **检查**: `memory(target="user")`

### Eval-004 (情境经验 → Experience)
- **输入**: "今天用 CDP 浏览器访问 GitHub 时发现，直接访问比 web_extract 获取的信息更完整"
- **预期**: 情境经验，需验证 → Experience 暂存
- **检查**: 写入 experiences/active/ 并更新 index

### Eval-005 (Skill 重复检测 → Curator 感知)
- **输入**: "学习一下知识路由的最佳实践，创建一个新 skill"
- **预期**: 先 skills_list 检查已有类似 skill
- **检查**: 不直接 create，先检查 curator

### Eval-006 (Memory 满 → Consolidate)
- **输入**: "再记一条：今天发现 Hermes 的 curator 在 30 天后将技能标记为 stale"
- **预期**: 检查容量，如 >80% 先 consolidate
- **检查**: 先 consolidate 再添加

---

## Red Flags

- ❌ **二进制思维**：知识不只 Memory 或 Skill — 还有 User 和 Experience 两个目标
- ❌ **跳过容量检查**：Memory 只有 2200 chars，写入前必须先检查
- ❌ **绕过 skill-creator**：创建/更新 Skill 必须加载 skill-creator
- ❌ **忽略 curator**：创建 skill 前不检查 curator 状态 → 可能创建重复 skill
- ❌ **长流程塞进 Memory**：操作 SOP 存 Memory → 耗尽容量且难以复用 → 必须走 Skill
- ❌ **琐碎事实写进 Skill**：一次性事件 → 建 Skill 造成库臃肿 → 走 Memory/Experience
