# Skill 生命周期覆盖审计 — 全量入口分析

> **审计时间**：2026-05-14  
> **审计范围**：Hermes Agent 源码（`~/.hermes/hermes-agent/`）+ skill 系统（`~/.hermes/skills/`）+ 脚本（`~/.hermes/scripts/`）  
> **方法**：全量搜索 skill 创建/修改/删除的代码路径，交叉引用 agent 工具管道路径

---

## 一、方法论

boku 遍历了以下源码目录的所有 skill 相关操作：

| 目录 | 文件数 | 关注点 |
|:-----|:------:|:-------|
| `hermes-agent/tools/` | 7 个工具 | `skill_manager_tool`, `skills_tool`, `skills_sync`, `skills_guard`, `skill_provenance`, `skill_usage`, `skills_hub` |
| `hermes-agent/hermes_cli/` | 4 个文件 | `skills_hub.py`, `skills_config.py`, `curator.py`, `profiles.py` |
| `hermes-agent/agent/` | 4 个文件 | `curator.py`, `skill_preprocessing`, `skill_commands`, `curator_backup` |
| `hermes-agent/plugins/` | 5 个目录 | 所有插件（kanban, disk-cleanup, memory, hermes-achievements） |
| `hermes-agent/hermes_cli/commands.py` | 1 个文件 | slash 命令注册表（COMMAND_REGISTRY） |
| `~/.hermes/skills/` | 4 个 skill | `skill-creator`, `learning-workflow`, `knowledge-precipitation`, `night-study-engine` |
| `~/.hermes/scripts/` | 2 个脚本 | `pre_flight.py`, `skill-auto-link.py`, `knowledge-ingest.py` |

---

## 二、27 个入口全表

### A. Agent 工具层 (2 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 1 | `skill_manage(action)` | `tools/skill_manager_tool.py` | create/edit/patch/delete/write_file/remove_file | pre_flight Gate 3 + AGENTS.md 铁律 + SQS + 依赖扫描 | ✅ |
| 2 | `write_file`/`patch` 到 skill 目录 | `tools/skill_manager_tool.py` 以外路径 | 直接文件写入 | ❌ 完全无检测 | ❌ |

**说明**：`write_file` 和 `patch` 是 Hermes 内置的通用文件工具，不经过 `skill_manager_tool.py`。当目标路径是 `~/.hermes/skills/xxx/` 时，没有触发任何 skill 质量门禁。

### B. CLI 命令层 (5 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 3 | `hermes skills install <id>` | `hermes_cli/skills_hub.py` → `tools/skills_hub.py` | 下载安装 hub skill | skills_guard 安全扫描 | ❌ |
| 4 | `hermes skills update` | `hermes_cli/skills_hub.py` | 检查并更新 | 版本对比 | ❌ |
| 5 | `hermes skills uninstall <n>` | `hermes_cli/skills_hub.py` | 删除 skill | 无 | ❌ |
| 6 | `hermes skills publish <path>` | `hermes_cli/skills_hub.py` | 发布到 registry | 无 | ❌ |
| 7 | `hermes skills tap add <repo>` | `hermes_cli/skills_hub.py` | 添加 GitHub 源 | 无 | ❌ |

**说明**：CLI 命令直接调用 Hermes 内部库函数（`tools/skills_hub.py`），不走 agent 的工具调用（tool calling）管道。`skills_guard` 对 hub 安装做安全扫描但不做质量评分。

### C. 同步层 (1 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 8 | `skills_sync` 内置同步 | `tools/skills_sync.py` | 启动时复制 bundled skills | 版本 hash 对比 | ❌ |

**说明**：Hermes 启动或更新时，`skills_sync.py` 扫描 `skills/.bundled_manifest`，将 repo 中的 bundled skills 同步到用户目录。通过 MD5 hash 判断用户是否修改过。无质量门禁（bundled skill 默认质量有保障，但同步流程本身不验证）。

### D. 策展人层 (2 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 9 | `agent/curator` 后台自动扫描 | `agent/curator.py` | 自主创建/合并/归档 skill | skill_provenance 标记 | ❌ |
| 10 | `hermes curator <subcommand>` CLI | `hermes_cli/curator.py` | 手动 curator 操作（status/run/pin/unpin/pause） | 无 | ❌ |

**说明**：curator 使用辅助模型（auxiliary client）在后台运行，通过 `skill_provenance` 的 ContextVar 标记写来源（`background_review` vs `foreground`），但不加载 skill-creator。curator 遵循严格的安全约束（只操作 agent-created skills、never auto-deletes），但无质量门禁。

### E. 文件系统层 (4 入口)

