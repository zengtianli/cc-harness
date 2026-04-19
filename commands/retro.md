---
description: 工程复盘（工具链视角）— 从头到尾把本轮做的事写成模块化 MD，重点标出每步用了什么工具/skill/command，便于用户下次精准指挥
---

用户提供了参数: $ARGUMENTS

## 触发时机

- 用户说「写个 md 说说你刚才做了什么」「从头到尾复盘」「用了什么工具」「复用了什么 skill/command」
- 长会话结束前、多 PR 工作完成后、用户要把经验沉淀成方法论时
- 区别于 `/recap`：
  - `/recap` 偏会话复盘 + 更新 memory/skills/commands（给 CC 内部）
  - `/retro` 偏**工程流程 + 工具链视角**（给**用户**看，用户读完能更精准地指挥 CC）

## 参数

- 无参数 → 完整复盘 MD，写入 `~/Dev/docs/knowledge/session-retro-{YYYYMMDD}-{topic-slug}.md`
- `--stdout` → 只输出到屏幕不写文件
- `--path <path>` → 指定输出路径
- 短描述（如 `r7 mega`）→ 作为 topic-slug，文件名 `session-retro-20260419-r7-mega.md`

## 硬约束

**模块化分节，按时间+阶段组织。每阶段**必须**有 4 个子段**：

1. **输入** — 这个阶段拿到什么（文件路径、用户口令、上阶段产物）
2. **工具调用链** — 表格列出每步用的工具（Tool / skill / command / MCP / subagent），注明复用来源
3. **复用 vs 新增** — 明确标出哪些是复用现有资产、哪些是本次新增
4. **产出** — 具体文件路径 / commit hash / 线上验证

**第七节必须有**「复用清单 · 总览」，分 3 栏：
- 现有工具链（本次复用的所有 R1-Rn 铺好的基础设施）
- 本轮新增
- 未使用但本可用（让用户知道还有什么工具，下次可以要求 CC 用）

## 完整流程

### Phase 1 · 通读对话

从会话开头到当前位置，按时间提取：

1. 用户最初的口令（原文）
2. 你的路径规划和阶段切分（Plan mode？Task list？几个 PR？）
3. 每阶段的输入 / 工具 / 产出
4. 用户在中途的插入（AskUserQuestion 答案、纠正、澄清）
5. 最终产物清单（commits、文件、URL、audit 状态）

### Phase 2 · 识别工具链

对会话里每一次重要的工具调用，标注：

| 工具 | 类型 | 例子 |
|---|---|---|
| **内置 Tool** | 系统自带 | Read / Write / Edit / Bash / Grep / Glob / WebFetch |
| **控制流工具** | 元操作 | Plan mode / ExitPlanMode / AskUserQuestion / ToolSearch / TaskCreate / TaskUpdate |
| **Subagent** | Agent() 调用 | Explore / Plan / general-purpose / 自定义 |
| **Skill** | `Skill` tool 或被动触发 | `/recap`、`/handoff`、`/menus-audit` 等（列在 available-skills） |
| **Slash command** | 用户或 CC 输入 `/foo` | `/deploy`、`/ship` 等 |
| **MCP 工具** | 名字前缀 `mcp__` | `mcp__cclog__search_sessions` 等 |
| **项目脚本** | Bash 调用 | `navbar_refresh.sh` / `deploy.sh` / `menus.py` / `generate.py` |

**关键：要把"项目脚本"和"内置 Tool"分开**。用户想知道"我原来已经有这些工具"，所以本项目自己造的脚本（SSOT 工具链、deploy.sh、sync scripts）要单列。

### Phase 3 · 分阶段写

按"自然阶段"分节，不要死板套 3/5/7 个阶段。典型结构：

```markdown
# Session Retro · {date} · {topic}

> 一句话概述：拿到什么 → 交付了什么

## 零 · Meta
| 项 | 值 |
|---|---|
| 会话日期 | {date} |
| 主题 | {topic} |
| 基准状态 | {前置条件/上轮状态} |
| 需求入口 | {用户原话} |
| 产出 | {commits + 文件 + URL} |
| 耗时 | {估算} |

## 一 · 需求理解阶段
### 输入 / 工具调用链 / 关键发现 / 产出（plan file 等）

## 二 · 设计决策阶段（如果有 Plan mode）
### 输入 / 工具调用链 / 关键设计 / 教训

## 三..N · 各 PR/批次
### 输入 / 工具调用链 / 复用 / 新增 / 产出

## N+1 · 收尾
### audit / PROGRESS / HANDOFF / ship

## N+2 · 复用清单 · 总览
### 现有工具链 | 本轮新增 | 未使用但本可用

## N+3 · 经验教训
### 做对了什么 / 做错了什么 / 可复用模式 / 沟通模式

## N+4 · 下一轮候选
按价值排序的 TODO

## N+5 · 关键文件索引
表格：文件路径 / 行数 / 作用
```

