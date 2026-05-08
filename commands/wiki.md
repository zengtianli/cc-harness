---
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, mcp__auggie__codebase-retrieval
description: Wiki 工作流族（项目本地 / super vault / Obsidian / 任意目录）— new 立 topic / entry 加条目 / verify 验完整性 / link 项目 wiki / rebuild 重生 _meta。强制 frontmatter + [[wikilinks]] + 50-150 行 + MOC。
---

# /wiki — 多目的地 wiki 工作流

把工作内容体系化进 `<vault>/wiki/topics/<topic>/`。**vault 不限定 Obsidian** — 可以是项目本地（`--here`）、super vault（cwd 父目录的 `.obsidian/`）、任意路径（`--vault <path>`）或提炼层 `~/Obsidian/dev-vault`（`--global`）。强制约定：frontmatter / `[[wikilinks]]` / 50-150 行 / 每 topic 有 `_INDEX.md` MOC。

```
/wiki new <slug> "<descrip>" [--vault <path>] [--here] [--global]
/wiki entry <topic> <slug> [--vault <path>] [--here] [--global]
/wiki verify [<topic>] [--vault <path>] [--here] [--global]
/wiki link <project-path> [--vault <path>] [--here] [--global]
/wiki rebuild [--vault <path>] [--here] [--global]
```

> v0.3 (2026-05-08)：加 `--here` flag — cwd 即 vault 根，**跳过** `.obsidian/` 探测。任意目录都能当 wiki 容器，**不强制 Obsidian**。Obsidian 只是众多目的地之一（`--global`），不是默认。
>
> v0.2 (2026-05-07)：vault-scoped — 默认按 cwd 找最近 `.obsidian/` parent 当 vault root，不再固定 `~/Obsidian/dev-vault`。详见下方「Vault 解析」节。

约定参考 `~/Dev/tools/configs/playbooks/obsidian-wiki.md`。本 command 是该 playbook 的**自动化执行版**。

---

## 全局约定（所有子命令必守）

### 路径

- Vault 根：由 cwd 解析（见下方「Vault 解析」节），或 `--here` 直接用 cwd，或 `--vault <path>` 指定；fallback `~/Obsidian/dev-vault/`
- Topic 目录：`<vault>/wiki/topics/<topic-slug>/`（提炼层 `~/Obsidian/dev-vault` 走旧 `topics/<topic-slug>/`）
- 每 topic 必有：`_INDEX.md` MOC + N 个 entry md
- 跨项目项目级 wiki（symlink）：`topics/<topic-from-topic-index>/<project-name>/` ← 项目的 `docs/wiki/`

### Frontmatter（每个 md 必有）

```yaml
---
tags: [<topic>, <subtag1>, <subtag2>]
aliases: [<别名 1>, <别名 2>]
created: YYYY-MM-DD
---
```

`_INDEX.md` 加 `moc` 进 tags。

### 链接风格

- **直接写在 vault 的 topic** → 全用 `[[wikilinks]]`，禁 `[](file.md)`
- **symlink 进来的项目 wiki** → 保持项目内原有 markdown link（不动）
- 跨 topic 引用：`[[../<topic>/<entry>]]` 或 `[[../<topic>/_INDEX|<别名>]]`

### 长度

- Reference 类 entry：**50-150 行**
- 行动页 / INDEX：**50-200 行**
- 超 200 行 → 拆；30 行以下 → 合并或不写

### 数量

- 每 topic 默认 ≤ 8 entry（含 INDEX）
- 超 10 必 AskUserQuestion 复述边界

### MOC（_INDEX.md）必有

- 一句话定位
- 目录（按主题分组的 entry 列表）
- 关键速查表（2-4 表）
- 跨 topic 相关链接
- "改这里？去 SoT"指示

---

## Vault 解析（默认行为）

`/wiki` 不再固定 `~/Obsidian/dev-vault` — 根据 cwd 自动定位 vault：

