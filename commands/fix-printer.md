办公室 Canon iR C3322L 打印机诊断修复。

运行修复脚本 `~/Dev/devtools/scripts/tools/printer/fix_printer.sh`，自动处理：
- 网络环境检测（办公室 172.21.x.x vs 热点）
- VPN 隧道绕过（Shadowrocket 等代理劫持路由时添加静态路由）
- CUPS 打印机配置修复（确保 socket:// 协议）
- 打印队列清理 + 测试页

需要 sudo 权限（添加路由时），脚本会自动请求。

直接执行：
```bash
bash ~/Dev/devtools/scripts/tools/printer/fix_printer.sh
```

如果脚本报错或行为异常，参考排查文档：`~/Dev/devtools/scripts/tools/printer/CLAUDE.md`
