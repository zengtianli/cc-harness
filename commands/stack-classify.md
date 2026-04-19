扫描 ~/Dev 所有项目，产出技术栈 × 部署 × 活跃度 × 迁移目标的**只读分类清单**。$ARGUMENTS 可选。

- 不动目录，不改文件
- 与 `/tidy`（破坏性文档清理）互不干扰
- 支持过滤与多种输出格式

## $ARGUMENTS

```
--target <path>           # 扫描目标，默认 ~/Dev
--format md|json|table    # 输出格式，默认 md
--filter <regex>          # 只输出 path/name 匹配正则的条目
--include-archived        # 也扫 _archived / scripts-archive
```

## 调用

```bash
python3 ~/Dev/devtools/lib/tools/classify.py $ARGUMENTS
```

## 输出列

| 列 | 含义 |
|---|---|
| `Project` | 目录名 |
| `Stack` | nextjs / streamlit / fastapi / python-cli / node / static / config / docs / monorepo / unknown |
| `Deployed` | 子域（从 `~/Dev/website/lib/services.ts` 读）或 `—` |
| `30d Commits` | 近 30 天 git 提交数 |
| `Migration Target` | `apps/<name>-web` / `already-nextjs` / `to-monorepo` / `keep-as-is` / `archive-candidate` / `fastapi-only` / `n/a` |
| `Notes` | 备注 |

## 典型用法

```
/stack-classify
/stack-classify --format table
/stack-classify --format json --filter hydro
/stack-classify --include-archived
```

## 判断规则（按优先级）

1. `next.config.*` → `nextjs`
2. `pnpm-workspace.yaml` / `turbo.json` → `monorepo`
3. `pyproject.toml` / `requirements.txt` 含 `streamlit` → `streamlit`
4. 同上但含 `fastapi` 且无 streamlit → `fastapi`
5. 仅 `pyproject.toml` / `requirements.txt` → `python-cli`
6. `package.json`（非 next）→ `node`
7. `.claude/commands/` → `config`
8. `deploy.sh` / `generate.py` → `static`
9. 目录下 >50% 是 `.md` → `docs`
10. 其他 → `unknown`

## 迁移目标映射

| Stack | 目标 |
|---|---|
| streamlit | `apps/<name>-web` — pilot pattern，Python 保留 + FastAPI wrapper |
| nextjs | `already-nextjs` — 可选并入 `~/Dev/web-stack` |
| fastapi | `fastapi-only` — 后端复用，前端走 monorepo |
| python-cli / config / docs / node / monorepo | `keep-as-is` |
| static + deployed | `keep-as-is`（视觉刷新走 `/site-refresh-all`） |
| 无 git + 未部署 + 30 天静默 | `archive-candidate` |

## 不做

- 不搬目录（要搬走 `/tidy` 或手工）
- 不修改 `.git` / remote
- 不碰 `~/Dev/_archived/`（除非 `--include-archived`）
