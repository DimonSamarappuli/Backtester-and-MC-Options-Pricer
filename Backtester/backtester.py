import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


pd.set_option('display.max_columns', None)
pd.set_option("display.width", None)
import math

# Portfolio:
initial_cash = 10000
fee_per_trade = 0.001
slippage = 0.0003
position_size = 1 

# risk:
risk_free_rate = 0

annualize = math.sqrt(252)

def main():
    df = get_data("MSFT", "2018-01-01", "2026-08-08")
    df = compute_signals(df, 50, 200)
    df = compute_returns(df)
    sf, b_and_h_stats = compute_metrics(df)
    sf = pd.DataFrame(sf)
    sf = sf.T
    sf["Buy and Hold"] = b_and_h_stats
    print(sf)
    plt.show()

def get_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    # downloads Microsoft's stock data
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        df = df.loc[(df.index > "2023-08-01")]  # testing df
        return df
# changes the multi-index dataframe into a single index one

list_of_statistics = []
df_1 = get_data("MSFT", "2018-01-01", "2026-08-08")
asset_daily_return = df_1["Close"].pct_change()
# calculates the fractional change between the current row in a dataframe/series and the previous element
years = len(df_1) / 252
days_held = len(df_1)

def compute_signals(df, short_window, long_window):
    df = df.copy()
    df["Short_SMA"] = df["Close"].rolling(window=short_window).mean()
    df["Long_SMA"]= df["Close"].rolling(window=long_window).mean()
    first_valid_idx = df["Long_SMA"].first_valid_index()
    df = df.loc[first_valid_idx:]

    df["signal"] = (df["Short_SMA"] > df["Long_SMA"]).astype(int)
    # 1 = holding the stock, 0 = sold and are sitting in cash
    # pandas is vectorised so this expression will compare row by row of short sma and long sma and return a series
    # returns a series of true/false which then gets turned into 0s and 1s

    df["shifted_signal"] = df["signal"].shift(1).fillna(False).astype(int)
    # shifts the signal 1 day forward. This is because you will only know the closing price that day after the day ends
    # so you can only include that closing price on the next day

    df["strategy_daily_return"] = position_size * asset_daily_return * df["shifted_signal"]
    # the strategy only makes money if you are holding the stock (signal=1) when the stock price changes.
    # if you aren't holding and are sitting in cash, you make no money

    df["signal_change"] = df["signal"].diff().fillna(0).astype(int)
    # subtracts the previous row's value from the current row's value
    df["shifted_signal_change"] = df["shifted_signal"].diff().fillna(0).astype(int)
    return df

def compute_returns(df):
    df = df.copy()
    df["buy_and_hold_return"] = (1 + asset_daily_return).cumprod()
    deductibles = (df["shifted_signal_change"] != 0).astype(int)
    # this returns a series of 1s and 0s, 1 is when the signal does not equal 0, 0 is when the signal equals 0.

    df["strategy_daily_return"] = df["strategy_daily_return"] - deductibles * (fee_per_trade + slippage)
    df["cum_strat_return"] = (1 + df["strategy_daily_return"]).cumprod()
    # 1 is added to strategy_daily_return so that we can see what the compounding effect is on 1 dollar.

    df["equity"] = initial_cash * df["cum_strat_return"]
    # equity simply means the total dollar value of what you own
    return df

def compute_metrics(df):
    buy_and_hold_final = df["buy_and_hold_return"].iloc[-1]

    CAGR_buy_and_hold_return = (buy_and_hold_final ** (1 / years)) - 1

    annualized_volatility_of_asset = asset_daily_return.std() * annualize

    sharpe_buy_and_hold = (CAGR_buy_and_hold_return - risk_free_rate) / annualized_volatility_of_asset

    running_peak_of_buy_and_hold = df["buy_and_hold_return"].cummax()

    percentage_difference_between_peak_and_current_value_of_buy_and_hold = (
            ((df["buy_and_hold_return"] - running_peak_of_buy_and_hold) / running_peak_of_buy_and_hold) * 100)

    min_of_buy_and_hold = f"{percentage_difference_between_peak_and_current_value_of_buy_and_hold.min():.2f}%"

    buy_and_hold_win_series = (asset_daily_return > 0).astype(int)
    only_wins_of_buy_and_hold = buy_and_hold_win_series[buy_and_hold_win_series == 1]
    buy_and_hold_wins = len(only_wins_of_buy_and_hold)
    win_rate_buy_and_hold = buy_and_hold_wins / days_held

    number_of_trades_buy_and_hold = 1

    buy_and_hold_statistics = (
        pd.Series([CAGR_buy_and_hold_return, annualized_volatility_of_asset,
                   sharpe_buy_and_hold, min_of_buy_and_hold, win_rate_buy_and_hold,
                   number_of_trades_buy_and_hold],

                  index=["CAGR", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown",
                         "Win Rate", "Trade Count"]))

    # CAGR : compound annual growth rate, this asks "at what rate did my stock need to grow to go from the starting value to the ending value"
    cum_strat_return_final = df["cum_strat_return"].iloc[-1]

    CAGR_cum_strat_return = (cum_strat_return_final**(1/years)) - 1

    annualized_volatility_of_strategy = df["strategy_daily_return"].std() * annualize


    # Sharpe Ratio : The standard risk-adjusted-return metric — return earned per unit of risk taken
    # formula = (annualized return - risk free rate) / annualized volatility

    sharpe_strategy = (CAGR_cum_strat_return - risk_free_rate) / annualized_volatility_of_strategy

    # Max drawdown: the largest peak to trough decline your equity curve ever experienced

    running_peak_of_strategy = df["equity"].cummax()
    percentage_difference_between_peak_and_current_value_of_strategy = (
            ((df["equity"] - running_peak_of_strategy) / running_peak_of_strategy) * 100)
    min_of_strategy = percentage_difference_between_peak_and_current_value_of_strategy.min()

    # Win Rate:
    days_holding = df["shifted_signal"][df["shifted_signal"] == 1]
    win = (df["strategy_daily_return"] > 0).astype(int)
    win_series = (df["shifted_signal"] & win)
    # when holding, to have a positive strategy return, the stock's price has to go up
    win_count = len(win_series[win_series == 1])
    win_rate = win_count / len(days_holding)

    # Number of Trades
    buy_days = df["signal_change"][df["signal_change"] == 1]
    sell_days = df["signal_change"][df["signal_change"] == -1]
    number_of_trades = len(buy_days) + len(sell_days)

    summary_statistics = pd.Series(
        [
            CAGR_cum_strat_return,
            annualized_volatility_of_strategy,
            sharpe_strategy,
            min_of_strategy,
            win_rate,
            number_of_trades,
        ],
    index = ["CAGR", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown",
             "Win Rate", "Trade Count"]
    )

    df[["cum_strat_return", "buy_and_hold_return"]].plot(
        figsize = (12,6),
        xlabel = "Date",
        ylabel = f"Return",
        grid = True,
        )
    list_of_statistics.append(summary_statistics)
    return list_of_statistics, buy_and_hold_statistics

if __name__ == "__main__":
    main()
