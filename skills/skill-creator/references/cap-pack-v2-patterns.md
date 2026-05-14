# 🏗️ Capability Pack v2 设计模式参考

> 来源: skill-quality-cap-pack 设计实战 (2026-05-14)
> Schema: `project/hermes-cap-pack/schemas/cap-pack-v2.schema.json`

## v2 新增核心字段

| 字段 | 类型 | 用途 |
|:-----|:-----|:------|
| `classification` | enum: domain/toolset/skill/infrastructure | 包分类。新增 `infrastructure` 用于系统级包 |
| `compatibility.hermes_version` | {min, max} string | Hermes 版本兼容范围声明 |
| `integration` | object | 纯外部集成核心——声明脚本/门禁/审计/行为约束 |
| `verification` | object | 健康检查脚本 + SQS 目标 + 签名校验 |
| `lifecycle` | object | 三阶段管理：install/update/uninstall |
| `config_schema` | object | 包配置值的类型声明 |

## integration 段设计模式

### locate（环境检测）
```yaml
integration:
  locate:
    script: scripts/hermes-locate.py
    required: true
    auto_detect:
      targets: [hermes_home, source_type, version, tools, skills_dirs, profiles]
```
- 所有下游脚本依赖 locate 的输出
- 跨系统自动检测：支持 git_clone/pip_package/system/unknown

### monitors（文件监控）
```yaml
monitors:
  - id: skill-file-watchdog
    trigger: cron
    schedule: "*/15 * * * *"
    alert_on: change
```
- 推荐使用 cron 触发而非 inotify（更简单、跨平台）

### gates（质量门禁）
```yaml
gates:
  - id: pre-flight-enhancer
    hook_point: pre_flight
    blocking: false
    timeout_seconds: 10
```
- hook_point 映射到 skill-creator 的检查点
- blocking: true 表示 exit code 1 阻断流程

### audits（定期审计）
```yaml
audits:
  - id: daily-quality-audit
    schedule: "0 7 * * *"
    output_format: feishu_card
    deliver_to: feishu
```
- 复用已有的 SQS + 依赖扫描脚本

### behaviors（行为约束）
```yaml
behaviors:
  - id: subagent-skill-guard
    enforcement: self_discipline
    rule: "在 delegate_task context 中注入 skill 操作约束..."
```
- 纯外部方案的核心：不碰核心代码，靠行为规则约束
- enforcement 枚举: self_discipline / skill_rule / pre_flight_script / memory

## 生命周期三阶段

```
install:   pre_install → install → post_install → verify
update:    pre_update → update → post_update → migrate
uninstall: pre_uninstall → uninstall → rollback
```

每个阶段支持三种 hook 类型:
- shell — 执行 shell 命令（注册 cron、创建目录）
- python — 内联 Python 代码（环境检测、配置校验）
- notify — 发送通知（用户提示）

## 纯外部 vs 补丁方案对比

| 维度 | 补丁方案（改核心） | 纯外部方案（推荐） |
|:-----|:-----------------:|:------------------:|
| 核心代码修改 | 40+ 行 | 0 行 |
| Hermes 升级影响 | 需重新合并补丁 | 不受影响 |
| 覆盖率 | 100% | 90%（审计兜底） |
| 实现成本 | 3-5 人天 | 5-8 人天 |
| 可移植性 | Hermes 专属 | 可适配多个 Agent |

## Schema 迁移注意事项

v1 → v2 迁移需补充字段:
- classification: 根据包内容选择 domain/toolset/skill/infrastructure
- display_name: 人类可读的包名（60 字以内）
- compatibility.agent_types: 扩展了 opencode、copilot 等
- 日期字段必须加引号（"2026-05-14"），否则 YAML 解析为 datetime.date

当前所有 pack 已通过 v2 schema 验证（2026-05-14）。
