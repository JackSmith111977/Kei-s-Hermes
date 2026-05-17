---
name: file-system-manager
description: Hermes Agent 文件系统自主管理——归档、清理、整理、健康监控
version: 4.4.0
triggers:
  - 文件管理
  - 清理
  - 归档
  - 磁盘
  - 整理
  - 文件系统
  - 磁盘空间
  - 缓存
  - 磁盘清理
  - 文件整理
  - 文件迁移
  - 根目录文件
  - root files
  - disk
  - clean
  - organize
  - archive
  - storage
  - space
  - cache cleanup
  - disk-cleanup
  - 项目存放
  - 项目管理
  - 项目目录
  - projects
  - 独立项目
  - home目录
  - 根目录
  - home
  - root directory
  - 清理项目
  - home cleanup
  - skill-quality
  - skill健康
  - skill-health
  - SQS
  - 质量评分
  - 技能质量
  - 文件系统规范
  - 文件审计
  - fs-enforce
  - 文件系统执行
  - 规范执行
  - 文件拦截
  - 文件钩子
  - file system enforcement
  - hook
  - 审计日志
  - fs-audit
  - 文件系统健康
  - fs-health
depends_on:
  - delete-safety
  - linux-ops-guide
design_pattern: Library-Reference
skill_type: Workflow
---

# 📁 Hermes 文件系统自主管理 v2.0

> **核心理念**：分层自动管理——即时清理 + 每日/每周/每月维护，让文件系统保持整洁高效！

## 一、系统现状（当前环境）

| 项目 | 数值 |
|------|:----:|
| 磁盘容量 | 50GB |
| 已使用 | 32GB (68% — 2026-05-17) |
| cache 总占用 | ~7.5GB |
| state.db | 207MB |
| sessions | 178MB |
| 旧版本备份 | 452MB |

### 🎨 汇报呈现规范（2026-05-17 明确纠正）

> **⚠️ 飞书上终端 ASCII 图不可见！**
> 当需要在飞书向主人汇报文件系统结构时：
> 1. ✗ **不要**发截图（主人明确说「以后发我原文件而不是截图」）
> 2. ✓ 直接发送 HTML 源文件：在回复中包含 `MEDIA:/path/file.html`
> 3. ✗ **不要**用终端 `tree` / `echo` 画 ASCII 树图
> 4. ✓ 复杂结构用 `write_file` 写 HTML 可视化报告发源文件
> 5. ✓ 简单汇报用 Markdown 列表即可

## 二、诊断第一：检查自动清理是否真正生效

> ⚠️ **🚨 陷阱：插件 enabled ≠ 插件在运行！**
> 2026-05-17 实战发现：`config.yaml` 中 `plugins.enabled: [disk-cleanup]` ✅
> 但 `~/.hermes/disk-cleanup/` 目录**不存在**——状态文件从未创建，插件从未实际触发。
> 源码确认：`__init__.py` 的 `_on_post_tool_call` → `_attempt_track` → `dg.track()` 逻辑正确，
> 但需要**第一次触发**来初始化状态目录。

**每次清理前，先做三件事：**

```bash
# 1. 检查 cron job 是否启用且最近运行过
cat ~/.hermes/cron/jobs.json | python3 -c "import json,sys; j=json.load(sys.stdin); [print(f\"  {'🟢' if x.get('enabled',True) else '🔴'} {x['name']:30s} last={x.get('last_run_at','never')[:19]} state={x.get('state','?')}\") for x in j.get('jobs',[])]"
```

```bash
# 2. 检查 sessions prune 实际效果（30天阈值在密集对话下可能永远无效）
echo "sessions < 30天: $(find ~/.hermes/sessions/ -type f -mtime +30 2>/dev/null | wc -l)"
echo "sessions 总数: $(find ~/.hermes/sessions/ -type f 2>/dev/null | wc -l)"
```

```bash
# 3. 检查 disk-cleanup 是否在运行
ls -la ~/.hermes/disk-cleanup/tracked.json 2>/dev/null && echo "🟢 有跟踪文件" || echo "🔴 无跟踪文件（可能未启用）"
```

## 三、已启用的自动机制

### ✅ disk-cleanup 插件（v2.0.0 — 已启用）
自动追踪 `write_file`/`terminal`/`patch` 创建的临时文件，会话结束时自动清理。

**清理规则**：

| 分类 | 阈值 | 确认方式 |
|------|:----:|:--------:|
| test 文件 | 每次会话结束 | 自动 |
| temp 文件 | >7天 | 自动 |
| cron-output | >14天 | 自动 |
| 空目录 | 总是 | 自动 |
| research | >30天（保留最新10个） | deep模式确认 |
| >500MB 文件 | 永不自动 | deep模式确认 |

**Slash 命令**：
- `/disk-cleanup status` — 查看状态
- `/disk-cleanup quick` — 快速清理
- `/disk-cleanup deep` — 深度清理
- `/disk-cleanup dry-run` — 预览

