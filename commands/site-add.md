---
description: 脚手架新建一个 ~/Dev/<name> 静态站点项目（projects.yaml + generate.py + deploy.sh）
---

`/site-add <name> [--template stack|changelog|docs|md-docs] [--source <repo-name>]`

生成可直接 `bash deploy.sh` + `/ship-site <name>` 的项目骨架。

## 流程

### 1. 参数解析
- `<name>` 必填，项目目录名（也是默认子域名）
- `--template` 可选：默认 `stack`
  - `stack` — yaml → HTML 卡片站（参考 ~/Dev/stations/stack）
  - `changelog` — yaml → 时间线（参考 cc-evolution）
  - `docs` — 文档站
  - `md-docs` — **跨仓读 markdown + frontmatter → HTML**（参考 ~/Dev/stations/assets）
- `--source <repo>` 仅 `md-docs` 需要：指定源 Markdown 仓（如 `international-assets`），generate.py 将读取 `~/Dev/<source>/docs/*.md`，仅渲染带 frontmatter `public: true` 的文章

### 2. 目录检查
- 确认 `~/Dev/<name>/` 不存在（已存在则报错退出）

### 3. 创建骨架

```
~/Dev/<name>/
├── CLAUDE.md
├── README.md
├── deploy.sh           # 从 ~/Dev/cc-evolution/deploy.sh 拷贝，替换域名
├── generate.py         # 从 stack/generate.py 拷贝或简化版
├── projects.yaml       # 占位（或对应模板）
└── site/
    └── index.html      # 首次 generate 产物
```

关键模板来源：
- `~/Dev/cc-evolution/` — 静态 HTML 生成器范式
- `~/Dev/stations/stack/` — 项目说明书范式（含 scan_cc_inventory 模式）
- `~/Dev/devtools/lib/templates/nginx-static.conf` — Nginx 模板

### 4. 初始化内容
- 拷贝对应 template 的 generate.py 和 deploy.sh
- 在 deploy.sh 里把域名替换成 `<name>.tianlizeng.cloud`
- 生成最小可用的 projects.yaml（或 template 指定的数据文件）
- 写 CLAUDE.md 说明项目架构（参考 ~/Dev/stations/stack/CLAUDE.md 格式）

### 5. 第一次生成
- 运行 `python3 generate.py` 验证能出 site/index.html

### 6. 提示下一步
告诉用户：
> 下一步：编辑 `~/Dev/<name>/projects.yaml`（或数据源），然后 `/ship-site <name>` 一键上线。

## 规则

- 所有模板路径动态查找（不硬编码 cc-evolution 路径位置）
- 失败时清理已创建的 `~/Dev/<name>/`（或提示用户手工删）
- 不触碰 git init（让用户自己决定）

## 模板 · md-docs（跨仓 Markdown → HTML）

**场景**：把某个 private repo 的部分 markdown 发布成公开静态站（assets.tianlizeng.cloud 就是此模式）。

**源仓约定**：
- 位置：`~/Dev/<source>/docs/*.md`
- 过滤：仅 frontmatter `public: true` 的文章被渲染（防 PII 误泄）
- 可选 frontmatter 字段：`title` / `group` / `abstract` / `order`

**脚手架产物**（在 `stack` template 基础上替换 generate.py）：
```
~/Dev/<name>/
├── CLAUDE.md            # 说明源仓 + 分组 key + 加新文章流程
├── README.md
├── deploy.sh            # rsync 到 VPS:/var/www/<name>
├── generate.py          # 从 ~/Dev/stations/assets/generate.py 拷贝，改：
│                        #   DOCS_DIR = Path.home()/"Dev"/"<source>"/"docs"
│                        #   GROUPS = [...按业务场景定义...]
│                        #   SITE_HEADER 面包屑/标题
├── site-navbar.html     # 从 ~/Dev/devtools/lib/templates/site-navbar.html 拷贝
├── site-header.html     # 本站专属
├── site-content.css     # 从 ~/Dev/devtools/lib/templates/ 拷贝
└── site/                # generate.py 产物（index + per-article 独立页）
```

**参考实现**：`~/Dev/stations/assets/generate.py`（2026-04-19 首次落地，已在生产）

**首次 generate 前必做**：在源仓给要公开的 .md 加 frontmatter，最少：
```yaml
---
public: true
title: ...
group: ...      # 对应 GROUPS 的 key
abstract: ...   # 首页卡片摘要
order: 10       # 首页排序
---
```

**依赖**：`uv pip install --system --break-system-packages markdown pyyaml`

## 参考

- 下一步：`/ship-site <name>` — 一键部署（覆盖 nginx + CF DNS/Origin/Access + 首次 rsync）
- 再下一步：`/launch` — 新项目一条龙（/site-add → /groom → /repo-map → /promote → /ship-site → /deploy）
- Playbook：`~/Dev/tools/configs/playbooks/web-scaffold.md`
