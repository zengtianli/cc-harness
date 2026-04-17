---
description: 脚手架新建一个 ~/Dev/<name> 静态站点项目（projects.yaml + generate.py + deploy.sh）
---

`/site-add <name> [--template stack|changelog|docs]`

生成可直接 `bash deploy.sh` + `/ship-site <name>` 的项目骨架。

## 流程

### 1. 参数解析
- `<name>` 必填，项目目录名（也是默认子域名）
- `--template` 可选：默认 `stack`（参考 cc-evolution/stack 结构）

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
- `~/Dev/stack/` — 项目说明书范式（含 scan_cc_inventory 模式）
- `~/Dev/devtools/lib/templates/nginx-static.conf` — Nginx 模板

### 4. 初始化内容
- 拷贝对应 template 的 generate.py 和 deploy.sh
- 在 deploy.sh 里把域名替换成 `<name>.tianlizeng.cloud`
- 生成最小可用的 projects.yaml（或 template 指定的数据文件）
- 写 CLAUDE.md 说明项目架构（参考 ~/Dev/stack/CLAUDE.md 格式）

### 5. 第一次生成
- 运行 `python3 generate.py` 验证能出 site/index.html

### 6. 提示下一步
告诉用户：
> 下一步：编辑 `~/Dev/<name>/projects.yaml`（或数据源），然后 `/ship-site <name>` 一键上线。

## 规则

- 所有模板路径动态查找（不硬编码 cc-evolution 路径位置）
- 失败时清理已创建的 `~/Dev/<name>/`（或提示用户手工删）
- 不触碰 git init（让用户自己决定）

## 参考

- 下一步：`/ship-site <name>` — 一键部署
- 再下一步：`/launch` (如果存在) — 编排 GitHub + webhook + 部署