### ✅ Sessions 管理

**核心问题**：`state.db` 中的 `sessions` 表（~20MB）和 `messages` 表（~90MB + FTS 索引 ~270MB）是两大空间消耗源。sessions 清理不能只靠 `hermes sessions prune`，需要三步到位。

**完全清理流程（2026-05-17 实战验证）**：

```bash
# Step 1: 先改 retention 配置
# ~/.hermes/config.yaml
sessions:
  auto_prune: true
  retention_days: 7       # ⚡ 密集对话环境建议 7 天，而非 30 天
  vacuum_after_prune: true
  min_interval_hours: 24

# Step 2: 手动清理 JSON 文件（prune 不删文件！）
find ~/.hermes/sessions/ -name '*.json' -mtime +7 -delete

# Step 3: 清理 SQLite 记录
hermes sessions prune --older-than 7 --yes
```

**实战数据（2026-05-17）**：
```text
JSON 文件: 1,129 → 467  (-662)
sessions 表: 614 → 197  (-417)
messages 表: 25,471 → 8,875  (-16,596)
sessions 目录: 480MB → 270MB  (-210MB)
state.db: 464MB → 459MB  (-5MB, FTS 索引无法随 DELETE 回收)
```

**⚠️ 陷阱一：密集对话下所有 sessions < 30 天，`--older-than 30` 永远无效！**
2026-05-17 实测：1,120 个 session 文件（474MB）全部在 30 天内，prune 不删任何文件。必须降低 `retention_days` 到 7。

**⚠️ 陷阱二：hermes sessions prune 只删 SQLite 记录，不删 JSON 文件！**
源码确认（hermes_state.py:1264）：`prune_sessions()` 只标记 SQLite 中的 ended_at，不调用 `os.remove()`。
JSON 文件在 `~/.hermes/sessions/` 中永久累积（已知 bug，GitHub Issue #3015）。
Workaround：必须手动 `find ... -delete`。

## 四、安全缓存清理（一键脚本）

使用 `scripts/cache-cleanup.sh` 安全清理构建工具缓存：

```bash
# 预览模式（不删除）
python3 ~/.hermes/skills/file-system-manager/scripts/cache-cleanup.py --dry-run

# 执行清理
python3 ~/.hermes/skills/file-system-manager/scripts/cache-cleanup.py --apply
```

**可安全清理的缓存**：
| 缓存 | 典型大小 | 命令 |
|------|:--------:|------|
| pip cache | ~3.2GB | `pip cache purge` |
| npm cache | ~1.5GB | `npm cache clean --force` |
| uv cache | ~817MB | `uv cache clean` |
| APT cache | 安全 | `sudo apt clean` |
| Journal logs | 可回收 | `sudo journalctl --vacuum-time=7d` |

## 五、文件整理（organize）

使用 `scripts/file-organize.py` 整理 `~/.hermes/` 根目录散乱文件：

```bash
# 预览
python3 ~/.hermes/skills/file-system-manager/scripts/file-organize.py --dry-run

# 执行
python3 ~/.hermes/skills/file-system-manager/scripts/file-organize.py --apply
```

**文件分类规则**：
| 扩展名 | 目标目录 |
|--------|----------|
| .pdf, .docx, .pptx, .xlsx | output/documents/ |
| .png, .jpg, .jpeg, .gif, .svg | output/images/ |
| .html, .htm | output/html/ |
| .py, .sh | scripts/ |
| 版本标记文件（_v, _backup） | archive/ |

## 六、健康检查

使用 `scripts/file-health-check.py` 检查文件系统健康状态：

```bash
python3 ~/.hermes/skills/file-system-manager/scripts/file-health-check.py
```

**检查项**：
- 根目录散乱文件
- 缺失的必备目录
- 缺失的重要文件
- output 目录结构
- 文件数量/总大小统计

### ⚠️ 健康检查陷阱：`EXPECTED_ROOT_FILES` 硬编码列表

**问题**：`file-health-check.py` 的 `EXPECTED_ROOT_FILES` 列表（第 23-38 行）硬编码了「期待在根目录存在」的重要文件列表。当文件被迁移到标准目录（state/, data/, cache/, archive/）后，健康检查会误报「缺失重要文件」。

**2026-05-17 实战**：Phase 1 文件迁移后将 9 个文件移出根目录 → 健康检查报告 9 个 missing 警告（实际是误报——文件已通过软链接/归档安全存在于标准位置）。

**检测方法**：
```bash
# 查看当前 EXPECTED_ROOT_FILES 列表
grep -A 20 'EXPECTED_ROOT_FILES' ~/.hermes/skills/dogfood/file-system-manager/scripts/file-health-check.py
```

**修复流程**：
1. 确认文件是否已通过软链接存在于标准目录（`ls -la ~/.hermes/data/auth.json`）
2. 如果已正确迁移，从 `EXPECTED_ROOT_FILES` 中移除
3. 运行健康检查验证：`python3 file-health-check.py | grep -c "缺失重要文件"` 应为 0

