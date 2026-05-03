# Session Retro · 2026-05-02 · cmd-protocol — /wrap+/start+KB v0.2 协议级升级

> 主题：narrow patch → 用户怒怼"逐子命令系统升级了吗" → A+B+C 三大件 + agent team 多并行实施
> 模式：**协议级升级 > 单点 patch**、**agent team 并行 > 单线串行**、**KB 聚合器加 source > 各自查**

---

## 1. 做对了什么

### 1.1 第一波：handoff wrap-cmd-evolution 收尾（3 commits）
- `9a0723e` cc-configs：wrap.md 5 处过时点（personal-kb 进 distill 表 + dead 阈值阶梯 + cf-audit→cf + retro 示例 ×3）
- `b30b91c` tools/configs：新立 `playbooks/personal-kb.md`（META §3 8 节骨架）+ META §5 同步触发表
- `1dab657` Dev meta：归档上轮 handoff（含 "拆 vs 不拆"调研结论 = 不拆，单 /wrap 命令统御）

### 1.2 第二波：A+B+C 系统级升级（4 commits · agent team 并行）
- **A · KB v0.2**（`a20d9ac` configs）：catalog 聚合器加 `handoff-archive` 域 — schema.yaml + extract.py 3 处 surgical edit。一个 `kb.py search` 全私域命中 7 domain（投资/简历/软著/handoff/handoff-archive/retro/knowledge）
- **B · /wrap 协议升级**（`e7e420f` cc-configs）：顶部新加「§ 跨子命令编排协议」节（4 子节：唯一写入入口表 / priority marker `[P0]/[defer]/[external]` / handoff↔recap 内部合约 / multi-slug 协调矩阵）。retro 简化 150→54 行，distill 78→44 行，**总行数 455→400**
- **C · warmup.py 升级**（`d0ffab0` devtools）：加 4 函数（`_parse_priority` / `_extract_unfinished_multi` / `_format_priority_item` / `_suggest_slug`）+ `section_handoff` 多 handoff 分支（按 slug 分组前 12 条 + priority marker 高亮 + slug 推荐避免串线）。`_extract_unfinished` 返回类型 `list[str] → list[tuple[priority, content]]`，向后兼容验证过
- **同 push 改 start.md L37**：Phase 1 输出段第 3 项重写为多 handoff 跨汇总 + priority marker 解析展示（`**[P0]**` 加粗 / `~~[defer-vX.Y]~~` 灰化 / `⏳[external]`）

### 1.3 personal-kb DB 表同步（`fd21e35`）
v0.2 表更新到 ~106 entries（含 4 条 handoff-archive），CLAUDE.md 字段说明对齐。

### 1.4 agent team 并行实施
A/B/C 三大件并行 dispatch：A 跑 catalog build + audit、B 改 wrap.md 单文件大段重写、C 改 warmup.py 函数族。三路独立可并行，~25 分钟拿到 4 commits（vs 串行预估 ~70 分钟）。

---

## 2. 走了哪些弯路

### 2.1 第一波只 patch 5 处过时点 → 用户怒怼"逐子命令系统升级了吗"
- **现象**：第一波处理 wrap-cmd-evolution 的 3 项 + 顺手 fix 2 项过时点，就报告"完成"
- **用户原话**："/start 彻底对这些命令也进行对应的更新和优化，最高收益激进计划" "你先多agent，agent team 调查"
- **根因**：我倾向"narrow patch + 等用户确认"，没主动审视"是否系统级升级"。用户问的"输入源 / 输出目的地 / 多对多场景"本质是 4 子命令的协议级 gap
- **下次怎么办**：用户说"命令更新"= 默认"协议级 / 跨子命令"，**不是单点 patch**。先 dispatch agent team 调研 4 子命令 gap → 列 P0/P1/P2 → 才动手

### 2.2 paths dead 56（>50 触发协议升级阈值）但跟本会话无关
- **现象**：本会话尾期 `paths audit --brief` → `56 dead`，按刚立的协议应升级到「待完成」首项
- **判别**：paths 死链是 dev-meta 既有问题，已在另一活跃 handoff `domain-migration-prep` 标注。**不在 cmd-protocol 重复列入**（避免两 handoff 同挂一项）
- **学到**：协议触发阈值要配合"归属判别"，不要僵化套用

