# -*- coding: utf-8 -*-
"""FEATURES.md: every SHACL term the course demonstrates, and where.

    python scripts/features.py          # writes FEATURES.md, prints the gaps

The index is built by scanning the shapes of every lesson for sh: terms, so
it cannot disagree with them. TERMS lists the vocabulary the course means to
cover, grouped as the specifications group it; a term in TERMS with no lesson
is printed as a gap, and a term in the shapes that TERMS does not know is
printed too, so the list stays complete in both directions.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import catalogue  # noqa: E402,F401
import specs  # noqa: E402
from shapecat import CATALOGUE, REPO, DECLARE  # noqa: E402

# group -> [(term, spec key or None)]
TERMS = [
    ("Shapes and targets", [
        ("sh:NodeShape", "nodeShapes"), ("sh:PropertyShape", "propertyShapes"), ("sh:property", "property"),
        ("sh:path", "propertyShapes"), ("sh:targetClass", "targetClass"), ("sh:targetNode", "targetNode"),
        ("sh:targetSubjectsOf", "targetSubjectsOf"), ("sh:targetObjectsOf", "targetObjectsOf"),
        ("sh:target", "afTargets"), ("sh:SPARQLTarget", "afSparqlTarget"), ("sh:SPARQLTargetType", "afTargetType"),
        ("sh:targetWhere", "c12targetWhere"), ("sh:shape", "c12shape"), ("sh:ShapeClass", "c12ShapeClass"),
        ("sh:severity", "severity"), ("sh:Violation", "severity"), ("sh:Warning", "severity"), ("sh:Info", "severity"),
        ("sh:message", "message"), ("sh:deactivated", "deactivated"),
    ]),
    ("Property paths", [
        ("sh:inversePath", "pathInverse"), ("sh:alternativePath", "pathAlternative"),
        ("sh:zeroOrMorePath", "pathZeroOrMore"), ("sh:oneOrMorePath", "pathOneOrMore"),
        ("sh:zeroOrOnePath", "pathZeroOrOne"),
    ]),
    ("Value type, cardinality, range", [
        ("sh:class", "class"), ("sh:datatype", "datatype"), ("sh:nodeKind", "nodeKind"),
        ("sh:IRI", "nodeKind"), ("sh:Literal", "nodeKind"), ("sh:BlankNode", "nodeKind"), ("sh:BlankNodeOrIRI", "nodeKind"),
        ("sh:minCount", "minCount"), ("sh:maxCount", "maxCount"),
        ("sh:minInclusive", "minInclusive"), ("sh:maxInclusive", "range"),
        ("sh:minExclusive", "range"), ("sh:maxExclusive", "range"),
    ]),
    ("Strings and languages", [
        ("sh:minLength", "strings"), ("sh:maxLength", "strings"), ("sh:pattern", "pattern"), ("sh:flags", "pattern"),
        ("sh:languageIn", "languageIn"), ("sh:uniqueLang", "uniqueLang"), ("sh:singleLine", "c12singleLine"),
    ]),
    ("Property pairs", [
        ("sh:equals", "equals"), ("sh:disjoint", "disjoint"), ("sh:lessThan", "lessThan"),
        ("sh:lessThanOrEquals", "lessThanOrEquals"),
    ]),
    ("Logic and shape-based", [
        ("sh:not", "not"), ("sh:and", "and"), ("sh:or", "or"), ("sh:xone", "xone"), ("sh:node", "node"),
        ("sh:qualifiedValueShape", "qualified"), ("sh:qualifiedMinCount", "qualified"), ("sh:qualifiedMaxCount", "qualified"),
        ("sh:closed", "closed"), ("sh:ignoredProperties", "closed"), ("sh:hasValue", "hasValue"), ("sh:in", "in"),
        ("sh:memberShape", "c12lists"), ("sh:minListLength", "c12lists"),
        ("sh:reifierShape", "c12reifier"), ("sh:reificationRequired", "c12reifier"),
        ("sh:uniqueValuesFor", "c12uniqueValuesFor"),
    ]),
    ("SPARQL-based constraints and components", [
        ("sh:sparql", "sparql"), ("sh:select", "sparqlSyntax"), ("sh:ask", "askValidator"),
        ("sh:prefixes", "prefixes"), ("sh:declare", "prefixes"), ("sh:prefix", "prefixes"), ("sh:namespace", "prefixes"),
        ("sh:ConstraintComponent", "components"), ("sh:parameter", "parameters"), ("sh:optional", "parameters"),
        ("sh:labelTemplate", "labelTemplate"), ("sh:validator", "validators"),
        ("sh:nodeValidator", "validators"), ("sh:propertyValidator", "validators"),
        ("sh:SPARQLAskValidator", "askValidator"), ("sh:SPARQLSelectValidator", "selectValidator"),
        ("sh:SPARQLFunction", "afSparqlFunction"), ("sh:returnType", "afFunctions"),
    ]),
    ("Rules and node expressions", [
        ("sh:rule", "afRules"), ("sh:TripleRule", "afTripleRule"), ("sh:SPARQLRule", "afSparqlRule"),
        ("sh:subject", "afTripleRule"), ("sh:predicate", "afTripleRule"), ("sh:object", "afTripleRule"),
        ("sh:construct", "afSparqlRule"), ("sh:condition", "afCondition"), ("sh:order", "afOrder"),
        ("sh:this", "afFocusExpr"), ("sh:filterShape", "afFilterShape"), ("sh:nodes", "afFilterShape"),
        ("sh:union", "afUnion"), ("sh:intersection", "afIntersection"),
    ]),
    ("Non-validating and report vocabulary", [
        ("sh:name", "nonValidating"), ("sh:description", "nonValidating"), ("sh:group", "nonValidating"), ("sh:PropertyGroup", "nonValidating"),
        ("sh:ValidationReport", "report"), ("sh:ValidationResult", "result"), ("sh:conforms", "conforms"),
        ("sh:result", "report"), ("sh:focusNode", "result"), ("sh:resultPath", "resultPath"),
        ("sh:value", "resultValue"), ("sh:resultSeverity", "resultSeverity"), ("sh:resultMessage", "resultMessage"),
        ("sh:sourceShape", "sourceShape"), ("sh:sourceConstraintComponent", "result"),
    ]),
]

_TERM = re.compile(r"(?<![A-Za-z0-9_])sh:[A-Za-z][A-Za-z0-9]*")
_STR = re.compile(r"\"\"\".*?\"\"\"|\"(?:[^\"\\]|\\.)*\"", re.S)
_COMMENT = re.compile("#[^" + chr(10) + "]*")

# Terms that appear only inside a rule's or constraint's parameters and mean
# something else, or that are used as ordinary vocabulary rather than taught.
IGNORE = {"sh:Target"}


def terms_in(lesson) -> set:
    text = lesson.body + (chr(10) + DECLARE if lesson.declare else "")
    # Report vocabulary appears in the companion queries and in the strings
    # that hold SPARQL; count both, since the lesson is about them.
    for q in lesson.queries:
        text += chr(10) + q.text
    found = set(_TERM.findall(_COMMENT.sub(" ", text)))
    # Terms inside the SPARQL strings (e.g. $shapesGraph) are not sh: terms.
    return {t for t in found if t not in IGNORE}


def main() -> None:
    where: dict[str, list] = {}
    for l in CATALOGUE:
        for t in terms_in(l):
            where.setdefault(t, []).append(l)
    known = {t for _, items in TERMS for t, _ in items}
    lines = ["# Features", "",
             "Every SHACL term the course demonstrates, and the lessons that demonstrate it. "
             "Generated by `python scripts/features.py` from the shapes themselves, so it cannot "
             "disagree with them. Each term links to the section of the standard that defines it, "
             "and each lesson to its file.", ""]
    total = 0
    for group, items in TERMS:
        lines.append(f"## {group}")
        lines.append("")
        lines.append("| Term | Defined in | Lessons |")
        lines.append("|---|---|---|")
        for term, key in items:
            lessons = where.get(term, [])
            total += bool(lessons)
            label, url = specs.SECTIONS[key] if key else ("", "")
            spec = f"[{label}]({url})" if key else ""
            refs = ", ".join(f"[{l.sid}](shapes/{l.module}/{l.filename})" for l in lessons) or "*(no lesson yet)*"
            lines.append(f"| `{term}` | {spec} | {refs} |")
        lines.append("")
    extra = sorted(t for t in where if t not in known)
    if extra:
        lines.append("## Also used")
        lines.append("")
        lines.append("Terms the shapes use that the table above does not list.")
        lines.append("")
        for t in extra:
            refs = ", ".join(f"[{l.sid}](shapes/{l.module}/{l.filename})" for l in where[t])
            lines.append(f"- `{t}`: {refs}")
        lines.append("")
    (ROOT / "FEATURES.md").write_text(chr(10).join(lines), encoding="utf-8", newline=chr(10))
    gaps = [t for _, items in TERMS for t, _ in items if t not in where]
    print(f"FEATURES.md: {total} of {len(known)} terms demonstrated")
    if gaps:
        print("no lesson for: " + ", ".join(gaps))
    if extra:
        print("used but not catalogued: " + ", ".join(extra))


if __name__ == "__main__":
    main()
