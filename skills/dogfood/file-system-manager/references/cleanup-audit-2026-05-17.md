# 2026-05-17 全量清理审计记录

## 清理范围
- HOME 根目录：8 个杂乱目录 + 60+ 散乱文件（17 PDF + 24 PY + 20+ HTML/MD/PNG）
- Skill 测试残留：4 个废弃目录（bak-test/remove-test/multi-hermes-test/survivor）
- Learning 历史产物：11 个子目录全部清除
- Cron output：427 文件清空
- 系统缓存：gateway.lock + models_dev_cache.json
- 所有备份文件：disk-cleanup/ 目录清空

## 磁盘变化
- 清理前：76%（36/50GB）
- 清理后：64%（30/50GB）
- 释放：~6GB

## 关键发现

### 1. disk-cleanup 插件已启用但从未实际运行
- config.yaml 中 `plugins.enabled: [disk-cleanup]` ✅
- 但 `~/.hermes/disk-cleanup/` 目录不存在（状态文件从未创建）
- 源码确认：`post_tool_call` + `on_session_end` hooks 逻辑正确
- 需要第一次触发来创建 tracked.json

### 2. Sessions 清理陷阱
- hermes sessions prune --older-than 30 ：所有 1120 个 session 都 <30 天，无效
- 源码确认（hermes_state.py:1264）：prune 只删 SQLite 记录，不删 JSON 文件
- GitHub Issue #3015 已报告此 bug
- Workaround：`find ~/.hermes/sessions/ -name '*.json' -mtime +30 -delete`

### 3. 学习脚本被覆盖为桩文件（<100 bytes）
- learning-state.py（707行→5行）、skill_finder.py、reflection-gate.py 均被破坏
- 从 `~/.hermes/profiles/experiment/skills/learning-workflow/scripts/` 恢复

### 4. Skill 结构审计
- 84 个 skill 中仅 34% 有 references/，20% 有 scripts/
- 20 个（24%）只有单文件 SKILL.md
- SQS 评分系统有效但手动运行

## 教训
1. 只扫目录不扫文件 → 漏扫 60+ 散乱文件
2. 备份大文件会超时 → 5.7GB cp -r 导致整个脚本中断
3. 插件 enabled ≠ 插件在运行 → 必须检查状态目录是否存在
