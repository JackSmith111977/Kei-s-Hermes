---
name: news-briefing
description: 新闻采集与报刊级别简报生成技能。涵盖 RSS/API 采集管线、新闻分类筛选去重、AI 辅助摘要、以及使用 WeasyPrint 生成专业报刊级 PDF 文档（4+页，网格系统+视觉层次+多栏布局）。
version: 2.1.0
triggers:
- 新闻采集
- 新闻简报
- news briefing
- 报刊
- 报纸
- 日报
- 周报
- 看新闻
- 新闻汇总
depends_on:
- web-access
- pdf-layout-weasyprint
allowed-tools:
- terminal
- read_file
- write_file
- patch
- mcp_tavily_tavily_search
- mcp_tavily_tavily_extract
metadata:
  hermes:
    tags:
    - news
    - briefing
    - rss
    - aggregation
    - newspaper
    - layout
    - weasyprint
    - pdf
    category: research
    skill_type: doc-generation
    design_pattern: generator
---
# 新闻采集与报刊简报生成技能 v2.0 📰

> 从新闻采集到报刊级 PDF 输出的完整工作流（经过系统性学习提炼）

## 触发条件

**使用此 skill 当：**
- 用户需要采集、整理、汇报今日/本周/特定时间段新闻
- 用户需要生成报刊级别（4+页）的新闻简报文档
- 用户需要 RSS/API 新闻源聚合和分类
- 用户需要 AI 辅助新闻摘要和去重
- 用户要求定时生成新闻简报

---

## 一、新闻采集工作流（Pipeline）

### 1.1 完整管线架构
```
RSS/API 源 → 采集(fetch) → 去重(dedup) → 分类(classify) → 摘要(summarize) → 排序(rank) → 排版(template) → PDF(weasyprint)
```

### 1.2 新闻源定义

```python
# 推荐新闻源（按类别）
NEWS_SOURCES = {
    'international': [
        ('Reuters', 'https://feeds.reuters.com/reuters/topNews'),
        ('BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
        ('AP News', 'https://rsshub.app/apnews/topics/headlines'),
    ],
    'china': [
        ('新华网', 'https://rsshub.app/xinhua/app'),
        ('央视新闻', 'https://rsshub.app/cctv/top_news'),
        ('澎湃新闻', 'https://rsshub.app/thepaper/channel/25950'),
    ],
    'tech': [
        ('TechCrunch', 'https://techcrunch.com/feed/'),
        ('The Verge', 'https://www.theverge.com/rss/index.xml'),
        ('36Kr', 'https://rsshub.app/36kr/news/latest'),
    ],
    'finance': [
        ('Bloomberg', 'https://feeds.bloomberg.com/markets/news.rss'),
        ('财新网', 'https://rsshub.app/caixin/finance'),
    ],
    'sports': [
        ('新浪体育', 'https://rsshub.app/sina/sports'),
    ],
}
```

### 1.3 采集策略（按优先级分级）

| 级别 | 来源 | 轮询间隔 | 说明 |
|------|------|---------|------|
| Tier 1 | 主流新闻源 | 1-2 分钟 | BBC、Reuters、新华社 |
| Tier 2 | 中型/区域性 | 5 分钟 | 澎湃新闻、TechCrunch |
| Tier 3 | 小众/低频 | 10-15 分钟 | 个人博客、专业论坛 |

> **注意**：在 Hermes 环境中，使用 `mcp_tavily_tavily_search` 进行实时搜索更高效，无需自建 RSS 轮询。

### 1.4 搜索策略

```python
# 多维搜索确保覆盖
SEARCH_QUERIES = [
    "2026年5月4日 今日新闻 重要新闻 头条",           # 综合新闻
    "2026年5月4日 科技 AI 互联网 芯片 企业",          # 科技
    "2026年5月4日 体育 娱乐 文化 生活 社会新闻",      # 社会
    "2026年5月4日 国际新闻 欧洲 乌克兰 中东",          # 国际
]
```

### 1.5 去重与分类

```python
import hashlib

def deduplicate(articles, window_hours=4):
    """按标题哈希去重"""
    seen = set()
    unique = []
    for a in articles:
        key = hashlib.md5(a['title'].encode('utf-8')).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique

def classify_article(title, summary=''):
    """基于关键词的新闻分类"""
    text = (title + ' ' + summary).lower()
    CATEGORIES = {
        'international': ['战争', '停火', '制裁', 'election', 'war', '中东', '俄乌', '伊朗'],
        'china': ['中国', '习近平', '央视', '新华社', '两会', '政策'],
        'tech': ['AI', '芯片', '科技', '互联网', '手机', '发布', 'AI', '芯片'],
        'finance': ['股市', '财报', '经济', 'GDP', '央行', '利率', '原油'],
        'sports': ['冠军', '比赛', '进球', '夺冠', '奥运', '世界杯'],
        'entertainment': ['电影', '票房', '演唱会', '明星', '综艺'],
    }
    for cat, keywords in CATEGORIES.items():
        if any(kw in text for kw in keywords):
            return cat
    return 'general'
```

---

## 二、报刊级排版设计

### 2.1 核心设计原则

| 原则 | 说明 |
|------|------|
| **网格系统** | 所有元素对齐到网格，创造秩序感 |
| **视觉层次** | 报头(38pt) > 头条(24pt) > 栏目(13pt) > 正文(9.5pt) |
| **模块化** | 每篇文章占据矩形区域，不交叉不重叠 |
| **主导元素** | 每页一个主视觉（大图或大标题） |
| **Lazy S 扫描** | 读者视线呈懒S形，左上角最先被看到 |
| **内容密度** | 一页塞满，信息密集，像真正的报纸（用户偏好高密度排版） |

