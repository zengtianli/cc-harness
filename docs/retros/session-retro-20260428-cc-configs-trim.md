# Session Retro · 2026-04-28 · CC 配置三轮瘦身

> Topic: memory + commands + CLAUDE.md 三层瘦身（73→29 / 73→60 / 双层去重）

## 核心编排

```
用户口令「合并 memory skill commands」+ /insights 触发
  ↓
【Round 1 入场】 /effort max + 用户讨论
  ↓
【盘候选】     批 Read 当前 MEMORY.md + 重叠 memory
              → AskUserQuestion 颗粒度（粗/中/细）
  ↓
【Round 1 执行】 4 合并 + 2 新增（17 → 6）
              并行 Write 6 + 一条 Bash rm 15
  ↓
【Round 2 讨论】 用户问"我的工作流变化" + memory 折旧机制
              → 多 Bash + Read 收集证据（git log / mtime / retros）
              → 判断 14 条已内化 / 已被超集
  ↓
【Round 2 执行】 删 14 条 + 重写 MEMORY.md
  ↓
【用户嫌不够】  "东西太多记不住用不好"
              → /effort max + 进入 Plan mode
  ↓
【Plan 调研】   3 个 Explore agents 并发（commands / CLAUDE.md / 死链）
              → 实地读 5 个 commands 文件验证 agent 结论
              → AskUserQuestion 拍板（commands 真合并 vs 归档 vs cheatsheet）
  ↓
【Plan v3 写】  Write plan file → ExitPlanMode → 用户批准
  ↓
【Round 3 执行】 24 Read（合并源）→ 7 并行 Write（新合并 memory）
              → 1 Bash rm 38（28 旧 memory + 10 旧 commands）
              → Write refresh-site.md + Edit auggie/repo-map/cf
              → CLAUDE.md 双层重写 + cf.md frontmatter
              → MEMORY.md 重写
  ↓
【收尾】       2 并行 Bash commit+push（cc-configs + ~/Dev meta）
```

关键数字：**3 轮 plan 迭代** · **3 个 Explore agents 并发** · **Phase A 7 并行 Write** · **Phase B 4 并行 ops**。

---

## Phase 1 · 用户讨论（不动手，对齐颗粒度）

### 用什么 skill：`AskUserQuestion` + 用户对话

**触发时机**：用户给抽象需求（"合并 memory 和 skills"），未指定颗粒度。

**本次怎么做的**：第一次给 3 档（粗/中/细）让用户选。用户没选具体档，反而进了"我的变化"对话。

**正确姿势**：抽象任务先 `AskUserQuestion` 问 1-2 个核心选择，不直接出 v1 plan。颗粒度 + 范围对齐再写。

**下次记得**：用户说"X 可以合并的吧" 是邀请讨论，不是给 spec —— 拉开 1 轮对话。

---

## Phase 2 · 实证盘清候选（必走）

### 用什么 skill：`Read` + `Glob` + `Grep` 多文件并行

**触发时机**：要决定"X 和 Y 能不能合并"。

**本次怎么做的**：v1 plan 凭直觉写"sites-health → services-health"互相超集。被嫌"收益低"后，进 Plan mode + Explore agents 实地盘 5 个 commands 文件，发现：
- `/sites-health` vs `/services-health` 互补（services-health 自己 § 相关 引用 sites-health）
- `/handoff` `/recap` `/retro` `/distill` 受众分工清楚（CC自己 / 用户 / 团队 / 全局）—— 不能合
- refresh 4 件套是 master + 3 atomic（可合到 `--kind` 子参数）
- auggie 3 个独立功能但同主题（可合到子命令）

**正确姿势**：合并候选**必须实地读两个文件**再判断，不凭 description 字面 OR 个人直觉。

**下次记得**：合并是减熵，**减错了反而增熵**（破坏分工 → 后期再拆开成本更高）。

---

## Phase 3 · Plan 迭代（v1 → v2 → v3）

### 用什么 skill：Plan mode + Write plan file + ExitPlanMode

**触发时机**：多步任务 + 跨 layer + 涉及破坏性删除。

**本次怎么做的**：
- v1（保守）：删 3 + 修死链 + 补 frontmatter — 用户嫌"收益不高"
- v2（中等）：memory 7 组合并 + commands 删过期 — 用户嫌"东西太多记不住"
- v3（激进）：v2 + commands 真合并（refresh 4→1, auggie 3→1, repo-map 2→1）

**正确姿势**：plan 必须切**用户痛点**。痛点不是"代码层"问题，是"用户认知负担"。前两轮没读懂。

