---
name: web-ui
description: Hermes Agent Web UI Dashboard 管理指南。涵盖安装启动、配置管理、API Key 管理、会话浏览、Cron 任务、日志查看、数据分析、OAuth 认证、主题切换、插件扩展、安全加固等完整操作。
version: 1.0.0
triggers:
  - web dashboard
  - hermes web
  - web ui
  - dashboard
  - web管理
  - web面板
  - web server
  - fastapi web
  - hermes dashboard
  - 网页界面
  - web管理面板
depends_on: []
referenced_by:
  - self-capabilities-map
design_pattern: Tool Wrapper
skill_type: product-verification
---

# Hermes Web UI Dashboard

Hermes Agent 的 Web 管理面板，通过浏览器可视化管理配置、API Key、会话、Cron 任务、日志和分析数据。

**技术栈：** FastAPI (Python) + React 19 + TypeScript + Vite + Tailwind CSS v4

---

## 快速启动

```bash
# 安装依赖
pip install 'fastapi' 'uvicorn[standard]'

# 启动（自动构建前端）
hermes dashboard

# 默认访问 http://127.0.0.1:9119
```

### 常用启动参数

```bash
hermes dashboard --port 8080           # 自定义端口
hermes dashboard --no-open             # 不自动打开浏览器
hermes dashboard --host 0.0.0.0 --insecure  # 公网绑定（⚠️危险）
```

### 前端构建（首次或更新后）

```bash
cd ~/.hermes/hermes-agent/web
npm install
npm run build
```

---

## 核心功能

### 1. 系统状态 (Status)
- 版本号、配置路径、Gateway 状态
- 活跃会话数、配置版本检查
- 各平台连接状态（Telegram/Discord/Slack 等）

### 2. 配置管理 (Config)
- **表单模式**：按 Tab 分类编辑（general/agent/terminal/display/memory 等）
- **YAML 模式**：直接编辑原始 config.yaml 内容
- 支持的字段类型：string、number、boolean、select、list、object

### 3. 环境变量 (API Keys)
- 查看所有环境变量（默认脱敏）
- 添加/删除/编辑变量
- 安全查看明文（需认证 + 30s/5次限流）

### 4. 会话管理 (Sessions)
- 分页浏览历史会话
- FTS5 全文搜索（支持部分匹配和引号短语）
- 查看完整消息历史和工具调用记录
- 删除指定会话

### 5. 日志查看 (Logs)
- 按文件、级别、组件筛选
- 实时查看最近日志行

### 6. 数据分析 (Analytics)
- 每日 Token 消耗趋势图
- 按模型统计
- Skill 使用排行榜
- 总成本估算

### 7. Cron 任务
- 创建/编辑/删除定时任务
- 暂停/恢复/立即触发
- 查看运行状态和错误信息

### 8. 技能与工具集
- 查看和启用/禁用 Skills
- 查看 Toolsets 状态和包含的工具列表

### 9. OAuth 认证
- 查看 OAuth 提供者状态（Anthropic PKCE、Nous Device Code 等）
- 在浏览器中完成 OAuth 流程
- 断开已连接的提供者

### 10. 主题系统
6 种内置主题：
| 主题 | 描述 |
|------|------|
| default (Hermes Teal) | 经典深青色 |
| midnight | 深蓝紫罗兰 |
| ember | 暖红青铜色 |
| mono | 灰度极简 |
| cyberpunk | 霓虹绿黑 |
| rose | 柔和粉色 |

自定义主题放在 `~/.hermes/dashboard-themes/*.yaml`。

### 11. 插件系统
插件目录：`~/.hermes/plugins/<name>/dashboard/`
- 添加自定义 Tab 页
- 自定义 CSS
- 自定义后端 API 路由

---

## API 端点速查

### 公开端点（无需 Token）
| 端点 | 说明 |
|------|------|
| `GET /api/status` | 系统状态 |
| `GET /api/config/defaults` | 默认配置 |
| `GET /api/config/schema` | 配置 schema |
| `GET /api/model/info` | 模型信息 |
| `GET /api/dashboard/themes` | 主题列表 |
| `GET /api/dashboard/plugins` | 插件列表 |

