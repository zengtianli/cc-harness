# Agent: 项目内容完整性检查员

## 任务目标

检查 Dashboard 中所有项目卡片，确保每个可点击的卡片都有实际内容。删除或修复空项目。

## 背景

- OA Dashboard 地址：`http://localhost:3000`
- 项目数据来源：`/Users/tianli/Downloads/zdwp/.oa/data/projects.json`
- 项目物理目录：`/Users/tianli/Downloads/zdwp/02_业务项目/`
- Dashboard 显示 6 个标准文件夹：数据、成果、文档、参考、代码、县市项目

## 问题定义

"空项目"指：项目卡片可点击，但详情页无任何文件显示（6个标准文件夹都为空）。

## 检查步骤

### 1. 获取所有项目列表

```bash
# 找到所有有 _project.yaml 的目录
find /Users/tianli/Downloads/zdwp/02_业务项目 -name "_project.yaml" | while read yaml; do
  dir=$(dirname "$yaml")
  echo "$dir"
done
```

### 2. 检查每个项目的标准文件夹

对于每个项目目录，检查是否有以下任一文件夹且包含文件：
- 数据/
- 成果/
- 文档/
- 参考/
- 代码/
- 县市项目/

```bash
# 检查单个项目是否为空
check_empty() {
  dir="$1"
  for folder in 数据 成果 文档 参考 代码 县市项目; do
    if [ -d "$dir/$folder" ]; then
      count=$(find "$dir/$folder" -type f ! -name ".*" | wc -l | tr -d ' ')
      if [ "$count" -gt 0 ]; then
        return 1  # 不为空
      fi
    fi
  done
  return 0  # 为空
}
```

### 3. 批量检查脚本

```bash
echo "=== 检查空项目 ===" 
find /Users/tianli/Downloads/zdwp/02_业务项目 -name "_project.yaml" | while read yaml; do
  dir=$(dirname "$yaml")
  
  # 统计标准文件夹内文件数
  total=0
  for folder in 数据 成果 文档 参考 代码; do
    if [ -d "$dir/$folder" ]; then
      count=$(find "$dir/$folder" -type f ! -name ".*" 2>/dev/null | wc -l | tr -d ' ')
      total=$((total + count))
    fi
  done
  
  if [ "$total" -eq 0 ]; then
    rel=$(echo "$dir" | sed 's|/Users/tianli/Downloads/zdwp/02_业务项目/||')
    echo "❌ 空: $rel"
  fi
done
```

## 修复策略

### 策略 A：删除空项目
如果项目目录确实没有任何有价值的文件，删除 `_project.yaml` 使其不再出现在 Dashboard 中。

```bash
rm "$dir/_project.yaml"
```

### 策略 B：整理根目录文件
如果项目根目录有文件但没放到标准文件夹：

```bash
# 移动文档类文件到 文档/
mkdir -p "$dir/文档"
find "$dir" -maxdepth 1 -type f \( -name "*.docx" -o -name "*.doc" -o -name "*.pdf" -o -name "*.md" \) ! -name "_*.yaml" -exec mv {} "$dir/文档/" \;
```

### 策略 C：整理非标准文件夹
如果项目有非标准文件夹（如 1_招标方文件、相关资料等）：

| 原文件夹 | 目标 |
|----------|------|
| *招标* | → 参考/ |
| *投标* | → 文档/ |
| *合同* | → 文档/ |
| *资料* | → 参考/ |
| *数据* | → 数据/ |

## 验证标准

修复后，每个保留的项目必须满足：
1. 点击卡片后，至少有 1 个标准文件夹有内容
2. 或者有子项目可展开

## 同步数据

修复后执行：

```bash
cd /Users/tianli/Downloads/zdwp/.oa && pnpm run sync
```

## 输出要求

完成后输出报告：

```
=== 项目完整性检查报告 ===
检查时间: YYYY-MM-DD HH:MM
总项目数: XX
空项目数: XX
已删除: XX
已修复: XX

删除列表:
- 项目A
- 项目B

修复列表:
- 项目C: 根目录文件→文档/
- 项目D: 相关资料→参考/
```

## 注意事项

1. 删除前确认目录确实没有有价值的文件
2. 不要删除主项目（14个领域），只处理子项目
3. 修改后运行 sync 更新 Dashboard 数据
4. 优先保留而不是删除，能整理就整理