| 场景 | 解析结果 |
|---|---|
| 传 `--here` | **cwd 即 vault 根**（跳过 .obsidian 探测）|
| 传 `--vault <path>` | **指定路径即 vault 根**（跳过探测）|
| 传 `--global` | **强制 `~/Obsidian/dev-vault`**（提炼层） |
| cwd 在 `~/Dev/stations/` 内 | `~/Dev/stations/`（子 vault） |
| cwd 在 `~/Dev/content/` 内 | `~/Dev/content/`（子 vault） |
| cwd 在 `~/Dev/` 顶层（非子 vault 子目录） | `~/Dev/`（super vault） |
| 找不到任何 `.obsidian/` 父目录 | fallback `~/Obsidian/dev-vault`（向后兼容） |

**显式覆盖**（按优先级排）：
- `--vault <path>` 指定任意 vault root（最强，**推荐**）
- `--here` cwd 即 vault 根（项目本地，**v0.3 新增**，跳过 .obsidian 探测）
- `--global` 强制写 `~/Obsidian/dev-vault`（旧的"提炼层"，Obsidian 应用可见）

> Obsidian 不是默认目的地 —— 是 `--global` 一种选项。各种目录都能当 wiki 容器，Obsidian 只是其中之一。

### 输出位置约定

| Vault | 路径 |
|---|---|
| `~/Obsidian/dev-vault`（提炼层） | `<vault>/topics/<topic>/` (旧布局，保留向后兼容) |
| 其他所有 vault | `<vault>/wiki/topics/<topic>/` (新约定，不污染 vault 根) |

理由：super vault `~/Dev/` 已含 stations/ content/ labs/ 等顶级目录，新增 topics/ 顶层会污染；用 `wiki/topics/` 子目录隔离。

### 实例

```bash
# 在站群项目内立站群专属 wiki
cd ~/Dev/stations && /wiki new mega-navbar "站群顶部导航 SSOT 拓扑"
# → 写到 ~/Dev/stations/wiki/topics/mega-navbar/

# 跨项目主题写到 super vault
cd ~/Dev && /wiki new project-coordination "跨项目协作流"
# → 写到 ~/Dev/wiki/topics/project-coordination/

# 项目本地 wiki（v0.3 新增 --here）—— 项目无 .obsidian/ 也行
cd ~/Dev/sale-estates && /wiki new butterfly-park-pricing "西溪蝶园定价分析" --here
# → 写到 ~/Dev/sale-estates/wiki/topics/butterfly-park-pricing/
# 跳过 .obsidian/ 探测，sale-estates 目录直接当 vault 根

# 显式指任意路径
/wiki new my-topic "..." --vault /tmp/some-vault
# → /tmp/some-vault/wiki/topics/my-topic/

# 写进提炼层（Obsidian 应用可见）
/wiki new bid-lifecycle "标书全周期" --global
# → 写到 ~/Obsidian/dev-vault/topics/bid-lifecycle/
```

**多目的地的实务建议**：写到一个主目的地（项目本地 / super vault / `--vault`），需要 Obsidian 应用查看时再用 `/wiki link <project> --global` 把项目 symlink 进 dev-vault。**不复制内容到多处** —— SoT 单一，多处 = 漂移。

---

## /wiki new

立新 topic — 创建目录 + INDEX + 引导 entry 生成。

### 流程

```
0. 解析 vault root（cwd 找最近 `.obsidian/` parent；尊重 `--vault` / `--global`）
1. 校验 topic-slug：kebab-case，不带空格
2. 检查是否已存在：`[[ -e <vault>/wiki/topics/<slug> ]]`（提炼层走 `<vault>/topics/<slug>`）→ 已存在则报告 + exit
3. AskUserQuestion 3 项：
   ├─ 内容源（哪些 path / repo 抽？）
   ├─ 估几个 entry（4-6 推荐，>8 必复述）
   └─ 是否跨 topic 引用（哪些 sibling topic）
4. 第一动作 mcp__auggie__codebase-retrieval（如内容源 indexable）拿主题清单
5. `mkdir -p <vault>/wiki/topics/<slug>`（提炼层 `<vault>/topics/<slug>`）
6. Write _INDEX.md 骨架（按下方模板）
7. 列建议的 entry 名 + 主题给用户拍板
8. 用户批准 → 进 /wiki entry 流程逐个生成
9. 完成后 → /wiki verify <slug> + 提示更新 README
```

### _INDEX.md 模板

