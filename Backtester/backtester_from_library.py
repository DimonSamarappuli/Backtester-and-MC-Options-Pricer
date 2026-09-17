from backtesting import Backtest, Strategy
import pandas as pd
import yfinance as yf
from backtesting.lib import crossover
pd.set_option('display.max_columns', None)
pd.set_option("display.width", None)

df = yf.download("MSFT", start="2018-01-01", end="2026-08-08")
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df["Temp"] = df["Close"]
df["Close"] = df["Open"]
df["Open"] = df["Temp"]
df.drop(columns=["Temp"], inplace=True)
df.rename(columns={"Close": "Open", "Open": "Close"}, inplace=True)
#df = df.loc[(df.index <= "2023-08-01")], # training df
df = df.loc[(df.index > "2023-08-01")] # testing df

#def optim_func():
#    return

def SMA_short(price_array, sma_short_window):
    return pd.Series(price_array).rolling(window=sma_short_window).mean()

def SMA_long(price_array, sma_long_window):
    return pd.Series(price_array).rolling(window=sma_long_window).mean()

class SMA_oscillator(Strategy):
    sma_short_window = 50
    sma_long_window = 200
    def init(self):
        self.sma_short = self.I(SMA_short, self.data.Close, self.sma_short_window)
        # here, backtesting.py calls the SMA function on df["Close"] and a window
        # the window can be changed by using sma_window = range(10, 100, 10)

        self.sma_long = self.I(SMA_long, self.data.Close, self.sma_long_window)

    def next(self):
        if crossover(self.sma_short, self.sma_long):
            if not self.position:
                self.buy()
        elif crossover(self.sma_long, self.sma_short):
            if self.position:
                self.position.close()

bt = Backtest(df, SMA_oscillator, cash=10_000, commission= 0.0013, exclusive_orders = True)
"""
stats = bt.optimize(
    sma_short_window = 50,
    sma_long_window = 200
   #maximize =
)
"""
stats = bt.run()
print(stats)
bt.plot()



