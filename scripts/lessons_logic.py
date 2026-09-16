# -*- coding: utf-8 -*-
"""Module 04 -- Shapes inside shapes, and logic."""
from shapecat import s, Query, D11, DFAULTY
import specs

M = "04-shapes-and-logic"

s(
    sid="s24", module=M,
    title="A shape for the value",
    asks="A work's publisher is a well-formed publisher; a stock record's shop is a well-formed shop -- typed or not.",
    how="sh:node hands each value to another node shape and asks whether it "
        "conforms. bt:PublisherShape has no target of its own: it is only "
        "ever reached through sh:node, and it says a publisher has a name and "
        "is located in at most one settlement. bt:pub-orbit (F19) is located "
        "in a country, so the work it published fails. The result is on the "
        "work, names the publisher as the value, and says no more: what "
        "went wrong inside the nested check is not reported. Compare "
        "sh:class in s12. The record at the untyped Ghost Shop fails "
        "sh:class bs:Bookshop because the shop has no type, and passes "
        "sh:node bt:ShopShape because it has everything the shape asks for. "
        "The record at The Foxed Page is the other way round: typed, so it "
        "passes sh:class, and not well formed, so it fails sh:node.",
    diagram="""
   bt:WorkShape                            bt:PublisherShape   (no target)
     sh:property [                           sh:property [ rdfs:label   minCount 1 ]
        sh:path bs:publishedBy ;             sh:property [ bs:locatedIn maxCount 1 ; class bs:Settlement ]
        sh:node bt:PublisherShape ]  ---->   conformance check of the value, yes or no
                                             |
   bt:book-unnumbered bs:publishedBy bt:pub-orbit     pub-orbit locatedIn bt:place-wales: no
        result on bt:book-unnumbered, value bt:pub-orbit, NodeConstraintComponent

   sh:class  asks  what is it typed as?            ghost shop: fails    foxed page: passes
   sh:node   asks  does it look right?             ghost shop: passes   foxed page: fails
""",
    learn=[
        "sh:node is a conformance check of the value against a node shape: a boolean. The inner results are not in the report.",
        "A shape with no target is a definition. Give it a name and reuse it from as many sh:node constraints as you like.",
        "sh:class tests rdf:type; sh:node tests structure. Data that is described but not typed needs the second.",
    ],
    body="""
bt:PublisherShape
    a  sh:NodeShape ;
    sh:property [ sh:path rdfs:label ;   sh:minCount 1 ] ;
    sh:property [ sh:path bs:locatedIn ; sh:maxCount 1 ; sh:class bs:Settlement ] .

bt:ShopShape
    a  sh:NodeShape ;
    sh:property [ sh:path rdfs:label ;   sh:minCount 1 ] ;
    sh:property [ sh:path bs:locatedIn ; sh:minCount 1 ; sh:nodeKind sh:IRI ] ;
    sh:property [ sh:path bs:founded ;   sh:minCount 1 ; sh:datatype xsd:gYear ] .

bt:WorkShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [
        sh:path     bs:publishedBy ;
        sh:node     bt:PublisherShape ;
        sh:message  "{$value} is not a well-formed publisher." ;
    ] .

bt:StockShopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [
        sh:path     bs:atShop ;
        sh:node     bt:ShopShape ;
        sh:message  "{$value} does not look like a shop." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=2, focus=["book-unnumbered", "stock-foxed-page"], nofocus=["stock-ghost"]),
)
specs.register("s24", "node", "class")

s(
    sid="s25", module=M,
    title="Not",
    asks="A bookshop is not a publisher, a settlement is not a shop, and nobody specialises in 'Literature'.",
    how="sh:not takes a shape and passes a node that does not conform to it. "
        "On a node shape it tests the focus node: bt:BookshopShape says a "
        "shop does not conform to [ sh:class bs:Publisher ], and the shop "
        "that is typed as both (F03) fails. The vocabulary declares the two "
        "classes disjoint with owl:AllDisjointClasses; that is a statement "
        "for a reasoner, and this is the same statement for a validator. On "
        "a property shape sh:not tests each value: [ sh:hasValue "
        "bt:genre-literature ] as a node shape means 'is that node', so "
        "sh:not of it means 'is not that node', and no shop specialises in "
        "the top of the scheme.",
    diagram="""
   sh:not S      passes n   when   n does not conform to S

   bt:shop-halfmoon  a bs:Bookshop, bs:Publisher
        conforms to [ sh:class bs:Publisher ]  ->  sh:not fails  ->  violation

   sh:property [ sh:path bs:specialises ; sh:not [ sh:hasValue bt:genre-literature ] ]
        each value v:  v conforms to [ sh:hasValue X ]  iff  v = X
""",
    learn=[
        "sh:not is a conformance check turned round. Anything that can be a shape can be negated.",
        "owl:disjointWith is advice to a reasoner; sh:not [ sh:class ... ] is the check.",
        "A node shape with sh:hasValue and no path tests whether the node is that value. Inside sh:not it is 'anything but'.",
    ],
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:not          [ sh:class bs:Publisher ] ;
    sh:message      "{$this} is typed as both a bookshop and a publisher; the vocabulary says those are disjoint." ;
    sh:property [
        sh:path     bs:specialises ;
        sh:not      [ sh:hasValue bt:genre-literature ] ;
        sh:message  "A specialism narrower than the whole of literature, please." ;
    ] .

bt:SettlementShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:not          [ sh:class bs:Bookshop ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=1, focus=["shop-halfmoon"]),
)
specs.register("s25", "not", "logical")

s(
    sid="s26", module=M,
    title="Or, and, exactly one",
    asks="A work has an ISBN or predates them; a place is exactly one kind of place; a shop is named and located.",
    how="sh:or, sh:and and sh:xone each take a list of shapes and combine "
        "the conformance checks. bt:WorkShape says a work conforms to one of "
        "two shapes: it has an ISBN, or its year matches a pattern for 1000 "
        "to 1969 -- sh:pattern works on the lexical form, so it can do to a "
        "gYear what sh:maxInclusive cannot. Eleven clean works from before "
        "1970 pass by the second branch; the 1998 work without an ISBN (F12) "
        "fails both. bt:PlaceKind uses sh:xone: a place is exactly one of "
        "country, region, council area, settlement. Great Britain is none of "
        "them, and it is reported -- on the clean data as well. That is a "
        "true finding about how the data was modelled, and "
        "bt:PlaceKindFixed records the decision by adding a fifth branch for "
        "the one node with skos:notation \"GB\". bt:ShopShape uses sh:and to "
        "compose two named shapes; the shop with no name (F01) fails the "
        "first of them.",
    diagram="""
   sh:or   ( S1 S2 )     at least one conforms
   sh:and  ( S1 S2 )     all conform
   sh:xone ( S1 S2 )     exactly one conforms

   bt:book-unnumbered   isbn? no    year 1998 matches ^1[0-8]..|^19[0-6]. ? no    -> or fails
   bt:book-hedgerow-alphabet   isbn? no    year 1966 matches                       -> or passes

   bt:place-gb   Country? Region? CouncilArea? Settlement?   none  -> xone fails
                 ... or skos:notation "GB"?                  yes   -> fixed xone passes
""",
    learn=[
        "The list operators combine conformance checks of the focus node. Each branch is a full shape and can be as complex as you like.",
        "sh:pattern on a year is a way round the gYear comparison problem when the range has a lexical description.",
        "A finding on clean data is a modelling decision surfacing. Change the shape to record the decision, and say why in a comment.",
    ],
    body="""
bt:WorkShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:or (
        [ sh:property [ sh:path bs:isbn ; sh:minCount 1 ] ]
        [ sh:property [ sh:path bs:publicationYear ; sh:pattern "^(1[0-8][0-9][0-9]|19[0-6][0-9])$" ] ]
    ) ;
    sh:message  "{$this} has no ISBN and was published after 1969." .

# A place is exactly one kind of place. Great Britain is none of them.
bt:PlaceKind
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:xone (
        [ sh:class bs:Country ]
        [ sh:class bs:Region ]
        [ sh:class bs:CouncilArea ]
        [ sh:class bs:Settlement ]
    ) ;
    sh:message  "{$this} is not exactly one kind of place." .

# The same rule, with the root of the hierarchy allowed for.
bt:PlaceKindFixed
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:xone (
        [ sh:class bs:Country ]
        [ sh:class bs:Region ]
        [ sh:class bs:CouncilArea ]
        [ sh:class bs:Settlement ]
        [ sh:property [ sh:path skos:notation ; sh:hasValue "GB" ] ]
    ) .

bt:Named    a sh:NodeShape ; sh:property [ sh:path rdfs:label ;   sh:minCount 1 ] .
bt:Located  a sh:NodeShape ; sh:property [ sh:path bs:locatedIn ; sh:minCount 1 ] .

bt:ShopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:and          ( bt:Named bt:Located ) ;
    sh:message      "{$this} is not both named and located." .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=3, focus=["book-unnumbered", "place-gb", "shop-halfmoon"]),
)
specs.register("s26", "or", "xone")

