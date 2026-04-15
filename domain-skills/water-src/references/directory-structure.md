# 2025水源地评估目录结构

## 水库目录结构（盂溪水库、西岙水库相同）

| 编号 | 目录名 |
|------|--------|
| 01 | 供水保障程度 |
| 02 | 应急备用水源地建设 |
| 03 | 水量调度管理 |
| 04 | 取输水设施运行 |
| 05 | 取水口水质 |
| 06 | 保护区划分 |
| 07 | 封闭管理及界标设立 |
| 08 | 一级保护区综合治理 |
| 09 | 二级保护区综合治理 |
| 10 | 准保护区综合治理 |
| 11 | 含磷洗涤剂农药化肥使用 |
| 12 | 保护区交通设施管理 |
| 13 | 保护区生态建设 |
| 14 | 监测预警与生态监测 |
| 15 | 水量监测 |
| 16 | 视频监控 |
| 17 | 管理规范程度 |
| 18 | 应急能力保障 |
| 19 | 信息化管理 |
| 20 | 资金保障 |

## 文件命名规则

- 格式：`编号 年份_水库_文件描述.扩展名`
- 示例：`1-1 2025_盂溪_来水量保证率计算说明.pdf`
- 共用文件：`18-3-1 2025_盂溪西岙_防洪和干旱应急演练记录.docx`

## 源文件目录

- `00 源文件/` - 存放原始文档和盖章文件
- `00 源文件/盖章1205/` - 2025年12月5日的盖章文件

## DOCX转PDF方法

```bash
# Raycast脚本（Finder选中文件使用）
# [已废弃] docx_to_pdf.sh

# 命令行用 Microsoft Word AppleScript 转换
osascript -e '
tell application "Microsoft Word"
    activate
    open POSIX file "/path/to/file.docx"
    save as active document file name "/path/to/file.pdf" file format format PDF
    close active window saving no
end tell
'
```

## 分发规则

- DOCX 文件需先转为 PDF 再分发到目标目录
- 源文件保留在 `00 源文件/`
