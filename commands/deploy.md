Deploy the current project to VPS.

Steps:
1. Check if `deploy.sh` exists in the current project directory
2. If frontend/ has uncommitted changes or dist/ is stale, build first: `cd frontend && npm run build`
3. Run `bash deploy.sh`
4. Verify: `ssh root@104.218.100.67 "systemctl status oauth-proxy --no-pager -l"`
5. Test endpoint: `curl -sI https://proxy.tianlizeng.cloud/`

$ARGUMENTS may contain flags like `--backend-only` or `--no-restart`.

Credentials are in `~/.personal_env` — never ask the user for them.
