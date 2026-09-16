# Module 05 · Targets and constraints in SPARQL

Some conditions cannot be written with the Core components: a join between two nodes, an arithmetic comparison, a path that must not lead back to its start. SHACL-SPARQL lets a SELECT query decide, with $this bound to the node under test. The module also writes targets in SPARQL, sets out what pre-binding forbids, and queries the report as the RDF graph it is.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL §5 SPARQL-based Constraints](https://www.w3.org/TR/shacl/#sparql-constraints)
- [SHACL §5.2 Syntax of SPARQL-based Constraints](https://www.w3.org/TR/shacl/#sparql-constraints-syntax)
- [SHACL §5.2.1 Prefix Declarations for SPARQL Queries](https://www.w3.org/TR/shacl/#sparql-prefixes)
- [SHACL §5.3.1 Pre-bound Variables in SPARQL Constraints](https://www.w3.org/TR/shacl/#sparql-constraints-prebound)
- [SHACL §5.3.2 Mapping of Solution Bindings to Result Properties](https://www.w3.org/TR/shacl/#sparql-constraints-variables)
- [SHACL Appendix A Pre-binding of Variables in SPARQL Queries](https://www.w3.org/TR/shacl/#pre-binding)
- [SHACL-AF §3.1 SPARQL-based Targets](https://www.w3.org/TR/shacl-af/#SPARQLTarget)
- [SHACL 1.2 Core §3.1.3.6 Where Targets (sh:targetWhere)](https://www.w3.org/TR/shacl12-core/#targetWhere)
- [SHACL §3.6 Validation Report](https://www.w3.org/TR/shacl/#validation-report)
- [SHACL §1.6 Relationship between SHACL and SPARQL](https://www.w3.org/TR/shacl/#shacl-sparql)

| Lesson | Checks | Data |
|---|---|---|
| [s30 The constraint you cannot write in Core](s30-the-constraint-you-cannot-write-in-core.ttl) | Nothing contains itself: no place, genre, publisher or author is above itself in its own hierarchy. | `bookshop-trail-faulty.ttl` |
| [s31 A join, an arithmetic comparison, and $PATH](s31-a-join-an-arithmetic-comparison-and-path.ttl) | A shelf price is at most twice the recommended price; no work predates its author; an event does not feature the dead. | `bookshop-trail-faulty.ttl` |
| [s32 What a query can put in the result](s32-what-a-query-can-put-in-the-result.ttl) | The six shops without a website again, with the path and the value chosen by the query, and what this engine does with ?message. | `bookshop-trail-1.1.ttl` |
| [s33 A target written in SPARQL](s33-a-target-written-in-sparql.ttl) | Every book town has a bookshop; a shop with a cafe has room for one; a city has more than one shop. | `bookshop-trail-faulty.ttl` |
| [s34 What pre-binding forbids](s34-what-pre-binding-forbids.ttl) | Works nobody stocks -- written the way pre-binding allows, with the three ways it does not. | `bookshop-trail-1.1.ttl` |
| [s35 Aggregation in a constraint](s35-aggregation-in-a-constraint.ttl) | No shop holds more than a hundred copies in total, and no shop has held more than three events. | `bookshop-trail-1.1.ttl` |
| [s36 Reachability as a constraint](s36-reachability-as-a-constraint.ttl) | Every shop can be walked to from The Inkwell -- and two cannot, by design. | `bookshop-trail-1.1.ttl` |
| [s37 Two graphs, one constraint](s37-two-graphs-one-constraint.ttl) | An event's kind is one the shapes graph lists -- with the list kept as data in the shapes graph, not in a sh:in. | `bookshop-trail-faulty.ttl` |
| [s38 The report is a graph](s38-the-report-is-a-graph.ttl) | A short shapes graph that finds a dozen faults, and three queries over its report. | `bookshop-trail-faulty.ttl` |
