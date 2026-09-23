# -*- coding: utf-8 -*-
"""Module 01 -- First shapes."""
from shapecat import s, Query, D11, DFAULTY, DSHOPS, DBOOKS
import specs

M = "01-first-shapes"

s(
    sid="s01", module=M,
    title="Every bookshop has a name",
    asks="Every bs:Bookshop has at least one rdfs:label.",
    how="A shape has two parts. sh:targetClass bs:Bookshop is the target: it "
        "selects every node in the data with rdf:type bs:Bookshop, and each of "
        "those becomes a focus node in turn. sh:property points at a property "
        "shape, which is the constraint: sh:path names the property to look at "
        "and sh:minCount 1 says there must be at least one value. For each of "
        "the 33 shops the engine collects the values of rdfs:label, counts "
        "them, and finds one. Nothing is reported, so the report says "
        "conforms.",
    diagram="""
   shapes graph                          data graph

   bt:BookshopShape                      bt:shop-inkwell
     sh:targetClass bs:Bookshop  ---->     a bs:Bookshop            <- focus node
     sh:property [                         rdfs:label "The Inkwell"@en
        sh:path     rdfs:label  ------->   ^ value nodes of the path: 1
        sh:minCount 1                      1 >= 1, nothing to report
     ]

   33 focus nodes, 33 counts, 0 results   =>   sh:conforms true
""",
    learn=[
        "A shape is a target plus constraints. The target picks the focus nodes; the constraints are checked at each one.",
        "A property shape constrains the values reached from the focus node along sh:path.",
        "No results means conforms. The headline also counts the shapes it compiled -- two here, the node shape and the property shape inside it.",
    ],
    tryit="In the data tab, delete the rdfs:label line of one shop and press Validate "
          "again. One violation appears, naming the shop and the path. Put the line "
          "back and it goes.",
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      rdfs:label ;
        sh:minCount  1 ;
    ] .
""",
    data=DSHOPS,
    expect=dict(conforms=True, violations=0, shapes=2),
)
specs.register("s01", "shapes", "targetClass", "minCount")

s(
    sid="s02", module=M,
    title="Reading a violation",
    asks="The same shape, on the faulty edition of the data: one shop has no name.",
    how="bookshop-trail-faulty.ttl is the clean dataset with data/faults.ttl "
        "appended; fault F01 is a shop with no rdfs:label. The report has one "
        "row. Read it left to right: the severity (Violation, the default), "
        "the focus node (the shop), the path (rdfs:label), the value (none, "
        "because the complaint is about absence), the message, and the source "
        "shape -- shown as 'bt:BookshopShape > property 1', because the "
        "property shape is a blank node and has no name of its own. Report as "
        "tab shows the same row as RDF: a sh:ValidationResult with "
        "sh:focusNode, sh:resultPath, sh:sourceConstraintComponent "
        "sh:MinCountConstraintComponent, sh:resultSeverity and "
        "sh:resultMessage. The severity here is written out; sh:Violation "
        "is what a shape gets when it says nothing.",
    diagram="""
   one result, seven things to read

   sh:resultSeverity            sh:Violation
   sh:focusNode                 bt:shop-halfmoon          <- which node
   sh:resultPath                rdfs:label                <- which property
   sh:value                     (none: nothing to point at)
   sh:sourceConstraintComponent sh:MinCountConstraintComponent   <- which rule
   sh:sourceShape               the property shape        <- which shape said so
   sh:resultMessage             "Every bookshop needs a name ..."

   {$this} in sh:message is replaced by the focus node.
""",
    learn=[
        "A validation result is a node in an RDF graph, and the table in the editor is one rendering of it.",
        "sh:value is present only when there is a value to point at. Cardinality results have none.",
        "sh:message is a template. {$this}, {$path} and {$value} are filled in from the result.",
        "The source shape of a property constraint is the property shape, not the node shape around it. That matters for severities later.",
    ],
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      rdfs:label ;
        sh:minCount  1 ;
        sh:severity  sh:Violation ;
        sh:message   "Every bookshop needs a name: {$this} has none." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=1, focus=["shop-halfmoon"]),
    queries=[Query("The result as RDF", """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?focus ?path ?component ?severity ?message
