Claude Code 会话监控与上下文工程工具。保障 compact 后不丢失关键细节。

CLI：`python3 ~/Dev/cc-context/context.py $ARGUMENTS`

子命令（通过 $ARGUMENTS 传入）：
- `monitor` — 当前会话的 token 统计、工具调用分布
- `monitor --all --json` — 所有会话概览
- `health` — 健康检查（上下文膨胀、重复查询、大文件读取等）
- `health --all` — 检查所有近期会话
- `snapshot save` — 保存当前上下文快照
- `snapshot restore` — 恢复快照
- `hooks install` — 安装 CC hooks

典型场景：
- 会话中途卡顿：`/context monitor` 看 token 消耗在哪
- 怀疑上下文膨胀：`/context health` 检查是否有重复读取/查询
- 准备交接下个会话：`/context snapshot save`
