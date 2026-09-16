# Notices, attribution and provenance

## What is in this repository, and who owns it

Everything committed here — the shapes, the explanations, the diagrams, the
faults file, the build scripts and the course document — was written for this
project and is copyright © 2026 Peter Winstanley, released under the MIT
License in [LICENSE](LICENSE).

The dataset in `data/` is the [SPARQL course](https://github.com/pwin/SPARQL_Course)'s
Bookshop Trail, by the same author under the same licence, copied here
unchanged so that this repository stands on its own. The two files this
course adds, `data/faults.ttl` and `data/faults-1.2.ttl`, are written for this
project; the two combined "faulty" files are the SPARQL course's files with
those appended.

No third-party text, data or code is copied into this repository.

## The dataset is fiction

**The places are real. Everything else is invented.** The
[SPARQL course's NOTICE](https://github.com/pwin/SPARQL_Course/blob/main/NOTICE.md)
sets this out in full. The same applies to the additions here: Newtown and
Brecon in `faults.ttl` are real Welsh towns with their real coordinates, and
the bookshops, works, authors, publishers, events, sources and claims added
alongside them are invented.

> Any resemblance between a bookshop, publisher, author or book in this dataset
> and a real one is coincidental. Names were chosen to sound plausible for
> their setting, and with a plausible name in a real town some collision is
> statistically inevitable; none is intended, and nothing here is a statement
> about any real business or person. If you find a collision that troubles
> you, open an issue and it will be renamed.

The faults are faults on purpose. Nothing in `faults.ttl` is a claim about any
place or person; a latitude north of the pole is there to be caught by
`sh:maxInclusive 90`.

## Vocabularies referenced

The shapes use terms from published vocabularies by IRI and do not copy their
definitions.

| Vocabulary | Publisher |
|---|---|
| SHACL (`sh:`), including the SHACL-AF and SHACL 1.2 terms | W3C |
| RDF, RDFS, OWL, SKOS, PROV-O | W3C |
| GeoSPARQL (`geo:`, `sf:`) | Open Geospatial Consortium |
| Dublin Core Terms (`dct:`) | DCMI |
| WGS84 Geo Positioning (`wgs84:`) | W3C |
| schema.org (`schema:`, used in s43's rule) | W3C Schema.org Community Group |

Instance IRIs use `https://example.org/`, which RFC 6761 reserves for
documentation and examples.

## Tools used, and not redistributed

Nothing under `scripts/` bundles a third-party package. `npm install --prefix
scripts` fetches two from the npm registry, under their own licences:

| Package | What for | Licence |
|---|---|---|
| [`shacl-wasm-node`](https://www.npmjs.com/package/shacl-wasm-node) | the SHACL engine, the same WebAssembly build the Turtle Editor Viewer runs | MIT or Apache-2.0 |
| [`n3`](https://www.npmjs.com/package/n3) | parsing the Turtle before it reaches the engine, as the editor does | MIT |

`scripts/compare_pyshacl.py` uses [pySHACL](https://github.com/RDFLib/pySHACL)
and [rdflib](https://github.com/RDFLib/rdflib) if they are installed (Apache-2.0
and BSD-3-Clause respectively); neither is needed for the course.

The **Turtle Editor Viewer** at <https://semantechs.co.uk/turtle-editor-viewer/>
is used online and is not part of this repository. Its source is at
<https://github.com/pwin/turtle-editor-viewer>, MIT.

The **Semantechs name and mark** in `assets/` are excluded from the MIT grant.
