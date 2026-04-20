批量 git pull --ff-only。

## 范围

从 $ARGUMENTS 确定目标（同 /ship 的参数规范）：
- 无参数 → 当前目录（必须是 git repo）
- `.` → 当前目录
- `<name> [name2 ...]` → 在 `~/Dev/tools/configs/repo-map.json` 查 `local` 路径
- `all` → repo-map.json 中所有 `"ignored": false` 的 repo

## 流程

对每个目标 repo：
1. 解析 `local` 路径，确认目录存在
2. `git fetch --all --prune`
3. `git pull --ff-only`
4. 如果 ff-only 失败（diverged），报 ⚠ 不强制操作

## 输出

```
✓ dockit          pulled (2 commits)
✓ hydro-rainfall  already up to date
⚠ vps             diverged — manual resolve needed
— oauth-proxy     no remote tracking branch
✗ hydro-qgis      directory not found
```

## 规则

- 永远不 force pull 或 auto-rebase
- 跳过 `local` 路径不存在的 repo（报 ✗）
- 跳过 `"ignored": true` 的 repo
