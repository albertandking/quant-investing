"""常用技术指标与交易信号。

第8章及策略章节会反复用到均线、RSI、MACD、布林带等指标，
统一在此实现一次（纯 pandas，可作用于单只标的的价格 Series）。
"""

from __future__ import annotations

import pandas as pd


def sma(price: pd.Series, window: int) -> pd.Series:
    """简单移动平均（Simple Moving Average）。"""
    return price.rolling(window).mean()


def ema(price: pd.Series, span: int) -> pd.Series:
    """指数移动平均（Exponential Moving Average）。"""
    return price.ewm(span=span, adjust=False).mean()


def rsi(price: pd.Series, window: int = 14) -> pd.Series:
    """相对强弱指标（RSI），取值范围 0–100。

    采用 Wilder 平滑：用指数加权平均估计平均涨幅与平均跌幅，
    RSI = 100 - 100 / (1 + 平均涨幅 / 平均跌幅)。

    Args:
        price: 价格序列。
        window: 回看窗口（经典取 14）。

    Returns:
        与输入等长的 RSI 序列（前 window 个值为 NaN）。
    """
    delta = price.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def macd(
    price: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """MACD 指标。

    返回含三列的 DataFrame：
    - macd：快线 EMA(fast) − 慢线 EMA(slow)（DIF）；
    - signal：macd 的 EMA(signal)（DEA）；
    - hist：macd − signal（柱状图，量化常用的金叉/死叉判据）。
    """
    dif = ema(price, fast) - ema(price, slow)
    dea = dif.ewm(span=signal, adjust=False).mean()
    hist = dif - dea
    return pd.DataFrame({"macd": dif, "signal": dea, "hist": hist})


def bollinger_bands(
    price: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> pd.DataFrame:
    """布林带（中轨为 SMA，上/下轨为中轨 ± num_std 倍滚动标准差）。

    返回含 [mid, upper, lower] 三列的 DataFrame。
    """
    mid = sma(price, window)
    sd = price.rolling(window).std(ddof=0)
    return pd.DataFrame(
        {
            "mid": mid,
            "upper": mid + num_std * sd,
            "lower": mid - num_std * sd,
        }
    )


def crossover(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """金叉：fast 上穿 slow 的当根为 True（前一根 fast<=slow，当根 fast>slow）。"""
    prev = fast.shift(1) <= slow.shift(1)
    now = fast > slow
    return (prev & now).fillna(False).astype(bool)


def crossunder(fast: pd.Series, slow: pd.Series) -> pd.Series:
    """死叉：fast 下穿 slow 的当根为 True（前一根 fast>=slow，当根 fast<slow）。"""
    prev = fast.shift(1) >= slow.shift(1)
    now = fast < slow
    return (prev & now).fillna(False).astype(bool)
