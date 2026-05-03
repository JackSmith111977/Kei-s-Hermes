---
name: financial-analyst
description: "金融数据分析与研报生成技能。使用 akshare 获取行情，ta 库计算指标，matplotlib 绘制图表，LLM 生成研报。"
version: 1.0.0
triggers: ["股票分析", "行情查询", "研报生成", "financial analysis", "stock report", "大盘走势"]
depends_on:
  - web-access
  - pdf-layout-weasyprint
metadata:
  hermes:
    tags: [finance, analysis, report]
    category: data-science
    skill_type: generator
    design_pattern: pipeline
---

# 金融分析师 (Financial Analyst Agent)

## 核心工作流

1.  **数据获取**：使用 `akshare` 获取 A 股/港股/美股/加密货币数据。
2.  **技术分析**：使用 `ta` 库计算 MA, MACD, RSI, BOLL 等指标。
3.  **可视化**：使用 `matplotlib` 绘制 K 线图 + 指标副图。
4.  **智能研报**：结合 LLM 分析图表与数据，生成 PDF 研报。

## 一、数据获取 (akshare)

**推荐接口**：
- **A 股日线**：`ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20230101", adjust="qfq")`
- **实时行情**：`ak.stock_zh_a_spot_em()`
- **大盘指数**：`ak.stock_zh_index_daily(symbol="sh000001")`

**注意事项**：
- 数据源可能需要代理，但 `akshare` 大部分接口在国内直连可用。
- 获取数据后务必检查 `df.empty` 处理异常情况。

## 二、技术指标计算 (ta 库)

**常用指标代码示例**：
```python
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# MA 均线
df['MA20'] = SMAIndicator(df['close'], window=20).sma_indicator()
# MACD
macd = MACD(df['close'])
df['MACD'] = macd.macd()
df['MACD_Signal'] = macd.macd_signal()
# RSI
df['RSI'] = RSIIndicator(df['close'], window=14).rsi()
```

## 三、可视化 (Matplotlib)

- 必须使用中文字体（如 `WQY ZenHei`）。
- **K 线图绘制**：使用 `matplotlib.finance` (如果可用) 或手动绘制 Bar 图。
- **保存格式**：PNG (用于 LLM Vision 分析) 和 PDF (研报附件)。

## 四、研报生成 (LLM + PDF)

**Prompt 结构**：
1.  **角色**：资深证券分析师。
2.  **输入**：K 线图 (Vision) + 关键数据 (RSI 数值, MACD 金叉/死叉状态, 近期涨跌幅)。
3.  **输出**：
    - **技术面分析**：趋势、支撑/压力位、指标信号。
    - **基本面摘要**：(如果获取到) PE/PB, 营收增速。
    - **操作建议**：买入/持有/卖出 (附带风险提示)。

## 🚩 Red Flags

- **环境隔离**：`akshare`, `ta`, `mplfinance` 等库仅安装在 `/usr/bin/python3.12`。**严禁**在 `execute_code` 沙箱中运行，必须通过 `terminal` 调用系统 Python。
- **无头渲染**：在服务器运行 Matplotlib 必须 `import matplotlib; matplotlib.use('Agg')`，否则报错。
- **合规性**：必须声明"仅供参考，不构成投资建议"。
- **交付顺序**：**先发送图片/图表，再发送文字分析**，确保用户体验。

## 评估用例 (Eval Cases)

1.  **Eval-001 (个股分析)**：
    - *输入*："帮我分析一下贵州茅台的技术面"
    - *预期*：获取茅台数据 -> 计算指标 -> 画图 -> 生成分析摘要。
2.  **Eval-002 (大盘研报)**：
    - *输入*："生成一份上证指数今日研报"
    - *预期*：生成包含 K 线图和详细分析的 PDF 文件。