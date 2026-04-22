---
description: 全景健康扫描 — 合并 menus-audit + services_vs_live 输出 12 服务 × N 维矩阵
---

聚合 `menus.py audit()` (13 类 SSOT 漂移) + `services_vs_live.py` (live /api/metadata) 成一份矩阵，定位单服务问题到单一命令。

## 用法

```bash
/services-health              # markdown 表
/services-health --json       # JSON 供 ops-console / CI 消费
```

## 执行

```bash
python3 ~/Dev/devtools/scripts/tools/services_health.py "$@"
```

## 输出列

| 列 | 含义 | 来源 |
|---|---|---|
| service_id | 子域 id | entities/subdomains.yaml |
| public_port | 前端/nginx 端口 | subdomains.yaml |
| api_port | FastAPI 内部端口 (+100 convention) | derived |
| live_version | 实时 /api/metadata 返回版本 | services_vs_live |
| http | /api/metadata HTTP 状态码 | services_vs_live |
| ms | /api/metadata 响应毫秒 | services_vs_live |
| menus | 该服务相关的 menus.audit 漂移数 | menus.audit() |
| live-drift | port/id/version 漂移项 | services_vs_live |

## 相关

- `/menus-audit` — 单独跑 SSOT 13 类漂移（不 probe live）
- `/sites-health` — 边缘 HTTP + CF Access + navbar（公网视角）
- `/cf-audit` — DNS + nginx + Origin Rules + Access 声明对账
- services_vs_live.py — 纯 live probe（单独跑也行）

## 规则

- 只读；无副作用
- 13 类 + live + http 全绿 → exit 0
- 任一红项 → exit 1（可 CI gate）
- Live probe 需要服务端口本地可达（127.0.0.1:$api_port） — VPS 上自动满足，本机 dev 需先起 uvicorn
