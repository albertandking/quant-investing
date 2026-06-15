"""生成内置示例数据集（离线、可复现）。

为了让全书章节**断网也能运行**，这里用固定随机种子合成多份贴近真实形态的
教学数据，写入 data/processed/。所有数据均为合成，**不代表真实行情/公司**。
需要真实数据时见 scripts/fetch_data.py。

生成的数据集：
1. prices.parquet     —— 多只股票日度 OHLCV 行情面板（长表，40 只 × 约1000交易日）
2. benchmark.parquet  —— 基准指数与无风险利率日度序列（内置股票对其有真实 beta）
3. universe.parquet   —— 股票池静态信息与横截面特征（代码/名称/行业/板块/市值/PB/PE）

运行：
    uv run python scripts/make_sample_data.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "data" / "processed"

N_STOCKS = 40
N_DAYS = 1000  # 约四年交易日
SEED = 20260615  # 行情/股票池主种子

MARKET_MU = 0.06  # 基准年化漂移
MARKET_SIGMA = 0.20  # 基准年化波动
RF_ANNUAL = 0.02  # 无风险利率（年化，约定值）

# 行业与板块池（合成）
INDUSTRIES = ["金融", "消费", "科技", "医药", "工业", "公用", "材料", "能源"]
BOARDS = ["主板", "创业板", "科创板"]


def simulate_universe(rng: np.random.Generator) -> pd.DataFrame:
    """合成股票池静态信息与横截面特征。"""
    symbols = [f"STK{i + 1:03d}" for i in range(N_STOCKS)]
    industries = rng.choice(INDUSTRIES, size=N_STOCKS)
    boards = rng.choice(BOARDS, size=N_STOCKS, p=[0.6, 0.25, 0.15])
    # 规模（流通市值，亿元）：对数正态，跨度从小盘到大盘
    float_mktcap = np.round(rng.lognormal(mean=4.2, sigma=0.9, size=N_STOCKS), 1)
    pb = np.round(np.clip(rng.lognormal(mean=0.6, sigma=0.5, size=N_STOCKS), 0.3, 15), 2)
    pe = np.round(np.clip(rng.lognormal(mean=3.0, sigma=0.6, size=N_STOCKS), 5, 200), 1)

    names = [f"示例{ind}{i + 1:02d}" for i, ind in enumerate(industries)]
    return pd.DataFrame(
        {
            "symbol": symbols,
            "name": names,
            "industry": industries,
            "board": boards,
            "float_mktcap": float_mktcap,
            "pb": pb,
            "pe": pe,
        }
    )


def simulate_prices(
    rng: np.random.Generator,
    universe: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray, pd.DatetimeIndex]:
    """合成多只股票日度 OHLCV 面板，并返回驱动它们的共同市场冲击与日期。

    每只股票收益 = beta·市场冲击 + 个体冲击，制造横截面相关；
    由收盘价反推开/高/低与成交量，得到可直接回测的 OHLCV 长表。
    """
    dates = pd.bdate_range(end="2025-12-31", periods=N_DAYS)
    dt = 1 / 252
    market = rng.normal(0, 1, size=N_DAYS)  # 共同市场冲击（标准正态）

    frames = []
    for _, row in universe.iterrows():
        # 个股年化漂移与波动：高 PB 略高波动，纯属教学设定
        raw_sigma = 0.18 + 0.10 * rng.standard_normal() + 0.02 * (row["pb"] > 3)
        sigma = float(np.clip(raw_sigma, 0.12, 0.55))
        mu = float(np.clip(0.05 + 0.5 * sigma * rng.standard_normal() * 0.3, -0.05, 0.30))
        beta = float(np.clip(sigma / 0.25 + 0.2 * rng.standard_normal(), 0.3, 2.0))
        start = float(np.clip(rng.lognormal(mean=2.8, sigma=0.5), 3, 200))

        idio = rng.normal(0, 1, size=N_DAYS)
        shocks = 0.6 * beta * market + 0.4 * idio
        log_ret = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * shocks
        close = start * np.exp(np.cumsum(log_ret))

        # 由收盘价反推 OHLC：开盘=昨收带小跳空，日内高低在收盘附近浮动
        prev_close = np.concatenate([[start], close[:-1]])
        gap = rng.normal(0, 0.004, size=N_DAYS)
        open_ = prev_close * (1 + gap)
        intraday = np.abs(rng.normal(0, 0.012, size=N_DAYS))
        high = np.maximum(open_, close) * (1 + intraday)
        low = np.minimum(open_, close) * (1 - intraday)
        # 成交量：与当日波幅正相关，对数正态量级
        base_vol = rng.lognormal(mean=15.0, sigma=0.4)
        vol_noise = rng.lognormal(0, 0.2, size=N_DAYS)
        volume = (base_vol * (1 + 5 * intraday) * vol_noise).astype(np.int64)

        frames.append(
            pd.DataFrame(
                {
                    "date": dates,
                    "symbol": row["symbol"],
                    "open": np.round(open_, 2),
                    "high": np.round(high, 2),
                    "low": np.round(low, 2),
                    "close": np.round(close, 2),
                    "volume": volume,
                }
            )
        )

    panel = pd.concat(frames, ignore_index=True)
    return panel, market, dates


def simulate_benchmark(market_shocks: np.ndarray, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """由与个股相同的市场冲击构造基准指数与无风险利率日度序列。"""
    dt = 1 / 252
    drift = (MARKET_MU - 0.5 * MARKET_SIGMA**2) * dt
    idx_logret = drift + MARKET_SIGMA * np.sqrt(dt) * market_shocks
    index_close = 3000.0 * np.exp(np.cumsum(idx_logret))  # 类沪深300起点
    index_ret = np.concatenate([[np.nan], np.diff(index_close) / index_close[:-1]])
    rf_annual = RF_ANNUAL + 0.003 * np.sin(np.linspace(0, 3 * np.pi, len(dates)))

    df = pd.DataFrame(
        {
            "index_close": np.round(index_close, 2),
            "index_return": index_ret,
            "rf_annual": np.round(rf_annual, 5),
            "rf_daily": np.round(rf_annual / 252, 8),
        },
        index=dates,
    )
    df.index.name = "date"
    return df


def _save(df: pd.DataFrame, name: str, index: bool) -> None:
    df.to_parquet(OUT_DIR / f"{name}.parquet", index=index)
    print(f"  - {name}.parquet  ({len(df)} 行 x {df.shape[1]} 列)")


def main() -> None:
    """生成全部内置数据集并写入 data/processed/。"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    universe = simulate_universe(rng)
    prices, market_shocks, dates = simulate_prices(rng, universe)
    benchmark = simulate_benchmark(market_shocks, dates)

    print("已生成内置示例数据：")
    _save(prices, "prices", index=False)
    _save(benchmark, "benchmark", index=True)
    _save(universe, "universe", index=False)

    print(f"\n股票数：{universe['symbol'].nunique()}，交易日：{len(dates)}")
    print("基准指数末值：", benchmark["index_close"].iloc[-1])


if __name__ == "__main__":
    main()
