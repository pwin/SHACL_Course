# -*- coding: utf-8 -*-
"""Module 05 -- Targets and constraints in SPARQL."""
from shapecat import s, Query, D11, DFAULTY
import specs

M = "05-sparql-constraints"

s(
    sid="s30", module=M,
    title="The constraint you cannot write in Core",
    asks="Nothing contains itself: no place, genre, publisher or author is above itself in its own hierarchy.",
    how="A sh:sparql constraint holds a SELECT query. The engine runs it once "
        "per focus node with $this bound to that node, and every row that "
        "comes back is a validation result. 'This place is inside itself' is "
        "$this bs:within+ $this -- a property path back to the start, which "
        "no Core component can express. The prefixes the query uses are "
        "declared with sh:declare on bt:prefixes and named by sh:prefixes; "
        "the @prefix lines at the top of the file are Turtle syntax and never "
        "reach the query engine. Four shapes, one pattern. The two council "
        "areas inside each other (F27), the two genres broader than each "
        "other (F30) and the publisher that is an imprint of itself (F19) "
        "are violations. bt:InfluenceShape is a warning, because the clean "
        "data has a cycle of three authors on purpose -- the SPARQL course's "
        "q34 -- and the author influenced by himself (F18) joins them.",
    diagram="""
   sh:sparql [
       sh:prefixes  bt:prefixes ;                <- names the sh:declare block
       sh:select    "SELECT $this WHERE { $this bs:within+ $this }" ;
   ]

   for each focus node n:   bind $this = n, run the query
        no rows    ->  nothing
        a row      ->  one validation result, focus node n

   bt:place-loop-a --within--> bt:place-loop-b --within--> bt:place-loop-a     a row
""",
    learn=[
        "A SPARQL constraint returns rows; each row is a result. An empty result set is conformance.",
        "$this is the focus node, pre-bound. Every row must have it; project ?value and ?path too if you want them in the result (s32).",
        "Declare prefixes for the query with sh:declare and sh:prefixes. @prefix does not reach it.",
    ],
    body="""
bt:PlaceHierarchyShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} contains itself, directly or through a chain of bs:within." ;
        sh:select    \"\"\"
            SELECT $this WHERE { $this bs:within+ $this }
        \"\"\" ;
    ] .

bt:GenreHierarchyShape
    a               sh:NodeShape ;
    sh:targetClass  skos:Concept ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} is broader than itself." ;
        sh:select    \"\"\"
            SELECT $this WHERE { $this skos:broader+ $this }
        \"\"\" ;
    ] .

bt:ImprintShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Publisher ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} is an imprint of itself." ;
        sh:select    \"\"\"
            SELECT $this WHERE { $this bs:imprintOf+ $this }
        \"\"\" ;
    ] .

# The clean data has one cycle of influence on purpose (q34 in the SPARQL
# course), so this is a warning rather than a violation.
bt:InfluenceShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Author ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} is in a cycle of influence." ;
        sh:select    \"\"\"
            SELECT $this WHERE { $this bs:influencedBy+ $this }
        \"\"\" ;
    ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, violations=5, warnings=4,
                focus=["place-loop-a", "genre-loop-b", "pub-orbit", "author-owen-harker", "author-rab-fingal"]),
)
specs.register("s30", "sparql", "prefixes")

s(
    sid="s31", module=M,
    title="A join, an arithmetic comparison, and $PATH",
    asks="A shelf price is at most twice the recommended price; no work predates its author; an event does not feature the dead.",
    how="Each of these needs a value from a second node, which is a join, "
        "and Core has none. bt:StockPriceShape puts the sh:sparql on a "
        "property shape, where $PATH stands for the shape's sh:path and the "
        "results carry the path automatically. It joins the record to its "
        "work's bs:rrp and compares. The one record at three times the "
        "recommended price (F23) is reported, with the offending price as "
        "?value. bt:WorkAfterBirth joins a work to its author's birth year, "
        "with the STR cast from s14, and finds the book published five years "
        "before its author was born (F11). bt:LivingFeature is on the clean "
        "data too: a lecture in 2025 by an author who died in 2004. That may "
        "be a memorial event or a mistake, so it is a warning. Its year comes "
        "from SUBSTR(STR(?date), 1, 4): YEAR() is defined on xsd:dateTime, and "
        "on an xsd:date this engine leaves it unbound, so the filter would "
        "never be true.",
    diagram="""
   property shape:  sh:path bs:shelfPrice ;  sh:sparql [ ... $this $PATH ?value ... ]
        $PATH is replaced by the shape's path before the query runs
        the result gets sh:resultPath bs:shelfPrice without being told

   $this --shelfPrice--> 68.07
   $this --ofWork--> work --rrp--> 22.69        68.07 > 2 * 22.69  ->  a row

   xsd:integer(SUBSTR(STR("2025-04-05"^^xsd:date), 1, 4)) = 2025
        >  xsd:integer(STR("2004"^^xsd:gYear)) = 2004
   (YEAR() of an xsd:date is unbound on this engine; see q130 in the SPARQL course)
""",
    learn=[
        "A join is a SPARQL constraint. If the condition mentions two nodes, it is not a Core constraint.",
        "On a property shape, $PATH is the shape's path, and the result's path is filled in for you.",
        "Project ?value to say which value the row is about. It becomes sh:value and fills {$value}.",
    ],
    body="""
bt:StockPriceShape
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [
        sh:path  bs:shelfPrice ;
        sh:sparql [
            sh:prefixes  bt:prefixes ;
            sh:message   "{$value} is more than twice the recommended price." ;
            sh:select    \"\"\"
                SELECT $this ?value WHERE {
                  $this $PATH ?value ;
                        bs:ofWork/bs:rrp ?rrp .
                  FILTER ( ?value > 2 * ?rrp )
                }
            \"\"\" ;
        ] ;
    ] .

bt:WorkAfterBirth
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} was published in {$value}, before its author was born." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:publicationYear ?value ;
                    bs:author/bs:born ?born .
              FILTER ( xsd:integer(STR(?value)) < xsd:integer(STR(?born)) )
            }
        \"\"\" ;
    ] .

