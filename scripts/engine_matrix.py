# -*- coding: utf-8 -*-
"""What the engine in the editor does with each feature: the reference table
for module 12, drawn on by the module README and the course document.

Every row was measured against shacl-wasm-node 0.2.0, the build the Turtle
Editor Viewer ships, while this course was written. `status` is one of:

    runs      implemented; the lesson shows it
    partial   implemented with a difference from the specification worth knowing
    error     not implemented, and the engine says so
    silent    not implemented, and the engine says nothing: the feature is read and ignored
"""
from __future__ import annotations

ROWS = [
    # (feature, where defined, status, lesson, note)
    ("SHACL Core constraint components", "SHACL section 4", "runs", "s01-s29", "All of them, including sh:closed, sh:qualifiedValueShape and the property pair components."),
    ("Comparisons on xsd:gYear", "SHACL 4.3, 4.5", "partial", "s14, s18, s61", "Range and pair comparisons cannot compare gYear values and report every one. xsd:date compares as expected. Cast through STR() in a SPARQL constraint."),
    ("Recursive shapes", "SHACL 3.4.3", "partial", "s29", "Undefined by the specification. A check already in progress for the same node and shape is treated as passing, so a cycle in the data is not detected by recursion."),
    ("sh:severity on a node shape", "SHACL 2.1.4", "runs", "s05", "Applies to constraints on the node shape only; property shapes take their own. As specified."),
    ("Warnings, infos and sh:conforms", "SHACL 3.6.1.1", "partial", "s03", "Only sh:Violation counts against conformance in this build. The specification's default disallows Warning and Info too; engine 0.3.0 follows it."),
    ("Several sh:message values", "SHACL 2.1.5", "partial", "s05", "Joined into one string rather than reported as separate values."),
    ("sh:sparql constraints, $this, $PATH, ?value, ?path", "SHACL section 5", "runs", "s30-s38", ""),
    ("?message in a SPARQL constraint", "SHACL 5.3.2", "silent", "s32", "Ignored; sh:message is used. {?var} templates are not filled either."),
    ("$shapesGraph, $currentShape", "SHACL 5.3.1", "runs", "s37", ""),
    ("sh:severity on a sh:sparql constraint", "SHACL 1.2 SPARQL 3.2", "runs", "s32", "A 1.2 addition. SHACL 1.0 allows severity on shapes only, and a 1.0 validator such as pySHACL reports such rows as violations."),
    ("MINUS, VALUES, SERVICE under pre-binding", "SHACL Appendix A", "error", "s34", "Refused with a message naming the construct. SERVICE is refused in constraints, targets and rules alike; it remains allowed in queries run from the SPARQL panel."),
    ("A SPARQL target whose query does not parse", "SHACL-AF 3.1", "silent", "s33", "Selects nothing. The same query in sh:sparql is an error."),
    ("An aggregate projected as ?value", "SHACL 5.3.2", "silent", "s35", "The row is reported; sh:value is not set."),
    ("Custom constraint components, ASK and SELECT validators", "SHACL section 6", "runs", "s39-s42", ""),
    ("SELECT property validators", "SHACL 6.2.3.1", "partial", "s41, s42", "Run once per value node rather than once per focus node, so a validator that counts or tests for absence does not run when the path has no values. Use a node validator to count."),
    ("Parameters in sh:message ({$param})", "SHACL 6.2.2", "silent", "s40", "Left as written."),
    ("sh:labelTemplate", "SHACL 6.2.2", "silent", "s40", "Accepted; nothing in the report uses it."),
    ("SPARQL-based targets, sh:SPARQLTarget", "SHACL-AF 3.1", "runs", "s33", ""),
    ("SPARQL-based target types, sh:SPARQLTargetType", "SHACL-AF 3.2", "silent", "s70", "Compiled and counted; gives the shape no focus nodes."),
    ("Result annotations, sh:resultAnnotation", "SHACL-AF section 4", "silent", "", "Results appear without the annotation."),
    ("SHACL functions, sh:SPARQLFunction", "SHACL-AF section 5", "error", "s69", "'The custom function ... is not supported'."),
    ("Node expressions: sh:this, constants, [ sh:path ], filter shapes, sh:union, sh:intersection", "SHACL-AF section 6", "runs", "s43-s46", "Inside rules. Anything else is an error rather than an empty result."),
    ("Expression constraints, sh:expression", "SHACL-AF section 7", "error", "", "'unsupported node expression' for every form but sh:this."),
    ("Triple rules, SPARQL rules, sh:condition, sh:order, sh:deactivated", "SHACL-AF section 8", "runs", "s43-s52", "One pass as specified; 'rules, iterated' repeats to a fixpoint, up to ten rounds."),
    ("RDFS inference before validation", "SHACL 1.5", "runs", "s58, s59", "rdfs2, rdfs3, rdfs5, rdfs7, rdfs9, rdfs11. Opt-in."),
    ("sh:ShapeClass", "SHACL 1.2 Core 3.1.3.3", "runs", "s08", ""),
    ("sh:targetWhere", "SHACL 1.2 Core 3.1.3.6", "runs", "s33", ""),
    ("sh:shape in the data graph", "SHACL 1.2 Core 3.1.3.7", "runs", "s56", ""),
    ("sh:severity as an annotation on one constraint", "SHACL 1.2 Core 3.1.4", "silent", "s57", "The result takes the shape's severity. Engine 0.3.0 honours it."),
    ("sh:select as a target or node expression", "SHACL 1.2 SPARQL 6.1", "runs", "s33", "As a target. sh:values with sh:select is not enforced in this build."),
    ("sh:reifierShape", "SHACL 1.2 Core 7.8.5", "runs", "s53", ""),
    ("sh:reificationRequired", "SHACL 1.2 Core 7.8.5", "silent", "s53", "Parsed, not enforced. Engine 0.3.0 enforces it."),
    ("sh:nodeKind sh:TripleTerm", "SHACL 1.2 Core 7.1.3", "error", "", "'not a known node kind'."),
    ("sh:singleLine", "SHACL 1.2 Core 7.4.4", "runs", "s57", ""),
    ("List constraints: sh:memberShape, sh:minListLength, sh:maxListLength", "SHACL 1.2 Core 7.5", "runs", "s57", ""),
    ("sh:subsetOf", "SHACL 1.2 Core 7.6.3", "runs", "", "Measured on a small example; the dataset has no natural pair of properties for it."),
    ("sh:uniqueValuesFor", "SHACL 1.2 Core 7.9.5", "silent", "s70", "Duplicates pass."),
    ("sh:values, sh:defaultValue (derived values)", "SHACL 1.2 Node Expressions", "silent", "", "The property shape's other constraints see only asserted values."),
    ("The shnex: node expression library", "SHACL 1.2 Node Expressions section 4", "error", "", "Not implemented; the vocabulary changed between drafts in 2026."),
    ("SHACL 1.2 Rules (SPARQL-RL)", "SHACL 1.2 Rules", "error", "s52", "A different language from SHACL-AF rules; not implemented. s52 reads it for the stratification it adds."),
    ("SHACL-JS, the compact syntax", "SHACL-JS, SHACL Compact Syntax", "error", "", "Not implemented."),
    ("Named graphs in TriG or N-Quads data", "SHACL 3.2", "partial", "", "Merged into one data graph. A result does not say which graph its focus node came from."),
    ("Annotations after ';' inside [ ... ]", "RDF 1.2 Turtle", "partial", "s57", "The editor's Turtle parser wants an annotation to be the last item inside a blank node's brackets. Write the annotated constraint on a named shape."),
]

STATUS_LABEL = {"runs": "runs", "partial": "runs, with a difference", "error": "error", "silent": "silent"}


def markdown_table() -> str:
    lines = ["| Feature | Defined in | This build | Lesson | Note |", "|---|---|---|---|---|"]
    for feature, spec, status, lesson, note in ROWS:
        lines.append(f"| {feature} | {spec} | **{STATUS_LABEL[status]}** | {lesson} | {note} |")
    return "\n".join(lines)