| # | 入口 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:--------:|:-----:|
| 11 | `terminal: cp/mv/rm` → skill 目录 | 文件系统操作 | ❌ 完全无检测 | ❌ |
| 12 | `terminal: cat/echo/tee >` → skill 目录 | 文件系统操作 | ❌ 完全无检测 | ❌ |
| 13 | git clone/pull → 技能仓库 | 代码库操作 | ❌ 完全无检测 | ❌ |
| 14 | 手动文件编辑器修改 | 文件系统操作 | ❌ 完全无检测 | ❌ |

**说明**：终端工具（terminal）可以执行任何 shell 命令直接操作 skill 文件系统。这些操作没有任何 skill-creator 介入。

### F. 脚本自动化层 (2 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 15 | cronjob 创建/修改 skill | `cron/` + terminal 工具 | 定时任务操作 skill | 无 skill-creator 加载 | ❌ |
| 16 | `delegate_task` 子代理 | `run_agent.py` → 子 AIAgent | 委托任务调 skill_manage | skip_context_files=True | ❌ |

**说明**：cron 任务在独立会话中运行，不加载 skill-creator。`delegate_task` 的子代理默认 `skip_context_files=True`，这是完全绕过 skill-creator 的最严重缺口。此问题已在 Hermes 社区记录（issue #18963）。

### G. 知识沉淀层 (4 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 17 | learning-workflow STEP 4 | `skills/learning-workflow/SKILL.md` §STEP 4 | 学习→创建 skill | 显式调用 skill-creator | ✅ |
| 18 | night-study-engine STEP 6 | `skills/night-study-engine/SKILL.md` §五 | 自学→产出 Artifact | 无独立 skill-creator 门禁 | ❌ |
| 19 | knowledge-precipitation L1 维护 | `skills/knowledge-precipitation/SKILL.md` §三 | 维护 L1 skills | 无强制对接 skill-creator | ❌ |
| 20 | knowledge-ingest.py | `~/.hermes/scripts/knowledge-ingest.py` | 自动沉淀知识到 skill | 无 skill-creator 调用 | ❌ |

**说明**：learning-workflow 是唯一在流程中显式调用 skill-creator 的知识沉淀入口。其他入口（night-study-engine、knowledge-precipitation、knowledge-ingest）也输出 skill 文件，但没有强制加载 skill-creator 的门禁。

### H. Profile 层 (2 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 21 | `hermes profile create --clone` | `hermes_cli/profiles.py` line 510 | `shutil.copytree(source_skills, target_skills)` | 直接文件复制 | ❌ |
| 22 | `hermes profile export/import` | `hermes_cli/profiles.py` | 导出/导入 profile 含 skills | 仅 tar.gz 打包 | ❌ |

**说明**：Profile 克隆通过 `shutil.copytree()` 直接复制 skill 目录，不经过任何质量检查。导入时也不验证 skill 完整性。

### I. 插件层 (2 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 23 | `hermes plugins install <name>` | `hermes_cli/plugins.py` | 安装插件（可能带 skill） | 无 | ❌ |
| 24 | 插件内部 skill 写入 | `plugins/*/__init__.py` | 插件运行时创建 skill | 无 | ❌ |

### J. 安全扫描层 (3 入口)

| # | 入口 | 代码位置 | 操作类型 | 当前保护 | 覆盖？ |
|:-:|:-----|:---------|:---------|:--------:|:-----:|
| 25 | skills_guard 扫描 | `tools/skills_guard.py` | 安全扫描（exfiltration/injection/destructive） | 仅安全，不查质量 | ❌ |
| 26 | skill_provenance 追踪 | `tools/skill_provenance.py` | ContextVar 标记写来源 | 仅追踪，不查质量 | ❌ |
| 27 | path_security 路径验证 | `tools/path_security.py` | 路径 escape 检测 | 仅安全，不查质量 | ❌ |

**说明**：安全扫描层是当前最完整的 skill 保护机制，但只关注**安全性**（防注入/防泄漏），不关注**质量**（SQS 评分/结构完整性/可发现性）。

---

## 三、覆盖统计

| 分类 | 总数 | 已覆盖 | 覆盖率 |
|:-----|:----:|:------:|:-----:|
| Agent 工具层 | 2 | 1 | 50% |
| CLI 命令层 | 5 | 0 | 0% |
| 同步层 | 1 | 0 | 0% |
| 策展人层 | 2 | 0 | 0% |
| 文件系统层 | 4 | 0 | 0% |
| 脚本自动化层 | 2 | 0 | 0% |
| 知识沉淀层 | 4 | 1 | 25% |
| Profile 层 | 2 | 0 | 0% |
| 插件层 | 2 | 0 | 0% |
| 安全扫描层 | 3 | 0 | 0% (仅安全) |
| **总计** | **27** | **4 (含安全2)** | **15%** |

