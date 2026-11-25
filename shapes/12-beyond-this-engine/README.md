# Module 12 · Beyond this engine

Reference rather than lesson. Validators differ in what they implement, and the SHACL 1.2 drafts are still changing. This module records what the engine in the editor does with each feature it does not implement -- an error for some, no output for others -- and where pySHACL, TopBraid and Jena differ from it.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL-AF section 5 SHACL Functions](https://www.w3.org/TR/shacl-af/#functions)
- [SHACL-AF 5.4 SPARQL-based Functions](https://www.w3.org/TR/shacl-af/#SPARQLFunction)
- [SHACL-AF 3.2 SPARQL-based Target Types](https://www.w3.org/TR/shacl-af/#SPARQLTargetType)
- [SHACL-AF section 4 Annotation Properties](https://www.w3.org/TR/shacl-af/#sparql-constraints-annotations)
- [SHACL-AF section 7 Expression Constraints](https://www.w3.org/TR/shacl-af/#ExpressionConstraintComponent)
- [SHACL 1.2 Node Expressions section 2 Getting started with Node Expressions](https://www.w3.org/TR/shacl12-node-expr/#getting-started)
- [SHACL 1.2 Node Expressions section 4 Node Expressions Library](https://www.w3.org/TR/shacl12-node-expr/#library)
- [SHACL 1.2 SPARQL section 6 SPARQL-based Node Expressions](https://www.w3.org/TR/shacl12-sparql/#sparql-node-expressions)
- [SHACL 1.2 SPARQL section 7 Declaring SPARQL Functions based on Node Expressions](https://www.w3.org/TR/shacl12-sparql/#sparql-functions)
- [SHACL 1.2 Core 7.9.5 sh:uniqueValuesFor](https://www.w3.org/TR/shacl12-core/#UniqueValuesForConstraintComponent)
- [SHACL 1.2 Core 7.5 List Constraint Components](https://www.w3.org/TR/shacl12-core/#core-components-list)
- [SHACL 1.2 Rules section 3 SPARQL-RL](https://www.w3.org/TR/shacl12-rules/#overview)
- [SHACL 1.2 Rules 3.4 Negation](https://www.w3.org/TR/shacl12-rules/#desc-negation)

| Lesson | Checks | Data |
|---|---|---|
| [s69 A function you cannot call](s69-a-function-you-cannot-call.ttl) | A SHACL function that turns a gYear into an integer -- declared, refused by this engine, and replaced by the same expression inline. | `bookshop-trail-1.1.ttl` |
| [s70 Targets the engine ignores](s70-targets-the-engine-ignores.ttl) | A SPARQL target type with a parameter, which this build reads and does nothing with, and sh:uniqueValuesFor, which runs only in the form the specification gives it. | `bookshop-trail-1.1.ttl` |

## What this engine does with each feature

Measured against `shacl-wasm-node` 0.2.0 when this course was written, and re-measured against `semops-wasm-node` 0.31.0, the SemOps System build the Turtle Editor Viewer ships. *runs* means the lesson shows it; *error* means the engine refuses and says why; *silent* means the feature is read and ignored, and the report looks the same as if it had passed -- the case to test for before relying on anything in that row. Where a row changed between builds, its note says what the earlier build did: an upgrade that moves a feature between columns is the reason to re-test one.

| Feature | Defined in | This build | Lesson | Note |
|---|---|---|---|---|
| SHACL Core constraint components | SHACL section 4 | **runs** | s01-s29 | All of them, including sh:closed, sh:qualifiedValueShape and the property pair components. |
| Comparisons on xsd:gYear | SHACL 4.3, 4.5 | **runs, with a difference** | s14, s18, s61 | Range and pair comparisons cannot compare gYear values and report every one. xsd:date compares as expected. Cast through STR() in a SPARQL constraint. |
| Recursive shapes | SHACL 3.4.3 | **runs, with a difference** | s29 | Undefined by the specification. A check already in progress for the same node and shape is treated as passing, so a cycle in the data is not detected by recursion. |
| sh:severity on a node shape | SHACL 2.1.4 | **runs** | s05 | Applies to constraints on the node shape only; property shapes take their own. As specified. |
| Warnings, infos and sh:conforms | SHACL 3.6.1.1 | **runs** | s03 | Violations, warnings and infos all count against conformance unless the report narrows it with sh:conformanceDisallows, as specified. Engine 0.2.0 counted violations only. |
| Several sh:message values | SHACL 2.1.5 | **runs, with a difference** | s05 | Joined into one string in the editor's result list. The report graph keeps them as separate sh:resultMessage values. |
| sh:sparql constraints, $this, $PATH, ?value, ?path | SHACL section 5 | **runs** | s30-s38 |  |
| ?message in a SPARQL constraint | SHACL 5.3.2 | **silent** | s32 | Ignored; sh:message is used. {?var} templates in it are filled from the row, which engine 0.2.0 left as written. |
| $shapesGraph, $currentShape | SHACL 5.3.1 | **runs** | s37 |  |
| sh:severity on a sh:sparql constraint | SHACL 1.2 SPARQL 3.2 | **runs** | s32 | A 1.2 addition. SHACL 1.0 allows severity on shapes only, and a 1.0 validator such as pySHACL reports such rows as violations. |
| MINUS, VALUES, SERVICE under pre-binding | SHACL Appendix A | **error** | s34 | Refused with a message naming the construct. SERVICE is refused in constraints, targets and rules alike; it remains allowed in queries run from the SPARQL panel. |
| A SPARQL target whose query does not parse | SHACL-AF 3.1 | **silent** | s33 | Selects nothing. The same query in sh:sparql is an error. |
| A computed ?value: an aggregate, BIND or STR() | SHACL 5.3.2 | **runs** | s35 | Reported as sh:value, as specified. Up to shacl-wasm-node 0.3.8 the row came without sh:value unless the computed term happened to occur in the data, while {?value} in sh:message still showed it. |
| Custom constraint components, ASK and SELECT validators | SHACL section 6 | **runs** | s39-s42 |  |
| SELECT property validators | SHACL 6.2.3.1 | **runs, with a difference** | s41, s42 | Run once per value node rather than once per focus node, so a validator that counts or tests for absence does not run when the path has no values. Use a node validator to count. |
| Parameters in sh:message ({$param}) | SHACL 6.2.2 | **runs** | s40 | Filled with the parameter's value. Engine 0.2.0 left them as written. |
| sh:labelTemplate | SHACL 6.2.2 | **silent** | s40 | Accepted; nothing in the report uses it. |
| SPARQL-based targets, sh:SPARQLTarget | SHACL-AF 3.1 | **runs** | s33 |  |
| SPARQL-based target types, sh:SPARQLTargetType | SHACL-AF 3.2 | **silent** | s70 | Compiled and counted; gives the shape no focus nodes. |
| Result annotations, sh:resultAnnotation | SHACL-AF section 4 | **silent** |  | Results appear without the annotation. |
| SHACL functions, sh:SPARQLFunction | SHACL-AF section 5 | **error** | s69 | 'The custom function ... is not supported'. |
| Node expressions: sh:this, constants, [ sh:path ], filter shapes, sh:union, sh:intersection | SHACL-AF section 6 | **runs** | s43-s46 | In rules, in sh:expression, and in sh:values, which engine 0.2.0 ignored. |
| Expression constraints, sh:expression | SHACL-AF section 7 | **runs** |  | A value node whose expression does not evaluate to true is reported. |
| Triple rules, SPARQL rules, sh:condition, sh:order, sh:deactivated | SHACL-AF section 8 | **runs** | s43-s52 | One pass as specified; 'rules, iterated' repeats to a fixpoint, up to ten rounds. |
| RDFS inference before validation | SHACL 1.5 | **runs** | s58, s59 | rdfs2, rdfs3, rdfs5, rdfs7, rdfs9, rdfs11. Opt-in. |
| sh:ShapeClass | SHACL 1.2 Core 3.1.3.3 | **runs** | s08 |  |
| sh:targetWhere | SHACL 1.2 Core 3.1.3.6 | **runs** | s33 |  |
| sh:shape in the data graph | SHACL 1.2 Core 3.1.3.7 | **runs** | s56 |  |
| sh:severity as an annotation on one constraint | SHACL 1.2 Core 3.1.4 | **runs** | s57 | That constraint's results take the annotated severity. Engine 0.2.0 read it and used the shape's. |
| sh:select as a target or node expression | SHACL 1.2 SPARQL 6.1 | **runs** | s33 | As a target, and inside sh:values. Engine 0.2.0 ran it as a target only. |
| sh:reifierShape | SHACL 1.2 Core 7.8.5 | **runs** | s53 |  |
| sh:reificationRequired | SHACL 1.2 Core 7.8.5 | **runs** | s53 | A value with no reifier is a violation. Engine 0.2.0 parsed it and let such values pass. |
| sh:nodeKind sh:TripleTerm | SHACL 1.2 Core 7.1.3 | **error** |  | 'not a known node kind'. |
| sh:singleLine | SHACL 1.2 Core 7.4.4 | **runs** | s57 |  |
| List constraints: sh:memberShape, sh:minListLength, sh:maxListLength | SHACL 1.2 Core 7.5 | **runs** | s57 |  |
| sh:subsetOf | SHACL 1.2 Core 7.6.3 | **runs** |  | Measured on a small example; the dataset has no natural pair of properties for it. |
| sh:uniqueValuesFor | SHACL 1.2 Core 7.9.5 | **runs** | s70 | On a node shape, naming the path whose values must differ across its focus nodes, as the 1.2 test suite writes it. Written on a property shape naming a class, the form this course first used, it is read and ignored. |
| sh:values (derived values) | SHACL 1.2 Node Expressions | **runs** |  | The node expression supplies the value nodes the path would have. Engine 0.2.0 ignored it, and the other constraints saw only asserted values. |
| sh:defaultValue | SHACL 1.2 Node Expressions | **silent** |  | The property shape's constraints see only asserted values. |
| The shnex: node expression library | SHACL 1.2 Node Expressions section 4 | **runs** |  | In the namespace of the current draft, http://www.w3.org/ns/shacl-node-expr#, measured with shnex:pathValues inside sh:values. The vocabulary changed between drafts in 2026, so check which one a shapes graph was written against. Engine 0.2.0 did not implement it. |
| SHACL 1.2 Rules (SPARQL-RL) | SHACL 1.2 Rules | **error** | s52 | A different language from SHACL-AF rules; not implemented. s52 reads it for the stratification it adds. |
| SHACL-JS, the compact syntax | SHACL-JS, SHACL Compact Syntax | **error** |  | Not implemented. |
| Named graphs in TriG or N-Quads data | SHACL 3.2 | **runs, with a difference** |  | Merged into one data graph. A result does not say which graph its focus node came from. |
| Annotations after ';' inside [ ... ] | RDF 1.2 Turtle | **runs, with a difference** | s57 | The editor's Turtle parser wants an annotation to be the last item inside a blank node's brackets. Write the annotated constraint on a named shape. |

## Other validators

Three other validators are in common use, and each implements a different SHACL. None of this is a criticism of any of them; it is the reason to check a shapes graph on the engine that will run it.

| | This engine | pySHACL | TopBraid SHACL API | Apache Jena SHACL |
|---|---|---|---|---|
| SHACL Core | yes | yes | yes | yes |
| SHACL-SPARQL constraints and components | yes | yes | yes | yes |
| SPARQL-based targets | yes | yes | yes | yes |
| SHACL-AF rules | yes (`sh:rule`, one pass or iterated) | yes (`--advanced`, `--inplace`) | yes (`shaclinfer`) | no |
| SHACL functions | no, error | yes | yes | no |
| SHACL-JS | no | yes | yes | no |
| Warning or Info breaks `sh:conforms` | no (0.2.0); yes (0.3.0) | yes, unless `--allow-warnings` | not measured here | not measured here |
| `sh:severity` on a `sh:sparql` block (SHACL 1.2) | yes | no: the shape's severity | not measured here | not measured here |
| RDF 1.2 data (annotations, triple terms) | yes | no: rdflib does not parse it | no | yes |
| Runs in the browser | yes | no | no | no |

### Measured against pySHACL

`python scripts/compare_pyshacl.py` runs eight of this course's lessons through pySHACL 0.40 as well and prints both reports side by side. The directional literals in the data (`@ar--rtl`) are stripped first, because rdflib does not read them. What it shows with the engine at shacl-wasm-node 0.3.8, and at semops-wasm-node 0.31.0, whose reports for these eight lessons are identical row for row:

| Lesson | The engine in the editor | pySHACL | Why |
|---|---|---|---|
| s03 six shops without a website | does not conform, 6 warnings | the same | the specification's default counts warnings against conformance; this engine did not until 0.3.0 |
| s05 messages and severities | 7 violations, 1 warning, 7 infos | the same | severity does not inherit from node shape to property shape on either |
| s14 comparing years | 2 violations | 2 violations | pySHACL cannot compare the gYear either; the STR cast works on both |
| s18 comparing two properties | 10 violations, 58 infos | error | `sh:lessThanOrEquals` on gYear values stops pySHACL with an exception |
| s32 what a query can put in the result | 12 infos | 12 violations | `sh:severity` inside `sh:sparql` is SHACL 1.2; pySHACL takes the shape's severity |
| s41 a required language | does not conform, 3 warnings | the same | the component agrees, and since 0.3.0 so does the verdict |
| s53, s57 SHACL 1.2 and RDF 1.2 | runs | error | rdflib does not parse the `{\| ... \|}` annotations in the 1.2 data |
