# Hermes Skill → Cap-Pack 自动转换器设计

> **来源**: 2026-05-16 深度代码库分析 — `~/Hermes-Cap-Pack`
> **背景**: 治理引擎（EPIC-005/006）能扫描和修复 cap-pack，但 **不能从 Hermes 原生 skill 目录自动创建 cap-pack**。

## 现状分析

### 已有能力（但碎片化）

| 组件 | 文件 | 能力 | 限制 |
|:-----|:------|:-----|:------|
| `extract-pack.py` | `scripts/extract-pack.py` | 单个 skill 提取（文件复制） | 不能从零生成 cap-pack.yaml，只能更新已有 |
| `CapPackAdapter` | `skill_governance/adapter/cap_pack_adapter.py` | `suggest()` 推荐匹配包，`apply()` 更新 manifest | `apply()` **不复制**文件和目录 |
| `find_skill_dir()` | `extract-pack.py:27-46` | Hermes skill 目录查找 | 模糊匹配 |
| `_parse_frontmatter()` | `cap_pack_adapter.py:160-178` | SKILL.md frontmatter 解析 | 可提取到共用模块 |

### 核心差距

```
Hermes 原生 skill 格式                     Cap-Pack 格式
~/.hermes/skills/<name>/               packs/<pack>/SKILLS/<name>/
├── SKILL.md                    ─────►  ├── SKILL.md
├── references/                 ─────►  ├── references/
├── scripts/                    ─────►  ├── scripts/
├── templates/                  ─────►  ├── templates/
└── checklists/                 ─────►  └── checklists/
                                        ├── cap-pack.yaml  ← 需自动生成
                                        ├── EXPERIENCES/   ← 需自动聚合
                                        └── KNOWLEDGE/     ← 需自动聚合
```

| # | 差距 | 现状 | 难度 |
|:-:|:------|:----:|:----:|
| 1 | 从零生成 `cap-pack.yaml` | ❌ 只更新已有 manifest | 低 |
| 2 | 批量提取所有 ~/.hermes/skills/ | ❌ 只能逐个 | 低 |
| 3 | 智能分组（多 skill → 一个 pack） | 🔶 `suggest()` 可推荐但不会自动执行 | 中 |
| 4 | 生成 EXPERIENCES/ 目录 | ❌ | 低 |
| 5 | 生成 KNOWLEDGE/ 目录 | ❌ | 低 |
| 6 | 聚合 pack 级元数据 | ❌ | 中 |
| 7 | CLI `extract` 子命令 | ❌ 只有 scan/fix/watcher/rules | 低 |

## 最小可行方案

### 新增模块: `skill_governance/converter/`

| 文件 | 用途 | 预计行数 |
|:-----|:------|:--------:|
| `converter/extractor.py` | 核心提取逻辑（文件解析+复制+manifest 生成） | ~300 |
| `converter/manifest_builder.py` | cap-pack.yaml 生成器（从 SKILL.md frontmatter 构造） | ~200 |
| `converter/grouping.py` | 智能分组引擎（按 tag/domain/classification 聚类） | ~150 |
| CLI 集成到 `cli/main.py` | `skill-governance extract` 命令 | ~80 |
| 测试 | | ~200 |
| **总计** | | **~930** |

### 核心逻辑

```python
class SkillExtractor:
    """从 ~/.hermes/skills/ 提取技能到 cap-pack 格式"""

    def extract_one(self, skill_name: str, pack_dir: Path,
                    create_manifest: bool = True) -> bool
    def extract_all(self, dest_root: Path) -> dict[str, list[str]]
    def extract_to_pack(self, skill_names: list[str],
                        pack_name: str, dest_root: Path) -> bool
```

**extract_one() 流程**: 路径解析 → 解析 SKILL.md frontmatter → 创建 SKILLS/ 目录 → 复制所有文件 → 生成或更新 cap-pack.yaml → 聚合 pack 级 metadata

### 可复用资产

