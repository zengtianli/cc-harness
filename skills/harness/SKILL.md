---
name: harness
description: 管理 CC skills 跨项目分发与同步。当需要检查/同步/初始化项目 skills 配置时触发。
---

# Harness — CC 配置分发管理

Source of truth 在 `~/Dev/cc-configs/`，通过 symlink 提供全局 skills/commands/agents，通过 sync 分发项目专属 skills。

## 用法

```bash
python3 ~/Dev/cc-configs/tools/harness/harness.py status              # 查看同步状态
python3 ~/Dev/cc-configs/tools/harness/harness.py sync [--force]      # 同步到各项目
python3 ~/Dev/cc-configs/tools/harness/harness.py sync --dry-run      # 预览
python3 ~/Dev/cc-configs/tools/harness/harness.py init <project-path> # 初始化项目
python3 ~/Dev/cc-configs/tools/harness/harness.py audit <project-path> # 审计项目 CC 配置
```

## 子命令

| 命令 | 说明 |
|------|------|
| `status` | 扫描注册表，报告 synced / missing / drifted |
| `sync` | 从 repo 复制项目专属 skills。全局 skills 通过 symlink 自动生效 |
| `init <path>` | 给项目创建 .claude/skills/ 并复制注册的 skills |
| `audit <path>` | 六维度审计项目 CC 配置质量 |

## 注册表

`~/Dev/cc-configs/harness.yaml`（symlink 到 `~/.claude/harness.yaml`）

## 规则

- Source of truth: `~/Dev/cc-configs/`（GitHub 版本管理）
- 全局 skills/commands/agents 通过 symlink 自动生效，不需要 sync
- 项目专属 skills 需要 `sync` 分发
- drifted 的 skill 默认不覆盖，需 `--force`
