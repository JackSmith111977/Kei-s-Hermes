# 治理驱动修复策略 — 扫描→修复闭环设计

> **背景**: EPIC-005 治理引擎可对能力包执行 L0-L4 合规扫描，但「发现问题→自动修复」的闭环尚未建立。
> **本文件**: 分析各条扫描规则的修复方式，指导 `skill-governance fix` 命令的设计。
> **来源**: 2026-05-16 EPIC-005 Phase 3 完成后的跨包扫描实验（5 包均 non_compliant，平均分 79.6）

---

## 一、规则可修复性分类

基于对实际扫描结果的逐条分析（doc-engine 包为例），33 条规则可分为三类：

### 🟢 确定性修复（可纯脚本自动化）

| 规则 | 问题 | 修复动作 | 信任度 | 18 包影响 | 
|:-----|:-----|:---------|:------:|:---------:|
| F001 | 缺失 SKILL.md | 从 skill 文件元数据生成模板 SKILL.md | **100%** | 极高 |
| F007 | 缺失 triggers | 从 tags/title 提取或自动推断 | **90%** | 极高 |
| H001 | 树簇未归属 | Jaccard tag 匹配最佳簇 | **85%** | 高 |
| H002 | 簇大小异常 | 推荐合并到相邻大簇（Jaccard 最相似） | **95%** | 中 |

**实现策略**: 固定模板/规则 → 无需 LLM，直接执行。

**F001 SKILL.md 骨架模板**:
```markdown
# {skill_name}

> **id**: `{skill_id}`
> **description**: {auto_inferred_from_dir}
> **tags**: [{tags_from_parent}]
> **version**: "0.1.0"
> **classification**: toolset

---

## Overview

{one-line description}

## Usage

{tbd}
```

### 🟡 半自动修复（需启发式/上下文）

| 规则 | 问题 | 修复动作 | 信任度 | 难点 |
|:-----|:-----|:---------|:------:|:-----|
| F006 | 无效 classification | 从包类型/内容推断 | 60-70% | 分类边界模糊 |
| E001 | SRA 发现性不足 | 补充 triggers + description | 70% | 需理解 skill 用途 |
| E002 | 跨平台兼容缺失 | 补充 agent_type 声明 | 70% | 需推断所属平台 |

**实现策略**: 启发式规则 + LLM 兜底。

**F006 启发式推断逻辑**:
```python
def infer_classification(pack_name: str, skill_name: str, tags: list[str]) -> str:
    """基于包名和标签推断 classification"""
    domain_keywords = ["learning", "design", "social", "financial", "media", "game", "network"]
    toolset_keywords = ["tool", "cli", "sdk", "api", "plugin", "adapter"]
    infra_keywords = ["quality", "system", "ops", "monitor", "health", "audit"]
    
    all_text = f"{pack_name} {skill_name} {' '.join(tags)}".lower()
    
    for kw in domain_keywords:
        if kw in all_text:
            return "domain"
    for kw in toolset_keywords:
        if kw in all_text:
            return "toolset"
    for kw in infra_keywords:
        if kw in all_text:
            return "infrastructure"
    return "toolset"  # 兜底
```

### 🔴 需要外部验证的修复

| 规则 | 问题 | 修复动作 | 信任度 | 难点 |
|:-----|:-----|:---------|:------:|:-----|
| E005 | 断裂链接 | 验证 URL 并替换/移除 | 30% | 需网络访问 |

**实现策略**: LLM 辅助 + 人工确认兜底。

---

## 二、混合修复架构

### 两阶段执行流

```
skill-governance scan <pack>              # 第一阶段: 检测
    → 输出 JSON (含全部违规 + 建议)
    
skill-governance fix <pack> [--rules F001,F007] [--dry-run]  # 第二阶段: 修复
    └─ Phase 1: 确定性修复 (纯脚本)
    │      rules: F001, F007, H001, H002
    │      动作: 生成文件/修改 YAML
    │      速度: < 5s/pack
    │      验证: 文件存在 + yaml 合法
    │
    └─ Phase 2: 语义修复 (LLM 辅助)
           rules: F006, E001, E002, E005
           动作: 推断分类/生成描述/更新元数据
           速度: ~30s/pack (LLM 调用)
           验证: 再扫描确认通过
```

### 安全机制

```text
fix --dry-run  → 输出 diff，不实际写入
fix --apply    → 执行修改（非交互式，需主人先确认 diff）
fix --apply --interactive → 逐条确认修改

回滚: 每次 fix --apply 前自动 git stash 或备份文件
```

### CLI 设计

```bash
# 使用
skill-governance fix packs/doc-engine/ --dry-run --rules F001,F007
skill-governance fix packs/doc-engine/ --apply --rules F001
skill-governance fix packs/doc-engine/ --apply --all    # 全部规则

# 输出
📋 Fix Plan for packs/doc-engine/ (dry-run)
─────────────────────────────────────────
  F001: CREATE SKILLS/pdf-layout/SKILL.md         [确定]
  F001: CREATE SKILLS/pdf-pro-design/SKILL.md     [确定]
  F007: PATCH SKILLS/pdf-layout/SKILL.md +triggers [确定]
  F006: PATCH SKILLS/pdf-layout/SKILL.md → classification=toolset [推测]
  ─────────────────────────────────
  4 changes: 3 deterministic + 1 heuristic
  → Use --apply to apply | OK?
```

