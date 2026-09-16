# Module 10 · Debugging shapes

'Conforms' is what a validator says when the data is right, and also what it says when it checked nothing. This module collects the ways a shape goes wrong without an error: a target that matches nothing, a path in the wrong direction, a datatype or language tag that stops a match, a severity that does not inherit. Each comes with the check that catches it.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL §3.4.1 Failures](https://www.w3.org/TR/shacl/#failures)
- [SHACL §3.5 Conformance Checking](https://www.w3.org/TR/shacl/#conformance-definition)
- [SHACL §2.1.3 Targets](https://www.w3.org/TR/shacl/#targets)
- [SHACL §3.7 Value Nodes](https://www.w3.org/TR/shacl/#value-nodes)
- [SHACL §2.1.4 Declaring the Severity of a Shape](https://www.w3.org/TR/shacl/#severity)
- [SHACL §3.6.2.4 sh:sourceShape](https://www.w3.org/TR/shacl/#results-source-shape)
- [SHACL §4.1.2 sh:datatype](https://www.w3.org/TR/shacl/#DatatypeConstraintComponent)

| Lesson | Checks | Data |
|---|---|---|
| [s60 The shape that finds nothing](s60-the-shape-that-finds-nothing.ttl) | Four shapes that should each report something on the faulty data, and do not -- and the canary that shows validation ran. | `bookshop-trail-faulty.ttl` |
| [s61 The shape that flags everything](s61-the-shape-that-flags-everything.ttl) | Four shapes that report every node they look at, on clean data, each for a different reason. | `bookshop-trail-1.1.ttl` |
| [s62 Naming your shapes](s62-naming-your-shapes.ttl) | The same constraints as s38, with every property shape named and described, so the report says which rule fired. | `bookshop-trail-faulty.ttl` |
| [s63 Shapes that check nothing](s63-shapes-that-check-nothing.ttl) | Three ways to write a constraint the engine accepts and never applies. | `bookshop-trail-faulty.ttl` |