### 认证端点（需 Bearer Token）
| 端点 | 说明 |
|------|------|
| `GET/PUT /api/config` | 读取/保存配置 |
| `GET/PUT /api/config/raw` | 原始 YAML |
| `GET/PUT/DELETE /api/env` | 环境变量 |
| `POST /api/env/reveal` | 查看明文（+ 限流） |
| `GET /api/sessions` | 会话列表 |
| `GET /api/sessions/search` | 全文搜索 |
| `GET /api/sessions/{id}/messages` | 会话消息 |
| `DELETE /api/sessions/{id}` | 删除会话 |
| `GET /api/logs` | 日志 |
| `GET /api/analytics/usage?days=N` | 分析 |
| `GET/POST /api/cron/jobs` | Cron 管理 |
| `GET /api/skills` | 技能列表 |
| `PUT /api/skills/toggle` | 切换技能 |
| `GET /api/tools/toolsets` | 工具集 |

### 认证方式
- Token 自动注入到 SPA HTML（`window.__HERMES_SESSION_TOKEN__`）
- 前端所有 API 请求自动携带 `Authorization: Bearer <token>`
- Token 每次服务器启动随机生成，进程退出后失效
- 使用 `hmac.compare_digest()` 防时序攻击

---

## 安全考虑

### ⚠️ 重要安全规则

1. **仅限本地访问**：默认绑定 127.0.0.1，CORS 限制 localhost
2. **禁止公网暴露**：`--host 0.0.0.0` 需要 `--insecure` 标志，有明确警告
3. **API Key 默认脱敏**：明文查看需额外认证 + 限流
4. **无持久化认证**：Token 仅存在于内存，重启后失效
5. **路径穿越防护**：静态文件和插件资源都检查路径合法性

### 🔒 远程访问方案

```bash
# 方案 1：SSH 隧道（推荐）
ssh -L 9119:127.0.0.1:9119 user@server
# 然后本地访问 http://127.0.0.1:9119

# 方案 2：Nginx 反向代理 + 额外认证
# 在 Nginx 层添加 Basic Auth 或 OAuth
```

### 🚫 不应做的

- ❌ 直接绑定 0.0.0.0 暴露在公网
- ❌ 使用无认证的反向代理
- ❌ 将 dashboard 作为多用户服务（无 RBAC）

---

## 与 CLI 对应关系

| Web UI | CLI 命令 |
|--------|----------|
| 状态面板 | `hermes status` |
| 配置编辑 | `hermes config edit` |
| 会话浏览 | `hermes sessions browse` |
| Cron 管理 | `hermes cron list/create` |
| 日志查看 | `hermes logs` |
| 使用分析 | `hermes insights` |
| 技能管理 | `hermes skills list` |
| 工具管理 | `hermes tools` |
| 认证管理 | `hermes auth add` |

---

## 故障排查

### 前端未构建
```
Error: Frontend not built. Run: cd web && npm run build
```
**解决：** `cd ~/.hermes/hermes-agent/web && npm install && npm run build`

### 依赖缺失
```
Web UI requires fastapi and uvicorn.
```
**解决：** `pip install 'fastapi' 'uvicorn[standard]'`

### 端口被占用
```
ERROR: [Errno 98] Address already in use
```
**解决：** `hermes dashboard --port 9120` 或 `lsof -i :9119` 查找占用进程

### CORS 错误
浏览器控制台报 CORS 错误 → 确认是从 localhost/127.0.0.1 访问，非远程 IP

### 主题不生效
- 检查 `~/.hermes/dashboard-themes/*.yaml` 格式是否正确
- 自定义主题需包含 `name` 字段

---

## 自定义主题示例

```yaml
# ~/.hermes/dashboard-themes/my-theme.yaml
name: my-theme
label: My Theme
description: Custom dashboard theme
# 颜色定义在前端 themes/presets.ts 中扩展
```

## 插件开发

```
~/.hermes/plugins/my-plugin/
├── dashboard/
│   ├── manifest.json     # 插件元数据
│   ├── dist/index.js     # 前端组件
│   ├── style.css         # 自定义样式
│   └── api.py            # 后端 API（可选，需暴露 router）
```

manifest.json 示例：
```json
{
  "name": "my-plugin",
  "label": "My Plugin",
  "description": "Custom dashboard extension",
  "icon": "Settings",
  "version": "1.0.0",
  "tab": { "path": "/my-plugin", "position": "end" },
  "entry": "dist/index.js",
  "api": "api.py"
}
```
