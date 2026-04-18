#!/usr/bin/env python3
"""对比两份 docx 中的图片，通过 SHA256 识别二进制完全相同的图片，定位章节位置。

Usage:
  python3 image_dedup.py --src OLD.docx --dst NEW.docx --out 图片重复清单.md
"""
import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docx import Document


def media_hashes(docx_path: Path) -> dict:
    out = {}
    with zipfile.ZipFile(docx_path) as z:
        for name in z.namelist():
            if name.startswith("word/media/") and not name.endswith("/"):
                fn = name.split("/")[-1]
                if not fn:
                    continue
                data = z.read(name)
                h = hashlib.sha256(data).hexdigest()
                out[fn] = (h, len(data))
    return out


def rels_map(docx_path: Path) -> dict:
    out = {}
    with zipfile.ZipFile(docx_path) as z:
        rels_xml = z.read("word/_rels/document.xml.rels")
    root = ET.fromstring(rels_xml)
    for rel in root:
        if rel.tag.endswith("Relationship"):
            target = rel.get("Target", "")
            if "media/" in target:
                rid = rel.get("Id")
                out[rid] = target.split("/")[-1]
    return out


def image_positions(docx_path: Path) -> list:
    doc = Document(str(docx_path))
    positions = []
    heading_stack = {}
    for i, p in enumerate(doc.paragraphs):
        style = (p.style.name or "").strip()
        m = re.match(r"^(?:Heading|标题)\s*(\d+)$", style, re.IGNORECASE)
        if m and p.text.strip():
            lvl = int(m.group(1))
            heading_stack[lvl] = p.text.strip()
            for k in list(heading_stack):
                if k > lvl:
                    del heading_stack[k]
        xml = p._p.xml
        for embed in re.findall(r'r:embed="([^"]+)"', xml):
            chain = " > ".join(heading_stack[k] for k in sorted(heading_stack))
            positions.append((i, embed, chain or "（前言）"))
    return positions


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="源 docx")
    ap.add_argument("--dst", required=True, help="目标 docx")
    ap.add_argument("--out", required=True, help="输出 MD 路径")
    args = ap.parse_args()

    SRC, DST = Path(args.src), Path(args.dst)
    src_hashes = media_hashes(SRC)
    dst_hashes = media_hashes(DST)
    print(f"源 {SRC.name}: {len(src_hashes)} 张", file=sys.stderr)
    print(f"目标 {DST.name}: {len(dst_hashes)} 张", file=sys.stderr)

    src_by_hash = {}
    for fn, (h, sz) in src_hashes.items():
        src_by_hash.setdefault(h, []).append((fn, sz))

    duplicates = {}
    for fn, (h, sz) in dst_hashes.items():
        if h in src_by_hash:
            duplicates[fn] = (h, sz, [n for n, _ in src_by_hash[h]])

    dst_rels = rels_map(DST)
    dst_pos = image_positions(DST)
    media_to_chains = {}
    for _, rid, chain in dst_pos:
        media = dst_rels.get(rid)
        if media:
            media_to_chains.setdefault(media, []).append(chain)

    lines = [f"# 图片重复清单 — {SRC.stem} → {DST.stem}\n",
             f"> 源 {len(src_hashes)} 张 / 目标 {len(dst_hashes)} 张 / **重复 {len(duplicates)} 张**\n",
             ""]
    if not duplicates:
        lines.append("✅ 无重复图片。\n")
    else:
        lines.append("## 二进制完全相同的图片\n")
        lines.append("| 目标文件 | 源文件 | KB | 出现章节 |")
        lines.append("|---------|--------|-----|---------|")
        for fn in sorted(duplicates, key=lambda x: int(re.sub(r"\D", "", x) or 0)):
            h, sz, src_fns = duplicates[fn]
            chains = media_to_chains.get(fn, ["（未在文档中引用）"])
            chains_str = "<br>".join(chains)
            lines.append(f"| {fn} | {', '.join(src_fns)} | {sz//1024} | {chains_str} |")

    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"OK -> {args.out}", file=sys.stderr)
    print(f"重复 {len(duplicates)} 张", file=sys.stderr)


if __name__ == "__main__":
    main()
