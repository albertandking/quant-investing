"""qfin —— 《量化投资》全书复用工具包。

正文与各章 notebook 统一从这里导入，避免逻辑在多处重复维护：

    from qfin import load_prices, daily_returns, sma, set_chinese_font
"""

from qfin.data import (
    DATA_DIR,
    list_datasets,
    load_benchmark,
    load_close,
    load_prices,
    load_universe,
)
from qfin.metrics import (
    annualized_return,
    annualized_volatility,
    calmar_ratio,
    daily_returns,
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
    win_rate,
)
from qfin.plotting import set_chinese_font
from qfin.signals import (
    bollinger_bands,
    crossover,
    crossunder,
    ema,
    macd,
    rsi,
    sma,
)

__all__ = [
    # 数据
    "DATA_DIR",
    "list_datasets",
    "load_prices",
    "load_close",
    "load_benchmark",
    "load_universe",
    # 指标
    "daily_returns",
    "annualized_return",
    "annualized_volatility",
    "sharpe_ratio",
    "sortino_ratio",
    "calmar_ratio",
    "max_drawdown",
    "win_rate",
    # 信号
    "sma",
    "ema",
    "rsi",
    "macd",
    "bollinger_bands",
    "crossover",
    "crossunder",
    # 绘图
    "set_chinese_font",
]

__version__ = "0.1.0"
