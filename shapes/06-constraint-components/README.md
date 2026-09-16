# Module 06 · Your own constraint components

sh:minCount is a parameter and a validator, and a shapes graph can declare new components on the same terms. A constraint component gives a SPARQL check a name and parameters, so the shapes that use it read like Core and the query is written once. Appendix D of the specification defines every Core component this way.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL §6 SPARQL-based Constraint Components](https://www.w3.org/TR/shacl/#sparql-constraint-components)
- [SHACL §6.2.1 Parameter Declarations (sh:parameter)](https://www.w3.org/TR/shacl/#constraint-components-parameters)
- [SHACL §6.2.2 Label Templates (sh:labelTemplate)](https://www.w3.org/TR/shacl/#labelTemplate)
- [SHACL §6.2.3 Validators](https://www.w3.org/TR/shacl/#constraint-components-validators)
- [SHACL §6.2.3.1 SELECT-based Validators](https://www.w3.org/TR/shacl/#SPARQLSelectValidator)
- [SHACL §6.2.3.2 ASK-based Validators](https://www.w3.org/TR/shacl/#SPARQLAskValidator)
- [SHACL Appendix D Summary of SHACL Core Validators](https://www.w3.org/TR/shacl/#core-validators)

| Lesson | Checks | Data |
|---|---|---|
| [s39 An ISBN check digit](s39-an-isbn-check-digit.ttl) | Every ISBN-13's last digit is the check digit its first twelve imply. | `bookshop-trail-faulty.ttl` |
| [s40 A SELECT validator with parameters](s40-a-select-validator-with-parameters.ttl) | A value is at most some multiple of a value reached through two properties -- a shelf price against a recommended price, said generally. | `bookshop-trail-faulty.ttl` |
| [s41 A required language, and an optional parameter](s41-a-required-language-and-an-optional-parameter.ttl) | Every Welsh place has a Welsh name -- with an option to accept one from skos:altLabel. | `bookshop-trail-1.1.ttl` |
| [s42 Core components are SPARQL too](s42-core-components-are-sparql-too.ttl) | sh:minCount and sh:minInclusive written as constraint components -- the second in a version that understands years. | `bookshop-trail-1.1.ttl` |
