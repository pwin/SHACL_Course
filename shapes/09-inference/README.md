# Module 09 · Validating with inference

SHACL follows rdfs:subClassOf when it works out what a class covers, and nothing else. The editor can materialise the RDFS closure first (subclass, subproperty, domain and range), which changes the report in both directions: it finds nodes nobody typed, and it makes some errors disappear. Two lessons, and a pointer to the SPARQL course's module on reasoning.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

Lessons marked with an inference mode need the **Inference** dropdown set to that mode before validating; the LOAD IT link sets it for you.

**In the standards.** The sections this module is defined by:

- [SHACL 1.5 Relationship between SHACL and RDFS inferencing](https://www.w3.org/TR/shacl/#shacl-rdfs)
- [SHACL 1.2 Core 6.3 Graph for rdfs:subClassOf Triples](https://www.w3.org/TR/shacl12-core/#subClassOfInShapesGraph)
- [SHACL 2.1.3.2 sh:targetClass](https://www.w3.org/TR/shacl/#targetClass)
- [SHACL 4.1.1 sh:class](https://www.w3.org/TR/shacl/#ClassConstraintComponent)

| Lesson | Checks | Data |
|---|---|---|
| [s58 The event nobody typed](s58-the-event-nobody-typed.ttl) | Under RDFS inference, an event with no rdf:type is still an event, because bs:heldAt has a domain. | `bookshop-trail-faulty.ttl · *rdfs*` |
| [s59 The inference that hides an error](s59-the-inference-that-hides-an-error.ttl) | The same class constraints as s12, under RDFS: two of the errors disappear and two new ones appear. | `bookshop-trail-faulty.ttl · *rdfs*` |
