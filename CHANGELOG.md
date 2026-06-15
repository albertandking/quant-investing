# 更新日志

本项目版本遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 工程

- 初始化仓库脚手架：uv 管理（Python 3.14，兼容 3.11+）、`mkdocs-material` 成书、
  GitHub Actions 自动部署到 GitHub Pages、双许可（代码 MIT / 正文 CC BY 4.0）。
- `qfin` 复用工具包（data / metrics / plotting / signals）与离线合成数据集
  （多股票日度 OHLCV 面板、基准指数、股票池信息），冒烟测试覆盖。
- 全书 6 部分 20 章 + 附录 A–E 的导航与占位骨架。

### 内容

- 首页、前言、第1章《量化投资导论》（含环境搭建）。
- 样板章节：第5章《行情数据获取》（AkShare/Tushare/BaoStock 多数据源对比）、
  第16章《事件驱动回测》（akquant 主线，Backtrader/vectorbt/Qlib 对比）。