bt:LivingFeature
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} features {$value}, who had died by then. A memorial, or a mistake?" ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:featuring ?value ; bs:eventDate ?date .
              ?value bs:died ?died .
              FILTER ( xsd:integer(SUBSTR(STR(?date), 1, 4)) > xsd:integer(STR(?died)) )
            }
        \"\"\" ;
    ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, violations=2, warnings=1,
                focus=["stock-foxed-page", "book-precocious", "event-severn-leaf-2025-04-05"]),
)
specs.register("s31", "prebound", "bindings")

s(
    sid="s32", module=M,
    title="What a query can put in the result",
    asks="The six shops without a website again, with the path and the value chosen by the query, and what this engine does with ?message.",
    how="Beyond $this, three projected variables have meaning. ?value becomes "
        "sh:value; ?path becomes sh:resultPath, which is how a node-shape "
        "constraint gets a path into its results; ?message is meant to "
        "override sh:message row by row. bt:NoWebsite binds ?path to "
        "bs:website and ?value to the shop's label, so the rows read as "
        "'this shop, this property, this name'. bt:MessageProbe binds "
        "?message, and its rows still show the sh:message text: this build "
        "ignores a bound ?message, and it also leaves {?var} templates "
        "unfilled. Keep row-specific detail in ?value and the words in "
        "sh:message. sh:severity inside the sh:sparql block works, and is "
        "used here to make both shapes report information rather than "
        "violations. That placement is SHACL 1.2: the 1.0 specification "
        "allows sh:severity on shapes only, and pySHACL, which follows 1.0, "
        "reports these twelve rows as violations. Where shapes have to run "
        "on a 1.0 validator, give the constraint a shape of its own and put "
        "the severity there.",
    diagram="""
   SELECT $this ?value ?path WHERE { ... BIND(bs:website AS ?path) ... }

   projected     becomes              in the message template
   $this         sh:focusNode         {$this}
   ?value        sh:value             {$value}
   ?path         sh:resultPath        {$path}
   ?message      sh:resultMessage     -- not on this engine: sh:message is used

   {?anyOtherVariable}   left as written
""",
    learn=[
        "?value and ?path are the two projections worth using. They shape the row the reader sees.",
        "A node-shape SPARQL constraint has no path unless the query binds ?path.",
        "Portability: ?message and {?var} are in the specification and not in this engine; sh:severity on a sh:sparql block is in SHACL 1.2 and not in 1.0 validators. sh:message with {$value}, and severity on the shape, work everywhere.",
    ],
    body="""
bt:NoWebsite
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$value} has no {$path}." ;
        sh:select    \"\"\"
            SELECT $this ?value ?path WHERE {
              $this rdfs:label ?value .
              FILTER NOT EXISTS { $this bs:website ?w }
              BIND ( bs:website AS ?path )
            }
        \"\"\" ;
    ] .

# Binds ?message. On this engine the rows show sh:message instead.
bt:MessageProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "Text from sh:message. A bound ?message would replace this on an engine that honours it." ;
        sh:select    \"\"\"
            SELECT $this ?message WHERE {
              FILTER NOT EXISTS { $this bs:website ?w }
              BIND ( "Text from the ?message variable." AS ?message )
            }
        \"\"\" ;
    ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, infos=12, violations=0, focus=["shop-signature"]),
)
specs.register("s32", "bindings", "message")

s(
    sid="s33", module=M,
    title="A target written in SPARQL",
    asks="Every book town has a bookshop; a shop with a cafe has room for one; a city has more than one shop.",
    how="A target need not be a class. sh:target [ a sh:SPARQLTarget ; "
        "sh:select ... ] makes the focus nodes whatever the query binds to "
        "?this, and bt:BookTownShape uses it to pick the settlements with "
        "bs:isBookTown true and require at least one shop in each. On the "
        "faulty data Newtown (F25) is a book town with none. SHACL 1.2 "
        "shortens the same idea to sh:target [ sh:select ... ], a select "
        "expression, which bt:CafeShape uses for the shops with a cafe; four "
        "of them have under a hundred square metres, reported as "
        "information. sh:targetWhere, also 1.2, takes a shape instead of a "
        "query: the settlements that conform to 'population at least "
        "100,000' are the cities, and three of them have fewer than two "
        "shops. All three forms run in this engine.",
    diagram="""
   sh:target [ a sh:SPARQLTarget ; sh:select "SELECT ?this WHERE { ?this bs:isBookTown true }" ]
        focus nodes = the bindings of ?this          (SHACL-AF)

   sh:target [ sh:select "..." ]                     (SHACL 1.2: a select expression)

   sh:targetWhere [ sh:class bs:Settlement ; sh:property [ sh:path bs:population ; sh:minInclusive 100000 ] ]
        focus nodes = the nodes that conform to this shape     (SHACL 1.2)
""",
    learn=[
        "A SPARQL target is any SELECT that binds ?this. Use it when the population is defined by a condition rather than a class.",
        "sh:targetWhere is the same idea without SPARQL: the target is 'whatever conforms to this shape'.",
        "A target query that fails to parse selects nothing and reports nothing on this engine. Check the shapes count and keep a canary (s09).",
    ],
    body="""
bt:BookTownShape
    a  sh:NodeShape ;
    sh:target [
        a            sh:SPARQLTarget ;
        sh:prefixes  bt:prefixes ;
        sh:select    "SELECT ?this WHERE { ?this bs:isBookTown true }" ;
    ] ;
    sh:property [
        sh:path      [ sh:inversePath bs:locatedIn ] ;
        sh:minCount  1 ;
        sh:message   "{$this} is a book town with no bookshop." ;
    ] .

# SHACL 1.2: a select expression as the target.
bt:CafeShape
    a  sh:NodeShape ;
    sh:target [
        sh:prefixes  bt:prefixes ;
        sh:select    "SELECT ?this WHERE { ?this bs:hasCafe true }" ;
    ] ;
    sh:property [
        sh:path          bs:floorArea ;
        sh:minInclusive  100 ;
        sh:severity      sh:Info ;
        sh:message       "{$this} has a cafe in {$value} square metres." ;
    ] .

# SHACL 1.2: a shape as the target.
bt:CityShape
    a  sh:NodeShape ;
    sh:targetWhere [
        sh:class     bs:Settlement ;
        sh:property  [ sh:path bs:population ; sh:minInclusive 100000 ] ;
    ] ;
    sh:property [
        sh:path      [ sh:inversePath bs:locatedIn ] ;
        sh:minCount  2 ;
        sh:severity  sh:Info ;
        sh:message   "{$this} is a city with fewer than two shops on the trail." ;
    ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, violations=1, infos=7, focus=["place-newtown", "place-exeter", "shop-penwith"]),
)
specs.register("s33", "afSparqlTarget", "c12targetWhere")

