# -*- coding: utf-8 -*-
"""Flag wording in the lesson texts that does not belong in this course.

    python scripts/lint_prose.py            # every lesson
    python scripts/lint_prose.py s20 s44    # just these

The course's prose is meant to read like the SPARQL course's: short
declarative sentences, concrete nouns, few adverbs. This lists the words and
turns of phrase that drift from that, with the lesson and field they occur
in, so they can be rewritten. It is advisory; nothing here fails a build.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import catalogue  # noqa: E402,F401
from shapecat import CATALOGUE, MODULE_INFO  # noqa: E402

WORDS = [
    "honest", "vendored", "genuinely", "plainly", "quietly", "crucially", "robust", "nuanced",
    "delve", "leverage", "seamless", "worth noting", "worth knowing", "in earnest", "elegant",
    "simply", "merely", "essentially", "arguably", "importantly", "interestingly", "notably",
    "of course", "needless to say", "it turns out", "the beauty of", "the point is",
    "not just", "not merely", "not only", "at its core", "in essence", "in other words",
    "let's", "we'll", "you'll", "dangerous", "surprise", "confident", "tell,", "the tell",
]
PATTERNS = [
    (re.compile(r"—"), "em dash (use -- in file text)"),
    (re.compile(r"\bThat is what\b"), "rhetorical closer"),
    (re.compile(r"\bThat is the\b [a-z]+ (of|about)\b"), "rhetorical closer"),
    (re.compile(r"\bnot an? \w+[,;.] (it|but) (is|a)\b", re.I), "'not X, it is Y' framing"),
    (re.compile(r"\b(\w+), (\w+) and (\w+) rows\b"), "triplet for rhythm"),
    (re.compile(r"!\s"), "exclamation"),
]


def check(sid: str, field: str, text: str, out: list) -> None:
    low = text.lower()
    for w in WORDS:
        for m in re.finditer(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low):
            start = max(0, m.start() - 40)
            out.append((sid, field, w, text[start:m.end() + 40].replace("\n", " ")))
    for pat, label in PATTERNS:
        for m in pat.finditer(text):
            start = max(0, m.start() - 40)
            out.append((sid, field, label, text[start:m.end() + 40].replace("\n", " ")))


def main() -> int:
    wanted = {a.lower() for a in sys.argv[1:]}
    out: list = []
    for l in CATALOGUE:
        if wanted and l.sid not in wanted:
            continue
        check(l.sid, "title", l.title, out)
        check(l.sid, "asks", l.asks, out)
        check(l.sid, "how", l.how, out)
        check(l.sid, "diagram", l.diagram, out)
        check(l.sid, "notes", l.notes, out)
        check(l.sid, "tryit", l.tryit, out)
        for i, item in enumerate(l.learn):
            check(l.sid, f"learn[{i}]", item, out)
        check(l.sid, "body", l.body, out)
    if not wanted:
        for module, (title, blurb) in MODULE_INFO.items():
            check(module, "blurb", blurb, out)
    for sid, field, what, ctx in out:
        print(f"{sid:24} {field:9} {what:28} ...{ctx}...")
    print(f"\n{len(out)} flags")
    return 0


if __name__ == "__main__":
    main()