**下次记得**：用户说"东西太多" → 优先减**用户感知**的入口数量（commands），不是 CC 内部资产（memory 用户根本不直接读）。

---

## Phase 4 · Round 3 执行（并行优先）

### 用什么 skill：批量 Read → 批量 Write/Edit/Bash

**触发时机**：多文件相关改动（28 删 + 7 新增 + 多 Edit）。

**本次怎么做的**：
1. 24 Read 并行（4 已在 context）
2. 7 Write 并行（新合并 memory）
3. 1 Bash rm 38（一条命令删 28 memory + 10 commands）
4. Write refresh-site + 2 Edit + 1 Edit cf.md 并行
5. CLAUDE.md 双层重写 + cf.md frontmatter 并行
6. 2 Bash commit+push 并行

**正确姿势**：✅ 这次做对了。同一 message 多 tool call，不分批串行。

**下次记得**：合并产物 Write 完先验证 `ls` 数量再 rm 旧文件（防止 rm 提前导致 Write 失败信息丢失）。本次顺序：先 Write 后 rm，已守住。

---

## 通用 Playbook · CC 配置瘦身

下次「memory/commands/CLAUDE.md 太多」抄这个走：

```
1. /warmup                          # 看现状
2. AskUserQuestion 颗粒度 + 范围    # 粗/中/细 × memory/commands/CLAUDE.md
3. Plan mode：
   3a. Explore agents 并发盘
       - commands 重叠 / 过期 / 分工
       - CLAUDE.md 双层冗余
       - 已删 memory 死链残留
   3b. 实地 Read 关键合并候选 5-10 个
   3c. Write plan file → ExitPlanMode
4. Round N 执行：
   4a. 批量 Read 合并源
   4b. 并行 Write 新合并产物
   4c. 一条 Bash rm 旧文件批量删
   4d. Edit 死链 + 跨层指针化
   4e. Write 新索引（MEMORY.md）
5. 验证：
   5a. ls 数量对比 plan 期望
   5b. grep 死链 0 命中
   5c. git status 看遗漏
6. /ship 或手动 commit+push 多 repo
```

---

## 本次漏了什么 skill

| 漏的 skill | 应该用的场景 | 下次记得 |
|---|---|---|
| `/preflight` | Round 3 执行前盘破坏性 rm 38 文件爆炸半径 | 大批量删除前必跑 |
| `/menus-audit` | refresh-site 合并涉及 navbar/header/content SSOT 引用 | 涉及 menus 类合并必跑 audit |
| `/critique` | v1/v2 plan 草案审一遍可能省 1-2 轮 | plan 草案先 /critique |

---

## 沟通层面反思

- ✅ 用户两次回头嫌"收益不高 / 思维负担" → 立即 reset 重写 plan，没固执
- ✅ /sites-health 误判子集后立即承认互补，不嘴硬
- ✅ "用户内化的就可删" 这个洞察是用户教的（不是我自己悟的）— 老实承认
- ⚠️ Round 1 第一次给 3 档颗粒度对的，但用户不挑直接进对话 → 我也没及时进对话模式，还在 plan 思维。下次抓信号更敏感

---

## 成果清单

| 产物 | 路径 | 说明 |
|---|---|---|
| 7 合并 memory | `~/.claude/projects/-Users-tianli-Dev/memory/{reference_vps,reference_stations_arch,reference_cc_infra,feedback_execution_style,feedback_verify_universal,feedback_frontend_gotchas,user_profile}.md` | 28 旧 → 7 新 |
| MEMORY.md 索引 | `~/.claude/projects/-Users-tianli-Dev/memory/MEMORY.md` | 29 条 |
| /refresh-site | `~/Dev/tools/cc-configs/commands/refresh-site.md` | 4 旧 refresh 合并到 --kind 子参数 |
| /auggie 扩展 | `~/Dev/tools/cc-configs/commands/auggie.md` | + ws-add + map 子命令 |
| /repo-map 扩展 | `~/Dev/tools/cc-configs/commands/repo-map.md` | + regen 子命令 |
| 项目级 CLAUDE.md | `~/Dev/CLAUDE.md` | 138 → 125 行（跨层指针化） |
| 全局 CLAUDE.md | `~/.claude/CLAUDE.md` | 删反代档案 + skill 表更新 |
| Plan 文件 | `~/.claude/plans/agent-quiet-eagle.md` | v1→v3 决策记录 |
| HANDOFF | `~/Dev/HANDOFF.md` | 本次替代 ssot-os v1.0 状态 |
| 旧 HANDOFF 归档 | `~/Dev/stations/docs/handoffs/20260428-ssot-os-v1.0.md` | ssot-os 项目结束状态 |
