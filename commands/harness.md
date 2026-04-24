根据项目性质和当前阶段，生成或升级 Claude Code 配置脚手架。

## 用法

```
/harness                    → 当前项目
/harness ~/Dev/new-project  → 指定项目
/harness --check            → 只诊断，不修改
```

$ARGUMENTS 为目标路径（默认 `.`）。

---

## Step 1: 项目诊断

扫描项目，判定两个关键属性：

### 1a. 项目类型

| 类型 | 判定依据 |
|------|---------|
| `streamlit` | 有 `app.py` + `streamlit` in requirements |
| `tauri` | 有 `src-tauri/` |
| `cli` | 有 `if __name__` 入口 + argparse/click，无 web 框架 |
| `library` | 有 `setup.py` / `pyproject.toml`，无入口脚本 |
| `scripts` | 多个独立脚本，无统一入口 |
| `docs` | 纯 Markdown，无代码 |
| `monorepo` | 多个子项目（apps/packages 目录） |
| `webapp` | Flask/FastAPI/Express 等 web 框架 |

### 1b. 项目阶段

| 阶段 | 判定依据 | 配置预期 |
|------|---------|---------|
| **seed** | 无 CLAUDE.md，<5 个源文件 | 最小配置：CLAUDE.md |
| **growing** | 有 CLAUDE.md 但不完整，5-50 个源文件 | 补全 CLAUDE.md + README + .gitignore |
| **established** | 有 CLAUDE.md + README，>50 个源文件或有部署 | 完整配置 + hooks + 项目专用 rules |
| **mature** | 完整配置，多贡献者或复杂工作流 | 优化：skills 绑定、agent 定义、验证闭环 |

输出诊断结果：

```
📋 项目诊断
类型：streamlit
阶段：growing → established
路径：~/Dev/stations/web-stack/services/hydro-rainfall
源文件：37 个 Python, 2 个 YAML
部署：VPS (hydro-rainfall.tianlizeng.cloud)
现有配置：CLAUDE.md ✓  README.md ✓  README_CN.md ✗  .gitignore ✓  hooks ✗
```

如果 `--check`，到这里停止。

---

## Step 2: 生成配置方案

根据诊断结果，生成需要创建/升级的配置清单。不同阶段的配置层级：

### seed → 最小可用

| 配置 | 内容 |
|------|------|
| **CLAUDE.md** | 项目概述、Quick Reference 表、常用命令、项目结构（tree depth 2） |

### growing → 补全基础

包含 seed 全部，加：

| 配置 | 内容 |
|------|------|
| **README.md** | 按 `/audit` 的 readme_template 规则生成（app/infra/content/minimal） |
| **README_CN.md** | README.md 的中文翻译 |
| **.gitignore** | 按语言补全 baseline 条目（复用 `repo-standards.json → common.gitignore_baseline`） |
| **LICENSE** | MIT（copyright holder = tianli） |

### established → 工程化

包含 growing 全部，加：

| 配置 | 内容 |
|------|------|
| **CLAUDE.md 升级** | 添加开发注意事项、技术栈、数据源说明 |
| **hooks** | 根据项目类型推荐 PostToolUse hooks |
| **rules/** | 项目专用规则（如有 Word 文档处理 → 写作规范 rule） |

推荐的 hooks 策略：

| 项目类型 | 推荐 hooks |
|---------|-----------|
| streamlit / webapp | Bash 后自动检查端口冲突 |
| cli / library | Edit 后检查 import 完整性 |
| scripts | Bash 后检查退出码 |
| 有测试的项目 | Edit 后提示运行相关测试 |

### mature → 优化闭环

包含 established 全部，加：

| 配置 | 内容 |
|------|------|
| **skills 绑定** | 检查 `~/Dev/tools/cc-configs/skills/` 是否有适用的 skill，建议绑定 |
| **agent 定义** | 如果项目有复杂多步工作流，建议创建专用 agent |
| **验证命令** | 在 CLAUDE.md 中添加 done-conditions 和验证命令 |

---

## Step 3: 逐项生成

对每个配置项：

1. **已存在且达标** → 跳过，标记 ✓
2. **已存在但不完整** → 显示 diff 预览，等待审批
3. **不存在** → 生成完整内容，等待审批

### CLAUDE.md 生成规则

读项目代码后生成，风格参考已有项目的 CLAUDE.md（中文）：

```markdown
# {项目名}

{一句话描述}

## Quick Reference

| 项目 | 路径/值 |
|------|---------|
| 入口 | `{main entry}` |
| 部署 | {deploy info if any} |
| 测试 | `{test command}` |

## 常用命令

\```bash
# {最常用的命令}
{command}
\```

## 项目结构

\```
{tree output, depth 2}
\```

## 开发注意事项

- {从代码中提取的关键约束}
```

### README.md 生成规则

复用 `/audit` 的 readme_template 体系。金标准参考：`~/Dev/stations/dockit/README.md`。

必须包含：
- 语言切换：`**English** | [中文](README_CN.md)`
- for-the-badge 徽章
- 分隔线 + 截图占位
- 功能表格
- 安装 / 快速上手

### README_CN.md 生成规则

镜像 README.md 结构，翻译为中文。保持代码块、URL、技术术语不变。

---

## Step 4: 审批与应用

逐项展示生成结果，等待用户审批：

```
[1/4] CLAUDE.md (新建)
{preview first 20 lines}
→ 审批? [Y/n/edit]

[2/4] README.md (新建)
{preview first 20 lines}
→ 审批? [Y/n/edit]

[3/4] README_CN.md (新建)
→ 审批? [Y/n/edit]

[4/4] .gitignore (补全 3 条)
+ __pycache__/
+ .env
+ *.pyc
→ 审批? [Y/n/edit]
```

---

## Step 5: 汇总

```
🏗️ 脚手架完成

项目：hydro-rainfall (streamlit, established)
新建：CLAUDE.md, README_CN.md
升级：.gitignore (+3 条)
跳过：README.md (已达标), LICENSE (已存在)
建议：下次可添加 hooks (项目已有部署)

提交? [Y/n]
```

如果用户确认，调用 `/ship` 提交。

---

## 规则

- CLAUDE.md 用中文，README.md 用英文，README_CN.md 用中文
- 不覆盖已有内容——只补全或升级
- 每个配置项都要审批，不批量强推
- 不生成用不到的配置（seed 阶段不推 hooks，没部署不推 deploy 相关）
- 复用已有命令的逻辑：.gitignore baseline 来自 repo-standards.json，README 模板来自 /audit 体系
- 阶段判定要保守——宁可低估，让用户决定是否升级
