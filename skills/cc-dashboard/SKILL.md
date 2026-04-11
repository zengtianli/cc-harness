---
name: cc-dashboard
description: QQQ Covered Call Dashboard 数据刷新 + 部署。当在 international-assets 项目中工作时触发。
---

QQQ Covered Call Dashboard 数据刷新 + 部署。

## 前置步骤（所有操作共用）

每次执行任何子命令前，必须先：
1. 输出当前时间：美东 ET + 北京 CST + 星期几
2. 判断美股市场状态（开盘/盘前/盘后/休市）
3. 如果休市，说明原因（周末/节假日）和下次开盘时间

## 参数

$ARGUMENTS 指定操作：

### `refresh` — 刷新数据 + 推送（默认）
按顺序执行：
1. **前置步骤**（时间 + 市场状态）
2. `source ~/.personal_env`
3. `python3 scripts/st_snapshot.py` — SnapTrade 拉取最新持仓 → `portfolio.json`（期权价格自动用 Yahoo Finance mid price 覆盖）
4. `python3 scripts/st_activities.py` — 拉取全量交易流水 → `data/activities.json`
5. `python3 scripts/phase2_equity_curve.py` — 重建历史 NLV + 基准对比 → `data/daily_nlv.csv`
6. `git add portfolio.json data/daily_nlv.csv data/activities.json && git commit && git push` — 推送触发 VPS webhook 自动部署
7. **VPS 健康检查**（push 后等 10 秒）：`ssh root@104.218.100.67 "systemctl is-active rh-dashboard"`。如果不是 active，执行修复：`ssh root@104.218.100.67 "fuser -k 8521/tcp; systemctl restart rh-dashboard"`
8. 输出刷新结果摘要 + VPS 面板链接 https://cc.tianlizeng.cloud

### `start` — 刷新 + 启动本地 Dashboard
1. 执行上面的 `refresh` 全流程（含 push）
2. `streamlit run scripts/app.py` — 启动本地 Streamlit
3. 输出本地 + VPS 访问地址

### `open` — 仅启动本地（不刷新）
直接 `streamlit run scripts/app.py`，使用已有数据

### `time` — 仅查看时间 + 市场状态
只执行前置步骤，不拉数据

### 无参数
等同于 `refresh`

## 部署架构
- VPS: https://cc.tianlizeng.cloud → `/var/www/rh-dashboard`
- GitHub push → webhook → VPS 自动 `git fetch + reset + systemctl restart`
- 所以 refresh 最后必须 push，否则 VPS 看不到新数据

## 自动化
- LaunchAgent `com.tianli.rh-dashboard` 每天 17:00 自动执行 `scripts/daily_update.sh`
- 日志: `data/cron.log`
- SnapTrade 凭证在 `~/.personal_env`
