---
description: 会话收尾族 — recap 复盘 / retro 写 playbook / handoff 全流程交接 / distill 提炼到全局
---

# /wrap — 会话收尾统一入口

`/wrap <subcommand> [args]`

| 子命令 | 受众 | 产出 |
|---|---|---|
| `handoff` | 下次会话 | HANDOFF.md + recap + harness 三合一（默认） |
| `recap` | CC 自己 | 更新 memory/skills/commands，session-retro MD |
| `retro` | 用户 | Playbook 式复盘（slash command 编排流程） |
| `distill` | 全局知识库 | 从项目提炼 commands / 踩坑 / playbook 骨架 |

未传子命令 → `handoff`（最完整）。

---

## handoff — 会话收尾与交接（推荐默认）

一步完成复盘、配置升级、交接文件生成。

### 参数
- 无参数 → 完整流程（recap + harness + HANDOFF.md）
- `quick` → 跳过 recap 和 harness，只生成 HANDOFF.md

### Phase 1: 复盘（内部调 recap 流程）

执行 `/wrap recap` 的全部步骤：回顾对话 / 提取主题/进程/成果/踩坑 / 分析做对做错 / 更新 CC 侧记录（Memory/Skills/Commands/CLAUDE.md）/ 生成 session-retro（默认「主项目 docs/retros/ + 中央 symlink」双向链接，见 retro 节「输出位置规则」）

### Phase 2: 配置升级检查（/harness）

基于本轮收获检查项目 CC 配置是否需要升级：Skills / Commands / CLAUDE.md / Hooks。需要更新的直接执行。

### Phase 3: 生成 HANDOFF.md

#### Step 3.0a · Paths 健康体检（提示不阻塞）

```bash
python3 ~/Dev/devtools/lib/tools/paths.py audit --brief
```

dead > 0 不阻塞，但必须把这一行原样记入生成的 HANDOFF.md「踩过的坑」或「待完成」节。

#### Step 3.0b · 多轮项目识别与版本号闭环

判断本轮是否属于多轮项目（任一命中即是）：
- 当前目录已有 `HANDOFF-<topic>-v0.N-*.md` 或 `HANDOFF-*-v1.X-*.md`
- 本轮对话出现 `v0.X` / `v1.X` / "第 X 轮" / "下一轮" / "终点"
- 上轮 HANDOFF.md 顶部 banner 含 `共 N 轮 → v1.0`

命中后必须用 AskUserQuestion 一次问全 4 项：本轮 v0.几？总共多少轮？v1.0 = 什么样？本轮闭环了哪个子任务？

未命中 → 跳过此步，走默认 `HANDOFF.md`。

##### 文件名约定
- 单轮：`HANDOFF.md`
- 多轮：`HANDOFF-<topic>-v0.N-YYYY-MM-DD.md`

##### 多轮 HANDOFF 必含节
- 顶部 banner：`> 这是 <topic> 项目的 v0.N（共 N 轮 → v1.0）— 终点：<v1.0 验收标准>`
- 「本轮闭环」节：本轮做完了哪几件事，分别对应路线图哪一步
- 「下一轮 (v0.N+1)」节：下个会话该做什么 + 启动指令

#### Step 3.0 · 判主项目（确定落地目录）

启发式：
1. 盘点本轮所有 Edit/Write 文件绝对路径
2. 按 `~/Dev/{stations,labs,content,tools,devtools,migrated}/<top>` 归组
3. 唯一桶 ≥70% 改动 → 落该 repo 根；跨 3+ repo 且根级文件占主 → `~/Dev/HANDOFF.md`；模糊用 AskUserQuestion 让用户选

#### Step 3.1 · 写入

格式：

```markdown
# Handoff · {项目名}

> {YYYY-MM-DD} · {一句话当前状态}

## 当前进展
{已完成工作，按逻辑分组}

## 待完成
- [ ] {具体任务}
  - {关键决策、设计思路、注意事项}

## 关键文件
| 文件 | 说明 |
|---|---|
| {完整绝对路径} | {一句话} |

## 踩过的坑
{本轮问题与解决方案}

## 下个会话启动
{建议第一条指令}
```

### Phase 4: 输出汇总