**预防**：每次执行完文件迁移后，记得同步更新 `EXPECTED_ROOT_FILES` 列表。

## 七、旧版本清理

确认当前 Hermes 版本运行正常后可以安全删除：

```bash
# 检查当前版本
hermes --version

# 确认后删除旧版本
rm -rf ~/.hermes/hermes-agent_old_v0.10.0
```

**⚠️ 前提**：确保新版 hermes 已稳定运行至少 1 天，功能正常。

## 八、自动定时清理（建议 cron）

```bash
# 每日 3:00 — disk-cleanup quick
cronjob create --name "daily-disk-cleanup" --schedule "0 3 * * *" \
  --prompt "运行 /disk-cleanup quick 进行安全清理"

# 每周日 3:00 — session prune
cronjob create --name "weekly-session-prune" --schedule "0 3 * * 0" \
  --prompt "运行 hermes sessions prune --older-than 7 --yes"

# 每月 1 日 3:00 — state.db VACUUM
cronjob create --name "monthly-db-vacuum" --schedule "0 3 1 * *" \
  --prompt "对 ~/.hermes/state.db 执行 SQLite VACUUM + WAL checkpoint，记录前后大小变化"

# 每月 1 日 3:00 — 缓存清理
cronjob create --name "monthly-cache-cleanup" --schedule "0 3 1 * *" \
  --prompt "运行 python3 ~/.hermes/skills/file-system-manager/scripts/cache-cleanup.py --apply"
```

> ⚠️ `monthly-db-vacuum` 只回收空闲页（freelist）。如果 state.db 的真实内容是 FTS 索引（不能压缩），VACUUM 效果有限。详见第十五节。

## 九、绝对安全规则

### 🚫 永远不自动清理
- `sessions/` 中活跃会话文件
- `state.db`（只 prune 不删除）
- `logs/` 下 7 天内的日志
- `sessions/` 下最近 7 天的会话记录

### 🗑️ 安全可删的根状态文件
以下 `.hermes/` 根目录文件**可安全删除**（系统会自动重建）：

| 文件 | 大小 | 说明 |
|:-----|:----:|:-----|
| `gateway.lock` | ~4K | 运行时锁文件，重启后自动重建 |
| `models_dev_cache.json` | ~2MB | 模型开发缓存，下次调用时自动重生成 |

### 📌 必须保留的根状态文件
以下文件是**系统运行状态**，删除会导致功能异常或数据丢失：

| 文件 | 大小 | 用途 | 删除后果 |
|:-----|:----:|:-----|:---------|
| `sdd_state.json` | ~36K | SDD 工作流状态 | SDD 进度丢失 |
| `installed_packs.json` | ~4K | 能力包安装记录 | 需要重装所有包 |
| `installed_opencode_packs.json` | ~4K | OpenCode 包记录 | 同左 |
| `kanban.db` | ~100K | Kanban 看板数据 | 看板清空 |
| `KNOWLEDGE_INDEX.md` | ~8K | 知识索引 | 需要重建索引 |
| `learning_history.json` | ~8K | 学习历史 | 历史丢失 |
| `health-report-state.json` | ~4K | 健康报告状态 | 报告状态丢失 |
| `config.yaml` | — | 主配置 | ⚠️ 系统无法启动 |
| `AGENTS.md` | — | 工作流门禁规则 | ⚠️ 工作流恢复失败 |
| `SOUL.md` | — | boku 的灵魂 | ⚠️ 身份丢失 |
| `state.db` | ~200M | SQLite 状态数据库 | ⚠️ 所有状态丢失 |

### 🛡️ 清理前必须确认
- `hermes-agent_old_v0.10.0/`：确认新版正常
- `state-snapshots/`：保留最近 3 个
- `~/.cache/camoufox/`：浏览器配置，重建成本高

### 📍 路径安全
- 只清理 `$HERMES_HOME` 和 `/tmp/hermes-*`
- 拒绝对外部路径的操作
- 所有脚本都有 `dry-run` 模式

---

## 十、独立项目存放规范

> `file-system-manager` 管理的是 **$HERMES_HOME 内部** 的文件。独立项目不应放在 `~/.hermes/` 或 `/tmp/` 下。

### 标准项目目录

```
~/projects/              ← 所有独立项目（Runtime/常驻服务）的家
├── sra/                 ← SRA (Skill Runtime Advisor)
└── ...                  ← 未来的独立项目
```

### 三类文件的分界

| 类型 | 存放位置 | 管理方式 | 示例 |
|:-----|:---------|:---------|:-----|
| 🏠 **Hermes 内部** | `~/.hermes/` | file-system-manager 管理 | skills, config, sessions, cache |
| 📦 **独立项目** | `~/projects/<name>/` | 项目自身管理 | SRA 源码 |
| 🕊️ **临时文件** | `/tmp/` | 预期可丢失 | 编译产物、下载缓存 |

