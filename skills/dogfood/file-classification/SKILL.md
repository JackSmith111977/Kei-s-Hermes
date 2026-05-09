---
name: file-classification
description: Hermes 文件产物分类管理标准——按生命周期和语义角色分类归档
version: 1.0.0
triggers:
  - 文件分类
  - 分类管理
  - 产物分类
  - 归档标准
  - 文件类型
  - file classification
  - taxonomy
  - classify
depends_on:
  - file-system-manager
  - delete-safety
design_pattern: Library-Reference
skill_type: Reference
---

# 📂 Hermes 文件分类管理标准

## 分类原则

1. **按生命周期**：活跃（Active）→ 归档（Archive）→ 可删除（Expired）
2. **按语义角色**：原始资料(Capability) → 提炼知识(Knowledge) → 产出产物(Output)
3. **按管理策略**：持久保留 / 按龄归档 / 自动清理

---

## Hermes 产物分类体系总表

| 大类 | 子类 | 路径 | 生命周期 | 管理策略 |
|:----|:-----|:-----|:--------:|:---------|
| 🛠️ **能力** | skills | `~/.hermes/skills/` | ♾️ 永久 | 持续进化，不自动删除 |
| 📚 **知识** | learning | `~/.hermes/learning/` | 📅 提炼后归档 | 提取精华至 knowledge base 后归档 |
| 🧪 **经验** | experiences/active | `~/.hermes/experiences/active/` | 📅 活跃→归档 | 移入 archive 后按时间清理 |
| 📄 **产出** | output/pdf, images, documents | `~/.hermes/output/` | 📅 按龄 | 保留最新版本，旧版按月归档 |
| 📋 **会话** | sessions | `~/.hermes/sessions/` | ⏱️ 30天 | auto_prune 自动清理（retention=30d） |
| 🗄️ **临时** | cron/output | `~/.hermes/cron/output/` | ⏱️ 14天 | disk-cleanup 插件自动清理 |
| 🗑️ **缓存** | cache, .cache | `~/.hermes/cache/` | ⏱️ 按策略 | cache-cleanup.py 月清理 |
| 🖼️ **媒体** | image_cache, audio_cache | `~/.hermes/image_cache/` | 📅 按需 | 保留最近使用，可安全清理 |
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
| `learning/` | 学习中 | 提炼后移入 archive | 90天后可删 |
| `output/pdf/` | 6个月 | 6-12个月 | 12个月后可删 |
| `output/images/` | 3个月 | 3-6个月 | 6个月后可删 |
| `archive/` | — | 12个月 | 12个月后可删 |
| `cache/` | 即时 | — | cache-cleanup 自动清理 |
| `image_cache/` | 即时 | — | 可安全清理 |

---

## 与知识库系统的关系

文件分类管理是 Hermes 知识库系统的基础层：
- **文件系统**：$HERMES_HOME 内的原始文件存储
- **分类管理**：按标准归档、清理、整理
- **知识库**：从文件中提炼的知识（GBrain/Wiki），持久化存储和检索

三者构成完整的数据生命周期：
```
文件系统 → 分类管理（清理噪音） → 知识库（提炼精华）
              ↑                         ↓
              文件归档（保留可恢复的原始记录）
```
