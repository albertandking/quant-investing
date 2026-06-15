"""统一的绘图配置与主题。

量化图表常需显示中文（标的名称、轴标签），且全书希望视觉风格一致。
本模块集中处理：中文字体、统一配色、网格、边框、字号等，
让所有章节的图表风格统一、清爽、便于阅读。

每章 notebook 开头调用一次 `set_chinese_font()` 即可应用全套主题。
"""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
from cycler import cycler

# 按操作系统优先尝试的中文字体（Windows / macOS / Linux）
_CJK_FONTS = [
    "Microsoft YaHei",  # Windows 微软雅黑
    "SimHei",  # Windows 黑体
    "PingFang SC",  # macOS
    "Heiti SC",  # macOS
    "Noto Sans CJK SC",  # Linux
    "WenQuanYi Micro Hei",
]

# 全书统一配色（清晰、可区分、偏专业），供需要时直接引用
PALETTE = [
    "#2E5A88",  # 深蓝
    "#C0504D",  # 砖红
    "#4E9A65",  # 绿
    "#8064A2",  # 紫
    "#C9A227",  # 金
    "#4FA7B8",  # 青
    "#E08E45",  # 橙
    "#7F6A57",  # 棕
]

# A股习惯：红涨绿跌（与国际相反），需要时引用
COLOR_UP = "#C0504D"  # 涨：红
COLOR_DOWN = "#4E9A65"  # 跌：绿


def _pick_cjk_font() -> None:
    available = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
    for font in _CJK_FONTS:
        if font in available:
            plt.rcParams["font.sans-serif"] = [font]
            return


def set_chinese_font() -> None:
    """配置中文字体并应用全书统一绘图主题。

    在每章 notebook 开头调用一次：

        from qfin import set_chinese_font
        set_chinese_font()

    应用内容：中文字体与负号、统一配色循环、轻量网格、去除上/右边框、
    统一字号与图例样式、合适的图幅与分辨率。
    """
    _pick_cjk_font()
    plt.rcParams.update(
        {
            # 中文与负号
            "axes.unicode_minus": False,
            # 图幅与分辨率
            "figure.figsize": (9, 5),
            "figure.dpi": 110,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            # 统一配色
            "axes.prop_cycle": cycler(color=PALETTE),
            # 网格（置于数据下方，轻量）
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": "#B0B0B0",
            "grid.alpha": 0.30,
            "grid.linewidth": 0.6,
            # 边框：去除上、右
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#444444",
            "axes.linewidth": 0.9,
            # 字号与标题
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "axes.labelcolor": "#222222",
            # 线条与图例
            "lines.linewidth": 1.8,
            "legend.frameon": False,
            "legend.fontsize": 10,
        }
    )
