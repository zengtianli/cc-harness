# cc-harness

[English](README.md) | **中文**

个人 Claude Code 工具套件 — 配置审计工具 + 斜杠命令 + 自动触发技能 + Agent 定义，全部用代码管理在一个 repo 里，symlink 到 `~/.claude/`。

[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge)](https://python.org)

---

![cc-harness 演示](docs/screenshots/demo.png)

---

## 这是什么？

这个 repo 是定制 Claude Code 行为的**唯一真相源**：

| 层 | 内容 | 位置 |
|----|------|------|
| **审计工具** | 六维度配置质量扫描 | `harness.py` + `analyzers/` |
| **Commands** | 17 个斜杠命令（`/ship`、`/deploy`、`/groom`……） | `commands/` |
| **Skills** | 13 个自动触发的上下文注入 | `skills/` |
| **Agents** | 2 个专用 Agent 定义 | `agents/` |
| **注册表** | Skill → 项目的映射关系 | `harness.yaml` |

`install.sh` 将 `commands/`、`skills/`、`agents/`、`harness.yaml` symlink 到 `~/.claude/`，Claude Code 在所有项目中自动加载。

## 安装

```bash
git clone https://github.com/zengtianli/cc-harness.git ~/Dev/cc-harness
cd ~/Dev/cc-harness
bash install.sh
```

创建的 symlink：

```
~/.claude/commands     → ~/Dev/cc-harness/commands
~/.claude/skills       → ~/Dev/cc-harness/skills
~/.claude/agents       → ~/Dev/cc-harness/agents
~/.claude/harness.yaml → ~/Dev/cc-harness/harness.yaml
```

更新只需 `git pull`，symlink 保持同步。

---

## Commands 命令手册

在 Claude Code 中输入 `/命令名 [参数]` 调用。每个 command 封装了一套可重复的工作流。

### 交付与部署

| 命令 | 用法 | 说明 |
|------|------|------|
| `/ship` | `/ship`、`/ship all`、`/ship dockit hydro-risk` | 提交 + 推送一个或多个 repo。自动生成 conventional commit 消息。`all` 模式从 `repo-map.json` 发现所有有变更的 repo。 |
| `/deploy` | `/deploy`、`/deploy --backend-only` | 部署当前项目到 VPS。检测 `deploy.sh`，需要时先 build 前端，部署后 curl 验证。 |
| `/dashboard` | `/dashboard`、`/dashboard --scan-only` | 用 LLM 分析 Claude Code 会话，然后部署 dashboard 应用。`--scan-only` 只扫描不部署，`--force` 忽略缓存。 |

### Repo 管理

| 命令 | 用法 | 说明 |
|------|------|------|
| `/groom` | `/groom`、`/groom hydro-risk learn`、`/groom --check` | 完整 repo 维护流水线：pull → 审计（LICENSE、.gitignore、README、CLAUDE.md、GitHub metadata）→ 修复 → 审批 → push。按修复类型分批审批，高效。 |
| `/promote` | `/promote`、`/promote all --check` | 轻量 GitHub metadata 审计：description、topics、homepage、截图。是 `/groom` 的子集，专注公开可见性。 |
| `/repo-map` | `/repo-map scan`、`/repo-map sync`、`/repo-map show` | 管理 GitHub ↔ 本地路径注册表（`repo-map.json`）。`scan` 扫描磁盘发现 repo，`sync` 同步到下游消费者，`show` 打印表格。 |

### 基础设施

| 命令 | 用法 | 说明 |
|------|------|------|
| `/vps-status` | `/vps-status`、`/vps-status nginx` | SSH 到 VPS，展示运行中的服务、端口、磁盘、内存、Docker 容器。指定服务名会额外显示最近日志。 |
| `/cf-dns` | `/cf-dns list`、`/cf-dns add status`、`/cf-dns delete old-sub` | 通过 API 管理 Cloudflare DNS 记录。`add` 一步创建 A 记录 + Origin Rule。 |

### 文档处理

| 命令 | 用法 | 说明 |
|------|------|------|
| `/md2word` | `/md2word path/to/file.md` | 完整 MD/DOCX → Word 流水线：套模板样式 → 文本修复（标点、单位）→ 图名居中。4 步自动化。 |
| `/review-docx` | `/review-docx path/to/report.docx` | 审阅 Word 文档：提取文本，分析禁用词/错误标点/缺失引用，写入修订批注到文件中。 |

### 水利项目工具

| 命令 | 用法 | 说明 |
|------|------|------|
| `/build-hydro` | `/build-hydro capacity`、`/build-hydro all` | 构建 hydro 桌面应用的 Tauri 安装包。报告产物路径和大小。 |
| `/migrate-hydro` | `/migrate-hydro capacity` | 将 hydro Streamlit 应用的计算逻辑移植到对应 Tauri 桌面应用。读 Python → 写 Rust + React。 |

### 会话与工作流

| 命令 | 用法 | 说明 |
|------|------|------|
| `/recap` | `/recap` | 会话结束复盘：回顾对话、提取经验、更新 memory/skills/commands/CLAUDE.md，生成 `session-retro-{date}.md`。 |
| `/context` | `/context monitor`、`/context health` | 监控 Claude Code 会话健康——token 消耗、工具调用分布、上下文膨胀检测、快照保存/恢复。 |
| `/tidy` | `/tidy`、`/tidy ~/Work/project/docs` | 深度清理目录：发现垃圾文件、版本链、散乱文件。按目录分组输出表格，确认后才执行。 |
| `/health` | `/health`、`/health --llm` | 运行 ZDWP 工作区健康检查。报告 Git 泄漏、版本冗余、散乱文件，附修复建议。 |

### 规范

| 命令 | 用法 | 说明 |
|------|------|------|
| `/frontend` | （自动引用） | 前端开发规范：信息密度、紧凑布局、可操作数据、Streamlit 约定。通常不直接调用，做 UI 时自动参考。 |

---

## Skills 技能手册

Skills 是自动触发的上下文注入。Claude Code 检测到匹配场景时自动加载技能知识，无需手动调用。

### 全局技能（所有项目生效）

| 技能 | 触发场景 | 提供的知识 |
|------|---------|-----------|
| **context** | 在 ZDWP 水利公司项目中工作 | 集团架构、县市列表、数据字段规范、交付标准 |
| **structure** | 整理文件、创建新项目 | 目录命名规则、文件分类规则、自动整理逻辑 |
| **plan-first** | 批量操作、破坏性动作 | 强制"先写方案再操作"纪律——展示表格，等待审批 |
| **quarto** | 将 DOCX 转换为 Quarto 项目 | Quarto 编译工作流、模板结构、图表处理 |

### 项目专用技能

| 技能 | 绑定项目 | 提供的知识 |
|------|---------|-----------|
| **risk-map** | ~/Work/risk-map | 洪水风险图数据处理、QGIS 空间工作流、Excel 模板填充 |
| **eco-flow** | ~/Work/eco-flow | 生态流量计算（Tennant 法）、水库筛选、保障方案 |
| **zdys** | ~/Work/zdys | 浙东引水运行态势、调度模型、灌溉需水计算 |
| **water-src** | ~/Work/water-src | 饮用水水源地安全保障评估方法 |
| **water-quality** | （独立） | 千岛湖引水分质供水管理 |
| **resources** | risk-map, eco-flow, zdys, water-src | 共享资源目录：水库数据、GIS 底图、行政边界、水资源年报、行业规范 |

### 工具技能

| 技能 | 触发场景 | 提供的知识 |
|------|---------|-----------|
| **harness** | 检查/同步技能配置 | 技能分发注册表、跨项目同步逻辑 |
| **repo-manage** | 管理 GitHub repo | 审计/截图/推广 SOP |
| **restart** | 终端重启后恢复会话 | 会话恢复指令 |

---

## Agents 手册

Agents 是用于复杂多步任务的专用自治工作者。

| Agent | 用途 |
|-------|------|
| **bid-chapter-writer** | 按公司模板和格式标准编写标书章节 |
| **project-content-checker** | 按需求清单审计项目交付物完整性 |

---

## 审计工具

审计工具（`harness.py`）扫描任意项目的 Claude Code 配置，生成六维度评分报告：

| 维度 | 检查内容 |
|------|---------|
| **D1 Context** | CLAUDE.md 质量、Token 预算、重复规则、凭证泄露 |
| **D2 Hooks** | PostToolUse 覆盖、schema 有效性、输出截断、错误上报 |
| **D3 Agents** | Skill 数量、重叠、描述质量、frontmatter |
| **D4 验证** | 完成条件、build/test 命令、CI 集成 |
| **D5 会话** | Compact Instructions、HANDOFF.md、上下文预算 |
| **D6 结构** | 孤立文件、引用链、命名规范、gitignore |

### 项目级别检测

自动识别项目规模，校准检查预期：

| 级别 | 特征 | 预期配置 |
|------|------|---------|
| Simple | <500 源文件、1 贡献者、无 CI | 仅需 CLAUDE.md |
| Standard | 500-5K 文件、小团队或有 CI | CLAUDE.md + rules + skills + hooks |
| Complex | >5K 文件、多贡献者、活跃 CI | 完整六层配置 |

### 用法

```bash
# 完整审计
python3 harness.py /path/to/project

# JSON 输出
python3 harness.py /path/to/project --json

# 仅安全扫描
python3 harness.py /path/to/project --security-only

# 自定义 Claude 目录
python3 harness.py /path/to/project --claude-home ~/.claude
```

### 安全扫描

内置扫描器检查 skills 的 6 类风险：

1. **Prompt injection** — 指令覆盖、角色劫持
2. **数据外泄** — 携带密钥的 HTTP POST、base64 编码
3. **破坏性命令** — rm -rf /、force-push main、chmod 777
4. **硬编码凭证** — api_key/secret_key 与长字符串
5. **混淆** — eval $()、base64 解码管道到 shell
6. **安全绕过** — bypass/disable safety/rules/hooks

---

## Skill 分发机制（harness.yaml）

`harness.yaml` 是技能到项目的映射注册表：

```yaml
global_skills:        # 全局生效
  - context
  - structure
  - plan-first
  - quarto

projects:             # 项目专用技能包
  risk-map:
    path: ~/Work/risk-map
    skills: [risk-map, resources, plan-first]
  eco-flow:
    path: ~/Work/eco-flow
    skills: [eco-flow, resources, plan-first]
  # ...

standalone:           # 单项目技能
  - water-quality
```

`/harness` 技能负责将注册表同步到各项目的实际配置。

---

## 项目结构

```
cc-harness/
├── harness.py          # CLI 入口——级别检测 + 审计调度
├── harness.yaml        # Skill → 项目分发注册表
├── install.sh          # Symlink 安装脚本
├── analyzers/          # 六维度审计逻辑
├── collectors/         # 数据采集器（metrics/hooks/config/skills）
├── security/           # 安全扫描器（6 类风险）
├── reporters/          # 输出格式化（scorecard + markdown）
├── commands/           # 17 个斜杠命令 → ~/.claude/commands
├── skills/             # 13 个自动触发技能 → ~/.claude/skills
├── agents/             # 2 个 Agent 定义 → ~/.claude/agents
├── tests/              # pytest 测试套件
└── docs/               # 截图、文档
```

## 测试

```bash
python3 -m pytest tests/ -v
```

## 许可证

MIT
