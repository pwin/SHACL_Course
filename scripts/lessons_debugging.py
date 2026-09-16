# -*- coding: utf-8 -*-
"""Module 10 -- Debugging shapes."""
from shapecat import s, Query, D11, DFAULTY
import specs

M = "10-debugging"

s(
    sid="s60", module=M,
    title="The shape that finds nothing",
    asks="Four shapes that should each report something on the faulty data, and do not -- and the canary that shows validation ran.",
    how="Each shape here has one mistake that makes it select or match "
        "nothing, and none of them produces an error. bt:WrongClass targets "
        "bs:BookShop with a capital S: no such class, no focus nodes. "
        "bt:WrongDirection puts [ sh:inversePath bs:heldAt ] on events: "
        "nothing points at an event with bs:heldAt, so there are no value "
        "nodes, and sh:class on no values passes -- the event held at a "
        "publisher (F20) goes unreported. bt:WrongTag looks for shops "
        "labelled \"The Inkwell\" with no language tag: the data says "
        "\"The Inkwell\"@en, a different term, so the query never matches "
        "(the SPARQL course's q95). bt:WrongPredicate targets the subjects "
        "of bs:heldat, lower case: none. The canary from s09 is the only "
        "row. The shapes count of eight says all of them compiled; the "
        "single result says four of them did nothing.",
    diagram="""
   symptom: Conforms, or fewer rows than expected, and no error

   check                                   this file
   is the target's class or predicate spelled as the data spells it?    bs:BookShop, bs:heldat
   is the path in the direction the data uses?                          ^bs:heldAt on an event
   do literals in the shape carry the same tag and datatype as the data?  "The Inkwell" vs "The Inkwell"@en
   does a canary that must fail, fail?                                  yes: validation ran
""",
    learn=[
        "A constraint on a path with no values passes. Missing values are a minCount question, and nothing else will notice them.",
        "Term equality is exact: language tag and datatype included. Copy the literal from the data, do not retype it.",
        "When a shape reports nothing, first prove that the target selects something: swap in sh:targetNode with a node you know.",
    ],
    tryit="Fix one mistake at a time and validate after each: BookShop to Bookshop, remove the "
          "sh:inversePath, add @en to the label, correct bs:heldat. A row should appear each time.",
    body="""
bt:WrongClass
    a               sh:NodeShape ;
    sh:targetClass  bs:BookShop ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] .

bt:WrongDirection
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [
        sh:path     [ sh:inversePath bs:heldAt ] ;
        sh:class    bs:Bookshop ;
        sh:message  "Meant: the place an event is held at is a bookshop." ;
    ] .

bt:WrongTag
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "Meant: flag the shop called The Inkwell." ;
        sh:select    \"\"\"
            SELECT $this WHERE { $this rdfs:label ?l . FILTER ( ?l = "The Inkwell" ) }
        \"\"\" ;
    ] .

bt:WrongPredicate
    a                    sh:NodeShape ;
    sh:targetSubjectsOf  bs:heldat ;
    sh:class             bs:Event .

bt:Canary
    a              sh:NodeShape ;
    sh:targetNode  bt:shop-inkwell ;
    sh:property [ sh:path rdf:type ; sh:maxCount 0 ;
                  sh:message "The canary: validation ran." ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, violations=1, shapes=8, focus=["shop-inkwell"], nofocus=["event-foxed-page"]),
)
specs.register("s60", "failures", "targets")

s(
    sid="s61", module=M,
    title="The shape that flags everything",
    asks="Four shapes that report every node they look at, on clean data, each for a different reason.",
    how="The opposite failure is a report full of rows that are all wrong. "
        "bt:GYearOrder is the SPARQL course's sh:lessThan between bs:born "
        "and bs:died: gYears do not compare on this engine, so every author "
        "with both dates is reported (s14). bt:StringLabels asks for "
        "xsd:string on labels that are all rdf:langString (s11): 33 shops. "
        "bt:HeldAtForwards puts bs:heldAt on shops, where it should be the "
        "inverse: no shop has one, 33 minCount rows. bt:RetailerClass "
        "declares in the shapes graph that a bookshop is a bs:Retailer and "
        "asks every stock record's shop to be one: rdfs:subClassOf is read "
        "from the data graph, not the shapes graph, so none is, and 95 rows "
        "follow. When every focus node fails, the shape is wrong before the "
        "data is, and the count in the headline shows it first.",
    diagram="""
   symptom: a row for every focus node

   cause                                       here
   a comparison the engine cannot make          sh:lessThan on xsd:gYear          8 rows
   a datatype the data never uses               xsd:string on "..."@en labels     33 rows
   a path in the wrong direction                bs:heldAt on a shop                33 rows
   a class hierarchy in the wrong graph         rdfs:subClassOf in the shapes file 95 rows
""",
    learn=[
        "A row for every node is a property of the shape, not the data. Read the shape again before touching the data.",
        "rdfs:subClassOf is followed in the data graph. If the hierarchy lives with the shapes, sh:class will not see it (SHACL 1.2 Core §6.3 discusses this).",
        "Datatype and direction mistakes fail every node the same way. Look at the first row's value and ask why it should have passed.",
    ],
    body="""
bt:GYearOrder
    a               sh:NodeShape ;
    sh:targetClass  bs:Author ;
    sh:property [ sh:path bs:born ; sh:lessThan bs:died ;
                  sh:message "Reported for every author with both dates: gYear does not compare." ] .

bt:StringLabels
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path rdfs:label ; sh:datatype xsd:string ;
                  sh:message "Reported for every shop: a tagged label is an rdf:langString." ] .