s(
    sid="s34", module=M,
    title="What pre-binding forbids",
    asks="Works nobody stocks -- written the way pre-binding allows, with the three ways it does not.",
    how="$this is pre-bound: the engine substitutes the focus node before "
        "the query runs, and the specification lists what a query may not "
        "then contain. MINUS, VALUES and SERVICE are forbidden, a sub-select "
        "must project $this, and $this may not be assigned with AS. This "
        "engine refuses the whole shapes graph with a message naming the "
        "construct, so the file cannot demonstrate them and stay runnable; "
        "the diagram shows the three forbidden spellings and the text the "
        "engine returns for each. The shape uses FILTER NOT EXISTS, which is "
        "allowed and is what MINUS would have meant, and reports the eight "
        "works no shop stocks as information. The SPARQL course's q17 is "
        "about why MINUS and NOT EXISTS differ; here only one of them is "
        "available.",
    diagram="""
   forbidden                                          the engine says
   SELECT $this WHERE { $this a bs:Work
       MINUS { ?r bs:ofWork $this } }                 MINUS cannot be combined with SHACL pre-binding
   SELECT $this WHERE { VALUES $this { ... } }        VALUES cannot be combined with SHACL pre-binding
   SELECT $this WHERE { SERVICE <...> { ... } }       SERVICE cannot be combined with SHACL pre-binding

   allowed
   SELECT $this WHERE { FILTER NOT EXISTS { ?r bs:ofWork $this } }
   SELECT $this WHERE { { SELECT $this (COUNT(?x) AS ?n) WHERE { ... } GROUP BY $this } ... }
""",
    learn=[
        "Pre-binding is substitution, and MINUS, VALUES and SERVICE do not survive it. Write NOT EXISTS, put the list in the shapes graph (s37), and keep remote data out of shapes.",
        "A sub-select inside a constraint must project $this, or the outer pattern has nothing to join on.",
        "This engine fails loudly on all three. Some validators do not; a shape that passes everywhere but one engine is worth a second look at its query.",
    ],
    tryit="Replace FILTER NOT EXISTS { ?r bs:ofWork $this } with MINUS { ?r bs:ofWork $this } "
          "and validate. The engine refuses the shapes graph and names MINUS.",
    body="""
bt:UnstockedWork
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "No shop on the trail stocks {$this}." ;
        sh:select    \"\"\"
            SELECT $this WHERE {
              FILTER NOT EXISTS { ?record bs:ofWork $this }
            }
        \"\"\" ;
    ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, infos=8, violations=0, focus=["book-the-shieling"]),
)
specs.register("s34", "prebinding", "prebound")

s(
    sid="s35", module=M,
    title="Aggregation in a constraint",
    asks="No shop holds more than a hundred copies in total, and no shop has held more than three events.",
    how="A SPARQL constraint can aggregate, as long as the grouping keeps "
        "$this. bt:StockTotal sums bs:copies over every record at the shop, "
        "GROUP BY $this, and keeps the groups over a hundred with HAVING. One "
        "shop on the clean data, Ex Libris, holds 101. bt:BusyShop counts "
        "events the same way. Both are facts rather than faults, so both "
        "are warnings or information. One limitation of this build: an "
        "aggregate projected as ?value does not reach the result, so the "
        "rows name the shop and not the total. The SPARQL course's module 04 "
        "is the reference for the aggregation itself.",
    diagram="""
   SELECT $this WHERE {
     { SELECT $this (SUM(?c) AS ?total)
       WHERE { ?r bs:atShop $this ; bs:copies ?c }
       GROUP BY $this }
     FILTER ( ?total > 100 )
   }

   $this is pre-bound in the inner query too: one group, one row, one test
   bt:shop-ex-libris   101   ->  a row
""",
    learn=[
        "Aggregate inside a sub-select that groups by $this and projects it; test the total outside.",
        "HAVING and a FILTER on the projected total are equivalent here. The sub-select form is the one that keeps $this in scope for both.",
        "On this engine an aggregate does not become sh:value. Say the threshold in sh:message; the focus node says which shop.",
    ],
    body="""
bt:StockTotal
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} holds more than a hundred copies in total." ;
        sh:select    \"\"\"
            SELECT $this WHERE {
              { SELECT $this (SUM(?c) AS ?total)
                WHERE { ?record bs:atShop $this ; bs:copies ?c }
                GROUP BY $this }
              FILTER ( ?total > 100 )
            }
        \"\"\" ;
    ] .