### 为什么独立项目不放 `~/.hermes/`？

- `~/.hermes/` 是 Hermes Agent 的领地，混入外部项目会污染目录结构
- 独立项目有自己的生命周期（git 仓库、pip install、systemd 服务），和 Hermes 的配置/日志/缓存完全不同
- 清理脚本（disk-cleanup）如果误伤项目文件会造成严重后果

### 为什么不放 `/tmp/`？

- `/tmp/` 重启可能被系统清理
- 缺乏持久性保证
- 项目源码应该有稳定的存放位置

### 独立项目的典型安装方式

```bash
cd ~/projects/<project-name>
# editable 安装到 Hermes venv，修改源码后立即生效
~/.hermes/hermes-agent/venv/bin/python3 -m pip install --no-build-isolation -e .
```

---

## 十一、HOME 根目录清理规程

> `~/` 是用户家目录，不应成为各种实验产物的堆放地。任何未经规划的独立项目放在 `~/` 根目录，都要走此规程。

### 四步清理法（从实战提炼）

| 步骤 | 操作 | 说明 |
|:----:|:-----|:-----|
| 1️⃣ **排查** | `find ~/ -maxdepth 1 -type d` 列出所有根目录项目 | 识别哪些是 Hermes 目录，哪些是散乱项目 |
| 2️⃣ **汇报** | 列出每个目录的大小、内容、最近修改时间 | ⚠️ 用 HTML 截图汇报，不用终端 ASCII |
| 3️⃣ **等待确认** | **必须等主人逐项回复后再执行** | ❌ 不可跳過此步一次刪完 |
| 4️⃣ **执行** | 按 owner 确认逐项删除，完成后验证 | 报告每个目录的状态 + 磁盘释放情况 |

### 🔄 多步清理工作流（主人铁律）

当清理涉及多个步骤（如 Step1→2→3→4）时，**必须**：
1. 先交付完整的**分步方案**给主人审阅
2. **等主人批准后再执行 Step 1**
3. 每完成一个 Step，汇报结果
4. **等主人说"继续"才能进下一个 Step**
5. ❌ 永远不「我先全部执行，最后报告」
6. ❌ 永远不「擅自推进到下一步」

### ⚠️ 备份超时陷阱（重要！）

```bash
# ❌ 错误做法 — 大目录会超时
cp -r ~/large-dir/ ~/.hermes/disk-cleanup/backup/

# ✅ 正确做法 — 用 tar 流式压缩（不超时）
tar -czf ~/.hermes/disk-cleanup/backup-$(date +%Y%m%d).tar.gz -C ~ large-dir/

# ✅ 大目录（5GB+）跳过备份，直接删除
# Python venv、node_modules 等可重新安装
timeout 30 tar -czf ... || (echo "文件太大，跳过备份直接删除" && rm -rf ~/large-dir/)
```

**规则**：
- 目录 < 1GB → `cp -r` 备份（最快）
- 目录 1-5GB → `tar` 压缩备份
- 目录 > 5GB → ⚠️ 直接删除（Python venv / node_modules 等可重建）
- **永远不要在备份步骤中用 `cp -r` 拷贝 5GB+ 目录**——会导致脚本超时中断

### ⚠️ 常见陷阱：只扫目录，不扫文件（2026-05-17 实战发现）

在 Step 2 清理了 8 个根目录后，**boku 以为已经干净了**，但主人指出 **根目录还有几十个 PDF、PY、HTML 文件散落着**。教训：

```bash
# ❌ 只查目录 — 遗漏了单个文件！
find ~/ -maxdepth 1 -type d  # 只列目录

# ✅ 必须同时查文件和目录！
find ~/ -maxdepth 1 \( -type f -o -type d \) ! -name ".*"  # 所有非隐藏文件+目录
find ~/ -maxdepth 1 -name "*.pdf" -o -name "*.py"  # 特定文件类型
```

**规律**：根目录散乱 ≠ 只有散乱目录。Python 脚本（一次性生成器）、PDF 报告、HTML 预览图等单文件更容易被遗漏，因为它们不像目录那么显眼。

**扫描流程修正**：
1. 先扫目录：`find ~/ -maxdepth 1 -type d`（剔除系统隐藏目录）
2. 再扫文件：`find ~/ -maxdepth 1 -type f ! -name ".*"`（所有非隐藏文件）
3. 特别关注：`*.pdf`, `*.py`, `*.html`, `*.pptx`, `*.png`, `*.json`
4. 合并汇报给主人，统一确认后再处理

### 判定基准：哪些 `~/` 下的目录可删？

