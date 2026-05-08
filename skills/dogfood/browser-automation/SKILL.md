---
name: browser-automation
description: Chrome headless 浏览器自动化实战技能。涵盖页面导航、表单填写、点击交互、快照分析、视觉截图、验证码识别等完整工作流。
version: 1.0.0
triggers:
- 浏览器
- 自动化
- chrome
- 网页交互
- screenshot
metadata:
  hermes:
    tags:
    - browser
    - chrome
    - automation
    - visual-analysis
    category: dogfood
    skill_type: library
    design_pattern: tool_wrapper
---
# 浏览器自动化技能 🌐🤖

## 一、环境状态

```
Chrome: google-chrome-stable 147.0.7727.137 (已安装)
启动: google-chrome --headless=new --no-sandbox --disable-gpu --remote-debugging-port=9222
CDP: http://localhost:9222
```

### 启动命令
```bash
google-chrome --headless=new --no-sandbox --disable-gpu \
  --remote-debugging-port=9222 \
  --disable-dev-shm-usage \
  --disable-software-rasterizer \
  --disable-extensions about:blank
```

---

## 二、工具链与使用顺序

### 标准工作流
```
1. browser_navigate(url)     → 导航到网页（返回 snapshot）
2. browser_snapshot()         → 刷新页面快照（获取 ref IDs）
3. browser_click(@eN)         → 点击元素
4. browser_type(@eN, text)    → 填写表单
5. browser_scroll(up/down)    → 滚动页面
6. browser_vision(question)   → 截图+AI视觉分析
7. browser_get_images()       → 获取页面所有图片
8. browser_console()          → 查看 JS 控制台输出
```

### 关键规则
- **navigate 后自动返回 snapshot**，不需要额外调用 snapshot
- **交互后（click/type）需要调用 snapshot 刷新**才能获取新页面元素
- **ref ID 格式**：`@e1`, `@e2` 等，来自 snapshot 中的 `[ref=eN]`
- **超时处理**：navigate 超时 60s，国内访问国外网站可能超时

---

## 三、实战场景

### 场景 1：页面信息提取
```
browser_navigate("https://example.com")
→ 拿到 snapshot，提取需要的文本和链接
→ 如果内容不全，browser_snapshot(full=true) 获取完整内容
```

### 场景 2：表单填写 + 搜索
```
browser_navigate("https://baidu.com")
→ 找到搜索框 ref (@e14)
→ browser_type("@e14", "搜索关键词")
→ browser_click("@e15")  # 点击搜索按钮
→ sleep 3 秒
→ browser_snapshot()  # 获取搜索结果
```

### 场景 3：视觉分析（复杂页面）
```
browser_navigate("https://36kr.com")
→ browser_vision("这个页面是什么？主要内容和布局？")
→ AI 返回截图分析结果
```

### 场景 4：验证码识别
```
browser_vision("这是什么类型的验证码？如何操作？")
→ AI 识别验证码类型（滑块、旋转、文字等）
→ 描述操作步骤
→ 注意：boku 无法自动拖动滑块，需要用户手动完成
```

### 场景 5：JS 错误检测
```
browser_console()  → 查看页面 JS 错误和 console.log
browser_console(expression="document.title")  → 执行 JS 表达式
```

---

## 四、常见问题与对策

| 问题 | 原因 | 对策 |
|:---|:---|:---|
| navigate 超时 60s | 国外网站被墙/无代理 | 走代理或换国内网站 |
| 验证码拦截 | 百度等网站反爬虫 | 用 vision 分析类型，手动处理 |
| snapshot 内容截断 | 页面太大（>8000字符） | 用 browser_snapshot(full=true) 或 browser_vision |
| ref ID 失效 | 页面刷新后元素变化 | 重新调用 snapshot 获取最新 ref |
| Chrome 未启动 | 进程未运行 | 先启动 headless Chrome |
| **browser_vision 挂死 8+ 分钟** | GeminiNativeClient 默认 read timeout=600s，per-request timeout=120s 未必正确覆盖 | ① 优先用国内可达的 vision provider（不走 google） ② 或修改 `gemini_native_adapter.py:834` 将 `read=600.0` 改为 `read=120.0` ③ 或配置 config.yaml `auxiliary.vision.provider` 为非 google 的 provider |

---

## 五、与 MCP 工具的配合

### 分层信息处理流程
```
1. MCP Search (tavily_search)    → 快速获取多个来源摘要
2. 评估哪些 URL 值得精读
3. MCP Extract (tavily_extract)  → 精读 1-2 篇最有价值的文章
4. Browser Navigate             → 需要交互时打开网页
5. Browser Vision               → 需要视觉理解时截图分析
```

### 选择原则
- **纯信息获取** → MCP Search（最快）
- **需要精读全文** → MCP Extract（次快）
- **需要交互操作** → Browser Navigate（最灵活）
- **需要视觉理解** → Browser Vision（唯一选择）

---

## 七、参考文档

- `references/gemini-vision-timeout-debug.md` — GeminiNativeClient vision 超时调试记录（国内环境 + 代理场景的挂死根因分析）

---

## 八、性能优化

- **Chrome 启动后保持运行**，不要每次导航都重启
- **优先用 snapshot 而非 vision**（snapshot 更快、无 token 消耗）
- **vision 仅在需要视觉理解时使用**（布局分析、验证码、图表）
- **大页面用 full=false**（默认），只在需要完整内容时用 full=true
