# 四种工作流集成 unified-state-machine 指南

## sdd-workflow
每次 spec-state.py 的变更命令前：`project-state.py verify`
每次变更命令后：`project-state.py sync`
铁律 #8 已加入 SKILL.md

## generic-dev-workflow
Step 7.4 项目状态同步：sync + verify
铁律 #6 已加入 SKILL.md

## generic-qa-workflow
L4 发布门禁 Step 5：project-state.py verify（exit 1 阻断）

## project-startup-workflow
Phase 4.5 状态机初始化：复制模板 → sync → verify
