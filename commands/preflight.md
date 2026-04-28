---
description: 破坏性操作前的全面侦察 — 并行扫描所有相关配置层/产物/依赖，输出「爆炸半径」清单，Claude 逐项确认后才能动手
---

任何涉及**多 repo / 删除 / CF 配置 / MCP 环境 / symlink / 大范围重构**的操作，先跑这个命令。输出一份结构化清单，Claude 必须逐项 acknowledge 后才能进入执行阶段。

## 用法

```
/preflight <任务描述>
```

示例：
```
/preflight 把站群 navbar 模板同步到 6 个消费者 repo
/preflight 清理 VPS /var/www 下的废弃目录
/preflight 修改 CF Access 配置让 auggie 能访问
```

## 执行流程

### Step 1 — 并行侦察（全只读）

同时起以下维度的检查，**不允许串行**：

| 维度 | 检查内容 |
|---|---|
| **配置层** | 所有可能影响该操作的配置文件、env var、hook、settings |
| **部署产物** | 目标文件/目录是否为部署产物、symlink、被其他地方引用 |
| **外部服务** | CF DNS / Origin Rules / Access / nginx vhost / GHA workflow |
| **依赖关系** | 改动会影响哪些下游消费者、repo、站点 |
| **风险文件** | *.css / *.md / symlink — 删改前确认非 SSOT 产物 |
| **代码引用（语义）** | `mcp__auggie__codebase-retrieval` 召回任务涉及的跨文件语义引用 — 补 Grep 字符串扫描的盲区（"看起来像 X 的代码" / "X 的所有调用方" 这类） |

### Step 2 — 输出清单

以下格式输出，**不跳过任何维度**：

```
## Preflight Report: <任务描述>

### 必须先处理（阻断项）
- [ ] ...

### 发现的配置层（逐层列出）
- ...

### 爆炸半径（会影响的范围）
- Repos: ...
- 站点/子域: ...
- 外部服务: ...

### 风险项
- ...

### 可以安全跳过
- ...
```

### Step 3 — 用户确认

输出完毕后，**暂停**，等用户说「确认」或「继续」后才进入执行阶段。

## 硬规则

- 侦察阶段 **零写操作** —— 只读、只查、只列
- CF 类问题必须一次性列出所有相关规则（bot protection / security level / managed rules / Access），不允许发现一层改一层
- symlink / *.css / *.md 出现在删除目标时，自动标记为「阻断项」
- MCP 环境问题先验证 MCP 路径，不用 CLI 推断

## 什么时候跑

- 改动涉及 >2 个 repo
- 任何删除操作（文件 / 目录 / CF 规则 / nginx vhost）
- 调试 CF / Auth / MCP / env 类不透明问题
- 大范围 SSOT 同步前（navbar / site-content / menus）

## 不做

- 不自动进入执行阶段
- 不修改任何文件或配置
- 不因为「看起来很简单」就跳过
