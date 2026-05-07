---
name: cv
description: 简历自动化项目上下文。SSOT (profile.yaml) + Jinja2 模板族 + build.py 渲染管线。当在 ~/Dev/content/resume/ 工作或讨论简历生成、岗位定制简历、应聘登记表时触发。
---

# 简历自动化 · 项目上下文

**项目根**：`~/Dev/content/resume/`

## 数据 SSOT（一改全改的源头）

| 文件 | 角色 | git tracked |
|---|---|---|
| `profile/profile.yaml` | 公开数据（教育/工作/项目/论文/软著/技能/...） | ✅ |
| `profile/profile.private.yaml` | PII（身份证/户籍/家庭/紧急联系人） | ❌ gitignore |
| `profile/profile.schema.yaml` | 公开数据 JSON Schema 定义 | ✅ |
| `profile/profile.private.schema.yaml` | PII Schema 定义 | ✅ |

**铁律**：所有简历产物从 `profile.yaml` 推出。**不要直接编辑生成的 .md/.docx/.pdf**，改在 yaml 里然后重 build。

## 模板族（5 个 Jinja2 模板）

`templates/<name>.md.j2`：
- `full-cn` — 完整中文版（对标 `_archive/历史文件/2025-CV-CN.pdf` 4 页结构）
- `concise-cn` — 1 页精简版
- `full-en` — 英文版（用 `*_en` 字段）
- `role-tailored` — 岗位定制版（按 `meta.yaml` 选 sections + emphasis_tags + include_projects）
- `registration-form` — 应聘登记表 markdown 版

## 渲染管线

`bin/build.py <template> [--out md|docx|pdf|all] [-o OUT_DIR] [--meta FILE]`

```
profile.yaml + template.j2  ──jinja2──→  markdown
                                            ↓ pandoc (--reference-doc)
                                          docx
                                            ↓ docx2pdf (uses MS Word)
                                          pdf
```

**Python**：必须用 `~/Dev/.venv/bin/python`（共享 venv 已含 jinja2/pyyaml/jsonschema/openpyxl/docx2pdf）

## 验证

`bin/validate.py` 跑 JSON Schema 校验（Draft 2020-12）。改 yaml 后必先 validate 0 error 再 build。

## Application 标准结构

```
applications/<公司-岗位>/
├── jd.md             # 岗位描述
├── gap-analysis.md   # 差距分析（可选）
├── meta.yaml         # 控制 role-tailored 模板的渲染
├── resume.{md,docx,pdf}  # 生成产物
├── interview/        # 面试材料
└── supporting/       # 公司 PDF / 资料
```

## 命令

`/cv {build,tailor,validate,new-app,form}` — 5 个子命令，详见 `commands/cv.md`

## 关键 project id（在 profile.yaml 引用用）

数字孪生浙东引水: `zhedong-twin`
梯级水库群多目标联合调度模型: `reservoir-multi-objective`
绍兴市水资源承载力评价: `shaoxing-capacity`
缙云县管网水力分析: `jinyun-pipeline`
小型水库生态流量核定: `reservoir-eco-flow`
钱塘江干流岸线保护与利用规划: `qiantang-shoreline`
洪水风险图编制: `flood-risk-mapping`
嘉兴市水源地优化调整: `jiaxing-water-source`
千岛湖引水分质供水管理: `qiandao-water-supply`
OA Dashboard: `oa-dashboard`
个人总控中心: `cursor-shared`
自动化脚本库: `script-library`
Neovim 配置: `neovim-config`
Execute 工具: `execute-tool`
Zsh 配置: `zsh-config`

## 不做

- 不直接编辑 build/ 下的产物
- 不在 markdown 简历手动加新项目（改 profile.yaml 后重 build）
- 不把 PII 提交到 git
- 不机翻中文为英文（让 `*_en` 字段缺时保留中文 fallback）
