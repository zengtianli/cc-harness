把一个 hydro-* Streamlit 站迁成 `~/Dev/stations/web-stack/apps/<name>-web/` Next.js 骨架 + `~/Dev/<name>/api.py` FastAPI wrapper。**不碰原 app.py 和 src/**。

## $ARGUMENTS

```
<repo>                   # 必填，如 hydro-capacity
--dry-run                # 只打印不写文件
--force                  # 覆盖已有骨架
```

## 调用

```bash
python3 ~/Dev/devtools/lib/tools/stack_migrate_hydro.py $ARGUMENTS
```

## 产物

- `~/Dev/stations/web-stack/apps/<repo>-web/` — 完整 Next.js 骨架（package.json / next.config.mjs / tsconfig / tailwind / app/layout.tsx / app/page.tsx 用 `XlsxComputeForm` 模板）
- `~/Dev/<repo>/api.py` — FastAPI wrapper（`/api/health` + `/api/meta` + `/api/compute` 501 占位）
- `~/Dev/<repo>/pyproject.toml` — 已加 `fastapi` + `uvicorn` 依赖

## 后续手工动作

1. `cd ~/Dev/<repo> && uv add python-multipart`（上传需要）
2. `cd ~/Dev/<repo> && uv sync`
3. 把 `api.py::/api/compute` 的 501 占位替换成真实计算（参考 `~/Dev/hydro-reservoir/api.py::_run_reservoir()`）
4. `cd ~/Dev/stations/web-stack && pnpm install`
5. 本地联调：`cd ~/Dev/<repo> && uv run uvicorn api:app --port <api_port>` + `cd ~/Dev/stations/web-stack && pnpm --filter <repo>-web dev`

## 端口规则

脚本自动读 `~/Dev/stations/website/lib/services.ts`：
- `streamlit_port` — 原 Streamlit 端口
- `api_port` = streamlit_port + 100
- `web_port` = streamlit_port - 5400

## 相关

- `/stack-classify` — 全项目分类清单，判断哪些该迁
- `reference_webstack.md` — monorepo 速查
