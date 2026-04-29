---
name: hsbc-wpl
description: HSBC WPL（滙財組合貸款）月结单 PDF 一键分析 — 解密 + 解析 + 反推有效年化 + 推断 spread vs 1M HIBOR
---

# /hsbc-wpl

HSBC `INVSTM0019` 投资 + WPL 综合结单分析。链路：

```
加密 PDF → pdf-decrypt（密码） → pdftotext → 抽字段 → 算有效年化 → HKAB HIBOR → 推 spread → 报告
```

## 用法

```bash
/hsbc-wpl <pdf-path>                  # 自动：当前 HIBOR
/hsbc-wpl <pdf-path> --hibor 2.65     # 手填期间均值（更精确）
/hsbc-wpl <pdf-path> --no-hibor       # 离线，只算有效年化
/hsbc-wpl <pdf-path> --json           # JSON 输出
```

## 执行

```bash
PDF="$1"
shift
[ "$PDF" = "" ] && { echo "usage: /hsbc-wpl <pdf>"; exit 2; }

# 1. 解密（如已有 -decrypted.pdf 跳过）
DEC="${PDF%.pdf}-decrypted.pdf"
if [ ! -f "$DEC" ]; then
  python3 ~/.claude/skills/pdf-decrypt/scripts/decrypt.py "$PDF" --issuer hsbc-hk
fi

# 2. 分析
python3 ~/Dev/tools/cc-configs/skills/hsbc-wpl/scripts/analyze.py "$DEC" "$@"
```

## 何时跑

- 收到 HSBC HK 月结单邮件，PDF 加密
- 想知道"这个月利息合不合理 / spread 漂没漂"
- 调研 1M HIBOR + Premier 议价空间
- 多月对比时（手工跑两遍 `--json`，diff 输出）

## 不做（v0.x 计划）

- HIBOR 历史自动抓（HKAB 没 API，要手填 `--hibor`）
- 多月 diff（手 diff JSON 输出）
- 告警（margin ratio 阈值监控）

## 相关

- `/pdf-decrypt`（解密前置）
- `docs/hsbc.md`（HSBC 账户全景）
- `docs/statements/`（个人结单存档）
