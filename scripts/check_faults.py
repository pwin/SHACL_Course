# -*- coding: utf-8 -*-
"""Confirm that every numbered fault is reported by the lessons that name it.

    python scripts/check_shapes.py      # first, to produce build/results/
    python scripts/check_faults.py

data/faults.ttl and data/faults-1.2.ttl carry one comment block per fault:

    # F22  A segment from The Inkwell to The Inkwell, of no length
    #                                                          -> s18 (sh:disjoint), s13 (sh:minExclusive)
    bt:seg-inkwell-inkwell
        ...

This script reads the fault number, the lesson ids in its comment, and the
subject of the first triple after the comment, then checks that each named
lesson's measured report has a result whose focus node is that subject (or,
for the annotation faults, whose message or value mentions it). It is the
answer key made checkable: the faults file says which lesson catches what,
and this confirms it still does.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "build" / "results"

FAULT = re.compile(r"^# (F\d\d)\s+(.*)$")
LESSON = re.compile(r"\bs\d\d\b")
SUBJECT = re.compile(r"^(bt:[A-Za-z0-9._-]+)")

# Faults whose focus node is not the subject line: a reifier (blank node), or
# a fault reported on a neighbouring resource. Each maps to what to look for
# in the result's focus node, value or message instead.
INDIRECT = {
    "F07": "stock-ghost",            # the untyped shop is found through its stock record
    "F25:s28": "place-powys",        # the second book town is reported on its council area
    "F33": "shop-marginalia",        # the reifier is anonymous; the result is on the shop
    "F34": "the manager",            # the reifier is anonymous; the value is the string
    "F35": "stock-inkwell--the-book-town",
}


def faults(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    out, current, lessons = [], None, set()
    for line in lines:
        m = FAULT.match(line)
        if m:
            if current:
                out.append((current, sorted(lessons), None))
            current, lessons = m.group(1), set(LESSON.findall(line))
            continue
        if current and line.startswith("#"):
            lessons |= set(LESSON.findall(line))
            continue
        if current and (sm := SUBJECT.match(line)):
            out.append((current, sorted(lessons), sm.group(1)))
            current, lessons = None, set()
    # Two comments can share one subject block: keep every fault, fill in subjects.
    filled, last_subject = [], None
    for fid, ls, subj in reversed(out):
        if subj is None:
            subj = last_subject
        else:
            last_subject = subj
        filled.append((fid, ls, subj))
    return list(reversed(filled))


def main() -> int:
    all_faults = faults(ROOT / "data" / "faults.ttl") + faults(ROOT / "data" / "faults-1.2.ttl")
    failed = 0
    for fid, lessons, subject in all_faults:
        for sid in lessons:
            needle = INDIRECT.get(f"{fid}:{sid}", INDIRECT.get(fid, subject.split(":", 1)[1] if subject else ""))
            path = RESULTS / f"{sid}.json"
            if not path.exists():
                print(f"??   {fid} {sid}: no results file (run check_shapes.py)")
                failed += 1
                continue
            r = json.loads(path.read_text(encoding="utf-8"))
            hit = any(needle in (x["focusNode"] or "") or needle in (x["value"] or "") or needle in (x["message"] or "")
                      for x in r.get("results", []))
            mark = "ok  " if hit else "MISS"
            failed += not hit
            print(f"{mark} {fid} -> {sid:4} {needle}")
    print(f"\n{len(all_faults)} faults; {failed} lesson references not confirmed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
