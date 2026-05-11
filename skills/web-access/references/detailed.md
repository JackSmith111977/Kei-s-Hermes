# Detailed Reference

## 三、启动流程（Step by Step）

### Step 1: 前置检查

```bash
node "${HERMES_SKILL_DIR}/scripts/check-deps.mjs"
```

输出示例：
```
node: ok (v22.22.2)
chrome: ok (port 9222)
proxy: ready
```

### Step 2: 如 Chrome 未运行

```bash
# 启动虚拟显示
Xvfb :99 -screen 0 1280x1024x24 -ac &
sleep 2

# 启动 Chrome
DISPLAY=:99 google-chrome \
  --no-first-run \
  --no-default-browser-check \
  --disable-gpu \
  --remote-debugging-port=9222 \
  --remote-debugging-address=127.0.0.1 \
  --disable-dev-shm-usage \
  --headless=new \
  --disable-extensions \
  --disable-background-networking \
  --user-data-dir=/tmp/chrome-debug \
  about:blank &
sleep 3

# 验证
curl -s http://127.0.0.1:9222/json/version
```

### Step 3: 如 Proxy 未运行

check-deps 会自动启动。手动启动：

```bash
node "${HERMES_SKILL_DIR}/scripts/cdp-proxy.mjs" &
sleep 2
```

### Step 4: 展示风险提示

检查通过后，**必须**向用户展示：

```
⚠️ 温馨提示：部分站点对浏览器自动化操作检测严格，存在账号封禁风险。
已内置防护措施但无法完全避免，继续操作即视为接受。
```

---

## 四、CDP Proxy API 速查

> 完整参考见 `references/cdp-api.md`

### 核心操作

```bash
# 1. 创建新后台 tab（自动等待加载）
TARGET=$(curl -s "http://localhost:3456/new?url=https://example.com" | jq -r '.targetId')

# 2. 获取页面信息
curl -s "http://localhost:3456/info?target=$TARGET" | jq .

# 3. 执行 JS
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d 'document.title'

# 4. 点击元素
curl -s -X POST "http://localhost:3456/click?target=$TARGET" -d 'button.submit'

# 5. 截图
curl -s "http://localhost:3456/screenshot?target=$TARGET&file=/tmp/shot.png"

# 6. 滚动
curl -s "http://localhost:3456/scroll?target=$TARGET&direction=bottom"

# 7. 关闭 tab
curl -s "http://localhost:3456/close?target=$TARGET"
```

### 完整 API 列表

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/targets` | 列出所有 tab |
| GET | `/new?url=` | 创建新 tab |
| GET | `/close?target=` | 关闭 tab |
| GET | `/navigate?target=&url=` | 导航 |
| GET | `/back?target=` | 后退 |
| GET | `/info?target=` | 页面信息 |
| POST | `/eval?target=` | 执行 JS |
| POST | `/click?target=` | JS 点击 |
| POST | `/clickAt?target=` | 真实鼠标坐标点击 |
| POST | `/setFiles?target=` | 文件上传 |
| GET | `/scroll?target=&direction=` | 滚动 |
| GET | `/screenshot?target=&file=` | 截图 |

---

## 五、浏览哲学

**像人一样思考，兼顾高效与适应性。**

1. **拿到请求** — 先明确用户要做什么，定义成功标准
2. **选择起点** — 根据任务性质选最可能直达的方式
3. **过程校验** — 每一步的结果都是证据，方向错了立即调整
4. **完成判断** — 确认任务完成后才停止

---

## 六、常见任务模式

### 模式 A：简单页面抓取

```bash
TARGET=$(curl -s "http://localhost:3456/new?url=https://example.com" | jq -r '.targetId')
sleep 2
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d 'document.body.innerText'
curl -s "http://localhost:3456/close?target=$TARGET"
```

### 模式 B：提取图片 URL

```bash
# 获取所有图片
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d \
  'JSON.stringify(Array.from(document.querySelectorAll("img")).map(i => ({src: i.src, alt: i.alt})))'
```

### 模式 C：表单填写与提交

```bash
# 填写输入框
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d \
  'document.querySelector("#username").value = "myuser"'
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d \
  'document.querySelector("#password").value = "mypass"'
# 点击提交
curl -s -X POST "http://localhost:3456/click?target=$TARGET" -d 'button[type="submit"]'
```

### 模式 D：无限滚动页面

```bash
# 滚动到底部触发懒加载
curl -s "http://localhost:3456/scroll?target=$TARGET&direction=bottom"
sleep 2
# 检查高度变化
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d 'document.body.scrollHeight'
```

### 模式 E：登录检测

```bash
# 检查是否存在登录表单
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d \
  'document.querySelector("input[type=password]") ? "需要登录" : "无需登录"'