| 资产 | 来源 | 用途 |
|:-----|:------|:------|
| `_parse_frontmatter()` | `cap_pack_adapter.py:160-178` | 解析 SKILL.md YAML frontmatter |
| `PackManifest.from_file()` | `cap_pack_adapter.py:46-78` | 解析已有 manifest |
| `CapPackAdapter.suggest()` | `cap_pack_adapter.py:427-491` | 自动匹配合适的 pack |
| `find_skill_dir()` | `extract-pack.py:27-46` | Hermes skill 目录查找 |
| `list_skill_files()` | `extract-pack.py:66-78` | 文件清单提取 |
| `PackParser` | `scripts/uca/parser.py` | cap-pack.yaml 解析 |
| `cap-pack-v3.schema.json` | `schemas/cap-pack-v3.schema.json` | 生成结果格式验证 |
| `validate-pack.py` | `scripts/validate-pack.py` | 提取后完整性验证 |

### CLI 使用示例

```bash
# 提取单个 skill 到新包
skill-governance extract pdf-layout --pack doc-engine

# 批量提取所有 skill，自动分组
skill-governance extract --all --auto-group

# 提取到已有包（suggest + 确认）
skill-governance extract pdf-layout --auto

# 预览模式
skill-governance extract pdf-layout --dry-run
```

### 处理流程

```text
~/.hermes/skills/                           packs/<pack-name>/
├── skill-a/                  ──►            ├── cap-pack.yaml (自动生成)
│   ├── SKILL.md                             ├── SKILLS/
│   ├── references/                          │   ├── skill-a/
│   └── scripts/                             │   │   ├── SKILL.md
├── skill-b/                  ──►            │   │   ├── references/
│   ├── SKILL.md                             │   │   └── scripts/
│   ├── templates/                           │   └── skill-b/
│   └── checklists/                          │       ├── SKILL.md
│                                            │       ├── templates/
│                                            │       └── checklists/
│                                            ├── EXPERIENCES/ (自动聚合)
│                                            └── KNOWLEDGE/ (自动聚合)
```

## 实现路径

### Phase 1 — 基础设施（底层能力）

| 步骤 | 内容 | 预估 |
|:-----|:------|:----:|
| 1 | 创建 `converter/` 包结构 | 10 min |
| 2 | 实现 `extractor.py` 核心提取 | 90 min |
| 3 | 实现 `manifest_builder.py` 从 SKILL.md 生成 cap-pack.yaml | 45 min |
| 4 | 单元测试 | 45 min |

### Phase 2 — 批量与智能

| 步骤 | 内容 | 预估 |
|:-----|:------|:----:|
| 5 | CLI 集成 + extract 命令 | 30 min |
| 6 | 批量模式 `--all` | 30 min |
| 7 | 智能分组 `--auto-group` | 60 min |
| 8 | EXPERIENCES/KNOWLEDGE 聚合 | 45 min |
| 9 | 集成测试 | 30 min |

### Phase 3 — 端到端闭环

| 步骤 | 内容 | 预估 |
|:-----|:------|:----:|
| 10 | 与 scan/fix/watcher 工作流集成 | 30 min |
| 11 | 提取后自动验证（调用 validate） | 15 min |
| 12 | 文档对齐（auto-update project-report） | 30 min |

## 陷阱

| 陷阱 | 后果 | 预防 |
|:-----|:------|:------|
| 生成 cap-pack.yaml 时缺少 type/compatibility 字段 | schema 验证失败 | 用 `cap-pack-v3.schema.json` 作为输出模板，确保必填字段全部生成 |
| 文件名编码问题 | skill 名含中文/特殊符号 → 路径错误 | 仅支持 `[a-z0-9-]` skill 名，不符的映射为 kebab-case |
| 已有 manifest 合并时 skill 去重 | 重复添加同一 skill | 合并前检查 skill name/id 是否已存在 |

## 相关资源

| 资源 | 路径 |
|:-----|:------|
| `extract-pack.py` | `~/Hermes-Cap-Pack/scripts/extract-pack.py` |
| `cap_pack_adapter.py` | `~/Hermes-Cap-Pack/packages/skill-governance/skill_governance/adapter/cap_pack_adapter.py` |
| cli/main.py | `~/Hermes-Cap-Pack/packages/skill-governance/skill_governance/cli/main.py` |
| capability-pack-design SKILL.md | §四-B 提取 SOP（手动流程） |
| cap-pack-v3.schema.json | `~/Hermes-Cap-Pack/schemas/cap-pack-v3.schema.json` |