WHERE {
  ?r a sh:ValidationResult ;
     sh:focusNode ?focus ;
     sh:sourceConstraintComponent ?component ;
     sh:resultSeverity ?severity .
  OPTIONAL { ?r sh:resultPath ?path }
  OPTIONAL { ?r sh:resultMessage ?message }
}""")],
)
specs.register("s02", "result", "message")

s(
    sid="s03", module=M,
    title="A constraint the data disagrees with",
    asks="Every bookshop has a website -- which six of them do not.",
    how="The shape is the same pattern as s01 with bs:website in place of "
        "rdfs:label, and on the clean data it reports six shops. Nothing is "
        "wrong with the data: the vocabulary declares bs:website functional, "
        "which means at most one, and says nothing about needing one. The "
        "shape states a policy the data was never built to. Deciding who is "
        "right is not the validator's job; recording the decision is, and "
        "sh:severity is where it goes. sh:Violation means the data is wrong. "
        "sh:Warning means someone should look. sh:Info means this is a fact "
        "you asked to be told. Here it is a warning, and the report says the "
        "data does not conform, because by default every one of those three "
        "severities counts. A report can say otherwise: sh:conformanceDisallows "
        "lists the severities being judged by, and the verdict then travels "
        "with the rule that produced it.",
    diagram="""
   the shape says        every shop  --website-->  something
   the data says         27 shops do, 6 do not

   who is right?  that is a decision about the policy, not about the data

   sh:severity records the decision:
     sh:Violation   the data is wrong           counts against conforms
     sh:Warning     someone should look         counts
     sh:Info        a fact you asked for        counts
     sh:Debug       for the shape author        does not   (1.2)
     sh:Trace       for the shape author        does not   (1.2)

   a report may narrow that:  sh:conformanceDisallows sh:Violation
                              -> only violations count, and the report says so
""",
    learn=[
        "A shape is a statement of policy. When the data disagrees, check the policy before you fix the data.",
        "Severity is a property of the shape, and it is how you say what kind of finding this is.",
        "Warning and Info stop a report from conforming, as the specification says and as pySHACL has always done. This engine counted only violations until 0.3.0; module 12 records the difference and when it went.",
    ],
    tryit="Change sh:Warning to sh:Info and validate again. Same six rows, same "
          "verdict: all three severities count. Then add sh:conformanceDisallows "
          "sh:Violation to ask for a narrower judgement, and the headline turns "
          "to Conforms while the six rows stay.",
    body="""
bt:WebsiteExpected
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      bs:website ;
        sh:minCount  1 ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} has no website on record. Six shops do not; check with the shop before treating it as an error." ;
    ] .
""",
    data=D11,
    expect=dict(conforms=False, warnings=6, violations=0, focus=["shop-marginalia", "shop-ex-libris"]),
)
specs.register("s03", "severity", "conforms")

s(
    sid="s04", module=M,
    title="Exactly one town",
    asks="Each shop is in exactly one settlement, has exactly one founding year, and at most one website.",
    how="sh:minCount and sh:maxCount together give a cardinality range. "
        "[1..1] is 'exactly one'; [0..1] is 'optional, but not more than one'; "
        "a bare sh:minCount 1 is 'at least one'. On the faulty data three "
        "shops fail, one per property: The Inkwell has been placed in a second "
        "town (F04), the shop with no name also has no founding year (F01), and "
        "The Foxed Page lists two websites (F06). The website maximum needs no "
        "minimum: six real shops have none, and s03 decided that was allowed.",
    diagram="""
                      minCount  maxCount     reads as
   bs:locatedIn          1         1         exactly one
   bs:founded            1         1         exactly one
   bs:website            -         1         at most one

   bt:shop-inkwell   bs:locatedIn  bt:place-wigtown, bt:place-hay-on-wye    2 > 1
   bt:shop-halfmoon  bs:founded    (nothing)                                0 < 1
   bt:shop-foxed-page bs:website   "www...", "https://..."                  2 > 1
