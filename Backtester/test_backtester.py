from backtester import compute_signals, compute_returns, compute_metrics
import backtester
import pandas as pd

def make_test_df():
    prices = [10, 10, 10, 10, 10, 10, 12, 14, 16, 15, 13, 11, 9, 9, 9]
    dates = pd.date_range(start="2024-01-01", periods=len(prices), freq="D")
    df = pd.DataFrame({"Close": prices}, index=dates)
    return df

def test_compute_signals():
    df = make_test_df()
    df = compute_signals(df, 2, 6)
    assert "Short_SMA" in df.columns
    assert "Long_SMA" in df.columns
    assert "signal" in df.columns
    assert "shifted_signal" in df.columns
    assert "signal_change" in df.columns
    assert "shifted_signal_change" in df.columns
    assert set(df["signal_change"].dropna().unique()).issubset({-1, 0, 1})
    assert df["shifted_signal"].iloc[1] == df["signal"].iloc[0]


def test_compute_returns():
    df = make_test_df()
    df = compute_signals(df, 2, 6)
    df = compute_returns(df)
    assert "buy_and_hold_return" in df.columns
    assert "strategy_daily_return" in df.columns
    assert "cum_strat_return" in df.columns
    assert "equity" in df.columns
    days_flat = df[df["shifted_signal"] == 0]
    assert (days_flat["strategy_daily_return"].fillna(0) == 0).all()


def test_compute_metrics():
    df = make_test_df()
    df = compute_signals(df, 2, 6)
    df = compute_returns(df)
    project.years = len(df) / 365.25
    project.annualize = 252 ** 0.5
    project.risk_free_rate = 0
    project.asset_daily_return = df["Close"].pct_change()
    project.list_of_statistics = []
    result_list, buy_and_hold_statistics = compute_metrics(df)

    strategy_statistics = result_list[0]

    expected_labels = [
        "CAGR", "Annualized Volatility", "Sharpe Ratio",
        "Max Drawdown", "Win Rate", "Trade Count"]
    assert list(strategy_statistics.index) == expected_labels
    assert list(buy_and_hold_statistics.index) == expected_labels

    assert 0 <= strategy_statistics["Win Rate"] <= 1
    assert 0 <= buy_and_hold_statistics["Win Rate"] <= 1
    