| 类型 | 示例 | 处理方式 |
|:-----|:------|:---------|
| 📸 预览图产物 | `learning_workflow_cn_previews*/` | 可删除，可重新生成 |
| 🐍 Python venv | `docling-env/`, `.*-env/` | 可删除，用 `pip install` 重建 |
| 🎯 单文件项目 | `trump_china_visit/` | 评估是否有价值，可移入 `~/projects/` |
| 📂 学习工作流产物 | `cycle-analysis/`（在 learning/ 内） | 评估是否过时 |
| ⚙️ 系统目录 | `.config/`, `.local/`, `.cache/`, `.ssh/` | 🚫 永远不删 |

---

## 十二、文件系统规范（权威标准）

> **`~/.hermes/standards/filesystem-规范.md`** 是 Hermes 文件系统的**规范权威来源 SSoT**。
> 所有文件写/删操作必须参照此规范执行。本 skill 的清理/整理/健康检查职能建立在规范之上。

### 12.1 规范覆盖的核心内容

| 规范章节 | 与本 skill 的关系 | 关键规则 |
|:---------|:-----------------|:---------|
| 目录布局（第2-3章） | 定义哪些目录该存在 | XDG 五类模型：CONFIG/DATA/STATE/CACHE/TEMP |
| 文件类型与生命周期（第4章） | 定义保留/清理策略 | 每类文件特定保留期 |
| 命名规范（第5章） | organize 脚本的过滤规则 | `{前缀_}{描述_}{日期}.{扩展名}` |
| Skill 结构（第6章） | 84 个 skill 必须遵循 | 6 个子目录 + SKILL.md |
| 项目结构（第7章） | `~/projects/` 组织方式 | README + AGENTS.md + docs/ |
| 写删门禁（第8章） | **file-system-manager 的执行依据** | 20 条门禁规则 |
| 归档清理（第10章） | 与第8章 cron 联动 | 90天清理门禁 |

### 12.2 规范中的保护列表（禁止自动删除）

与第9节「绝对安全规则」联动，规范还额外保护：
- `~/.hermes/standards/` — 规范文档
- `~/.hermes/docs/research/fs-enforcement-hooks-research.md` — 钩子研究
- `~/projects/*/.git/` — Git 仓库
- `skills/**/SKILL.md` — 任何 skill 的核心文件

### 12.3 如何引用规范

```bash
# 查看完整规范
cat ~/.hermes/standards/filesystem-规范.md

# 检查某个路径是否符合规范
python3 ~/.hermes/skills/file-system-manager/scripts/file-health-check.py

# 组织文件到正确目录（按规范分类）
python3 ~/.hermes/skills/file-system-manager/scripts/file-organize.py --dry-run
```

---

## 十三、规范自动执行策略（已实施）

> 本 skill 除了手动清理/整理，已通过 **Hermes 钩子系统** 自动执行规范。
> `config.yaml` 已配置 `hooks:` 块，`plugins/fs-enforce/` 插件已安装并启用。

### 13.1 三层介入架构（完整链路）

```
L1: Shell Hooks（配置驱动，零代码）   ← ✅ 已配置（config.yaml hooks:）
    ├─ 每次 write_file/patch → 记录路径到审计日志
    ├─ pre_tool_call 可 block 违规操作
    └─ 工具: ~/.hermes/scripts/fs-enforce/fs-audit.py

L2: Python Plugin（完整拦截能力）    ← ✅ 已启用（plugins.enabled）
    ├─ pre_tool_call → 拦截违规写入（命名/目录/范围）
    ├─ post_tool_call → 执行规范检查
    └─ /fs-enforce 命令 → 诊断（status/stats/log/check）

L3: 源码扩展（最后防线）             ← 📋 可选（待定）
    └─ 扩展 tools/file_tools.py 的 _SENSITIVE_PATH_PREFIXES
```

### 13.2 具体实施状态

| 阶段 | 内容 | 状态 | 交付物 |
|:----:|:-----|:----:|:-------|
| Phase 0 | 地基搭建 | ✅ 已完成 | `standards/filesystem-规范.md` + `scripts/fs-enforce/rules.yaml` |
| Phase 1 | Shell Hooks | ✅ 已完成 | `config.yaml` hooks 配置 + `fs-audit.py` 审计引擎 |
| Phase 2 | Python Plugin | ✅ 已完成 | `plugins/fs-enforce/`（plugin.yaml + __init__.py + enforcer.py） |
| Phase 3 | Skill 存量整改 | 📋 待主人确认 | 84 个 skill 合规审计 |
| Phase 4 | 持续自动化 | ✅ 已完成 | cronjob `daily-fs-audit` + `fs-health.py` 健康报告 |

### 13.3 关键文件位置

