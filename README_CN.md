# cc-harness

Claude Code 配置质量审计工具。扫描项目的 Claude Code 配置（CLAUDE.md、skills、hooks、rules 等），输出六维度评分卡 + 分级修复建议报告。

## 功能

- 自动检测项目级别（Simple / Standard / Complex）
- 六维度评分（Context、Hooks、Agents、验证、会话、结构）
- 安全扫描（prompt injection、凭证泄露、破坏性命令等 6 类）
- 输出 Markdown 报告或 JSON
- 纯 Python 标准库，无需安装依赖

## 六维度

| 维度 | 检查内容 |
|------|---------|
| **D1 Context** | CLAUDE.md 质量、Token 预算、重复规则、嵌套文件、凭证 |
| **D2 Hooks** | PostToolUse 覆盖、schema 验证、输出截断、错误上报 |
| **D3 Agents** | Skill 数量、重叠、描述质量、frontmatter、disable-model-invocation |
| **D4 验证** | 完成条件、build/test 命令、CI 集成 |
| **D5 会话** | Compact Instructions、HANDOFF.md、上下文预算文档 |
| **D6 结构** | 孤立文件、引用链、命名规范、gitignore |

## 使用

```bash
# 完整审计
python3 harness.py /path/to/project

# JSON 输出
python3 harness.py /path/to/project --json

# 仅安全扫描
python3 harness.py /path/to/project --security-only

# 自定义 Claude 目录
python3 harness.py /path/to/project --claude-home ~/.claude
```

## 报告结构

报告按严重程度分三级：
- **Critical** -- 立即修复（安全漏洞、凭证泄露、配置冲突）
- **Structural** -- 尽快修复（缺失的 hooks/rules/verification、重复 skills）
- **Incremental** -- 可选改进（精简描述、添加 version、优化上下文）

末尾附六维度评分卡和修复路线图。

## 测试

```bash
python3 -m pytest tests/ -v
```

## 许可

MIT
