---
name: file-classification
description: Hermes 文件产物分类管理标准——按生命周期和语义角色分类归档
version: 2.0.0
depends_on:
  - file-system-manager
  - delete-safety
  - file-system-manager  # 引用最新的文件系统规范
design_pattern: Library-Reference
skill_type: Reference
---

# 📂 Hermes 文件分类管理标准

> ⚠️ **此 skill 是高层分类概览，完整规范请参考权威来源**：
> `~/.hermes/standards/filesystem-规范.md`（v1.0，2026-05-17）

## 分类原则

1. **按生命周期**：活跃（Active）→ 归档（Archive）→ 可删除（Expired）
2. **按语义角色**：原始资料(Capability) → 提炼知识(Knowledge) → 产出产物(Output)
3. **按管理策略**：持久保留 / 按龄归档 / 自动清理

---

## Hermes 产物分类体系总表

| 大类 | 子类 | 路径 | 生命周期 | 管理策略 |
|:----|:-----|:-----|:--------:|:---------|
| 🛠️ **能力** | skills | `~/.hermes/skills/` | ♾️ 永久 | 持续进化，不自动删除 |
| 📚 **知识** | docs/learning-logs | `~/.hermes/docs/learning-logs/` | 📅 提炼后归档 | 提取精华至 knowledge base 后归档 |
| 🧪 **经验** | experiences/active | `~/.hermes/experiences/active/` | 📅 活跃→归档 | 移入 archive 后按时间清理 |
| 📄 **产出** | output/pdf, images, documents | `~/.hermes/output/` | 📅 按龄 | 保留最新版本，旧版按月归档 |
| 📋 **会话** | sessions | `~/.hermes/sessions/` | ⏱️ 30天 | auto_prune 自动清理（retention=30d） |
| 🗄️ **临时** | cron/output | `~/.hermes/cron/output/` | ⏱️ 14天 | disk-cleanup 插件自动清理 |
| 🗑️ **缓存** | cache, .cache | `~/.hermes/cache/` | ⏱️ 按策略 | cache-cleanup.py 月清理 |
| 🖼️ **媒体** | audio_cache | `~/.hermes/audio_cache/` | 📅 按需 | 保留最近使用，可安全清理 |
| 🎯 **审计** | fs-audit | `~/.hermes/data/fs-audit/` | 📅 90天 | 自动轮转，90天后可归档 |
| ✅ **规范** | standards | `~/.hermes/standards/` | ♾️ 永久 | 规范文档，不可删除 |
| 🔌 **插件** | plugins | `~/.hermes/plugins/` | ♾️ 永久 | 用户插件，持续运行 |
| ⚙️ **配置** | config, .env | `~/.hermes/config.yaml` | ♾️ 永久 | 备份后保留，不可自动删除 |
| 🔄 **运行时** | state.db, processes.json | `~/.hermes/` | ♾️ 永久 | 核心运行态，不可删除（可 prune） |
| 📦 **归档** | archive | `~/.hermes/archive/` | 📅 按时间 | 超过 90 天无访问可清理 |
| 📊 **日志** | logs | `~/.hermes/logs/` | ⏱️ 按策略 | journalctl --vacuum-time=7d |

---

## 文件产物分类流程图

```
新文件生成
    ↓
判断路径是否在 $HERMES_HOME 内？
    ├─ 否 → 不处理（外部文件不管理）
    └─ 是 → 进入分类决策
              ↓
判断文件语义角色：
    ├─ 能力类（skills/）     → 持久保留，注册到 skill 系统
    ├─ 知识类（learning/）   → 提炼精华，原始文件可选归档
    ├─ 经验类（experiences/）→ 移入 skill references/ 或归档
    ├─ 产出类（output/）     → 按类型归入子目录
    ├─ 临时类（cron-output/）→ 14天后自动删除
    ├─ 测试类（test_*）      → 会话结束时自动删除
    ├─ 会话类（sessions/）   → 30天后自动清理
    └─ 其他       → 使用 file-organize 归类
```

---

## 文件命名规范

### 推荐格式
```
{类型前缀}_{描述}_{日期}.{扩展名}
```

| 类型前缀 | 用途 | 示例 |
|:---------|:-----|:------|
| `report_` | 研究报告 | `report_rlhf_survey_20260501.md` |
| `learn_` | 学习笔记 | `learn_rag_arch_20260502.md` |
| `exp_` | 经验记录 | `exp_pdf_font_fix.md` |
| `skill_` | 技能设计 | `skill_file_classify_v1.md` |
| `tmp_` | 临时文件 | `tmp_test_output.txt` |
| `bk_` | 备份文件 | `bk_config_20260501.yaml` |

### 禁止使用的命名
- `test.txt`, `output.txt` 等无意义名称
- 特殊字符：空格、`/`、`\`、`:`、`*`、`?`、`"`、`<`、`>`
- 超过 200 字符的长文件名

---

## 各目录文件保留策略

| 目录 | 活跃期 | 归档期 | 最终处理 |
|:-----|:------:|:------:|:--------|
| `docs/learning-logs/` | 学习中 | 提炼后移入 archive | 90天后可删 |
| `output/pdf/` | 6个月 | 6-12个月 | 12个月后可删 |
| `output/images/` | 3个月 | 3-6个月 | 6个月后可删 |
| `archive/` | — | 12个月 | 12个月后可删 |
| `cache/` | 即时 | — | cache-cleanup 自动清理 |
| `audio_cache/` | 即时 | — | 可安全清理 |

---

## 与知识库和规范的关系

文件分类管理是 Hermes 知识库系统和规范体系的基础层：

```
┌─ 规范层 ──────────────────────────────────┐
│  filesystem-规范.md   ← SSoT 权威来源        │
│  (命名/目录归属/生命周期/门禁)              │
├─ 分类层 ──────────────────────────────────┤
│  本 skill (file-classification)            │
│  高层概览，快速查阅                        │
├─ 执行层 ──────────────────────────────────┤
│  file-system-manager skill                 │
│  清理/整理/健康检查脚本                    │
│  → 未来将接入 hooks 自动执行               │
└────────────────────────────────────────────┘
```

### 关键规范引用

| 规范章节 | 与本 skill 的关系 |
|:---------|:-----------------|
| 第4章 文件类型与生命周期 | **保留策略速查表**——细化每个目录的活跃/归档/删除期 |
| 第5章 命名规范 | 文件命名规则——与分类前缀联动 |
| 第8章 写删门禁 | 分类后如何安全删除——按类别分级门禁 |
| 第10章 归档与清理 | 归档流程和清理门禁 |
| 第6章 Skill 结构 | Skill 内产物的分类——中间产物内部消化规则 |
