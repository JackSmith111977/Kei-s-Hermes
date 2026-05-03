#!/usr/bin/env python3
"""
金融绘图脚本 v1.0
功能：输入股票代码和日期范围，生成 K 线图 + MA/MACD/RSI 指标图。
依赖：akshare, ta, matplotlib
"""

import sys
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator

def fetch_data(symbol, start_date, end_date):
    """获取 A 股历史数据"""
    print(f"Fetching data for {symbol}...")
    try:
        # 转换日期格式 YYYYMMDD -> YYYY-MM-DD for akshare sometimes, but akshare usually accepts YYYYMMDD for zhi_a_hist
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        df.rename(columns={
            "日期": "date", "开盘": "open", "收盘": "close", 
            "最高": "high", "最低": "low", "成交量": "volume"
        }, inplace=True)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def add_indicators(df):
    """计算技术指标"""
    if df.empty: return df
    
    # MA
    df['MA5'] = SMAIndicator(df['close'], window=5).sma_indicator()
    df['MA20'] = SMAIndicator(df['close'], window=20).sma_indicator()
    
    # MACD
    macd = MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()
    
    # RSI
    df['RSI'] = RSIIndicator(df['close'], window=14).rsi()
    
    return df

def plot_chart(df, symbol, output_path):
    """绘制图表"""
    if df.empty: return
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True, 
                             gridspec_kw={'height_ratios': [3, 1, 1, 1]})
    
    # 1. K 线 (简化版 - 折线 + 填充)
    ax1 = axes[0]
    ax1.plot(df['date'], df['close'], color='red', linewidth=1.5)
    ax1.fill_between(df['date'], df['close'], alpha=0.1, color='red')
    ax1.plot(df['date'], df['MA5'], label='MA5', color='orange')
    ax1.plot(df['date'], df['MA20'], label='MA20', color='blue')
    ax1.set_title(f"{symbol} 股价走势 (复权)")
    ax1.legend()
    ax1.grid(True)
    
    # 2. 成交量
    ax2 = axes[1]
    colors = ['red' if c >= o else 'green' for c, o in zip(df['close'], df['open'])]
    ax2.bar(df['date'], df['volume'], color=colors, alpha=0.7)
    ax2.set_ylabel("成交量")
    ax2.grid(True)
    
    # 3. MACD
    ax3 = axes[2]
    ax3.plot(df['date'], df['MACD'], label='MACD', color='black')
    ax3.plot(df['date'], df['MACD_Signal'], label='Signal', color='orange')
    ax3.bar(df['date'], df['MACD_Hist'], color='gray', alpha=0.5)
    ax3.axhline(0, color='black', linewidth=0.8)
    ax3.set_ylabel("MACD")
    ax3.legend()
    ax3.grid(True)
    
    # 4. RSI
    ax4 = axes[3]
    ax4.plot(df['date'], df['RSI'], label='RSI(14)', color='purple')
    ax4.axhline(70, color='red', linestyle='--', alpha=0.5)
    ax4.axhline(30, color='green', linestyle='--', alpha=0.5)
    ax4.set_ylabel("RSI")
    ax4.legend()
    ax4.grid(True)
    
    # X 轴格式化
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    symbol = sys.argv[1] if len(sys.argv) > 1 else "600519"
    start = sys.argv[2] if len(sys.argv) > 2 else "20240101"
    end = sys.argv[3] if len(sys.argv) > 3 else "20260503"
    
    df = fetch_data(symbol, start, end)
    df = add_indicators(df)
    
    output = f"/tmp/stock_{symbol}_analysis.png"
    plot_chart(df, symbol, output)
