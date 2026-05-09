---
name: knowledge-precipitation
description: 三层知识库(L1 Skills/L2 Experiences/L3 Brain)的使用维护指南——知识沉淀后的索引、调用、维护流程
version: 1.3.0
triggers:
  - 知识沉淀
  - 三层知识库
  - 知识调用
  - 知识库维护
  - knowledge precipitation
  - 知识积累
  - 知识索引
  - 知识维护
  - 知识库使用
  - L1
  - L2
  - L3
  - brain
depends_on:
  - knowledge-routing
  - file-classification
  - hermes-knowledge-base
  - file-system-manager
design_pattern: Pipeline
skill_type: Workflow
---

# 📚 Hermes 三层知识库使用指南 v1.1

> **分工说明**：新知识该存到哪里→请走 `knowledge-routing`（四维路由决策树）
> 本指南只负责：知识已经存好之后，如何在三层中**检索、调用、维护**

---

## 一、三层知识库地图

```
        knowledge-routing 负责路由 ↴
新知识 → [Memory] [User] [Experience] [Skill] → 存入对应层
                                                    ↓
        本指南负责维护和使用 ↴
                                    L1 Skills     L2 Experiences    L3 Brain
                                    检索/调用      索引/维护        更新/进化
```

| 层 | 位置 | 内容类型 | 谁来维护 |
|:---|:-----|:---------|:---------|
| **L1 Skills** | `~/.hermes/skills/` | 操作级：代码、脚本、工作流 | boku 按需更新 |
| **L2 Experiences** | `~/.hermes/experiences/` | 经验级：教训、最佳实践、发现 | boku 定期归档 |
| **L3 Brain** | `~/.hermes/brain/` | 实体级：概念、实体、关系、摘要 | boku 持续进化 |

---

## 二、知识检索流程（三层协同）

当需要回答问题时，按以下优先级检索：

```
① L3 Brain → 查 index.md 定位概念/实体/摘要页面
② L2 Experiences → 查 experiences/index.md 定位相关经验
③ L1 Skills → 触发 skill triggers 加载操作指南
```

### 具体步骤

```python
def retrieve(question):
    # 1. 先读 KNOWLEDGE_INDEX.md 定位知识属于哪个主题区域
    topics = scan_knowledge_index(question)
    
    # 2. 从 L3 Brain 获取核心概念
    brain_pages = scan_brain_index(question)
    
    # 3. 从 L2 Experiences 获取经验教训
    experiences = scan_experiences(question)
    
    # 4. 触发 L1 Skills
    triggered = match_skill_triggers(question)
    
    return merge(brain_pages, experiences, triggered)
```

---

## 三、各层维护操作

### L1 Skills 维护
```bash
# 查看所有 skill
skills_list

# 加载 skill 查看内容
skill_view(name="skill-name")

# 更新 skill（发现遗漏/过时内容）
skill_manage(action="patch", name="skill-name", 
             old_string="...", new_string="...")

# 创建新 skill（需先加载 skill-creator）
skill_view(name="skill-creator")
```

### L2 Experiences 维护
```bash
# 查看所有活跃经验
ls ~/.hermes/experiences/active/

# 查看经验索引
cat ~/.hermes/experiences/index.md

# 📋 生命周期规则：
#   1. 经验 > 30 天且未引用 → 自动归档到 archive/
#   2. reusability=high 且被引用 ≥ 3 次 → 标记为"成熟经验"，可升级到 L3 Brain
#   3. 经验内容已体现在对应 skill 中 → 标记为"已吸收"，可归档

# 使用 knowledge-ingest.py 自动沉淀新经验
python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type experience --title "标题" --reusability high --confidence 4

# 归档超过 30 天无引用的经验
mv ~/.hermes/experiences/active/exp-xxx.md ~/.hermes/experiences/archive/
```

### L3 Brain 维护

**添加新知识页面（推荐使用自动工具）：**
```bash
# 使用 knowledge-ingest.py 自动创建 + 更新索引
python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type concept --name "概念名" --content "内容..."

python3 ~/.hermes/scripts/knowledge-ingest.py \
  --type entity --name "实体名" --content "内容..."
```

**手动添加：**
1. 按类型选目录：`concepts/` / `entities/` / `summaries/` / `analyses/`
2. 遵循 AGENTS.md 中的页面模板
3. 使用 `[[页面名称]]` 建立交叉引用
4. 更新 `index.md`
5. 追加 `log.md`

**📋 生命周期规则：**
- L3 页面 > 90 天未更新 → 标记为"需复审"
- 孤立页面（无任何其他页面引用）→ 检查是否需要归档
- 死链（引用不存在的页面）→ 修复或移除

**健康检查（每周 lint）：**
```bash
# 检查孤立页面（没有被其他页面引用的）
grep -r "\[\[" ~/.hermes/brain/wiki/ | grep -o '\[\[[^]]*\]\]' | sort -u

# 检查死链（引用不存在的页面）
# 对比所有 [[引用]] 和实际文件列表

# 检查超过 30 天未更新的页面
find ~/.hermes/brain/wiki -name "*.md" -mtime +30
```

---

## 四、知识流动路径

```
学习/对话 → 新知识产生
    ↓
knowledge-routing 决策 ↴
    ├─ 存 Memory → 临时性事实
    ├─ 存 User → 用户偏好
    ├─ 存 Experience → 未验证/低频经验 → (验证后) → 提炼到 L3 Brain
    └─ 存 Skill → 已验证/高频技能
                          ↓
            更新 KNOWLEDGE_INDEX.md 确保可检索
```

### 跨层升级路径

```
新 Experience (L2) → 验证 reusability=high
    → 提炼核心概念写入 L3 Brain/wiki/concepts/
    → 更新 KNOWLEDGE_INDEX.md

新 Skill (L1) → 使用中积累经验
    → 经验写入 L2 Experiences
    → 核心方法论提炼到 L3 Brain
```

---

## 五、与 KNOWLEDGE_INDEX.md 的关系

`~/.hermes/KNOWLEDGE_INDEX.md` 是三层统一的检索入口，它的作用是：

1. **按主题组织**：将同一主题的 L1/L2/L3 知识关联在一起
2. **快速定位**：知道查哪层、哪个页面
3. **追踪更新**：底部有更新记录

每次沉淀知识后，检查 KNOWLEDGE_INDEX.md 是否需要更新。

---

## 六、示例场景

### 场景：主人问「Bounded Autonomy 是什么？」
1. boku 查 L3 Brain `index.md` → 找到 `concepts/bounded-autonomy.md`
2. 读取页面内容 → 理解概念
3. 查 L2 Experiences → 找到相关经验（如有）
4. 触发 L1 `learning-workflow` skill → 在上下文中提供完整回答

### 场景：主人说「记下来这个经验」
1. `knowledge-routing` 判断 → 经验级、reusability=high
2. 写入 L2 Experiences `active/exp-xxx.md`
3. 同时提炼核心概念 → 更新 L3 Brain 对应页面
4. 更新 `KNOWLEDGE_INDEX.md`
5. 回复末尾标注：`📚 知识已沉淀: L2/exp-xxx | L3/concept-name`
