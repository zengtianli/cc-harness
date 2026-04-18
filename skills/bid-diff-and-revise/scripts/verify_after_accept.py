#!/usr/bin/env python3
"""模拟 Word "接受所有修订" 后扫描 docx 残留关键字。

track-changes docx 同时含 <w:del>（旧）+ <w:ins>（新）。用 zipfile 提取 document.xml，
删除 <w:del> 节点 + 解包 <w:ins> 内容，再扫残留关键字。

Usage:
  python3 verify_after_accept.py --docx 修改稿.docx --terms "自然资源集约利用,林长制,水质通报"
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def simulate_accept(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        doc_xml = z.read("word/document.xml")
    root = ET.fromstring(doc_xml)

    def remove_dels(elem):
        for child in list(elem):
            if child.tag == W + "del":
                elem.remove(child)
            else:
                remove_dels(child)

    def unwrap_ins(elem):
        for child in list(elem):
            if child.tag == W + "ins":
                idx = list(elem).index(child)
                for i, sub in enumerate(list(child)):
                    child.remove(sub)
                    elem.insert(idx + i, sub)
                elem.remove(child)
            else:
                unwrap_ins(child)

    remove_dels(root)
    unwrap_ins(root)

    texts = []
    for t in root.iter(W + "t"):
        if t.text:
            texts.append(t.text)
    return "".join(texts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docx", required=True, help="track-changes 修改稿 docx")
    ap.add_argument("--terms", required=True, help="要扫的关键字（逗号分隔）")
    ap.add_argument("--context", type=int, default=20, help="命中时显示的上下文字符数（默认 20）")
    args = ap.parse_args()

    terms = [t.strip() for t in args.terms.split(",") if t.strip()]

    all_text = simulate_accept(Path(args.docx))
    print(f"模拟接受所有修订后，文档总文本长度: {len(all_text)} 字")
    total = 0
    for term in terms:
        cnt = all_text.count(term)
        if cnt == 0:
            continue
        print(f"\n「{term}」 命中 {cnt} 处：")
        for m in re.finditer(re.escape(term), all_text):
            start = max(0, m.start() - args.context)
            end = min(len(all_text), m.end() + args.context)
            snippet = all_text[start:end].replace("\n", " ")
            print(f"  ... {snippet} ...")
        total += cnt

    print(f"\n模拟接受后残留合计: {total} 处")
    sys.exit(0 if total == 0 else 1)


if __name__ == "__main__":
    main()
