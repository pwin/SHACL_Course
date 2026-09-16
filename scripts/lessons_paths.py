# -*- coding: utf-8 -*-
"""Module 03 -- Property paths in shapes."""
from shapecat import s, Query, D11, DFAULTY
import specs

M = "03-property-paths"

s(
    sid="s19", module=M,
    title="A path through two hops",
    asks="Every shop's town is inside a council area; every stock record's shop is in a settlement.",
    how="A sequence path is an RDF list. sh:path ( bs:locatedIn bs:within ) "
        "starts at the focus node, follows bs:locatedIn, then follows "
        "bs:within from wherever that arrived, and the value nodes are the "
        "ends of the walk. The constraints then apply to those ends as they "
        "would to any values: sh:class bs:CouncilArea and sh:minCount 1. The "
        "Foxed Page (F06) has \"Kendal\" for a town, a string with no "
        "bs:within, so the walk ends nowhere and sh:minCount reports it. Its "
        "stock record walks bs:atShop then bs:locatedIn and arrives at the "
        "same string, which fails sh:class bs:Settlement. The record at the "
        "untyped Ghost Shop passes: the walk goes through the shop whatever "
        "its type, and Durham is a settlement.",
    diagram="""
   sh:path ( bs:locatedIn bs:within )

   bt:shop-inkwell --locatedIn--> bt:place-wigtown --within--> bt:place-dumfries-galloway
                                                                 ^ value node: a CouncilArea, ok

   bt:shop-foxed-page --locatedIn--> "Kendal" --within--> (nothing)
                                                             no value nodes: minCount 1 fails

   sh:path ( bs:atShop bs:locatedIn )
   bt:stock-ghost --atShop--> bt:shop-ghost --locatedIn--> bt:place-durham     a Settlement, ok
""",
    learn=[
        "A sequence path is a list: ( p1 p2 ). The value nodes are where the whole walk ends.",
        "Constraints see only the ends. Anything wrong in the middle shows up as a missing or wrong end, not as its own result.",
        "sh:minCount 1 on a path is 'the walk arrives somewhere'. It is the check for a broken chain.",
    ],
    body="""
bt:ShopInCouncilArea
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      ( bs:locatedIn bs:within ) ;
        sh:minCount  1 ;
        sh:class     bs:CouncilArea ;
        sh:message   "Two hops from {$this} should reach a council area." ;
    ] .

bt:RecordInSettlement
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [
        sh:path      ( bs:atShop bs:locatedIn ) ;
        sh:minCount  1 ;
        sh:class     bs:Settlement ;
        sh:message   "The shop holding {$this} is in {$value}, which is not a settlement." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=2, focus=["shop-foxed-page", "stock-foxed-page"], nofocus=["stock-ghost"]),
)
specs.register("s19", "pathSequence", "paths")

s(
    sid="s20", module=M,
    title="The fixed chain that misses twenty shops",
    asks="Every shop is inside Great Britain -- first with a fixed number of hops, then with a path of any length.",
    how="The place hierarchy is uneven, and the SPARQL course's q28 is built "
        "on that. An English town sits in a council area in a region in a "
        "country in Great Britain; a Scottish or Welsh town has no region. "
        "bt:FixedChain walks bs:locatedIn and then exactly three bs:within "
        "hops and asks for bt:place-gb among the ends. From a Scottish shop "
        "three hops reach Great Britain; from an English shop they reach "
        "England, and the shape reports twenty English shops as outside the "
        "country. bt:AnyDepth replaces the three hops with "
        "[ sh:oneOrMorePath bs:within ], whose value nodes are every place "
        "reached by one or more hops. Great Britain is among them for all 33 "
        "shops, and it reports nothing. The wrong shape produces no error, "
        "and twenty rows that are all wrong.",
    diagram="""
   England (4 levels)                    Scotland / Wales (3 levels)

   shop --locatedIn--> york              shop --locatedIn--> edinburgh
          --within--> north-yorkshire           --within--> edinburgh-city
          --within--> yorkshire                 --within--> scotland
          --within--> england                   --within--> gb           <- 3 hops arrive
          --within--> gb                <- needs 4

   ( bs:locatedIn bs:within bs:within bs:within )   sh:hasValue bt:place-gb
        Scottish and Welsh shops pass, 20 English shops fail

   ( bs:locatedIn [ sh:oneOrMorePath bs:within ] )  sh:hasValue bt:place-gb
        every hop's destination is a value node; gb is among them for all 33
""",
    learn=[
        "A fixed number of hops encodes an assumption about the data's depth. When the depth varies, the shape is wrong for part of the data and silent about it.",
        "[ sh:oneOrMorePath p ] and [ sh:zeroOrMorePath p ] make every intermediate node a value node. sh:hasValue then asks whether the one you want is among them.",
        "Twenty violations on data you believe to be right is a reason to reread the shape first.",
    ],
    body="""
# Wrong: assumes every shop is exactly four hops from Great Britain.
bt:FixedChain
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      ( bs:locatedIn bs:within bs:within bs:within ) ;
        sh:hasValue  bt:place-gb ;
        sh:message   "Fixed chain: {$this} 'is not in Great Britain'. It is; the chain is the wrong length." ;
    ] .

