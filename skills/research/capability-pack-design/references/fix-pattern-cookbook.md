# Fix Pattern Cookbook — 修复引擎通用模式速查

> **用途**: 实现任何 FixRule 时直接复用的代码片段和模式。
> **来源**: EPIC-006 深度代码库分析 (2026-05-16)

---

## 模式 1: YAML 读/修改/写 (YAML RMW)

```python
import yaml
from pathlib import Path

def fix_yaml_field(yaml_path: str, field: str, value) -> bool:
    """修改 YAML 文件的某个字段，幂等"""
    path = Path(yaml_path)
    data = yaml.safe_load(path.read_text())
    
    # 幂等性检查
    if data.get(field) == value:
        return False  # 无需修改
    
    data[field] = value
    new_yaml = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(new_yaml)
    return True  # 已修改
```

**来源**: `scripts/fix-pack-metadata.py:108-146`

---

## 模式 2: Frontmatter 正则注入

```python
import re
import yaml

FRONTMATTER_RE = re.compile(r'^(---\n)(.*?)(\n---\n)(.*)', re.DOTALL)

def inject_frontmatter_field(content: str, field: str, value) -> str:
    """在现有 frontmatter 中注入字段，保留其他字段"""
    match = FRONTMATTER_RE.match(content)
    if not match:
        return content
    
    frontmatter_text = match.group(2)
    try:
        fm = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return content
    
    if fm is None:
        fm = {}
    
    # 幂等性
    if fm.get(field) == value:
        return content
    
    fm[field] = value
    
    new_fm = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{new_fm}---\n{match.group(4)}"
    return new_content

def validate_yaml(content: str) -> bool:
    """验证 frontmatter 的 YAML 有效性"""
    match = FRONTMATTER_RE.match(content)
    if not match:
        return False
    try:
        parsed = yaml.safe_load(match.group(2))
        return isinstance(parsed, dict)
    except yaml.YAMLError:
        return False
```

**来源**: `scripts/fix-low-score-skills.py:40-80`

---

## 模式 3: 启发式类型检测

```python
def infer_classification(name: str, description: str = "", tags: list[str] = None) -> str:
    """基于关键词推断 classification"""
    text = f"{name} {description}".lower()
    tags = [t.lower() for t in (tags or [])]
    combined = f"{text} {' '.join(tags)}"
    
    # 优先级顺序
    if any(kw in combined for kw in ['quality', 'engine', 'governance', 'audit', 'scanner']):
        return 'infrastructure'
    if any(kw in combined for kw in ['workflow', 'process', 'pipeline', 'orchestrat']):
        return 'toolset'
    if any(kw in combined for kw in ['creative', 'design', 'analysis', 'learning', 'research']):
        return 'domain'
    if any(kw in combined for kw in ['integration', 'install', 'config', 'mcp']):
        return 'infrastructure'
    
    return 'toolset'  # 默认
```

**来源**: `scripts/fix-l2-frontmatter.py:23-39`

---

## 模式 4: 备份 & 回滚

```python
import shutil
from pathlib import Path

def backup(path: str) -> str:
    """创建 .bak 备份文件"""
    src = Path(path)
    bak = src.with_suffix(src.suffix + '.bak')
    shutil.copy2(str(src), str(bak))
    return str(bak)

def restore_from_backup(bak_path: str) -> bool:
    """从 .bak 恢复"""
    bak = Path(bak_path)
    if not bak.exists():
        return False
    original = bak.with_suffix('')  # .bak → 去掉后缀
    shutil.copy2(str(bak), str(original))
    bak.unlink()
    return True
```

---

## 模式 5: 幂等性检查

```python
def is_already_fixed(check_func, *args) -> bool:
    """通用幂等性检查：如果已合规则跳过"""
    return check_func(*args)

# 使用示例
def _f001_already_fixed(pack_path: str, skill_id: str) -> bool:
    """SKILL.md 已存在 → 跳过"""
    md_path = Path(pack_path) / "SKILLS" / skill_id / "SKILL.md"
    return md_path.exists()

def _f007_already_fixed(skill_md_path: str) -> bool:
    """已有 triggers → 跳过"""
    content = Path(skill_md_path).read_text()
    match = FRONTMATTER_RE.match(content)
    if not match:
        return False
    fm = yaml.safe_load(match.group(2))
    return bool(fm and fm.get('triggers'))
```

---

## 模式 6: Unfied Diff 输出

```python
import difflib

def generate_diff(old_content: str, new_content: str, filepath: str) -> str:
    """生成 unified diff，用于 dry_run 预览"""
    return '\n'.join(difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=filepath,
        tofile=filepath
    ))
```

---

## 模式 7: 临时包创建 (测试用)

```python
import yaml
from pathlib import Path

@pytest.fixture
def temp_pack(tmp_path):
    """创建含已知问题的临时 cap-pack 包"""
    pack_dir = tmp_path / "test-pack"
    pack_dir.mkdir()
    
    # 创建 cap-pack.yaml (缺少 triggers, 部分 SKILL.md 缺失)
    manifest = {
        "name": "test-pack",
        "version": "1.0.0",
        "classification": "toolset",
        "skills": [
            {"id": "existing-skill", "name": "Existing Skill", 
             "path": "SKILLS/existing-skill/SKILL.md",
             "tags": ["test", "example"]},
            {"id": "missing-skill", "name": "Missing Skill",
             "path": "SKILLS/missing-skill/SKILL.md",
             "tags": ["new", "unwritten"]},
        ],
        "triggers": [],
    }
    with open(pack_dir / "cap-pack.yaml", "w") as f:
        yaml.dump(manifest, f)
    
    # 创建 existing-skill 的 SKILL.md
    skill_dir = pack_dir / "SKILLS" / "existing-skill"
    skill_dir.mkdir(parents=True)
    skill_md = """---
name: Existing Skill
description: A skill that exists
version: 1.0.0
tags: [test, example]
---
# Existing Skill Content
"""
    (skill_dir / "SKILL.md").write_text(skill_md)
    
    # missing-skill 没有 SKILL.md（故意）
    
    return pack_dir
```

**来源**: `scripts/tests/test_cli_commands.py:27-127`
