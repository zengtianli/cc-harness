---
name: hsbc-wpl
description: HSBC Wealth Portfolio Lending (滙財組合貸款) 月结单分析 — 解码 PDF（先用 pdf-decrypt skill 解密）→ pdftotext 提取 → 反推有效年化利率 → 推断 spread vs 1M HIBOR → 输出报告 / 写入 docs/statements/。当用户给 HSBC INVSTM0019 类结单 PDF 或问"我的利率基准/spread 多少 / 这个月利息合理吗"时触发。
---

# hsbc-wpl · v0.1

> **依赖**：`pdftotext`（poppler，`brew install poppler`）+ `qpdf`（解密前置，由 pdf-decrypt skill 调）+ Python 3.9+
>
> **输入**：解密后的 HSBC `INVSTM0019` 综合结单 PDF
>
> **输出**：终端报告 / `--json` / 可粘贴的 Markdown 节

## 何时触发

- 用户给 HSBC `INVSTM0019` 类结单（投资 + WPL 综合结单）
- 用户问"我的利率基准是多少 / 利率多少 / spread 多少 / 这次利息合不合理 / 信贷限额是多少 / 净孖展比率"
- 用户拍照/截图 HSBC HK Easy Invest / Online Banking 的 WPL 页面

## 解密前置

PDF 加密 → 先跑 `pdf-decrypt` skill：

```bash
python3 ~/.claude/skills/pdf-decrypt/scripts/decrypt.py /path/file.pdf
# 产出 /path/file-decrypted.pdf
```

再喂给本 skill。

## 用法

```bash
# 基础（自动抓 HKAB 当前 1M HIBOR）
python3 ~/Dev/tools/cc-configs/skills/hsbc-wpl/scripts/analyze.py file-decrypted.pdf

# 用历史 HIBOR avg（推算 spread 更准）
python3 .../analyze.py file.pdf --hibor 2.65

# 跳过 HIBOR 查（只算有效年化）
python3 .../analyze.py file.pdf --no-hibor

# JSON 输出，便于后续脚本消费
python3 .../analyze.py file.pdf --json
```

## 抽取的字段

| 字段 | 来源 PDF 区块 |
|---|---|
| `statement_date` | Date 日期 |
| `ac_name` / `ac_no` / `branch` | 户口头部 |
| `ut_hkd` / `si_hkd` / `portfolio_total_hkd` / `usd_hkd` | Portfolio summary |
| `cash_bf` / `cash_interest` / `cash_cf` | Cash Account Summary |
| `interest_from` / `interest_to` / `interest_days` | DEBIT INTEREST 行的期间 |
| `outstanding_loan` / `credit_limit` / `max_credit_limit` | Net Margin Ratio + Details of financial accommodation |
| `net_margin_ratio` / `margin_surplus` | Net Margin block |
| `effective_rate_pct` | 算: `interest / cash_bf × (365 / days) × 100` |
| `hibor_1m_pct` / `hibor_source` | HKAB 当前 1M HIBOR（自动） / `--hibor` 手填 |
| `spread_pct` | `effective_rate_pct − hibor_1m_pct` |
| `floored` | true 当 `effective ≈ 1.00%`（HSBC 1% p.a. 地板触发） |

## HIBOR 数据源

| 模式 | 源 | 何时用 |
|---|---|---|
| 默认（无参数） | 抓 HKAB 主页 1M 当前 fixing | 当结单期跨度短 / 用户只想看 spread 量级 |
| `--hibor X` | 用户手输 % | 当结单期 ≥ 一周，需要算期间均值才精确（HKAB 历史要 web 翻日历，没暴露 API） |
| `--no-hibor` | 不查 | 离线 / 只想看有效年化 |

**期间均值取法**：`https://www.hkab.org.hk/en/rates/hibor` → 选历史日期 → 取 `1month` → 自己算 18 个工作日（含周末填前值）平均，喂 `--hibor`。

## 1% 地板

结单条款明示：`HIBOR + spread < 1% p.a. → 按 1% 收`。
脚本判定 `|effective - 1.00%| < 0.05%` → 标 `floored=true`，此时 `spread_pct` 是下界估计（实际 spread 可能更负）。

## 与其他 skill 的关系

```
用户给加密 PDF
  ↓
pdf-decrypt    ← 解密（已存在）
  ↓
hsbc-wpl       ← 本 skill：解析 + 利率反推
  ↓
docs/statements/<bank>-wpl-YYYYMMDD.md  ← 用户视情粘贴 / 落地
```

## 后续 v0.x 想法（未做）

- **HIBOR 历史缓存** —— 写个 `lib/hibor.py` 维护 `~/.cache/hkab-hibor.csv`，跑一次抓全年，离线加速
- **多月结单 diff** —— 对比相邻 2 张结单，列出 spread 漂移 / 投资组合变化
- **告警** —— `--alert` 设阈值（spread > -0.5% 报警 / margin ratio < 200% 报警）
- **CN/HK 卡 + 投资交叉对账** —— 把 WPL 结单 vs HSBC 综合理财结单（CMP）joint，验证现金流闭环