""",
    learn=[
        "minCount and maxCount are independent. Use both for 'exactly one', one of them for 'at least' or 'at most'.",
        "A maxCount result has no sh:value either: it is about the count, not any one value.",
        "Property shapes are cheap. One node shape can carry as many as the class has properties, and a report row names the one that fired.",
    ],
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      bs:locatedIn ;
        sh:minCount  1 ;
        sh:maxCount  1 ;
        sh:message   "A shop is in exactly one settlement." ;
    ] ;
    sh:property [
        sh:path      bs:founded ;
        sh:minCount  1 ;
        sh:maxCount  1 ;
        sh:message   "A shop records the one year it opened." ;
    ] ;
    sh:property [
        sh:path      bs:website ;
        sh:maxCount  1 ;
        sh:message   "At most one website." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=3, focus=["shop-inkwell", "shop-halfmoon", "shop-foxed-page"]),
)
specs.register("s04", "minCount", "maxCount")

s(
    sid="s05", module=M,
    title="Messages and severities",
    asks="Where a severity has to be written for it to take effect, and what a message template can say.",
    how="Two shapes report the shops without a website. bt:WebsiteAdvice puts "
        "sh:severity sh:Info on the node shape; its results come back as "
        "Violations. bt:WebsiteAdviceFixed puts the same severity on the "
        "property shape, and its results are Infos. The rule is that a result "
        "takes its severity from its source shape, and the source shape of a "
        "property constraint is the property shape. A severity on the node "
        "shape applies only to constraints written on the node shape itself. "
        "The third shape shows a message using {$value}: sh:minInclusive "
        "(module 02) reports the offending value, so the template has "
        "something to fill in. Messages can carry a language tag, and a shape "
        "can have several.",
    diagram="""
   bt:WebsiteAdvice                        bt:WebsiteAdviceFixed
     sh:severity sh:Info   <- ignored        sh:property [
     sh:property [            by this          sh:path bs:website ;
        sh:path bs:website ;  property         sh:minCount 1 ;
        sh:minCount 1 ]       shape            sh:severity sh:Info ]   <- used
          |                                        |
          v                                        v
     7 x Violation                            7 x Info

   the source shape of a property constraint is the property shape
""",
    learn=[
        "Write sh:severity on the shape that owns the constraint. For a property constraint that is the property shape.",
        "{$value} is filled only when the result has a value. A message that mentions it on a minCount constraint keeps the braces.",
        "Several sh:message values are allowed, usually one per language. This engine joins them into one string; keep to one per shape if that matters.",
    ],
    tryit="Move sh:severity sh:Info from bt:WebsiteAdvice onto its property shape. The "
          "seven violations become infos and the headline changes to Conforms.",
    body="""
# The severity is on the node shape. The constraint is on the property shape.
# The results come from the property shape, so they are Violations.
bt:WebsiteAdvice
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:severity     sh:Info ;
    sh:property [
        sh:path      bs:website ;
        sh:minCount  1 ;
        sh:message   "No website on record for {$this}. (severity written on the node shape)" ;
    ] .

# The same constraint with the severity where it takes effect.
bt:WebsiteAdviceFixed
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      bs:website ;
        sh:minCount  1 ;
        sh:severity  sh:Info ;
        sh:message   "No website on record for {$this}. (severity written on the property shape)" ;
    ] .

# A constraint with a value to report, so {$value} has something to say.
bt:StaffedShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path          bs:staffCount ;
        sh:minInclusive  1 ;
        sh:severity      sh:Warning ;
        sh:message       "{$this} reports {$value} staff. A shop with nobody in it is not trading."@en ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=7, infos=7, warnings=1, focus=["shop-halfmoon"]),
)
specs.register("s05", "severity", "message")

