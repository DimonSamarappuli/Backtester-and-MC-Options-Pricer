# Moving Average Crossover Backtester: Building and Validating a Trading Strategy

## 1. Project Overview
This projects aims to implement a simple moving average (SMA) crossover trading strategy, backtest it on historical data and validate the result on an independently built version on a backtesting library, backtesting.py.
The goal was not to produce a strategy that beats the market, but to build a rigorous backtesting pipeline from the ground up, to understand common statistical pitfalls that make backtests misleading, and to gain an understanding of them through a working implementation.

Asset Tested: MSFT (Microsoft)

Data Source: Yahoo Finance, from yfinance

Core Strategy: SMA Crossover 

Tools: Python, Pandas, backtesting.py, matplotlib

## 2. Core Theory of Strategy
A moving average crossover is a trend following strategy: when a short window moving average rises above a long window moving average, it's read as the start of an uptrend ("golden cross"). When the opposite happens, it is read as a downtrend ("death cross").

A well known weakness of this strategy is a principle known as **whipsawing**, where the short and long moving average windows repeatedly cross each other with no real trend, generating false signals and so causing repeated small losses.
This is a known flaw of this strategy and not a flaw or limitation that is unique to my implementation.

### 3. Method
### 3.1 Setup and Data
Historical OHLC data was pulled from yfinance. An early easy to miss issue is that yfinance returns the columns of the resulting dataframe in a multi-index format, which needs to be flattened down into single index before any of the following code can work.

### 3.1 Signal Generation
Two SMAs are computed with the pandas .rolling(window=).mean() function function. A binary signal is then generated, where 1 is when the short SMA is above the long, and 0 otherwise. The signal represents a state of holding/flat rather than an action of buy/sell.

### 3.3 Avoiding Look Ahead Bias
The signal for day N can only be known after day N has ended, due to needing day N's close price, Hence, it can only be acted upon on day N+1, which is a principle raw backtesters ignore. To prevent the backtester from essentially being able to "see the future" by one day , every day, and return an inflated performance, the raw signal was shifted one by using .shift(1).
