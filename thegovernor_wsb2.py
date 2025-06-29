#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 29 12:37:21 2025

@author: cabrown802
"""

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import matplotlib.dates as mdates
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# === CONFIGURATION ===
df = pd.read_csv("Reddit_Sentiment_Equity2.csv")
tickers = ['AMZN', 'CRWD', 'GOOG', 'MSFT']  # Add/remove tickers here
start_date = '2019-01-01'
end_date = '2025-06-01'

# === Load your sentiment data ===
# Assumes DataFrame `df` exists with: Ticker, commentdate, comment_sentiment_average
# Example:
# df = pd.read_csv("your_sentiment_data.csv")  # or however you're loading it
df['commentdate'] = pd.to_datetime(df['commentdate'])
df = df[df['ticker'].isin(tickers)]
df = df[df['commentdate'] >= pd.to_datetime(start_date)]

# === Download stock data for each ticker ===
price_data = {}
for ticker in tickers:
    stock_df = yf.download(ticker, start=start_date, end=end_date)
    # stock_df['Daily_Growth'] = (stock_df['Close'] - stock_df['Open']) / stock_df['Open']
    # stock_df['Cumulative_Growth'] = (1 + stock_df['Daily_Growth']).cumprod()
    stock_df['Close'] = stock_df['Close'] / stock_df.iloc[0]['Open']
    
    stock_df = stock_df.reset_index()
    stock_df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in stock_df.columns.values]
    #import pdb; pdb.set_trace()
    #stock_df.rename(columns={'Date': 'commentdate', 'Close': f'{ticker}_price'}, inplace=True)
    price_data[ticker] = stock_df

# # === Plotting ===
# fig, ax1 = plt.subplots(figsize=(14, 7))

# # Plot sentiment data (left y-axis)
# for ticker in tickers:
#     sentiment = df[df['ticker'] == ticker]
#     ax1.plot(sentiment['commentdate'], sentiment['comment_sentiment_average'], label=f'Sentiment ({ticker})')

# ax1.set_xlabel('Date')
# ax1.set_ylabel('Average Sentiment')
# ax1.grid(True)
# ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# # Create second y-axis (right) for stock prices
# ax2 = ax1.twinx()
# colors = ['black', 'gray', 'darkgreen', 'purple', 'navy']

# for i, ticker in enumerate(tickers):
#     stock_df = price_data[ticker]
#     ax2.plot(stock_df['commentdate'], stock_df[f'{ticker}_price'], 
#              linestyle='--', color=colors[i % len(colors)], label=f'{ticker} Price')

# ax2.set_ylabel('Stock Price')

# # Combine legends from both y-axes
# lines1, labels1 = ax1.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# plt.title('Sentiment vs Stock Price Over Time')
# plt.tight_layout()
# plt.show()

fig = make_subplots()

for ticker in tickers:
    sentiment = df[df['ticker'] == ticker]
    stock_df = price_data[ticker]
    
    fig.add_trace(
        go.Scatter(
            x=sentiment['commentdate'],
            y=sentiment['comment_sentiment_average'],
            mode='lines',
            name=f'Sentiment ({ticker})',
            line=dict(dash='solid')
        )
    )
    fig.add_trace(
        go.Scatter(
            x=stock_df['Date_'],
            y=stock_df[f'Close_{ticker}'],
            mode='lines',
            name=f'{ticker} Price',
            line=dict(dash='solid')
        )
    )
    
import plotly.io as pio
pio.renderers.default = 'browser'
fig.show()