# Skill 候选池

从 /recap 分析中自动识别的重复工作模式。出现 3 次以上建议正式创建 skill。

---

<!-- 候选记录会自动追加在下方 -->

## VPS 服务部署
- 发现时间: 2026-04-12
- 出现次数: 5
- 状态: done（已创建 /deploy command）
- 模式描述: 创建 systemd service + Nginx reverse proxy + CF DNS/Origin Rule + deploy.sh 的完整流程。本次对 website 和之前 dashboard 都执行了类似流程。
- 涉及项目: website, repo-dashboard
- 潜在 skill 类型: command

## 开源项目分析 → 借鉴落地
- 发现时间: 2026-04-12
- 出现次数: 1
- 模式描述: 研究开源项目 → 写分析文档（审计/对比/机会）→ 优先级排序 → 逐项落地。本次对 Hermes Agent 执行了此流程。
- 涉及项目: analysis-hermes-vs-mine
- 潜在 skill 类型: command

## 站群深度体检 (3 Explore 并发诊断 → 用户拍板 → 修复)
- 发现时间: 2026-04-20
- 出现次数: 1
- 状态: active
- 模式描述: 用户说"X 乱了"→ 3 个 Explore agent 分维度并发深挖（导航 × 重复 × IA/隐藏）→ 整合 plan 文件 → AskUserQuestion 集中拍板 3 类（语义/范围/优先级）→ 自主执行修复链 + 安全 audit + push + deploy + 验证。
- 涉及项目: stations
- 潜在 skill 类型: command（/site-audit）

## 站群 SSOT 同步链 (catalog → navbar → website-navbar → audit → refresh)
- 发现时间: 2026-04-21
- 出现次数: 1
- 状态: active
- 模式描述: 改 navbar.yaml / sites/*.yaml / services.ts 任一后必须按固定顺序跑 5 步：menus.py build-catalog -w → render-navbar -w → build-website-navbar -w → audit → navbar_refresh.sh。颠倒顺序 audit 报 drift。
- 涉及项目: stations (devtools + tools/configs)
- 潜在 skill 类型: command（/menus-sync 一键链）

## VPS 配置 SSOT 抽取 (vps_config.sh 模式)
- 发现时间: 2026-04-21
- 出现次数: 1
- 状态: active
- 模式描述: 找出硬编码（grep IP/路径） → 设计 SSOT 文件（防重复 source 哨兵 + ${VAR:-default}） → N 个消费者改 source SSOT → smoke test override 机制。本次抽 vps_config.sh，9 个 deploy.sh 接入。
- 涉及项目: stations (devtools)
- 潜在 skill 类型: skill（/extract-ssot &lt;pattern&gt;）

## xlsx 多 sheet 匹配回填（源按分类分 sheet → 目标跨类汇总）
- 发现时间: 2026-04-21
- 出现次数: 1
- 状态: active
- 模式描述: 源数据按行业/类别分 sheet 列位不同，目标下发模板跨类汇总；按业务主键（信用代码 + 名称）匹配回填 N 列。坑：Excel 18 位代码存成 float 需 by_name 回退 / 多 sheet 同单位必须 merge 而非覆盖 / 匹配率 <100% 必列 unmatched 清单。本轮台州 1976 行 100% 命中。
- 涉及项目: 04 水预算单位名录整理
- 潜在 skill 类型: skill（项目内 `.claude/skills/fill-water-budget/`，已创建）；后续若跨省用可考虑抽到全局 `/xlsx-fill` 通用骨架

## AI batch 翻译 markdown 双轨（frontmatter *_en + .en.md sibling）
- 发现时间: 2026-05-06
- 出现次数: 1
- 状态: active
- 模式描述: 中文站国际化时翻 N 篇 .md：扫范围 + 词典提取（jieba/N-gram + menus.yaml SSOT 锁高置信）+ AskUserQuestion 抽检关键术语（机构/项目/头衔）+ 起 3-4 agent 并发翻（每 8-12 篇）+ 双产物（原 .md frontmatter 加 *_en sibling 字段 + 同目录 .en.md 完整英文）+ build size sentinel + puppeteer 实测 + commit。本轮 32 篇 / 64 文件 / 25-30 min/agent。无 ANTHROPIC_API_KEY 时直接用 Claude subagent 翻（agent 本身就是 Claude）。
- 涉及项目: stations/website
- 潜在 skill 类型: skill（/translate-content <range> <glossary>），≥3 次再正式建

## next.js 15 standalone 常见坑诊断（recursiveDelete / cross-app Link / RSC fail / chunk hash mismatch）
- 发现时间: 2026-05-06
- 出现次数: 1
- 状态: active
- 模式描述: standalone + outputFileTracingRoot + 外部 symlink 配置组合，触发 4 类已知坑：(1) cleanDistDir follow symlink 删 target；(2) cross-app Link 自动 prefetch RSC fail；(3) middleware self-fetch SSL EPROTO；(4) build hash mismatch CF 缓存 stale。诊断脚本扫 4 类，给修复建议（prebuild rm / Link→a / nextUrl.clone+protocol=http / CF purge）。
- 涉及项目: stations/website
- 潜在 skill 类型: skill（/diagnose-next-standalone），≥3 次再正式建
