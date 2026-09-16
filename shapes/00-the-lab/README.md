# Module 00 · The lab

Twenty minutes on the tool before the first shape. Everything in this course runs in the **Turtle Editor Viewer**, used online at <https://semantechs.co.uk/turtle-editor-viewer/>. Nothing is installed and nothing you load leaves your browser: the parser, the SPARQL engine and the SHACL engine all run inside the page. The engine is a WebAssembly build of the same validator that runs from the command line as `shacl` and from Python as `pip install shacl`; the report you see in the browser is the report they would give.

If you did the SPARQL course, its [module 00](https://github.com/pwin/SPARQL_Course/tree/main/queries/00-the-lab) covers the editor's graph view, layout engines, reasoner and format conversion. This page covers the part that course only touched: the validator.

## Two tabs and a button

A validation needs two graphs: the data and the shapes. In the editor they are two tabs.

1. Open the editor. The first tab is the data tab. **Choose File** or **Load URL** to put a dataset in it -- `data/04-bookshops.ttl` is small enough to see whole.
2. Press **+** at the end of the tab strip to open a second tab, and load a shapes file into it. It takes the file's name.
3. Switch back to the **data** tab. Validation always checks the tab in front.
4. In the **Shapes** dropdown at the right of the SPARQL & SHACL panel's buttons, choose the shapes tab. It gets a small *shapes* badge.
5. Leave **Inference** at *none* unless the lesson says otherwise.
6. Press **Validate**. The first press also loads the engine, about a megabyte; after that it is instant.

Every lesson in this course has a **LOAD IT** link in its header that does steps 1 to 5 for you: it opens the editor with the data in the first tab, the shapes in a second tab already selected, and the Inference dropdown set. The link is built from three parameters --

```
?dot=<data url>&shapes=<shapes url>&inference=rules
```

-- and `scripts/open-editor.ps1` builds one for any lesson or any pair of files.

## Reading the report

The headline says **Conforms** or **Does not conform**, then the counts: violations, warnings, infos, and how many shapes were compiled. Under it, one row per result:

| Column | What it is | Where the specification defines it |
|---|---|---|
| Severity | `Violation` counts against conformance; `Warning` and `Info` do not | [§2.1.4](https://www.w3.org/TR/shacl/#severity) |
| Focus node | The node that was checked | [§3.6.2.1](https://www.w3.org/TR/shacl/#results-focus-node) |
| Path | The property the constraint is about; blank for a constraint on the node itself. A compound path is written out, as `^bs:heldAt` or `bs:within*` | [§3.6.2.2](https://www.w3.org/TR/shacl/#results-path) |
| Value | The offending value, where there is one. A count has none | [§3.6.2.3](https://www.w3.org/TR/shacl/#results-value) |
| Message | The shape's `sh:message` with `{$this}`, `{$path}` and `{$value}` filled in, or the constraint component's name | [§3.6.2.7](https://www.w3.org/TR/shacl/#results-message) |
| Shape | Which shape said so. A property shape written as `[ ... ]` has no name, and shows as `bt:BookshopShape › property 2` | [§3.6.2.4](https://www.w3.org/TR/shacl/#results-source-shape) |

Two things to know about the headline. **The shapes count is the number of shapes that compiled**, node shapes and property shapes together; if it is smaller than you expect, something did not compile as a shape (s63). And **Conforms means no violations were found**, which is also what it says when nothing was checked (s09). In this engine a warning or an info does not stop a report from conforming; the specification's own rule is stricter, and module 08 says how.

**Report as tab** opens the report itself as a new tab. It is an RDF graph -- one `sh:ValidationReport`, one `sh:ValidationResult` per row -- so the SPARQL panel can query it, the diagram can draw it, and **Export report** saves it as `validation-report.ttl`. Module 05's last lesson and module 11 are built on this. **Clear** puts the panel back.

## The Inference dropdown

Next to **Shapes** is **Inference**, and it says what the engine works out before it validates:

| Setting | What is validated | Used in |
|---|---|---|
| *none* | The data as written. SHACL as the specification defines it | modules 01 to 06, 08, 10 |
| *RDFS* | The RDFS closure of the data: subclass, subproperty, domain and range are followed first | module 09 |
| *rules* | The data plus what the shapes graph's SHACL-AF rules (`sh:rule`) infer, in one pass | module 07 |
| *rules, iterated* | The same, repeated until nothing new appears, at most ten rounds | s51 |

The text in the tab is never changed by any of these; the expanded graph lives only for the run. The inferred triples are not listed either -- a validator's only output is its report -- and module 07 shows the technique this course uses to see them: a shape at Info severity that reports each inferred triple as a row.

## The data

The dataset is the SPARQL course's [Bookshop Trail](https://github.com/pwin/SPARQL_Course#the-data), unchanged: real towns, real coordinates, and an invented network of independent bookshops, authors, publishers, books and events. Everything except the geography is fiction. The files in `data/` are the SPARQL course's files, byte for byte, plus two this course adds:

| File | What it is |
|---|---|
| `bookshop-trail-1.1.ttl` | The whole dataset, RDF 1.1. Most lessons use this |
| `bookshop-trail-1.2.ttl` | The same plus the RDF 1.2 annotations: disputed founding dates, attendance claims, stock as annotations. Module 08 |
| `04-bookshops.ttl` and the other numbered files | One subject area each, small enough for the graph view |
| `faults.ttl` | **Added here.** Thirty-six deliberate mistakes, numbered, each commented with the lesson that catches it |
| `bookshop-trail-faulty.ttl` | The 1.1 dataset with `faults.ttl` appended. What a lesson points at when it needs something to find |
| `bookshop-trail-faulty-1.2.ttl` | The 1.2 dataset with the faults, plus the four that need annotation syntax |

The clean data conforms to nearly everything in this course. Where a lesson reports something on the clean data -- six shops without a website, a translation with no translator, two shops you cannot walk to -- that is a fact about the dataset, and the lesson says so.

## Trying it before the first lesson

Open [s01](../01-first-shapes/s01-every-bookshop-has-a-name.ttl)'s LOAD IT link, press **Validate**: Conforms, 2 shapes, no rows. In the data tab, delete one shop's `rdfs:label` line and press **Validate** again: one row, naming the shop. Put the line back. That is the whole loop -- edit the data or the shapes, validate, read -- and every lesson from here on is a variation of it.

## Running it yourself

The same engine runs outside the browser, on the same files:

```powershell
npm install --prefix scripts                       # once: shacl-wasm-node and n3
node scripts/validate.mjs --data data/bookshop-trail-faulty.ttl `
                          --shapes shapes/01-first-shapes/s02-reading-a-violation.ttl
node scripts/validate.mjs --data data/bookshop-trail-1.1.ttl `
                          --shapes shapes/07-rules/s51-to-a-fixpoint.ttl --inference rules-iterated
node scripts/validate.mjs ... --format turtle > report.ttl      # the report as RDF
```

`scripts/validate.mjs` does what the editor does before it calls the engine -- names the nested property shapes, renders the compound paths -- so its output matches the browser's row for row. It is also what the course's own checker uses: `python scripts/check_shapes.py` validates every lesson and compares the report with what the lesson says it should be, and `python scripts/check_faults.py` confirms that every numbered fault is caught by the lesson that names it.

The native forms of the engine are `cargo install` from [github.com/pwin/SHACL_Engine](https://github.com/pwin/SHACL_Engine), `pip install shacl` for Python, and `npm install shacl-wasm-node` for Node. All four take the same inference modes.

## What is where

```
shapes/NN-module/sNN-title.ttl     one lesson: header, then the shapes graph
shapes/NN-module/README.md         the module's lessons, blurb and standards
data/                              the Bookshop Trail, clean and faulty
docs/index.html                    the whole course as one document, with the measured reports
FEATURES.md                        every SHACL term, and which lesson shows it
scripts/                           the catalogue the lessons are generated from, and the checkers
```

Start with [module 01](../01-first-shapes/).