| 文件 | 路径 | 作用 |
|:-----|:-----|:------|
| 规范文档 | `~/.hermes/standards/filesystem-规范.md` | SSoT 权威来源 |
| 规则配置 | `~/.hermes/scripts/fs-enforce/rules.yaml` | 热加载规则 |
| 审计脚本 | `~/.hermes/scripts/fs-enforce/fs-audit.py` | Shell Hook 调用的审计引擎 |
| Python 插件 | `~/.hermes/plugins/fs-enforce/` | 拦截 + 审计 + 诊断 |
| 审计日志 | `~/.hermes/data/fs-audit/audit.log` | 所有文件操作记录 |
| 健康报告 | `~/.hermes/scripts/fs-enforce/fs-health.py` | 6 维度健康检查 |
| 日报脚本 | `~/.hermes/scripts/fs-enforce/daily-audit.sh` | 每日审计报告 |
| Skill 健康检查 | `~/.hermes/scripts/fs-enforce/skill-health-check.py` | SQS v2.0 集成到每日报告 |
| 实施计划 | `~/.hermes/docs/plans/fs-enforcement-implementation-plan.md` | 详细实施文档 |

### 13.4 Hermes 可用的钩子（与文件操作相关）

| 钩子 | 触发时机 | 适合做什么 | 可 block? |
|:-----|:---------|:-----------|:---------:|
| `pre_tool_call` | 工具执行前 | 拦截违规写入 ✅ | ✅ |
| `post_tool_call` | 工具执行后 | 记录审计日志 | ❌ |
| `on_session_end` | 会话结束 | 清理中间产物 | ❌ |
| `transform_tool_result` | 结果展示前 | 改写工具输出 | ❌ |

### 13.5 /fs-enforce 命令使用

```bash
# 查看状态摘要
/fs-enforce status

# 查看审计统计
/fs-enforce stats

# 查看最近 10 条审计日志
/fs-enforce log 10

# 检查一个路径是否合规
/fs-enforce check ~/.hermes/test.txt
```

### 13.6 Skill 质量健康检查（集成到每日报告）

从 2026-05-17 起，每日 cron 任务 `daily-fs-audit` 自动集成 Skill 质量健康检查：

```bash
# 手动运行
python3 ~/.hermes/scripts/fs-enforce/skill-health-check.py
```

**检查维度（204 个 skill）**：
- frontmatter 覆盖率
- `depends_on` 覆盖率
- `triggers` 丰富度
- 版本号完整性
- 超过 180 天未更新的 skill 数量
- 综合健康度评分（%）

产出示例：
```
## 📦 Skill 质量健康检查
- 总 Skill 数: 205
- ✅ 有 YAML frontmatter: 205/205
- ✅ 有 depends_on: 205/205
- 🔴 超过 180 天未更新: 0/205
🟡 Skill 生态健康度: 79% — 待改进
```

### 13.7 SQS v2.0 评分集成

日常修改 skill 时通过 `pre_flight.py` 自动触发 SQS 评分：

```bash
# 在 pre_flight 输出中可见
Gate 3: 🛠️ 检测到技能操作
    ├── SQS v2.0: 106/140 🟡 (良好)
    └── 可优化维度: S5_relations, S1_metadata
```

**SQS v2.0 评分系统**：7 维度 × 20 分 = 140 分制。详见 `skill-creator v6.0`。

```
{
  "ts": "2026-05-17T13:42:03Z",     # 时间戳
  "tool": "write_file",              # 工具名
  "path": "~/.hermes/AGENTS.md",    # 原始路径
  "real_path": "/home/ubuntu/.hermes/AGENTS.md",
  "verdict": "BLOCKED",             # PASS | BLOCKED | WARN
  "reason": "protected_path:AGENTS.md",  # 违规原因
  "session": "test_2"               # 会话 ID
}
```

---

## 十四、本次真实清理记录
- disk-cleanup 插件已启用但从未运行的完整分析
- Sessions 清理双重陷阱（30天阈值无效 + prune 不删 JSON 文件）
- 84 个 skill 结构合规性审计数据
- 学习脚本被覆盖为桩文件的恢复方法

> **完整 Phase 0-4 执行记录见** `references/governance-phase0-4-execution.md`


## 十五、state.db 数据库优化

> Hermes 的核心数据存储在 SQLite 数据库 `~/.hermes/state.db` 中。这是文件系统管理的重要组成部分。

### 15.1 空间分布（实战分析 2026-05-17）

| 表/索引 | 行数 | 空间 | 说明 |
|:--------|:----:|:----:|:-----|
| `messages_fts_trigram_data` | 43,307 | **165MB** 🔴 | FTS 三元组索引（最大消耗者） |
| `messages_fts_content` | 25,471 × 2 | **152MB** 🔴 | FTS 全文索引（两份） |
| `messages` | 25,471 → **8,875** | **90MB** 🟡 | 对话消息本体 |
| `messages_fts_data` | 7,454 | 29MB | FTS 辅助索引 |
| `sessions` | 614 → **197** | 20MB | 会话元数据 |
| 其他 | — | ~5MB | 元数据、配置 |
| **总计** | | **459–464MB** | 大部分为 FTS 索引 |

### 15.2 维护操作

