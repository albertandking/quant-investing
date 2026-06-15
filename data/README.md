# 数据说明

本目录存放本书使用的数据。

- `processed/`：**内置示例数据集**（入库，离线可跑）。由 `scripts/make_sample_data.py`
  用固定随机种子合成，**全部为合成数据，不代表任何真实股票、公司或行情**。
- `raw/`：联网抓取的原始数据（**不入库**，见 `.gitignore`）。由 `scripts/fetch_data.py` 生成。

## 内置数据集（data/processed/）

运行一次生成：

```bash
uv run python scripts/make_sample_data.py
```

| 文件 | 形态 | 规模 | 主要列 | 用途 |
|---|---|---|---|---|
| `prices.parquet` | 长表/tidy | 40 只 × ~1000 交易日 | date, symbol, open, high, low, close, volume | 行情、信号、策略、回测 |
| `benchmark.parquet` | 时间序列 | ~1000 交易日 | index_close, index_return, rf_annual, rf_daily | 业绩基准、超额收益、CAPM |
| `universe.parquet` | 横截面 | 40 只 | symbol, name, industry, board, float_mktcap, pb, pe | 因子/选股的横截面特征 |

读取方式（统一通过 `qfin`）：

```python
from qfin import load_prices, load_close, load_benchmark, load_universe

panel = load_prices()       # OHLCV 长表
close = load_close()         # 收盘价宽表（行=日期，列=股票）
bench = load_benchmark()     # 基准指数与无风险利率
uni = load_universe()        # 股票池静态信息与特征
```

## 真实数据

书中第5章《行情数据获取》系统讲解如何用 AkShare / Tushare / BaoStock 抓取真实 A 股数据。
最小演示见：

```bash
uv sync --extra data
uv run python scripts/fetch_data.py --symbol 600519 --start 20230101 --end 20251231
```
