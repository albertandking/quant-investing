# 量化投资（Quantitative Investing）

面向**中国本科生、研究生与量化投资爱好者**的开源量化投资实战教程。**零编程基础起步**，带你从 Python 与统计基础，一路走到 A 股因子、策略、回测、风控与实盘。

- **正文**用 Markdown 编写（`book/` 目录）
- **代码**放在 Jupyter Notebook 中（`notebooks/` 目录），可本地逐格运行
- 正文按需**引用 / 嵌入** notebook 的代码与输出（通过 `scripts/export_notebooks.py` 手动导出）
- 数据：**内置示例数据集**（离线可跑）+ **中国市场接口**（akshare / tushare / baostock，联网抓取）
- 回测：主线用事件驱动框架 **akquant**，并对比 **Backtrader / vectorbt / Qlib**
- 环境：**uv** 管理，推荐 **Python 3.14**（兼容 3.11+）；成书：**MkDocs + Material 主题**
- 复现：`uv.lock` 锁定全部依赖精确版本；可读版本表见[附录A](book/appendix/a-setup.md)

> 本书是《[金融数据科学](https://github.com/albertandking/financial-data-science)》的姊妹书：那本讲方法与工具（广），本书讲量化投资流水线与策略实战（专、深），且**完全自包含、零基础可读**。

---

## 在线访问

- 📖 **在线阅读**（GitHub Pages）：<https://albertandking.github.io/quant-investing/>
- ▶️ **在线运行代码**：每章正文顶部都有 **Colab** 与 **Binder** 徽章，点开即可在云端运行该章 notebook（无需本地环境）。
  - Colab 会自动克隆本仓库并安装 `qfin` 包（notebook 内置「自举单元」，本地运行时自动跳过）；
  - Binder 通过 `binder/` 下的配置自动装好环境与内置数据。

> 网站由 GitHub Actions 自动部署：push 到 `main` → 构建 MkDocs → 发布到 Pages（见 `.github/workflows/deploy.yml`）。
> 首次启用：仓库 **Settings → Pages → Source 选「GitHub Actions」**。

---

## 一、目录结构

```
ff/
├── pyproject.toml          # uv 项目与依赖定义
├── uv.lock                 # 锁定版本（提交入库，保证复现）
├── .python-version         # Python 版本（3.14）
├── mkdocs.yml              # 成书配置与章节导航
├── README.md
│
├── book/                   # 【正文】MkDocs 文档源（Markdown）
│   ├── index.md            #   首页
│   ├── preface.md          #   前言
│   ├── assets/figures/     #   正文图示（PNG，由 scripts/make_figures.py 生成）
│   ├── part1/              #   第一部分·入门与基础
│   ├── part2/              #   第二部分·数据
│   ├── part3/              #   第三部分·信号与因子
│   ├── part4/              #   第四部分·策略
│   ├── part5/              #   第五部分·回测
│   ├── part6/              #   第六部分·风险与实盘
│   └── appendix/           #   附录 A–E
│
├── notebooks/              # 【代码】各章可执行 Jupyter Notebook
│
├── src/qfin/               # 全书复用的工具包（import qfin）
│   ├── data.py             #   内置数据集加载（OHLCV 面板、基准、股票池）
│   ├── metrics.py          #   收益、风险、绩效等指标
│   ├── plotting.py         #   统一的中文绘图样式
│   └── signals.py          #   常用技术指标与交易信号
│
├── data/
│   ├── raw/                #   原始/下载数据（不入库）
│   ├── processed/          #   清洗好的内置示例数据（入库，离线可跑）
│   └── README.md           #   数据说明
│
├── scripts/
│   ├── make_sample_data.py #   离线生成内置示例数据集
│   ├── fetch_data.py       #   从中国市场接口抓取真实数据
│   └── export_notebooks.py #   notebook -> markdown 手动导出
│
└── tests/                  # 冒烟测试，保证代码可跑
```

---

## 二、快速开始

### 1. 安装环境（一次）

```bash
# 安装核心依赖 + 成书工具链（uv 会自动下载 Python 3.14）
uv sync

# 如需联网抓取中国市场数据，额外安装 data 组
uv sync --extra data

# 主线回测框架 akquant（第16章）
uv sync --extra quant

# 对比用回测框架 / 机器学习章节，按需安装
uv sync --extra compare
uv sync --extra advanced
```

### 2. 生成内置示例数据（一次，离线）

```bash
uv run python scripts/make_sample_data.py
```

### 3. 运行书中代码

```bash
# 启动 Jupyter，逐章打开 notebooks/ 下的 .ipynb
uv run jupyter lab

# 或命令行执行某个 notebook 验证可跑
uv run jupyter nbconvert --to notebook --execute notebooks/ch01_introduction.ipynb --stdout > /dev/null
```

### 4. 本地预览整本书

```bash
# 把 notebook 的代码与输出导出为 markdown 片段
uv run python scripts/export_notebooks.py

# 启动本地文档服务器，浏览器打开 http://127.0.0.1:8000
uv run mkdocs serve

# 导出静态网站到 site/
uv run mkdocs build
```

---

## 三、写作约定

- **一章 = 一个 `book/partX/NN-题目.md` + 一个 `notebooks/chNN_主题.ipynb`**
- 正文里需要展示代码/图表时，引用 notebook 导出的片段，避免代码两处维护
- 所有 notebook 默认依赖**内置示例数据**，保证**断网也能跑**；用到联网接口的代码放在明确标注的「联网」小节
- 复用逻辑（指标计算、绘图样式、数据加载、技术指标）抽进 `src/qfin`，正文与 notebook 都 `from qfin import ...`

---

## 四、许可、引用与贡献

- **许可证**：代码（`src/`、`scripts/`、`notebooks/`）采用 **MIT**；正文与图表（`book/`）采用 **CC BY 4.0**。详见 [`LICENSE`](LICENSE)。
- **如何引用**：见 [`CITATION.cff`](CITATION.cff)（仓库页有「Cite this repository」按钮）。
- **勘误与贡献**：发现问题请提 [Issue](https://github.com/albertandking/quant-investing/issues)，参与改进见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
- **更新日志**：见 [`CHANGELOG.md`](CHANGELOG.md)。

> ⚠️ **风险提示**：本书所有内容仅用于教育与研究目的，**不构成任何投资建议**。书中数据多为合成示例，策略示例不代表真实收益。量化投资有风险，入市需谨慎。