### 2.2 字体层级规范

| 层级 | 字号 | 用途 |
|------|------|------|
| 报头/刊名 | 36-38pt | 文档名称，letter-spacing 12px |
| 头条标题 | 22-24pt | 最重要的新闻 |
| 栏目标题 | 12-14pt | 分类标题，border-left 装饰 |
| 文章标题 | 11-12pt | 单篇文章标题 |
| 正文 | 9-10.5pt | 正文内容，line-height 1.6-1.7 |
| 元信息 | 7.5-8pt | 来源、日期、页码 |

### 2.3 配色方案（报纸风格）

```python
COLORS = {
    'bg': '#ffffff',          # 白色背景（干净现代）
    'ink': '#1a1a1a',         # 墨黑色正文
    'red': '#c41e3a',         # 头条红/分割线/标签
    'blue': '#1e3a5f',        # 栏目标题深蓝/数据条背景
    'gray': '#666666',        # 辅助文字
    'light_gray': '#e0dcd4',  # 分割线
    'accent': '#d4a017',      # 金色强调（点评区标题）
    'note_bg': '#fff8e1',     # 点评区背景
    'note_border': '#ffe082', # 点评区边框
    'data_bar': '#1e3a5f',    # 数据条背景
}
```

### 2.4 多页报刊结构

```
第 1 页 ── 封面/报头 + 头条 + 市场数据条 + 国际焦点（双栏）
第 2 页 ── 中美关系 + 国内要闻（双栏）+ 编辑点评
第 3 页 ── 科技财经（双栏）+ 数据表格 + 深度分析
第 4 页 ── 文体/社会新闻 + 一周回顾/数据汇总 + 页尾
```

---

## 三、WeasyPrint 技术要点

### 3.1 页面设置
```css
@page {
    size: A4;
    margin: 18mm 22mm 20mm 22mm;
    @top-left {
        content: "刊名";
        font-size: 9pt;
        color: #c41e3a;
        font-weight: bold;
    }
    @top-right {
        content: "日期";
        font-size: 9pt;
        color: #666;
    }
    @bottom-center {
        content: "— " counter(page) " / " counter(pages) " —";
        font-size: 8pt;
        color: #999;
    }
}
```

### 3.2 双栏布局
```css
/* ✅ 正确：使用 CSS columns */
.columns-2 {
    column-count: 2;
    column-gap: 24px;
    column-rule: 1px solid #e0dcd4;
}

/* ❌ 错误：不要用 flexbox 做多栏 */
/* flexbox 在多页时会断裂 */
```

### 3.3 分页控制
```css
.article {
    page-break-inside: avoid;  /* 防止文章被分页切断 */
    margin-bottom: 12px;
}
.section {
    page-break-inside: avoid;
}
```

### 3.4 中文字体
```python
# WeasyPrint 使用系统字体，确保安装中文字体
# Ubuntu: sudo apt install fonts-wqy-zenhei
# 验证: python3 -c "from weasyprint import HTML; print('OK')"
```

### 3.5 生成脚本
```python
from weasyprint import HTML
HTML(string=html_content).write_pdf(
    output_path,
    presentational_hints=True,
)
# 验证: pdftoppm -png -r 150 output.pdf preview && vision_analyze
```

---

## 四、避坑指南

| 坑 | 解法 |
|----|------|
| WeasyPrint 中文显示方块 | 安装 WQY ZenHei：`sudo apt install fonts-wqy-zenhei` |
| 多栏布局断裂 | 使用 CSS `columns`，不要用 flexbox |
| 文章被分页切断 | `page-break-inside: avoid` |
| RSS 源 403 | 添加 User-Agent 头 |
| 页面留大片空白 | 用 columns-2 或 columns-3 布局，在每页底部加额外文章/表格/点评填满 |
| 第1页太空 | 第1页就开始双栏，头条下直接接双栏内容，底部加三栏快讯 |
| 字体过多 | ≤2种字体，通过字重变化区分层次 |
| 颜色杂乱 | 60-30-10 法则 |
| 飞书发 PDF 失败 | 飞书不支持 send_message MEDIA，需用飞书 API 上传→获 file_key→发 file 消息 |
| 飞书 receive_id 报错 | POST body 里放 `receive_id` 和 `msg_type`，URL 用 `receive_id_type=open_id` |

---

## 五、完整工作流

```
1. 采集 ──→ mcp_tavily_tavily_search 多关键词搜索（3-5组）
2. 去重 ──→ 标题哈希去重，合并同类新闻
3. 分类 ──→ 按 国际/国内/财经/科技/体育/社会 分类
4. 摘要 ──→ 每篇提炼 2-3 句核心摘要
5. 排序 ──→ 按重要性/热度排序
6. 排版 ──→ 套用报刊 HTML 模板（4+页，双栏，数据条）
7. 生成 ──→ WeasyPrint → PDF
8. 验证 ──→ pdftoppm 转图 + vision_analyze 检查排版
9. 发送 ──→ 飞书 API 上传文件 → 发 file 消息
```

---

## 六、模板结构速查

```html
报头 .masthead → 头条 .headline → 数据条 .data-bar → 双栏 .columns-2
  ├─ .section .section-title .article（文章1）
  ├─ .section .section-title .article（文章2）
  └─ .pull-quote / .editor-note（跨栏元素）
页脚 .footer → 来源列表 + 页码
```
