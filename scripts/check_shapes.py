# -*- coding: utf-8 -*-
"""Validate every lesson with the engine the editor runs, and compare.

    python scripts/check_shapes.py              # every lesson
    python scripts/check_shapes.py s07 s08      # just these
    python scripts/check_shapes.py --show s07   # print the result rows
    python scripts/check_shapes.py --module 05-sparql-constraints

Each lesson's shapes are written to build/shapes/, validated against the data
file it names, under the inference mode it names, by scripts/validate.mjs --
which is the WebAssembly build of the engine inside the Turtle Editor
Viewer. The measured report is compared with the lesson's `expect`, and the
run fails on any engine error the lesson did not ask for, and on any
expectation that does not hold.

Two files come out of it:

    build/results/<sid>.json     the result rows, for the course document
    build/reports.json           the one-line REPORTS summary per lesson,
                                 which build_shapes.py writes into each header
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import catalogue  # noqa: E402  (registers every lesson)
from shapecat import CATALOGUE, DATA  # noqa: E402

BUILD = ROOT / "build"
NODE = "node"


def summary_line(r: dict) -> str:
    if not r.get("ok"):
        return "engine error -- " + r.get("error", "").splitlines()[0][:110]
    c = r["counts"]
    plural = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    verdict = "conforms" if r["conforms"] else "does not conform"
    return (f"{verdict} -- {plural(c['Violation'], 'violation')}, {plural(c['Warning'], 'warning')}, "
            f"{c['Info']} info; {plural(r['shapeCount'], 'shape')}")


def check_expectation(lesson, r: dict) -> list[str]:
    """Every way the measured report disagrees with the lesson."""
    e = lesson.expect
    problems = []
    if not r.get("ok"):
        err = r.get("error", "")
        if e.get("error") and e["error"] in err:
            return []
        return [f"engine error: {err.splitlines()[0][:160]}"]
    if e.get("error"):
        problems.append(f"expected an engine error containing {e['error']!r}, but it ran")
    c = r["counts"]
    for key, name in (("violations", "Violation"), ("warnings", "Warning"), ("infos", "Info")):
        if key in e and c[name] != e[key]:
            problems.append(f"{key}: expected {e[key]}, got {c[name]}")
    for key, name in (("min_violations", "Violation"), ("min_warnings", "Warning"), ("min_infos", "Info")):
        if key in e and c[name] < e[key]:
            problems.append(f"{key}: expected at least {e[key]}, got {c[name]}")
    if "conforms" in e and r["conforms"] != e["conforms"]:
        problems.append(f"conforms: expected {e['conforms']}, got {r['conforms']}")
    if "shapes" in e and r["shapeCount"] != e["shapes"]:
        problems.append(f"shapes: expected {e['shapes']}, got {r['shapeCount']}")
    focus = {x["focusNode"] for x in r["results"]}
    for name in e.get("focus", []):
        if not any(name in f for f in focus):
            problems.append(f"no result for focus node containing {name!r}")
    for name in e.get("nofocus", []):
        if any(name in f for f in focus):
            problems.append(f"unexpected result for focus node containing {name!r}")
    for text in e.get("messages", []):
        if not any(text in x["message"] for x in r["results"]):
            problems.append(f"no result whose message contains {text!r}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="lesson ids, e.g. s07")
    ap.add_argument("--module", help="only lessons in this module folder")
    ap.add_argument("--show", action="store_true", help="print the result rows")
    ap.add_argument("--limit", type=int, default=40, help="rows to print with --show")
    args = ap.parse_args()

    lessons = list(CATALOGUE)
    if args.ids:
        wanted = {i.lower() for i in args.ids}
        lessons = [l for l in lessons if l.sid in wanted]
    if args.module:
        lessons = [l for l in lessons if l.module == args.module]
    if not lessons:
        print("no lessons matched")
        return 2

    shapes_dir = BUILD / "shapes"
    shapes_dir.mkdir(parents=True, exist_ok=True)
    (BUILD / "results").mkdir(parents=True, exist_ok=True)
    jobs = []
    for l in lessons:
        path = shapes_dir / f"{l.sid}.ttl"
        path.write_text(l.shapes_text, encoding="utf-8", newline="\n")
        jobs.append({"id": l.sid, "data": str(DATA / l.data), "shapes": str(path), "inference": l.inference})
    jobs_path = BUILD / "jobs.json"
    jobs_path.write_text(json.dumps(jobs), encoding="utf-8")
    out_path = BUILD / "results.json"
    proc = subprocess.run([NODE, str(ROOT / "scripts" / "validate.mjs"), "--batch", str(jobs_path),
                           "--out", str(out_path)], capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        print(proc.stderr)
        return 1
    results = {r["id"]: r for r in json.loads(out_path.read_text(encoding="utf-8"))}

    reports_path = BUILD / "reports.json"
    reports = json.loads(reports_path.read_text(encoding="utf-8")) if reports_path.exists() else {}

    failed = 0
    for l in lessons:
        r = results[l.sid]
        problems = check_expectation(l, r)
        line = summary_line(r)
        reports[l.sid] = line
        (BUILD / "results" / f"{l.sid}.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
        mark = "FAIL" if problems else "ok  "
        failed += bool(problems)
        print(f"{mark} {l.sid} {l.title[:48]:48} {line}")
        for p in problems:
            print(f"        ! {p}")
        if args.show and r.get("ok"):
            for x in r["results"][: args.limit]:
                print(f"        {x['severity'][:4]} {x['focusNode']:34} {(x['path'] or ''):28} "
                      f"{(x['value'] or '')[:28]:28} {x['message'][:70]}   [{x['sourceShape']}]")
            if len(r["results"]) > args.limit:
                print(f"        ... {len(r['results']) - args.limit} more")
    reports_path.write_text(json.dumps(reports, indent=1, sort_keys=True), encoding="utf-8")
    print(f"\n{len(lessons) - failed} of {len(lessons)} lessons as expected")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
