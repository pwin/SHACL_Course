# Module 11 · Putting it together

A complete shapes graph for the Bookshop Trail, run on the clean data and then on the faulty edition as its answer key; shapes used as questions rather than rules; a report turned into a list of issues in the dataset's own vocabulary; and a rule set that enriches the graph before checking it.

Each `.ttl` file carries its own explanation: what it checks, how it works, a diagram of the mechanism, and what to take away. Read the header, then open the LOAD IT link -- it puts the data in one tab and the shapes in another, and the Validate button does the rest.

Lessons marked with an inference mode need the **Inference** dropdown set to that mode before validating; the LOAD IT link sets it for you.

**In the standards.** The sections this module is defined by:

- [SHACL 3.1 Shapes Graph](https://www.w3.org/TR/shacl/#shapes-graph)
- [SHACL 3.6 Validation Report](https://www.w3.org/TR/shacl/#validation-report)
- [SHACL 3.6.2 Validation Result](https://www.w3.org/TR/shacl/#results-validation-result)
- [SHACL-AF section 8 SHACL Rules](https://www.w3.org/TR/shacl-af/#rules)
- [SHACL section 5 SPARQL-based Constraints](https://www.w3.org/TR/shacl/#sparql-constraints)

| Lesson | Checks | Data |
|---|---|---|
| [s64 The whole trail in one shapes graph](s64-the-whole-trail-in-one-shapes-graph.ttl) | A shapes graph for every class in the dataset, run on the faulty edition. Every numbered fault in data/faults.ttl appears in the report. | `bookshop-trail-faulty.ttl` |
| [s65 Shapes as questions](s65-shapes-as-questions.ttl) | Six facts about the clean data, asked as shapes and answered as information. | `bookshop-trail-1.1.ttl` |
| [s66 From report to issues](s66-from-report-to-issues.ttl) | A report turned into bs:DataIssue records -- the vocabulary already has a class for them. | `bookshop-trail-faulty.ttl` |
| [s67 A rule set for the trail](s67-a-rule-set-for-the-trail.ttl) | Infer each shop's country and each record's value, then check what only the inferred data can answer. | `bookshop-trail-1.1.ttl · *rules*` |
| [s68 Challenge: the walking tour](s68-challenge-the-walking-tour.ttl) | Four questions about the trail that each need two or three techniques at once. Try them before reading the shapes. | `bookshop-trail-1.1.ttl · *rules*` |