s(
    sid="s06", module=M,
    title="Pinning one node, and switching a shape off",
    asks="Check one named shop against several constraints, and keep a shape in the file without running it.",
    how="sh:targetNode names the focus nodes one by one. While a shape is "
        "being written, pointing it at a single node you know keeps the report "
        "short and the cause of each row obvious; the SPARQL course does the "
        "same thing with a VALUES clause in q94. The Foxed Page has two "
        "websites, so the one violation is that. sh:deactivated true takes a "
        "shape out of validation without deleting it: bt:EveryShopShape would "
        "report every shop without a website, and reports nothing. It still "
        "counts in the shapes total.",
    diagram="""
   sh:targetNode bt:shop-foxed-page       one focus node, whatever else is in the data
        |
        +-- rdfs:label   minCount 1     "The Foxed Page"        ok
        +-- bs:locatedIn minCount 1     "Kendal"                ok  (a string, but present)
        +-- bs:website   maxCount 1     two values              1 violation

   sh:deactivated true                    compiled, counted, never run
""",
    learn=[
        "sh:targetNode is the fastest way to develop a shape: one node, one report row per problem.",
        "Several targets on one shape are unioned. targetNode and targetClass can be used together.",
        "sh:deactivated keeps a shape in the file and out of the report. Remember to take it off.",
    ],
    body="""
bt:OneShopShape
    a              sh:NodeShape ;
    sh:targetNode  bt:shop-foxed-page ;
    sh:property [ sh:path rdfs:label ;   sh:minCount 1 ] ;
    sh:property [ sh:path bs:locatedIn ; sh:minCount 1 ] ;
    sh:property [ sh:path bs:website ;   sh:maxCount 1 ;
                  sh:message "{$this} lists more than one website." ] .

bt:EveryShopShape
    a               sh:NodeShape ;
    sh:deactivated  true ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path bs:website ; sh:minCount 1 ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=1, focus=["shop-foxed-page"], nofocus=["shop-halfmoon", "shop-marginalia"]),
)
specs.register("s06", "targetNode", "deactivated")

s(
    sid="s07", module=M,
    title="The four kinds of target",
    asks="One shape for each way of choosing focus nodes: by class, by name, as the subject of a property, as its object.",
    how="sh:targetClass bs:Event picks the typed events; the faulty event "
        "with nobody featuring (F20) fails sh:minCount on bs:featuring. "
        "sh:targetSubjectsOf bs:heldAt picks everything that has a bs:heldAt, "
        "typed or not, and sh:class bs:Event at node level then catches the "
        "event nobody typed (F21) -- a node sh:targetClass could never have "
        "seen. sh:targetObjectsOf bs:heldAt picks the things events are held "
        "at, and sh:class bs:Bookshop catches the event held at a publisher. "
        "sh:targetNode bt:shop-inkwell is one node by name. Note that "
        "sh:class on a node shape constrains the focus node itself, so the "
        "value in the report is the focus node.",
    diagram="""
   sh:targetClass      bs:Event      ->  every ?x with  ?x rdf:type bs:Event (or a subclass)
   sh:targetSubjectsOf bs:heldAt     ->  every ?x with  ?x bs:heldAt ?o
   sh:targetObjectsOf  bs:heldAt     ->  every ?o with  ?s bs:heldAt ?o
   sh:targetNode       bt:shop-inkwell -> that node

   the untyped event         bs:heldAt bt:shop-inkwell     seen by SubjectsOf, invisible to targetClass
   the event at a publisher  bs:heldAt bt:pub-pica         its object fails sh:class bs:Bookshop
""",
    learn=[
        "targetClass depends on rdf:type. Data that is described but never typed is invisible to it.",
        "targetSubjectsOf and targetObjectsOf select by use of a property. They are how you check the untyped, and how you check what a property points at.",
        "sh:class on a node shape tests the focus node; on a property shape it tests each value.",
    ],
    body="""
bt:TypedEventShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [ sh:path bs:featuring ; sh:minCount 1 ;
                  sh:message "An event features at least one author." ] .

bt:HeldAtSubjectShape
    a                    sh:NodeShape ;
    sh:targetSubjectsOf  bs:heldAt ;
    sh:class             bs:Event ;
    sh:message           "{$this} has a bs:heldAt but is not typed as a bs:Event." .

bt:HeldAtObjectShape
    a                   sh:NodeShape ;
    sh:targetObjectsOf  bs:heldAt ;
    sh:class            bs:Bookshop ;
    sh:message          "Events are held at bookshops; {$this} is not one." .

bt:InkwellShape
    a              sh:NodeShape ;
    sh:targetNode  bt:shop-inkwell ;
    sh:property [ sh:path bs:locatedIn ; sh:maxCount 1 ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=4,
                focus=["event-foxed-page", "event-inkwell-2025-06-01", "pub-pica", "shop-inkwell"]),
)
specs.register("s07", "targets", "targetSubjectsOf")

