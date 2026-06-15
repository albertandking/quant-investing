"""常用金融与绩效指标计算。

这些函数贯穿全书（收益率、波动率、夏普/索提诺/卡玛比率、最大回撤、胜率），
统一实现一次，正文与各章 notebook 共用。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# 输入恒为价格/收益的序列或多列表；标量结果（如对单列求年化）用 float 表示。
PandasData = pd.Series | pd.DataFrame
ScalarOrSeries = float | pd.Series

TRADING_DAYS = 252  # A股一年约定的交易日数，年化时使用


def daily_returns(prices: PandasData, log: bool = False) -> PandasData:
    """由价格序列计算日度收益率。

    Args:
        prices: 价格序列（Series）或多列价格表（DataFrame）。
        log: True 计算对数收益率 ln(P_t / P_{t-1})，否则计算简单收益率。

    Returns:
        与输入同型的收益率（已丢弃首行 NaN）。
    """
    if log:
        return np.log(prices / prices.shift(1)).dropna()
    return prices.pct_change().dropna()


def annualized_return(returns: PandasData, periods: int = TRADING_DAYS) -> ScalarOrSeries:
    """几何年化收益率。

    Args:
        returns: 周期收益率序列或多列表。
        periods: 一年的周期数（日频默认 252）。

    Returns:
        Series 输入返回标量，DataFrame 输入逐列返回 Series。
    """
    n = len(returns)
    cumulative = (1 + returns).prod()  # 累计净值（多列时为各列净值的 Series）
    return cumulative ** (periods / n) - 1


def annualized_volatility(returns: PandasData, periods: int = TRADING_DAYS) -> ScalarOrSeries:
    """年化波动率（标准差按 sqrt(periods) 缩放）。

    Args:
        returns: 周期收益率序列或多列表。
        periods: 一年的周期数（日频默认 252）。

    Returns:
        年化波动率：标量或逐列 Series。
    """
    return returns.std(ddof=1) * np.sqrt(periods)


def sharpe_ratio(
    returns: PandasData,
    risk_free: float = 0.0,
    periods: int = TRADING_DAYS,
) -> ScalarOrSeries:
    """年化夏普比率。

    Args:
        returns: 周期收益率序列或多列表。
        risk_free: 年化无风险利率（会折算到每个周期再扣减）。
        periods: 一年的周期数（日频默认 252）。

    Returns:
        年化夏普比率：标量或逐列 Series。
    """
    excess = returns - risk_free / periods  # 超额收益（已折算无风险利率到周期）
    return (excess.mean() / returns.std(ddof=1)) * np.sqrt(periods)


def sortino_ratio(
    returns: pd.Series,
    risk_free: float = 0.0,
    periods: int = TRADING_DAYS,
) -> float:
    """年化索提诺比率（只惩罚下行波动）。

    与夏普比率类似，但分母仅用负收益的标准差（下行风险），
    更贴合「投资者只厌恶亏损」的直觉。

    Args:
        returns: 周期收益率序列。
        risk_free: 年化无风险利率（折算到周期后扣减）。
        periods: 一年的周期数（日频默认 252）。

    Returns:
        年化索提诺比率。下行波动为 0 时返回 inf。
    """
    excess = returns - risk_free / periods
    downside = excess[excess < 0]
    downside_std = downside.std(ddof=1)
    if downside_std == 0 or np.isnan(downside_std):
        return float("inf")
    return float(excess.mean() / downside_std * np.sqrt(periods))


def max_drawdown(returns: pd.Series) -> float:
    """最大回撤（负值，越接近 0 越好）。"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    return float(drawdown.min())


def calmar_ratio(returns: pd.Series, periods: int = TRADING_DAYS) -> float:
    """卡玛比率 = 年化收益 / 最大回撤绝对值（衡量单位回撤换来的收益）。"""
    mdd = abs(max_drawdown(returns))
    if mdd == 0:
        return float("inf")
    return float(annualized_return(returns, periods) / mdd)


def win_rate(returns: pd.Series) -> float:
    """胜率：收益为正的周期占比（忽略恰好为 0 的周期）。"""
    nonzero = returns[returns != 0]
    if len(nonzero) == 0:
        return float("nan")
    return float((nonzero > 0).mean())
