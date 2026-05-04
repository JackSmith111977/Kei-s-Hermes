---
name: readme-for-ai
description: 编写模型友好型 README 的方法论。让 AI Agent 在阅读 README 后能自主完成安装、配置、运行全流程。
version: 1.0.0
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

## 六大原则

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
