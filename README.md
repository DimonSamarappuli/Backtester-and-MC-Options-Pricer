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

### 3.4 Returns
Daily returns of the stock were computed using .pct_change(). The returns of the strategy itself was computed as shifed_signal * daily_return. The shifted signal in this case acts as an on/off signal, when holding, the return is made, but when flat, the signal is 0 so nothing is made regardless of how the market did.

Cumulative returns are computed via a (1 + daily_return).cumprod(), rather than by summing, as return compound multiplicatively rather than additively.

### 3.5 Costs
Two separate types of costs were taken into consideration, fee per trade (essentially a commission fee) and slippages.
#### Fee per Trade
A fixed percentage cost that is applied on every day that a position changes. in both directions.

#### Slippages
A smaller fixed percentage applied on every position change. This models the fact that the assumed price at execution and the true price will always differ.

Both costs are gated by a deductibles flag which was made by diffing shifted signal .

### 4. Performance Metrics
Six metrics were computed for both the strategy and the buy-and-hold benchmark.
- CAGR: compound annual growth rate. Computed from the final cumulative return and the number of days the data span, (final_value^(1/years) - 1), not through simple division which would have ignored compounding,
- Annualized Volatility: standard deviation of daily return * 252
- Sharpe Ratio: annualized return divided by annualized volatility. Sharpe ratio takes into account risk.
- Max Drawdown: the largest subsequent peak to trough decline, computed using a running maximum cummax() compared against the value of the stock at each point in time, then taking the most negative point. This is different from finding the highest peak and lowest trough and calculating the decline, as they might not necessarily be next to each other, and hence not subsequent.
- Win Rate: the proportion of holding days with a positive return
- Trade count: the number of position changes, not the number of round trips

***image***

### 5. Avoiding Overfitting
Overfitting is a principle where too many parameters are used to force a model to fit a distinct set of points perfectly, which may exist due to noise, which causes the model to be very accurate at these exact points but inaccurate everywhere else, leading to false signals.

To prevent overfitting and the model learning noise, the data was split into 2 sections, a training set and a testing set. 
A small, deliberately picked set of SMA window pairs were tested on the training window and the Sharpe Ratio of each were used to pick a winning combination. Sharpe Ratio was preferred for this over CAGR due to Sharpe factoring in risk.

This process was conducted as a defence against curve fitting as parameters that look great on one dataset could simply be capturing noise specific to that dataset. 

### 6. Validating and Checking against backtesting.py
The validation process of the strategy was unexpectedly the largest learning resource of this entire project, due to the discrepancies between models that were introduced and investigated.

To check, an identical strategy was implemented independently in backtesting.py, a Python library built specifically for backtesting. The goal was to see whether two independently built implementations can agree with each other, which would be a strong sign that there were no bugs or errors.

During the cross-check, a few discrepancies were introduced and investigated:

#### Early Trade count mismatch: 
An earlier implementation of the model showed a trade count mismatch. This was caused due to having a short lookback buffer, the long SMA did not have a long enough warm up period, so when about 200 days of NaN transitioned to a real number, .diff() read this as a crossover, creating fake jumps. This was fixed by trimming the dataframe to start only once the long SMA had real values throughout.
first_valid_idx = df["Long_SMA"].first_valid_index()
df = df.loc[first_valid_idx:]

#### Trade Count mismatch due to convention
After the previously mentioned fix, the pandas version still counted more trades (5) than the backtesting.py version (2). This was resolved by confirming that this was simply a difference in counting convention, where the pandas version counts each position change as a trade whereas the backtesting.py version counts every round trip, so an open position at the end of the data with no matching end date would not be counted.

#### Return Mismatch
When comparing trade level return between the two versions, one trade showed that the backtesting.py version had double the return of the pandas version. This was caused by the pandas version only using a 0.5 position size, which was then fixed by changing it to 1, which caused the returns to match very closely.

#### Commission Mismatch
A discrepancy similar to the previous one was resolved by realising that the pandas version was only executing a commission fee during one of the events, either buy or sell, rather than during both. Once both fees were summed up, it matched the fee of the backtesting.py version.

#### Gap in Annualized Volatility, Sharpe Ratio and CAGR
Even after all the above mentioned fixes, the annualized volatility of the two models did not agree by an order of almost 1.6x. Investigating this discrepancy further led to the fact that this is an acknowledged and debated ambiguity in the method that backtesting.py uses to calculate annualized volatility, as it could be computed from two correct, but different, mathematical conventions, normal and lognormal. The residual gap is hence treated as an explained, expected difference rather than a bug, as every trade and cost level comparison underneath it was verified to match.

#### Conclusion
Almost none of the initial mismatches were caused due to genuine bugs, but rather mismatches in comparisons, such as date windows, positions and counting conventions. Once each comparison was normalised, the two models agreed with each other at the trade level, which is sufficient evidence to say that the pandas version is sound.

### 7. Accepted Limitations
- The strategy will only ever hold or exit
- Fee/slippage values are rough assumptions, not calibrated against a specific real broker's actual fee schedule.
- Annualized Volatility and hence Sharpe/CAGR, show a residual gap against backtesting.py's figures. This can be attributed to the normal vs lognormal return convention, which is a known point of disagreement in the field.

### 8. Project Demonstrations
Regardless of how the strategy performed against a simple buy-and-hold strategy, the process of building, testing and validating the model from the ground up and going hands-on into essentially every backtesting statistical pitfall was the true learning point of this project, from look ahead bias and how it is caused, the dangers of overfitting and the train/test splits used to guard against it to the value of independent cross validation between versions to catch errors that may initially appear as bugs. The debugging process of tracing each number to its root cause and figuring out the issue rather than accepting a plausible looking result, was in a lot of ways, the actual substance of this project.
