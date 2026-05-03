# 🐱 Hermes Catgirl Deploy

> 一键部署 Hermes AI Agent（猫娘女仆版本）到其他环境

## 📋 前置要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 核心运行环境 |
| Node.js | 22+ | 浏览器工具和 MCP |
| Git | 最新 | 克隆核心代码 |
| uv | 最新 | Python 包管理器（推荐） |

## 🚀 快速部署

### 方式一：一键部署脚本

```bash
# 克隆本仓库
git clone https://github.com/YOUR_USERNAME/hermes-catgirl-deploy.git
cd hermes-catgirl-deploy

# 运行部署脚本
chmod +x deploy.sh
./deploy.sh
```

### 方式二：手动部署

#### 1. 获取 Hermes 核心代码

```bash
# 创建目录
mkdir -p ~/.hermes

# 克隆核心代码
git clone https://github.com/NousResearch/hermes-agent.git ~/.hermes/hermes-agent
cd ~/.hermes/hermes-agent
```

#### 2. 安装依赖

```bash
# 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 Python 依赖
uv sync

# 安装 Node.js 依赖（可选，用于浏览器工具）
npm install
```

#### 3. 配置

```bash
# 复制配置模板
cp config/config.yaml.example ~/.hermes/config.yaml
cp config/.env.example ~/.hermes/.env

# 编辑配置（填入你的 API Key）
nano ~/.hermes/.env
nano ~/.hermes/config.yaml
```

#### 4. 安装自定义 Skills

```bash
# 复制 skills 到 hermes-agent 内置目录
cp -r skills/* ~/.hermes/hermes-agent/skills/

# 或者放到外部目录（需要在 config.yaml 中配置 skills.external_dirs）
cp -r skills/* ~/.hermes/skills/
```

#### 5. 安装中文字体（可选，用于 PPT/PDF 生成）

```bash
# Ubuntu/Debian
sudo apt install -y fonts-wqy-microhei fonts-noto-cjk

# CentOS/RHEL
sudo yum install -y wqy-microhei-fonts google-noto-cjk-fonts
```

#### 6. 启动

```bash
# 方式一：使用 uv
cd ~/.hermes/hermes-agent
uv run hermes

# 方式二：激活虚拟环境
cd ~/.hermes/hermes-agent
source .venv/bin/activate
hermes
```

## 📁 仓库结构

```
hermes-catgirl-deploy/
├── README.md                     # 本文件
├── LICENSE                       # MIT License
├── .gitignore                    # Git 排除规则
├── deploy.sh                     # 一键部署脚本
├── config/
│   ├── .env.example              # 环境变量模板
│   └── config.yaml.example       # 配置文件模板
├── skills/
│   ├── doc-design/               # 文档排版设计 Skill（v3.0.0）
│   │   ├── SKILL.md
│   │   └── references/           # 13 个参考文档
│   ├── web-access/               # 网页访问 Skill（v4.0.0）
│   │   ├── SKILL.md
│   │   ├── scripts/              # CDP 代理等
│   │   └── references/
│   └── yuanbao/                  # 元宝群交互 Skill
│       └── SKILL.md
└── scripts/
    └── setup-chrome.sh           # Chrome 浏览器安装脚本
```

## 🔑 必须配置的 API Key

| Key | 用途 | 获取地址 |
|-----|------|----------|
| `OPENROUTER_API_KEY` 或自定义 Provider | LLM 模型调用 | https://openrouter.ai/keys |
| `FEISHU_APP_ID` + `FEISHU_APP_SECRET` | 飞书机器人 | https://open.feishu.cn/ |
| `TAVILY_API_KEY` | AI 搜索（可选） | https://tavily.com/ |

## 🎨 自定义 Skills 说明

### doc-design（文档排版设计）
- **版本**：v3.0.0
- **功能**：Word/Excel/PPT/PDF/EPUB/HTML/LaTeX 文档生成与排版
- **升级内容**：Pipeline 进度追踪 + 评估体系 + 设计模式映射（基于 skill-creator v10.1.0）

### web-access（网页访问）
- **版本**：v4.0.0-hermes
- **功能**：基于 CDP 代理的浏览器自动化，支持搜索、抓取、登录后操作
- **升级内容**：Pipeline 进度追踪 + 评估体系 + 站点模式积累

## 🔄 更新

```bash
# 拉取最新配置
git pull origin main

# 更新核心代码
cd ~/.hermes/hermes-agent
git pull origin main
uv sync

# 更新 Skills
cp -r skills/* ~/.hermes/hermes-agent/skills/
```

## ⚠️ 注意事项

1. **永远不要提交 `.env` 文件到 Git** — 包含 API Key 等敏感信息
2. **永远不要提交 `config.yaml`** — 如果包含真实密钥
3. **hermes-agent 核心代码** 通过 `git clone https://github.com/NousResearch/hermes-agent.git` 获取，不包含在本仓库中（~729MB）
4. **会话记录和状态数据库** 不包含在仓库中（隐私 + 体积）

## 📄 License

MIT License — 自由使用和修改
