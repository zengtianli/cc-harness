# Skill 候选池

从 /recap 分析中自动识别的重复工作模式。出现 3 次以上建议正式创建 skill。

---

<!-- 候选记录会自动追加在下方 -->

## VPS 服务部署
- 发现时间: 2026-04-12
- 出现次数: 5 ⚠️ 建议正式创建 skill
- 模式描述: 创建 systemd service + Nginx reverse proxy + CF DNS/Origin Rule + deploy.sh 的完整流程。本次对 website 和之前 dashboard 都执行了类似流程。
- 涉及项目: website, repo-dashboard
- 潜在 skill 类型: command

## 开源项目分析 → 借鉴落地
- 发现时间: 2026-04-12
- 出现次数: 1
- 模式描述: 研究开源项目 → 写分析文档（审计/对比/机会）→ 优先级排序 → 逐项落地。本次对 Hermes Agent 执行了此流程。
- 涉及项目: analysis-hermes-vs-mine
- 潜在 skill 类型: command