bt:BusyShop
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} has held more than three events." ;
        sh:select    \"\"\"
            SELECT $this WHERE {
              { SELECT $this (COUNT(?event) AS ?n)
                WHERE { ?event bs:heldAt $this }
                GROUP BY $this }
              FILTER ( ?n > 3 )
            }
        \"\"\" ;
    ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, warnings=1, infos=1, focus=["shop-ex-libris"]),
)
specs.register("s35", "sparqlAggregates", "prebound")

s(
    sid="s36", module=M,
    title="Reachability as a constraint",
    asks="Every shop can be walked to from The Inkwell -- and two cannot, by design.",
    how="The SPARQL course's q31 and q32 walk the trail with the path "
        "(bs:connectsTo|^bs:connectsTo)+ and find that two shops in the "
        "south west connect only to each other. The same path inside FILTER "
        "NOT EXISTS is a constraint: a shop that the path from The Inkwell "
        "never reaches is reported. The shape comes from the SPARQL course's "
        "shapes-advanced.ttl, and it is a warning there for the same reason "
        "it is here: two unreachable shops are the intended shape of the "
        "trail, and a third would be a mistake.",
    diagram="""
   bt:shop-inkwell --(connectsTo | ^connectsTo)+--> every shop on the main line and its branches

   FILTER NOT EXISTS { bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ $this }

   bt:shop-penwith  <--> bt:shop-west-quay        a pair joined to nothing else
        two rows, both warnings
""",
    learn=[
        "A reachability check is a property path from a fixed node to $this, negated.",
        "Constraints written for the SPARQL course's queries port with almost no change: the query becomes the sh:select, the interesting variable becomes $this.",
        "Known exceptions get a warning, not a lower threshold. The report should still say they are there.",
    ],
    body="""
bt:UnreachableShopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} cannot be reached on foot from The Inkwell. Two shops cannot, by design; a third would be a mistake." ;
        sh:select    \"\"\"
            SELECT $this WHERE {
              FILTER NOT EXISTS {
                bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ $this .
              }
            }
        \"\"\" ;
    ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, warnings=2, focus=["shop-penwith", "shop-west-quay"]),
)
specs.register("s36", "sparqlPaths", "sparql")

s(
    sid="s37", module=M,
    title="Two graphs, one constraint",
    asks="An event's kind is one the shapes graph lists -- with the list kept as data in the shapes graph, not in a sh:in.",
    how="A SPARQL constraint can see the shapes graph as well as the data, "
        "through the pre-bound $shapesGraph. bt:eventKinds is an ordinary "
        "node in the shapes file with one bs:allows per kind, and the query "
        "asks, for each value of bs:eventKind, whether GRAPH $shapesGraph "
        "holds it. The list can now be edited, queried and reused without "
        "touching the constraint, which sh:in does not allow. The event whose "
        "kind is \"Recital\" (F20) is the one result. s34 said VALUES is "
        "forbidden under pre-binding; this is where a list goes instead.",
    diagram="""
   shapes graph                                  data graph
   bt:eventKinds bs:allows "Reading", "Signing", ...    bt:event-... bs:eventKind "Recital"

   SELECT $this ?value WHERE {
     $this bs:eventKind ?value .
     FILTER NOT EXISTS { GRAPH $shapesGraph { bt:eventKinds bs:allows ?value } }
   }
""",
    learn=[
        "$shapesGraph gives a constraint read access to the shapes graph. Reference data that belongs with the shapes can live there.",
        "The specification makes $shapesGraph optional; this engine supports it. Say so in a comment if the shapes may move.",
        "sh:in for a short fixed list; a lookup in $shapesGraph or in the data graph for a longer or shared one.",
    ],
    body="""
bt:eventKinds
    bs:allows  "Reading", "Signing", "Panel", "Workshop", "Launch", "Lecture", "Book Club" .

bt:EventKindShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$value} is not a kind of event listed in the shapes graph." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:eventKind ?value .
              FILTER NOT EXISTS { GRAPH $shapesGraph { bt:eventKinds bs:allows ?value } }
            }
        \"\"\" ;
    ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, violations=1, focus=["event-foxed-page"]),
)
specs.register("s37", "prebound", "in")

