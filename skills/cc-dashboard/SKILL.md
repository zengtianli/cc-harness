---
name: cc-dashboard
description: QQQ Covered Call Dashboard 数据刷新 + 部署。当在 international-assets 项目中工作时触发。
---

QQQ Covered Call Dashboard 数据刷新 + 部署。

## 关键约束（必须遵守）

- **收益对比必须用 TWR**（`compute_twr_curve()`），绝对不能用原始 NLV 增长率（有多次入金）
- **策略起始日：2025-04-10**
- **期权价格用 Yahoo Finance bid/ask mid price**（`st_snapshot.py` 的 `_yahoo_mid_prices()`）
- **回撤硬约束 ≤ QQQ**：CC 策略的回撤不能超过 QQQ 同期回撤
- **详见 `strategy-roll.md`**——投资哲学、roll 规则、Greeks 推导、策略评价

## 策略概要

- 杠杆持有 QQQ（~3×）+ 卖 ATM Covered Call
- **开仓永远卖 ATM**，市场自动分层（涨了变 ITM 对冲层）
- **绝不 roll up / roll down**，只做 calendar roll 或 let assign + 重开 ATM
- Deep ITM + DTE ≤ 7 → let assign（滑点太大，assign 后重开 ATM 更便宜）

## 实绩（2025-04-10 → 2026-04-10，TWR）

| 指标 | CC 实盘 | TQQQ 3x | QQQ 1x |
|------|--------|---------|--------|
| 累计收益 | +71.6% | +113.1% | +37.0% |
| Sharpe | **4.04** | 1.67 | 1.73 |
| MaxDD | **-11.1%** | -37.2% | -11.6% |

## 脚本工具链

| 脚本 | 用途 |
|------|------|
| st_snapshot.py | 拉持仓 → portfolio.json（期权价格 Yahoo mid price 覆盖） |
| st_activities.py | 拉全量交易流水 → data/activities.json |
| phase2_equity_curve.py | 重建 NLV + TWR + 基准对比 → data/daily_nlv.csv |
| lib_greeks.py | BS/Greeks/IV/scenario/roll 信号公共库（MARGIN_COST=4.25%） |
| app.py | Streamlit 单页 Dashboard |
| daily_update.sh | 全量刷新入口脚本 |
| log_trade.py | 记录 Roll 决策 → data/trade_log.jsonl |

## 数据文件

| 文件 | git 管理 | 说明 |
|------|----------|------|
| data/daily_nlv.csv | ✅ | 历史 NLV 曲线（本地 phase2 生成） |
| data/activities.json | ✅ | 全量交易流水 |
| portfolio.json | ✅ | 实时持仓快照 |
| data/dashboard_settings.json | ❌ | Dashboard 用户设置 |

## /cc-dashboard 命令

### `refresh` — 刷新数据 + 推送（默认）
按顺序执行：
1. **前置步骤**：输出美东 ET + 北京 CST + 星期几 + 市场状态
2. `source ~/.personal_env`
3. `python3 scripts/st_snapshot.py` — 拉持仓 + Yahoo mid price 覆盖
4. `python3 scripts/st_activities.py` — 拉全量交易流水
5. `python3 scripts/phase2_equity_curve.py` — 重建 NLV + TWR
6. `git add portfolio.json data/daily_nlv.csv data/activities.json && git commit && git push`
7. **VPS 健康检查**（push 后等 10 秒）：`ssh root@104.218.100.67 "systemctl is-active rh-dashboard"`。如果不是 active：`ssh root@104.218.100.67 "fuser -k 8521/tcp; systemctl restart rh-dashboard"`
8. 输出刷新结果摘要 + VPS 面板链接 https://cc.tianlizeng.cloud

### `start` — 刷新 + 启动本地 Dashboard
1. 执行 `refresh` 全流程
2. `streamlit run scripts/app.py`

### `open` — 仅启动本地（不刷新）
直接 `streamlit run scripts/app.py`

### `time` — 仅查看时间 + 市场状态
只执行前置步骤

### 无参数
等同于 `refresh`

## 部署架构

- VPS: https://cc.tianlizeng.cloud → `/var/www/rh-dashboard`
- GitHub push → webhook → VPS 自动 `git fetch + reset + systemctl restart`
- Systemd: KillMode=mixed + ExecStop fuser -k 8521，防端口残留
- Nginx: /etc/nginx/sites-enabled/cc.tianlizeng.cloud → proxy 8521

## 项目文档索引

| 文档 | 内容 |
|------|------|
| strategy-roll.md | 投资哲学、roll 规则、退出规则、Greeks 推导、策略评价、同类对比 |
| robinhood.md | Robinhood 账户细节、Direct Deposit |
| CLAUDE.md | 仓库结构、关键约束、脚本说明 |
