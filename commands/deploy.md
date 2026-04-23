通用部署，适配任意有 deploy.sh 的项目。

## 流程

### 0. Pre-flight（任一失败立即停止，零副作用）
- 确认 `deploy.sh` 存在
- `git status` — 如有未 commit 变更，打印警告并等用户确认是否继续
- 检查 VPS 连通性：`ssh root@104.218.100.67 "echo ok"` 超时 5s 则报错退出

### 1–3. 构建 + 部署
1. 自动检测前置步骤：有 `frontend/` 且有未构建变更 → `cd frontend && npm run build`
2. 运行 `bash deploy.sh`

### 4. 验证（不得用 exit code 0 代替）
- 线上地址 → `curl -sI` 检查实际 HTTP 状态码（200/302 才算通过）
- 服务名 → `ssh root@104.218.100.67 "systemctl is-active <service>"` 必须返回 `active`
- 两项任一未通过 → 报错，打印排查路径，不声称"完成"

## 参数

$ARGUMENTS 可选：
- `--no-verify`：跳过验证步骤
- `--dry-run`：只显示会执行什么，不实际执行

## 验证逻辑

从 CLAUDE.md 中提取：
- `线上地址` / `https://xxx.tianlizeng.cloud` → curl 目标
- `systemd 服务` / `端口` → systemctl 检查目标

如果 CLAUDE.md 没有相关信息，跳过验证并提示用户补充。

## 规则

- 凭证在 `~/.personal_env`，不问用户要
- 不硬编码任何 URL 或服务名
- deploy.sh 失败时立即停止，不继续验证
