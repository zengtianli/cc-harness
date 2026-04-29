#!/usr/bin/env python3
"""HSBC Wealth Portfolio Lending statement analyzer.

Inputs: decrypted HSBC INVSTM0019 PDF
Extracts: Cash Account opening/closing balance, DEBIT INTEREST, period dates,
          Outstanding Loan, Credit Limit, Net Margin Ratio, Maximum Credit Limit,
          Portfolio holdings (UT + Structured)
Computes: effective annualized rate, infers spread vs 1M HIBOR
Output:  text report (stdout) or JSON (--json)

HIBOR sources (in order):
  1. --hibor X.XX (manual override, e.g. period average)
  2. HKAB current rate (parsed from https://www.hkab.org.hk/en/rates/hibor)
  3. None → skip spread inference, only effective rate

Usage:
  analyze.py <decrypted.pdf>                    # auto-fetch current HIBOR
  analyze.py <decrypted.pdf> --hibor 2.65       # use given HIBOR avg %
  analyze.py <decrypted.pdf> --json             # JSON output
  analyze.py <decrypted.pdf> --md > report.md   # markdown report
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}


def pdftotext(path: Path, layout: bool = True) -> str:
    args = ["pdftotext"]
    if layout:
        args.append("-layout")
    args += [str(path), "-"]
    out = subprocess.run(args, capture_output=True, text=True, check=True)
    return out.stdout


def parse_ddmmmyy(s: str) -> datetime:
    # "10APR26" → 2026-04-10
    m = re.match(r"(\d{1,2})([A-Z]{3})(\d{2})", s)
    if not m:
        raise ValueError(f"bad date: {s}")
    d, mon, yy = int(m.group(1)), MONTHS[m.group(2)], int(m.group(3))
    return datetime(2000 + yy, mon, d)


def extract(text: str) -> dict:
    """Pull every field we care about from pdftotext output.

    pdftotext default mode flattens 3-column tables into a top-down sequence,
    so we can't rely on adjacency between row-heads and amounts. Strategy:
    pin to nearest unique anchor for each field, then take next-matching value.
    """
    data: dict = {}

    # Header (with -layout mode, label and value are on same line)
    if m := re.search(r"Date\s+日期\s*:\s*(\d{1,2}[A-Z]{3}\d{4})", text):
        data["statement_date"] = m.group(1)
    if m := re.search(r"A/C name\s+戶口名稱\s*:\s*([A-Z][A-Z0-9* ]+?)\s*$", text, re.M):
        data["ac_name"] = m.group(1).strip()
    if m := re.search(r"A/C no\s+戶口號碼\s*:\s*([\d\-*]+)", text):
        data["ac_no"] = m.group(1).strip()
    if m := re.search(r"Branch\s+分行\s+([A-Z][A-Z\s]+?OFFICE)", text):
        data["branch"] = m.group(1).strip()

    # Interest period "10APR26 TO 27APR26"
    if m := re.search(r"(\d{1,2}[A-Z]{3}\d{2})\s+TO\s+(\d{1,2}[A-Z]{3}\d{2})", text):
        d1 = parse_ddmmmyy(m.group(1))
        d2 = parse_ddmmmyy(m.group(2))
        data["interest_from"] = d1.strftime("%Y-%m-%d")
        data["interest_to"] = d2.strftime("%Y-%m-%d")
        # Inclusive day count: 10APR..27APR = 18 days
        data["interest_days"] = (d2 - d1).days + 1

    # Cash Account (3 amounts in DR form, in order: B/F, interest, C/F)
    cash_section = text
    if m := re.search(
        r"Cash Account Summary.*?(?=Net Margin Ratio|$)", text, re.S
    ):
        cash_section = m.group(0)
    drs = re.findall(r"([\d,]+\.\d{2})\s*DR\b", cash_section)
    if len(drs) >= 3:
        data["cash_bf"] = float(drs[0].replace(",", ""))
        data["cash_interest"] = float(drs[1].replace(",", ""))
        data["cash_cf"] = float(drs[2].replace(",", ""))

    # Margin block — labels and values are split across cols. Pin per-field.
    margin_section = text
    if m := re.search(
        r"Net Margin Ratio as of the statement date.*?(?=Details of financial|$)",
        text, re.S
    ):
        margin_section = m.group(0)

    def first_hkd_after(label: str, where: str = margin_section) -> float | None:
        m = re.search(rf"{re.escape(label)}.*?HKD\s*([\d,]+\.\d{{2}})", where, re.S)
        return float(m.group(1).replace(",", "")) if m else None

    if v := first_hkd_after("Outstanding Loan"):
        data["outstanding_loan"] = v
    if v := first_hkd_after("Credit Limit1"):
        data["credit_limit"] = v
    if m := re.search(r"Net Margin Ratio2\b.*?([\d,]+\.\d+)\s*%", margin_section, re.S):
        data["net_margin_ratio"] = float(m.group(1).replace(",", ""))
    if m := re.search(r"Margin Surplus.*?Surplus.*?HKD\s*([\d,]+\.\d{2})", margin_section, re.S):
        data["margin_surplus"] = float(m.group(1).replace(",", ""))

    # Details of financial accommodation — Maximum Credit Limit
    fin_section = text
    if m := re.search(r"Details of financial accommodation.*", text, re.S):
        fin_section = m.group(0)
    if v := first_hkd_after("Maximum Credit Limit", fin_section):
        data["max_credit_limit"] = v

    # Portfolio summary totals: "UNIT TRUSTS\n[...]\n331,612.70"
    portfolio_section = text
    if m := re.search(r"Portfolio summary.*?(?=Portfolio details|$)", text, re.S):
        portfolio_section = m.group(0)
    # -layout output may have address fragments before the label, e.g.
    # "       ***801***                            UNIT TRUSTS                331,612.70"
    if m := re.search(r"^.*?\bUNIT TRUSTS\s+([\d,]+\.\d{2})\s*$", portfolio_section, re.M):
        data["ut_hkd"] = float(m.group(1).replace(",", ""))
    if m := re.search(
        r"^.*?\bSTRUCTURED INVESTMENT\s+([\d,]+\.\d{2})\s*$", portfolio_section, re.M
    ):
        data["si_hkd"] = float(m.group(1).replace(",", ""))
    if m := re.search(r"^.*?\bTotal\s+([\d,]+\.\d{2})\s*$", portfolio_section, re.M):
        data["portfolio_total_hkd"] = float(m.group(1).replace(",", ""))

    # Exchange rate "Exchange rate against HKD ... USD 7.8353500"
    if m := re.search(r"Exchange rate.*?USD\s+([\d.]+)", text, re.S):
        try:
            r = float(m.group(1))
            if 5 < r < 10:
                data["usd_hkd"] = r
        except ValueError:
            pass

    return data


def fetch_hkab_hibor_1m(timeout: float = 6.0) -> tuple[float, str] | None:
    """Scrape current 1M HIBOR from HKAB rates page.

    HKAB embeds 8 fixings (O/N, 1W, 2W, 1M, 2M, 3M, 6M, 12M) inline.
    We pick the 1M slot heuristically: the term structure is typically
    monotonic-ish but has a shape; safer to look near the "1month" label.
    """
    req = urllib.request.Request(
        "https://www.hkab.org.hk/en/rates/hibor", headers={"User-Agent": UA}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as f:
            html = f.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[warn] HKAB fetch failed: {e}", file=sys.stderr)
        return None

    # Find the "as at ... on YYYY-M-D" stamp
    stamp = ""
    if m := re.search(r"as at[^<]*on\s*(\d{4}-\d{1,2}-\d{1,2})", html):
        stamp = m.group(1)

    # Pull all float values around the rates table; try near "1month" / "1 month" tokens
    # HKAB markup uses 'maturity' labels; we look at the cluster of 8 floats following the table.
    rates_block = re.search(
        r"(?is)Maturity.*?(?=Historical|<footer|</main)", html
    )
    pool = rates_block.group(0) if rates_block else html
    floats = [float(x) for x in re.findall(r"\b[0-9]\.\d{4,6}\b", pool)]
    if len(floats) < 4:
        return None
    # Heuristic: term structure has 8 fixings. If there are exactly 8, 1M is index 3 (O/N, 1W, 2W, 1M).
    # If duplicated (16) take first 8.
    if len(floats) >= 16:
        floats = floats[:8]
    elif len(floats) >= 8:
        floats = floats[:8]
    if len(floats) >= 4:
        return floats[3], stamp
    return None


def fmt_money(x: float, ccy: str = "HKD") -> str:
    return f"{ccy} {x:,.2f}"


def report_text(d: dict) -> str:
    lines = []
    lines.append(f"=== HSBC WPL 结单分析 · {d.get('statement_date', '?')} ===")
    lines.append(f"账户: {d.get('ac_name', '?')}  /  {d.get('ac_no', '?')}")
    lines.append("")
    lines.append("[投资组合]")
    if "ut_hkd" in d:
        lines.append(f"  Unit Trust:           {fmt_money(d['ut_hkd'])}")
    if "si_hkd" in d:
        lines.append(f"  Structured Inv:       {fmt_money(d['si_hkd'])}")
    if "usd_hkd" in d:
        lines.append(f"  USD/HKD:              {d['usd_hkd']:.5f}")
    lines.append("")
    lines.append("[贷款 / 孖展]")
    if "outstanding_loan" in d:
        lines.append(f"  未偿还贷款:           {fmt_money(d['outstanding_loan'])}")
    if "credit_limit" in d:
        lines.append(f"  当期信贷限额:         {fmt_money(d['credit_limit'])}")
    if "max_credit_limit" in d:
        lines.append(f"  信贷限额上限:         {fmt_money(d['max_credit_limit'])}")
    if "net_margin_ratio" in d:
        lines.append(f"  净孖展比率:           {d['net_margin_ratio']:.2f}%")
    if "margin_surplus" in d:
        lines.append(f"  孖展盈余:             {fmt_money(d['margin_surplus'])}")
    lines.append("")
    lines.append("[利息 / 利率反推]")
    if "interest_from" in d:
        lines.append(f"  计息期:               {d['interest_from']} → {d['interest_to']}  ({d['interest_days']} 天)")
    if "cash_bf" in d:
        lines.append(f"  期初本金 (B/F):       {fmt_money(d['cash_bf'])}")
    if "cash_interest" in d:
        lines.append(f"  本期利息:             {fmt_money(d['cash_interest'])}")
    if "cash_cf" in d:
        lines.append(f"  期末余额 (C/F):       {fmt_money(d['cash_cf'])}")

    if "effective_rate_pct" in d:
        lines.append("")
        lines.append(f"  ▸ 有效年化:           {d['effective_rate_pct']:.4f}% p.a.")
        lines.append(f"     公式: 利息 / 本金 × (365 / 天数)")
    if "hibor_1m_pct" in d:
        src = d.get("hibor_source", "?")
        lines.append(f"  ▸ 1M HIBOR (参照):    {d['hibor_1m_pct']:.4f}%  [{src}]")
    if "spread_pct" in d:
        lines.append(f"  ▸ 推算 spread:        {d['spread_pct']:+.4f}% p.a.")
        if d.get("floored"):
            lines.append("     ⚠ 有效利率已触 1% p.a. 地板，spread 数值仅作下界估计")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="HSBC WPL statement analyzer")
    ap.add_argument("pdf", type=Path, help="Decrypted HSBC INVSTM0019 PDF")
    ap.add_argument("--hibor", type=float, default=None,
                    help="1M HIBOR avg over period in percent (e.g. 2.65). "
                         "If omitted, fetch current from HKAB.")
    ap.add_argument("--no-hibor", action="store_true",
                    help="Skip HIBOR fetch / spread inference")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"error: PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    text = pdftotext(args.pdf)
    d = extract(text)

    # Effective rate
    if all(k in d for k in ("cash_bf", "cash_interest", "interest_days")) and d["cash_bf"] > 0:
        eff = d["cash_interest"] / d["cash_bf"] * (365 / d["interest_days"]) * 100
        d["effective_rate_pct"] = eff

        # HIBOR
        hibor = None
        src = None
        if args.hibor is not None:
            hibor = args.hibor
            src = "manual"
        elif not args.no_hibor:
            hit = fetch_hkab_hibor_1m()
            if hit:
                hibor, stamp = hit
                src = f"HKAB current ({stamp})"
        if hibor is not None:
            d["hibor_1m_pct"] = hibor
            d["hibor_source"] = src or "?"
            d["spread_pct"] = eff - hibor
            # Floor check: HSBC tariff says "HIBOR + spread < 1% → charged at 1%"
            # Mark "near floor" only if eff is within 5bp of 1.000% (clearly clamped)
            if abs(eff - 1.0) < 0.05:
                d["floored"] = True

    if args.json:
        print(json.dumps(d, indent=2, ensure_ascii=False))
    else:
        print(report_text(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
