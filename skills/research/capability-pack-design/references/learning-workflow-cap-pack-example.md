# learning-workflow cap-pack.yaml 参考示例

> **来源**: 2026-05-14 — SPEC-1-5 端到端测试时创建
> **关联**: 适配器验证门禁模式 (§十一)

## 能力包结构

```
packs/learning-workflow/
├── cap-pack.yaml                    ← 完整清单（含 install/depends_on）
└── SKILLS/
    └── learning-workflow/
        ├── SKILL.md                 ← 带 YAML frontmatter
        ├── scripts/                  ← 4 个 Python 脚本
        │   ├── learning-state.py
        │   ├── reflection-gate.py
        │   ├── skill_finder.py
        │   └── skill_finder_v2.py
        ├── references/              ← 7 个参考文档
        └── checklists/
```

## cap-pack.yaml 完整内容

```yaml
name: learning-workflow
version: 5.5.0
type: capability-pack
compatibility:
  agent_types: [hermes]
description: "学习/研究任务强制流程引擎"

skills:
  - id: learning-workflow
    name: 学习研究流程引擎
    description: "所有学习/研究任务的强制流程拦截器"
    version: 5.5.0
    tags: [learning, workflow, research, study, gate, loop]
    source: learning-workflow
    sqs_target: 80.0

depends_on:
  quality-assurance:
    version: ">=1.0.0"
    reason: "健康检查脚本 + 质量门禁"

install:
  scripts:
    - source: SKILLS/learning-workflow/scripts/learning-state.py
      target: ~/.hermes/skills/learning-workflow/scripts/learning-state.py
    - source: SKILLS/learning-workflow/scripts/reflection-gate.py
      target: ~/.hermes/skills/learning-workflow/scripts/reflection-gate.py
    - source: SKILLS/learning-workflow/scripts/skill_finder.py
      target: ~/.hermes/skills/learning-workflow/scripts/skill_finder.py
    - source: SKILLS/learning-workflow/scripts/skill_finder_v2.py
      target: ~/.hermes/skills/learning-workflow/scripts/skill_finder_v2.py
  references:
    - source: SKILLS/learning-workflow/references
      target: ~/.hermes/skills/learning-workflow/references/
  post_install:
    - "chmod +x ~/.hermes/skills/learning-workflow/scripts/*.py"
```

## 关键字段说明

| 字段 | 作用 | 验证门禁检查点 |
|:-----|:------|:---------------|
| `install.scripts` | 声明需要安装的脚本文件（source→target） | 脚本目标存在 + 可执行权限 |
| `install.references` | 声明需要复制的引用文档（支持目录批量） | 目标文件存在 |
| `install.post_install` | 安装后执行的 shell 命令 | 验证门禁前由 _run_post_install 执行 |
| `depends_on` | 声明对其他能力包的依赖 | 由 _check_dependencies 非阻塞检查 |