### Phase 4 · 写"复用清单"章节（重中之重）

这一节用户看得最仔细，决定他下次怎么指挥 CC。结构：

#### 4.1 现有工具链（本次复用了哪些）

表格 3 列：**资产名 / 类型 / R7 用法**。
类型包括：SSOT 目录、Python CLI、Bash 脚本、渲染产物、Shell 脚本、文档协议、架构选择、slash skill 等。
"R7 用法"要说清楚**具体复用了哪个函数/哪个路径/哪个机制**，而不是"用了 menus.py"这种泛泛描述。

#### 4.2 本轮新增

表格 3 列：**资产名 / 类型 / 复用性**（未来几次会再用、只本次）。

#### 4.3 Anthropic 内置工具/机制

表格 2 列：**工具 / 用途 / 次数**。目的：让用户理解内置工具怎么组合出工作流。

#### 4.4 未使用但本可用

表格 2 列：**工具/skill / 为什么没用**。目的：用户看完能说"下次如果遇到 X 场景，要求 CC 用 Y 工具"。

### Phase 5 · 写"经验教训"

**做对了什么**：列 5-8 条**具体**的做对（不是"认真做事"这种废话）。例子：
- "Plan mode 里用 AskUserQuestion + ASCII preview 让用户拍板"（对比历史事故）
- "跑 `git diff` 先验证 HANDOFF 的过时信息"

**做错了什么**：列 3-5 条**具体**的错误或可优化点（CC 的，不是用户的）。要有**教训**：下次怎么做。

**可复用模式**：5 条以内，形成可命名的 pattern（比如"SSOT + renderer + audit + slash skill 四件套"）。

**沟通模式**：用户的口令/反馈透露的偏好，下次同类场景能识别。

### Phase 6 · 确定文件名 + 写盘

文件名：`~/Dev/docs/knowledge/session-retro-{YYYYMMDD}-{topic-slug}.md`

- `{YYYYMMDD}` 用当前日期（已转绝对日期）
- `{topic-slug}` 从主题提炼：`r7-mega` / `bid-cleanup` / `hydro-irrigation-fix` 等，全小写 kebab-case
- 如果同日同 slug 已存在，加 `-2`、`-3`

写盘前最后检查：
- 所有用到的**工具名**拼写正确（Tool 名看 system prompt，skill 名看 available-skills）
- 每个**复用项**的路径可访问
- 每个 **commit hash** 实际存在（如果你提了）
- 每个 **URL** 可达（如果你提了）

## 不要做的事

1. **不要**写成时间戳日志（`10:05 - 开始改文件`）。要按**阶段**+**主题**组织。
2. **不要**把每次 tool call 都列出来。只列**关键节点**。100 次 Edit 合并成一条"~20 次 Edit 跨 4 个文件"即可。
3. **不要**把 CC 行为和用户反馈混着写。"做对的"是 CC 做对的；"沟通模式"是用户偏好。
4. **不要**省略"未使用但本可用"章节——这是用户指挥 CC 的关键参考。
5. **不要**自吹。"做对了什么"只列客观工程决策，不是"我很细心"。
6. **不要**漏掉真实踩坑。CC 的错误 / 理解偏差 / 返工必须在"做错了什么"里如实写。

## 示例产物

参考 `~/Dev/docs/knowledge/session-retro-20260419-r7-mega.md`（R7 本轮产物）。

## 和其他命令的关系

| 命令 | 区别 |
|---|---|
| `/recap` | 更新 CC 内部 memory/skills；偏 CC 自我进化 |
| `/handoff` | 会话收尾三合一（recap + harness + HANDOFF.md）；偏状态传递 |
| `/distill` | 从单个项目提炼 commands / 踩坑到全局；偏知识迁移 |
| **`/retro`** | **工程流程 + 工具链视角复盘**；偏让用户看懂 CC 干了什么 |

通常在**用户主动要求**时触发 `/retro`。`/handoff` 和 `/retro` 可以同日产出（前者给 CC 自己看下次入场，后者给用户看"我用了哪些工具"）。
