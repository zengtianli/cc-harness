一键部署新静态站点到 `<name>.tianlizeng.cloud`。编排 rsync + Nginx + `/cf dns/origin/access` + 验证。

## 用法

```bash
/ship-site <name> [--source DIR] [--no-access]
```

- `<name>` — 子域名（也是 `/var/www/<name>` 目录名）
- `--source DIR` — 本地源目录（默认：当前目录下的 `site/`）
- `--no-access` — 公开站点，不加 CF Access 保护

## 执行步骤

按顺序执行，任一步失败立即停止：

### 0. Pre-flight（并行扫，任一阻断项 → 停止等确认）
同时检查以下维度，输出清单后**暂停等用户确认**再继续：
- `$SOURCE/index.html` 存在？
- CF DNS / Access 是否已有同名记录（冲突 or 幂等？）
- VPS `/var/www/<name>` 是否已存在（rsync 会覆盖！）
- VPS nginx `sites-enabled/<hostname>` 是否已存在
- VPS 连通性：`ssh root@104.218.100.67 "echo ok"`

### 1. 本地预检
- 计算 `HOSTNAME=<name>.tianlizeng.cloud`
- 计算 `REMOTE=/var/www/<name>`

### 2. 幂等检查（先查再建）
```bash
python3 ~/Dev/devtools/lib/tools/cf_api.py dns list --filter $HOSTNAME
python3 ~/Dev/devtools/lib/tools/cf_api.py access list | grep $HOSTNAME
ssh root@104.218.100.67 "ls /etc/nginx/sites-enabled/$HOSTNAME 2>/dev/null"
```
已存在的资源跳过对应步骤，不重建。

### 3. rsync 内容到 VPS
```bash
ssh root@104.218.100.67 "mkdir -p $REMOTE"
rsync -avz --delete $SOURCE/ root@104.218.100.67:$REMOTE/
```

### 4. Nginx 配置
用模板 `~/Dev/devtools/lib/templates/nginx-static.conf`，替换 `{{HOSTNAME}}` 和 `{{NAME}}`，写到 `/etc/nginx/sites-available/<hostname>`，软链到 `sites-enabled/`，然后 `nginx -t && systemctl reload nginx`。

### 5. CF DNS + Origin Rule
```bash
/cf dns add <name>
/cf origin add <hostname> 8443
```

### 6. CF Access（默认开启）
```bash
/cf access add <hostname>
```
邮箱从现有 policy 自动沿用（zengtianli1@gmail.com）。`--no-access` 时跳过。

### 7. 验证
等 5 秒后 `curl -sI https://$HOSTNAME`：
- **302** 到 cloudflareaccess.com = Access 保护生效 ✓
- **200** = 站点直接可达（`--no-access` 模式）✓
- **其他** = 报错并提示检查的文件路径

### 8. 登记（提示用户手工加）
告诉用户：
> 记得在 `~/Dev/stations/website/lib/services.ts` 加一条（accessType: cf-access 除非 --no-access）

## 规则

- 凭证在 `~/.personal_env`，工具自动读，不问用户
- 不硬编码 VPS IP / 端口 / 邮箱 — 全部从现有资源或环境变量推断
- 每一步失败立即停止，不继续链路
- 所有"创建类"操作先 `list` 再 `add`（幂等原则，避免重复建）

## 参考

- 模板：`~/Dev/devtools/lib/templates/nginx-static.conf`
- 后端：`/cf`（`cf_api.py`）
- 实战参考：2026-04-17 stack.tianlizeng.cloud 首次部署流程
