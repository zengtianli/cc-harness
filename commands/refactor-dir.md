---
description: 搬目录 + 零死链的原子工作流。加 paths.yaml migration → mv → rewrite-dead → build-const → scan-dead 验证。
argument-hint: <old> <new> [--dry] [--no-rewrite] [--reason "<text>"]
---

将目录 `<old>` 搬到 `<new>`，同时维护 `paths.yaml` SSOT + 批量重写老文档引用 + 零新死链验证。

## 用法

```bash
/refactor-dir ~/Dev/<old> ~/Dev/labs/<old> --reason "新 repo 归 labs 孵化"
/refactor-dir ~/Dev/<old> ~/Dev/_archive/<old>-YYYY-MM --no-rewrite   # 归档场景跳过 rewrite
/refactor-dir ~/Dev/<old> ~/Dev/<new> --dry                           # 只预览计划
```

## 何时用

- 搬一个 `~/Dev/<xxx>` 目录到新位置（labs/ / stations/ / tools/ / content/ / _archive/ 任意）
- 触发词：「搬目录 / 搬 repo / 归档项目 / refactor-dir / 把 X 挪到 Y」
- **不是**：新建 stations 子项目（用 `/station-promote`）；不是 CF 子域下线（用 `/site-archive`）

## 执行（CC 按顺序做）

### Step 1 · Preflight
- 验证 `<old>` 存在
- 验证 `<new>` 不存在
- 若 `<old>` 是 git repo：`git status` 检查 clean（有未提交警告但不阻断）
- 失败即中止，报告原因

### Step 2 · 引用扫描（非阻塞预警）
用 Grep tool 扫下列位置中 `<old>` 出现的次数（三种写法都扫：`~/Dev/...` + `/Users/tianli/Dev/...` + 裸路径片段）：
- `~/Dev/tools/cc-configs/`
- `~/Dev/tools/configs/`
- `~/Dev/devtools/`
- `~/Dev/stations/docs/`
- `~/Dev/CLAUDE.md` / `~/Dev/HANDOFF.md` / `~/Dev/paths.yaml`

汇总命中数作为 Step 5 rewrite-dead 影响面预估。

### Step 3 · 追加 paths.yaml migration
用 Edit 工具往 `~/Dev/paths.yaml` 的 `migrations:` 节追加（**双写 `~/` 和 `/Users/tianli/`**）：

```yaml
  # <--reason 的内容>
  - {from: <old-home>, to: <new-home>}
  - {from: <old-absolute>, to: <new-absolute>}
```

- `<old-home>` / `<new-home>` = 用 `~/` 开头的形式
- `<old-absolute>` / `<new-absolute>` = 展开到 `/Users/tianli/...`
- 顺序：放在 `migrations:` 节末尾，除非 new 覆盖范围更小则靠前（避免父路径误伤子路径）

### Step 4 · 执行 mv

```bash
# 父目录不存在先创建
mkdir -p "$(dirname <new>)"
mv <old> <new>
```

### Step 5 · rewrite-dead（若无 `--no-rewrite`）

```bash
python3 ~/Dev/devtools/lib/tools/paths.py rewrite-dead --dry-run
# ← 预览将改哪些文件 / 多少行

# 若 --dry 开启：到此中止
# 否则实跑：
python3 ~/Dev/devtools/lib/tools/paths.py rewrite-dead
```

### Step 6 · build-const 刷派生

```bash
python3 ~/Dev/devtools/lib/tools/paths.py build-const -w
```

### Step 7 · scan-dead 验证

```bash
python3 ~/Dev/devtools/lib/tools/paths.py scan-dead --strict
```

- exit 0 = 零新死链，通过
- exit 非 0 = 有死链 → 打印详情 + **不自动回滚**（可能是历史债，由用户判断）

### Step 8 · Summary 打印

列出：
- 搬迁 `<old> → <new>`
- 新加 migration 条数
- rewrite-dead 影响文件数（若跑了）
- paths_const.py 是否刷新
- 接下来建议 commit 的 repo：
  - `~/Dev/paths.yaml` → dev-meta repo
  - `~/Dev/devtools/lib/paths_const.py` → devtools repo（若 Step 6 有变）
  - 被 rewrite-dead 改到的各 repo（Step 2 grep 结果里命中的位置）

## 失败回滚

| 步骤失败 | 回滚动作 |
|---|---|
| Step 1 Preflight | 无改动，直接退出 |
| Step 3 Edit paths.yaml | 工具会原子报错；无 mv 发生 |
| Step 4 mv 失败 | 用 Edit 工具删回 Step 3 加的 migration 条目 |
| Step 5 rewrite-dead 失败 | `mv <new> <old>` 反向 + 删 migration 条目 |
| Step 7 scan-dead 发现新死链 | **不回滚** — 打印详情让用户判断（新死链可能是先前的历史债显露） |

## 不做

- 不动 GitHub remote（归档独立 repo 时保留原 origin）
- 不自动 commit（让用户 diff 后决定）
- 不动 symlink / systemd / nginx / CF（这些不耦合 ~/Dev 源码路径）
- 不递归重命名 `<old>` 的子目录（`<old>` 必须是要搬的叶子 target）
- 不合并目录（`<new>` 必须不存在）

## 依赖

- `~/Dev/paths.yaml`（SSOT · 手写）
- `~/Dev/devtools/lib/tools/paths.py`（CLI: rewrite-dead/build-const/scan-dead）
- `~/Dev/devtools/lib/paths_const.py`（派生）

## 参考 playbook

完整 SOP + 踩坑 + 扩展机制见 `~/Dev/tools/configs/playbooks/paths.md`。
