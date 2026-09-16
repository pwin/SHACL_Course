# Module 04 · Shapes inside shapes, and logic

A constraint can hand a value to another shape. sh:node, sh:not, sh:and, sh:or and sh:xone are all built on that idea, as are qualified value shapes ('at least one of the values is a ...'), closed shapes that reject any property not listed, and shapes that refer to themselves.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL §4.7.1 sh:node](https://www.w3.org/TR/shacl/#NodeConstraintComponent)
- [SHACL §4.7.2 sh:property](https://www.w3.org/TR/shacl/#PropertyConstraintComponent)
- [SHACL §4.6 Logical Constraint Components](https://www.w3.org/TR/shacl/#core-components-logical)
- [SHACL §4.6.1 sh:not](https://www.w3.org/TR/shacl/#NotConstraintComponent)
- [SHACL §4.6.2 sh:and](https://www.w3.org/TR/shacl/#AndConstraintComponent)
- [SHACL §4.6.3 sh:or](https://www.w3.org/TR/shacl/#OrConstraintComponent)
- [SHACL §4.6.4 sh:xone](https://www.w3.org/TR/shacl/#XoneConstraintComponent)
- [SHACL §4.7.3 sh:qualifiedValueShape](https://www.w3.org/TR/shacl/#QualifiedValueShapeConstraintComponent)
- [SHACL §4.8.1 sh:closed, sh:ignoredProperties](https://www.w3.org/TR/shacl/#ClosedConstraintComponent)
- [SHACL §3.4.3 Handling of Recursive Shapes](https://www.w3.org/TR/shacl/#shapes-recursion)
- [SHACL §3.7 Value Nodes](https://www.w3.org/TR/shacl/#value-nodes)

| Lesson | Checks | Data |
|---|---|---|
| [s24 A shape for the value](s24-a-shape-for-the-value.ttl) | A work's publisher is a well-formed publisher; a stock record's shop is a well-formed shop -- typed or not. | `bookshop-trail-faulty.ttl` |
| [s25 Not](s25-not.ttl) | A bookshop is not a publisher, a settlement is not a shop, and nobody specialises in 'Literature'. | `bookshop-trail-faulty.ttl` |
| [s26 Or, and, exactly one](s26-or-and-exactly-one.ttl) | A work has an ISBN or predates them; a place is exactly one kind of place; a shop is named and located. | `bookshop-trail-faulty.ttl` |
| [s27 Closed shapes](s27-closed-shapes.ttl) | A bookshop has no properties other than the ones listed, and the typo bs:foundedIn is caught. | `bookshop-trail-faulty.ttl` |
| [s28 Some of the values](s28-some-of-the-values.ttl) | A shop is in exactly one country; every country contains a book town; no council area contains two. | `bookshop-trail-faulty.ttl` |
| [s29 A shape that refers to itself](s29-a-shape-that-refers-to-itself.ttl) | A place conforms if every place above it conforms -- and what that finds, and what it cannot. | `bookshop-trail-faulty.ttl` |
