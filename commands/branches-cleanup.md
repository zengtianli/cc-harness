扫 ~/Dev 全部 git repo，找出已合并到 main 的分支（本地+远端），列表批准后一键删。

## 用法

```
/branches-cleanup              # 扫 ~/Dev 全部 repo
/branches-cleanup --repo <path>  # 单 repo
```

无参默认扫 `~/Dev` 全部。

## 背景

用户默认在 main 上干活，**不开 feature branch**（要开必须先讲理由）。merge 完的分支是思维负担，必须清。本 skill 把「merge 完顺手清」固化成动作。

## 执行

### 1. 收集 repo

- 无 `--repo` → `find ~/Dev -name .git -type d -maxdepth 4 -prune` 列所有 repo
- 有 `--repo <path>` → 只看这一个

### 2. 每个 repo 扫已合并分支

进 repo 目录，跑：

```bash
git fetch --prune origin                              # 同步远端 + 清死引用
git branch --merged main                              # 已合并的本地分支
git branch -r --merged main                           # 已合并的远端分支
```

**排除项**（永远不动）：
- `main` / `master`
- `HEAD` / `origin/HEAD`
- 当前 checkout 的分支（带 `*` 的那条）

### 3. 汇总表给用户

```
repo            本地分支         远端分支              最后提交
website         feat/navbar-v2   origin/feat/navbar-v2  3 天前
cmds            -                origin/fix/typo        1 周前
stack           tmp/wip          -                      2 天前
```

末尾一行：`共 N repo，待删本地 X 条 / 远端 Y 条`

**等用户确认。** 不自动删。

### 4. 批准后执行

逐 repo 跑：

```bash
git branch -d <name>                       # 本地：用 -d 不是 -D，未合并会拒绝
git push origin --delete <name>            # 远端
```

**失败立即停**：任一条 `-d` 拒绝（说明分支没真的合并）→ 停下报告，不切 `-D`。

### 5. 输出对比

```
✓ website   删除 feat/navbar-v2 (本地+远端)
✓ cmds      删除 origin/fix/typo (远端)
✗ stack     tmp/wip 拒绝（未合并到 main）— 跳过
清理后：N repo，本地 X 条 / 远端 Y 条
```

## 不做

- 不删未合并分支（绝不用 `-D`）
- 不删 `main` / `master`
- 不切分支（保持用户当前 checkout）
- 不动远端 `origin/HEAD`
- 任一步失败立即停，不继续后续 repo

## 集成

`/ship` 推完 main 之后自动调用本 skill 一次（待办：单独改 ship.md，本次不动）。
