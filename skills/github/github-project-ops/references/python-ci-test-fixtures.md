# Python CI Test Fixture Portability

> 让 Python 测试在 CI 和本地环境都能**真正运行**，而不是空跑跳过。

## 问题

许多 Python 项目（尤其是 AI Agent 工具）的测试依赖本地环境路径（如 `~/.hermes/skills`、配置文件、数据库等）。在 GitHub Actions CI 中这些路径不存在，导致：

- `AttributeError` — 对象从未初始化
- 测试用 `if not has_skills: return` 空跑跳过
- CI 报告显示"全部通过"，实际上大部分测试什么都没验证

## 解决方案：Fixtures 代替环境依赖

### 第一步：创建 fixtures 目录

```
tests/fixtures/
└── skills/
    ├── category-a/
    │   ├── skill-1/SKILL.md
    │   └── skill-2/SKILL.md
    ├── category-b/
    │   ├── skill-3/SKILL.md
    │   └── skill-4/SKILL.md
    └── ...
```

### 第二步：测试类使用 fixtures

```python
import os

class TestAdvisor:
    SKILLS_FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "skills")

    def setup_method(self):
        self.advisor = SkillAdvisor(skills_dir=self.SKILLS_FIXTURE)
        self.advisor.refresh_index()
```

关键原则：**对象始终创建**，不要出现 `AttributeError`。

### 第三步：CI 工作流

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --tb=short -q
```

不需要额外 setup 步骤——fixtures 在 git 仓库中，clone 即用。

## Fixtures 设计原则

### 1. 覆盖多类别

- 不同 category（productivity, devops, creative, ...）
- 中英文 trigger 混合
- 有 tag 和无 tag 的 skill
- 短名称和长名称的 skill

### 2. 可预测的匹配行为

每个 fixture skill 的 trigger 应该设计为可预测的匹配结果：

```yaml
# tests/fixtures/skills/productivity/pdf-layout/SKILL.md
name: pdf-layout
triggers:
- pdf
- pdf layout
- 文档排版
```

查询"生成PDF文档" → 应匹配 pdf-layout（确信）

### 3. 数量适中

- 太少（<5）：覆盖率测试无意义
- 太多（>50）：测试变慢
- 推荐：**10-20** 个，覆盖 6-8 个类别

### 4. YAML frontmatter 格式

使用与真实 skill 相同的 YAML frontmatter 格式，确保 indexer 解析路径一致：

```yaml
---
name: skill-name
description: 一句话描述
triggers:
- trigger1
- trigger2
metadata:
  hermes:
    tags:
    - tag1
    - tag2
    category: category-name
---
# Body text
```

## 避免的反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| `if not os.path.exists(path): return` | 测试空跑 | 用 fixture 确保数据存在 |
| 硬编码 `~/.hermes/` 路径 | CI 环境不存在 | 用相对路径指向 fixtures |
| setup_method 中条件初始化 | 某些属性可能未定义 | 始终创建对象 + 用 has_* 标志位 |
| tests/ 外部的数据目录 | 克隆项目后找不到 | 放 tests/fixtures/ 内 |