# Right: any number of bs:within hops.
bt:AnyDepth
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) ;
        sh:hasValue  bt:place-gb ;
        sh:message   "{$this} is not inside Great Britain at any depth." ;
    ] .
""",
    data=D11,
    expect=dict(conforms=False, violations=20, focus=["shop-ex-libris"], nofocus=["shop-inkwell"]),
)
specs.register("s20", "pathOneOrMore", "hasValue")

s(
    sid="s21", module=M,
    title="Walking a link backwards",
    asks="Towns with no bookshop, and genres nobody stocks or specialises in -- found by following properties against their direction.",
    how="[ sh:inversePath bs:locatedIn ] at a settlement yields the things "
        "located in it. sh:minCount 1 then says every settlement has at least "
        "one, and four do not: Durham, Perth, Fort William and Truro, the "
        "same four the SPARQL course's q16 finds with FILTER NOT EXISTS. That "
        "is a fact about the data rather than a fault, so the shape reports "
        "it as a warning. bt:GenreInUse combines an inverse with an "
        "alternative: a concept is reached backwards along bs:genre from a "
        "work or backwards along bs:specialises from a shop, and a concept "
        "reached by neither is reported as information: five of them, the "
        "scheme's top concept and its broad divisions among them, which works "
        "are filed beneath rather than under. The three other "
        "shapes check that every shop has held an event, every author has a "
        "work and every publisher has published, and report nothing on the "
        "clean data.",
    diagram="""
   forward      bt:shop-inkwell --bs:locatedIn--> bt:place-wigtown
   inverse      bt:place-wigtown --[ sh:inversePath bs:locatedIn ]--> bt:shop-inkwell, bt:shop-marginalia

   sh:targetClass bs:Settlement ; sh:path [ sh:inversePath bs:locatedIn ] ; sh:minCount 1
        bt:place-durham   ->  no shops  ->  warning   (q16 in the SPARQL course)

   [ sh:alternativePath ( [ sh:inversePath bs:genre ] [ sh:inversePath bs:specialises ] ) ]
        a concept nobody files a book under and no shop specialises in
""",
    learn=[
        "An inverse path turns 'what does this point at' into 'what points at this'. Constraints on the count then read as 'is this used'.",
        "A shape can be a question. Warning and Info severities keep the answers out of the conformance verdict.",
        "Inverse, sequence and alternative paths nest freely. Read a compound path from the outside in.",
    ],
    body="""
bt:TownWithShop
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:property [
        sh:path      [ sh:inversePath bs:locatedIn ] ;
        sh:minCount  1 ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} has no bookshop. Four towns do not; see q16 in the SPARQL course." ;
    ] .

bt:GenreInUse
    a               sh:NodeShape ;
    sh:targetClass  skos:Concept ;
    sh:property [
        sh:path      [ sh:alternativePath ( [ sh:inversePath bs:genre ] [ sh:inversePath bs:specialises ] ) ] ;
        sh:minCount  1 ;
        sh:severity  sh:Info ;
        sh:message   "No work is filed under {$this} and no shop specialises in it." ;
    ] .

bt:ShopWithEvents
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path [ sh:inversePath bs:heldAt ] ; sh:minCount 1 ;
                  sh:message "{$this} has never held an event." ] .

bt:AuthorWithWork
    a               sh:NodeShape ;
    sh:targetClass  bs:Author ;
    sh:property [ sh:path [ sh:inversePath bs:author ] ; sh:minCount 1 ] .

bt:PublisherWithWork
    a               sh:NodeShape ;
    sh:targetClass  bs:Publisher ;
    sh:property [ sh:path [ sh:inversePath bs:publishedBy ] ; sh:minCount 1 ] .
""",
    data=D11,
    expect=dict(conforms=True, violations=0, warnings=4, min_infos=1,
                focus=["place-durham", "place-perth", "place-fort-william", "place-truro"]),
)
specs.register("s21", "pathInverse", "pathAlternative")

s(
    sid="s22", module=M,
    title="Any number of hops",
    asks="Every genre leads up to the top concept, and every place leads up to Great Britain.",
    how="[ sh:zeroOrMorePath skos:broader ] at a concept yields the concept "
        "itself and everything above it, however far up. sh:hasValue "
        "bt:genre-literature asks for the top of the scheme among them. Three "
        "concepts in the faulty data never get there: bt:genre-stray, which "
        "is under nothing (F29), and the two that are each broader than the "
        "other (F30) -- the walk goes round for ever in the data, and the "
        "path evaluation still terminates, because a path visits each node "
        "once. The same shape on bs:within finds the two council areas inside "
        "each other (F27). [ sh:zeroOrOnePath bs:translationOf ] is the third "
        "form: the focus node, or the one step from it; bt:WorkHasAuthor uses "
        "it to say a work or the work it translates has an author.",
    diagram="""
   [ sh:zeroOrMorePath skos:broader ]   from bt:genre-cosy-crime
        { cosy-crime, crime-fiction, fiction, literature }        literature present: ok

   from bt:genre-loop-a    { loop-a, loop-b }    round and round, visited once each
                                                  literature absent: violation

   [ sh:zeroOrOnePath bs:translationOf ]   { the work, the work it translates if any }
