#!/usr/bin/env python3
"""
pdf-decrypt — 自动猜密码解 PDF（银行账单 / 投资报告等）

读 ~/.personal_env 的 PDF_ID_* 变量，按已知发行方密码规则生成候选，
逐个用 qpdf 试解。命中则写出 <filename>-decrypted.pdf。

用法:
    decrypt.py <file.pdf> [--out OUTPUT] [--issuer hsbc-hk] [--password PW] [--list]

不带 --issuer 默认全规则跑。--password 用于跳过猜测直接解（也会缓存命中规则到 hit-log）。
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

PERSONAL_ENV = Path.home() / ".personal_env"
HIT_LOG = Path.home() / ".cache/pdf-decrypt/hits.tsv"


@dataclass
class Identity:
    birth_date: str = ""        # YYYY-MM-DD
    surname_py: str = ""        # ZENG
    given_py: str = ""          # TIANLI
    hkid: str = ""              # 香港身份证（不含括号校验位）
    passport_hk: str = ""       # 港澳通行证
    passport_intl: str = ""     # 国际护照
    cn_id: str = ""             # 大陆身份证

    @property
    def birth_year_last2(self) -> str:
        return self.birth_date[2:4] if len(self.birth_date) >= 4 else ""

    @property
    def birth_month(self) -> str:
        return self.birth_date[5:7] if len(self.birth_date) >= 7 else ""

    @property
    def birth_day(self) -> str:
        return self.birth_date[8:10] if len(self.birth_date) >= 10 else ""

    @property
    def birth_month_last_digit(self) -> str:
        return self.birth_month[-1] if self.birth_month else ""

    @property
    def yyyymmdd(self) -> str:
        return self.birth_date.replace("-", "") if self.birth_date else ""

    @property
    def ddmmyyyy(self) -> str:
        if len(self.birth_date) == 10:
            y, m, d = self.birth_date.split("-")
            return d + m + y
        return ""

    def all_ids(self) -> list[tuple[str, str]]:
        """[(label, value), ...] 所有非空证件号"""
        return [
            (k, v.upper())
            for k, v in [
                ("hkid", self.hkid),
                ("passport_hk", self.passport_hk),
                ("passport_intl", self.passport_intl),
                ("cn_id", self.cn_id),
            ]
            if v
        ]


def load_identity() -> Identity:
    """从 ~/.personal_env 读 PDF_ID_* 变量。"""
    i = Identity()
    if not PERSONAL_ENV.exists():
        return i
    pat = re.compile(r'^\s*export\s+(PDF_ID_\w+)\s*=\s*"?([^"\n]*)"?\s*$')
    mapping = {
        "PDF_ID_BIRTH_DATE": "birth_date",
        "PDF_ID_SURNAME_PY": "surname_py",
        "PDF_ID_GIVEN_PY": "given_py",
        "PDF_ID_HKID": "hkid",
        "PDF_ID_PASSPORT_HK": "passport_hk",
        "PDF_ID_PASSPORT_INTL": "passport_intl",
        "PDF_ID_CN_ID": "cn_id",
    }
    for line in PERSONAL_ENV.read_text().splitlines():
        m = pat.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if key in mapping:
            setattr(i, mapping[key], val)
    return i


# ---------- 密码规则库 ----------

# rule: (issuer_id, description, fn(identity, id_value) -> candidate or None)
Rule = Callable[[Identity, str], str | None]


def rule_hsbc_hk(i: Identity, id_value: str) -> str | None:
    """HSBC HK 投资 / WPL 结单：月末位 + 年末2位 + 证件首3位 + 姓末2字母大写"""
    if not (i.birth_month_last_digit and i.birth_year_last2 and i.surname_py):
        return None
    if len(id_value) < 3 or len(i.surname_py) < 2:
        return None
    return (
        i.birth_month_last_digit
        + i.birth_year_last2
        + id_value[:3].upper()
        + i.surname_py[-2:].upper()
    )


def rule_dob_yyyymmdd(i: Identity, id_value: str) -> str | None:
    """通用：YYYYMMDD"""
    return i.yyyymmdd or None


def rule_dob_ddmmyyyy(i: Identity, id_value: str) -> str | None:
    """通用：DDMMYYYY"""
    return i.ddmmyyyy or None


def rule_dob_mmddyy(i: Identity, id_value: str) -> str | None:
    if not (i.birth_month and i.birth_day and i.birth_year_last2):
        return None
    return i.birth_month + i.birth_day + i.birth_year_last2


def rule_id_full(i: Identity, id_value: str) -> str | None:
    """通用：证件号原文"""
    return id_value or None


def rule_id_last4(i: Identity, id_value: str) -> str | None:
    return id_value[-4:] if len(id_value) >= 4 else None


def rule_id_last6(i: Identity, id_value: str) -> str | None:
    return id_value[-6:] if len(id_value) >= 6 else None


def rule_surname_dob(i: Identity, id_value: str) -> str | None:
    """SURNAME + DDMMYYYY (常见某些发行方)"""
    if not (i.surname_py and i.ddmmyyyy):
        return None
    return i.surname_py.upper() + i.ddmmyyyy


RULES: dict[str, tuple[str, Rule]] = {
    "hsbc-hk": ("HSBC HK 投资/WPL/信用卡：月末位+年末2位+证件首3位+姓末2字母", rule_hsbc_hk),
    "dob-yyyymmdd": ("生日 YYYYMMDD（通用）", rule_dob_yyyymmdd),
    "dob-ddmmyyyy": ("生日 DDMMYYYY（英式 / 部分港行）", rule_dob_ddmmyyyy),
    "dob-mmddyy": ("生日 MMDDYY（部分美行）", rule_dob_mmddyy),
    "id-full": ("证件号原文", rule_id_full),
    "id-last4": ("证件号末 4 位", rule_id_last4),
    "id-last6": ("证件号末 6 位", rule_id_last6),
    "surname-dob": ("姓+DDMMYYYY", rule_surname_dob),
}


# ---------- qpdf 调用 ----------

# 加密类型分类：
#   none              — 完全未加密
#   permissions-only  — 仅权限位（user password 为空），qpdf --decrypt 一发可去
#   user-password     — 真加密，必须正确 user password 才能解
def classify_encryption(path: Path) -> str:
    """三态：none / permissions-only / user-password"""
    r = subprocess.run(
        ["qpdf", "--show-encryption", str(path)],
        capture_output=True, text=True
    )
    out = r.stdout + r.stderr
    if "File is not encrypted" in out:
        return "none"
    # qpdf 用空密码尝试时，如果命中 user password（即 user password 为空），
    # 会输出 "Supplied password is user password" 且 "User password = "（空值）
    if "Supplied password is user password" in out:
        return "permissions-only"
    # 也可能是 owner-only 模式：qpdf 对空密码返回需要密码 → requires-password 退 0
    rp = subprocess.run(
        ["qpdf", "--requires-password", str(path)],
        capture_output=True, text=True
    )
    if rp.returncode == 0:
        return "user-password"
    # 兜底：不属于以上几种归为 permissions-only（能开但有限制）
    return "permissions-only"


def strip_permissions(path: Path, out: Path) -> bool:
    """无密码去权限位：qpdf --decrypt（适用于 permissions-only 加密）"""
    r = subprocess.run(
        ["qpdf", "--decrypt", str(path), str(out)],
        capture_output=True, text=True
    )
    if r.returncode in (0, 3) and out.exists() and out.stat().st_size > 0:
        return True
    if out.exists():
        out.unlink()
    return False


def try_password(path: Path, password: str, out: Path) -> bool:
    """尝试用 password 解密。成功返回 True 并写 out。"""
    r = subprocess.run(
        ["qpdf", f"--password={password}", "--decrypt", str(path), str(out)],
        capture_output=True, text=True
    )
    # exit 0 = 干净, 3 = warning（仍生成文件），其他 = 失败
    if r.returncode in (0, 3) and out.exists() and out.stat().st_size > 0:
        return True
    if out.exists():
        out.unlink()
    return False


# ---------- candidates ----------

def generate_candidates(
    identity: Identity,
    issuer_filter: str | None = None,
) -> list[tuple[str, str, str]]:
    """生成 (rule_id, id_label, candidate_pw) 列表，去重保序。"""
    seen: set[str] = set()
    out: list[tuple[str, str, str]] = []
    ids = identity.all_ids() or [("none", "")]

    rules_to_run = (
        [(issuer_filter, RULES[issuer_filter])] if issuer_filter
        else list(RULES.items())
    )

    for rule_id, (_desc, fn) in rules_to_run:
        for id_label, id_val in ids:
            try:
                cand = fn(identity, id_val)
            except Exception:
                cand = None
            if not cand or cand in seen:
                continue
            seen.add(cand)
            out.append((rule_id, id_label, cand))
    return out


# ---------- 命中日志 ----------

def log_hit(file: Path, rule_id: str, id_label: str) -> None:
    HIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    import datetime
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')}\t{file.name}\t{rule_id}\t{id_label}\n"
    with HIT_LOG.open("a") as f:
        f.write(line)


def redact(pw: str) -> str:
    if len(pw) <= 4:
        return "*" * len(pw)
    return pw[:2] + "*" * (len(pw) - 4) + pw[-2:]


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="加密 PDF 路径")
    ap.add_argument("--out", help="输出路径（默认 <file>-decrypted.pdf）")
    ap.add_argument("--issuer", choices=list(RULES.keys()), help="只用指定规则")
    ap.add_argument("--password", help="跳过猜测直接用此密码")
    ap.add_argument("--list", action="store_true", help="列出所有规则后退出")
    ap.add_argument("--dry-run", action="store_true", help="只列候选不实际试")
    ap.add_argument("--show", action="store_true", help="成功后明文打印密码（默认遮罩）")
    args = ap.parse_args()

    if args.list:
        print("可用规则:")
        for k, (desc, _) in RULES.items():
            print(f"  {k:20} {desc}")
        return 0

    if not args.file:
        ap.print_help()
        return 1

    path = Path(args.file).expanduser().resolve()
    if not path.exists():
        print(f"ERROR: 文件不存在 {path}", file=sys.stderr)
        return 2

    if not is_encrypted(path):
        print(f"INFO: PDF 未加密（或 qpdf 检测无需密码），无需解密。")
        return 0

    out = Path(args.out).expanduser().resolve() if args.out else path.with_name(path.stem + "-decrypted.pdf")

    # 直接 password 模式
    if args.password:
        if try_password(path, args.password, out):
            print(f"OK: 解密成功 → {out}")
            return 0
        print(f"FAIL: 提供的密码不正确", file=sys.stderr)
        return 4

    identity = load_identity()
    candidates = generate_candidates(identity, args.issuer)

    if not candidates:
        print("ERROR: 无候选密码。", file=sys.stderr)
        print("请在 ~/.personal_env 设置：", file=sys.stderr)
        print('  export PDF_ID_BIRTH_DATE="YYYY-MM-DD"', file=sys.stderr)
        print('  export PDF_ID_SURNAME_PY="ZENG"', file=sys.stderr)
        print('  export PDF_ID_PASSPORT_HK="CJ6664388"  # 港澳通行证', file=sys.stderr)
        print('  export PDF_ID_HKID=""                  # 香港身份证', file=sys.stderr)
        print('  export PDF_ID_PASSPORT_INTL=""         # 国际护照', file=sys.stderr)
        print('  export PDF_ID_CN_ID=""                 # 大陆身份证', file=sys.stderr)
        return 3

    print(f"试 {len(candidates)} 个候选密码…")

    if args.dry_run:
        for rule_id, id_label, pw in candidates:
            print(f"  [{rule_id:20}] [{id_label:14}] {redact(pw)}")
        return 0

    for idx, (rule_id, id_label, pw) in enumerate(candidates, 1):
        if try_password(path, pw, out):
            shown = pw if args.show else redact(pw)
            print(f"OK ({idx}/{len(candidates)}): 命中规则 [{rule_id}] (id={id_label}) pw={shown}")
            print(f"  → {out}")
            log_hit(path, rule_id, id_label)
            return 0

    print(f"FAIL: {len(candidates)} 个候选都未命中。可用 --password 手动指定，或扩展规则库。", file=sys.stderr)
    return 4


if __name__ == "__main__":
    sys.exit(main())
