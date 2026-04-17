---
description: 下线一个闲置子域 — 停服务/删 nginx/CF DNS+Origin+Access/移 /var/www 到归档
---

对一个闲置子域做"整体下线"。services.ts 条目移除，`/var/www/<name>` 日期后缀移到 `_archived/`，可通过 git + `_archived/` 快速恢复。

## 用法

```bash
/site-archive <name> [--keep-data] [--yes] [--dry-run]
```

- `<name>` — 子域名（不带 `.tianlizeng.cloud`）
- `--keep-data` — 不动 `/var/www/<name>`
- `--yes` — 跳过交互确认
- `--dry-run` — 打印动作计划但不执行

## 执行

```bash
source ~/.personal_env
python3 ~/Dev/devtools/lib/tools/site_archive.py "$@"
```

## 动作顺序

1. **Pre-flight** — 扫描 services.ts / nginx / systemd / `/var/www`，打印即将执行的动作
2. **systemd** — `stop && disable` 对应 unit（若有）
3. **nginx** — `rm sites-enabled/{host}`，`nginx -t && reload`
4. **CF Access** — 删 Access app（若声明 cf-access）
5. **CF DNS** — 删 A 记录
6. **CF Origin Rule** — 从 expression 剔除 hostname
7. **services.ts** — 删 entry
8. **projects.yaml** — `status: archived`
9. **`/var/www/<name>`** — `mv` 到 `/var/www/_archived/<name>-YYYYMMDD/`

## 恢复

- `services.ts` / `projects.yaml`：`git checkout` 回旧版
- `/var/www`：从 `_archived/<name>-DATE/` 移回来
- CF DNS / Origin / Access：用 `/cf` 重建（参考 `/ship-site`）

## 规则

- 交互确认默认 ON；只有 `--yes` 或 `--dry-run` 跳过
- 失败某步后续步骤继续——各步幂等，可重跑
- 不依赖 7d 流量数据，由调用方（如 `/sites-health`）判断是否该归档
