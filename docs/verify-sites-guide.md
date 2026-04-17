# `/verify-sites` 完整使用指南

> 28 子域体系的"体检工具说明书"。本指南解决三个问题：
> 1. 怎么跑？
> 2. 结果怎么看懂？
> 3. 出问题怎么办？

---

## 一、TL;DR — 三分钟速查

只想知道现在系统好不好：

```bash
/verify-sites --quiet
```

输出里如果只有 `✓` + 末尾 `🎉 全部通过。`：你没事，走开。

如果看到 `⚠`：大概率是预期（14 天 301 窗口、架构性 drift），看 hint 里说的就行。

如果看到 `✗`：**是 bug，需要处理**。对着 hint 修。

---

## 二、为什么需要这个工具

子域体系散在 5 个注册表 + 3 处基础设施：

- `~/Dev/website/lib/services.ts`（前端展示）
- `~/Dev/stack/projects.yaml`（架构说明）
- Cloudflare DNS（CF 控制台）
- Cloudflare Origin Rules（路由到 nginx:8443）
- Cloudflare Access（Zero Trust app）
- VPS `/etc/nginx/sites-enabled/`
- VPS systemd services
- `~/Dev/configs/scheduled-archives.json`（归档计划）

任何一处 drift，网站可能就挂了。人肉挨个查要 20+ 分钟。`/verify-sites` 把所有核对逻辑固化，60 秒出结果。

---

## 三、检查分组详解

每组都会打印若干项，每项一个 `✓ PASS / ⚠ WARN / ✗ FAIL` + 一句话说明。

### 3.1 commands（命令存在性）

检查 7 个子域相关 slash 命令的 `.md` 文件是否在 `~/Dev/cc-configs/commands/`。

| 命令 | 作用 |
|---|---|
| `/sites-health` | HTTP/Access/Navbar 探针矩阵 |
| `/cf-audit` | 5 源 drift 报告 |
| `/navbar-refresh` | 共享 navbar 模板同步 |
| `/site-archive` | 原子下线一个子域 |
| `/site-rename` | 原子改名 + 14d 301 |
| `/site-activate` | 激活闲置站 |
| `/verify-sites` | 本工具自己 |

**如果 FAIL**：说明 `cc-configs/install.sh` 没跑，或 `~/.claude/commands/` 的 symlink 断了。跑 `bash ~/Dev/cc-configs/install.sh`。

### 3.2 services.ts（前端注册表）

- `parse` — 能不能从 services.ts 里抠出 ≥20 条服务（目前 27 条）
- `no-duplicates` — 同一个 subdomain 没出现两次

**如果 parse FAIL**：services.ts 格式变了，`~/Dev/devtools/lib/tools/_services_ts.py` 的 regex 跟不上。改 regex 或让 `_services_ts.py` 报告具体卡在哪行。

**如果 no-duplicates FAIL**：说明 `/site-rename` 没正确删老 subdomain。看 diff 手工修。

### 3.3 cf-audit（5 源对账）

调用 `cf_audit.py`，对比 services.ts / CF DNS / CF Origin Rules / CF Access / VPS nginx：

| 子项 | 含义 |
|---|---|
| `sources` | 四个源都抓到数据了吗 |
| `orphan-dns` | CF DNS 里有但 services.ts 里没（301 窗口期正常） |
| `missing-dns` | services.ts 声明了但 CF 没对应 A 记录（**bug**） |
| `nginx-missing` | 有 DNS 但 VPS 没独立 nginx vhost（**架构性，非 bug**） |
| `nginx-orphan` | VPS 有 nginx 配但 services.ts 没（301 窗口期正常） |
| `access-missing` | 声明 cf-access 但没 Access app（**bug**，用户会进不去） |
| `access-orphan` | 有 Access app 但 services.ts 没声明（301 窗口期正常） |

**"301 窗口期正常" 是啥意思**：跑了 `/site-rename cc cc-options` 之后，老的 `cc.tianlizeng.cloud` 会保留 14 天用来 301 跳到新域。这期间 cc 在 CF 里有 DNS/Origin/Access，但 services.ts 里已经变 cc-options 了。工具看到 `scheduled-archives.json` 里有 cc 条目，会自动认这些孤儿是预期，打 PASS 不报 WARN。

**如果 `nginx-missing` 里多出一条陌生的**：可能是你手工加了 DNS 但忘了建 nginx 配。跑 `/ship-site <name>`。

### 3.4 sites-health（live HTTP 探针）

调用 `sites_health.py`，对 27 站并发 curl：

| 子项 | 含义 |
|---|---|
| `no-unexpected-dead` | 没站返回 4xx/5xx / timeout（audiobook/panel/sub 的 405 预期） |
| `access-drift` | 声明 `public` 的站实际在 302 Access，或反之 |

