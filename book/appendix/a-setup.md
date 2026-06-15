# 附录A 环境与工具链配置

本附录汇总本书的环境配置、依赖说明与常见报错排查。

## A.1 安装 uv

uv 是一个极快的 Python 包与项目管理器，本书用它统一管理 Python 版本与依赖。

=== "Windows（PowerShell）"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "macOS / Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

验证：重开终端运行 `uv --version`。

## A.2 安装依赖（依赖组）

```bash
uv sync                  # 核心 + 成书工具链 + 测试工具（默认）
uv sync --extra data     # + 数据接口（akshare / tushare / baostock）
uv sync --extra quant    # + 主线回测框架 akquant
uv sync --extra compare  # + 对比框架 backtrader / vectorbt
uv sync --extra advanced # + 机器学习（lightgbm / xgboost）
```

| extra 组 | 内容 | 对应章节 |
|---|---|---|
| （默认） | numpy/pandas/scipy/matplotlib/sklearn/… + mkdocs + jupyter | 全书基础 |
| `data` | akshare, tushare, baostock, requests | 第5、6章 |
| `quant` | akquant | 第16章（主线） |
| `compare` | backtrader, vectorbt | 第16章（对比） |
| `advanced` | lightgbm, xgboost | 第19章 |

## A.3 生成内置数据

```bash
uv run python scripts/make_sample_data.py
```

生成的数据集见 [`data/README.md`](https://github.com/albertandking/quant-investing/blob/main/data/README.md)。

## A.4 运行与预览

```bash
uv run jupyter lab                       # 运行书中 notebook
uv run mkdocs serve                      # 本地预览整本书（http://127.0.0.1:8000）
uv run python scripts/export_notebooks.py  # 导出 notebook 为 markdown 片段
uv run pytest                            # 运行冒烟测试
```

## A.5 国内加速（可选）

若 `uv sync` 下载缓慢，可配置 PyPI 镜像（如清华 TUNA）：

```bash
# 临时：
uv sync --default-index https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
# 或在环境变量中设置 UV_DEFAULT_INDEX
```

## A.6 常见报错

| 现象 | 原因 | 解决 |
|---|---|---|
| `FileNotFoundError: ...prices.parquet` | 未生成内置数据 | 运行 `uv run python scripts/make_sample_data.py` |
| 图中中文显示成方框 | 缺中文字体 | `set_chinese_font()` 会自动选择；仍异常见下方字体说明 |
| `ImportError: akshare/akquant` | 未装对应 extra | `uv sync --extra data` / `--extra quant` |
| `mkdocs build --strict` 报断链 | 链接或图片路径错误 | 按提示修正相对路径 |

中文字体：Windows 自带「微软雅黑」「黑体」，macOS 自带「PingFang SC」，Linux 可安装 `fonts-noto-cjk`。

## A.7 版本参考表（待补）

正式发布时，会在此列出 `uv.lock` 锁定的关键依赖版本，便于复现。
