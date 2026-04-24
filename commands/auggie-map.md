---
description: 为大型项目生成二进制文件地图（_files.md），推到 GitHub 供 Auggie 索引
---

用户提供了参数: $ARGUMENTS

为大型项目生成文件地图，让 Auggie 能索引那些不推 GitHub 的二进制文件。

## 流程

### 1. 解析参数

从 `$ARGUMENTS` 解析：
- **目标路径**（必填）：项目根目录，如 `~/Dev/Work/zdwp`、`~/Dev/Work/reports`
- **--depth N**（可选，默认 3）：扫描深度
- **--dry-run**（可选）：只生成不提交

如果未提供目标路径，提示用户。

### 2. 验证前置条件

- 目标目录存在且是 git 仓库
- `.gitignore` 已包含 `!_files.md`（白名单模式下）；如果没有，提示用户是否添加

### 3. 运行扫描脚本

使用现有脚本生成 `_files.md`：

```bash
python3 ~/Dev/_archive/scripts-archive/scripts/file/scan_binary_manifest.py \
  --target <目标路径> \
  --depth <深度> \
  --clean
```

### 4. 生成项目级汇总

在项目根目录生成 `_PROJECT_MAP.md`，内容包含：

```markdown
# 项目地图 - <项目名>

> 自动生成，供 Auggie 索引 | 更新时间: YYYY-MM-DD HH:MM

## 目录结构

（用 tree 命令生成，depth 2，仅目录）

## 文件统计

| 类型 | 数量 | 总大小 |
|------|------|--------|
| .docx | 42 | 1.2 GB |
| .xlsx | 18 | 320 MB |
| ...  |     |        |

## 各目录文件清单

（列出所有生成的 _files.md 位置及各自包含的文件数量）
```

### 5. 提交并推送

如果不是 `--dry-run`：

1. `git add` 所有 `_files.md` 和 `_PROJECT_MAP.md`
2. 提交：`chore: update auggie file map`
3. `git push`

### 6. 报告结果

输出：
- 生成了多少个 `_files.md`
- 涵盖多少个二进制文件
- 是否已推送到 GitHub
- 提示用户可以用 Auggie 搜索这些文件信息了

## 注意事项

- `_files.md` 已在 zdwp 的 `.gitignore` 白名单中
- `_PROJECT_MAP.md` 需确认也在白名单中，否则加入
- 脚本路径：`~/Dev/_archive/scripts-archive/scripts/file/scan_binary_manifest.py`
- 只扫描二进制文件（docx/pdf/xlsx/shp/zip/tif 等），文本文件本身已被 git 跟踪