```markdown
---
tags: [moc, <topic>]
aliases: [<topic 中文名>]
created: <YYYY-MM-DD>
---

# <topic 中文名> · MOC

> <一句话定位>。SoT 在 `<源路径>`。这里是阅读副本。

## 目录

- [[<entry-1>]] — <一句话简介>
- [[<entry-2>]] — <一句话简介>
- ...

## 关键速查（2-4 个表，按 topic 实际）

| ... | ... |
|---|---|

## 来源

| 这里的条目 | 原始 SoT |
|---|---|
| [[<entry-1>]] | `<源文件路径>` |
| ... | ... |

**改文档去 SoT，不要改这里**。

## 相关 topic

- [[../<sibling-1>/_INDEX]]
- [[../<sibling-2>/_INDEX]]
```

---

## /wiki entry

加 entry 到既有 topic。

### 流程

```
0. 解析 vault root（cwd 找最近 `.obsidian/` parent；尊重 `--vault` / `--global`）
1. 校验 topic 存在：`[[ -d <vault>/wiki/topics/<topic> ]]`（提炼层 `<vault>/topics/<topic>`）
2. 校验 entry 不存在
3. 询问内容源（如 /wiki new 时未指定）
4. 第一动作 auggie（如适用）抽核心要点
5. Write entry md（按下方模板）
6. 更新 _INDEX.md 目录节加新行
7. /wiki verify <topic> 自动跑（不阻塞但报告问题）
```

### Entry 模板

```markdown
---
tags: [<topic>, <subtag>]
aliases: [<别名>]
created: <YYYY-MM-DD>
---

# <entry 标题>

> <一句话定位 / 价值>

## <主体节 1>

<高密度内容，不 transcribe。提炼 + 表格 + 速查清单>

## <主体节 2>

...

## 反模式 / 常见坑（如适用）

❌ ...
❌ ...

## 相关

- [[<sibling-entry>]]
- [[../<other-topic>/<entry>]]

---

_<可选脚注：触发事件 / 历史背景 1 行>_
```

---

## /wiki verify

检查 vault wiki 完整性。无参数 = 全 vault；传 topic = 只查那个 topic。

### 检查项（5 个）

```bash
# vault root 由 cwd 解析；此处 TOPIC_PATH 默认 = $VAULT_ROOT/wiki/topics（提炼层 = $VAULT_ROOT/topics）
# fallback 仅在找不到 .obsidian/ 时走 ~/Obsidian/dev-vault/topics（旧布局）
TOPIC_PATH="${1:-${VAULT_ROOT:-$HOME/Obsidian/dev-vault}/topics}"

# 1. Frontmatter 缺失
echo "=== Frontmatter ==="
missing=0
for f in $TOPIC_PATH/*.md $TOPIC_PATH/*/*.md; do
  [ -f "$f" ] || continue
  head -1 "$f" 2>/dev/null | grep -q '^---$' || { echo "❌ $f"; missing=$((missing+1)); }
done
[ $missing -eq 0 ] && echo "✅ 全部带 frontmatter"

# 2. 行数（50-200 范围；INDEX 可放宽）
echo "=== 行数检查 ==="
for f in $TOPIC_PATH/*/*.md; do
  [ -f "$f" ] || continue
  lines=$(wc -l < "$f")
  if [[ $lines -lt 30 ]]; then echo "⚠ 太短 ($lines): $f"
  elif [[ $lines -gt 200 ]]; then echo "⚠ 太长 ($lines): $f"
  fi
done

# 3. markdown link（应该是 [[wikilinks]]，不应有 [text](xx.md)）
echo "=== markdown 死链 ==="
grep -rEn '\]\([a-zA-Z0-9_-]+\.md\)' $TOPIC_PATH/ 2>/dev/null \
  | grep -vE '`\[\]|不要这样|wiki 用|建议|反例' | head -10 || echo "✅ 0"

