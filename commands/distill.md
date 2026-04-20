---
description: 从当前项目提炼可复用知识到全局（commands/踩坑/模板/playbook/slash 生态审计）
---

用户提供了参数: $ARGUMENTS

从当前项目中提炼可复用的 commands、踩坑经验、脚本模式、Playbook 骨架，内化到全局配置。**适用任意 ~/Dev/ 或 ~/Work/ 项目**（标书 / 水利 / 站群 / CC 配置本身 / 任意代码仓），不再特化于标书。

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
| 踩坑 | 大段替换用直接重建 | 🆕 | 补进 domain CLAUDE.md |
| 脚本 | rebuild_xxx.py | 模板 | 记录模式到 CLAUDE.md |

### 3.5 Slash 生态审计（全局）

扫描 `~/Dev/cc-configs/commands/*.md` 所有 description 行，按 **4 类问题**产出 `~/Dev/stations/docs/knowledge/slash-audit-{YYYYMMDD}.md`：

| 问题类型 | 识别规则 | 举例 | 建议 |
|---------|---------|------|------|
| **① 重叠** | 2+ 命令同类动作 | `/recap` vs `/handoff`（后者 Phase 1 就是前者） | 合并 / 明确分工写入 CLAUDE.md |
| **② 职责错位** | "命令" 实际是 skill 级工作流 | `/distill` 本身（编排 Phase 1-7），`/frontend-tweak`（守门 skill） | 降级为 skill 或保持但文档注明 |
| **③ 空隙** | 高频动作无对应 skill | 本次 `/ship-site` 内部的 nginx 写入若未来要拆出 | 新增 skill（含理由） |
| **④ 冗余** | 命令被更强命令完全包含 | `/recap` ⊂ `/handoff`；某些 bash wrapper | 标"可删除 / 保留作快捷方式" |

**产出格式**（示例）：

```markdown
# Slash 生态审计 — 2026-04-19

## 统计
- 总 commands: 52
- 总 skills: 46（global）+ N（domain）
- 软链 ~/.claude/commands/ → ~/Dev/cc-configs/commands/

## 重叠（2 处）

### /recap ⊂ /handoff
- 描述：/handoff Phase 1 就是调用 /recap
- 建议：**保留两者**（/recap 单独用于"只要复盘不要交接"），但在 /handoff 文档首节明确依赖关系
- 理由：两者受众不同（/recap = CC 自己，/handoff = 下次会话）

### /retro vs /distill
- 描述：都产生 playbook / session 知识
- 建议：**保持**（retro 记本次具体，distill 记通用化），但加一段「何时选哪个」对照表到两份文档首部
- 理由：颗粒度不同，合并会损失信息密度

## 职责错位（N 处）

### /distill
- 描述：7 个 Phase 的工作流，不是原子命令
- 建议：**保留 command 身份**但新增 skill 别名 `distill-skill`（未来用户可在 CLAUDE.md 引用为 skill）
- 理由：用户已熟悉 /distill 口令，不打破 muscle memory

## 空隙（N 处）

### 缺 `/menus-refresh` 薄封装
- 描述：改 navbar.yaml 后必跑 `menus.py render-navbar -w` + `build-website-navbar -w` + audit 三步
- 建议：新增 `/menus-refresh` 3 行 bash wrapper
- 理由：高频动作（R7 以来已跑 10+ 次），手工 bash 易漏步

## 冗余（N 处）

（暂无明显可删）

## 行动（--apply 模式）

1. [ ] Edit /handoff.md 首节加「/recap 依赖说明」
2. [ ] 新建 /menus-refresh
3. [ ] Edit /retro.md 与 /distill.md 各加一段「何时选哪个」
```

**--apply 模式下**：每条建议前用 AskUserQuestion 确认再执行；不 apply 则仅产出报告。

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

| cwd 前缀 | domain | playbook 文件 |
|---------|--------|-------------|
| `~/Work/bids/` | `bids` | `~/Work/_playbooks/bids/` |
| `~/Work/eco-flow/` | `eco-flow` | `~/Work/_playbooks/eco-flow/` |
| `~/Work/zdwp/projects/reclaim/` | `reclaim` | `~/Work/_playbooks/reclaim/` |
| `~/Work/zdwp/projects/*/` | `zdwp-<子项目名>` | `~/Work/_playbooks/zdwp-*/` |
| `~/Dev/<name>/`（站群相关：configs/menus 改动、navbar、stack 等）| `stations` | `~/Dev/configs/playbooks/stations.md` |
| `~/Dev/<name>/`（新站上线相关：site-add / ship-site / launch） | `web-scaffold` | `~/Dev/configs/playbooks/web-scaffold.md` |
| `~/Dev/hydro-*/` | `hydro` | `~/Dev/configs/playbooks/hydro.md` |
| `~/Dev/cc-configs/` 或 slash 整顿 | `cc-meta` | `~/Dev/configs/playbooks/META.md` §5 新增 |
| 其他 | 询问用户 | — |

**Dev 项目的 playbook 优先落**：`~/Dev/configs/playbooks/`（与 ~/Work/_playbooks/ 并列，分别对应 "开发" 与 "工作" 两个根）。

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
