---
name: readme-for-ai
description: 编写模型友好型 README 的方法论。让 AI Agent 在阅读 README 后能自主完成安装、配置、运行全流程。
version: 1.1.0
triggers:
- 写 README
- 模型友好
- AI 自主安装
- readme for AI
- 自述文件
- 文档编写
author: Emma (小喵)
license: MIT
metadata:
  hermes:
    tags:
    - documentation
    - readme
    - ai-friendly
    - autonomous-setup
    category: documentation
    skill_type: methodology
    design_pattern: template
---

# README for AI — 模型友好型 README 编写指南

> 让 AI Agent 在阅读 README 后能独立完成安装、配置、运行全流程。

## 核心理念

普通 README 写给人类看，模型友好型 README 写给 AI 看。

AI 和人类的阅读理解方式不同：
- 人类靠扫读，AI 靠关键词匹配
- 人类能脑补缺失步骤，AI 需要每一步都有命令
- 人类能自己查资料，AI 需要 FAQ 给出恢复路径

## 七大原则（v1.1 新增第 7 条）

### 1. 每步必有验证

每个操作步骤后面跟一个验证命令，让 AI 能 self-check。

```
# 普通写法：只有安装
pip install sra-agent

# 模型友好：安装 + 验证
pip install sra-agent
sra version    # 验证安装成功
```

### 2. 命令带预期输出

每个命令附带预期输出格式描述，让 AI 能判断执行结果。

```
sra recommend 画架构图
# 预期输出包含: -> 推荐技能、得分、置信度
```

### 3. 多路径安装

提供多种安装方式供 AI 按环境选择：
- 方式一：PyPI 安装（推荐，最简洁）
- 方式二：源码安装（需要 git）
- 方式三：一键脚本（需要 curl）

### 4. 前置条件明确

列出所有前置依赖和检测命令。

### 5. FAQ 即恢复路径

每个 FAQ 问题配排查步骤和命令。

### 6. 配置可脚本化

配置项可通过 CLI 修改，不需手改文件。

### 7. 🆕 安装脚本自动探测系统，生成配置而非要求手动放置

这是本次新增的核心原则。它的出发点是：

> **AI Agent 无法执行「请手动复制文件到 XX 目录」这样的步骤。所有系统配置必须由安装脚本自动生成。**

**常见反模式（❌ 不要这样做）：**
```bash
# README 中说：
cp srad.service ~/.config/systemd/user/
systemctl --user enable srad
```
AI Agent 读到这种指令会遇到问题：它不知道 `~` 展开后是什么路径，不知道目标目录是否存在，不知道文件权限是否正确。

**正确模式（✅ 应该这样做）：**
```bash
# install.sh 内部：
detect_os           # uname -s → linux/darwin/other
detect_init         # /run/systemd/system → systemd/launchd/other
check_sudo          # sudo -n true → true/false
check_hermes        # command -v hermes → true/false

case "$OS-$INIT" in
  linux-systemd)
    if $SUDO; then
      生成 /etc/systemd/system/xxx.service
    else
      生成 ~/.config/systemd/user/xxx.service
    fi
    ;;
  darwin-launchd)
    生成 ~/Library/LaunchAgents/com.xxx.plist
    ;;
  *)
    生成入口脚本 + 引导提示
    ;;
esac
```

**核心理念：不要「移植文件」，要「脚本生成」。**
- ❌ 把 systemd 文件作为静态文件放入仓库 → AI 不知道放哪
- ✅ 安装脚本检测系统 → 自动生成适配配置 → 自动启用

详细设计模式参见 `references/cross-platform-install-pattern.md`

## README 结构

1. 项目简介 + Badges
2. 目录（快速定位）
3. 为什么需要？（判断是否适用）
4. 核心能力（表格）
5. 架构
6. 安装（含验证）
7. 快速开始（三步走）
8. 命令大全（表格）
9. API 文档（含示例）
10. SDK 使用（代码示例）
11. 配置（可脚本修改）
12. 基准测试
13. FAQ（含恢复命令）
14. 开发指南

## 自检流程

AI 遇到问题时按以下顺序排查：
1. 命令找不到 -> 检查安装是否成功
2. 连接超时 -> 检查代理
3. 配置文件缺失 -> 检查默认路径
4. 认证失败 -> 检查 token
5. 版本问题 -> 检查 Python 版本
