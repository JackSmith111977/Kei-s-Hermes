---
name: sra-cli-usage
description: SRA (Skill Runtime Advisor) CLI 正确用法指南。替代 curl|python3 管道的安全方案，避免 security warning。
version: 1.0.0
triggers:
- sra
- sra 推荐
- sra 查询
- skill runtime advisor
- 技能推荐
author: boku
license: MIT
allowed-tools:
- terminal
metadata:
  hermes:
    tags:
    - sra
    - cli
    - security
    - best-practice
    category: developer-workflow
    skill_type: tool-wrapper
    design_pattern: tool-wrapper
---

# SRA CLI 使用指南

> **核心原则**：永远用 `sra` CLI 替代 `curl | python3` 管道。
> CLI 输出格式友好、无安全警告、无需额外解析。

## 安装

```bash
# 从源码安装
cd ~/projects/sra
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 或从 PyPI
pip install sra-agent
```

## 常用命令

### 技能推荐（替代 curl POST /recommend）

```bash
# ✅ 正确做法 — 直接 CLI
sra recommend "生成PDF文档"

# ❌ 错误做法 — 触发 security warning
curl -s http://127.0.0.1:8536/recommend -X POST ... | python3 -c "..."
```

### 指定 CLI 路径

如果 `sra` 不在 PATH 中，用完整路径：

```bash
~/projects/sra/venv/bin/sra recommend "查询内容"
```

### 索引管理

```bash
sra refresh          # 刷新技能索引（替代 curl POST /refresh）
sra stats            # 查看运行统计（替代 curl GET /health）
sra coverage         # 分析技能识别覆盖率
```

### 守护进程管理

```bash
sra start            # 启动后台守护进程
sra stop             # 停止
sra status           # 查看状态
sra restart          # 重启
```

## 输出解读

```
🔍 查询: '生成PDF文档'
⚡ 39.0ms | 📊 350 skills

🎯 推荐技能:
  💡 pdf-layout (得分: 72.2)
     📄 描述内容...
     💬 name匹配'pdf-layout'; tag'reportlab'
```

关键字段：
- `💡 技能名称 (得分: XX.X)` — 匹配度分数（0-100）
- `📄` — 技能描述
- `💬` — 匹配原因

## 注意事项

| 场景 | CLI | curl | 推荐 |
|:-----|:---|:-----|:----:|
| 查询推荐 | `sra recommend "查询"` | `curl POST /recommend` | ✅ CLI |
| 刷新索引 | `sra refresh` | `curl POST /refresh` | ✅ CLI |
| 查看状态 | `sra stats` | `curl GET /health` | ✅ CLI |
| 需要 JSON 输出 | `sra recommend "查询" --json` | curl + python3 解析 | ✅ CLI --json |
| 编程调用 | `subprocess.run(["sra", "recommend", q])` | `requests.post()` | ✅ subprocess |

## 设计原理

SRA CLI 的设计遵循 **「自带安全」** 原则：
- CLI 命令不需要 pipe-to-interpreter，不会被 Hermes 安全扫描器标记
- 输出已经是格式化文本，无需额外解析
- 所有命令在 `terminal` 工具中可直接执行