```
--- Handoff 完成 ---
复盘（物理）：<主项目>/docs/retros/session-retro-{date}.md
复盘（中央 symlink）：~/Dev/stations/docs/knowledge/session-retro-{date}.md
记忆：更新 {N} 条 / 新增 {N} 条
配置：{更新了什么 / 无需更新}
交接：{HANDOFF.md 的绝对路径}
待办：{N} 项未完成
下个会话启动：{建议指令}
```

无主项目（`--central` 或跨多 repo）→ 复盘行只显示中央路径。

### 规则
- HANDOFF.md 的受众是下一个 CC 会话，写得像技术文档不是散文
- 关键文件用完整绝对路径
- 待完成项附带思路和决策，不只是标题
- 踩过的坑写根因和解法
- `quick` 模式跳过 Phase 1+2
- 旧 HANDOFF（话题已换且有保留价值）→ `mv` 到 `~/Dev/stations/docs/handoffs/{YYYYMMDD}-{topic}.md`
- HANDOFF 落地：单 station 改动 → station 目录；跨站群 / ~/Dev 结构 → `~/Dev/HANDOFF.md`

---

## recap — 复盘本轮对话

通读对话，更新 CC 侧记录，生成 session retro 文件。

### Step 1: 回顾本轮对话
提取：主题 / 目的 / 进程 / 最终成果 / 踩坑经历

### Step 2: 改进与经验
分析：做对了什么 / 做错了什么 / 工程模式 / 沟通层面

### Step 3: CC 侧记录

逐项检查更新：

1. **Memory**（`~/.claude/projects/*/memory/`）— 新 feedback / project / user / reference？检查现有需更新或删除？

2. **Skills**（`~/Dev/tools/cc-configs/skills/`）— 现有 skill 需更新？需新建？

   **Skill 候选池**（`~/Dev/tools/cc-configs/skill-candidates.md`）— 识别**重复出现的工作模式**未被 skill/command 覆盖：
   - 多步操作被手动执行 2+ 次？
   - 固定判断逻辑被反复描述？
   - 特定领域知识被反复注入？

   新候选追加记录：候选名称 / 发现时间 / 出现次数 / 状态 (active|done|dismissed) / 模式描述 / 涉及项目 / 潜在 skill 类型。已存在则更新出现次数。次数 ≥ 3 提示用户正式创建。

   **Skill/Command 使用追踪**（`~/Dev/tools/cc-configs/skill-tracker.json`）— 更新 last_used / use_count / correction_count（用户纠正时）。correction_count >= 3 提示重写。

3. **Commands** — 现有需更新？需新建？

4. **CLAUDE.md** — 当前项目新约束或路径变化需记录？

### Step 3.5: Paths 健康体检（提示不阻塞）

```bash
python3 ~/Dev/devtools/lib/tools/paths.py audit --brief
```

dead > 0 不阻塞但记入 retro 文件「未完成项」节。

### Step 4: 用户侧记录

生成 session retro MD。**默认走「主项目目录 + 中央 symlink」双向链接模式**（见 retro 节「输出位置规则」），即：
- 物理：`<主项目>/docs/retros/session-retro-{YYYYMMDD}.md`（同日多 session 加 `-2.md` 后缀）
- 中央 symlink：`~/Dev/stations/docs/knowledge/session-retro-{YYYYMMDD}.md` → 物理
- 中央索引：`~/Dev/stations/docs/knowledge/INDEX.md` 追加一行

无主项目（跨多 repo）→ 直接落中央，不建 symlink。

格式：1.做对了什么 / 2.走了哪些弯路（和为什么）/ 3.工程模式 / 4.沟通反思 / 5.成果清单（路径表）/ 6.未完成项

### Step 5: 输出汇总

```
📋 本轮复盘完成
主题：...
成果：N 个文件
记忆：更新 N / 新增 N
技能候选：N 个新增 / N 个达阈值
追踪：N 个 skill/command 更新
待办：N 项
文件（物理）：<主项目>/docs/retros/session-retro-{date}.md
文件（中央 symlink）：~/Dev/stations/docs/knowledge/session-retro-{date}.md
中央索引：~/Dev/stations/docs/knowledge/INDEX.md（已追加一行）
```

