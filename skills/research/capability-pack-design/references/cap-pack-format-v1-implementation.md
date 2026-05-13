# Capability Pack 格式 v1 — 真实实现记录

> **来源**: 2026-05-13 会话 — hermes-cap-pack 项目 Phase 1
> **关联**: capability-pack-design 技能的方法论在这里被具体化为 YAML Schema + JSON Schema + 原型模块

## 一、产出物总览

| 产出 | 路径 | 说明 |
|:-----|:------|:------|
| 格式规范 | `schemas/cap-pack-format-v1.md` | 完整字段定义（8 大字段组） |
| JSON Schema | `schemas/cap-pack-v1.schema.json` | 可编程验证 |
| 原型模块 | `packs/doc-engine/cap-pack.yaml` | 12 技能 + 5 经验 |

## 二、格式设计的核心决策

### 2.1 字段组设计

```
顶层: name, version, type, classification, display_name, ...
compatibility: agent_types[], requires_mcp, requires_network
dependencies: cap_packs[], system_packages[], python_packages[]
skills: [{id, path, version, description, tags, experience_refs}]
experiences: [{id, path, type(pitfall|decision-tree|comparison|lesson), ...}]
mcp_servers: [{id, command|url, transport, tools}]
config_defaults: {key: value}
hooks: {on_activate[], on_deactivate[], on_update[]}
```

### 2.2 关键设计选择

| 决策 | 选项 | 选择 |
|:-----|:------|:------|
| 格式语言 | YAML vs JSON vs TOML | **YAML**（支持注释，AI 友好） |
| 分类维度 | domain vs toolset vs skill | **domain**（按领域，跨框架通用） |
| 版本号 | SemVer 2.0 | `MAJOR.MINOR.PATCH` |
| 经验类型 | 4 种 | pitfall / decision-tree / comparison / lesson |
| 钩子系统 | shell / notify / python | 安装/卸载/更新时执行 |

### 2.3 YAML 陷阱：日期解析

YAML 默认将 `2026-05-13` 解析为 `datetime.date` 对象，导致 JSON Schema 验证失败（期望 string）。**必须用引号**：
```yaml
created: '2026-05-13'  # ✅
created: 2026-05-13    # ❌ → datetime.date
```

## 三、doc-engine 原型数据

```
Skills:     12 个 (pdf-layout, pptx-guide, docx-guide, html-guide, ...)
Experiences: 5 个 (wqy-font-fallback, reportlab-cjk-encoding, ...)
Deps:        3 system + 5 python (weasyprint, reportlab, python-pptx, ...)
```

### 经验文档示例

每个经验文档包含：
- 问题描述（清晰的现象说明）
- 根因分析（为什么发生）
- 解决方案（可复制的代码/步骤）
- 验证方式（如何确认修复成功）
- 跨平台兼容策略（不同系统的差异）

## 四、未来改进方向

- **技能内容同步**：目前 SKILLS/ 下是引用文件，指向 Hermes 源 Skill。Phase 2 需要考虑何时/如何同步实际内容
- **MCP 配置扩展**：doc-engine 当前无 MCP 依赖，后续模块（如 messaging）需要完整 MCP 字段验证
- **HERMES 适配器脚本**：将能力包自动安装到 Hermes 的脚本尚未实现（Phase 1.2）

## 五、相关文件

- `~/projects/hermes-cap-pack/schemas/cap-pack-format-v1.md` — 完整格式规范
- `~/projects/hermes-cap-pack/schemas/cap-pack-v1.schema.json` — JSON Schema
- `~/projects/hermes-cap-pack/packs/doc-engine/` — 原型模块
