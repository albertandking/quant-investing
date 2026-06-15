"""把 notebooks/ 下的 Jupyter Notebook 手动导出为 Markdown，供正文引用。

工作流：
1. 在 notebooks/chNN_*.ipynb 中编写并运行代码；
2. 运行本脚本，将每个 notebook 转成 Markdown（含代码与输出），
   输出到 book/_generated/（该目录默认不入库）；
3. 在 book/ 的正文 Markdown 中用片段引用导出结果，例如：

       --8<-- "_generated/ch01_introduction.md"

   （需要时可在 mkdocs 中启用 pymdownx.snippets 扩展。）

运行：
    uv run python scripts/export_notebooks.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NB_DIR = REPO_ROOT / "notebooks"
OUT_DIR = REPO_ROOT / "book" / "_generated"


def export_one(nb_path: Path) -> Path:
    """先执行 notebook（保证输出最新），再转 markdown。"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "markdown",
        "--execute",
        "--output-dir",
        str(OUT_DIR),
        str(nb_path),
    ]
    subprocess.run(cmd, check=True)
    return OUT_DIR / (nb_path.stem + ".md")


def main() -> None:
    """执行并导出 notebooks/ 下的全部 notebook 为 Markdown。"""
    notebooks = sorted(NB_DIR.glob("*.ipynb"))
    if not notebooks:
        print("notebooks/ 下没有找到 .ipynb，跳过。")
        return
    for nb in notebooks:
        if ".ipynb_checkpoints" in str(nb):
            continue
        print(f"导出 {nb.name} ...")
        out = export_one(nb)
        print(f"  -> {out}")
    print("完成。可在正文中用 --8<-- 片段语法引用 book/_generated/ 下的结果。")


if __name__ == "__main__":
    main()
