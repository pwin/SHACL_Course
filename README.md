<img src="assets/semantechs-logo.png" alt="Semantechs" width="72" align="left" hspace="12">

# The Bookshop Trail — a SHACL course

*A Semantechs teaching resource.*

<br clear="left">

Seventy shapes graphs that take a beginner from `sh:minCount 1` to SPARQL
constraints, custom constraint components, SHACL-AF rules and the parts of
SHACL 1.2 that run today — on the [SPARQL course](https://github.com/pwin/SPARQL_Course)'s
dataset, in the same browser editor, with the report each lesson produces
printed beside it.

The courses are one package. The [SPARQL course](https://www.semantechs.co.uk/SPARQL_Course/)
asks the Bookshop Trail questions and gets tables back; this one says what
well-formed Bookshop Trail data looks like and gets a report of everywhere the
data falls short; and the **[ontology course](https://www.semantechs.co.uk/Ontology_Course/)**
builds the vocabulary both of them use, from the words in a brief to an OWL 2
DL schema a reasoner has agreed with. They share the data, the editor and the
house style, and each points at the others where a query, a shape and an axiom
are three ways of saying the same thing: `q28`, `s20`, `o52`. This course is
hosted at <https://www.semantechs.co.uk/SHACL_Course/>.

Everything here runs in one environment:

| Environment | What it is | Where it comes from |
|---|---|---|
| **Turtle Editor Viewer** | Browser editor with a SHACL panel. The engine is a WebAssembly build of the [`shacl` validator](https://github.com/pwin/SHACL_Engine): SHACL Core, SHACL-SPARQL, SHACL-AF rules, RDF 1.2 data, RDFS inference. Nothing you load leaves the page. | **[semantechs.co.uk/turtle-editor-viewer](https://semantechs.co.uk/turtle-editor-viewer/)** — used online, nothing to install |

The same engine runs from the command line, and the course's own checker uses
it that way: `scripts/validate.mjs` (Node, `npm install shacl-wasm-node`),
`pip install shacl` for Python, `cargo install` for the native binary. All of
them give the report the browser gives.

Every lesson has been **run through the engine** and its report compared with
what the lesson says it should find. Where the engine's behaviour is its own —
a comparison it cannot make, a feature it reads and ignores — the lesson says
so, and module 12 has the table.

---

## Start here

Open the editor:

**<https://semantechs.co.uk/turtle-editor-viewer/>**

Then:

1. **Choose File** → `data/04-bookshops.ttl` in the first tab.
2. Press **+** for a second tab and load `shapes/01-first-shapes/s01-every-bookshop-has-a-name.ttl` into it.
3. Switch back to the data tab, pick the shapes tab in the **Shapes** dropdown, press **Validate**.

Or skip the file-picking: this link opens the editor with both already loaded.

<https://semantechs.co.uk/turtle-editor-viewer/?dot=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSHACL_Course%2Fmain%2Fdata%2F04-bookshops.ttl&shapes=https%3A%2F%2Fraw.githubusercontent.com%2Fpwin%2FSHACL_Course%2Fmain%2Fshapes%2F01-first-shapes%2Fs01-every-bookshop-has-a-name.ttl>

The report says *Conforms, 2 shapes*. Delete one shop's `rdfs:label` line in
the data tab and press Validate again: one row, naming the shop. That is the
whole loop, and every lesson is a variation of it.

There is a single-page edition of the course too — [docs/index.html](docs/index.html)
— with every shapes graph, its explanation, and the report the engine produced
for it.

Then read [`shapes/00-the-lab/`](shapes/00-the-lab/) — twenty minutes on the
validator panel, the Inference dropdown and the report — and start on
[`shapes/01-first-shapes/`](shapes/01-first-shapes/).

---

## One click into the editor

The Turtle Editor Viewer accepts three parameters: `?dot=<url>` loads the
data, `&shapes=<url>` opens a shapes graph in its own tab already selected for
validation, and `&inference=rules` presets the Inference dropdown. Every lesson
file carries a **LOAD IT** line built that way, and every lesson in the course
document has an **Open in the editor** button.

```
https://semantechs.co.uk/turtle-editor-viewer/?dot=<data url>&shapes=<shapes url>&inference=none|rdfs|rules|rules-iterated
```

`raw.githubusercontent.com` sends `Access-Control-Allow-Origin: *`, so the
editor can fetch the files from this repository. `./scripts/open-editor.ps1 s20`
builds the link for a lesson and opens it; `-List` shows every lesson.

The course document's **Copy shapes** button puts the shapes on your clipboard
with a four-line comment at the top saying which lesson it is, what it checks
and which data file it needs — the same header the SPARQL course's **Copy
query** gives.

---

## The data

**The Bookshop Trail** is the SPARQL course's dataset, unchanged: a fictional
network of independent bookshops in real British towns, with real coordinates
and invented everything else. The [SPARQL course's README](https://github.com/pwin/SPARQL_Course#the-data)
describes it; the short version is 33 shops, 74 works, 32 authors, 59 events,
a SKOS genre tree, a place hierarchy of uneven depth, and a trail with two
shops you cannot walk to.

The clean data conforms to nearly every shape in this course, which is no use
for teaching validation. So this course adds one file:

- **`data/faults.ttl`** — thirty-six deliberate mistakes, numbered F01 to
  F36, each commented with the lesson that catches it: a shop with no name, a
  shop in two towns, an ISBN with the wrong check digit, an author who died
  before he was born, two council areas inside each other, a founding-year
  claim with no source. Real Welsh towns with their real coordinates, and the
  faults in the other columns.

It is appended to the clean data to make the files lessons point at:

```
data/
  01-vocabulary.ttl .. 11-bng-geometry.ttl   the SPARQL course's files, byte for byte
  bookshop-trail-1.1.ttl                     files 01-09: most lessons use this
  bookshop-trail-1.2.ttl                     files 01-10: the RDF 1.2 annotations, for module 08
  faults.ttl                                 added here: the numbered faults
  faults-1.2.ttl                             added here: four more, in annotation syntax
  bookshop-trail-faulty.ttl                  1.1 + faults
  bookshop-trail-faulty-1.2.ttl              1.2 + faults + faults-1.2
```

Where a lesson reports something on the *clean* data — six shops without a
website, a translation with no translator, three council areas with no Welsh
name, a lecture given by an author who had died — that is a fact about the
dataset, and the lesson says so and usually reports it as a warning. Several
of those are the SPARQL course's own lessons seen from the other side: q16's
four towns with no bookshop are s21's four warnings.

---

## The course

Each lesson is a `.ttl` file whose header carries the whole lesson: what it
checks, how it works, an ASCII diagram of the mechanism, what to take away,
the data file and inference mode it needs, a link that loads it, the sections
of the standard it is defined by, and the report the engine produced. Read the
file; do not just run it.

| Module | | |
|---|---|---|
| [00](shapes/00-the-lab/) | **The lab** | the editor's validator: two tabs, the Shapes and Inference dropdowns, reading the report, the report as RDF |
| [01](shapes/01-first-shapes/) | First shapes | targets, property shapes, `sh:minCount`, severities and messages, `sh:deactivated`, the four targets, implicit class targets, and the shape that checks nothing |
| [02](shapes/02-value-constraints/) | What a value may be | `sh:datatype`, `sh:nodeKind`, `sh:class`, ranges, strings and patterns, languages, `sh:in`, property pairs — and what `xsd:gYear` does to a comparison |
| [03](shapes/03-property-paths/) | **Property paths in shapes** | sequence, inverse, alternative, `*`, `+`, `?` — and the fixed chain that misses twenty shops |
| [04](shapes/04-shapes-and-logic/) | Shapes inside shapes, and logic | `sh:node`, `sh:not`, `sh:and`/`sh:or`/`sh:xone`, closed shapes, qualified value shapes, a recursive shape |
| [05](shapes/05-sparql-constraints/) | **Targets and constraints in SPARQL** | `sh:sparql`, `$this` and `$PATH`, what a query puts in the result, SPARQL targets, pre-binding, aggregation, reachability, `$shapesGraph`, the report as a graph |
| [06](shapes/06-constraint-components/) | Your own constraint components | an ISBN check digit, parameterised SELECT validators, optional parameters, Core components written out |
| [07](shapes/07-rules/) | **SHACL rules** | triple rules and node expressions, SPARQL rules, conditions, order, one pass against a fixpoint, negation that goes stale — every inference made visible through the report |
| [08](shapes/08-shacl-1-2/) | SHACL 1.2 and RDF 1.2 | reifier shapes for the disputed founding dates, constraining the claims, the same fact modelled twice, `sh:shape`, and what this build does with the rest of 1.2 |
| [09](shapes/09-inference/) | Validating with inference | the RDFS closure: the event nobody typed, and the inference that hides an error |
| [10](shapes/10-debugging/) | **Debugging shapes** | the shape that finds nothing, the shape that flags everything, naming shapes, shapes that check nothing |
| [11](shapes/11-putting-it-together/) | **Putting it together** | the whole trail in one shapes graph (the answer key), shapes as questions, report to issues, a rule set, a challenge |
| [12](shapes/12-beyond-this-engine/) | Beyond this engine *(reference)* | SHACL functions, target types, and the table of what the engine runs, refuses or silently ignores; pySHACL measured beside it |

Everything runs in the browser. Modules 07 and 11's rule lessons need the
**Inference** dropdown set to *rules* (or *rules, iterated* for s51), module
09 needs *RDFS*, and the LOAD IT link sets it in each case. Module 08 uses the
RDF 1.2 edition of the data.

### Finding a feature

**[FEATURES.md](FEATURES.md)** lists every SHACL term the course demonstrates
— 113 of them, from `sh:targetClass` to `sh:reifierShape` — and which lessons
demonstrate it, each linked to the section of the specification that defines
it. It is generated by scanning the shapes, so it cannot disagree with them,
and it doubles as the coverage report: `python scripts/features.py` prints
anything in the catalogue with no lesson against it.

### Suggested order

> 00 → 01 → 02 (s10, s12, s14) → 03 (s20, s22) → 04 (s24, s27, s28) →
> **05 in full** → 06 (s39) → **07 in full** → 10 → 11

Module 05 is where SHACL stops being a checklist and becomes a query language
with a report attached, and module 07 is where it starts inferring; the course
is arranged to reach both quickly. Module 08 reads best after the SPARQL
course's module 11 on RDF 1.2, module 09 after its module 18 on inference, and
module 12 is reference.

### The two courses, side by side

Lessons cite the SPARQL course's queries by number. The ones that come up most:

| The shape | The query |
|---|---|
| s20, the fixed chain that misses twenty shops | q28, why a fixed-length chain gets the wrong answer |
| s21, towns with no bookshop | q16 |
| s14, comparing years through `STR()` | q07, q13, the `xsd:gYear` trap |
| s30, nothing contains itself; the cycle of influence | q34 |
| s36, the shops you cannot walk to | q31, q32 |
| s38, s66, the report as a graph | q88, a validation report as RDF |
| s47, s67, stock value as a rule | q21 |
| s50, s51, `bs:within` closed by a rule: 186 pairs | module 18, the same 186 from a reasoner and from `bs:within+` |
| s53 to s55, the disputed founding dates | q61 to q68 |
| s59, the inference that hides an error | q143, the inference nobody wanted |

---

## The engine

The editor's validator is [`shacl`](https://github.com/pwin/SHACL_Engine), a
Rust engine compiled to WebAssembly, version 0.2.0 at the time of writing. It
passes the W3C SHACL 1.0 and 1.2 test suites, reads RDF 1.2 data, runs
SHACL-SPARQL and SHACL-AF rules, and refuses `SERVICE` inside a shapes graph.

The **Inference** dropdown beside **Shapes** selects what is materialised
before validation:

| | |
|---|---|
| *none* | SHACL as the specification defines it |
| *RDFS* | the RDFS closure of the data: subclass, subproperty, domain, range |
| *rules* | the shapes graph's `sh:rule`s, one pass, as SHACL-AF defines |
| *rules, iterated* | repeated to a fixpoint, at most ten rounds |

A validator's only output is its report, so module 07 shows its inferences the
only way it can: a shape at Info severity that reports each inferred triple.

### Running it yourself

```powershell
npm install --prefix scripts          # once: shacl-wasm-node and n3
node scripts/validate.mjs --data data/bookshop-trail-faulty.ttl `
                          --shapes shapes/01-first-shapes/s02-reading-a-violation.ttl
node scripts/validate.mjs --data data/bookshop-trail-1.1.ttl `
                          --shapes shapes/07-rules/s51-to-a-fixpoint.ttl --inference rules-iterated
node scripts/validate.mjs ... --format turtle > report.ttl
```

`validate.mjs` does what the editor does before it calls the engine — names
the nested property shapes so a result can say `bt:BookshopShape › property 2`,
and renders compound paths as `^bs:heldAt` or `(bs:connectsTo | ^bs:connectsTo)`
— so its output matches the browser's row for row.

### What it does with each feature

[Module 12's README](shapes/12-beyond-this-engine/README.md) has the full
table, measured. The short version:

| | |
|---|---|
| **runs** | all of SHACL Core, SHACL-SPARQL constraints and components, SPARQL targets, `$shapesGraph`, SHACL-AF triple and SPARQL rules with conditions and order, RDFS inference, and from 1.2: `sh:ShapeClass`, `sh:targetWhere`, `sh:shape`, `sh:reifierShape`, `sh:singleLine`, the list constraints |
| **runs, with a difference** | comparisons on `xsd:gYear` fail every value (s14); SELECT property validators run per value (s42); recursive shapes treat an in-progress check as passing (s29) |
| **error** | SHACL functions, `sh:expression`, `sh:nodeKind sh:TripleTerm`, `MINUS`/`VALUES`/`SERVICE` under pre-binding, SPARQL-RL |
| **silent** | `sh:SPARQLTargetType`, `sh:uniqueValuesFor`, `sh:resultAnnotation` |

The last row is the one to know: a feature that is read and ignored looks like
conformance. Lessons s09, s60 and s70 are about noticing.

---

## Verification

The course does not take its own word for anything.

```powershell
python scripts/check_shapes.py             # every lesson, through the engine, compared with its expectation
python scripts/check_shapes.py s20 s28     # just these
python scripts/check_shapes.py --show s64  # print the result rows
python scripts/check_faults.py             # every numbered fault is caught by the lesson that names it
python scripts/compare_pyshacl.py          # eight lessons through pySHACL as well, side by side
python scripts/lint_prose.py               # wording that does not belong in the headers
```

Each lesson declares what its report must contain — conformance, counts per
severity, focus nodes that must and must not appear, messages — and the run
fails on any engine error the lesson did not ask for and on any expectation
that does not hold. The measured headline is written into each lesson's
`REPORTS` line, and the rows into the course document, so what you read is
what the engine said.

### Things the checking found

Worth knowing before you write shapes for this engine:

| | |
|---|---|
| `sh:minInclusive`, `sh:lessThan` on `xsd:gYear` | every value reported; the comparison cannot be made. `xsd:date` compares. Cast through `STR()` in SPARQL (s14) |
| `YEAR()` on an `xsd:date` | unbound; use `SUBSTR(STR(?date), 1, 4)` (s31) |
| SPARQL has no `%` | `x - 10 * FLOOR(x / 10)` (s39) |
| a SELECT property validator | runs once per value, so it never runs on a node with no values; count with a node validator (s42) |
| an aggregate projected as `?value` | reported without the value (s35) |
| `?message` in a SPARQL constraint, `{?var}` in a message | ignored; use `sh:message` with `{$value}` (s32) |
| `sh:severity` inside `sh:sparql` | SHACL 1.2, and honoured here; pySHACL takes the shape's severity (s32) |
| a SPARQL *target* whose query does not parse | selects nothing, silently; the same query in `sh:sparql` is an error (s33) |
| `sh:minCount` written on a node shape | silently ignored (s63) |
| `rdfs:subClassOf` in the shapes graph | not followed; SHACL reads the hierarchy from the data graph (s61) |
| an RDF 1.2 annotation followed by `;` inside `[ ... ]` | the editor's parser objects; write the annotated constraint on a named shape (s57) |
| several `sh:message` values | joined into one string (s05) |

---

## Rebuilding

The lessons are generated from a catalogue, so that a shapes graph and its
explanation cannot drift apart. Edit the catalogue, not the `.ttl`.

```powershell
python scripts/build_faults.py      # data/faults.ttl and the two faulty editions
python scripts/check_shapes.py      # run every lesson; writes build/reports.json and build/results/
python scripts/check_faults.py      # the answer key
python scripts/build_shapes.py      # shapes/**/*.ttl and the module READMEs
python scripts/features.py          # FEATURES.md, and the coverage report
python scripts/build_docs.py        # docs/index.html
python scripts/check_links.py       # every standards link, anchors included
```

| Script | |
|---|---|
| `shapecat.py` | the catalogue: one `Lesson` per shapes graph, the `.ttl` writer, the editor links |
| `lessons_first.py`, `lessons_values.py`, `lessons_paths.py`, `lessons_logic.py`, `lessons_sparql.py`, `lessons_components.py`, `lessons_rules.py`, `lessons_12.py`, `lessons_inference.py`, `lessons_debugging.py`, `lessons_together.py`, `lessons_beyond.py` | the 70 lessons and their explanations, one file per module |
| `catalogue.py` | imports them in course order |
| `specs.py` | the sections of the standards each lesson and module is defined by, and the reading list |
| `build_faults.py` | the numbered faults and the faulty editions of the data |
| `validate.mjs`, `package.json` | the engine from Node: one lesson, or a batch for the checker |
| `check_shapes.py`, `check_faults.py`, `compare_pyshacl.py` | the verification |
| `build_shapes.py`, `build_docs.py`, `features.py`, `engine_matrix.py` | the files, the document, the index, the engine table |
| `lint_prose.py` | flags wording that does not belong in the headers |
| `open-editor.ps1` | builds a `?dot=&shapes=&inference=` link and opens the hosted editor |
| `check_links.py` | fetches every standards document and checks each anchor |

---

## The standards

Everything this course teaches is defined somewhere, usually in one short
section of one document. Start with the
[SHACL Recommendation](https://www.w3.org/TR/shacl/); section 4 is the constraint
component reference you will open most often, and Appendix D shows each Core
component as the SPARQL it is equivalent to.

**The specifications**

- [Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/) — the 2017 Recommendation. Modules 01 to 06 and 10 are defined here.
- [SHACL Advanced Features](https://www.w3.org/TR/shacl-af/) — a Working Group Note: SPARQL-based targets, node expressions, SHACL rules. Module 07.
- [SHACL 1.2 Core](https://www.w3.org/TR/shacl12-core/) — a Working Draft, still changing. Reifier shapes, `sh:targetWhere`, `sh:ShapeClass`, per-constraint severities, the new string and list components. Module 08 says which the engine runs.
- [SHACL 1.2 SPARQL Extensions](https://www.w3.org/TR/shacl12-sparql/) — the 1.2 edition of SHACL-SPARQL, including `sh:severity` on a constraint and select expressions.
- [SHACL 1.2 Node Expressions](https://www.w3.org/TR/shacl12-node-expr/) — a library of expression functions with a namespace of its own; not implemented by the engine, and module 12 says where it is heading.
- [SHACL 1.2 Rules (SPARQL-RL)](https://www.w3.org/TR/shacl12-rules/) — a rule language with stratified negation, not implemented; s52 reads it for what it fixes.

**The data model and the query language**

- [SPARQL 1.2 Query Language](https://www.w3.org/TR/sparql12-query/) — everything inside `sh:select`, `sh:ask` and `sh:construct`. The SPARQL course covers it in full.
- [RDF 1.2 Concepts and Abstract Syntax](https://www.w3.org/TR/rdf12-concepts/) — triple terms and reifiers, which module 08 validates.
- [RDF 1.2 Turtle](https://www.w3.org/TR/rdf12-turtle/) — the syntax of every file here, including the `{| ... |}` annotations.

Each module README links the particular sections it is defined by, and every
lesson header names two. `python scripts/check_links.py` fetches each document
and checks that every anchor still lands on its heading.

---

## Licence

MIT — see [LICENSE](LICENSE). Copyright © 2026 Peter Winstanley.

The **Semantechs name and mark** in `assets/` are excluded from that grant, as
trademarks normally are: the MIT licence covers the course, not the branding.
Fork and reuse the material freely; replace the mark with your own.

[NOTICE.md](NOTICE.md) covers what is and is not in this repository: the
fiction disclaimer, the data's origin in the SPARQL course, the vocabularies
referenced by IRI, and the third-party packages the scripts install rather than
redistribute.
