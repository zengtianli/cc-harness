# cc-configs — Claude Code 配置中心

所有 Claude Code 自定义配置（commands/skills/agents/rules）和配套 CLI 工具的单一 source of truth。

## Quick Reference

| 项目 | 路径/值 |
|------|---------|
| Commands | `commands/` (28 slash commands) |
| Skills | `skills/` (14 auto-triggered skills) |
| Agents | `agents/` (2 agent definitions) |
| Rules | `rules/` (command 规则文件) |
| 审计工具 | `tools/harness/harness.py` |
| Context 工具 | `tools/context/context.py` |
| 注册表 | `harness.yaml` |

## 常用命令

```bash
# 审计项目 CC 配置
python3 tools/harness/harness.py audit /path/to/project

# JSON 格式审计输出
python3 tools/harness/harness.py /path/to/project --json

# Context 监控
python3 tools/context/context.py monitor

# Context 健康检查
python3 tools/context/context.py health

# 运行测试
python3 -m pytest tools/harness/tests/ -v
python3 -m pytest tools/context/tests/ -v
```

## 项目结构

```
commands/               # slash commands (symlink → ~/.claude/commands)
skills/                 # auto-triggered skills (symlink → ~/.claude/skills)
agents/                 # agent definitions (symlink → ~/.claude/agents)
rules/                  # command 规则文件
tools/
  harness/              # CC 配置审计工具
    harness.py          # CLI 入口
    analyzers/          # 六维度分析 (D1-D6)
    collectors/         # 数据采集
    security/           # 安全扫描
    reporters/          # 报告输出
    tests/              # harness 测试
  context/              # CC 上下文工程工具
    context.py          # CLI 入口
    monitor/            # token 监控
    snapshot/           # 上下文快照
    health/             # 健康检查
    hooks/              # CC hooks 安装
    tests/              # context 测试
harness.yaml            # skill 分发注册表 (symlink → ~/.claude/)
install.sh              # symlink 安装脚本
```

## 开发注意事项

- **纯 stdlib**，不依赖任何第三方包
- `install.sh` 将 commands/skills/agents/harness.yaml symlink 到 `~/.claude/`
- tools/ 下的工具通过 commands 中的 slash command 调用，不直接 symlink
- 新增 command：在 `commands/` 加 `.md` 文件即可
- 新增 skill：在 `skills/` 加目录或 `.md` 文件
