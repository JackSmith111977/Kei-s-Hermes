# Skill Governance Engine — Cap-Pack 集成模式

> **背景**: EPIC-005 技能治理引擎 (2026-05-16) 设计决策记录
> **关系**: 治理引擎是 cap-pack 项目质量闭环的自动化环节

## 一、治理引擎在 Cap-Pack 生态中的位置

```
Skill 创建 ──→ 治理引擎自动检测 ──→ 适配改造建议 ──→ 主人确认 ──→ 纳入 cap-pack
    ↑                                                              │
    └────────────────────── 迭代反馈循环 ────────────────────────────┘
```

**现有 cap-pack 流程**：
1. 手动提取 skill → 验证 schema → 手动归类 → 手动更新 cap-pack.yaml
2. 缺少自动化质量门禁和合规检查

**加入治理引擎后**：
1. 新增 skill 自动触发 → 7 维检测 → 生成适配方案（dry-run）
2. 主人确认后自动执行：归类 + 更新 cap-pack.yaml + 建立簇索引
3. 持续 watcher 保持质量基线

## 二、集成点速查

| 集成点 | 治理引擎组件 | cap-pack 组件 | 交互方式 |
|:-------|:------------|:--------------|:---------|
| Schema 验证 | Compliance Scanner | cap-pack-v2.schema.json | 读取 schema → 逐项检查 |
| SQS 评分 | Quality Tester | skill-quality-score.py | 子进程调用或 Python import |
| 树索引 | Tree Validator | skill-tree-index.py | 读取 index JSON |
| 包注册 | Auto-Adapter | cap-pack.yaml | 修改 YAML + validate |
| CI 门禁 | pre_flight gate | chi-gate.py / ac-audit.py | exit code 门禁链 |

## 三、适配引擎三层决策

```python
# 适配引擎核心逻辑
class CapPackAdapter:
    def match_pack(self, skill_meta: dict) -> str:
        """基于 skill 描述和 tags 匹配最佳 cap-pack"""
        # 1. tags 匹配 → 直接归属
        # 2. 描述语义匹配 → 推荐归属
        # 3. 无法匹配 → 标记为"新包候选"
        
    def generate_entry(self, skill, pack_name) -> dict:
        """生成 cap-pack.yaml 条目（dry-run 输出）"""
        return {
            "skills": [{
                "id": skill.name,
                "path": f"SKILLS/{skill.name}/SKILL.md",
                "version": skill.version or "1.0.0"
            }]
        }
    
    def apply(self, pack_dir, entry, dry_run=True):
        """dry-run 预览或实际执行"""
```

## 四、关键设计模式

| 模式 | 说明 | 理由 |
|:-----|:------|:------|
| **dry-run 优先** | 所有适配改造先生成预览，主人确认后执行 | 自动适配涉及文件变更，必须有保护机制 |
| **git 可回滚** | 适配前 git commit，失败可 revert | cap-pack.yaml 是项目核心文件 |
| **refererence 非入侵** | 适配只改 cap-pack.yaml + 树索引，不修改 SKILL.md | Skill 内容应由 skill-creator 管理 |
| **scores as weight** | SQS/CHI/Governance 分作为整体质量权重 | 治理引擎提供新维度但不替代现有质量指标 |

## 五、相关文档

| 文档 | 位置 |
|:-----|:------|
| EPIC-005 完整文档 | ~/projects/hermes-cap-pack/docs/EPIC-005-skill-governance-engine.md |
| 研究支撑 | ~/projects/hermes-cap-pack/docs/research/EPIC-005-skill-governance-research.md |
| cap-pack v2 schema | ~/projects/hermes-cap-pack/schemas/cap-pack-v2.schema.json |
