扫描 ~/Dev 和 ~/Work 所有目录的 Auggie 索引状态，更新 dashboard 并部署。

## 流程

1. 运行 scanner 生成 scan.json：
   ```bash
   python3 ~/Dev/auggie-dashboard/lib/scanner.py ~/Dev/auggie-dashboard/data/scan.json
   ```
2. 部署到 VPS：
   ```bash
   bash ~/Dev/auggie-dashboard/deploy.sh
   ```
3. 输出摘要：总 repo 数、cloud complete、needs attention、missing _files.md

## 依赖

- ~/Dev/auggie-dashboard/（Streamlit app）
- VPS: root@104.218.100.67
- 域名: auggie.tianlizeng.cloud（需要 CF DNS + systemd service 首次配置）
