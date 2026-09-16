# Module 01 · First shapes

Everything here runs in the browser: the data in one tab, the shapes in another, then Validate. A shape has two halves. The target says which nodes to look at; the constraints say what must be true of them. The report lists each place the data falls short. This module makes that structure familiar, and teaches you to read one result in full before you write anything complicated.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL §2.1 Shapes](https://www.w3.org/TR/shacl/#shapes)
- [SHACL §2.1.3 Targets](https://www.w3.org/TR/shacl/#targets)
- [SHACL §2.1.3.2 sh:targetClass](https://www.w3.org/TR/shacl/#targetClass)
- [SHACL §2.1.3.1 sh:targetNode](https://www.w3.org/TR/shacl/#targetNode)
- [SHACL §2.1.3.4 sh:targetSubjectsOf](https://www.w3.org/TR/shacl/#targetSubjectsOf)
- [SHACL §2.1.3.5 sh:targetObjectsOf](https://www.w3.org/TR/shacl/#targetObjectsOf)
- [SHACL §2.1.3.3 Implicit Class Targets](https://www.w3.org/TR/shacl/#implicit-targetClass)
- [SHACL §2.3 Property Shapes](https://www.w3.org/TR/shacl/#property-shapes)
- [SHACL §4.2.1 sh:minCount](https://www.w3.org/TR/shacl/#MinCountConstraintComponent)
- [SHACL §4.2.2 sh:maxCount](https://www.w3.org/TR/shacl/#MaxCountConstraintComponent)
- [SHACL §2.1.4 Declaring the Severity of a Shape](https://www.w3.org/TR/shacl/#severity)
- [SHACL §2.1.5 Declaring Messages for a Shape](https://www.w3.org/TR/shacl/#message)
- [SHACL §2.1.6 Deactivating a Shape](https://www.w3.org/TR/shacl/#deactivated)
- [SHACL §3.6.2 Validation Result](https://www.w3.org/TR/shacl/#results-validation-result)
- [SHACL §3.5 Conformance Checking](https://www.w3.org/TR/shacl/#conformance-definition)

| Lesson | Checks | Data |
|---|---|---|
| [s01 Every bookshop has a name](s01-every-bookshop-has-a-name.ttl) | Every bs:Bookshop has at least one rdfs:label. | `04-bookshops.ttl` |
| [s02 Reading a violation](s02-reading-a-violation.ttl) | The same shape, on the faulty edition of the data: one shop has no name. | `bookshop-trail-faulty.ttl` |
| [s03 A constraint the data disagrees with](s03-a-constraint-the-data-disagrees-with.ttl) | Every bookshop has a website -- which six of them do not. | `bookshop-trail-1.1.ttl` |
| [s04 Exactly one town](s04-exactly-one-town.ttl) | Each shop is in exactly one settlement, has exactly one founding year, and at most one website. | `bookshop-trail-faulty.ttl` |
| [s05 Messages and severities](s05-messages-and-severities.ttl) | Where a severity has to be written for it to take effect, and what a message template can say. | `bookshop-trail-faulty.ttl` |
| [s06 Pinning one node, and switching a shape off](s06-pinning-one-node-and-switching-a-shape-off.ttl) | Check one named shop against several constraints, and keep a shape in the file without running it. | `bookshop-trail-faulty.ttl` |
| [s07 The four kinds of target](s07-the-four-kinds-of-target.ttl) | One shape for each way of choosing focus nodes: by class, by name, as the subject of a property, as its object. | `bookshop-trail-faulty.ttl` |
| [s08 A class that is its own shape](s08-a-class-that-is-its-own-shape.ttl) | bs:Translation declared as a class and a shape at once: every translation names what it translates, and who translated it. | `bookshop-trail-1.1.ttl` |
| [s09 Validating against nothing](s09-validating-against-nothing.ttl) | A shape whose target matches no node reports nothing, and 'conforms' is the result. How to notice. | `04-bookshops.ttl` |
