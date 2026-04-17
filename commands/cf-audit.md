---
description: 对账 services.ts / CF DNS / VPS nginx / Origin Rules / CF Access，找孤儿与漂移
---

跨 5 个注册表只读对账，为 `/site-rename` / `/site-archive` / `/sites-health` 提供输入。

## 用法

```bash
/cf-audit
```

## 执行

```bash
python3 ~/Dev/devtools/lib/tools/cf_audit.py
```

## 报告分类

- `orphan-in-cf-dns` — CF DNS A 记录存在，但 services.ts 里没有（冗余 DNS）
- `missing-cf-dns` — services.ts 声明了，但没建 DNS（注册表虚假）
- `nginx-missing` — 有 DNS，VPS 却无对应 sites-enabled（可能走 CF Origin Rule → port 直连而不经 nginx）
- `nginx-orphan` — VPS nginx 有配置，但 DNS/services.ts 都没对应（遗留配置）
- `origin-rule-missing` — services.ts 有 `port`，但 Origin Rule expression 里没这个 host
- `access-declared-missing` — services.ts 标 `cf-access`，但无 Access app（应加保护）
- `access-orphan-app` — 有 Access app，但 services.ts 没标 `cf-access`（应同步声明）

## 退出码

- `0` — 零漂移
- `1` — 有任一漂移（可用作 CI gate）

## 规则

- 只读，无副作用
- 直接 import `cf_api._request`，避免 `origin-rules list` 的 120 字符截断
- grep 用 `-RhD read` 才能跟 symlink（sites-enabled/ → sites-available/）
