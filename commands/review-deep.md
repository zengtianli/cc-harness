---
description: 4维度LLM深度审阅（完整性/结构性/立场措辞/数据一致性），输出Word批注
---

用户提供了一个文件路径: $ARGUMENTS

请对 Word 文档进行4维度深度审阅，以批注形式标出问题。

## 工具位置

- 核心脚本：`/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/review_deep.py`
- 规则目录：`~/Dev/cc-configs/rules/review-deep/`

## 并行策略

当审阅多个文档时：
- 为每个文档生成独立子代理（Agent tool），并行执行 4 维度审阅
- 每个子代理独立完成审阅并返回结果
- 主线程汇总所有审阅意见，输出统一报告
- 单个文档时直接执行，不生成子代理

## 流程

### 1. 确定输入

- 如果 `$ARGUMENTS` 为空，问用户要文件路径
- 确认文件存在且为 `.docx`
- 问用户选择规则，可用 `--list-rules` 查看可用规则

### 2. 确认参数

与用户确认：
- **规则**：必选，用 `--list-rules` 列出后让用户选
- **维度**：默认全部，可指定 `--dim completeness structure tone consistency`
- **模型**：默认 haiku（快速），重要文档建议 sonnet

### 3. 执行审阅

```bash
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/review_deep.py \
  "<输入文件>" \
  --rules <规则名> \
  --model haiku
```

可选参数：
- `--dim completeness` — 只检查完整性
- `--dim tone consistency` — 只检查立场措辞和数据一致性
- `--dry-run` — 只输出问题清单，不写入批注
- `-o <输出路径>` — 指定输出文件路径

### 4. 完成

- 用 `open` 打开审阅后的 docx
- 报告：按维度汇总问题数量

## 规则文件说明

规则文件位于 `~/Dev/cc-configs/rules/review-deep/`，YAML 格式：

```yaml
name: 文档类型名称
description: 一句话描述
chapter_pattern: "章节正则"
dimensions:
  completeness:
    name: 完整性
    rules: [...]
  structure:
    name: 结构性
    rules: [...]
  tone:
    name: 立场措辞
    rules: [...]
  consistency:
    name: 数据一致性
    rules: [...]
```

新增文档类型只需在规则目录下添加 `.yaml` 文件。
