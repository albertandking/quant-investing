"""数据加载工具。

内置示例数据集存放在仓库的 data/processed/ 下，**离线即可读取**，
保证书中所有基础章节断网也能运行。所有内置数据均为合成，
**不代表任何真实股票/公司/行情**；真实数据接口见 scripts/fetch_data.py。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# 定位到仓库根目录下的 data/，无论从 notebook 还是脚本调用都能找到。
# 本文件位于 src/qfin/data.py，向上三级即仓库根。
_REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = _REPO_ROOT / "data" / "processed"


def list_datasets() -> list[str]:
    """列出 data/processed/ 下所有可用的内置数据集文件名。"""
    if not DATA_DIR.exists():
        return []
    return sorted(p.name for p in DATA_DIR.glob("*.parquet"))


def _load(name: str) -> pd.DataFrame:
    """读取 data/processed/<name>.parquet，缺失时给出友好提示。"""
    path = DATA_DIR / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"未找到内置数据集 {path}。\n请先运行：uv run python scripts/make_sample_data.py"
        )
    return pd.read_parquet(path)


def load_prices() -> pd.DataFrame:
    """加载内置的多股票日度行情面板（长表/tidy 格式）。

    返回列为 [date, symbol, open, high, low, close, volume] 的长表，
    每个 (date, symbol) 一行，适合直接喂给回测框架或按 symbol 分组处理。
    其中 date 为 datetime64，symbol 为合成股票代码（见 load_universe）。
    """
    df = _load("prices")
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_close() -> pd.DataFrame:
    """加载收盘价宽表（行=日期、列=股票代码），便于做横截面与组合计算。

    等价于对 load_prices() 的 close 字段做 pivot，常用于因子/选股章节。
    """
    prices = load_prices()
    wide = prices.pivot(index="date", columns="symbol", values="close")
    wide.index.name = "date"
    wide.columns.name = None
    return wide


def load_benchmark() -> pd.DataFrame:
    """加载内置的基准指数与无风险利率日度序列。

    列：index_close（指数收盘）、index_return（指数日收益）、
    rf_annual（年化无风险利率）、rf_daily（日度无风险利率）。
    内置股票对该指数有真实的 beta，可用于业绩基准与 CAPM/超额收益计算。
    """
    df = _load("benchmark")
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    return df


def load_universe() -> pd.DataFrame:
    """加载内置股票池的静态信息与横截面特征（供因子/选股章节）。

    列：symbol（代码）、name（名称）、industry（行业）、board（板块）、
    float_mktcap（流通市值，亿元，规模因子代理）、pb（市净率）、pe（市盈率）。
    所有取值均为合成示意，仅用于教学演示横截面排序与分组。
    """
    return _load("universe")
