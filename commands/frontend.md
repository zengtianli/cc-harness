# 前端开发规范

构建 Web 前端（Streamlit 或其他）时，遵守以下原则：

## 信息密度
- **一屏看完**：关键信息必须不滚动就能看到，不要让用户点来点去
- **减少 tab/页面数量**：能合并就合并，宁可一个长页面也不要 6 个空页面
- **表格无滚动条**：小数据量用 `st.table()`（静态渲染），大数据量用 `st.dataframe(height=行数*35+38)`
- **紧凑排列**：减少空白、padding、间距

## 样式
- **亮色主题**：白色/浅灰背景，深色文字。不要暗色主题
- **字号紧凑**：metric 值 1.4rem，标签 0.8rem，标题 1.6rem，副标题 1.1rem
- **不要截断**：所有文字必须完整显示，宁可缩小字号也不要省略号
- Streamlit 用 `st.markdown` 注入自定义 CSS 修正默认的臃肿间距

## 可操作性
- **数据不只是看的，要能操作**：VPS 服务要能 start/stop/restart，不是只显示状态
- 操作按钮紧跟数据行，不要单独放到其他页面
- 操作后立即刷新状态（`st.rerun()`）

## Streamlit 具体规范
- `layout="wide"` 必开
- `initial_sidebar_state="collapsed"` 减少干扰
- 用 `st.columns()` 做多列布局，充分利用宽屏
- metric 卡片用自定义 CSS 压缩间距
- 用 `st.markdown()` 做紧凑列表，比 `st.container(border=True)` 省空间