""",
    learn=[
        "zeroOrMore includes the start; oneOrMore does not. When the start could itself satisfy the constraint, that matters.",
        "A cycle in the data does not stop a path. It stops a constraint from ever being satisfied, which is how you find the cycle.",
        "hasValue over a * or + path is the SHACL spelling of 'reachable from'.",
    ],
    body="""
bt:GenreReachesTop
    a               sh:NodeShape ;
    sh:targetClass  skos:Concept ;
    sh:property [
        sh:path      [ sh:zeroOrMorePath skos:broader ] ;
        sh:hasValue  bt:genre-literature ;
        sh:message   "{$this} does not lead up to the top of the genre scheme." ;
    ] .

bt:PlaceReachesGB
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:property [
        sh:path      [ sh:zeroOrMorePath bs:within ] ;
        sh:hasValue  bt:place-gb ;
        sh:message   "{$this} is not inside Great Britain at any depth." ;
    ] .

bt:WorkHasAuthor
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [
        sh:path      ( [ sh:zeroOrOnePath bs:translationOf ] bs:author ) ;
        sh:minCount  1 ;
        sh:message   "Neither {$this} nor the work it translates names an author." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=5,
                focus=["genre-stray", "genre-loop-a", "genre-loop-b", "place-loop-a", "place-loop-b"]),
)
specs.register("s22", "pathZeroOrMore", "pathZeroOrOne")

s(
    sid="s23", module=M,
    title="Either route, and the path in the report",
    asks="Every shop has a trail neighbour in one direction or the other; which shops are junctions; and what a compound path looks like in the report graph.",
    how="bs:connectsTo is asserted in one direction per segment, so a shop's "
        "neighbours are the union of what it connects to and what connects to "
        "it: [ sh:alternativePath ( bs:connectsTo [ sh:inversePath "
        "bs:connectsTo ] ) ]. Every shop has at least one, so bt:Connected "
        "reports nothing. bt:Junction uses the same path with sh:maxCount 2 "
        "and severity Info, which lists the shops with three or more "
        "neighbours: the points where the SPARQL course's two branches leave "
        "the main line. "
        "Open the report as a tab and look at sh:resultPath: it is not an IRI "
        "but a blank node carrying sh:alternativePath, an rdf:List and an "
        "sh:inversePath, a copy of the path from the shapes graph. The editor "
        "renders it as an expression; the query below reads it as RDF.",
    diagram="""
   [ sh:alternativePath ( bs:connectsTo [ sh:inversePath bs:connectsTo ] ) ]

   bt:shop-inkwell --connectsTo--> bt:shop-marginalia          forward
   bt:shop-quire   --connectsTo--> bt:shop-inkwell             backward from the Inkwell's side
        neighbours of the Inkwell: { marginalia, quire, ... }

   in the report:
   _:r  sh:resultPath  [ sh:alternativePath ( bs:connectsTo [ sh:inversePath bs:connectsTo ] ) ]
        a structure, not a name; the editor shows it as (bs:connectsTo | ^bs:connectsTo)
""",
    learn=[
        "An alternative path is a union of routes. It is how you treat an asserted-one-way property as symmetric.",
        "sh:resultPath carries the path as it was written, structure and all. Code that reads reports must expect a blank node there.",
        "sh:maxCount with an Info severity lists the nodes above a threshold without failing anything.",
    ],
    body="""
bt:Connected
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      [ sh:alternativePath ( bs:connectsTo [ sh:inversePath bs:connectsTo ] ) ] ;
        sh:minCount  1 ;
        sh:message   "{$this} is on no trail segment." ;
    ] .

bt:Junction
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      [ sh:alternativePath ( bs:connectsTo [ sh:inversePath bs:connectsTo ] ) ] ;
        sh:maxCount  2 ;
        sh:severity  sh:Info ;
        sh:message   "{$this} is a junction: three or more neighbours on the trail." ;
    ] .
""",
    data=D11,
    expect=dict(conforms=True, violations=0, min_infos=1),
    queries=[Query("The path structure inside a result", """
PREFIX sh:  <http://www.w3.org/ns/shacl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?focus ?first ?inverseOf
WHERE {
  ?r sh:focusNode ?focus ;
     sh:resultPath ?path .
  ?path sh:alternativePath ?list .
  ?list rdf:first ?first ;
        rdf:rest/rdf:first ?second .
  ?second sh:inversePath ?inverseOf .
}
LIMIT 5""")],
)
specs.register("s23", "pathAlternative", "resultPath")
