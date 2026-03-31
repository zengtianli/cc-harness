# cc-harness — Claude Code 配置质量审计工具

## Quick Reference

| 项目 | 路径/值 |
|------|---------|
| 入口 | `harness.py` |
| 分析器 | `analyzers/` (D1-D6 六维度) |
| 采集器 | `collectors/` (metrics/hooks/config/skills) |
| 安全扫描 | `security/scanner.py` |
| 报告输出 | `reporters/` (scorecard + markdown) |
| 测试 | `tests/` |

## 常用命令

```bash
# 全量审计（最常用）
python3 harness.py /path/to/project

# JSON 格式输出（便于脚本处理）
python3 harness.py /path/to/project --json

# 仅运行安全扫描
python3 harness.py /path/to/project --security-only

# 指定 Claude home 目录
python3 harness.py /path/to/project --claude-home ~/.claude

# 运行测试
python3 -m pytest tests/ -v
```

## 审计维度

| 维度 | 检查内容 |
|------|---------|
| D1 Context | CLAUDE.md 质量、token 预算、凭证泄露 |
| D2 Hooks | PostToolUse 覆盖、schema 有效性 |
| D3 Agents | Skill 数量、重叠、frontmatter |
| D4 Verification | done-conditions、构建/测试命令 |
| D5 Session | Compact Instructions、HANDOFF.md |
| D6 Structure | 孤立文件、命名规范、gitignore |

## 项目结构

```
harness.py          # CLI 入口，Tier 检测 + 调度
analyzers/          # 六维度分析逻辑（context/hooks/agents/verification/session/structure）
collectors/         # 数据采集（metrics/hooks/config/skills）
security/           # 安全扫描器（6 类风险检测）
reporters/          # 输出格式化（scorecard + markdown）
tests/              # pytest 测试套件
```

## 开发注意事项

- **纯 stdlib**，不依赖任何第三方包，不需要 pip install
- Tier 自动判定（Simple/Standard/Complex），避免误报
- 安全扫描区分"讨论"模式（benign）vs "使用"模式（flagged）
- 新增分析维度：在 `analyzers/` 加模块，在 `harness.py` 注册即可
