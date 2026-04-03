# cc-harness

[English](README.md) | **中文**

Claude Code 配置质量审计工具——扫描项目的 Claude Code 配置（CLAUDE.md、skills、hooks、rules 等），输出六维度评分卡 + 分级修复建议报告。

**无需 Claude Code 或 API key。** 纯 Python 标准库，无第三方依赖。

[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge)](https://python.org)

---

![cc-harness 演示](docs/screenshots/demo.png)

---

## 能做什么？

| 维度 | 检查内容 |
|------|---------|
| **D1 Context** | CLAUDE.md 质量、Token 预算、重复规则、嵌套文件、凭证 |
| **D2 Hooks** | PostToolUse 覆盖、schema 验证、输出截断、错误上报 |
| **D3 Agents** | Skill 数量、重叠、描述质量、frontmatter、disable-model-invocation |
| **D4 验证** | 完成条件、build/test 命令、CI 集成 |
| **D5 会话** | Compact Instructions、HANDOFF.md、上下文预算文档 |
| **D6 结构** | 孤立文件、引用链、命名规范、gitignore |

## 项目级别检测

自动识别项目规模，避免过度检查简单项目：

| 级别 | 特征 | 预期配置 |
|------|------|---------|
| Simple | <500 源文件、1 贡献者、无 CI | 仅需 CLAUDE.md |
| Standard | 500-5K 文件、小团队或有 CI | CLAUDE.md + rules + skills + hooks |
| Complex | >5K 文件、多贡献者、活跃 CI | 完整六层配置 |

## 安装

```bash
git clone https://github.com/zengtianli/cc-harness.git
cd cc-harness
python3 harness.py /path/to/your/project
```

依赖：Python 3.8+（仅标准库，无需 pip 安装）。

## 快速上手

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

## 安全扫描

内置安全扫描器检查 skills 的 6 类风险：

1. **Prompt injection** — 指令覆盖、角色劫持
2. **数据外泄** — 携带密钥的 HTTP POST、base64 编码
3. **破坏性命令** — rm -rf /、force-push main、chmod 777
4. **硬编码凭证** — api_key/secret_key 与长字符串
5. **混淆** — eval $()、base64 解码管道到 shell
6. **安全绕过** — bypass/disable safety/rules/hooks

扫描器区分 skills 中**讨论**安全模式（良性）和**使用**安全模式（标记）。

## 报告结构

报告按严重程度分三级：
- **Critical** — 立即修复（安全漏洞、凭证泄露、配置冲突）
- **Structural** — 尽快修复（缺失的 hooks/rules/verification、重复 skills）
- **Incremental** — 可选改进（精简描述、添加 version、优化上下文）

## 测试

```bash
python3 -m pytest tests/ -v
```

## 许可证

MIT