**每月 VACUUM**（推荐 cron 自动执行）：
```bash
python3 -c "
import sqlite3, os
db = os.path.expanduser('~/.hermes/state.db')
before = os.path.getsize(db)
conn = sqlite3.connect(db)
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
conn.execute('VACUUM')
conn.close()
after = os.path.getsize(db)
print(f'{before/1024/1024:.0f}MB → {after/1024/1024:.0f}MB ({(before-after)/1024/1024:.1f}MB freed)')
"
```

**空间查询工具**（诊断用）：
```python
python3 -c "
import sqlite3, os
db = os.path.expanduser('~/.hermes/state.db')
conn = sqlite3.connect(db)
cur = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
for t in cur.fetchall():
    name = t[0]
    count = conn.execute(f'SELECT COUNT(*) FROM \"{name}\"').fetchone()[0]
    pages = conn.execute(f'SELECT SUM(pgsize) FROM dbstat WHERE name=\"{name}\"').fetchone()[0]
    if pages:
        print(f'{name:40s} {count:>8} rows  {pages/1024/1024:>7.1f}MB')
conn.close()
"
```

### 15.3 重要认知

- **FTS 索引不可压缩**：`messages_fts_trigram_data` 等的 165MB 是功能代价（支持全文搜索）。DELETE 消息不会自动回收 FTS 空间，需要重建索引。
- **VACUUM 的收益**：仅回收空闲页（freelist）。在正常使用中 freelist 通常只占 1-5%，VACUUM 效果有限。如果数据库有大量 DELETE，空闲页占比会上升。
- **真正减少 state.db 大小的方法**：减少 messages 表行数（通过 prune 旧 sessions）。每条 message 会触发 FTS 索引写入，删除旧 message 虽然不会立即回收索引空间，但会阻止进一步膨胀。
- **sessions 清理是 state.db 减肥的钥匙**：详见第三节 Sessions 管理。

### 15.4 FTS 索引重建（释放空间的高级技术）

**何时使用**：大量 sessions prune（删除 10,000+ 条 messages）后，FTS 索引碎片化严重。

**操作**（5 分钟，低风险）：
```python
python3 -c "
import sqlite3, os
db = os.path.expanduser('~/.hermes/state.db')
before = os.path.getsize(db)
conn = sqlite3.connect(db)
conn.execute(\"INSERT INTO messages_fts(messages_fts) VALUES('rebuild')\")
conn.commit()
conn.execute(\"INSERT INTO messages_fts(messages_fts) VALUES('optimize')\")
conn.commit()
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
conn.execute('VACUUM')
conn.close()
after = os.path.getsize(db)
print(f'{before/1024/1024:.0f}MB → {after/1024/1024:.0f}MB ({(before-after)/1024/1024:.1f}MB freed)')
"
```

**预期收益**（实战数据 2026-05-17 — 累计效果，含 session prune + message prune + FTS rebuild + VACUUM）：
| FTS 表 | 碎片化前（估） | 重建后（估） | 释放 |
|:-------|:-------------:|:------------:|:----:|
| trigram_data | 165MB | ~120MB | ~45MB |
| fts_content | 152MB | ~110MB | ~42MB |
| **总计** | **~343MB** | **~275MB** | **~50-70MB** |

**安全风险**：🟢 低——FTS rebuild 是原子操作，重建期间搜索功能暂时降级（~1 秒）。
**回滚**：不可逆，但可重新插入数据重建（不推荐）。

**实战效果**（2026-05-17，累计 3 次操作）：
```text
操作: sessions prune (417 records) → messages prune (16,596 rows) 
      → FTS REBUILD + OPTIMIZE → VACUUM
结果: state.db 460MB → 328MB (释放 132MB 🎉)
说明: 实际释放量远超 FTS 碎片预估（50-70MB），因为 VACUUM 同时回收了
      session/message prune 产生的空闲页。FTS 碎片 + 空闲页 = 最大化收益。
```

### 15.5 何时用 VACUUM vs FTS REBUILD

| 场景 | 操作 | 预期释放 |
|:-----|:------|:--------:|
| 日常维护（freelist 回收） | VACUUM | 1-5% |
| 大量消息删除后（FTS 碎片） | FTS REBUILD + VACUUM | 15-20% |
| 两种都做 | REBUILD → OPTIMIZE → VACUUM | 最大化 |

### 15.6 配置优化

```yaml
# ~/.hermes/config.yaml
sessions:
  auto_prune: true
  retention_days: 7          # 默认 30→7，阻止膨胀
  vacuum_after_prune: true   # prune 后自动 VACUUM
  min_interval_hours: 24


## 十六、根目录文件安全迁移规程

> 当新文件/目录被加根目录时，需要按照规范迁移到标准目录。

### 16.1 三类文件迁移策略

| 类别 | 迁移方式 | 原因 | 通用命令 |
|:-----|:---------|:-----|:---------|
| **STATE**（运行时状态） | `mv → ln -s` | Hermes 可能硬编码路径 | `mv file state/ && ln -s state/file file` |
| **DATA**（持久数据） | `cp → verify → mv → ln -s` | 确保数据一致性 | 详见下方模板 |
| **CACHE**（缓存） | `mv → ln -s` | 可自动重建 | `mv file cache/ && ln -s ../cache/file file` |

### 16.2 STATE 迁移模板（软链接安全）

```bash
cd ~/.hermes
for f in sdd_state.json installed_packs.json; do
  [ -f "$f" ] && [ ! -L "$f" ] && \
    mv "$f" "state/$f" && \
    ln -s "state/$f" "$f" && \
    echo "✅ $f → state/$f"
