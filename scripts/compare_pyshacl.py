# -*- coding: utf-8 -*-
"""Run a few lessons through pySHACL as well, and show where the two reports
differ.

    pip install pyshacl
    python scripts/check_shapes.py          # the editor's engine, first
    python scripts/compare_pyshacl.py       # then this
    python scripts/compare_pyshacl.py s03 s14 s18

pySHACL is the most widely used validator outside a browser, and it does not
implement quite the same SHACL as the engine in the editor. The lessons
compared here are the ones where the course says the engine's behaviour is
its own: conformance with warnings, comparisons on xsd:gYear, ?message, and
the property validators that run per value. Everything is printed; nothing
here fails a build, because a difference is the point.

rdflib does not read RDF 1.2 directional literals (@ar--rtl), so the data is
loaded with the direction stripped; the affected literals are labels, and no
compared lesson constrains them.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import catalogue  # noqa: E402,F401
from shapecat import CATALOGUE, DATA  # noqa: E402

DEFAULT = ["s03", "s05", "s14", "s18", "s32", "s41", "s53", "s57"]
SH = "http://www.w3.org/ns/shacl#"
_DIR = re.compile(r"(@[a-zA-Z]+(?:-[a-zA-Z0-9]+)*)--(?:ltr|rtl)\b")


def load(path: Path):
    from rdflib import Graph
    text = _DIR.sub(r"\1", path.read_text(encoding="utf-8"))
    return Graph().parse(data=text, format="turtle")


def pyshacl_report(lesson):
    from pyshacl import validate
    from rdflib import Namespace
    data = load(DATA / lesson.data)
    shapes = load(ROOT / "build" / "shapes" / f"{lesson.sid}.ttl")
    inference = {"none": "none", "rdfs": "rdfs"}.get(lesson.inference, "none")
    conforms, graph, _ = validate(data, shacl_graph=shapes, advanced=True, inference=inference,
                                  allow_warnings=False)
    sh = Namespace(SH)
    counts = Counter()
    focus = set()
    for r in graph.subjects(sh.resultSeverity, None):
        sev = str(graph.value(r, sh.resultSeverity)).split("#")[1]
        counts[sev] += 1
        f = graph.value(r, sh.focusNode)
        if f is not None:
            focus.add(str(f).split("/")[-1])
    return conforms, counts, focus


def main() -> int:
    wanted = [a.lower() for a in sys.argv[1:]] or DEFAULT
    by_id = {l.sid: l for l in CATALOGUE}
    print(f"{'lesson':7} {'engine in the editor':40} {'pySHACL':40}")
    for sid in wanted:
        l = by_id[sid]
        ours_path = ROOT / "build" / "results" / f"{sid}.json"
        if not ours_path.exists():
            print(f"{sid:7} run check_shapes.py first")
            continue
        ours = json.loads(ours_path.read_text(encoding="utf-8"))
        oc = ours["counts"]
        ours_line = f"conforms={ours['conforms']} V{oc['Violation']} W{oc['Warning']} I{oc['Info']}"
        try:
            conforms, counts, focus = pyshacl_report(l)
            py_line = f"conforms={conforms} V{counts['Violation']} W{counts['Warning']} I{counts['Info']}"
        except Exception as e:  # pySHACL refused the shapes or the data
            py_line = "error: " + str(e).splitlines()[0][:60]
        print(f"{sid:7} {ours_line:40} {py_line:40} {l.title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
