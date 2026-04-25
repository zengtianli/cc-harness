会话收尾与交接。一步完成复盘、配置升级、交接文件生成。

## 触发时机

会话结束前、任务阶段性完成时、或用户主动 `/handoff` 时执行。

## 参数

- 无参数 → 完整流程（recap + harness + HANDOFF.md）
- `quick` → 跳过 recap 和 harness，只生成 HANDOFF.md

## 完整流程

### Phase 1: 复盘（/recap）

执行 `/recap` 的全部步骤：

1. 回顾对话，提取主题、进程、成果、踩坑
2. 分析做对/做错/工程模式/沟通
3. 更新 CC 侧记录（Memory、Skills、Commands、CLAUDE.md）
4. 生成 session-retro 文件到 `~/Dev/stations/docs/knowledge/session-retro-{YYYYMMDD}.md`

### Phase 2: 配置升级检查（/harness）

基于本轮对话的收获，检查当前项目的 CC 配置是否需要升级：

1. **Skills** — 本轮是否形成了可复用的工作流？需要新建或更新 skill 吗？
2. **Commands** — 本轮是否有频繁重复的操作可以抽成 command？
3. **CLAUDE.md** — 项目级指南是否需要补充新发现的约束、路径、规范？
4. **Hooks** — 是否有需要自动化的检查点？

对需要更新的项，直接执行更新。如果没有需要更新的，跳过并简要说明。

### Phase 3: 生成 HANDOFF.md

#### Step 3.0a · Paths 健康体检（提示不阻塞）

生成 HANDOFF 前先扫路径健康度：

```bash
python3 ~/Dev/devtools/lib/tools/paths.py audit --brief
```

- 输出单行形如 `paths: 25 registered / 20 dead / 0 drift`
- **dead > 0 时不阻塞**（handoff 是收尾动作，硬阻塞会把已完成工作卡住），但**必须把这一行原样记入生成的 HANDOFF.md「踩过的坑」或「待完成」节**，提示下个会话先处理路径死链
- exit 码忽略，只采纳 stdout 内容

#### Step 3.0b · 多轮项目识别与版本号闭环

判断本轮是否属于**多轮项目**（任一命中即是）：

- 当前目录已有 `HANDOFF-<topic>-v0.N-*.md` 或 `HANDOFF-*-v1.X-*.md`
- 本轮对话标题/内容出现 `v0.X` / `v1.X` / "第 X 轮" / "下一轮" / "终点" 等措辞
- 上轮 HANDOFF.md 顶部 banner 含 `共 N 轮 → v1.0` 字样

**命中后必须用 `AskUserQuestion` 一次问全 4 项**（不要分多次）：

1. **本轮编为 v0.几？**（若之前已编号，确认下一号；若未编号，问起点）
2. **总共预计多少轮**（v0.1 → v0.N → v1.0）
3. **v1.0 = 什么样**（验收标准 / 终点定义，越具体越好）
4. **本轮闭环了哪个子任务**（对齐 v0.N 路线图里的哪一步）

未命中（单轮任务）→ 跳过此步，走默认 `HANDOFF.md`。

##### 文件名约定

- 单轮：`HANDOFF.md`
- 多轮：`HANDOFF-<topic>-v0.N-YYYY-MM-DD.md`（topic 用 kebab-case，参考 `~/Dev/HANDOFF-paths-v1.1-stations-cleanup-20260425.md`）

##### 多轮 HANDOFF 必含节（在 Step 3.1 默认模板基础上追加）

- **顶部 banner**：`> 这是 <topic> 项目的 v0.N（共 N 轮 → v1.0）— 终点：<v1.0 验收标准>`
- **「本轮闭环」节**：本轮做完了哪几件事，分别对应路线图里的哪一步
- **「下一轮 (v0.N+1)」节**：下个会话该做什么 + 启动指令

##### 反例（避免）

- 直接进 v0.1 不画终点（用户不知道目标在哪）
- 每轮事后 narrate "v0.X 完成"，不主动对齐版本号
- 悄悄出 v1.1 / v1.2 续命（v1.0 已 ship 就该 **重启 v2.0** 而不是续号）

#### Step 3.0 · 判主项目（确定落地目录）

本轮改动最集中的 repo 根作为 HANDOFF target dir。启发式：

1. **盘点本轮改动** — 扫本会话所有 Edit/Write 调用的文件绝对路径
2. **分桶计数** — 按 `~/Dev/{stations,labs,content,tools,devtools,migrated}/<top>` 归组（顶层一级子目录）
3. **挑 target**：
   - 唯一桶命中 ≥70% 改动 → 落到该 repo 根（如 `~/Dev/stations/web-stack/HANDOFF.md`）
   - 跨 3+ repo 且**根级文件**（`~/Dev/CLAUDE.md` / `~/Dev/tools/configs/playbooks/` / 目录结构本身）占主导 → 落 `~/Dev/HANDOFF.md`
   - 模糊时 → `AskUserQuestion` 给候选（top 3 改动最多的 repo + `~/Dev/`）让用户选
4. 选中 repo 无 `.git/` 也可以 — HANDOFF 本就是文档，非 git 强依赖

#### Step 3.1 · 写入

在判定的 target dir 下生成 `HANDOFF.md`（覆盖已有的）。

**格式：**

```markdown
# Handoff · {项目名}

> {YYYY-MM-DD} · {一句话当前状态}

## 当前进展

{已完成的工作，按逻辑分组，简洁但完整}

## 待完成

- [ ] {具体任务}
  - {关键决策、设计思路、注意事项}
- [ ] {具体任务}

## 关键文件

| 文件 | 说明 |
|------|------|
| {完整绝对路径} | {一句话} |

## 踩过的坑

{本轮遇到的问题和解决方案，避免下个会话重蹈覆辙}

## 下个会话启动

{建议的第一条指令或操作步骤}
```

### Phase 4: 输出汇总

向用户展示简短汇总：

```
--- Handoff 完成 ---

复盘：~/Dev/stations/docs/knowledge/session-retro-{date}.md
记忆：更新 {N} 条 / 新增 {N} 条
配置：{更新了什么 / 无需更新}
交接：{HANDOFF.md 的绝对路径}
待办：{N} 项未完成

下个会话启动：{建议指令}
```

## 规则

- HANDOFF.md 的受众是**下一个 CC 会话**，不是人类——写得像技术文档，不要散文
- 关键文件必须用**完整绝对路径**
- 待完成项要附带**思路和决策**，不只是标题
- 踩过的坑要写**根因和解法**，不只是现象
- 如果本轮没有待完成项（任务全部做完），Phase 3 可以简化，只保留"当前进展"和"关键文件"
- `quick` 模式下跳过 Phase 1 和 Phase 2，直接执行 Phase 3 和 Phase 4
- 如果当前目录已有 HANDOFF.md，直接覆盖（旧的已经过时）
- **HANDOFF 落地规则**：越靠近具体改动 repo 越好。单 station 改动 → `~/Dev/stations/<name>/HANDOFF.md`；跨站群/纯 ~/Dev 结构变更才落 `~/Dev/HANDOFF.md`。不做 symlink — 让 HANDOFF 就待在它归属的项目里
- **旧 HANDOFF 归档**：若 target dir 已有过时的 HANDOFF（话题已换）且有保留价值，先 `mv HANDOFF.md ~/Dev/stations/docs/handoffs/{YYYYMMDD}-{topic}.md` 归档再覆盖
