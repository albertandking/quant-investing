"""冒烟测试：保证 qfin 工具包与内置数据可用。

运行：
    uv run python scripts/make_sample_data.py   # 先生成数据
    uv run pytest
"""

import numpy as np
import pandas as pd

from qfin import (
    annualized_return,
    annualized_volatility,
    bollinger_bands,
    calmar_ratio,
    crossover,
    daily_returns,
    ema,
    load_benchmark,
    load_close,
    load_prices,
    load_universe,
    macd,
    max_drawdown,
    rsi,
    sharpe_ratio,
    sma,
    sortino_ratio,
    win_rate,
)


def test_load_prices_panel() -> None:
    prices = load_prices()
    assert isinstance(prices, pd.DataFrame)
    assert {"date", "symbol", "open", "high", "low", "close", "volume"}.issubset(prices.columns)
    assert prices["symbol"].nunique() == 40
    assert pd.api.types.is_datetime64_any_dtype(prices["date"])
    # OHLC 关系自洽：最高价 >= 最低价
    assert (prices["high"] >= prices["low"]).all()


def test_load_close_matrix() -> None:
    close = load_close()
    assert isinstance(close.index, pd.DatetimeIndex)
    assert close.shape[1] == 40
    assert len(close) > 500
    assert (close > 0).all().all()


def test_load_benchmark() -> None:
    bench = load_benchmark()
    assert {"index_close", "index_return", "rf_annual", "rf_daily"}.issubset(bench.columns)
    assert isinstance(bench.index, pd.DatetimeIndex)
    assert (bench["index_close"] > 0).all()


def test_load_universe() -> None:
    uni = load_universe()
    assert {"symbol", "name", "industry", "board", "float_mktcap", "pb", "pe"}.issubset(uni.columns)
    assert uni["symbol"].nunique() == 40
    assert (uni["float_mktcap"] > 0).all()


def test_metrics_run() -> None:
    close = load_close()
    rets = daily_returns(close)
    assert (rets.abs() < 1).all().all()  # 日收益率应远小于 100%

    one = rets.iloc[:, 0]
    assert np.isfinite(annualized_return(one))
    assert annualized_volatility(one) > 0
    assert np.isfinite(sharpe_ratio(one, risk_free=0.02))
    assert np.isfinite(sortino_ratio(one, risk_free=0.02))
    assert -1 <= max_drawdown(one) <= 0
    assert np.isfinite(calmar_ratio(one))
    assert 0 <= win_rate(one) <= 1


def test_signals_run() -> None:
    close = load_close().iloc[:, 0]
    assert sma(close, 20).notna().sum() > 0
    assert ema(close, 12).notna().sum() > 0

    r = rsi(close, 14).dropna()
    assert ((r >= 0) & (r <= 100)).all()

    m = macd(close)
    assert {"macd", "signal", "hist"}.issubset(m.columns)

    bb = bollinger_bands(close, 20)
    valid = bb.dropna()
    assert (valid["upper"] >= valid["lower"]).all()

    fast, slow = sma(close, 5), sma(close, 20)
    assert crossover(fast, slow).dtype == bool
