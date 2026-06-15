# 第5章 行情数据获取

[![在 Colab 打开](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/albertandking/quant-investing/blob/main/notebooks/ch05_data_acquisition.ipynb) [![在 Binder 打开](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/albertandking/quant-investing/main?labpath=notebooks/ch05_data_acquisition.ipynb)

!!! info "配套代码"
    本章示例对应 `notebooks/ch05_data_acquisition.ipynb`。**联网小节**需要先安装数据依赖：`uv sync --extra data`；离线小节用内置数据即可运行。

---

## 5.1 本章导读：数据是策略的地基

再聪明的策略，喂进去错的数据也只会得到错的结论。本章解决量化的第一步：**把干净、正确、对齐好的行情数据拿到手**。

A 股没有像美股那样统一免费的高质量数据源，但有几个社区维护的优秀接口。本章会**并排对比三个主流免费数据源**——AkShare、Tushare、BaoStock——告诉你各自怎么用、有什么坑，并重点讲一个新手最容易忽视、却足以毁掉整个回测的问题：**复权**。

## 5.2 学习目标

学完本章，你应该能够：

- 说出 A 股行情数据的常见字段（OHLCV）与含义；
- 用 AkShare / Tushare / BaoStock 中至少一个，抓取一只股票的日线数据；
- 解释**前复权、后复权、不复权**的区别，并知道回测该用哪种；
- 把抓到的数据清洗、对齐成可直接使用的格式，并存成 parquet；
- 在内置数据上完成同样的加载与清洗流程（断网可跑）。

## 5.3 行情数据长什么样

最常用的是**日线行情**，每只股票每个交易日一行，核心字段是 **OHLCV**：

| 字段 | 含义 |
|---|---|
| `open` | 开盘价 |
| `high` | 最高价 |
| `low` | 最低价 |
| `close` | 收盘价 |
| `volume` | 成交量（手 / 股） |

本书内置数据就是这个结构，可离线加载：

```python
from qfin import load_prices

panel = load_prices()          # 长表：每个 (date, symbol) 一行
print(panel.head())
print(panel["symbol"].nunique(), "只股票")
```

## 5.4 三大免费数据源对比

下面用三个标签页给出**抓取同一类数据**（某只 A 股日线）的等价写法。新手建议从 **AkShare** 起步（免注册、最简单），这也是本书的主线数据源。

=== "AkShare（主线，免注册）"

    ```python
    # 安装：uv sync --extra data
    import akshare as ak

    # 前复权日线；symbol 用 6 位代码，不带交易所后缀
    df = ak.stock_zh_a_hist(
        symbol="600519",
        period="daily",
        start_date="20230101",
        end_date="20251231",
        adjust="qfq",          # qfq=前复权, hfq=后复权, ""=不复权
    )
    print(df.head())
    ```

    优点：免注册、覆盖广（股票/期货/基金/宏观/另类）、更新活跃。
    注意：返回列名为中文（日期/开盘/收盘…），需自行重命名；偶有接口变动。

=== "Tushare（需 token）"

    ```python
    # 安装：uv sync --extra data；需到 tushare.pro 注册获取 token，部分接口要积分
    import tushare as ts

    pro = ts.pro_api("你的_TOKEN")
    df = pro.daily(
        ts_code="600519.SH",   # 注意带交易所后缀
        start_date="20230101",
        end_date="20251231",
    )
    # daily 接口为不复权价；复权需配合 adj_factor 或 pro_bar
    df = ts.pro_bar(ts_code="600519.SH", adj="qfq",
                    start_date="20230101", end_date="20251231")
    print(df.head())
    ```

    优点：数据规范、字段统一、机构常用。
    注意：需注册 token，高频/历史接口消耗积分。

=== "BaoStock（免费历史）"

    ```python
    # 安装：uv sync --extra data
    import baostock as bs

    bs.login()
    rs = bs.query_history_k_data_plus(
        "sh.600519",                       # 带交易所前缀
        "date,open,high,low,close,volume",
        start_date="2023-01-01",
        end_date="2025-12-31",
        frequency="d",
        adjustflag="2",                    # 1=后复权, 2=前复权, 3=不复权
    )
    df = rs.get_data()
    bs.logout()
    print(df.head())
    ```

    优点：完全免费、历史数据稳定、适合批量下载。
    注意：需 login/logout，返回均为字符串，需手动转数值类型。

!!! tip "怎么选"
    - **学习与个人研究**：AkShare 足够，免注册、上手最快。
    - **要稳定字段与规范接口**：Tushare（愿意注册并攒积分）。
    - **批量下载长历史、追求免费稳定**：BaoStock。

    三者的更细对比（字段、频率、限速、复权口径）见[附录C](../appendix/c-data-framework.md)。

## 5.5 复权：最容易被忽视的致命细节

股票会**除权除息**（分红、送股）。除权当天，价格会「跳水」一截——但这不是真的下跌，只是把分红/送股从股价里扣出去了。如果直接用**不复权**价格回测，模型会把这种技术性跳空当成真实暴跌，得出完全错误的信号。

- **不复权**：原始成交价，有除权跳空，**不能直接用于跨除权日的回测**。
- **前复权（qfq）**：以**当前价**为基准，把历史价格按比例向下调整，使曲线连续。**最常用于回测**。
- **后复权（hfq）**：以**上市首日价**为基准向后调整，适合计算长期累计收益。

!!! warning "回测请用前复权"
    用不复权数据算出的「动量」「均线」全是错的——除权日的假跳空会污染一切技术指标。**做回测，默认用前复权（qfq）**。本书的 `fetch_data.py` 默认就取 `adjust="qfq"`。

!!! example "例 5.1　复权的影响"
    某股票除权前一日收盘 100 元，10 送 10 后理论除权价变为 50 元。不复权数据会显示「一夜下跌 50%」；而前复权会把除权前的 100 元调整为 50 元（及更早价格同比例下调），使收益曲线平滑连续，真实反映「持有者并未亏损」。

## 5.6 清洗与对齐（内置数据，离线可跑）

无论数据来自哪个源，拿到后都要做同样几步：统一列名与类型、按日期排序、设好索引、处理缺失、存盘。下面用**内置数据**演示这套流程（断网可跑）：

```python
import pandas as pd

from qfin import load_prices

panel = load_prices()

# 1) 取一只股票，按日期排序
one = panel[panel["symbol"] == "STK001"].sort_values("date").copy()

# 2) 设日期索引，确保数值类型
one = one.set_index("date")
ohlcv = ["open", "high", "low", "close", "volume"]
one[ohlcv] = one[ohlcv].apply(pd.to_numeric, errors="coerce")

# 3) 处理缺失（停牌日等）：这里用前值填充收盘，演示用
one["close"] = one["close"].ffill()

# 4) 存成 parquet（比 CSV 更快更小，保留类型）
one.to_parquet("data/raw/STK001_clean.parquet")
print(one.tail())
```

把多只股票的收盘价对齐成一张宽表，是后续因子/组合计算的标准输入：

```python
from qfin import load_close

close = load_close()            # 行=日期，列=股票代码，值=收盘价
print(close.shape)              # (交易日数, 股票数)
print(close.iloc[-3:, :4])
```

## 5.7 本章小结

**必须掌握**

1. 行情核心字段是 OHLCV；A 股代码在不同源有不同写法（纯 6 位 / 带后缀 / 带前缀）。
2. **回测必须用前复权（qfq）**，否则除权跳空会污染全部技术指标与收益。
3. 拿到数据的固定动作：统一列名与类型 → 排序设索引 → 处理缺失 → 存 parquet。

**理解即可**

4. AkShare / Tushare / BaoStock 各有取舍；本书主线用 AkShare。
5. 多只股票对齐成「收盘价宽表」是横截面分析的标准输入。

**实践提醒**

联网接口偶尔会变动或限速，把抓到的数据**及时存盘**（parquet），不要每次重跑都重新抓。

## 5.8 习题

### 数据获取

**习题5.1（抓一只股票）** 用 AkShare 抓取任意一只 A 股 2023 年至今的前复权日线，重命名为英文 OHLCV 列并存成 parquet。

??? tip "参考思路"
    `ak.stock_zh_a_hist(symbol=..., adjust="qfq")`，再 `df.rename(columns={"日期":"date","开盘":"open",...})`。

**习题5.2（复权对比）** 对同一只股票分别抓 `adjust=""` 与 `adjust="qfq"`，把两条收盘价曲线画在一起，找出除权跳空的位置。

??? tip "参考思路"
    不复权曲线会在除权日出现明显「断崖」，前复权则连续。

### 清洗对齐

**习题5.3（多只对齐）** 抓 3 只股票，拼成一张以日期为索引、股票为列的收盘价宽表，注意对齐交易日。

??? tip "参考思路"
    各自设 `date` 索引后 `pd.concat([...], axis=1, keys=symbols)`，或逐列 join。

## 5.9 拓展阅读

- **AkShare 文档**：<https://akshare.akfamily.xyz/>（数据接口大全）。
- **Tushare Pro 文档**：<https://tushare.pro/document/2>。
- **BaoStock 文档**：<http://baostock.com/>。
- 复权原理与口径差异，见[附录C](../appendix/c-data-framework.md)。