```

---

## 七、Red Flags（常见错误与陷阱）

### ❌ 连接错误
- **CDP Proxy 连接超时** → Chrome 147 headless 需要从 `/json/version` 获取 UUID 路径，已修复
- **WebSocket 失败** → 使用 `ws` 模块而非 Node.js 22 原生 WebSocket
- **端口占用** → 检查 `lsof -i :3456` 和 `lsof -i :9222`

### ❌ 操作错误
- **选择器不匹配** → 先用 `/eval` 检查 DOM 结构，不要套用固定模板
- **页面未加载完就操作** → `/new` 和 `/navigate` 会自动等待，但复杂页面需额外 `sleep`
- **忘记关闭 tab** → 任务结束必须 `/close`，避免内存泄漏
- **混淆 `/click` 和 `/clickAt`** → 普通按钮用 `/click`，文件上传/反自动化场景用 `/clickAt`

### ❌ 安全错误
- **未展示风险提示就开始操作** → 必须在操作前告知用户
- **在用户原有 tab 中操作** → 始终在 `/new` 创建的后台 tab 中操作
- **硬编码凭证** → 不要在脚本中硬编码账号密码

---

## 八、验证清单

每次联网任务完成后检查：

- [ ] check-deps 全部通过（node ok, chrome ok, proxy ready）
- [ ] 已向用户展示风险提示
- [ ] 所有 tab 已关闭（`curl /targets` 确认无残留）
- [ ] 获取的内容满足用户需求
- [ ] 无敏感信息泄露

---

## 九、任务结束清理

```bash
# 查看当前所有 tab
curl -s http://localhost:3456/targets | jq .

# 关闭所有自己创建的 tab（逐个关闭）
curl -s "http://localhost:3456/close?target=TARGET_ID"

# ⚠️ 不要关闭用户原有的 tab！
# ⚠️ 不要停止 Proxy（重启需要 Chrome 重新授权）
```

---

## 十、References 索引

| 文件 | 何时加载 |
|------|----------|
| `references/cdp-api.md` | 需要 CDP API 详细参考、JS 提取模式、错误处理时 |
| `references/site-patterns/{domain}.md` | 确定目标网站后，读取对应站点经验 |

### 站点经验

操作中积累的特定网站经验，按域名存储在 `references/site-patterns/` 下。

确定目标网站后，如果 site-patterns 列表中有匹配的站点，**必须**读取对应文件获取先验知识。

---

## 十一、设计模式映射（skill-creator v10.1.0）

> 基于 skill-creator 5 种设计模式，根据任务类型选择最优模式

### 模式选择决策树

```
联网任务
├─ 只需要搜索/摘要？ → Tool Wrapper 模式（Tavily Search，按需注入）
├─ 有固定抓取模板？ → Generator 模式（站点模板驱动，95% 确定性）
├─ 需要验证页面质量？ → Reviewer 模式（加载→验证→报告）
├─ 目标不明确/需要探索？ → Inversion 模式（先调研再行动）
└─ 多步骤复杂抓取？ → Pipeline 模式（强制顺序，遗漏率 90%→5%）
```

### 📦 Tool Wrapper 模式
- **适用场景**：简单搜索、已知 URL 抓取
- **Token 优化**：只加载需要的 API 文档片段
- **工具选择**：Tavily Search（搜索）/ curl（静态）/ browser（动态）

### 🏭 Generator 模式
- **适用场景**：重复性抓取任务（定时监控、批量提取）
- **模板库**：`references/site-patterns/{domain}.md`
- **流程**：加载模板 → 填充参数 → 执行抓取 → 输出结果

### 🔍 Reviewer 模式
- **适用场景**：验证页面内容质量、检查抓取结果
- **流程**：加载内容 → 验证完整性 → 输出质量报告
- **评估维度**：内容完整性、格式正确性、时效性

### 🎤 Inversion 模式
- **适用场景**：目标网站未知、需要探索性抓取
- **流程**：先调研网站结构 → 确认抓取策略 → 再执行
- **效果**：避免盲目抓取导致的返工

### 🔄 Pipeline 模式
- **适用场景**：复杂多步骤抓取（登录→导航→提取→清洗→存储）
- **流程**：
  ```
  Stage 1: 前置检查（check-deps）
  Stage 2: 环境启动（Chrome + Proxy）
  Stage 3: 导航目标（new/navigate）
  Stage 4: 内容提取（eval/截图）
  Stage 5: 数据清洗（格式化/去重）
  Stage 6: 验证交付（完整性检查）
  Stage 7: 清理收尾（close tabs）
  ```

---

## 十二、评估体系（Stage 9）

> 基于 skill-creator Stage9 评估设计，确保抓取质量

### 评估维度

| 维度 | 权重 | 关键检查点 |
|------|------|-----------|
| E1 内容完整性 | 30% | 目标信息全部获取、无遗漏 |
| E2 格式正确性 | 20% | 编码正确、无乱码、结构完整 |
| E3 时效性 | 20% | 内容是最新的、无过期数据 |
| E4 操作安全性 | 15% | 无账号风险、已展示提示 |
| E5 资源清理 | 15% | 所有 tab 已关闭、无残留进程 |

### Grader 等级

| 总分 | 等级 | 行动 |
|------|------|------|
| ≥ 0.90 | ✅ PASS | 直接交付 |
| 0.75-0.89 | ⚠️ WARN | 补充抓取后交付 |
| 0.60-0.74 | ❌ FAIL | 重新抓取 |
| < 0.60 | 🚨 CRITICAL | 更换策略重试 |

### 站点模式积累

每次成功抓取后，将经验写入 `references/site-patterns/{domain}.md`：

```markdown
# {domain} 抓取经验

## 最后验证：YYYY-MM-DD
## 状态：✅ 可用 / ⚠️ 部分可用 / ❌ 失效

## 登录方式
- 无 / 账号密码 / OAuth / Cookie

## 关键选择器
- 内容区域：`.content-main`
- 标题：`h1.article-title`
- 正文：`.article-body`

## 反爬措施
- 无 / Cloudflare / 验证码 / IP 限制

## 注意事项
- 需要等待 JS 渲染（sleep 3s）
- 内容在 iframe 中
- 需要滚动加载

## 示例代码
（保存成功的抓取代码片段）
```
