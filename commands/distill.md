---
description: 从当前标书项目提炼可复用知识到全局（commands/踩坑/模板）
---

用户提供了参数: $ARGUMENTS

从当前标书项目中提炼可复用的 commands、踩坑经验、脚本模式，内化到全局配置。

## 参数

- 无参数：分析当前目录，输出提炼报告
- `--apply`：执行提炼（复制 commands、更新 CLAUDE.md、写 playbook）
- `--dry-run`：只报告，不写文件
- `--skip-playbook`：跳过 Phase 6 Playbook 归档

## 流程

### 1. 盘点本项目产出

扫描以下位置：

| 位置 | 找什么 |
|------|--------|
| `.claude/commands/*.md` | 项目级 commands |
| `scripts/*.py` | 可复用脚本模式（rebuild、merge 等） |
| `HANDOFF.md` 踩过的坑 | 新教训 |
| `成果/md/*-改动草稿.md` | 改动草稿模板 |

### 2. 对比全局现有

检查每个本地 command 是否已在 `~/.claude/commands/` 存在：

```bash
for f in .claude/commands/*.md; do
  name=$(basename "$f")
  if [ -f ~/.claude/commands/"$name" ]; then
    echo "✅ 已存在: $name"
  else
    echo "🆕 待提升: $name"
  fi
done
```

同时检查 `~/Work/bids/CLAUDE.md` 的踩坑记录，看本项目 HANDOFF 中是否有新教训。

### 3. 生成提炼报告

输出表格：

| 类别 | 项目 | 状态 | 建议 |
|------|------|------|------|
| Command | batch-revise | 🆕 | 泛化后提升到全局 |
| Command | read-docx | ✅ 已存在 | 检查是否需要更新 |
| 踩坑 | 大段替换用直接重建 | 🆕 | 补进 bids/CLAUDE.md |
| 脚本 | rebuild_xxx.py | 模板 | 记录模式到 CLAUDE.md |

### 4. 执行提炼（`--apply`）

1. **泛化 commands**：移除项目特有引用（特定文件名、特定章节号），保留通用流程
2. **复制到全局**：`cp` 到 `~/.claude/commands/`
3. **更新 bids/CLAUDE.md**：追加新的踩坑条目到 "DOCX 操作踩坑记录" 节
4. **更新模板**：如果 `_template/.claude/commands/` 缺少新 commands，同步过去

### 5. 验证

- 列出所有全局 commands，确认新增的已注册
- `grep` bids/CLAUDE.md 确认踩坑条目已写入
- 输出总结

### 6. Playbook 归档（默认启用，`--skip-playbook` 可关）

**识别领域**（从 cwd 绝对路径前缀匹配）：

| cwd 前缀 | domain |
|---------|--------|
| `~/Work/bids/` | `bids` |
| `~/Work/eco-flow/` | `eco-flow` |
| `~/Work/zdwp/projects/reclaim/` | `reclaim` |
| `~/Work/zdwp/projects/*/` | `zdwp-<子项目名>` |
| 其他 | 询问用户 |

**识别"任务简称"**：优先读 `HANDOFF.md` 的首行 H1 或 `_project.yaml` 的 `name` 字段；找不到则询问用户。

**检查 playbook 是否存在**：
```bash
ls ~/Work/_playbooks/<domain>/ 2>/dev/null | grep "<项目名>-<任务简称>"
```

**分支 A：首次 distill（无 playbook）**

1. 创建 `~/Work/_playbooks/<domain>/<项目名>-<任务简称>-<YYYY-MM-DD>.md`
2. 按 `~/Work/_playbooks/README.md` 模板填：
   - **时间轴**：从本次会话的 user/assistant 消息中提取关键节点（触发→关键决策→完成），写成 `T+Nh` 格式
   - **CC 命令 / Skills**：从 tool_use 记录中抽本次用过的 slash commands + skill（不含 Bash/Read 等底层工具）
   - **脚本清单**：扫 `scripts/` 新增的 `.py`，每个标可复用度（高/中/低）+ 一句话做啥
   - **踩坑**：抽 HANDOFF.md "踩过的坑" 节 + 本次会话中的 `⚠️` / `修正` / `错误` 关键字附近内容
   - **下次复用建议**：总结"如果再遇到同类任务，按这个节奏走"
   - **可抽 skill 候选**：识别本次产出的流程骨架是否稳定到可独立封装
3. 在 `~/Work/_playbooks/INDEX.md` 对应领域表格加一行

**分支 B：已有 playbook（追加）**

1. 在现有 playbook 末尾追加 `## 后续会话追加 <YYYY-MM-DD>` 小节
2. 仅记本次会话新增的命令 / 脚本 / 踩坑（去重）
3. 更新 INDEX.md 中对应条目的"最近更新"列

**写入策略**：
- `--apply` 模式下执行写入
- 分析模式（无 flag）下只输出"将要写入 X 字节到 Y 路径"的预览

### 7. 验证 Playbook 归档

- `test -f ~/Work/_playbooks/<domain>/<file>.md` 确认生成
- `grep "<项目名>" ~/Work/_playbooks/INDEX.md` 确认索引注册
- 输出 playbook 路径让用户一键打开

## 关键约束

1. **泛化而非照搬**：移除项目名、特定文件名（如 `*0407.docx`）、特定章节号
2. **不覆盖已有全局 command**——如果全局已有同名且内容不同，列出 diff 让用户决定
3. **踩坑不重复**：先检查 bids/CLAUDE.md 是否已有相同教训
4. **变更前向用户确认**
5. **Playbook 写入时保持"时间轴+命令清单"简洁颗粒度**——参考 `~/Work/_playbooks/README.md`，不堆八股