# 4. broken wikilinks（跨 topic + 同 topic）
echo "=== broken wikilinks ==="
for f in $TOPIC_PATH/*/*.md; do
  [ -f "$f" ] || continue
  for link in $(grep -oE '\[\[[a-zA-Z0-9/_-]+(\|[^]]+)?\]\]' "$f" | sed 's/\[\[//; s/|.*\]\]//; s/\]\]//' | sort -u); do
    dir=$(dirname "$f")
    if [[ "$link" == ../* ]]; then
      target_dir="$dir/$(dirname $link)"
      target_name=$(basename "$link")
      if [ ! -e "$target_dir/${target_name}.md" ] && [ ! -e "$target_dir/${target_name}/_INDEX.md" ]; then
        echo "⚠ broken: [[$link]] in $f"
      fi
    elif [ ! -e "$dir/${link}.md" ]; then
      # 排除代码块内的反例（[[wikilink]] 用做示例）
      grep -q "\`\[\[${link}\]\]\`" "$f" || echo "⚠ broken: [[$link]] in $f"
    fi
  done
done | sort -u | head -10

# 5. INDEX 缺失
echo "=== INDEX 缺失 ==="
for d in $TOPIC_PATH/*/; do
  # 跳过 symlinked dir
  [ -L "${d%/}" ] && continue
  [ ! -f "$d/_INDEX.md" ] && echo "⚠ no _INDEX.md: $d"
done
```

输出格式：每项一行 ✅ / ⚠ / ❌。

---

## /wiki link

把项目的 `docs/wiki/` symlink 进 vault（封装现成的 `obsidian_sync.py link`）。

### 流程

```
0. 解析 vault root（cwd 找最近 `.obsidian/` parent；尊重 `--vault` / `--global`）
1. 校验 project-path 存在 + 有 docs/wiki/ 子目录
2. `python3 ~/Dev/devtools/lib/tools/obsidian_sync.py link <project-path> [--vault <vault>] [--global]`
3. 自动反查 topic-index.yaml 找该项目对应 topic
4. 建 symlink 到 `<vault>/wiki/topics/<topic>/<project-name>/`（提炼层 `<vault>/topics/<topic>/<project-name>/`）
5. 报告 md_files 数 + topic 归属
```

无 `docs/wiki/` 怎么办：
- 提示用户先用 `/wiki new` 立 topic 把内容直接写进 vault
- 或在项目内先建 `docs/wiki/` + `obsidian-wiki.md` playbook 拆了再 link

---

## /wiki rebuild

重生 `_meta/projects-index.md` + `_meta/topic-graph.md`。

```bash
python3 ~/Dev/devtools/lib/tools/obsidian_sync.py rebuild-index
```

什么时候用：
- `/wiki link <new-project>` 后
- `/wiki unlink <old-project>` 后（如有 unlink）
- 怀疑 _meta 漂移时

---

## 反模式（命令运行时立即纠正）

❌ topic-slug 用驼峰 / 含空格 / 含中文 → 强制 kebab-case
❌ 没 INDEX 就生 entry → /wiki entry 必须先确认 INDEX 存在
❌ 单 topic 写 12+ entry → 超 10 必 AskUserQuestion 复述边界
❌ 把 STATUS / README 放进 docs/wiki/ → /wiki 拒绝接受根目录 MD 入 wiki
❌ entry 用 markdown link 而非 wikilink → /wiki verify 报红
❌ entry < 30 行 / > 200 行 → /wiki verify 报警

---

## 与其他 skill 的分工

| 场景 | 用谁 |
|---|---|
| 把工作内容体系化进 vault | **本 command** |
| 在子 vault（stations/content）内立 wiki | **本 command** 默认行为（cd 进项目目录后跑 /wiki new） |
| 拆长 reference 多条目（项目内） | 走 `~/Dev/tools/configs/playbooks/obsidian-wiki.md` 流程 |
| 整理目录文件命名 | `/tidy` |
| 写项目 README / CLAUDE / STATUS | 不走 wiki，单文件高密度 |
| 命令本身的 SSOT 治理 | `/refresh-site` `/menus-audit` |

---

## 完成定义

- [ ] 新 topic 目录创建 + INDEX + N entry 全写完
- [ ] `/wiki verify <topic>` 全 ✅
- [ ] vault README 加新 topic 入口（手动 Edit 或本 command 自动加）
- [ ] 报告：N 文件 / 总行数 / 跨 topic 引用清单
- [ ] 提示用户在 Obsidian 里 `Cmd+G` 看 graph view 验证