无主项目时仅显示中央路径。

### 规则
- 诚实，不粉饰错误
- 踩坑写根因，不只描述现象
- 用户原话反馈如实记录
- Memory 更新具体，不写空泛"用户喜欢 X"
- 没踩坑可简写第 2 节；没新工程模式可跳过第 3 节
- retro 用中文

---

## retro — Playbook 式复盘

**Playbook，不是工具调用清单**。受众是用户，产出"这类任务的标准 slash command 编排流程"。

### 参数
- 无参数 → 走「主项目目录 + 中央 symlink」双向链接模式（见下方「输出位置规则」）
- `--central` → 强制只写中央位置 `~/Dev/stations/docs/knowledge/session-retro-{YYYYMMDD}-{topic-slug}.md`，不建 symlink。明确不属于单一项目（跨多 repo / `~/Dev` meta 级）时用
- `--stdout` → 只输出屏幕，不落盘
- `--path <path>` → 显式指定物理文件路径（仍会建中央 symlink + 更新 INDEX.md，除非 `--central`）
- 短描述（如 `r7 mega`）→ 作为 topic-slug

### 输出位置规则（默认行为）

**Step 1 · 判主项目**（复用 handoff Phase 3.0 的启发式）：
1. 盘点本轮所有 Edit/Write 文件绝对路径
2. 按 `~/Dev/{stations,labs,content,tools,devtools,migrated}/<top>` 归组
3. 唯一桶 ≥70% 改动 → 主项目 = 该 repo 根目录
4. 跨 3+ repo 且根级文件占主 → 无主项目 → 自动走 `--central`
5. 模糊用 AskUserQuestion 让用户选

**Step 2 · 写物理文件到主项目**：
- 路径：`<主项目>/docs/retros/session-retro-{YYYYMMDD}-{topic-slug}.md`
- 例：`~/Dev/wpl-calc/docs/retros/session-retro-20260501-carry-math-v0.8.md`
- `docs/retros/` 不存在则 `mkdir -p`

**Step 3 · 中央位置建相对 symlink**：
- 路径：`~/Dev/stations/docs/knowledge/session-retro-{YYYYMMDD}-{topic-slug}.md`
- macOS 命令（POSIX）：`cd ~/Dev/stations/docs/knowledge && ln -s "$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], '.'))" <物理文件绝对路径>)" session-retro-{YYYYMMDD}-{topic-slug}.md`
- 或用 `~/Dev/tools/cc-configs/tools/retro-symlink/retro_symlink.py link <物理文件>` 一句话搞定（自动算相对路径 + 更新 INDEX.md）

**Step 4 · 更新中央索引 `~/Dev/stations/docs/knowledge/INDEX.md`**：
- 文件不存在则创建，骨架：
  ```markdown
  # Session Retros 索引

  > 中央查询入口。物理文件分散在各项目 `docs/retros/`，本目录是 symlink 集合。

  ## 时间线
  ```
- 在「时间线」节追加一行（按日期倒序，最新在上）：
  `- {YYYY-MM-DD} · {主项目名} · {topic-slug 中文化简述} → {物理路径绝对地址}`
- 例：`- 2026-05-01 · wpl-calc · v0.8 carry 数学模型重构 → ~/Dev/wpl-calc/docs/retros/session-retro-20260501-carry-math-v0.8.md`

**`--central` 模式**：跳过 Step 1/2 项目判断，直接落 `~/Dev/stations/docs/knowledge/session-retro-{YYYYMMDD}-{topic-slug}.md`，不建 symlink；INDEX.md 仍追加一行，物理路径写中央位置自身。

### 硬约束 · playbook 格式

#### 必有「核心编排」节（放最前）

ASCII 流程图按阶段串起 slash command / skill：

```
用户口令「...」
  ↓
【入场】     /warmup
  ↓
【规划】     Plan mode + AskUserQuestion + ExitPlanMode
  ↓
【PR1】      Edit 核心文件
             /menus-audit
             /repo ship <repo1> <repo2>
  ↓
【PR2】      /refresh-site --kind navbar
             /deploy <site1>
             /deploy <site2>
  ↓
【收尾】     /wrap handoff
```

