# Module 02 · What a value may be

The constraint components that look at one value at a time: its datatype and node kind, its class, its numeric range, its length and pattern, its language tag, and how it compares with another property of the same node. The difference between a value and its lexical form matters here, and an xsd:gYear causes the same trouble it causes in SPARQL.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL §4.1.2 sh:datatype](https://www.w3.org/TR/shacl/#DatatypeConstraintComponent)
- [SHACL §4.1.3 sh:nodeKind](https://www.w3.org/TR/shacl/#NodeKindConstraintComponent)
- [SHACL §4.1.1 sh:class](https://www.w3.org/TR/shacl/#ClassConstraintComponent)
- [SHACL §4.3 Value Range Constraint Components](https://www.w3.org/TR/shacl/#core-components-range)
- [SHACL §4.4 String-based Constraint Components](https://www.w3.org/TR/shacl/#core-components-string)
- [SHACL §4.4.3 sh:pattern](https://www.w3.org/TR/shacl/#PatternConstraintComponent)
- [SHACL §4.4.4 sh:languageIn](https://www.w3.org/TR/shacl/#LanguageInConstraintComponent)
- [SHACL §4.4.5 sh:uniqueLang](https://www.w3.org/TR/shacl/#UniqueLangConstraintComponent)
- [SHACL §4.8.3 sh:in](https://www.w3.org/TR/shacl/#InConstraintComponent)
- [SHACL §4.8.2 sh:hasValue](https://www.w3.org/TR/shacl/#HasValueConstraintComponent)
- [SHACL §4.5 Property Pair Constraint Components](https://www.w3.org/TR/shacl/#core-components-property-pairs)
- [SHACL §4.5.3 sh:lessThan](https://www.w3.org/TR/shacl/#LessThanConstraintComponent)
- [SHACL §4.5.4 sh:lessThanOrEquals](https://www.w3.org/TR/shacl/#LessThanOrEqualsConstraintComponent)
- [SHACL §4.5.1 sh:equals](https://www.w3.org/TR/shacl/#EqualsConstraintComponent)
- [SHACL §4.5.2 sh:disjoint](https://www.w3.org/TR/shacl/#DisjointConstraintComponent)

| Lesson | Checks | Data |
|---|---|---|
| [s10 The right kind of value](s10-the-right-kind-of-value.ttl) | Years are xsd:gYear, counts are integers, prices are decimals, flags are booleans, and a date is a date. | `bookshop-trail-faulty.ttl` |
| [s11 IRI, literal or blank node](s11-iri-literal-or-blank-node.ttl) | A shop's town is a node, not a string; a shop's name is a literal with a language tag. | `bookshop-trail-faulty.ttl` |
| [s12 sh:class, and why it needs rdf:type](s12-sh-class-and-why-it-needs-rdf-type.ttl) | What a shop, a person, an event, a record and a settlement may point at. | `bookshop-trail-faulty.ttl` |
| [s13 Ranges](s13-ranges.ttl) | Coordinates on the globe, counts that are not negative, prices that are not negative, a confidence between 0 and 1. | `bookshop-trail-faulty.ttl` |
| [s14 Comparing years](s14-comparing-years.ttl) | No shop opened before 1800, and nobody died before they were born -- said in a way this engine can evaluate. | `bookshop-trail-faulty.ttl` |
| [s15 Strings: length and pattern](s15-strings-length-and-pattern.ttl) | An ISBN-13 is thirteen digits starting 978 or 979; a website starts with a scheme; an event kind is one of seven words. | `bookshop-trail-faulty.ttl` |
| [s16 Languages](s16-languages.ttl) | Place names are in English, Welsh or Gaelic, and one name per language; shop names carry a tag. | `bookshop-trail-faulty.ttl` |
| [s17 A fixed list of values](s17-a-fixed-list-of-values.ttl) | Kinds of event, kinds of source and writing languages come from short lists, and every country is inside Great Britain. | `bookshop-trail-faulty.ttl` |
| [s18 Comparing two properties](s18-comparing-two-properties.ttl) | A segment's two ends differ; a work's label and title agree; a translation is not older than its original; and the gYear problem again. | `bookshop-trail-faulty.ttl` |
