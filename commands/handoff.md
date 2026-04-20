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
