# 工具命令快查

## 文档读取

```bash
# Word 文档
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_tools.py <file.docx>

# Excel 文件
/Users/tianli/miniforge3/bin/python3 ~/Dev/hydro-risk/read_xlsx.py <file.xlsx> --list
```

## 格式修复

```bash
# Word 一键格式化
/Users/tianli/miniforge3/bin/python3 ~/Dev/doctools/scripts/document/docx_text_formatter.py <file.docx>

# Word 表格样式
# [已废弃] apply_table_style.py

# Word 标题样式
# [已废弃] apply_heading_styles.py

# Markdown 格式修复
# [已废弃] formatter.py
```

## 格式转换

```bash
# Word -> Markdown
# [已废弃] docx_to_md.sh

# Excel -> CSV
# [已废弃] to_csv.py

# PDF -> Markdown
# [已废弃] pdf_to_md.sh
```

## 比较与分析

```bash
# 比较文件/文件夹
# [已废弃] compare_files_folders.py

# 比较 Excel 数据
# [已废弃] compare_excel_data.py

# 字数统计
# [已废弃] count_chars.py
```

## 快捷常量

```bash
# Python 路径
/Users/tianli/miniforge3/bin/python3

# 脚本根目录（已废弃，各工具已迁移到 ~/Dev/ 下独立仓库）
```
