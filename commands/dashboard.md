扫描 Claude Code 会话，LLM 分析任务状态，部署 dashboard 到 VPS。

Steps:
1. 运行任务分析器：`python3 ~/Dev/repo-dashboard/lib/task_analyzer.py`
2. 部署到 VPS：`cd ~/Dev/repo-dashboard && bash deploy.sh`
3. 等待 5 秒，验证：`curl -sI https://dashboard.tianlizeng.cloud/`
4. 输出结果：✅ Dashboard 已更新 → https://dashboard.tianlizeng.cloud

$ARGUMENTS 可选：
- `--scan-only`：只扫描不部署，本地查看 tasks.json 结果
- `--force`：忽略缓存，重新分析所有会话
