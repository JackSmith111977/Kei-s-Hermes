---
name: hermes-ops-tips
description: "Hermes 运维与工具流最佳实践。包含 SRA Proxy 修复记录、高清架构图生成工作流 (SVG + cairosvg)、以及 Memory 满时的降级策略。"
triggers: [高清截图, cairosvg, sra proxy bug, 架构图, memory full, hermes运维]
---

# Hermes Ops & Workflow Tips

## 1. 高清架构图生成工作流
**问题**: `browser_vision` 截图会被压缩，导致文字模糊。
**解决方案**:
1.  使用 SVG 矢量图定义结构 (无限清晰)。
2.  使用 `cairosvg` (Python) 将 SVG 渲染为高分辨率 PNG。
    *   命令: `cairosvg input.svg -o output.png --output-width 3600`
    *   环境依赖: `sudo apt install libcairo2-dev` + `pip install cairosvg`.

## 2. SRA Proxy Bug 修复记录
**现象**: `sra start` 输出显示端口 8532，但实际服务在 8536。
**原因**: `daemon.py` 中 `cmd_start` 和 `cmd_status` 硬编码了 8532。
**修复**: 修改 `daemon.py` 读取 `load_config()` 获取 `http_port`。
**仓库**: `https://github.com/JackSmith111977/Hermes-Skill-View.git`

## 3. Memory 溢出降级策略
当 Memory 达到上限 (约 2200 chars) 无法写入时：
1.  优先替换过时的长条目 (如旧的学习记录)。
2.  若无法替换，将学习成果/报告保存为本地 Markdown 文件 (`~/.hermes/docs/`)。
3.  在 Memory 中记录文件路径作为索引。

## 4. SRA Skill 推荐优化
**现象**: 通用动词 (如"学习") 在 SRA 中分数低。
**对策**: 优化 Skill 的 `description` 和 `triggers`。增加用户视角的自然语言描述 (如 "当你需要搞懂/学习...时使用")，避免纯内部视角的术语。