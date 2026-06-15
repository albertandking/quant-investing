# 贡献与勘误

欢迎为本书纠错、补充与改进！

## 报告勘误 / 提问

发现**错别字、公式错误、代码报错、表述不清**等问题，请到
[Issues](https://github.com/albertandking/quant-investing/issues) 新建一个 issue，
尽量附上：

- 章节与小节号（如「第9章 9.3.2」）或 notebook 文件名与单元；
- 问题描述；如是代码报错，附上完整报错信息与你的环境（`uv run python --version`）。

## 提交修改（Pull Request）

1. Fork 本仓库并克隆到本地；
2. 安装环境：`uv sync`；生成内置数据：`uv run python scripts/make_sample_data.py`；
3. 修改后本地自检：
   - 代码风格：`uv run ruff check src scripts tests` 与 `uv run ruff format src scripts tests`
   - 测试：`uv run pytest`
   - 若改了 notebook：`uv run jupyter nbconvert --to notebook --execute notebooks/对应文件.ipynb`
   - 若改了正文：`uv run mkdocs build --strict`（确认无断链/缺图）
4. 提交 PR，说明改动内容与动机。

## 写作约定

### 体例

- 正文用简体中文，引号用中文全角「" "」（代码块、admonition 标题 `!!! x "..."`、HTML 属性中的引号保留 ASCII）；
- 小节统一编号 `X.Y`、`X.Y.Z`；
- 代码遵循 PEP8 + 类型注解（见 `pyproject.toml` 的 `[tool.ruff]`）；
- 正文图示由 `scripts/make_figures.py` 生成，存放于 `book/assets/figures/chNN_*.png`。

### 统一的章节模板

每章按以下固定结构写作（与全书保持一致）：

```markdown
# 第X章 标题

[Colab 徽章] [Binder 徽章]

!!! info "配套代码"
    本章示例对应 notebooks/chNN_xxx.ipynb，可逐格运行。

---

## X.1 本章导读：<一句话点出本章要解决的真实问题>

<用问题与直觉开场，再交代本章地图>

## X.2 学习目标

学完本章，你应该能够：
- ……

## X.3 …（正文：先直觉、再公式 `$$...$$`、再数值例子，配 A 股实例）

!!! example "例 X.1　<标题>"
    <带数字的可复算示例>

!!! warning "<陷阱标题>"
    <「看起来对、其实错」的常见错误>

## X.N 本章小结

**必须掌握** … / **理解即可** … / **实践提醒** …

## X.N+1 习题

### 基础概念
**习题X.1（类型）** …
??? tip "参考思路"
    …

## X.N+2 拓展阅读

经典文献 / 教材 / 中文资源 / 在线资源
```

### 代码与数据

- **一章 = 一个正文 md + 一个 notebook**；代码写在 notebook，正文引用导出片段，避免两处维护；
- 复用逻辑（指标、绘图、数据加载、技术指标）抽进 `src/qfin`，统一 `from qfin import ...`；
- notebook 默认用**内置示例数据**，保证断网可跑；联网接口代码放在明确标注的「联网」小节；
- 回测示例**主线统一用 akquant**；其他框架（Backtrader/vectorbt/Qlib）放在标签页 `=== "..."` 中对比。

### 风险提示

涉及策略与收益的章节，须包含教育用途与风险提示，不得表述为投资建议。

感谢你的贡献！