bt:HeldAtForwards
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path bs:heldAt ; sh:minCount 1 ;
                  sh:message "Reported for every shop: events point at shops, not the other way." ] .

# The hierarchy is declared here, in the shapes graph. SHACL reads it from the data graph.
bs:Bookshop  rdfs:subClassOf  bs:Retailer .

bt:RetailerClass
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [ sh:path bs:atShop ; sh:class bs:Retailer ;
                  sh:message "Reported for every record: the subclass axiom is in the wrong graph." ] .
""",
    data=D11,
    expect=dict(conforms=False, violations=169),
)
specs.register("s61", "c12subClassGraph", "datatype")

s(
    sid="s62", module=M,
    title="Naming your shapes",
    asks="The same constraints as s38, with every property shape named and described, so the report says which rule fired.",
    how="A property shape written as [ ... ] is a blank node, and the report "
        "can only call it 'bt:BookshopShape > property 3'. Give it an IRI and "
        "the report names it; add sh:name and sh:description and a form "
        "builder or a documentation tool can use them too. These are the "
        "non-validating characteristics of §2.3.2: they change nothing about "
        "what is checked. The query below groups the report by "
        "sh:sourceShape, which is only readable once the shapes have names. "
        "The convention here is the node shape's name, a hyphen, and the "
        "property's local name.",
    diagram="""
   before    sh:sourceShape  _:b12          shown as  bt:BookshopShape > property 3
   after     sh:sourceShape  bt:BookshopShape-founded

   bt:BookshopShape-founded
       a               sh:PropertyShape ;
       sh:path         bs:founded ;
       sh:name         "founded" ;                <- non-validating
       sh:description  "The year the shop opened, as an xsd:gYear." ;
       sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:gYear .
