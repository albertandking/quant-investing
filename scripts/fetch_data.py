"""从中国市场接口抓取真实行情（联网，按需）。

默认用 AkShare（免注册）抓取单只 A 股的前复权日线，存到 data/raw/（不入库）。
需要先安装 data 组依赖：

    uv sync --extra data

示例：
    uv run python scripts/fetch_data.py --symbol 600519 --start 20230101 --end 20251231

注意：本脚本仅做最小演示；更系统的数据获取（多数据源对比、复权、清洗）
见正文第5章《行情数据获取》。
"""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"


def fetch_one(symbol: str, start: str, end: str) -> Path:
    """用 AkShare 抓取单只 A 股前复权日线并保存到 data/raw/。"""
    try:
        import akshare as ak
    except ImportError as exc:  # noqa: F841
        raise SystemExit(
            "未安装 akshare。请先运行：uv sync --extra data"
        ) from exc

    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start,
        end_date=end,
        adjust="qfq",  # 前复权
    )
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = RAW_DIR / f"{symbol}_{start}_{end}.parquet"
    df.to_parquet(out, index=False)
    print(f"已保存 {len(df)} 行到 {out}")
    return out


def main() -> None:
    """命令行入口：解析参数并抓取数据。"""
    parser = argparse.ArgumentParser(description="抓取单只 A 股日线（AkShare，前复权）")
    parser.add_argument("--symbol", required=True, help="股票代码，如 600519")
    parser.add_argument("--start", default="20230101", help="开始日期 YYYYMMDD")
    parser.add_argument("--end", default="20251231", help="结束日期 YYYYMMDD")
    args = parser.parse_args()
    fetch_one(args.symbol, args.start, args.end)


if __name__ == "__main__":
    main()
