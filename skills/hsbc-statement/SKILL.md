---
name: hsbc-statement
description: HSBC 结单一站式分析 — 自动识别 INVSTM0005 (Premier 综合月结) / INVSTM0019 (WPL 单日) / INVSTM0021 (WPL 月结)，批量处理多 PDF，抽取关键字段，按类型写 MD 入 docs/statements/，归档 raw/decrypted PDF，重生 README.md 时间序列索引。当用户给 HSBC 任意结单 PDF 或问"我这个月利息合理吗 / 我的 portfolio / 我的 WPL 余额"等触发。
---

# hsbc-statement · v0.2

> **依赖**：`pdftotext`（poppler）+ `qpdf` + `pdf-decrypt` skill + Python 3.9+
>
> **输入**：1+ 个 HSBC 结单 PDF（加密或解密均可）
>
> **输出**：MD per PDF + 归档 raw/decrypted + 自动 README.md 索引

## 何时触发

- 用户拖来 HSBC 结单 PDF（`eStatementFile_*.pdf` / 自命名）
- 用户问"我这个月 portfolio / 利息 / spread / WPL 余额 / 净孖展"
- 用户问"我的 HSBC 资产负债"

## 支持的表单

| Form ID | 类型 | 周期 | 关键字段 |
|---|---|---|---|
| `INVSTM0005` (`IPSSTM0005`) | Premier 综合月结 | 月 | Net Position / Deposits / Investments / Credit Facilities / Cards / WPL / Time Deposits / TRB |
| `INVSTM0019` | WPL 投资 + 贷款单日切片 | 日 | Portfolio (UT/SI) / Outstanding / Credit Limit / Net Margin |
| `INVSTM0021` | WPL 投资 + 贷款月结复合 | 月 | 上面所有 + Cash 期初/利息/期末 + Transactions + Charges & Income + 有效年化 + spread vs 1M HIBOR |

## 用法

```bash
# 批量（推荐）— 自动解密 + 抽取 + 写 MD + 归档 PDF + 重生 README
python3 ~/.claude/skills/hsbc-statement/scripts/analyze.py *.pdf

# 指定输出目录（默认 docs/statements/）
python3 .../analyze.py *.pdf --out docs/statements/

# 月结：手动 HIBOR 期间均值（更准）
python3 .../analyze.py monthly.pdf --hibor 2.65

# 月结：实际借款起始日（结单期 ≠ 实借天数时）
python3 .../analyze.py monthly.pdf --start-date 2026-04-22

# 跳过归档（PDF 留原地）
python3 .../analyze.py *.pdf --no-archive

# JSON 输出（不写 MD，便于脚本消费）
python3 .../analyze.py *.pdf --json

# 仅重生 README 索引（不动 PDF / MD）
python3 .../analyze.py --regen-index --out docs/statements/
```

## 文件组织（推荐架构）

```
docs/statements/
├── README.md                          # auto-gen 索引（时间序列总表）
├── raw/                               # 加密原件（gitignore *.pdf）
│   ├── 2026-04-25_hsbc-premier-composite.pdf
│   ├── 2026-04-25_hsbc-wpl-monthly.pdf
│   ├── 2026-04-27_hsbc-wpl-daily.pdf
│   └── 2026-04-28_hsbc-wpl-daily.pdf
├── decrypted/                         # 解密产物（gitignore *-decrypted.pdf）
├── refs/                              # KFS / Tariff 等参考资料
│   └── 2026-03-23_hsbc-wpl-kfs.jpg
├── 2026-04-25_hsbc-premier-composite.md
├── 2026-04-25_hsbc-wpl-monthly.md
├── 2026-04-27_hsbc-wpl-daily.md
└── 2026-04-28_hsbc-wpl-daily.md
```

## 命名规范

文件名：`<YYYY-MM-DD>_hsbc-<kind>.{md,pdf}`

`kind` ∈ `premier-composite` / `wpl-daily` / `wpl-monthly`

后续可扩展：`cc-pulse-rmb` / `cc-diamond-hkd` / `lombard` / ...

## 脱敏规则

写入 MD 时自动脱敏（PDF 原文不动；PDF 已被 `.gitignore`）：

| 原文 | MD 中 |
|---|---|
| `ZENG TIANLI` | `ZENG T*****` |
| `125-433201-380` | `125-433***-***` |

完整账号 / 名字仅保留在本地 `raw/` PDF 中（不进 git）。

## 核心字段抽取

### Premier 综合（INVSTM0005）

- `statement_date` / `ac_no` / `branch`
- `deposits_total` / `investments_total` / `credit_facilities_total` / `credit_cards_total` / `net_position`
- `wpl_credit_limit` / `wpl_outstanding`
- `time_deposits[]`：ccy, principal, rate, start, maturity
- `credit_cards[]`：name, card last 4, ccy, limit, balance, hkd_eq
- `trb_avg` / `trb_period`

### WPL 单日 (INVSTM0019)

- `statement_date` / `period_from`==`period_to` / `ac_no` / `cash_ac_no`
- `holdings[]`：UT / Structured 行
- `ut_hkd` / `si_hkd` / `portfolio_total_hkd` / `usd_hkd`
- `outstanding_loan` / `credit_limit` / `max_credit_limit` / `net_margin_ratio` / `margin_surplus`

### WPL 月结 (INVSTM0021)

含单日全部字段 +：

- `cash_bf` / `cash_interest` / `cash_cf` / `interest_from` / `interest_to` / `interest_days`
- `transactions[]`：买卖 / `charges_income[]`：分红 / 费用
- `effective_rate_pct`：`利息 / 本金 × 365 / 天数 × 100`
- `hibor_1m_pct` / `hibor_source`：HKAB 当前 fixing（默认）/ `--hibor` 手填
- `spread_pct`：`effective − hibor`
- `floored`：true 当 effective ≈ 1.00%（HSBC 1% 地板触发）

## HIBOR 数据源

| 模式 | 源 | 何时用 |
|---|---|---|
| 默认（无 flag） | 抓 HKAB 主页 1M 当前 fixing | 看量级 |
| `--hibor X` | 用户手输 % 期间均值 | 月结期 ≥ 一周，需精确 |
| `--no-hibor` | 不查 | 离线 |

期间均值取法：[hkab.org.hk/en/rates/hibor](https://www.hkab.org.hk/en/rates/hibor) → 历史日期 → 1month → 工作日均值。

## 1% 地板

结单条款明示：`HIBOR + spread < 1% p.a. → 按 1% 收`。脚本判定 `|effective − 1.00%| < 0.05%` → 标 `floored=true`。

## 与其他 skill 的关系

```
用户给 HSBC PDF
    ↓
hsbc-statement (本 skill)
    ├→ 调 pdf-decrypt (前置解密)
    ├→ 抽字段 → MD
    ├→ 归档 raw/decrypted
    └→ 重生 README.md 索引
```

## 改 SSOT

源码：`~/Dev/tools/cc-configs/skills/hsbc-statement/`
分发：`~/.claude/skills/hsbc-statement/`（symlink）

## 历史

- v0.1 (2026-04-29) — 初版 `hsbc-wpl`，仅 INVSTM0019 + 利率反推
- v0.2 (2026-04-29) — 改名 `hsbc-statement`，加 INVSTM0005 / INVSTM0021，多 PDF 批处理，自动归档，README 索引