**如果 no-unexpected-dead FAIL**：有站真挂了。对着清单挨个 `curl -I <host>` 看详情。常见原因：
- nginx 配置语法错（`ssh root@VPS 'nginx -t'`）
- 后端服务挂了（`ssh root@VPS 'systemctl status <svc>'`）
- Origin Rule expression 漏了这个 host（`/cf-audit` 的 nginx-missing 会命中）

### 3.5 scheduled-archives（301 窗口存活）

读 `~/Dev/configs/scheduled-archives.json`，对每个登记的老域：
- 打印剩余天数
- SSH 到 VPS，用 Host 头 curl 本地 nginx:8443，确认还是返回 301

**为啥要 SSH 本地 curl**：从外部 curl 老域会先被 CF Access 拦 302，看不到 301 是不是还活着。本地带 Host 头直连 nginx 能绕过 CF 边缘。

**如果 `301 alive` FAIL**：老域的 nginx 配被意外改回实际内容了（而不是 301 redirect）。找 `sites-enabled/<host>` 的备份 `.prerename.bak`，对比后决定是恢复备份还是手写 301。

**如果过期天数 < 0**：该老域 14 天窗口已过，应该跑 `/site-archive <old>` 把它清掉。

### 3.6 git state（4 repo 工作区）

四个关键 repo：
- `~/Dev/devtools`（工具源码）
- `~/Dev/cc-configs`（slash 命令）
- `~/Dev/website`（services.ts）
- `~/Dev/stack`（projects.yaml）

每个 repo 检查两件事：
- `clean` — 工作区没有未提交改动（针对我们关心的路径）
- `pushed` — 本地 HEAD 没领先 upstream

**如果 WARN**：说明有工作没收尾。`cd <repo> && git status`，要么提交要么丢弃。

### 3.7 🧑 browser todos（人肉目测项）

脚本无论如何测不出的两类：
- **Streamlit 的 tlz-nav**：Streamlit 是 SPA，初始 HTML 只有一个空 `<div id="root">`，navbar 要 JS mount 后才进 DOM。HTTP 探针永远测不出。
- **CF Access 里 301 链路体验**：外部 curl 看到的是 302 到 Access，不是你最终跳向 cc-options。要真浏览器走 SSO 流程。

工具把这些列在末尾，让你打开浏览器手动验一遍。

---

## 四、常见状态解读

### 状态 1 · "全部通过"

```
**Summary**: 35 pass · 0 warn · 0 fail
🎉 全部通过。
```

走开，不用管。

### 状态 2 · "只有预期 warn"

```
**Summary**: 31 pass · 4 warn · 0 fail
提示：上面的 ⚠ 多数是预期（如 14-day 301 窗口）或架构性，查 hint 确认。
```

大概率是：
- 一个 `/site-rename` 正在 14 天 301 窗口里（`scheduled-archives` 那几行）
- 3 条架构性 nginx-missing（changelog / dashboard / tianlizeng.cloud — 这些走 CF Origin Rule 直接到服务端口，没有独立 nginx vhost）

**不用处理**。但每次看 warn 时扫一眼 hint，确认真是预期。

### 状态 3 · "有 FAIL"

```
**Summary**: 28 pass · 3 warn · 2 fail
```

**必须处理**。按 group 优先级：
1. `commands` FAIL → install.sh 问题，先修这个（其他命令跑不了）
2. `services.ts parse` FAIL → regex 要跟进
3. `cf-audit` FAIL → 基础设施 drift，可能有站要挂了
4. `sites-health no-unexpected-dead` FAIL → 真有站挂了，立即看
5. `scheduled-archives 301 alive` FAIL → 某老域的 301 被改掉了
6. `git clean/pushed` → 只是 WARN，不会 FAIL

---

## 五、集成到工作流

### 5.1 做完改动立即跑

```bash
/site-rename cc cc-options
/verify-sites  # 立刻验证
```

确保没破其他站。

### 5.2 会话结束前跑（推荐写进 /handoff）

会话要结束时：
```bash
/verify-sites --quiet  # 只看 warn/fail
```

把输出贴进 `HANDOFF.md`。下一轮开会话先跑一次 baseline 对比。

### 5.3 定期跑（考虑自动化）

可以加到 `launchd` / `cron`：

```bash
# 每天早晨 9 点跑一次，fail 时发邮件
0 9 * * * cd ~/Dev && python3 devtools/lib/tools/verify_sites.py --quiet 2>&1 | \
  tee /tmp/verify-$(date +%F).log; \
  [ ${PIPESTATUS[0]} -eq 0 ] || mail -s "verify-sites failed" you@example.com < /tmp/verify-$(date +%F).log
```

或更简单：让每天早上的 briefing 系统（`~/Dev/...briefing`）加一项跑 `/verify-sites --json`，出现 fail 就提醒。

### 5.4 CI gate（GHA）

```yaml
# .github/workflows/verify-sites.yml  (在需要的 repo 里)
- name: Verify subdomain ecosystem
  run: python3 ~/Dev/devtools/lib/tools/verify_sites.py --quiet
```

