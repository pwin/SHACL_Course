# -*- coding: utf-8 -*-
"""Fetch every standards document the course links to and confirm that each
anchor still lands on an element.

    python scripts/check_links.py

Specifications move: sections are renumbered and ids change between drafts,
and the SHACL 1.2 documents are drafts. This fetches each document once and
checks every anchor in specs.SECTIONS and specs.READING_LIST against the ids
in the page. Needs the internet; nothing else in the course does.
"""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import specs  # noqa: E402

ID = re.compile(r'\sid="([^"]+)"')
NAME = re.compile(r'<a[^>]+name="([^"]+)"')


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "SHACL-Course link check"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    links = [url for _, url in specs.SECTIONS.values()]
    links += [url for _, items in specs.READING_LIST for url, _, _ in items]
    by_doc: dict[str, set] = {}
    for url in links:
        doc, _, anchor = url.partition("#")
        by_doc.setdefault(doc, set())
        if anchor:
            by_doc[doc].add(anchor)
    failed = 0
    for doc, anchors in sorted(by_doc.items()):
        try:
            page = fetch(doc)
        except Exception as e:
            print(f"FAIL {doc}: {e}")
            failed += len(anchors) or 1
            continue
        ids = set(ID.findall(page)) | set(NAME.findall(page))
        missing = sorted(a for a in anchors if a not in ids)
        status = "ok  " if not missing else "FAIL"
        print(f"{status} {doc}  ({len(anchors)} anchors)")
        for a in missing:
            print(f"        missing #{a}")
        failed += len(missing)
    print(f"\n{failed} broken anchors")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