s(
    sid="s08", module=M,
    title="A class that is its own shape",
    asks="bs:Translation declared as a class and a shape at once: every translation names what it translates, and who translated it.",
    how="A node that is both an rdfs:Class and a sh:NodeShape targets its own "
        "instances; no sh:targetClass is needed. SHACL 1.2 spells the same "
        "thing sh:ShapeClass, and this engine accepts both. The rdf:type "
        "triples for the class live in the shapes graph; the rdfs:subClassOf "
        "triples SHACL follows when it decides what an instance is are read "
        "from the data graph, which here declares bs:Translation a subclass of "
        "bs:Work. On the clean data one of the six translations, the Hebrew "
        "edition of Cold Harbour, has no bs:translatedBy, and the shape "
        "reports it. Whether that is a gap in the data or a translator nobody "
        "recorded is a question for the data's maintainer; the shape has said "
        "what it was asked to.",
    diagram="""
   bs:Translation  a  rdfs:Class, sh:NodeShape        <- implicit target: its instances
        sh:property [ sh:path bs:translationOf ; minCount 1 ; maxCount 1 ]
        sh:property [ sh:path bs:translatedBy  ; minCount 1 ]

   data graph:  bt:book-the-dark-sea-ar  a  bs:Translation, bs:Work   -> a focus node
                (rdfs:subClassOf triples are read from here too)

   SHACL 1.2:   bs:Translation  a  sh:ShapeClass     same meaning, one type
""",
    learn=[
        "An implicit class target is a shape typed rdfs:Class. It is convenient when the schema and the shapes are maintained together.",
        "Class membership follows rdfs:subClassOf in the data graph, not in the shapes graph. Keep the hierarchy with the data if targets are to follow it.",
        "A finding on clean data is still a finding. Read it before deciding whether the data or the shape is at fault.",
    ],
    body="""
bs:Translation
    a  rdfs:Class, sh:NodeShape ;
    sh:property [
        sh:path      bs:translationOf ;
        sh:minCount  1 ;
        sh:maxCount  1 ;
        sh:message   "A translation is of exactly one work." ;
    ] ;
    sh:property [
        sh:path      bs:translatedBy ;
        sh:minCount  1 ;
        sh:message   "{$this} does not say who translated it." ;
    ] .

# The SHACL 1.2 spelling of the same idea: one type instead of two.
bs:Series
    a  sh:ShapeClass ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] .
""",
    data=D11,
    expect=dict(conforms=False, violations=1, focus=["book-cold-harbour-he"]),
)
specs.register("s08", "implicit", "c12ShapeClass")

s(
    sid="s09", module=M,
    title="Validating against nothing",
    asks="A shape whose target matches no node reports nothing, and 'conforms' is the result. How to notice.",
    how="bt:MistypedShape targets bs:BookShop, with a capital S. No node has "
        "that type, so the shape has no focus nodes, checks nothing, and "
        "contributes nothing to the report. On its own the report would say "
        "Conforms, which is true and useless. The second shape is a canary: "
        "it targets one node that certainly exists and asks for something "
        "certainly false, sh:maxCount 0 on rdf:type. Its one violation proves "
        "the data was loaded and validation ran. Take it out once the real "
        "shapes are reporting. The headline's shape count is the other check: "
        "if it is lower than you expect, something did not compile as a shape.",
    diagram="""
   sh:targetClass bs:BookShop      no such class in the data
        |
        no focus nodes  ->  no checks  ->  no results  ->  "Conforms"

   the canary
   sh:targetNode bt:shop-inkwell ; sh:property [ sh:path rdf:type ; sh:maxCount 0 ]
        |
        1 violation, always  ->  proof that validation happened
""",
    learn=[
        "Conforms means nothing that counts was found. It does not mean anything was checked.",
        "While writing shapes, keep one constraint that must fail. When it stops failing, the data is not what you think.",
        "The shapes count in the headline tells you how many shapes compiled. Compare it with how many you wrote.",
    ],
    tryit="Fix the capital S and validate again: the shape now checks 33 shops and finds nothing to report. Then delete the canary.",
    body="""
bt:MistypedShape
    a               sh:NodeShape ;
    sh:targetClass  bs:BookShop ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] .

# A constraint that cannot pass, on a node that certainly exists.
bt:Canary
    a              sh:NodeShape ;
    sh:targetNode  bt:shop-inkwell ;
    sh:property [
        sh:path      rdf:type ;
        sh:maxCount  0 ;
        sh:message   "The canary: validation ran and the data is loaded. Remove this shape when the real ones report." ;
    ] .
""",
    data=DSHOPS,
    expect=dict(conforms=False, violations=1, shapes=4, focus=["shop-inkwell"]),
)
specs.register("s09", "conformance", "targetClass")
