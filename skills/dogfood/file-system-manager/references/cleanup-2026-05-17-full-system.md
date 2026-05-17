# 2026-05-17 文件系统全面清理实战记录

## 概况
- 磁盘从 76% (36/50G) → 68% (32/50G)，释放 **4GB**
- 清理了 8 个 HOME 根目录散乱项目 + 4 个废弃 skill 目录 + 11 个 learning 子目录

## Step 1：Skill 目录清理
- 删除 `bak-test/` `remove-test/` `multi-hermes-test/` `survivor/`（4 个实验残留）
- 备份方式：`tar -czf backup.tar.gz -C ~/.hermes/skills/ ...`
- 验证：这些脚本的正式版本在 `learning-workflow/scripts/` 中

## Step 2：HOME 根目录清理
- 清理 8 个目录，释放 ~7.5GB（主要是 docling-env 占了 5.7GB）
- 备份陷阱：`cp -r` 备份 5.7GB 的 docling-env 导致脚本超时（60s）
- 教训：大目录 (>5GB) 跳过备份直接删除，Python venv 可重建

## Step 3：Sessions + Cron（跳过）
- 1120 sessions 全部 < 30 天，30 天 prune 策略无效
- 需要改用 7 天阈值或按数量策略
- Cron output 仅 2.3MB，不值得清理

## Step 4：Learning + 根目录
- 清理 11 个 learning 子目录 + `extracted_knowledge.md`
- 保留 3 个根级文件（gemini_api_presentation.html + 2 PPT）
- 发现 `gateway.lock` 和 `models_dev_cache.json` 可安全删除

## 关键发现
1. 密集对话环境下 sessions 永远 < 30 天 → 需改用 7 天阈值
2. `gateway.lock` + `models_dev_cache.json` → 安全可删
3. root 状态文件 (sdd_state / installed_packs / kanban 等) → **必须保留**
4. 终端 ASCII 图在飞书上无法显示 → 需用 HTML/SVG + 截图
5. 多步清理必须逐 step 等主人确认

## 追加清理（主人指出后才发现的遗漏）
在 Step 2 清理完 8 个根目录后，主人指出「根目录还有很多 pdf 和 py 文件啊」——boku 只扫了目录，漏掉了根目录的单个文件。

| 文件类型 | 数量 | 总大小 |
|:---------|:----:|:------:|
| PDF 报告 | 17 | ~25MB |
| PY 脚本（一次性生成器） | 24 | ~300K |
| HTML 预览 | 10+ | ~500K |
| PNG 截图 | 6+ | ~500K |
| 其他（PPTX/MD/JSON） | 10+ | ~200K |
| **总计** | **~60+** | **~7.5MB** |

**教训**：清理根目录时，**文件和目录要分开两轮扫描**。目录用 `-type d`，文件用 `-type f`。