""",
    learn=[
        "Name property shapes. sh:sourceShape is the fastest route from a report row to the rule that produced it.",
        "sh:name, sh:description, sh:order and sh:group are for people and tools; validation ignores them.",
        "A named shapes graph is documentation of the data model. Write it as if it will be read.",
    ],
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:name         "Bookshop" ;
    sh:description  "An independent bookshop on the trail." ;
    sh:property     bt:BookshopShape-label, bt:BookshopShape-locatedIn, bt:BookshopShape-founded,
                    bt:BookshopShape-staffCount, bt:BookshopShape-website .

bt:IdentityGroup
    a           sh:PropertyGroup ;
    rdfs:label  "Identity" ;
    sh:order    0 .

bt:BookshopShape-label
    a               sh:PropertyShape ;
    sh:path         rdfs:label ;
    sh:name         "name" ;
    sh:description  "The shop's name, with a language tag." ;
    sh:group        bt:IdentityGroup ;
    sh:order        1 ;
    sh:minCount     1 ;
    sh:datatype     rdf:langString .

bt:BookshopShape-locatedIn
    a               sh:PropertyShape ;
    sh:path         bs:locatedIn ;
    sh:name         "town" ;
    sh:description  "The settlement the shop is in. Exactly one." ;
    sh:group        bt:IdentityGroup ;
    sh:order        2 ;
    sh:minCount     1 ;
    sh:maxCount     1 ;
    sh:class        bs:Settlement .

bt:BookshopShape-founded
    a               sh:PropertyShape ;
    sh:path         bs:founded ;
    sh:name         "founded" ;
    sh:description  "The year the shop opened, as an xsd:gYear." ;
    sh:order        3 ;
    sh:minCount     1 ;
    sh:maxCount     1 ;
    sh:datatype     xsd:gYear .

bt:BookshopShape-staffCount
    a               sh:PropertyShape ;
    sh:path         bs:staffCount ;
    sh:name         "staff" ;
    sh:order        4 ;
    sh:datatype     xsd:integer ;
    sh:minInclusive 1 .

bt:BookshopShape-website
    a               sh:PropertyShape ;
    sh:path         bs:website ;
    sh:name         "website" ;
    sh:description  "Optional; at most one." ;
    sh:order        5 ;
    sh:maxCount     1 ;
    sh:datatype     xsd:anyURI ;
    sh:severity     sh:Warning .
""",
    data=DFAULTY,
    expect=dict(conforms=False, min_violations=6),
    queries=[Query("Results by named shape", """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?shape (COUNT(?r) AS ?results)
WHERE { ?r a sh:ValidationResult ; sh:sourceShape ?shape }
GROUP BY ?shape
ORDER BY DESC(?results)""")],
)
specs.register("s62", "nonValidating", "sourceShape")

s(
    sid="s63", module=M,
    title="Shapes that check nothing",
    asks="Three ways to write a constraint the engine accepts and never applies.",
    how="bt:NoTarget is a well-formed node shape with constraints and no "
        "target: it compiles, it counts, it checks nothing, and a rule on it "
        "would never fire (s43). bt:CountOnNodeShape puts sh:minCount 1 on "
        "the node shape itself, where it belongs to no path; the "
        "specification calls that ill-formed, and this engine ignores it "
        "without a word. bt:UntypedButTargeted is the case that does work, "
        "for contrast: a node with a target and property shapes is a shape "
        "whether or not it is typed sh:NodeShape. The canary reports, and "
        "the shape count of seven is the only sign the first two are there. "
        "s09 and s60 cover the target that matches nothing; this lesson is "
        "the constraint that is never reached.",
    diagram="""
   bt:NoTarget            a sh:NodeShape ; sh:property [ ... ]            no focus nodes
   bt:CountOnNodeShape    a sh:NodeShape ; sh:targetNode ... ; sh:minCount 1   ignored: no sh:path
   bt:UntypedButTargeted  sh:targetNode ... ; sh:property [ ... ]        works: a shape by use

   shapes compiled: 7     results: 2   (one from the untyped shape, one canary)
""",
    learn=[
        "A shape with no target is a definition. It checks nothing unless another shape reaches it with sh:node, sh:not or a qualified shape.",
        "Cardinality, datatype and the other property constraints belong on property shapes. On a node shape they are silently dropped by this engine.",
        "Compare the shapes count with what you wrote, and keep a canary while you are unsure.",
    ],
    body="""
bt:NoTarget
    a  sh:NodeShape ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] .

# Ill-formed: sh:minCount without a property shape. Ignored by this engine.
bt:CountOnNodeShape
    a              sh:NodeShape ;
    sh:targetNode  bt:shop-halfmoon ;
    sh:minCount    1 ;
    sh:message     "Never reported: there is no sh:path for the count to apply to." .

# Works without rdf:type sh:NodeShape: the target and the property shape make it a shape.
bt:UntypedButTargeted
    sh:targetNode  bt:shop-halfmoon ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ;
                  sh:message "{$this} has no name (reported by a shape with no rdf:type)." ] .

bt:Canary
    a              sh:NodeShape ;
    sh:targetNode  bt:shop-inkwell ;
    sh:property [ sh:path rdf:type ; sh:maxCount 0 ; sh:message "The canary: validation ran." ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=2, shapes=7, focus=["shop-halfmoon", "shop-inkwell"]),
)
specs.register("s63", "shapes", "syntaxRules")
