# project-state.py 脚本位置

本技能的主要管理脚本 `project-state.py` 已在 cap-pack 项目中实现。
路径: `/home/ubuntu/projects/hermes-cap-pack/scripts/project-state.py`

## 在新项目中使用

1. 复制此技能中的 `templates/project-state.yaml` 到新项目的 `docs/` 目录
2. 从 cap-pack 项目复制脚本: `cp ~/projects/hermes-cap-pack/scripts/project-state.py <new-project>/scripts/`
3. 修改 `docs/project-state.yaml` 中的项目元数据
4. 运行 `python3 scripts/project-state.py sync && verify`

## 命令参考

```
status      — 全局状态概览
verify      — 一致性验证 (CI 门禁)
scan        — 检测漂移
sync        — 从文档同步状态
gate        — 门禁预检
transition  — 状态转换 + 门禁 + 日志
list        — 实体列表
history     — 变更审计日志
```
