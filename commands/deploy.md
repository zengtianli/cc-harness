通用部署，适配任意有 deploy.sh 的项目。

## 流程

1. 确认当前目录有 `deploy.sh`，没有则报错退出
2. 自动检测前置步骤：
   - 有 `frontend/` 且有未构建变更 → `cd frontend && npm run build`
3. 运行 `bash deploy.sh`
4. 验证（从当前项目的 CLAUDE.md 自动提取）：
   - 线上地址 → `curl -sI` 检查 HTTP 200
   - 服务名 → `ssh root@104.218.100.67 "systemctl status <service> --no-pager -l"`

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