---

## 四、各缺口详细分析

### Gap 1：工具绕过 (Tool Bypass)

**严重性**：🔴 高危  
**涉及入口**：#2, #11-#14  
**真实风险**：最高。write_file 和 patch 是最常用的工具，无意中写入 skill 目录的概率最高。

**阻断方案**（手动，无需改 Hermes 核心）：
1. 在任何涉及 `~/.hermes/skills/` 路径的 write_file/patch 前，自觉加载 skill-creator
2. 在 AGENTS.md 的铁律中强化此项约束
3. 长期方案：修改 pre_flight.py 增加路径检测

### Gap 2：子代理盲区 (Subagent Blind Spot)

**严重性**：🔴 高危  
**涉及入口**：#16  
**真实风险**：高。复杂任务通过 delegate_task 拆分时，子代理完全不受约束。Hermes 社区 issue #18963 记录了此问题。

**阻断方案**（临时，子代理 context 注入）：
```python
delegate_task(
    goal="...",
    context="原上下文\n\n🔒 IMPORTANT: If you need to create, edit, or delete any skill, you MUST first load skill-creator via skill_view(name='skill-creator') and pass its quality checks. Do NOT use write_file or skill_manage on skill directories without this.",
    ...
)
```

### Gap 3：策展人质量门禁缺失 (Curator Quality Gap)

**严重性**：🟠 中危  
**涉及入口**：#9, #10  
**真实风险**：中。curator 的设计原则已经很保守（只操作 agent-created、never auto-deletes），但长期运行可能累积低质量 skill。

**阻断方案**：
1. 定期审查 curator 报告文件（`~/.hermes/skills/.curator_state` 的 `last_report_path`）
2. 对 curator 创建的 skill 手动运行 SQS 检查
3. 长期方案：修改 `agent/curator.py` 的 `_spawn_background_review()` 注入内联 SQS

### Gap 4：CLI 命令隔离 (CLI Isolation)

**严重性**：🟡 低危  
**涉及入口**：#3-#7  
**真实风险**：低。CLI 命令操作频率较低，且 hub skill 经过 skills_guard 安全扫描。

**阻断方案**：
1. 安装 hub skill 后自觉运行 `skill-quality-score.py <skill-name>` 检查质量
2. 长期方案：修改 `hermes_cli/skills_hub.py` 安装流程末尾调用 SQS 检查

---

## 五、源码关键位置索引

| 组件 | 文件 | 关键行/函数 |
|:-----|:-----|:-----------|
| skill_manage 实现 | `tools/skill_manager_tool.py` | `_do_create()`, `_do_edit()`, `_do_patch()`, `_do_delete()` |
| skills_list/skill_view | `tools/skills_tool.py` | `skills_list()` line 674, `skill_view()` line 849 |
| skills_guard 安全扫描 | `tools/skills_guard.py` | `scan_skill()`, `should_allow_install()` |
| skill_provenance | `tools/skill_provenance.py` | `set_current_write_origin()`, `BACKGROUND_REVIEW` |
| skill_usage 追踪 | `tools/skill_usage.py` | `bump_usage()`, `bump_view()`, `bump_patch()`, `mark_agent_created()` |
| skills_sync 同步 | `tools/skills_sync.py` | `sync_bundled_skills()`, manifest hash 对比 |
| skills_hub 库 | `tools/skills_hub.py` | `install_skill()`, `search()`, `resolve()`, `SkillBundle` |
| CLI skills_hub | `hermes_cli/skills_hub.py` | `do_install()`, `do_update()`, `do_uninstall()`, `do_publish()`, `do_tap()` |
| CLI curator | `hermes_cli/curator.py` | `_cmd_status()`, `_cmd_run()`, `_cmd_pin()`, `_cmd_unpin()` |
| agent curator | `agent/curator.py` | `maybe_run_curator()`, `_spawn_background_review()`, lifecycle transitions |
| 子代理 | `run_agent.py` | `delegate_task`, `skip_context_files=True` |
| pre_flight | `~/.hermes/scripts/pre_flight.py` | `check_skill_creator_need()` Gate 3, 关键词 regex 检测 |
| profile 克隆 | `hermes_cli/profiles.py` | line 510: `shutil.copytree(source_skills, profile_dir/"skills")` |
| CLI 命令注册 | `hermes_cli/commands.py` | `COMMAND_REGISTRY`, `GATEWAY_KNOWN_COMMANDS` |

---

## 六、审计更新记录

| 日期 | 版本 | 变更 |
|:-----|:-----|:-----|
| 2026-05-14 | v1.0 | 初始审计 — 全量扫描 Hermes 源码 + skill 系统，识别 27 入口 |
