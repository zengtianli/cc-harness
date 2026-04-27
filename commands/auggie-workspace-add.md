---
description: 把一个 repo 加入 auggie workspace 注册表 SSOT（yaml + build + audit），CC 后续可 resolve 到
---

`/auggie-workspace-add <id> <abs-path-or-~-path> [extra options]`

## 何时用

- 新 clone 一个 repo 到 ~/Dev 想被 auggie 索引
- 移动 / 重命名了某个已有 workspace 的路径
- 升降级 indexable（把数据型 repo 标 `indexable: false` 等）

## 参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `<id>` | ✅ | 稳定 slug，CC dispatch 用（建议跟 GitHub repo 名一致；目录名 ≠ id 时 notes 里标注） |
| `<path>` | ✅ | `~/Dev/...` 或绝对路径 |
| `--github=<owner/repo>` | | 不传则探测 `git -C <path> remote get-url origin` |
| `--type=code\|docs\|data\|meta` | | 默认 `code` |
| `--status=active\|archive\|data\|deprecated` | | 默认 `active` |
| `--indexable=true\|false` | | 默认 `true`；data/archive 默认 `false` |
| `--notes=<text>` | | 可选注解 |

## 流程

### 1. 参数检查 + 路径校验

- `<path>` 展开后必须存在，不存在直接报错
- `<id>` 在现有 yaml 里不能重复（先 `grep "^  - id: <id>$"` `~/Dev/tools/configs/auggie-workspaces.yaml`）

### 2. 自动探测（可选字段未传时）

- **github**: `git -C <expanded-path> remote get-url origin 2>/dev/null`，转成 `owner/repo` 形式；探不到 → `null` + visibility 设 `local-only`
- **visibility**: 已传 github 时跑 `gh repo view <owner/repo> --json visibility,isArchived -q '.visibility|ascii_downcase + (if .isArchived then ":archived" else "" end)'`
- **type**: 默认 `code`；如果 path 下含 `*.zip / *.pdf / *.shp / *.dbf` 大量数据 → 自动建议 `data` + 让用户确认

### 3. 体积闸门（破坏性反模式拦截）

跑 `/usr/bin/du -sh <path>`，单 repo > 500 MB → 强制提示：

> ⚠️ `<path>` size = <X>。建议设 `type=data, indexable=false, github=null`，
> 数据型不上 GitHub 不索引（参考 memory `feedback_data_vs_code_repo.md`）。
> 仍要按 code 处理？(y/N)

### 4. 写 yaml

在 `~/Dev/tools/configs/auggie-workspaces.yaml` 的合适分组（按目录大类：tools / labs / content / Work / migrated）末尾追加新条目，缩进对齐：

```yaml
  - id: <id>
    path: <path>
    github: <owner/repo or null>
    visibility: <visibility>
    status: <status>
    type: <type>
    indexable: <true/false>
    notes: <notes if present>
```

### 5. 重生成派生 + 校验

```bash
python3 ~/Dev/devtools/lib/tools/auggie_workspaces.py build
python3 ~/Dev/devtools/lib/tools/auggie_workspaces.py audit
```

任一失败 → 报错回退（`git checkout -- ~/Dev/tools/configs/auggie-workspaces.yaml`）。

### 6. 验证 dispatch

```bash
python3 ~/Dev/devtools/lib/tools/auggie_workspaces.py resolve <id>
```

应输出绝对路径。

### 7. 提示

```
✅ 加入注册表：<id> → <path>
   indexable: <true/false>
   github: <owner/repo or none>

下次调 auggie 直接：
  WS=$(python3 ~/Dev/devtools/lib/tools/auggie_workspaces.py resolve <id>)
  auggie -p -a -q "..." -w "$WS"
```

提示用户是否 `cd ~/Dev/tools/configs && git commit`（pre-commit hook 会自动跑 auggie audit gate）。

## 反模式 / 守门

- 不允许把 `~/Dev` 整个加进来（已存在 `dev-meta` 条目，indexable=false）
- 不允许把 `_archive/*` 子目录加进来
- `path` 必须是 git repo（`.git/` 存在），否则 auggie 索引意义不大

## 参考

- SSOT: `~/Dev/tools/configs/auggie-workspaces.yaml`
- 派生器: `~/Dev/devtools/lib/tools/auggie_workspaces.py`
- 协议: `~/.claude/CLAUDE.md` § auggie 使用规范 → workspace dispatch 协议
- Memory: `reference_auggie_workspaces_registry.md`