### 2.3 agent A 报 entries 数 127→106 而非预期 150+
- **现象**：spec 估"127 → 150-200"，实际 build.py 后 private=106
- **判别**：audit `leaks=0` 表示无安全泄露；entries 数是工程指标不是安全指标。诚实记 CLAUDE.md "~106" + 注明既有 dup id / visibility 边界 case 待 v0.3 清理。**不为追求"漂亮数字"虚报或调 schema**

### 2.4 retro/distill 大段简化用 Edit ×N 多次匹配失败
- **现象**：retro 节 ~150 行 + distill 节 ~78 行要替换为简化版
- **处理**：改用 Bash python3 内联脚本 `text[:retro_start] + new_retro + new_distill + text[ref_start:]` 一次性替换两块
- **判别**：单文件大段替换（>100 行）= python 内联（`text.index(anchor)` 定位）；小段 = Edit；跨文件 = subagent

### 2.5 catalog.public.json paths migration 自动 rewrite
- **现象**：commit configs 时 pre-commit hook 检测到 catalog.public.json 含 migrated refs，自动 rewrite 2 条引用
- **判别**：派生产物（catalog.* / services.ts / nginx out 等）含旧路径 → hook 自动改，不用手管。SSOT 文件（schema.yaml / paths.yaml）才需手工 migration

---

## 3. 工程模式（可抽象 / 可复用）

### 3.1 narrow patch vs 协议级升级 判别表
| 用户说 | 默认理解 |
|---|---|
| "X 不对，改一下" + 指明具体点 | narrow patch |
| "彻底 / 全面 / 激进 / 系统 / 一一 / 命令更新" | **协议级升级** |
| "刚才那 N 项处理掉" | narrow patch（处理列表） |
| "下个会话彻底做 /wrap 进化" | 协议级升级（先 agent 调研 gap） |

判别后**第一动作**：协议级升级 → dispatch agent team 调研 → 列 P0/P1/P2 → 用户批准后并行实施；narrow patch → 直接动手。

### 3.2 agent team 并行实施 pattern
独立的多大件改造（A/B/C 互不依赖）：
```
1. 先全员 调研 / spec（同 message 派 N 个 调研 agent + 硬时限 10min）
2. 主会话基于调研结果列 spec + AskUserQuestion 拍板
3. 同 message 派 N 个 实施 agent（A=KB schema / B=单文件大段重写 / C=函数族）
4. 主会话收口：跑 build / audit / 验证 / commit
```
本会话 A+B+C 三路并行 ~25min（vs 串行 ~70min）。**判别**：能切独立切片（不同文件 / 不同 repo / 不同 layer）= 并行；同一文件多处 = 串行 Edit。

### 3.3 KB 聚合器加 source 域 pattern
新接入一个数据源（handoff-archive / 新 content 子目录）：
```
1. schema.yaml 加一个 source 块（path_glob + visibility + 字段抽取规则）
2. extract.py 改 3 处：dispatcher / 对应 extractor 函数 / metadata 映射
3. kb.py import 重建 DB
4. audit 跑 leaks / dup id / visibility 边界
5. CLAUDE.md DB 表 entries 数对齐
```
4-5 个文件 surgical edit，不 touch core schema。

### 3.4 priority marker 协议（[P0] / [defer-vX.Y] / [external]）
handoff 待办格式统一：
- `**[P0]**` 加粗高亮（warmup 摘要置顶）
- `~~[defer-v0.x]~~` 灰化（不挂当前会话）
- `⏳[external]` 用户/外部依赖（不挂自己头上）
- 无 marker = P1（默认）

`/start` warmup.py 解析 marker → 跨 handoff 汇总 + 按 slug 分组前 12 条。

---

## 4. Handoff 状态对接

本会话产物已归档：
- **archived handoff**：`/Users/tianli/Dev/handoffs/_archive/2026-05-02-cmd-protocol.md`（详尽列 4 项待办 + 5 项踩过的坑 + 关键文件表）
- **下个会话启动**：A 选项继续 domain-migration-prep / B 选项用着看反馈调整 cmd-protocol / C 选项 KB v0.2→v0.3 治理

cmd-protocol handoff 列出的 4 项待办：
- [external] ×2：用户用 `/start` 多 handoff 项目验证跨汇总输出 + slug 推荐 / 用户用 `/wrap handoff` 验证 priority marker 落地
- [P2] ×2：catalog 既有 dup id（`session-retro-20260429` / `session-retro-20260419-assets-launch`）+ visibility 边界 case（5 条 private 漂 public，`leaks=0` 不影响安全）— 留 KB v0.3 时清理

本 retro 不再展开待办清单（那是 handoff 的事）。