s(
    sid="s38", module=M,
    title="The report is a graph",
    asks="A short shapes graph that finds a dozen faults, and three queries over its report.",
    how="Press Validate, then Report as tab. What opens is an RDF graph: one "
        "sh:ValidationReport with sh:conforms and one sh:result per row, each "
        "a sh:ValidationResult. The SPARQL panel now queries that tab, so the "
        "report can be summarised the way any graph can. The first query "
        "counts results by severity; the second by the constraint component "
        "that produced them; the third lists the focus nodes with the most "
        "results, which is where to start fixing. The SPARQL course's q88 "
        "produces a report of this shape from a query; here the validator "
        "produces it and the query reads it. Note that the report tab does "
        "not contain the data: to join a result to its focus node's label, "
        "paste the report into the data tab first, or use the CONSTRUCT in "
        "module 11.",
    diagram="""
   _:report  a sh:ValidationReport ;
             sh:conforms false ;
             sh:result _:r1, _:r2, ... .

   _:r1  a sh:ValidationResult ;
         sh:focusNode bt:shop-foxed-page ;
         sh:resultPath bs:founded ;
         sh:value "1985"^^xsd:integer ;
         sh:resultSeverity sh:Violation ;
         sh:sourceConstraintComponent sh:DatatypeConstraintComponent ;
         sh:sourceShape <...> ;
         sh:resultMessage "..." .

   Validate  ->  Report as tab  ->  the SPARQL panel now sees this graph
""",
    learn=[
        "The report is RDF. Everything the SPARQL course teaches about querying applies to it.",
        "Group by severity to see how bad; by component to see what kind of wrong; by focus node to see where to start.",
        "The report and the data are separate graphs in the editor. Joining them needs both in one tab.",
    ],
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path rdfs:label ;    sh:minCount 1 ; sh:datatype rdf:langString ] ;
    sh:property [ sh:path bs:locatedIn ;  sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:Settlement ] ;
    sh:property [ sh:path bs:founded ;    sh:minCount 1 ; sh:datatype xsd:gYear ] ;
    sh:property [ sh:path bs:staffCount ; sh:datatype xsd:integer ; sh:minInclusive 1 ] ;
    sh:property [ sh:path bs:floorArea ;  sh:minExclusive 0 ] ;
    sh:property [ sh:path bs:hasCafe ;    sh:datatype xsd:boolean ] ;
    sh:property [ sh:path bs:website ;    sh:maxCount 1 ; sh:datatype xsd:anyURI ; sh:severity sh:Warning ] .