---

## 三、与 CapPackAdapter 的集成

现有 `CapPackAdapter`（`adapter/cap_pack_adapter.py`）已有 `scan/suggest/dry_run/apply` 四步流程。`fix` 命令复用此架构：

```python
class CapPackFixEngine:
    """治理修复引擎 — 组合确定性规则 + 可选 LLM 辅助"""
    
    def __init__(self, llm_assist: bool = False):
        self.llm_assist = llm_assist
        self.adapter = CapPackAdapter()
        self._deterministic_fixers = {
            "F001": self._fix_f001_missing_skill_md,
            "F007": self._fix_f007_missing_triggers,
            "H001": self._fix_h001_cluster_membership,
            "H002": self._fix_h002_cluster_size,
        }
        self._heuristic_fixers = {
            "F006": self._fix_f006_classification,
        }
    
    def fix(self, pack_path: str, rules: list[str] | None = None, 
            dry_run: bool = True) -> FixResult:
        """执行修复计划"""
        # 1. 先扫描获取当前状态
        scan_result = self.adapter.scan(pack_path)
        
        # 2. 匹配修复器
        plan = []
        for rule_id, fixer in self._deterministic_fixers.items():
            if rules and rule_id not in rules:
                continue
            if self._is_rule_failing(scan_result, rule_id):
                plan.append(fixer(pack_path, dry_run))
        
        # 3. 执行或预览
        return FixResult(plan=plan, dry_run=dry_run)
```

---

## 四、批量修复策略

18 个能力包全部 `non_compliant`，批量修复时应按优先级分批：

```text
Phase A: F001 + F007 (所有包)        → 脚本秒级修复，100% 安全
Phase B: H001 + H002 (簇相关包)      → Jaccard 算法修复，95% 置信
Phase C: F006 (语义推断)              → 启发式 + 抽样人工确认
Phase D: E001 + E002 + E005 (生态)   → LLM 辅助，逐包处理
```

每 Phase 完成后 `skill-governance scan` 验证分数提升。

---

## 五、相关参考

| 资源 | 路径 |
|:-----|:------|
| EPIC-005 治理引擎完整文档 | `docs/EPIC-005-skill-governance-engine.md` |
| CapPackAdapter 实现 | `packages/skill-governance/skill_governance/adapter/cap_pack_adapter.py` |
| 跨包扫描实验结果 | 2026-05-16 会话存档（5 包平均 79.6） |
| 规则 YAML 定义 | `standards/rules.yaml`（33 条规则，5 层） |

---

## 六、代码库分析五步法（实战数据）

> **来源**: 2026-05-16 EPIC-006 深度代码分析  
> **适用**: 任何「基于现有扫描结果构建修复引擎」的设计前分析

### Step 1: 扫描器分析

| 检查项 | 发现 |
|:-------|:------|
| 扫描结果格式 | `ScanReport.to_dict()` → dict，5 layers × checks[] |
| 入口函数 | `_build_report()` in cli/main.py:83（240行） |
| 修复需从哪获取数据 | `CheckResult.details` + `suggestions`（models/result.py） |

### Step 2: 适配器分析

| 可复用函数 | 位置 | 行数 | 用途 |
|:----------|:-----|:----:|:-----|
| `_parse_frontmatter()` | adapter/cap_pack_adapter.py:160 | 18 | SKILL.md frontmatter 解析 |
| `_jaccard_similarity()` | adapter/cap_pack_adapter.py:105 | 20 | Tag 匹配算法 |
| `PackManifest.from_file()` | adapter/cap_pack_adapter.py:46 | 32 | YAML 包定义读取 |

**关键洞见**: 适配器是做「安装」的，修复引擎需要做「编辑」。两者相似但不同——复用数据提取和写入模式，但逻辑不同。

### Step 3: 已有修复脚本分析

| 脚本 | 行数 | 可复用模式 |
|:-----|:----:|:----------|
| `fix-pack-metadata.py` | 180 | YAML RMW + 幂等性检查 + 包遍历 |
| `fix-low-score-skills.py` | 130 | Frontmatter 正则注入 `^(---\\n)(.*?)(\\n---\\n)` |
| `fix-l2-frontmatter.py` | 71 | 启发式类型检测（关键词→分类） |

### Step 4: CLI 分析

| 问题 | 答案 |
|:-----|:------|
| 命令注册方式 | `@app.command()` Typer |
| 复用函数 | `_load_skills_from_pack()` + `_build_report()` |
| fix 放哪 | `cli/main.py` 新增 `@app.command("fix")` |

### Step 5: 依赖与测试分析

| 问题 | 答案 |
|:-----|:------|
| 新增 pip 依赖 | **零** |
| 测试 fixture 模式 | `tmp_path` + `monkeypatch` |
| 测试位置 | `packages/skill-governance/tests/` |
| fixture 模板 | 创建模拟 cap-pack.yaml + 1-2 个 SKILL/ 目录 |