关键数字总结：**X 个现成 skill 本该用但漏了**、**Y 个新造**。

#### 每个 Phase 节必含
1. 用什么 `/command` 或 skill（标题级）
2. 触发时机
3. 本次怎么做的（漏用 skill 老实说"走了 bash"）
4. 正确姿势
5. 替代方案
6. 下次记得（一句话指挥建议）

不要写工具调用次数 / Read/Edit/Write 文件清单 / bash 命令原文 — 这些是工具链细节，不是 playbook。

#### 必有「通用 Playbook」节（后半）

抽象成可复用模板：

```
下次站群/navbar 改造抄这个走：

1. /warmup
2. Plan mode + AskUserQuestion
3. 核心改造（Edit）
4. /menus-audit
5. /repo ship <ssot repo>
6. /refresh-site --kind {navbar,header,content}
7. /deploy × N
8. /menus-audit（再跑）
9. /wrap handoff
```

#### 必有「本次漏了什么 skill」节

诚实标出本该用 slash command 却走了 bash：

```
我在本次犯的流程错误：
1. 开头没 /warmup
2. 验证用 bash 跑 python3 → 应 /menus-audit
3. 部署手工 cd + bash deploy.sh × 4 → 应 /deploy <name> × 4

下次你看到我手工 bash 做本该有 skill 的事，直接说"用 /xxx"。
```

### 怎么识别"应该用的 skill"

1. 通读会话，提取每个关键动作
2. 查 available-skills 列表对照
3. 匹配：找到 → 标"本该用 /xxx"；找不到 → 标"无 skill，保留工程工作"
4. 分类：工程工作 vs 编排动作

常见可 skill 化的动作：

| 动作 | skill |
|---|---|
| 进项目看状态 | `/warmup` |
| 验证 yaml/配置 | `/menus-audit` `/cf-audit` `/repo audit` |
| 同步 SSOT | `/refresh-site --kind {all,navbar,header,content}` |
| 部署 | `/deploy <name>` `/site ship <name>` |
| commit + push | `/repo ship <repo1> <repo2>` |
| 健康检查 | `/health sites` `/health vps` `/health project` |
| 会话收尾 | `/wrap handoff` `/wrap recap` `/wrap retro` |
| 整理目录 | `/tidy <path>` |
| 代码简化 | `/simplify` |
| 项目脚手架 | `/harness` |

### 反例 vs 正解

❌ 工具调用清单（流水账）—「Write × 3 / Edit × 5 / Bash × 12」

✅ Playbook —「Phase 2 · PR1 · SSOT 改造 · 验证 /menus-audit（本次走了 bash，下次记得用 skill）」

### 心智模型

写时问自己：
1. 用户下次遇到类似任务，抄这份 MD 哪几行就能指挥 CC？
2. 我本该用 skill 却走了 bash 的地方在哪？用户看完能纠正我吗？
3. 这套流程能抽象成多少条 `/command` 编排？

答得出 1/2/3 = 好 playbook；答不出 = 工具清单，作废重写。

---

## distill — 从项目提炼到全局

从当前项目提炼可复用 commands / 踩坑 / 脚本模式 / Playbook 骨架，内化到全局。**适用任意 ~/Dev/ 或 ~/Dev/Work/ 项目**。

### 参数
- 无参数：分析当前目录，输出提炼报告
- `--apply`：执行提炼（复制 commands、更新 CLAUDE.md、写 playbook）
- `--dry-run`：只报告，不写文件
- `--skip-playbook`：跳过 Phase 6

### 流程

#### 1. 盘点本项目产出
扫：`.claude/commands/*.md` / `scripts/*.py` / `HANDOFF.md` 踩坑 / `成果/md/*-改动草稿.md`

#### 2. 对比全局现有
检查每个本地 command 是否在 `~/.claude/commands/` 存在。同时检查 domain CLAUDE.md 踩坑记录。

#### 3. 生成提炼报告
表格：类别 / 项目 / 状态（🆕 / ✅）/ 建议

#### 3.5 Slash 生态审计（全局）

扫 `~/Dev/tools/cc-configs/commands/*.md` 所有 description 行，按 4 类问题产出 `~/Dev/stations/docs/knowledge/slash-audit-{YYYYMMDD}.md`：

