审计 repo 完整性，基于 repo-standards.json 检查文件和 GitHub metadata。

## 范围

从 $ARGUMENTS 确定目标（同 /pull）：
- 无参数 → 当前目录
- `<name> [name2 ...]` → repo-map.json 查路径
- `all` → 所有 non-ignored repo
- `--category <cat>` → 按分类过滤（hydro/tools/infra/knowledge/personal/work）

## 并行策略

当审计多个目标时（如 `/audit ~/Dev/tools/doctools ~/Dev/devtools ~/Dev/tools/mactools`）：
- 为每个目标生成独立子代理（Agent tool），并行执行审计
- 每个子代理独立完成单个 repo 的审计并返回结果
- 主线程汇总所有结果，输出统一报告
- 单个目标时直接执行，不生成子代理

## 检查项

### 文件存在性
- LICENSE（MIT，copyright holder = tianli）
- .gitignore（包含 `repo-standards.json → common.gitignore_baseline` 所有条目）
- README.md
- README_CN.md（如果 `category.bilingual = true`）
- CLAUDE.md

### README 质量
按 repo 的 `readme_template` 检查结构：
- **app**: language selector, badges, separator, screenshot, feature table, install, quick start
- **infra**: title, badges, what-it-does, setup, usage
- **content**: title, badges, contents overview
- **minimal**: title, overview

### GitHub metadata
```bash
gh repo view zengtianli/<name> --json description,repositoryTopics,homepageUrl
```
- description 非空
- topics >= 3
- homepage 已设（如果有 VPS 部署或 Streamlit）

## 参考

- `~/Dev/configs/repo-standards.json` — 完整性标准
- `python3 ~/Dev/devtools/repo_manager.py audit` — 审计工具

## 输出

```
✅ dockit           — all clear
🔧 hydro-rainfall  — missing LICENSE, missing README_CN.md
🔧 learn           — missing CLAUDE.md, missing LICENSE, 0 topics
⚠️  essays          — missing LICENSE, no description
```

末尾汇总：`N repos checked, X all clear, Y need fixes`
