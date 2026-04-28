---
description: Cloudflare 统一管理 — DNS / Origin Rules / Access Applications
---

替代已归档的 `/cf-dns`。后端：`~/Dev/devtools/lib/tools/cf_api.py`，凭证自动从 `~/.personal_env` 读取。

## 用法

`/cf <subcommand> <action> [args]`

### DNS

```bash
/cf dns list [--filter NAME]
/cf dns add <subdomain>              # A 记录指向 VPS_IP，proxied
/cf dns delete <subdomain>
```

### Origin Rules（子域名 → 回源端口）

```bash
/cf origin list
/cf origin add <hostname> <port>     # e.g. stack.tianlizeng.cloud 8443
```

### Access Applications（Zero Trust）

```bash
/cf access list                      # 看所有 app 和 policy 邮箱
/cf access add <hostname>            # 自动沿用现有 app 的邮箱约定
/cf access add <hostname> --email X  # 覆盖邮箱
/cf access delete <hostname>
```

**关键保障**：`access add` 会**先 GET 现有 app 的 policy** 拿邮箱作为默认。杜绝"用错邮箱把自己锁外"的 2026-04-17 事故。

## 执行规则

1. 所有调用直接执行 `python3 ~/Dev/devtools/lib/tools/cf_api.py <args>`，把 $ARGUMENTS 原样传过去
2. 不要自己调 curl 或 urllib — 工具已覆盖
3. 凭证在 `~/.personal_env`，脚本自动 source，不问用户要

## 参考

- 已归档版：`commands/archive/cf-dns.md`
- 治理原则：新建任何 CF 配置前先 `list` 看现有 zone/origin/access 约定，避免重复创建
