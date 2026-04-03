文件卫生 + Git 状态检查。发现问题可调用 /tidy 清理。

## 范围

从 $ARGUMENTS 确定目标（同 /pull）：
- 无参数 → 当前目录
- `<name> [name2 ...]` → repo-map.json 查路径
- `all` → 所有 non-ignored repo

## 检查项

### 1. Git 状态
- uncommitted changes（`git status --short`）
- behind remote（`git fetch --dry-run 2>&1`）
- untracked 大文件 >10MB（`find . -not -path './.git/*' -size +10M`）
- 敏感文件被 track（`.env`、`*.pem`、`*.key`、`credentials*`）

### 2. 文件卫生
- 垃圾文件：`~$*`、`.DS_Store`、`Thumbs.db`、`__pycache__/`、`.~lock.*`
- docx 解包残留：包含 `word/`、`_rels/`、`[Content_Types].xml` 的目录
- 版本冗余：`deliverables/`、`docs/` 下同一文档的多个版本

### 3. ~/Work/ 目录额外检查
- 如果在 `~/Work/zdwp/` 下，额外运行 `python3 ~/Dev/devtools/scripts/tools/zdwp_health.py`
- 大目录（>1GB）提醒

## 输出

```
✅ doctools        — clean
⚠️  hydro-rainfall — 3 uncommitted files, 2 __pycache__/
⚠️  zdwp           — 5 version chains in deliverables/, 12 garbage files
✗  oauth-proxy    — .env tracked by git!
```

末尾汇总：`N checked, X clean, Y need attention`

## 清理

输出后若有可清理项，问用户：
- `是否调用 /tidy 清理？[Y/n]`

$ARGUMENTS 含 `--fix` 时自动调用 /tidy，不二次确认。

## 调用的原子命令

- `/tidy` — 目录深度整理
