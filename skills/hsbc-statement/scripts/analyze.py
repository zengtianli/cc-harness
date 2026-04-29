#!/usr/bin/env python3
"""HSBC statement multi-type analyzer + archiver + index regenerator.

Inputs: 1+ HSBC statement PDFs (encrypted or decrypted).
Auto-detects type per PDF:
  - INVSTM0005  → Premier composite (monthly all-account snapshot)
  - INVSTM0019  → WPL daily slice (Period from=to)
  - INVSTM0021  → WPL monthly composite (with DEBIT INTEREST)

For each PDF: extract → render MD → archive raw + decrypted PDF.
After all: regenerate <out>/README.md (time-series index).

Usage:
  analyze.py <pdf>...                              # batch
  analyze.py <pdf>... --out docs/statements/       # custom out dir
  analyze.py <pdf>... --hibor 2.65                 # for monthly: HIBOR override
  analyze.py <pdf>... --no-hibor                   # skip HIBOR fetch
  analyze.py <pdf>... --start-date 2026-04-22      # for monthly: actual borrow start
  analyze.py <pdf>... --no-archive                 # don't move PDFs
  analyze.py <pdf>... --no-index                   # don't regen README.md
  analyze.py <pdf>... --json                       # JSON output (no MD)
  analyze.py --regen-index --out docs/statements/  # only regen README from existing MDs
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
          "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
MON_FULL = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5,
            "June": 6, "July": 7, "August": 8, "September": 9, "October": 10,
            "November": 11, "December": 12}

PDF_DECRYPT = Path.home() / ".claude/skills/pdf-decrypt/scripts/decrypt.py"


# ─── core utils ────────────────────────────────────────────────────────

def pdftotext(path: Path, layout: bool = True) -> str:
    args = ["pdftotext"]
    if layout:
        args.append("-layout")
    args += [str(path), "-"]
    out = subprocess.run(args, capture_output=True, text=True, check=True)
    return out.stdout


def is_encrypted(path: Path) -> bool:
    r = subprocess.run(["qpdf", "--show-encryption", str(path)],
                       capture_output=True, text=True)
    blob = (r.stdout + r.stderr).lower()
    return "is not encrypted" not in blob


def ensure_decrypted(path: Path) -> Path:
    """Return a decrypted PDF path. Decrypts in-place if needed (sibling -decrypted.pdf)."""
    if path.name.endswith("-decrypted.pdf"):
        return path
    out = path.parent / f"{path.stem}-decrypted.pdf"
    if out.exists():
        return out
    if is_encrypted(path):
        if not PDF_DECRYPT.exists():
            print(f"[error] pdf-decrypt skill not found at {PDF_DECRYPT}", file=sys.stderr)
            sys.exit(2)
        subprocess.run([sys.executable, str(PDF_DECRYPT), str(path)], check=True,
                       capture_output=True, text=True)
        if not out.exists():
            print(f"[error] decryption failed for {path}", file=sys.stderr)
            sys.exit(2)
        return out
    return path  # not encrypted


# ─── type detection ────────────────────────────────────────────────────

def detect_type(text: str) -> tuple[str | None, str | None]:
    """Return (kind, form_no). kind in {'premier-composite','wpl-daily','wpl-monthly'}."""
    if "INVSTM0005" in text or "IPSSTM0005" in text or "Financial Diary" in text:
        return "premier-composite", "INVSTM0005"
    period_m = re.search(
        r"Period.*?:\s*From\s+(\d{1,2}[A-Z]{3}\d{4})\s+to\s+(\d{1,2}[A-Z]{3}\d{4})",
        text, re.S)
    if period_m:
        if period_m.group(1) == period_m.group(2):
            form = "INVSTM0019" if "INVSTM0019" in text else "INVSTM0021"
            return "wpl-daily", form
        return "wpl-monthly", "INVSTM0021"
    return None, None


# ─── redaction ─────────────────────────────────────────────────────────

def redact_name(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2 and len(parts[1]) >= 1:
        return f"{parts[0]} {parts[1][0]}{'*' * 5}"
    return name


def redact_acno(acno: str) -> str:
    m = re.match(r"(\d{3})-(\d{6})-(\d{3})", acno)
    if m:
        return f"{m.group(1)}-{m.group(2)[:3]}***-***"
    return acno


# ─── shared header parsing ─────────────────────────────────────────────

def parse_ddmmmyyyy(s: str) -> datetime | None:
    m = re.match(r"(\d{1,2})([A-Z]{3})(\d{4})", s)
    if not m:
        return None
    return datetime(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))


def parse_ddmmmyy(s: str) -> datetime | None:
    m = re.match(r"(\d{1,2})([A-Z]{3})(\d{2})", s)
    if not m:
        return None
    return datetime(2000 + int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))


def common_header(text: str) -> dict:
    d: dict = {}
    if m := re.search(r"Date\s+日期\s*:\s*(\d{1,2}[A-Z]{3}\d{4})", text):
        if dt := parse_ddmmmyyyy(m.group(1)):
            d["statement_date"] = dt.strftime("%Y-%m-%d")
    if m := re.search(r"A/C name\s+戶口名稱\s*:\s*([A-Z][A-Z\s]+?)\s*$", text, re.M):
        d["ac_name_raw"] = m.group(1).strip()
        d["ac_name"] = redact_name(d["ac_name_raw"])
    if m := re.search(r"A/C no\s+戶口號碼\s*:\s*([\d\-]+)", text):
        d["ac_no_raw"] = m.group(1)
        d["ac_no"] = redact_acno(m.group(1))
    if m := re.search(r"Branch\s+分行\s+([A-Z][A-Z\s]+?OFFICE)", text):
        d["branch"] = m.group(1).strip()
    if m := re.search(
        r"Period.*?:\s*From\s+(\d{1,2}[A-Z]{3}\d{4})\s+to\s+(\d{1,2}[A-Z]{3}\d{4})",
        text, re.S):
        if dt := parse_ddmmmyyyy(m.group(1)):
            d["period_from"] = dt.strftime("%Y-%m-%d")
        if dt := parse_ddmmmyyyy(m.group(2)):
            d["period_to"] = dt.strftime("%Y-%m-%d")
    if m := re.search(r"Cash A/C\s+結算戶口\s*:\s*([\d\-]+)", text):
        d["cash_ac_no"] = redact_acno(m.group(1))
    return d


# ─── premier-composite extractor ───────────────────────────────────────

def extract_premier_composite(text: str) -> dict:
    d: dict = {}
    if m := re.search(
        r"(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
        text):
        d["statement_date"] = f"{m.group(3)}-{MON_FULL[m.group(2)]:02d}-{int(m.group(1)):02d}"
    if m := re.search(r"Number\s*:?\s*(\d{3}-\d{6}-\d{3})", text):
        d["ac_no_raw"] = m.group(1)
        d["ac_no"] = redact_acno(m.group(1))
    if m := re.search(r"Branch\s*:?\s*([A-Z][A-Z\s]+?)\s+Page", text):
        d["branch"] = m.group(1).strip()

    if m := re.search(r"Deposits\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})", text):
        d["deposits_total"] = float(m.group(3).replace(",", ""))
    if m := re.search(r"Investments\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})", text):
        d["investments_total"] = float(m.group(3).replace(",", ""))
    if m := re.search(
        r"Credit Facilities\s+([\d,]+\.\d{2})\s*DR\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*DR",
        text):
        d["credit_facilities_total"] = float(m.group(3).replace(",", ""))
    if m := re.search(
        r"Credit Cards\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*DR\s+([\d,]+\.\d{2})\s*DR",
        text):
        d["credit_cards_total"] = float(m.group(3).replace(",", ""))
    if m := re.search(
        r"Net Position\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*DR\s+([\d,]+\.\d{2})", text):
        d["net_position"] = float(m.group(3).replace(",", ""))
    elif m := re.search(r"Net Position\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})",
                        text):
        d["net_position"] = float(m.group(3).replace(",", ""))

    if m := re.search(
        r"Wealth Portfolio Lending\s+\S+\s+HKD\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*DR",
        text):
        d["wpl_credit_limit"] = float(m.group(1).replace(",", ""))
        d["wpl_outstanding"] = float(m.group(2).replace(",", ""))

    if m := re.search(
        r"average Total Relationship Balance from\s+(\d+\s+\w+\s+\d+)\s+to\s+(\d+\s+\w+\s+\d+)\s+was HK\$\s*([\d,]+\.\d{2})",
        text):
        d["trb_avg"] = float(m.group(3).replace(",", ""))
        d["trb_period"] = f"{m.group(1)} ~ {m.group(2)}"

    tds = []
    td_section = ""
    if m := re.search(r"Time Deposits.*?(?=Total Relationship|HSBC Premier|$)", text, re.S):
        td_section = m.group(0)
    for m in re.finditer(
        r"^\s*\d{4}\s+(\w{3})\s+([\d,]+\.\d{2})\s+([\d.]+)%\s+(\d+\s+\w+\s+\d+)/\s*\n?\s*(\d+\s+\w+\s+\d+)",
        td_section, re.M):
        tds.append({
            "ccy": m.group(1),
            "principal": float(m.group(2).replace(",", "")),
            "rate": float(m.group(3)),
            "start": m.group(4).strip(),
            "maturity": m.group(5).strip(),
        })
    if tds:
        d["time_deposits"] = tds

    cards = []
    cc_section = ""
    if m := re.search(r"Other Accounts - Credit Card.*?(?=HSBC Premier Account|Total Relationship|$)",
                      text, re.S):
        cc_section = m.group(0)
    for m in re.finditer(
        r"(HSBC [\w\s]+?(?:Diamond|Card)\([\w]+\))\s*\n\s*(\d{4}\s+\d{4}\s+\d{4}\s+\d{4})\s+(\w{3})\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*(?:DR)?\s+([\d,]+\.\d{2})\s*(?:DR)?",
        cc_section):
        cards.append({
            "name": m.group(1),
            "card_no": m.group(2)[-4:],
            "ccy": m.group(3),
            "limit": float(m.group(4).replace(",", "")),
            "balance": float(m.group(5).replace(",", "")),
            "hkd_eq": float(m.group(6).replace(",", "")),
        })
    if cards:
        d["credit_cards"] = cards

    return d


# ─── wpl-daily / wpl-monthly extractor ─────────────────────────────────

def extract_wpl(text: str, kind: str) -> dict:
    d = common_header(text)

    portfolio_section = text
    if m := re.search(r"Portfolio summary.*?(?=Portfolio details|$)", text, re.S):
        portfolio_section = m.group(0)
    if m := re.search(r"^.*?\bUNIT TRUSTS\s+([\d,]+\.\d{2})\s*$", portfolio_section, re.M):
        d["ut_hkd"] = float(m.group(1).replace(",", ""))
    if m := re.search(r"^.*?\bSTRUCTURED INVESTMENT\s+([\d,]+\.\d{2})\s*$", portfolio_section,
                      re.M):
        d["si_hkd"] = float(m.group(1).replace(",", ""))
    if m := re.search(r"^.*?\bTotal\s+([\d,]+\.\d{2})\s*$", portfolio_section, re.M):
        d["portfolio_total_hkd"] = float(m.group(1).replace(",", ""))

    holdings = []
    detail = ""
    if m := re.search(r"Portfolio details.*?(?=Transaction summary|Exchange rate|$)",
                      text, re.S):
        detail = m.group(0)
    # UT: take 2nd qty (closing balance), not 1st (opening)
    for m in re.finditer(
        r"(U\d{5,})\s+(.+?)\s*\(UNT\).*?\n\s*[\d,]+\.\d+\s+([\d,]+\.\d+)\s+(\w{3})\s+([\d.]+)\s+(\w{3})\s+([\d,]+\.\d{2})",
        detail, re.S):
        holdings.append({
            "type": "UT", "code": m.group(1), "name": m.group(2).strip(),
            "qty": float(m.group(3).replace(",", "")),
            "ccy": m.group(4), "price": float(m.group(5)),
            "mv_ccy": m.group(6), "mv": float(m.group(7).replace(",", "")),
        })
    # Structured: take 2nd qty (closing)
    for m in re.finditer(
        r"(SESIN\d+\w*)\s+(.+?)\s*\((FMT|UNT)\).*?\n\s*[\d,]+\s+([\d,]+)\s+([\d.]+)%\s+(\w{3})\s+([\d,]+\.\d{2})",
        detail, re.S):
        holdings.append({
            "type": "SI", "code": m.group(1), "name": m.group(2).strip(),
            "qty": int(m.group(4).replace(",", "")),
            "price_pct": float(m.group(5)),
            "mv_ccy": m.group(6), "mv": float(m.group(7).replace(",", "")),
        })
    if holdings:
        d["holdings"] = holdings

    if m := re.search(r"Exchange rate.*?USD\s+([\d.]+)", text, re.S):
        try:
            r = float(m.group(1))
            if 5 < r < 10:
                d["usd_hkd"] = r
        except ValueError:
            pass

    margin_section = text
    if m := re.search(
        r"Net Margin Ratio as of the statement date.*?(?=Details of financial|Notes \(continue|$)",
        text, re.S):
        margin_section = m.group(0)

    def first_hkd_after(label, where=margin_section):
        mm = re.search(rf"{re.escape(label)}.*?HKD\s*([\d,]+\.\d{{2}})", where, re.S)
        return float(mm.group(1).replace(",", "")) if mm else None

    if v := first_hkd_after("Outstanding Loan"):
        d["outstanding_loan"] = v
    if v := first_hkd_after("Credit Limit1"):
        d["credit_limit"] = v
    if m := re.search(r"Net Margin Ratio2\b.*?([\d,]+\.\d+)\s*%", margin_section, re.S):
        d["net_margin_ratio"] = float(m.group(1).replace(",", ""))
    if m := re.search(r"Margin Surplus.*?Surplus.*?HKD\s*([\d,]+\.\d{2})", margin_section, re.S):
        d["margin_surplus"] = float(m.group(1).replace(",", ""))

    fin_section = text
    if m := re.search(r"Details of financial accommodation.*", text, re.S):
        fin_section = m.group(0)
    if v := first_hkd_after("Maximum Credit Limit", fin_section):
        d["max_credit_limit"] = v

    if kind == "wpl-monthly":
        cash_section = ""
        if m := re.search(r"Cash Account Summary.*?(?=Notes \(continue|Net Margin Ratio|1\.\s+Cash Account Summary for the statement|$)",
                          text, re.S):
            cash_section = m.group(0)
        # B/F: "[date] BALANCE B/F  HKD  603.64 CR" or "...DR"
        if m := re.search(r"BALANCE B/F\s+HKD\s+([\d,]+\.\d{2})\s*(CR|DR)", cash_section):
            v = float(m.group(1).replace(",", ""))
            d["cash_bf"] = -v if m.group(2) == "CR" else v
            d["cash_bf_sign"] = m.group(2)
        # DEBIT INTEREST line (only when borrowed)
        if m := re.search(r"DEBIT INTEREST.*?HKD\s+([\d,]+\.\d{2})\s*DR", cash_section, re.S):
            d["cash_interest"] = float(m.group(1).replace(",", ""))
        # C/F: "[date] BALANCE C/F  HKD  99,516.36 DR"
        if m := re.search(r"BALANCE C/F\s+HKD\s+([\d,]+\.\d{2})\s*(CR|DR)", cash_section):
            v = float(m.group(1).replace(",", ""))
            d["cash_cf"] = v if m.group(2) == "DR" else -v
            d["cash_cf_sign"] = m.group(2)
        if m := re.search(r"(\d{1,2}[A-Z]{3}\d{2})\s+TO\s+(\d{1,2}[A-Z]{3}\d{2})", text):
            if d1 := parse_ddmmmyy(m.group(1)):
                d["interest_from"] = d1.strftime("%Y-%m-%d")
            if d2 := parse_ddmmmyy(m.group(2)):
                d["interest_to"] = d2.strftime("%Y-%m-%d")
            if d.get("interest_from") and d.get("interest_to"):
                f = datetime.fromisoformat(d["interest_from"])
                t = datetime.fromisoformat(d["interest_to"])
                d["interest_days"] = (t - f).days + 1

        ci = []
        ci_section = ""
        if m := re.search(r"Charges and income summary.*?(?=Purchase and Sales|Notes \(continue|$)",
                          text, re.S):
            ci_section = m.group(0)
        for m in re.finditer(
            r"(\d{1,2}[A-Z]{3}\d{4})\s+([A-Z][A-Z \-]+?)\s+(U\d{5,}|SESIN\w+)\s*\n?\s*(.+?)\n.*?(USD|HKD|CNY)\s+([\d,]+\.\d{2})",
            ci_section, re.S):
            ci.append({
                "date": m.group(1), "type": m.group(2).strip(),
                "code": m.group(3), "desc": m.group(4).strip()[:60],
                "ccy": m.group(5), "amount": float(m.group(6).replace(",", "")),
            })
        if ci:
            d["charges_income"] = ci

        tx = []
        tx_section = ""
        if m := re.search(
            r"Transaction summary.*?(?=Charges and income|Purchase and Sales Transactions pending|Notes \(continue|$)",
            text, re.S):
            tx_section = m.group(0)
        for m in re.finditer(
            r"(SESIN\w+|U\d{5,})\s+(.+?)\s*\n?\s*(\d{1,2}[A-Z]{3}\d{4})\s+(\d{1,2}[A-Z]{3}\d{4})\s+([\d.]+)%\s+([\d,]+)\s+(\w{3})\s+([\d,]+\.\d{2})",
            tx_section, re.S):
            tx.append({
                "code": m.group(1), "name": m.group(2).strip()[:60],
                "trade_date": m.group(3), "settle_date": m.group(4),
                "price_pct": float(m.group(5)), "qty": int(m.group(6).replace(",", "")),
                "ccy": m.group(7), "amount": float(m.group(8).replace(",", "")),
            })
        if tx:
            d["transactions"] = tx

    return d


# ─── HIBOR (for wpl-monthly) ───────────────────────────────────────────

def fetch_hkab_hibor_1m(timeout: float = 6.0) -> tuple[float, str] | None:
    req = urllib.request.Request("https://www.hkab.org.hk/en/rates/hibor",
                                 headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as f:
            html = f.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[warn] HKAB fetch failed: {e}", file=sys.stderr)
        return None
    stamp = ""
    if m := re.search(r"as at[^<]*on\s*(\d{4}-\d{1,2}-\d{1,2})", html):
        stamp = m.group(1)
    rates_block = re.search(r"(?is)Maturity.*?(?=Historical|<footer|</main)", html)
    pool = rates_block.group(0) if rates_block else html
    floats = [float(x) for x in re.findall(r"\b[0-9]\.\d{4,6}\b", pool)]
    if len(floats) >= 16:
        floats = floats[:8]
    elif len(floats) >= 8:
        floats = floats[:8]
    if len(floats) >= 4:
        return floats[3], stamp
    return None


def compute_rates(d: dict, hibor: float | None, hibor_src: str | None,
                  start_date_override: str | None) -> None:
    days = d.get("interest_days")
    if start_date_override and "interest_to" in d:
        s = datetime.fromisoformat(start_date_override)
        e = datetime.fromisoformat(d["interest_to"])
        days = (e - s).days
        d["actual_borrow_start"] = start_date_override
        d["actual_borrow_days"] = days
    # Use absolute value if B/F was credit (CR sign means we had cash, not borrow);
    # rate inference requires actual borrow principal. If B/F < 0 (CR) and there's no
    # interest, skip. If start_date_override was given, use Outstanding Loan as borrow basis.
    borrow_basis = None
    if d.get("cash_bf", 0) > 0:
        borrow_basis = d["cash_bf"]
    elif start_date_override and "outstanding_loan" in d:
        borrow_basis = d["outstanding_loan"]
    if d.get("cash_interest") and borrow_basis and days:
        eff = d["cash_interest"] / borrow_basis * (365 / days) * 100
        d["effective_rate_pct"] = eff
        if hibor is not None:
            d["hibor_1m_pct"] = hibor
            d["hibor_source"] = hibor_src or "?"
            d["spread_pct"] = eff - hibor
            if abs(eff - 1.0) < 0.05:
                d["floored"] = True


# ─── MD renderers ──────────────────────────────────────────────────────

def md_premier_composite(d: dict, archive: str) -> str:
    L = []
    L.append("> 隶属：[国际资产配置体系](../../README.md)")
    L.append(">")
    L.append("> 来源：HSBC `INVSTM0005` Premier 综合月结单")
    L.append(f"> 原文（脱敏）：`raw/{archive}.pdf`（加密；`.gitignore`）/ `decrypted/{archive}-decrypted.pdf`")
    L.append("")
    L.append(f"# HSBC Premier 综合月结 · {d.get('statement_date', '?')}")
    L.append("")
    L.append("## 1. 户口")
    L.append("")
    L.append("| 字段 | 值 |")
    L.append("|---|---|")
    L.append(f"| 户口号码 | {d.get('ac_no', '?')} |")
    L.append(f"| 分行 | {d.get('branch', '?')} |")
    L.append(f"| 结单日期 | {d.get('statement_date', '?')} |")
    L.append("")
    L.append("## 2. Financial Overview（HKD 等值）")
    L.append("")
    L.append("| 类别 | 合计 |")
    L.append("|---|---:|")
    if "deposits_total" in d:
        L.append(f"| Deposits | **{d['deposits_total']:,.2f}** |")
    if "investments_total" in d:
        L.append(f"| Investments | **{d['investments_total']:,.2f}** |")
    if "credit_facilities_total" in d:
        L.append(f"| Credit Facilities | **{d['credit_facilities_total']:,.2f} DR** |")
    if "credit_cards_total" in d:
        L.append(f"| Credit Cards | **{d['credit_cards_total']:,.2f} DR** |")
    if "net_position" in d:
        L.append(f"| **Net Position** | **{d['net_position']:,.2f}** |")
    L.append("")

    if "wpl_credit_limit" in d:
        L.append("## 3. WPL（Wealth Portfolio Lending）")
        L.append("")
        L.append("| 字段 | 值 |")
        L.append("|---|---:|")
        L.append(f"| 信贷限额 | HKD {d['wpl_credit_limit']:,.2f} |")
        L.append(f"| 已用 | HKD {d['wpl_outstanding']:,.2f} DR |")
        utilization = d['wpl_outstanding'] / d['wpl_credit_limit'] * 100
        L.append(f"| 使用率 | {utilization:.1f}% |")
        L.append("")

    if "time_deposits" in d:
        L.append("## 4. 定期存款")
        L.append("")
        L.append("| 货币 | 本金 | 利率 | 起息日 | 到期日 |")
        L.append("|---|---:|---:|---|---|")
        for td in d["time_deposits"]:
            L.append(f"| {td['ccy']} | {td['principal']:,.2f} | {td['rate']:.3f}% | {td['start']} | {td['maturity']} |")
        L.append("")

    if "credit_cards" in d:
        L.append("## 5. 信用卡")
        L.append("")
        L.append("| 卡 | 末四位 | 货币 | 限额 | 余额 | HKD 等值 |")
        L.append("|---|---|---|---:|---:|---:|")
        for c in d["credit_cards"]:
            L.append(f"| {c['name']} | {c['card_no']} | {c['ccy']} | {c['limit']:,.2f} | {c['balance']:,.2f} | {c['hkd_eq']:,.2f} |")
        L.append("")

    if "trb_avg" in d:
        L.append("## 6. Total Relationship Balance")
        L.append("")
        L.append(f"- 平均 TRB：**HKD {d['trb_avg']:,.2f}**（{d.get('trb_period', '')}）")
        if d['trb_avg'] < 1_000_000:
            L.append("- 低于 100 万门槛，但作为 auto-upgrade 客户**豁免** Below Balance Fee")
        L.append("")

    return "\n".join(L) + "\n"


def md_wpl_daily(d: dict, archive: str) -> str:
    L = []
    L.append("> 隶属：[国际资产配置体系](../../README.md)")
    L.append(">")
    L.append("> 来源：HSBC `INVSTM0019` Investment + WPL 单日结单")
    L.append(f"> 原文（脱敏）：`raw/{archive}.pdf`（加密；`.gitignore`）/ `decrypted/{archive}-decrypted.pdf`")
    L.append("")
    L.append(f"# HSBC WPL 单日结单 · {d.get('statement_date', '?')}")
    L.append("")
    L.append("## 1. 户口")
    L.append("")
    L.append("| 字段 | 值 |")
    L.append("|---|---|")
    L.append(f"| 户口名称 | {d.get('ac_name', '?')} |")
    L.append(f"| 户口号码 | {d.get('ac_no', '?')} |")
    L.append(f"| 分行 | {d.get('branch', '?')} |")
    L.append(f"| 结单期 | {d.get('statement_date', '?')} 单日 |")
    L.append(f"| 结算户口 | {d.get('cash_ac_no', '?')} |")
    L.append("")

    L.append("## 2. 投资组合")
    L.append("")
    if "holdings" in d:
        L.append("| 类别 | 证券 | 数量 | 单价 | 市值 |")
        L.append("|---|---|---:|---:|---:|")
        for h in d["holdings"]:
            if h["type"] == "UT":
                L.append(f"| Unit Trust | {h['name']} `{h['code']}` | {h['qty']:,.3f} UNT | {h['ccy']} {h['price']:.2f} | {h['mv_ccy']} {h['mv']:,.2f} |")
            else:
                L.append(f"| Structured | {h['name']} `{h['code']}` | {h['qty']:,} FMT | {h['price_pct']:.2f}% | {h['mv_ccy']} {h['mv']:,.2f} |")
    if "portfolio_total_hkd" in d:
        L.append(f"| **合计 HKD** | | | | **{d['portfolio_total_hkd']:,.2f}** |")
    L.append("")
    if "usd_hkd" in d:
        L.append(f"汇率 USD/HKD = {d['usd_hkd']:.5f}")
        L.append("")

    if any(k in d for k in ("outstanding_loan", "credit_limit", "net_margin_ratio")):
        L.append("## 3. WPL 贷款 / 孖展")
        L.append("")
        L.append("| 字段 | 值 |")
        L.append("|---|---:|")
        if "outstanding_loan" in d:
            L.append(f"| 未偿还贷款 | **HKD {d['outstanding_loan']:,.2f} DR** |")
        if "credit_limit" in d:
            L.append(f"| 信贷限额（当期） | HKD {d['credit_limit']:,.2f} |")
        if "max_credit_limit" in d:
            L.append(f"| 信贷限额上限 | HKD {d['max_credit_limit']:,.2f} |")
        if "net_margin_ratio" in d:
            L.append(f"| **净孖展比率** | **{d['net_margin_ratio']:.2f}%** |")
        if "margin_surplus" in d:
            L.append(f"| 孖展盈余 | HKD {d['margin_surplus']:,.2f} |")
        L.append("")

    return "\n".join(L) + "\n"


def md_wpl_monthly(d: dict, archive: str) -> str:
    L = []
    L.append("> 隶属：[国际资产配置体系](../../README.md)")
    L.append(">")
    L.append("> 来源：HSBC `INVSTM0021` Investment + WPL 月结复合结单")
    L.append(f"> 原文（脱敏）：`raw/{archive}.pdf`（加密；`.gitignore`）/ `decrypted/{archive}-decrypted.pdf`")
    L.append("")
    period = f"{d.get('period_from', '?')} → {d.get('period_to', '?')}"
    L.append(f"# HSBC WPL 月结 · {d.get('statement_date', '?')}（结单期 {period}）")
    L.append("")
    L.append("## 1. 户口")
    L.append("")
    L.append("| 字段 | 值 |")
    L.append("|---|---|")
    L.append(f"| 户口名称 | {d.get('ac_name', '?')} |")
    L.append(f"| 户口号码 | {d.get('ac_no', '?')} |")
    L.append(f"| 分行 | {d.get('branch', '?')} |")
    L.append(f"| 结单期 | {period} |")
    L.append(f"| 结算户口 | {d.get('cash_ac_no', '?')} |")
    L.append("")

    L.append("## 2. 投资组合（结单日 close）")
    L.append("")
    if "holdings" in d:
        L.append("| 类别 | 证券 | 数量 | 单价 | 市值 |")
        L.append("|---|---|---:|---:|---:|")
        for h in d["holdings"]:
            if h["type"] == "UT":
                L.append(f"| Unit Trust | {h['name']} `{h['code']}` | {h['qty']:,.3f} UNT | {h['ccy']} {h['price']:.2f} | {h['mv_ccy']} {h['mv']:,.2f} |")
            else:
                L.append(f"| Structured | {h['name']} `{h['code']}` | {h['qty']:,} FMT | {h['price_pct']:.2f}% | {h['mv_ccy']} {h['mv']:,.2f} |")
    if "portfolio_total_hkd" in d:
        L.append(f"| **合计 HKD** | | | | **{d['portfolio_total_hkd']:,.2f}** |")
    L.append("")
    if "usd_hkd" in d:
        L.append(f"汇率 USD/HKD = {d['usd_hkd']:.5f}")
        L.append("")

    if "transactions" in d and d["transactions"]:
        L.append("## 3. 期间交易")
        L.append("")
        L.append("| 证券 | 交易日 | 交收日 | 单价 | 数量 | 金额 |")
        L.append("|---|---|---|---:|---:|---:|")
        for t in d["transactions"]:
            L.append(f"| {t['name']} `{t['code']}` | {t['trade_date']} | {t['settle_date']} | {t['price_pct']:.2f}% | {t['qty']:,} | {t['ccy']} {t['amount']:,.2f} |")
        L.append("")

    if "charges_income" in d and d["charges_income"]:
        L.append("## 4. 费用与收益")
        L.append("")
        L.append("| 日期 | 类型 | 证券 | 描述 | 金额 |")
        L.append("|---|---|---|---|---:|")
        for c in d["charges_income"]:
            L.append(f"| {c['date']} | {c['type']} | {c['code']} | {c['desc']} | {c['ccy']} {c['amount']:,.2f} |")
        L.append("")

    if any(k in d for k in ("outstanding_loan", "credit_limit", "net_margin_ratio")):
        L.append("## 5. WPL 贷款 / 孖展")
        L.append("")
        L.append("| 字段 | 值 |")
        L.append("|---|---:|")
        if "outstanding_loan" in d:
            L.append(f"| 未偿还贷款 | **HKD {d['outstanding_loan']:,.2f} DR** |")
        if "credit_limit" in d:
            L.append(f"| 信贷限额（当期） | HKD {d['credit_limit']:,.2f} |")
        if "max_credit_limit" in d:
            L.append(f"| 信贷限额上限 | HKD {d['max_credit_limit']:,.2f} |")
        if "net_margin_ratio" in d:
            L.append(f"| **净孖展比率** | **{d['net_margin_ratio']:.2f}%** |")
        if "margin_surplus" in d:
            L.append(f"| 孖展盈余 | HKD {d['margin_surplus']:,.2f} |")
        L.append("")

    if "cash_bf" in d or "cash_interest" in d:
        L.append("## 6. 利息 / 利率反推")
        L.append("")
        L.append("| 字段 | 值 |")
        L.append("|---|---:|")
        if "interest_from" in d:
            L.append(f"| 计息期（结单口径） | {d['interest_from']} → {d['interest_to']}（{d.get('interest_days', '?')} 天） |")
        if "actual_borrow_start" in d:
            L.append(f"| 实际借款起 | {d['actual_borrow_start']}（{d['actual_borrow_days']} 天）|")
        if "cash_bf" in d:
            sign = d.get("cash_bf_sign", "DR")
            L.append(f"| 期初 B/F | HKD {abs(d['cash_bf']):,.2f} {sign} |")
        if "cash_interest" in d:
            L.append(f"| 本期利息 | HKD {d['cash_interest']:,.2f} |")
        if "cash_cf" in d:
            sign = d.get("cash_cf_sign", "DR")
            L.append(f"| 期末 C/F | HKD {abs(d['cash_cf']):,.2f} {sign} |")
        if "effective_rate_pct" in d:
            L.append(f"| **有效年化** | **{d['effective_rate_pct']:.4f}% p.a.** |")
        if "hibor_1m_pct" in d:
            L.append(f"| 1M HIBOR 参照 | {d['hibor_1m_pct']:.4f}% （{d.get('hibor_source', '')}） |")
        if "spread_pct" in d:
            L.append(f"| **推算 spread** | **{d['spread_pct']:+.4f}%** |")
        if d.get("floored"):
            L.append("| ⚠ 1% 地板 | 已触发，spread 仅作下界估计 |")
        L.append("")

    return "\n".join(L) + "\n"


# ─── archive ───────────────────────────────────────────────────────────

def archive_name(d: dict, kind: str) -> str:
    date = d.get("statement_date", "0000-00-00")
    return f"{date}_hsbc-{kind}"


def archive_pdfs(orig: Path, decrypted: Path, out_dir: Path, archive: str):
    raw_dir = out_dir / "raw"
    dec_dir = out_dir / "decrypted"
    raw_dir.mkdir(parents=True, exist_ok=True)
    dec_dir.mkdir(parents=True, exist_ok=True)
    raw_target = raw_dir / f"{archive}.pdf"
    dec_target = dec_dir / f"{archive}-decrypted.pdf"
    if not raw_target.exists() and orig.exists() and orig.resolve() != raw_target.resolve():
        shutil.move(str(orig), str(raw_target))
    elif orig.exists() and orig.resolve() != raw_target.resolve():
        try:
            orig.unlink()
        except OSError:
            pass
    if decrypted.exists() and decrypted.resolve() != dec_target.resolve():
        if not dec_target.exists():
            shutil.move(str(decrypted), str(dec_target))
        else:
            try:
                decrypted.unlink()
            except OSError:
                pass


# ─── index regen ───────────────────────────────────────────────────────

def regen_index(out_dir: Path):
    rows = []
    for md in sorted(out_dir.glob("*_hsbc-*.md"), reverse=True):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_hsbc-(.+)\.md$", md.name)
        if not m:
            continue
        date, kind = m.group(1), m.group(2)
        body = md.read_text()
        portfolio = extract_field(body, r"\*\*合计 HKD\*\* \|.*?\| \*\*([\d,]+\.\d{2})") \
                    or extract_field(body, r"Total\s+([\d,]+\.\d{2})")
        loan = extract_field(body, r"未偿还贷款 \| \*\*HKD ([\d,]+\.\d{2})")
        margin = extract_field(body, r"净孖展比率\*\* \| \*\*([\d.]+)%")
        net_pos = extract_field(body, r"\*\*Net Position\*\* \| \*\*([\d,]+\.\d{2})")
        rows.append({"date": date, "kind": kind, "file": md.name,
                     "portfolio": portfolio, "loan": loan, "margin": margin,
                     "net_pos": net_pos})

    L = []
    L.append("> 隶属：[国际资产配置体系](../../README.md)")
    L.append("")
    L.append("# 银行结单 · 时间序列")
    L.append("")
    L.append("自动生成 — 由 `hsbc-statement` skill 维护。改单份 MD 后跑：")
    L.append("")
    L.append("```bash")
    L.append("python3 ~/.claude/skills/hsbc-statement/scripts/analyze.py --regen-index --out docs/statements/")
    L.append("```")
    L.append("")
    L.append("## 时间序列总表")
    L.append("")
    L.append("| 日期 | 类型 | Portfolio HKD | Loan DR | Net Margin | Net Pos | 链接 |")
    L.append("|---|---|---:|---:|---:|---:|---|")
    for r in rows:
        margin_cell = (r['margin'] + '%') if r['margin'] else '—'
        L.append(f"| {r['date']} | `{r['kind']}` | {r['portfolio'] or '—'} | {r['loan'] or '—'} | {margin_cell} | {r['net_pos'] or '—'} | [{r['file']}](./{r['file']}) |")
    L.append("")
    L.append("## 子目录")
    L.append("")
    L.append("- `raw/` — 加密原件 PDF（`.gitignore *.pdf`，仅本地）")
    L.append("- `decrypted/` — qpdf 解密产物（`.gitignore *-decrypted.pdf`，仅本地）")
    L.append("- `refs/` — 参考资料（KFS 截图 / Tariff PDF 等）")
    L.append("")
    (out_dir / "README.md").write_text("\n".join(L) + "\n")


def extract_field(body: str, pat: str) -> str | None:
    m = re.search(pat, body)
    return m.group(1) if m else None


# ─── main ──────────────────────────────────────────────────────────────

def process_pdf(pdf: Path, out_dir: Path, args) -> dict | None:
    decrypted = ensure_decrypted(pdf)
    text = pdftotext(decrypted)
    kind, form = detect_type(text)
    if kind is None:
        print(f"[skip] {pdf.name}: cannot detect type", file=sys.stderr)
        return None

    if kind == "premier-composite":
        d = extract_premier_composite(text)
    else:
        d = extract_wpl(text, kind)

    d["_kind"] = kind
    d["_form"] = form

    if kind == "wpl-monthly" and d.get("cash_bf"):
        hibor, src = None, None
        if args.hibor is not None:
            hibor, src = args.hibor, "manual"
        elif not args.no_hibor:
            if hit := fetch_hkab_hibor_1m():
                hibor, stamp = hit
                src = f"HKAB current ({stamp})"
        compute_rates(d, hibor, src, args.start_date)

    if args.json:
        return d

    archive = archive_name(d, kind)
    if kind == "premier-composite":
        md_text = md_premier_composite(d, archive)
    elif kind == "wpl-daily":
        md_text = md_wpl_daily(d, archive)
    else:
        md_text = md_wpl_monthly(d, archive)

    md_path = out_dir / f"{archive}.md"
    md_path.write_text(md_text)
    print(f"[ok] {pdf.name} → {md_path}")

    if not args.no_archive:
        archive_pdfs(pdf, decrypted, out_dir, archive)

    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="*", type=Path)
    ap.add_argument("--out", type=Path, default=Path("docs/statements/"))
    ap.add_argument("--no-archive", action="store_true")
    ap.add_argument("--no-index", action="store_true")
    ap.add_argument("--regen-index", action="store_true")
    ap.add_argument("--hibor", type=float, default=None)
    ap.add_argument("--no-hibor", action="store_true")
    ap.add_argument("--start-date", type=str, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.regen_index:
        regen_index(out_dir)
        print(f"[ok] index regen → {out_dir / 'README.md'}")
        return 0

    if not args.pdfs:
        print("error: provide PDFs or --regen-index", file=sys.stderr)
        return 2

    results = []
    for pdf in args.pdfs:
        if not pdf.exists():
            print(f"[skip] {pdf}: not found", file=sys.stderr)
            continue
        d = process_pdf(pdf, out_dir, args)
        if d:
            results.append(d)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    elif not args.no_index:
        regen_index(out_dir)
        print(f"[ok] index → {out_dir / 'README.md'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
