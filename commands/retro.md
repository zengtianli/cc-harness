---
description: 产出 Playbook 式复盘 — 用 slash command / skill 为主角串起"这类任务应该怎么做"的可复用流程。用户下次读完能按步骤指挥 CC。
---

用户提供了参数: $ARGUMENTS

## 核心定位

**Playbook，不是工具调用清单**。

用户知道 bash / Read / Edit / Write 是什么，**不需要**你列"我用了 20 次 Edit"这种底层调用。

用户想知道的是：**"这类任务的标准流程是什么 slash command / skill 编排"**，下次他说"做 X" 的时候，能准确指挥 CC 用哪几个 `/command` 顺序跑过去。

## 和其他命令的区别

| 命令 | 受众 | 产出重点 |
|---|---|---|
| `/recap` | CC 自己 | 更新 memory/skills，session-retro MD |
| `/handoff` | 团队/下次会话 | HANDOFF.md + recap + harness 三合一 |
| `/distill` | 全局知识库 | 从项目提炼 commands/踩坑 |
| **`/retro`** | **用户** | **"这类任务的 slash command 编排流程"** |

## 参数

- 无参数 → 写 playbook MD 到 `~/Dev/stations/docs-renamed-test/knowledge/session-retro-{YYYYMMDD}-{topic-slug}.md`
- `--stdout` → 只输出到屏幕
- `--path <path>` → 指定输出路径
- 短描述（如 `r7 mega`）→ 作为 topic-slug

## 硬约束 · playbook 格式

### 必须有「核心编排」节（放最前）

用 ASCII 流程图 **按阶段** 串起 slash command / skill。示例：

```
用户口令「...」
  ↓
【入场】     /warmup
  ↓
【规划】     Plan mode + AskUserQuestion + ExitPlanMode
  ↓
【PR1】      Edit 核心文件
             /menus-audit
             /ship <repo1> <repo2>
  ↓
【PR2】      /navbar-refresh
             /deploy <site1>
             /deploy <site2>
  ↓
【收尾】     /handoff
```

关键数字总结：**X 个现成 skill 本该用但漏了**、**Y 个新造**。

### 每个 Phase 节必须包含

1. **用什么 `/command` 或 skill**（标题级）
2. **触发时机**（什么场景应该用这个）
3. **本次怎么做的**（如果漏用了 skill 就老实说"走了 bash"）
4. **正确姿势**（应该怎么用 skill）
5. **替代方案**（没 skill 的场景怎么办，或 skill 不够用时）
6. **下次记得**（一句话的指挥建议）

不要写工具调用次数、不要列 Read/Edit/Write 的文件清单、不要贴 bash 命令原文——这些叫"工具链细节"，不是 playbook。

### 必须有「通用 Playbook」节（放后半）

把本次任务**抽象成可复用模板**。例：

```
下次站群/navbar 改造抄这个走：

1. /warmup
2. Plan mode + AskUserQuestion
3. 核心改造（Edit）
4. /menus-audit
5. /ship <ssot repo>
6. /navbar-refresh（或 /site-header-refresh / /site-content-refresh）
7. /deploy × N
8. /menus-audit（再跑）
9. /handoff
```

让用户抄走就能指挥 CC 做下次类似任务。

### 必须有「本次漏了什么 skill」节

诚实标出**本该用 slash command 却走了 bash**的地方。这是 playbook 的核心教育价值——**让用户下次能纠正 CC**。例：

```
我在本次犯的流程错误：
1. 开头没 /warmup
2. 验证用 bash 跑 python3 → 应 /menus-audit
3. 部署手工 cd + bash deploy.sh × 4 → 应 /deploy <name> × 4
...

下次你看到我手工 bash 做本该有 skill 的事，直接说"用 /xxx"。
```

## 怎么识别"应该用的 skill"

### 流程

1. **通读会话**：提取每个关键动作（同步文件、部署、验证、提交、收尾）
2. **查 available-skills 列表**：对照系统 prompt 里 `# userSkills` 节 的 skill 清单
3. **匹配**：每个动作找最对应的 skill。找到了 → 标"本该用 /xxx"；找不到 → 标"无 skill，保留工程工作"
4. **分类**：把动作分成
   - **工程工作**（Edit/Write 真实内容，无法 skill 化）
   - **编排动作**（应该走 skill：同步、部署、验证、提交、收尾）

### 常见可 skill 化的动作

| 动作类型 | 典型 skill |
|---|---|
| 进项目看状态 | `/warmup` |
| 规划多步/破坏性任务 | Plan mode（内置，不是 skill 但是流程关键） |
| 提问用户拍板 | `AskUserQuestion`（内置控制流工具） |
| 验证 yaml/配置漂移 | `/menus-audit` `/cf-audit` `/audit` |
| 同步 SSOT 到消费者 | `/navbar-refresh` `/site-header-refresh` `/site-content-refresh` |
| 部署项目 | `/deploy <name>` `/ship-site <name>` |
| git commit + push | `/ship <repo1> <repo2>` |
| 健康检查 | `/sites-health` `/vps-status` `/health` |
| 会话收尾 | `/handoff` / `/recap` / `/retro` |
| 整理目录 | `/tidy <path>` |
| 代码简化复查 | `/simplify` |
| 项目配置脚手架 | `/harness` |

## 反例 · 不要写成这样

### ❌ 工具调用清单（初版错误风格）

```
工具调用链：
| 步 | 工具 | 目标文件 | 动作 |
| 1 | Write | navbar.yaml | 改 mega_categories |
| 2 | Bash | python3 menus.py validate | 跑验证 |
| 3 | Edit × 3 | menus.py | 改 3 处 |
...
```

这是流水账，用户不想要。

### ✅ Playbook（正确风格）

```
## Phase 2 · PR1 · SSOT 改造

### 核心改造：Edit yaml + renderer（无法 skill 化）

### 验证：/menus-audit（本次走了 bash，下次记得用 skill）

触发时机：改完任何 menus/ 下的 yaml → 必跑
本次怎么做的：python3 menus.py audit
正确姿势：/menus-audit，自动 8 类 drift 报告
下次记得：改 yaml 就 /menus-audit

### 提交：/ship configs devtools（本次漏了，手写 git）

正确姿势：/ship configs devtools 一条命令两 repo commit + push
下次记得：PR 级交付就 /ship
```

## 输出文件

- 默认：`~/Dev/stations/docs-renamed-test/knowledge/session-retro-{YYYYMMDD}-{topic-slug}.md`
- `--stdout` → 不写盘

文件名示例：
- `session-retro-20260419-r7-mega.md`（R7 mega menu 重构）
- `session-retro-20260420-bid-xxcounty.md`（某县标书）
- `session-retro-20260421-hydro-geocode-bug.md`（某 bug 修复）

## 示例产物

参考 `~/Dev/stations/docs-renamed-test/knowledge/session-retro-20260419-r7-mega.md` —— R7 本轮的 playbook，含「核心编排」「通用 Playbook」「本次漏了什么 skill」三节。

## 心智模型

写 `/retro` 时问自己：

1. 用户下次遇到类似任务，**抄这份 MD 的哪几行**就能指挥 CC？
2. 我**本该用 skill 却走了 bash** 的地方在哪里？用户看完能纠正我吗？
3. 这套流程能**抽象成多少条 `/command` 的编排**？

如果答得出 1/2/3，就是好 playbook。

答不出来 = 写成了工具清单，作废重写。
