扫描 ~/Dev 和 ~/Work 所有 git+GitHub repo，为缺少 _files.md 的补上清单并 commit+push。

## 流程

1. 批量修复：
   ```bash
   python3 ~/Dev/auggie-dashboard/lib/fix_files_md.py
   ```
2. 刷新 dashboard 数据并部署：
   ```bash
   python3 ~/Dev/auggie-dashboard/lib/scanner.py ~/Dev/auggie-dashboard/data/scan.json
   bash ~/Dev/auggie-dashboard/deploy.sh
   ```
3. 输出修复摘要

## 参数

$ARGUMENTS

- `--dry-run`：只检查不修复（传给 fix_files_md.py）
- 无参数：执行修复 + 部署 dashboard

## 依赖

- ~/Dev/auggie-dashboard/lib/fix_files_md.py
- ~/Dev/auggie-dashboard/lib/scanner.py
- ~/Dev/auggie-dashboard/deploy.sh
