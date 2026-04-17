---
description: 给闲置站点赋新用途 — 更新 projects.yaml 的 status/notes 并记入 memory
---

把一个闲置/archived 子域标记为重新激活，写入用途说明。配合 `/ship-site` 做实际部署。

## 用法

```bash
/site-activate <name> --purpose "新的用途描述"
```

## 执行

```bash
name="$1"; shift
purpose=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --purpose) purpose="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done
if [[ -z "$purpose" ]]; then
  echo "Usage: /site-activate <name> --purpose \"...\"" >&2
  exit 1
fi

yaml="$HOME/Dev/stack/projects.yaml"
today=$(date +%F)

# 更新 projects.yaml
if grep -q "- name: $name" "$yaml"; then
  python3 - <<PY
import re, sys
from pathlib import Path
p = Path("$yaml")
text = p.read_text()
# Mark the block starting with - name: $name as active + set notes
pattern = re.compile(r'(- name:\s*$name\s*\n(?:\s+[^\n]*\n)*?)', re.MULTILINE)
def repl(m):
    block = m.group(1)
    # remove existing status/notes
    block = re.sub(r'^\s+status:.*\n', '', block, flags=re.MULTILINE)
    block = re.sub(r'^\s+notes:.*\n', '', block, flags=re.MULTILINE)
    indent = '        '  # 8 spaces; projects are under groups.services.*
    return block + f"{indent}status: active\n{indent}notes: Reactivated $today — $purpose\n"
new = pattern.sub(repl, text, count=1)
p.write_text(new)
print("✓ projects.yaml updated")
PY
else
  echo "⚠ projects.yaml: $name not found — run /site-add first"
fi

# 追加到 memory 日志
memfile="$HOME/.claude/projects/-Users-tianli-Dev/memory/site_activations.md"
if [[ ! -f "$memfile" ]]; then
  cat > "$memfile" <<EOF
---
name: Site Activations Log
description: 子域重新激活记录，每行一个 activation
type: project
---

EOF
  # 加索引到 MEMORY.md
  idx="$HOME/.claude/projects/-Users-tianli-Dev/memory/MEMORY.md"
  grep -q "site_activations.md" "$idx" || \
    echo "- [Site Activations Log](site_activations.md) — 子域激活时间线" >> "$idx"
fi
echo "$today  $name  $purpose" >> "$memfile"
echo "✓ memory logged: $today $name"

echo
echo "Next: if nginx/CF Access 需改，跑 /ship-site $name"
```

## 规则

- 只动 projects.yaml 和 memory，不碰 CF / nginx / services.ts — 激活后的实际部署交给 `/ship-site`
- memory 文件 `site_activations.md` 首次触发会自动创建 + 登记到索引