s(
    sid="s27", module=M,
    title="Closed shapes",
    asks="A bookshop has no properties other than the ones listed, and the typo bs:foundedIn is caught.",
    how="sh:closed true turns a node shape into an allow-list: any predicate "
        "on the focus node that is not the sh:path of one of its property "
        "shapes, and not in sh:ignoredProperties, is a violation. The "
        "Inkwell carries bs:foundedIn (F05), a misspelling of bs:founded that "
        "nothing else in this course notices, because every other shape looks "
        "for the properties it knows about and ignores the rest. The cost is "
        "that the shape must list every legitimate property, including the "
        "geometry and coordinate ones, and rdf:type has to be ignored "
        "explicitly. bt:SettlementClosed shows the other common addition: "
        "some places carry owl:sameAs links to DBpedia, which the shape "
        "ignores rather than lists. Remove owl:sameAs from its "
        "sh:ignoredProperties and validate again to see them.",
    diagram="""
   sh:closed true ; sh:ignoredProperties ( rdf:type )
   allowed:  the sh:path of every sh:property on the shape, plus the ignored list

   bt:shop-inkwell
     rdf:type          ignored
     rdfs:label        listed
     bs:locatedIn      listed
     bs:founded        listed
     bs:foundedIn      not listed   ->  violation, value "1979"^^xsd:gYear
     ...

   the SPARQL course's q96 finds the same kind of mistake with a query
""",
    learn=[
        "A closed shape is the only Core check that notices a property you did not expect. It is how a typo in a predicate gets found.",
        "Every legitimate property must be listed, with or without constraints. An empty property shape [ sh:path p ] is enough to allow p.",
        "sh:ignoredProperties is for the properties you allow but do not want to enumerate: rdf:type, and links added by other tools.",
    ],
    body="""
bt:BookshopClosed
    a                     sh:NodeShape ;
    sh:targetClass        bs:Bookshop ;
    sh:closed             true ;
    sh:ignoredProperties  ( rdf:type ) ;
    sh:message            "{$this} has a property this shape does not know: {$path}." ;
    sh:property [ sh:path rdfs:label ] ;
    sh:property [ sh:path bs:locatedIn ] ;
    sh:property [ sh:path bs:founded ] ;
    sh:property [ sh:path bs:floorArea ] ;
    sh:property [ sh:path bs:staffCount ] ;
    sh:property [ sh:path bs:specialises ] ;
    sh:property [ sh:path bs:sellsSecondHand ] ;
    sh:property [ sh:path bs:hasCafe ] ;
    sh:property [ sh:path bs:website ] ;
    sh:property [ sh:path bs:connectsTo ] ;
    sh:property [ sh:path bs:stocks ] ;
    sh:property [ sh:path wgs84:lat ] ;
    sh:property [ sh:path wgs84:long ] ;
    sh:property [ sh:path geo:hasGeometry ] ;
    sh:property [ sh:path geo:hasDefaultGeometry ] ;
    sh:property [ sh:path sh:shape ] .

bt:SettlementClosed
    a                     sh:NodeShape ;
    sh:targetClass        bs:Settlement ;
    sh:closed             true ;
    sh:ignoredProperties  ( rdf:type owl:sameAs ) ;
    sh:property [ sh:path rdfs:label ] ;
    sh:property [ sh:path bs:within ] ;
    sh:property [ sh:path bs:population ] ;
    sh:property [ sh:path bs:isBookTown ] ;
    sh:property [ sh:path wgs84:lat ] ;
    sh:property [ sh:path wgs84:long ] ;
    sh:property [ sh:path geo:hasGeometry ] ;
    sh:property [ sh:path geo:hasDefaultGeometry ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=1, focus=["shop-inkwell"]),
)
specs.register("s27", "closed")

s(
    sid="s28", module=M,
    title="Some of the values",
    asks="A shop is in exactly one country; every country contains a book town; no council area contains two.",
    how="sh:class on a path with many values requires all of them to be of "
        "the class. To say 'at least one of them is', use "
        "sh:qualifiedValueShape with sh:qualifiedMinCount: the values that "
        "conform to the qualified shape are counted, and the count is "
        "compared. bt:ShopInOneCountry walks up from the shop's town through "
        "every bs:within and requires exactly one of the places reached to be "
        "a bs:Country. On the faulty data The Inkwell, placed in Wigtown and "
        "Hay-on-Wye (F04), reaches Scotland and Wales, and The Foxed Page, "
        "placed in a string, reaches nothing. bt:CouncilAreaBookTowns looks "
        "down instead, with an inverse path, and sh:qualifiedMaxCount 1 "
        "catches Powys once Newtown (F25) joins Hay-on-Wye as a book town.",
    diagram="""
   sh:path ( bs:locatedIn [ sh:oneOrMorePath bs:within ] )
   bt:shop-inkwell  ->  { wigtown's areas ..., scotland, gb,  hay's areas ..., wales }
                        qualified shape [ sh:class bs:Country ]:  scotland, wales  ->  2
                        sh:qualifiedMinCount 1  ok      sh:qualifiedMaxCount 1  violation

   sh:path [ sh:inversePath bs:within ]   at bt:place-powys
                        { hay-on-wye, newtown, ... }
                        qualified shape [ bs:isBookTown true ]:  2   ->  qualifiedMaxCount 1 fails
""",
    learn=[
        "A plain constraint on a property shape applies to every value. A qualified value shape counts the values that conform to it.",
        "qualifiedMinCount 1 is 'some value is a ...'; qualifiedMinCount 1 with qualifiedMaxCount 1 is 'exactly one value is a ...'.",
        "sh:qualifiedValueShapesDisjoint true stops one value from being counted by two sibling qualified shapes on the same property shape.",
    ],
    body="""
bt:ShopInOneCountry
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path                 ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) ;
        sh:qualifiedValueShape  [ sh:class bs:Country ] ;
        sh:qualifiedMinCount    1 ;
        sh:qualifiedMaxCount    1 ;
        sh:message              "{$this} is in some number of countries other than one." ;
    ] .

