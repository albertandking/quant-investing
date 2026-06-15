# 第16章 事件驱动回测（akquant）

[![在 Colab 打开](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/albertandking/quant-investing/blob/main/notebooks/ch16_event_driven_backtest.ipynb) [![在 Binder 打开](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/albertandking/quant-investing/main?labpath=notebooks/ch16_event_driven_backtest.ipynb)

!!! info "配套代码"
    本章示例对应 `notebooks/ch16_event_driven_backtest.ipynb`。主线示例需安装回测框架：`uv sync --extra quant`（akquant）；对比示例需 `uv sync --extra compare`（backtrader / vectorbt）。

---

## 16.1 本章导读：从「向量化」到「事件驱动」

第15章我们用**向量化**方式做过回测：用 `持仓 = 信号.shift(1)`，一次性把所有持仓和收益算出来。它快、适合海量参数扫描，但对成交细节做了理想化假设（满仓成交、无逐笔风控、无未成交订单）。

**事件驱动回测**则**逐根 K 线（bar）推进**：每来一根 bar，策略决定下不下单，引擎模拟撮合、更新持仓与现金、记录净值。它更慢，但更贴近真实交易，能加入仓位管理、止损、滑点、分批成交等真实约束。

本章主线用 **akquant**——akshare 生态的开源事件驱动回测框架（**Rust 内核 + Python 接口**，速度快），并在标签页中对比 **Backtrader / vectorbt / Qlib**，方便你迁移到熟悉的工具。

## 16.2 学习目标

学完本章，你应该能够：

- 说清向量化回测与事件驱动回测的区别与各自适用场景；
- 用 akquant 写一个最简策略（`on_bar` 回调），跑通回测并读懂绩效；
- 把内置 OHLCV 数据喂给回测引擎，画出净值曲线；
- 了解 Backtrader / vectorbt / Qlib 的等价写法与定位差异。

## 16.3 事件驱动的核心概念（akquant）

akquant 的策略写法是**继承 `Strategy`、实现 `on_bar(bar)` 回调**：

| 概念 | 说明 |
|---|---|
| `Strategy.on_bar(bar)` | 每根 K 线回调一次；`bar` 提供 `open/high/low/close/symbol/timestamp_iso` 等 |
| `self.buy(symbol=, quantity=)` | 下买单 |
| `self.close_position(symbol=)` | 平仓 |
| `self.get_position(symbol)` | 查询当前持仓数量 |
| `self.get_history(count, field="close")` | 取近 `count` 根某字段历史（返回 NumPy 数组） |
| `aq.run_backtest(data, strategy, symbols, initial_cash, history_depth=, t_plus_one=)` | 运行回测，返回 `BacktestResult` |
| `result` / `result.metrics` / `result.equity_curve` | 绩效指标、指标包装、净值曲线 |

## 16.4 最小示例：均线交叉策略

策略逻辑：5 日均线上穿 20 日均线（金叉）买入，下穿（死叉）平仓。我们直接用内置 OHLCV 数据（断网可跑），它本就含 `open/high/low/close/volume`，无需再伪造。

=== "akquant（主线）"

    ```python
    # 安装：uv sync --extra quant
    import akquant as aq
    from akquant import Strategy

    from qfin import load_prices

    # 取一只股票，整理成 akquant 需要的列（date + OHLCV）
    df = (
        load_prices()
        .query("symbol == 'STK001'")
        .sort_values("date")
        .reset_index(drop=True)
    )

    class MaCross(Strategy):
        fast, slow = 5, 20

        def on_bar(self, bar):
            closes = self.get_history(self.slow, field="close")   # 近 slow 根收盘（ndarray）
            if closes is None or len(closes) < self.slow:
                return
            ma_fast = closes[-self.fast:].mean()
            ma_slow = closes.mean()
            pos = self.get_position(bar.symbol)
            if pos == 0 and ma_fast > ma_slow:        # 金叉买入
                self.buy(symbol=bar.symbol, quantity=100)
            elif pos > 0 and ma_fast < ma_slow:       # 死叉平仓
                self.close_position(symbol=bar.symbol)

    result = aq.run_backtest(
        data=df, strategy=MaCross, symbols="STK001",
        initial_cash=100_000.0,
        history_depth=30,        # 让 get_history 至少能取到 slow 根
        t_plus_one=True,         # A 股 T+1：当日买入次日才可卖
    )
    print(result)                       # 总收益、夏普、最大回撤、胜率等一应俱全
    result.equity_curve.plot(title="akquant 事件驱动回测净值曲线")
    ```

    > 以上基于 akquant 0.2.45 实测跑通。`get_history(count, field=...)` 返回近 `count` 根的 NumPy 数组；历史深度可用 `history_depth=` 预留。不同版本 API 可能微调，以 `import akquant; help(akquant.Strategy)` 为准。

=== "Backtrader（对比）"

    ```python
    # 安装：uv sync --extra compare
    import backtrader as bt

    class MaCross(bt.Strategy):
        params = dict(fast=5, slow=20)

        def __init__(self):
            ma_fast = bt.ind.SMA(period=self.p.fast)
            ma_slow = bt.ind.SMA(period=self.p.slow)
            self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)

        def next(self):
            if not self.position and self.crossover > 0:
                self.buy(size=100)
            elif self.position and self.crossover < 0:
                self.close()

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MaCross)
    # cerebro.adddata(bt.feeds.PandasData(dataname=df_indexed_by_date))
    cerebro.broker.setcash(100_000.0)
    cerebro.run()
    print(cerebro.broker.getvalue())
    ```

    定位：社区最大、文档最全、指标丰富；纯 Python，速度一般，适合教学与中低频。

=== "vectorbt（对比）"

    ```python
    # 安装：uv sync --extra compare
    import vectorbt as vbt

    close = df.set_index("date")["close"]
    fast = vbt.MA.run(close, 5).ma
    slow = vbt.MA.run(close, 20).ma
    entries = fast.vbt.crossed_above(slow)
    exits = fast.vbt.crossed_below(slow)

    pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=100_000)
    print(pf.stats())
    pf.plot().show()
    ```

    定位：**向量化**、极快，适合成千上万组参数扫描；API 较陡，撮合细节不如事件驱动精细。

=== "Qlib（对比）"

    ```python
    # 微软开源的 AI 量化平台，工作流式（数据/模型/回测一体），偏机构与 ML 流水线
    # 通常通过 qrun 配置文件或 workflow API 驱动，学习曲线较陡，这里仅示意定位。
    # pip install pyqlib
    ```

    定位：**工业级 AI 量化平台**，内置数据/特征/模型/回测全流程，适合做机器学习选股流水线（见第19章），轻量策略研究用它偏重。

!!! note "怎么选框架"
    - **快速研究、参数扫描** → vectorbt（向量化）。
    - **贴近真实撮合、加风控** → akquant / Backtrader（事件驱动）。
    - **机器学习选股全流程** → Qlib。

    本书后续章节统一用 **akquant** 作为事件驱动主线，保证示例可一致复现。

## 16.5 读懂回测结果

`run_backtest` 返回的 `result` 至少包含这些你必须看的指标（详解见第17章）：

| 指标 | 含义 | 看什么 |
|---|---|---|
| 年化收益 | 几何年化 | 高不一定好，要结合风险 |
| 夏普比率 | 单位波动的超额收益 | 越高越好，<1 通常偏弱 |
| 最大回撤 | 从峰值的最大跌幅 | 决定你能不能拿得住 |
| 胜率 / 换手 | 盈利交易占比 / 交易频繁度 | 高换手对成本极敏感 |

!!! warning "别只看净值曲线"
    一条漂亮的净值曲线可能来自前视偏差、过拟合或忽略了交易成本。务必把第15章的陷阱清单和本章的绩效指标**一起**用来判断策略是否可信。

## 16.6 本章小结

**必须掌握**

1. 事件驱动逐 bar 撮合、贴近真实；向量化一次性计算、快但理想化——两者互补。
2. akquant 的范式：继承 `Strategy` → 实现 `on_bar` → `aq.run_backtest(...)` → 读 `result`。
3. 回测要同时看年化、夏普、最大回撤、换手，而非只盯净值曲线。

**理解即可**

4. Backtrader（教学友好）、vectorbt（向量化扫描）、Qlib（ML 全流程）的定位差异。

**实践提醒**

先在内置数据上把框架跑通，再换成真实行情（第5章）。换数据时别忘了前复权与 T+1 滞后。

## 16.7 习题

**习题16.1（跑通主线）** 安装 akquant，把 16.4 的均线交叉策略在 `STK001` 上跑通，打印绩效并画净值曲线。

??? tip "参考思路"
    `uv sync --extra quant`；内置数据已含 OHLCV，直接 `query("symbol=='STK001'")`。

**习题16.2（换参数）** 把快慢均线改成 (10, 60)，对比夏普与最大回撤的变化，思考是否过拟合（呼应第15章）。

??? tip "参考思路"
    单点最优往往不稳健；最好扫一组参数看是否存在「参数高原」。

**习题16.3（换框架）** 选 Backtrader 或 vectorbt，复现同一策略，对比两套结果是否一致、为什么可能不同。

??? tip "参考思路"
    差异常来自撮合假设（成交价、手续费、最小变动单位）不同。

## 16.8 拓展阅读

- **akquant**：<https://github.com/akfamily/akquant>。
- **Backtrader**：<https://www.backtrader.com/docu/>。
- **vectorbt**：<https://vectorbt.dev/>。
- **Qlib**：<https://github.com/microsoft/qlib>。
- 绩效指标与归因详见第17章；回测陷阱见第15章。
