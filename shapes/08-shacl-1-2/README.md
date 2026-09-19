# Module 08 · SHACL 1.2 and RDF 1.2

The RDF 1.2 edition of the data has statements about statements: a shop with two founding dates, each claimed by a source. SHACL 1.2 can validate the claims themselves, target nodes by a shape rather than by a class, and declare a class that is its own shape. The module uses what the engine in the editor runs today and lists the parts of the 1.2 drafts it does not.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL 1.2 Core 7.8.5 sh:reifierShape, sh:reificationRequired](https://www.w3.org/TR/shacl12-core/#ReifierShapeConstraintComponent)
- [SHACL 1.2 Core 3.1.3.3 Implicit Class Targets and sh:ShapeClass](https://www.w3.org/TR/shacl12-core/#implicit-targetClass)
- [SHACL 1.2 Core 3.1.3.6 Where Targets (sh:targetWhere)](https://www.w3.org/TR/shacl12-core/#targetWhere)
- [SHACL 1.2 Core 3.1.3.7 Explicit shape targets (sh:shape)](https://www.w3.org/TR/shacl12-core/#explicit-shape-target)
- [SHACL 1.2 Core 3.1.4 Declaring the Severity of a Shape or Constraint](https://www.w3.org/TR/shacl12-core/#severity)
- [SHACL 1.2 Core 7.4.4 sh:singleLine](https://www.w3.org/TR/shacl12-core/#SingleLineConstraintComponent)
- [SHACL 1.2 Core 7.6.3 sh:subsetOf](https://www.w3.org/TR/shacl12-core/#SubsetOfConstraintComponent)
- [SHACL 1.2 Core 6.7.1.2 sh:conformanceDisallows](https://www.w3.org/TR/shacl12-core/#conformanceDisallows)
- [RDF 1.2 Concepts 2.2 Triple Terms and Reification](https://www.w3.org/TR/rdf12-concepts/#section-triple-terms)
- [RDF 1.2 Turtle 2.9 Reifying Triples](https://www.w3.org/TR/rdf12-turtle/#reifying-triples)

| Lesson | Checks | Data |
|---|---|---|
| [s53 Two founding dates](s53-two-founding-dates.ttl) | A shop has one founding year -- unless each year is a claim with a source, in which case it may have several. | `bookshop-trail-faulty-1.2.ttl` |
| [s54 Constraining the claims themselves](s54-constraining-the-claims-themselves.ttl) | Every claim names one statement and a real source, and a claim about a founding year is about a bookshop. | `bookshop-trail-faulty-1.2.ttl` |
| [s55 The same fact modelled twice](s55-the-same-fact-modelled-twice.ttl) | The RDF 1.1 stock records and the RDF 1.2 stock annotations agree on every count. | `bookshop-trail-faulty-1.2.ttl` |
| [s56 A node that names its own shape](s56-a-node-that-names-its-own-shape.ttl) | A shop that says in the data which shape it should conform to, and a shape with no other target. | `bookshop-trail-faulty.ttl` |
| [s57 New in 1.2 Core, and what this build does with it](s57-new-in-1.2-core-and-what-this-build-does-with-it.ttl) | Notices stay on one line; the vocabulary's union classes are lists of classes; and the 1.2 features this engine reads but does not enforce. | `bookshop-trail-faulty-1.2.ttl` |
