# 第8章 技术指标与交易信号

!!! info "编写中"
    本章正在编写中，以下为内容骨架与学习目标。配套 notebook：`notebooks/ch08_technical_signals.ipynb`（待补）。

## 8.1 本章导读

技术指标是把价格序列转成「信号」的最直接方式。本章带你实现并理性看待均线、动量、RSI、MACD、布林带。

## 8.2 学习目标

学完本章，你应该能够：

- 计算并解释 SMA/EMA、动量、RSI、MACD、布林带；
- 把指标转化为可回测的买卖信号（含金叉/死叉）；
- 警惕技术指标的过度拟合与「事后看图」错觉；
- 用 `qfin.signals` 复用这些指标。

## 8.3 内容大纲（待编写）

- 8.3 移动平均与均线系统
- 8.4 动量与 RSI
- 8.5 MACD 与布林带
- 8.6 从指标到信号：金叉/死叉与去噪
- 8.7 本章小结 / 习题 / 拓展阅读

> 本章指标已在 `qfin.signals` 中实现（`sma`、`ema`、`rsi`、`macd`、`bollinger_bands`、`crossover`、`crossunder`）。
