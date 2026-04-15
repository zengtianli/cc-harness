---
description: 从当前标书项目提炼可复用知识到全局（commands/踩坑/模板）
---

用户提供了参数: $ARGUMENTS

从当前标书项目中提炼可复用的 commands、踩坑经验、脚本模式，内化到全局配置。

## 参数

- 无参数：分析当前目录，输出提炼报告
- `--apply`：执行提炼（复制 commands、更新 CLAUDE.md）
- `--dry-run`：只报告，不写文件

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

## 关键约束

1. **泛化而非照搬**：移除项目名、特定文件名（如 `*0407.docx`）、特定章节号
2. **不覆盖已有全局 command**——如果全局已有同名且内容不同，列出 diff 让用户决定
3. **踩坑不重复**：先检查 bids/CLAUDE.md 是否已有相同教训
4. **变更前向用户确认**