bt:CountryHasBookTown
    a               sh:NodeShape ;
    sh:targetClass  bs:Country ;
    sh:property [
        sh:path                 [ sh:inversePath [ sh:oneOrMorePath bs:within ] ] ;
        sh:qualifiedValueShape  [ sh:property [ sh:path bs:isBookTown ; sh:hasValue true ] ] ;
        sh:qualifiedMinCount    1 ;
        sh:message              "{$this} has no book town." ;
    ] .

bt:CouncilAreaBookTowns
    a               sh:NodeShape ;
    sh:targetClass  bs:CouncilArea ;
    sh:property [
        sh:path                 [ sh:inversePath bs:within ] ;
        sh:qualifiedValueShape  [ sh:property [ sh:path bs:isBookTown ; sh:hasValue true ] ] ;
        sh:qualifiedMaxCount    1 ;
        sh:message              "{$this} contains more than one book town." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=3, focus=["shop-inkwell", "shop-foxed-page", "place-powys"]),
)
specs.register("s28", "qualified")

s(
    sid="s29", module=M,
    title="A shape that refers to itself",
    asks="A place conforms if every place above it conforms -- and what that finds, and what it cannot.",
    how="bt:PlaceShape requires a geometry, and requires the place's "
        "bs:within to conform to bt:PlaceShape. The specification says the "
        "result of validating a recursive shape is undefined; this engine "
        "follows the reference and treats a check that is already in "
        "progress for the same node and shape as passing. Two things follow. "
        "Wigtown has a geometry and so does everything above it except Great "
        "Britain, three hops up, which has none; the failure surfaces at "
        "Wigtown as a sh:node result naming Dumfries and Galloway, with no "
        "trace of where in the chain it came from. And the two council areas "
        "inside each other (F27) do not trip the recursion at all: Loop A "
        "fails only because it has no geometry itself. The path shapes of "
        "s22 answer both questions better -- a cycle is a place that never "
        "reaches Great Britain, and a missing geometry is a result on the "
        "place that lacks it.",
    diagram="""
   bt:PlaceShape
     geo:hasGeometry minCount 1
     bs:within  sh:node bt:PlaceShape      <- refers to itself

   wigtown -> dumfries-galloway -> scotland -> gb (no geometry)
      ^ one result here: "something above dumfries-galloway does not conform"

   loop-a -> loop-b -> loop-a (in progress: assumed to conform) ...
      results: loop-a has no geometry; loop-a's bs:within fails sh:node because loop-b has none
      the cycle itself is never reported
""",
    learn=[
        "Recursive shapes are allowed by the syntax and undefined by the specification. Engines differ; this one terminates and assumes an in-progress check passes.",
        "A failure deep inside a sh:node chain is reported at the top with no detail. For a long chain, prefer a path and constrain the nodes it reaches.",
        "A cycle in the data is found by a reachability constraint, not by recursion.",
    ],
    body="""
bt:PlaceShape
    a              sh:NodeShape ;
    sh:targetNode  bt:place-wigtown, bt:place-loop-a ;
    sh:property [
        sh:path      geo:hasGeometry ;
        sh:minCount  1 ;
        sh:message   "{$this} has no geometry." ;
    ] ;
    sh:property [
        sh:path      bs:within ;
        sh:maxCount  1 ;
        sh:node      bt:PlaceShape ;
        sh:message   "Something above {$value} does not conform to bt:PlaceShape." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=3, focus=["place-wigtown", "place-loop-a"]),
)
specs.register("s29", "recursion", "node")