但这要求 CI 里有 CF_API_KEY 等环境变量，不建议（秘钥泄露风险）。**本地跑更合适**。

---

## 六、本会话（2026-04-17）交付的验证项

这份指南专门给这一轮的实盘做对应关系。每一条交付都对应工具里的具体 check：

| 交付 | 工具检查项 | 预期结果 |
|---|---|---|
| auggie 400 修复 | `sites-health › no-unexpected-dead` | PASS（auggie 不在 dead 列表） |
| hammerspoon 孤儿清理 | `cf-audit › orphan-dns` 不含 hammerspoon | PASS |
| cc → cc-options rename 成功 | `services.ts › no-duplicates` + `scheduled-archives › cc.tianlizeng.cloud` | PASS + WARN（14 天倒计时） |
| cc 301 还活着 | `scheduled-archives › cc.tianlizeng.cloud 301 alive` | PASS |
| 6 个新命令存在 | `commands` 组 | 7 个全 PASS（含 verify-sites 自己） |
| Streamlit 3 站 navbar 修复 | 🧑 browser todos 的 dashboard / auggie 项 | 人肉目测 |
| git 全部推送 | `git` 组 | 4 repo 全 PASS |

跑一次：

```bash
/verify-sites
```

应该看到：
- `commands`：7/7 pass
- `services.ts`：2/2 pass（27 条、无重复）
- `cf-audit`：6 条都 pass 或 expected-warn（cc 孤儿是 scheduled-archives 里登记的）
- `sites-health`：2/2 pass
- `scheduled-archives`：cc.tianlizeng.cloud 14 天倒计时 WARN + 301 alive PASS
- `git`：8/8 pass（4 repo × clean+pushed）
- browser todos：2 条（dashboard、auggie、cc 端到端）

这样就知道本轮 3 个目标（auggie / hammerspoon / cc rename）真的都 OK 了。

---

## 七、常见坑

### 坑 1 · "FAIL: services.ts 解析到 15 条"

**现象**：regex 没匹配全。
**原因**：有人把某条 service 格式改成了多行：
```ts
{
  name: "X",
  subdomain: "y"
}
```
而不是单行。
**修法**：改 `_services_ts.py` 的 `_SERVICE_RE` 用 `re.DOTALL` + 贪婪控制。

### 坑 2 · "WARN: auggie-dashboard 1 commit 未 push"

**现象**：改完 Streamlit config 忘 push。
**修法**：`cd ~/Dev/auggie-dashboard && git push`（GHA 会接力重新部署）。

### 坑 3 · "FAIL: cc.tianlizeng.cloud 301 alive FAIL，origin 返回 502"

**现象**：老的 301 vhost 被意外改掉了。
**原因**：可能有人手工编辑了 sites-enabled/cc.tianlizeng.cloud。
**修法**：
```bash
ssh root@104.218.100.67 "cp /etc/nginx/sites-enabled/cc.tianlizeng.cloud.prerename.bak \
  /etc/nginx/sites-enabled/cc.tianlizeng.cloud && nginx -t && systemctl reload nginx"
```
然后手工恢复 301 内容（参见 `site_rename.py` 里 `redirect_conf` 模板）。

### 坑 4 · "sites-health 超慢"

**现象**：跑一次 2 分钟。
**原因**：SSH 到 VPS 的连接慢了（网络抖动或 VPS 负载高）。
**修法**：`/verify-sites --quiet` 只打印 warn/fail；或 `python3 ~/Dev/devtools/lib/tools/sites_health.py --no-traffic`（本 verify 脚本已内部 skip traffic）。

---

## 八、扩展：加检查项

要加新的检查（比如"检查某 Markdown 里的死链"）：

1. 在 `~/Dev/devtools/lib/tools/verify_sites.py` 加个 `check_xxx(r: Report)` 函数，调 `r.add(group, name, status, message, hint)`
2. 在 `main()` 里调这个函数
3. `/verify-sites` 自动包含新检查

不用改 `.md` 命令文件，框架就是这样扩展的。

---

## 九、设计 FAQ

**Q：为什么不直接调 `/sites-health` 和 `/cf-audit`？**
A：两者都只报告单一维度的结果；`/verify-sites` 统合它们，加上 session-specific（301 窗口、git 状态）和"已知预期 drift 不报警"的智能。等于一个语义层。

**Q：为什么 git state 只是 WARN 不是 FAIL？**
A：本地没 push 不影响生产（生产走 GHA 拉远端）。只是提醒你别忘。FAIL 级留给真影响生产的问题。

**Q：浏览器项为什么不 FAIL？**
A：机器测不出的东西，让机器 PASS/FAIL 没意义。列出来让人去做。

**Q：`--json` 输出干嘛用的？**
A：给 `/handoff` 这种上层命令消费。比如 `/handoff` 里可以 `python3 verify_sites.py --json | jq '.summary.fail'`，fail > 0 就拒绝 handoff，强迫你先修。
