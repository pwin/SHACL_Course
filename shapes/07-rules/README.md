# Module 07 · SHACL rules

The Advanced Features note lets a shape infer triples as well as check them. A triple rule builds one triple from node expressions; a SPARQL rule runs a CONSTRUCT. Rules run before validation, so a result can depend on an inferred triple. The editor's Inference dropdown switches them on. A validator's only output is its report, so each lesson here uses a shape to make its inferences visible.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

Lessons marked with an inference mode need the **Inference** dropdown set to that mode before validating; the LOAD IT link sets it for you.

**In the standards.** The sections this module is defined by:

- [SHACL-AF §8 SHACL Rules](https://www.w3.org/TR/shacl-af/#rules)
- [SHACL-AF §8.2 General Syntax of SHACL Rules](https://www.w3.org/TR/shacl-af/#rules-syntax)
- [SHACL-AF §8.5 Triple Rules](https://www.w3.org/TR/shacl-af/#TripleRule)
- [SHACL-AF §8.6 SPARQL Rules](https://www.w3.org/TR/shacl-af/#SPARQLRule)
- [SHACL-AF §8.2.1 sh:condition](https://www.w3.org/TR/shacl-af/#condition)
- [SHACL-AF §8.2.2 sh:order](https://www.w3.org/TR/shacl-af/#rules-order)
- [SHACL-AF §8.2.3 sh:deactivated](https://www.w3.org/TR/shacl-af/#deactivated)
- [SHACL-AF §8.4 General Execution Instructions for SHACL Rules](https://www.w3.org/TR/shacl-af/#rules-execution)
- [SHACL-AF §6 Node Expressions](https://www.w3.org/TR/shacl-af/#node-expressions)
- [SHACL-AF §6.5 Path Expressions](https://www.w3.org/TR/shacl-af/#node-expressions-path)
- [SHACL-AF §6.3 Filter Shape Expressions](https://www.w3.org/TR/shacl-af/#node-expressions-filter-shape)
- [SHACL-AF §6.7 Union Expressions](https://www.w3.org/TR/shacl-af/#union)
- [SHACL-AF §6.6 Intersection Expressions](https://www.w3.org/TR/shacl-af/#intersection)
- [SHACL-AF §8.3 The sh:Rules Entailment Regime](https://www.w3.org/TR/shacl-af/#Rules)
- [SHACL 1.2 Rules §3 SPARQL-RL](https://www.w3.org/TR/shacl12-rules/#overview)
- [SHACL 1.2 Rules §4.4 Stratification](https://www.w3.org/TR/shacl12-rules/#stratification)

| Lesson | Checks | Data |
|---|---|---|
| [s43 Your first rule](s43-your-first-rule.ttl) | Every bookshop is also a schema:BookStore -- inferred, then made visible in the report. | `04-bookshops.ttl · *rules*` |
| [s44 A value copied along a path](s44-a-value-copied-along-a-path.ttl) | Each shop gets a bs:townName: the label of the town it is in -- every label, in every language. | `bookshop-trail-1.1.ttl · *rules*` |
| [s45 Filtering the values](s45-filtering-the-values.ttl) | Each shop gets a bs:inCountry: the one place above it that is a country. | `bookshop-trail-1.1.ttl · *rules*` |
| [s46 Union and intersection](s46-union-and-intersection.ttl) | Everyone who worked on a work, and the stocked works that match a shop's specialism. | `bookshop-trail-1.1.ttl · *rules*` |
| [s47 A rule written in SPARQL](s47-a-rule-written-in-sparql.ttl) | The value of each stock line, and a flag on every work without an ISBN. | `bookshop-trail-1.1.ttl · *rules*` |
| [s48 Conditions, and a rule switched off](s48-conditions-and-a-rule-switched-off.ttl) | Shops with a cafe get an amenity; shops without a website get a status; a third rule is present and inactive. | `bookshop-trail-1.1.ttl · *rules*` |
| [s49 Order, and rules that feed rules](s49-order-and-rules-that-feed-rules.ttl) | A shop's country, then the country's name from it -- and the same second rule placed where it sees nothing. | `bookshop-trail-1.1.ttl · *rules*` |
| [s50 One pass](s50-one-pass.ttl) | bs:within made transitive by a rule, run once: how far a single pass reaches. | `bookshop-trail-1.1.ttl · *rules*` |
| [s51 To a fixpoint](s51-to-a-fixpoint.ttl) | The same rule, repeated until nothing new appears: the full closure, and the count the SPARQL course measured. | `bookshop-trail-1.1.ttl · *rules-iterated*` |
| [s52 Negation that goes stale](s52-negation-that-goes-stale.ttl) | Mark the shops without a website, then give every such shop a placeholder website -- and see the mark outlive its reason. | `bookshop-trail-1.1.ttl · *rules*` |
