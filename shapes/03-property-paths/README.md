# Module 03 · Property paths in shapes

sh:path is not always a single predicate. A property shape can follow a sequence of steps, walk a link backwards, take either of two routes, or continue for any number of hops. These are the paths SPARQL has, written as RDF. One lesson repeats the SPARQL course's point about fixed-length chains, because the same mistake is just as easy to make in a shape.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

**In the standards.** The sections this module is defined by:

- [SHACL 2.3.1 SHACL Property Paths](https://www.w3.org/TR/shacl/#property-paths)
- [SHACL 2.3.1.2 Sequence Paths](https://www.w3.org/TR/shacl/#property-path-sequence)
- [SHACL 2.3.1.4 Inverse Paths](https://www.w3.org/TR/shacl/#property-path-inverse)
- [SHACL 2.3.1.3 Alternative Paths](https://www.w3.org/TR/shacl/#property-path-alternative)
- [SHACL 2.3.1.5 Zero-Or-More Paths](https://www.w3.org/TR/shacl/#property-path-zero-or-more)
- [SHACL 2.3.1.6 One-Or-More Paths](https://www.w3.org/TR/shacl/#property-path-one-or-more)
- [SHACL 2.3.1.7 Zero-Or-One Paths](https://www.w3.org/TR/shacl/#property-path-zero-or-one)
- [SHACL 3.6.2.2 sh:resultPath](https://www.w3.org/TR/shacl/#results-path)
- [SPARQL 1.2 Query section 9 Property Paths](https://www.w3.org/TR/sparql12-query/#x9-property-paths)

| Lesson | Checks | Data |
|---|---|---|
| [s19 A path through two hops](s19-a-path-through-two-hops.ttl) | Every shop's town is inside a council area; every stock record's shop is in a settlement. | `bookshop-trail-faulty.ttl` |
| [s20 The fixed chain that misses twenty shops](s20-the-fixed-chain-that-misses-twenty-shops.ttl) | Every shop is inside Great Britain -- first with a fixed number of hops, then with a path of any length. | `bookshop-trail-1.1.ttl` |
| [s21 Walking a link backwards](s21-walking-a-link-backwards.ttl) | Towns with no bookshop, and genres nobody stocks or specialises in -- found by following properties against their direction. | `bookshop-trail-1.1.ttl` |
| [s22 Any number of hops](s22-any-number-of-hops.ttl) | Every genre leads up to the top concept, and every place leads up to Great Britain. | `bookshop-trail-faulty.ttl` |
| [s23 Either route, and the path in the report](s23-either-route-and-the-path-in-the-report.ttl) | Every shop has a trail neighbour in one direction or the other; which shops are junctions; and what a compound path looks like in the report graph. | `bookshop-trail-1.1.ttl` |