| 问题 | 识别 | 举例 | 建议 |
|---|---|---|---|
| ① 重叠 | 2+ 命令同类动作 | `/wrap recap` vs `/wrap handoff`（后者含前者） | 文档说明分工 |
| ② 职责错位 | 命令实际是 skill 级工作流 | `/wrap distill` 编排 7 phase | 降级 skill 或文档注明 |
| ③ 空隙 | 高频动作无 skill | nginx 写入若未来要拆 | 新增 skill |
| ④ 冗余 | 命令被更强命令完全包含 | bash wrapper | 标"可删 / 保留快捷方式" |

`--apply` 模式：每条建议前 AskUserQuestion 确认；不 apply 则仅产报告。

#### 4. 执行提炼（`--apply`）
1. 泛化 commands（移除项目特有引用）
2. `cp` 到 `~/.claude/commands/`
3. 更新 domain CLAUDE.md 踩坑节
4. 同步 `_template/.claude/commands/`

#### 5. 验证
列全局 commands 确认已注册；grep CLAUDE.md 确认踩坑写入。

#### 6. Playbook 归档（默认启用，`--skip-playbook` 关）

cwd 前缀匹配 domain：

| cwd 前缀 | domain | playbook 文件 |
|---|---|---|
| `~/Dev/Work/bids/` | `bids` | `~/Dev/Work/_playbooks/bids/` |
| `~/Dev/Work/eco-flow/` | `eco-flow` | `~/Dev/Work/_playbooks/eco-flow/` |
| `~/Dev/Work/zdwp/projects/reclaim/` | `reclaim` | `~/Dev/Work/_playbooks/reclaim/` |
| `~/Dev/Work/zdwp/projects/*/` | `zdwp-<子项目名>` | `~/Dev/Work/_playbooks/zdwp-*/` |
| `~/Dev/<name>/`（站群） | `stations` | `~/Dev/tools/configs/playbooks/stations.md` |
| `~/Dev/<name>/`（新站） | `web-scaffold` | `~/Dev/tools/configs/playbooks/web-scaffold.md` |
| `~/Dev/hydro-*/` | `hydro` | `~/Dev/tools/configs/playbooks/hydro.md` |
| `~/Dev/tools/cc-configs/` 或 slash 整顿 | `cc-meta` | `~/Dev/tools/configs/playbooks/META.md` §5 |
| 其他 | 询问用户 | — |

**首次 distill（无 playbook）**：建文件，按 README 模板填时间轴 / CC 命令 Skills / 脚本清单（可复用度 高/中/低）/ 踩坑 / 下次复用建议 / 可抽 skill 候选；INDEX.md 加一行。

**已有 playbook（追加）**：末尾 `## 后续会话追加 <YYYY-MM-DD>` 小节；INDEX.md 更新"最近更新"列。

写入策略：`--apply` 执行；分析模式只输出"将写入 X 字节到 Y 路径"。

#### 7. 验证 Playbook 归档
- `test -f` 确认生成
- `grep` INDEX.md 确认索引注册
- 输出 playbook 路径

### 关键约束
1. 泛化而非照搬（移除项目名 / 文件名 / 章节号）
2. 不覆盖已有全局 command — 同名不同内容则列 diff 让用户决定
3. 踩坑不重复（先检查 domain CLAUDE.md）
4. 变更前向用户确认
5. Playbook 写入保持时间轴 + 命令清单简洁颗粒度

---

## 参考

- Playbook 总入口：`~/Dev/tools/configs/playbooks/META.md`
- 中央 retro 索引：`~/Dev/stations/docs/knowledge/INDEX.md`（symlink 集合 + 时间线）
- retro symlink 工具：`~/Dev/tools/cc-configs/tools/retro-symlink/retro_symlink.py`（link 单文件 / migrate 批量回迁）
- 旧示例（单一中央）：`~/Dev/stations/docs/knowledge/session-retro-20260419-r7-mega.md`
- 新示例（物理 + symlink）：`~/Dev/wpl-calc/docs/retros/session-retro-20260501-carry-math-v0.8.md` ← `~/Dev/stations/docs/knowledge/session-retro-20260501-carry-math-v0.8.md`