bt:WorkShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [ sh:path bs:isbn ;  sh:pattern "^97[89][0-9]{10}$" ] ;
    sh:property [ sh:path bs:pages ; sh:minInclusive 1 ] ;
    sh:property [ sh:path bs:rrp ;   sh:minInclusive 0 ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, min_violations=10),
    queries=[
        Query("The headline, as a query", """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?conforms (COUNT(?r) AS ?results)
WHERE {
  ?report a sh:ValidationReport ; sh:conforms ?conforms .
  OPTIONAL { ?report sh:result ?r }
}
GROUP BY ?conforms"""),
        Query("How bad: results by severity", """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?severity (COUNT(?r) AS ?results)
WHERE { ?r a sh:ValidationResult ; sh:resultSeverity ?severity }
GROUP BY ?severity
ORDER BY ?severity"""),
        Query("What kind of wrong: results by constraint component", """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?component (COUNT(?r) AS ?results)
WHERE { ?r a sh:ValidationResult ; sh:sourceConstraintComponent ?component }
GROUP BY ?component
ORDER BY DESC(?results)"""),
        Query("Where to start: the focus nodes with the most results", """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?focus (COUNT(?r) AS ?results) (GROUP_CONCAT(DISTINCT ?path; separator=", ") AS ?paths)
       (GROUP_CONCAT(DISTINCT STR(?value); separator=", ") AS ?values)
WHERE {
  ?r a sh:ValidationResult ; sh:focusNode ?focus .
  OPTIONAL { ?r sh:resultPath ?path }
  OPTIONAL { ?r sh:value ?value }
}
GROUP BY ?focus
ORDER BY DESC(?results)"""),
    ],
)
specs.register("s38", "report", "result")
