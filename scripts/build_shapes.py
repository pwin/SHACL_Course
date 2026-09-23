# -*- coding: utf-8 -*-
"""Write shapes/**/*.ttl and the module READMEs from the catalogue.

    python scripts/build_shapes.py

Run check_shapes.py first if you want the REPORTS line in each header to be
current: it is read from build/reports.json.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import catalogue  # noqa: E402
import engine_matrix  # noqa: E402
import specs  # noqa: E402
from shapecat import CATALOGUE, MODULE_INFO, SHAPES, EDITOR_BASE, RAW_BASE  # noqa: E402
from urllib.parse import quote  # noqa: E402

BUILD = ROOT / "build"


def module_readme(module: str, lessons: list) -> str:
    title, blurb = MODULE_INFO[module]
    num = module.split("-")[0]
    lines = [f"# Module {num} · {title}", "", blurb, ""]
    lines.append("Each `.ttl` file carries its own explanation: what it checks, how it works, "
                 "a diagram of the mechanism, and what to take away. Read the header, then open "
                 "the LOAD IT link -- it puts the data in one tab and the shapes in another, and "
                 "the Validate button does the rest.")
    lines.append("")
    inferred = [l for l in lessons if l.inference != "none"]
    if inferred:
        lines.append("Lessons marked with an inference mode need the **Inference** dropdown set "
                     "to that mode before validating; the LOAD IT link sets it for you.")
        lines.append("")
    lines.append("**In the standards.** The sections this module is defined by:")
    lines.append("")
    for label, url in specs.for_module(module):
        lines.append(f"- [{label}]({url})")
    lines.append("")
    lines.append("| Lesson | Checks | Data |")
    lines.append("|---|---|---|")
    for l in lessons:
        data = l.data + ("" if l.inference == "none" else f" · *{l.inference}*")
        lines.append(f"| [{l.sid} {l.title}]({l.filename}) | {l.asks} | `{data}` |")
    lines.append("")
    if module == "12-beyond-this-engine":
        lines += [
            "## What this engine does with each feature",
            "",
            "Measured against `shacl-wasm-node` 0.2.0, the build the Turtle Editor Viewer ships, while "
            "this course was written. *runs* means the lesson shows it; *error* means the engine refuses "
            "and says why; *silent* means the feature is read and ignored, and the report looks the same "
            "as if it had passed -- the case to test for before relying on anything in that row.",
            "",
            engine_matrix.markdown_table(),
            "",
            "## Other validators",
            "",
            "Three other validators are in common use, and each implements a different SHACL. None of "
            "this is a criticism of any of them; it is the reason to check a shapes graph on the engine "
            "that will run it.",
            "",
            "| | This engine | pySHACL | TopBraid SHACL API | Apache Jena SHACL |",
            "|---|---|---|---|---|",
            "| SHACL Core | yes | yes | yes | yes |",
            "| SHACL-SPARQL constraints and components | yes | yes | yes | yes |",
            "| SPARQL-based targets | yes | yes | yes | yes |",
            "| SHACL-AF rules | yes (`sh:rule`, one pass or iterated) | yes (`--advanced`, `--inplace`) | yes (`shaclinfer`) | no |",
            "| SHACL functions | no, error | yes | yes | no |",
            "| SHACL-JS | no | yes | yes | no |",
            "| Warning or Info breaks `sh:conforms` | no (0.2.0); yes (0.3.0) | yes, unless `--allow-warnings` | not measured here | not measured here |",
            "| `sh:severity` on a `sh:sparql` block (SHACL 1.2) | yes | no: the shape's severity | not measured here | not measured here |",
            "| RDF 1.2 data (annotations, triple terms) | yes | no: rdflib does not parse it | no | yes |",
            "| Runs in the browser | yes | no | no | no |",
            "",
            "### Measured against pySHACL",
            "",
            "`python scripts/compare_pyshacl.py` runs eight of this course's lessons through pySHACL 0.40 "
            "as well and prints both reports side by side. The directional literals in the data "
            "(`@ar--rtl`) are stripped first, because rdflib does not read them. What it shows with "
            "the engine at 0.3.2:",
            "",
            "| Lesson | The engine in the editor | pySHACL | Why |",
            "|---|---|---|---|",
            "| s03 six shops without a website | does not conform, 6 warnings | the same | the specification's default counts warnings against conformance; this engine did not until 0.3.0 |",
            "| s05 messages and severities | 7 violations, 1 warning, 7 infos | the same | severity does not inherit from node shape to property shape on either |",
            "| s14 comparing years | 2 violations | 2 violations | pySHACL cannot compare the gYear either; the STR cast works on both |",
            "| s18 comparing two properties | 10 violations, 58 infos | error | `sh:lessThanOrEquals` on gYear values stops pySHACL with an exception |",
            "| s32 what a query can put in the result | 12 infos | 12 violations | `sh:severity` inside `sh:sparql` is SHACL 1.2; pySHACL takes the shape's severity |",
            "| s41 a required language | does not conform, 3 warnings | the same | the component agrees, and since 0.3.0 so does the verdict |",
            "| s53, s57 SHACL 1.2 and RDF 1.2 | runs | error | rdflib does not parse the `{\\| ... \\|}` annotations in the 1.2 data |",
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    reports_path = BUILD / "reports.json"
    reports = json.loads(reports_path.read_text(encoding="utf-8")) if reports_path.exists() else {}
    for l in CATALOGUE:
        l.report = reports.get(l.sid, "")

    # Remove stale lesson files, keep hand-written READMEs (the lab's).
    for folder in SHAPES.iterdir() if SHAPES.exists() else []:
        if folder.is_dir():
            for f in folder.glob("s*.ttl"):
                f.unlink()

    by_module: dict[str, list] = {}
    for l in CATALOGUE:
        by_module.setdefault(l.module, []).append(l)
    count = 0
    for module, lessons in by_module.items():
        lessons.sort(key=lambda l: l.sort_key)
        folder = SHAPES / module
        folder.mkdir(parents=True, exist_ok=True)
        for l in lessons:
            l.path.write_text(l.text(), encoding="utf-8", newline="\n")
            count += 1
        (folder / "README.md").write_text(module_readme(module, lessons), encoding="utf-8", newline="\n")
    print(f"wrote {count} lessons in {len(by_module)} modules")


if __name__ == "__main__":
    main()