done
```

### 16.3 DATA 迁移模板（复制+一致性验证）

```bash
cd ~/.hermes
for f in auth.json kanban.db; do
  cp "$f" "data/$f" && \
  mv "$f" "data/$f.orig" && \
  ln -s "data/$f" "$f" && \
  if cmp -s "data/$f" "data/$f.orig"; then
    rm "data/$f.orig" && echo "✅ $f verified"
  else
    echo "❌ $f MISMATCH"
  fi
done
```

### 16.4 CACHE 迁移模板

```bash
cd ~/.hermes
  for f in models_dev_cache.json; do
    [ -f "$f" ] && [ ! -L "$f" ] && \
      mv "$f" "cache/$f" && \
      ln -s "cache/$f" "$f"
  done
```

### 16.5 迁移后的验证

```bash
cd ~/.hermes
for f in sdd_state.json installed_packs.json auth.json kanban.db; do
  if [ -L "$f" ] && [ -f "$(readlink -f "$f")" ]; then
    echo "✅ $f → $(readlink "$f") ($(wc -c < "$f") bytes, readable)"
  else
    echo "❌ $f broken"
  fi
done
```

### 16.6 实战数据（2026-05-17）

一次迁移 13 个根目录文件到标准目录，全部使用软链接保持向后兼容。

- **STATE 文件**（8 个）：sdd_state.json, installed(_opencode)_packs.json, learning/health-report/gateway_state.json, auth.lock, processes.json → `state/`
- **DATA 文件**（4 个）：auth.json, feishu_seen_message_ids.json, kanban.db, channel_directory.json → `data/`
- **CACHE 文件**（1 个）：models_dev_cache.json → `cache/`

详见 `references/file-migration-20260517.md`。

### 16.7 注意事项

1. 🚫 **不要直接 `rm` 原文件** — 先 `mv` 移走再 `ln -s`，确保路径持续有效
2. 🚫 **不要用 `cp` 覆盖** — 文件可能正被 Hermes 进程使用
3. ✅ **DATA 类必须验证** — `cmp -s` 确保复制内容无误后再删除原文件
4. ✅ **state.db 不迁移** — 硬编码在 Hermes 源码中
5. ✅ **逐个处理** — 不要 batch mv，某些文件可能被进程锁定
6. ⚠️ **验证迁移后的软链接** — `os.path.exists()` 必须为 True

### 16.8 🚨 经典陷阱：软链接相对路径

**问题**：从 `~/.hermes/` 创建软链接时，`ln -s "../data/auth.json" auth.json` 创建的路径相对于 **链接本身的位置**（`~/.hermes/`），`../data/` 解析为 `~/data/` ❌，而非 `~/.hermes/data/`。

```bash
# ❌ 错误 — 会断链！
cd ~/.hermes
ln -s "../data/auth.json" auth.json  
# 解析: ~/.hermes/auth.json → ~/.hermes/../data/auth.json → ~/data/auth.json ❌

# ✅ 正确 — 从 symlink 所在目录出发
cd ~/.hermes
ln -s "data/auth.json" auth.json
# 解析: ~/.hermes/auth.json → ~/.hermes/data/auth.json ✅
```

**根因**：软链接的 `..` 相对于链接文件所在目录，而非常规认知的「相对于当前工作目录」。

**检测方法**：
```bash
cd ~/.hermes
for f in auth.json feishu_seen_message_ids.json kanban.db channel_directory.json; do
  if [ -L "$f" ] && [ ! -e "$f" ]; then
    echo "❌ 断链: $f → $(readlink "$f") (realpath: $(realpath "$f" 2>&1))"
  fi
done
```

**修复**：
```bash
cd ~/.hermes
for f in auth.json feishu_seen_message_ids.json kanban.db channel_directory.json; do
  if [ -L "$f" ] && [ ! -e "$f" ]; then
    target="${f#../}"  # 去掉 "../" 前缀
    [ -f "data/$f" ] && target="data/$f"
    [ -f "cache/$f" ] && target="cache/$f"
    rm "$f" && ln -s "$target" "$f" && echo "✅ 修复: $f → $target"
  fi
done
```

**实战教训**（2026-05-17）：Phase 1 迁移 13 个根目录文件时，DATA 和 CACHE 软链接全部使用了 `../` 前缀，导致 5/13 个软链接断链。健康检查报告了 9 个「缺失重要文件」误报，根源在此。
