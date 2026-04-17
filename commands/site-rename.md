---
description: 原子改名子域 — CF DNS/Origin/Access + nginx + services.ts + 14 天 301
---

一致改名一个子域，所有注册表 + CF + nginx 都同步更新，老域名 14 天 301 到新域名，到期后用 `/site-archive <old>` 收尾。

## 用法

```bash
/site-rename <old> <new> [--301-days N] [--yes] [--dry-run]
```

- `<old>` / `<new>` — 子域名（不带 `.tianlizeng.cloud`）
- `--301-days` — 老域 301 保留天数（默认 14）
- `--yes` — 跳过交互确认
- `--dry-run` — 打印动作计划但不执行

## 执行

```bash
source ~/.personal_env
python3 ~/Dev/devtools/lib/tools/site_rename.py "$@"
```

## 动作顺序

1. **Pre-flight**（任一失败则 0 副作用）
   - `<old>` 在 services.ts 中存在
   - `<new>` 不在 services.ts / CF DNS
   - `services.ts` + `projects.yaml` 的 git 工作区 clean
2. **CF DNS**：`dns add <new>` → VPS_IP，proxied；老记录保留
3. **CF Origin Rule**（如老域有 `port`）：在现有 Rule expression 里加 `<new>`
4. **CF Access**（如老域是 `cf-access`）：新建 app，沿用现有邮箱约定
5. **VPS nginx**：
   - `cp sites-available/<old> → <new>`，`sed` 改 `server_name` 和 `root`
   - 静态站：`ln -sfn /var/www/<old> /var/www/<new>`（共享目录，不拷贝）
   - 老 vhost 备份 `.prerename.bak` 后改写为 `return 301 https://<new>$request_uri`
   - `nginx -t && systemctl reload`
6. **services.ts**：精确 sed — 只改那条 entry 的 subdomain 字段
7. **projects.yaml**：全局 `<old-host>` → `<new-host>` 替换
8. **scheduled-archives.json**：登记 `<old>` 的预期归档日

## 验证

```bash
/sites-health --filter <new>          # 新域应 200 / 302
curl -sI https://<old>.tianlizeng.cloud # 应 301 → new
```

## 回滚

每步都有明确副作用，可单步回滚：
- `cf_api.py dns delete <new>` / `access delete <new>`
- `cf_api.py origin-rules remove <new>`
- VPS：从 `.prerename.bak` 恢复老 vhost；`rm /etc/nginx/sites-enabled/<new>`；reload
- `git checkout --` services.ts / projects.yaml

## 规则

- 不覆盖老 CF Access app（301 期间老域名也需走 Access）
- `/var/www/<new>` 用软链而非 mv（流量 0 中断）
- 到期 teardown 靠 `/site-archive <old>`，不自动
