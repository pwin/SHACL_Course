# -*- coding: utf-8 -*-
"""Module 11 -- Putting it together."""
from shapecat import s, Query, D11, DFAULTY, RULES
import specs

M = "11-putting-it-together"

# Every focus node the faults file says a shape should find, apart from the
# RDF 1.2 ones (F32 to F36), which module 08 covers.
FAULT_FOCUS = [
    "shop-halfmoon", "shop-inkwell", "shop-foxed-page", "stock-ghost",
    "book-the-margin-notes", "book-precocious", "book-unnumbered", "book-the-dark-sea-fr",
    "author-owen-harker", "pub-orbit", "event-foxed-page", "event-inkwell-2025-06-01",
    "seg-inkwell-inkwell", "stock-foxed-page", "place-newtown", "place-brecon",
    "place-loop-a", "place-loop-b", "place-kendal", "genre-stray", "genre-loop-a",
    "genre-loop-b", "source-rumour", "place-powys",
]

s(
    sid="s64", module=M,
    title="The whole trail in one shapes graph",
    asks="A shapes graph for every class in the dataset, run on the faulty edition. Every numbered fault in data/faults.ttl appears in the report.",
    how="This is the course's shapes in one file, organised the way a real "
        "shapes graph is: one node shape per class, every property shape "
        "named, a message on everything, and severities that say what kind "
        "of finding each is. The Core constraints come from modules 01 to "
        "04, the SPARQL constraints from 05, the ISBN check digit from 06. "
        "Nothing in it compares xsd:gYear values with a Core component; the "
        "year comparisons are SPARQL with the STR cast. On the clean data the "
        "graph reports no violations and six warnings, all of them known "
        "features of the dataset: the two unreachable shops, the three "
        "authors in the cycle of influence, and the lecture given by an "
        "author who had died. On the faulty data it reports every fault "
        "from F01 to F31, and the checker that builds this course confirms "
        "each one is there. Read the report as an answer key: each row's "
        "focus node is a resource the faults file describes.",
    diagram="""
   one node shape per class            bt:BookshopShape, bt:SettlementShape, bt:WorkShape, ...
   named property shapes               bt:BookshopShape-founded, ...
   severities                          Violation for errors, Warning for known exceptions, Info for facts
   SPARQL where Core cannot            cycles, joins, year comparisons
   a constraint component              the ISBN check digit

   clean data:   0 violations, 6 warnings
   faulty data:  every fault F01 to F31, by focus node
""",
    learn=[
        "A shapes graph is a document about the data model. Name the shapes, write the messages, and it reads as one.",
        "Severity is how the graph records what is an error and what is a known feature. A report with warnings and no violations is a clean run.",
        "Keep a faulty edition of the data beside the shapes and run both. A shape that finds nothing in the faulty data is not doing its job.",
    ],
    body="""
# ---------------------------------------------------------------- bookshops

bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:not          [ sh:class bs:Publisher ] ;
    sh:message      "{$this} is typed as both a bookshop and a publisher." ;
    sh:property     bt:BookshopShape-label, bt:BookshopShape-locatedIn, bt:BookshopShape-founded,
                    bt:BookshopShape-staffCount, bt:BookshopShape-floorArea, bt:BookshopShape-hasCafe,
                    bt:BookshopShape-website, bt:BookshopShape-specialises, bt:BookshopShape-country ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} opened in {$value}, before 1800." ;
        sh:select    "SELECT $this ?value WHERE { $this bs:founded ?value . FILTER ( xsd:integer(STR(?value)) < 1800 ) }" ;
    ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} cannot be reached on foot from The Inkwell. Two shops cannot, by design." ;
        sh:select    "SELECT $this WHERE { FILTER NOT EXISTS { bt:shop-inkwell (bs:connectsTo|^bs:connectsTo)+ $this } }" ;
    ] .

bt:BookshopShape-label       a sh:PropertyShape ; sh:path rdfs:label ;
    sh:minCount 1 ; sh:datatype rdf:langString ; sh:languageIn ( "en" "cy" "gd" ) ;
    sh:message "A shop has a name with a language tag." .
bt:BookshopShape-locatedIn   a sh:PropertyShape ; sh:path bs:locatedIn ;
    sh:minCount 1 ; sh:maxCount 1 ; sh:nodeKind sh:IRI ; sh:class bs:Settlement ;
    sh:message "A shop is in exactly one settlement." .
bt:BookshopShape-founded     a sh:PropertyShape ; sh:path bs:founded ;
    sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:gYear ;
    sh:message "A shop records the one year it opened, as an xsd:gYear." .
bt:BookshopShape-staffCount  a sh:PropertyShape ; sh:path bs:staffCount ;
    sh:maxCount 1 ; sh:datatype xsd:integer ; sh:minInclusive 1 ;
    sh:message "Staff count is a positive integer: {$value}." .
bt:BookshopShape-floorArea   a sh:PropertyShape ; sh:path bs:floorArea ;
    sh:maxCount 1 ; sh:datatype xsd:decimal ; sh:minExclusive 0 ;
    sh:message "Floor area is a positive number of square metres: {$value}." .
bt:BookshopShape-hasCafe     a sh:PropertyShape ; sh:path bs:hasCafe ;
    sh:maxCount 1 ; sh:datatype xsd:boolean .
bt:BookshopShape-website     a sh:PropertyShape ; sh:path bs:website ;
    sh:maxCount 1 ; sh:datatype xsd:anyURI ; sh:pattern "^https?://" ;
    sh:message "At most one website, with a scheme: {$value}." .
bt:BookshopShape-specialises a sh:PropertyShape ; sh:path bs:specialises ;
    sh:maxCount 1 ; sh:class skos:Concept ;
    sh:message "A specialism is a concept from the genre scheme, not {$value}." .
bt:BookshopShape-country     a sh:PropertyShape ;
    sh:path ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) ;
    sh:qualifiedValueShape [ sh:class bs:Country ] ; sh:qualifiedMinCount 1 ; sh:qualifiedMaxCount 1 ;
    sh:message "{$this} is in some number of countries other than one." .

bt:BookshopClosed
    a                     sh:NodeShape ;
    sh:targetClass        bs:Bookshop ;
    sh:closed             true ;
    sh:ignoredProperties  ( rdf:type sh:shape ) ;
    sh:message            "{$this} has a property the model does not know: {$path}." ;
    sh:property [ sh:path rdfs:label ] ; sh:property [ sh:path bs:locatedIn ] ;
    sh:property [ sh:path bs:founded ] ; sh:property [ sh:path bs:floorArea ] ;
    sh:property [ sh:path bs:staffCount ] ; sh:property [ sh:path bs:specialises ] ;
    sh:property [ sh:path bs:sellsSecondHand ] ; sh:property [ sh:path bs:hasCafe ] ;
    sh:property [ sh:path bs:website ] ; sh:property [ sh:path bs:connectsTo ] ;
    sh:property [ sh:path bs:stocks ] ; sh:property [ sh:path wgs84:lat ] ;
    sh:property [ sh:path wgs84:long ] ; sh:property [ sh:path geo:hasGeometry ] ;
    sh:property [ sh:path geo:hasDefaultGeometry ] ; sh:property [ sh:path skos:note ] .

# ---------------------------------------------------------------- places

bt:PlaceShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:property     bt:PlaceShape-label, bt:PlaceShape-lat, bt:PlaceShape-long, bt:PlaceShape-reachesGB ;
    sh:xone (
        [ sh:class bs:Country ] [ sh:class bs:Region ] [ sh:class bs:CouncilArea ] [ sh:class bs:Settlement ]
        [ sh:property [ sh:path skos:notation ; sh:hasValue "GB" ] ]
    ) ;
    sh:message  "{$this} is not exactly one kind of place." ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} contains itself." ;
        sh:select    "SELECT $this WHERE { $this bs:within+ $this }" ;
    ] .

bt:PlaceShape-label      a sh:PropertyShape ; sh:path rdfs:label ;
    sh:minCount 1 ; sh:languageIn ( "en" "cy" "gd" ) ; sh:uniqueLang true ;
    sh:message "Place names are in English, Welsh or Gaelic, one per language." .
bt:PlaceShape-lat        a sh:PropertyShape ; sh:path wgs84:lat ;
    sh:maxCount 1 ; sh:minInclusive -90 ; sh:maxInclusive 90 ;
    sh:message "Latitude {$value} is off the globe." .
bt:PlaceShape-long       a sh:PropertyShape ; sh:path wgs84:long ;
    sh:maxCount 1 ; sh:minInclusive -180 ; sh:maxInclusive 180 .
bt:PlaceShape-reachesGB  a sh:PropertyShape ; sh:path [ sh:zeroOrMorePath bs:within ] ;
    sh:hasValue bt:place-gb ;
    sh:message "{$this} is not inside Great Britain at any depth." .

bt:SettlementShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:property     bt:SettlementShape-within, bt:SettlementShape-population, bt:SettlementShape-geometry .

bt:SettlementShape-within      a sh:PropertyShape ; sh:path bs:within ;
    sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:CouncilArea ;
    sh:message "A settlement sits directly inside one council area; {$value} is not one." .
bt:SettlementShape-population  a sh:PropertyShape ; sh:path bs:population ;
    sh:maxCount 1 ; sh:datatype xsd:integer ; sh:minInclusive 0 .
bt:SettlementShape-geometry    a sh:PropertyShape ; sh:path geo:hasDefaultGeometry ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:message "{$this} has no default geometry." .

bt:CouncilAreaShape
    a               sh:NodeShape ;
    sh:targetClass  bs:CouncilArea ;
    sh:property [
        sh:path                 [ sh:inversePath bs:within ] ;
        sh:qualifiedValueShape  [ sh:property [ sh:path bs:isBookTown ; sh:hasValue true ] ] ;
        sh:qualifiedMaxCount    1 ;
        sh:message              "{$this} contains more than one book town." ;
    ] .

# ---------------------------------------------------------------- works

bt:ISBN13ConstraintComponent
    a  sh:ConstraintComponent ;
    sh:parameter [ sh:path bt:isbn13 ; sh:datatype xsd:boolean ] ;
    sh:validator [
        a  sh:SPARQLAskValidator ;
        sh:prefixes  bt:prefixes ;
        sh:message   "The check digit of {$value} is wrong." ;
        sh:ask  \"\"\"
            ASK {
              BIND ( STR($value) AS ?s )
              BIND (   xsd:integer(SUBSTR(?s, 1, 1))  + 3 * xsd:integer(SUBSTR(?s, 2, 1))
                     + xsd:integer(SUBSTR(?s, 3, 1))  + 3 * xsd:integer(SUBSTR(?s, 4, 1))
                     + xsd:integer(SUBSTR(?s, 5, 1))  + 3 * xsd:integer(SUBSTR(?s, 6, 1))
                     + xsd:integer(SUBSTR(?s, 7, 1))  + 3 * xsd:integer(SUBSTR(?s, 8, 1))
                     + xsd:integer(SUBSTR(?s, 9, 1))  + 3 * xsd:integer(SUBSTR(?s, 10, 1))
                     + xsd:integer(SUBSTR(?s, 11, 1)) + 3 * xsd:integer(SUBSTR(?s, 12, 1)) AS ?sum )
              BIND ( 10 - (?sum - 10 * FLOOR(?sum / 10)) AS ?c )
              BIND ( ?c - 10 * FLOOR(?c / 10) AS ?check )
              FILTER ( !REGEX(?s, "^97[89][0-9]{10}$") || ?check = xsd:integer(SUBSTR(?s, 13, 1)) )
            }
        \"\"\" ;
    ] .

bt:WorkShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property     bt:WorkShape-label, bt:WorkShape-author, bt:WorkShape-publishedBy, bt:WorkShape-year,
                    bt:WorkShape-pages, bt:WorkShape-rrp, bt:WorkShape-isbn, bt:WorkShape-genre ;
    sh:or (
        [ sh:property [ sh:path bs:isbn ; sh:minCount 1 ] ]
        [ sh:property [ sh:path bs:publicationYear ; sh:pattern "^(1[0-8][0-9][0-9]|19[0-6][0-9])$" ] ]
    ) ;
    sh:message  "{$this} has no ISBN and was published after 1969." ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} was published in {$value}, before its author was born." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:publicationYear ?value ; bs:author/bs:born ?born .
              FILTER ( xsd:integer(STR(?value)) < xsd:integer(STR(?born)) )
            }
        \"\"\" ;
    ] .

bt:WorkShape-label        a sh:PropertyShape ; sh:path rdfs:label ; sh:minCount 1 ; sh:equals dct:title ;
    sh:message "A work's rdfs:label and dct:title agree." .
bt:WorkShape-author       a sh:PropertyShape ; sh:path bs:author ; sh:minCount 1 ; sh:class bs:Author .
bt:WorkShape-publishedBy  a sh:PropertyShape ; sh:path bs:publishedBy ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:node bt:PublisherShape ; sh:message "{$value} is not a well-formed publisher." .
bt:WorkShape-year         a sh:PropertyShape ; sh:path bs:publicationYear ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:datatype xsd:gYear .
bt:WorkShape-pages        a sh:PropertyShape ; sh:path bs:pages ; sh:maxCount 1 ; sh:datatype xsd:integer ;
    sh:minInclusive 1 ; sh:message "{$value} pages is not a book." .
bt:WorkShape-rrp          a sh:PropertyShape ; sh:path bs:rrp ; sh:maxCount 1 ; sh:datatype xsd:decimal ;
    sh:minInclusive 0 ; sh:message "A negative price: {$value}." .
bt:WorkShape-isbn         a sh:PropertyShape ; sh:path bs:isbn ; sh:maxCount 1 ;
    sh:pattern "^97[89][0-9]{10}$" ; bt:isbn13 true ;
    sh:message "An ISBN-13 is thirteen digits starting 978 or 979: {$value}." .
bt:WorkShape-genre        a sh:PropertyShape ; sh:path ( bs:genre [ sh:zeroOrMorePath skos:broader ] ) ;
    sh:hasValue bt:genre-literature ;
    sh:message "{$this} is filed under a genre that is not in the scheme." .

bt:TranslationShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Translation ;
    sh:property [ sh:path bs:translationOf ; sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:Work ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} was published in {$value}, before the work it translates." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:publicationYear ?value ; bs:translationOf/bs:publicationYear ?original .
              FILTER ( xsd:integer(STR(?value)) < xsd:integer(STR(?original)) )
            }
        \"\"\" ;
    ] .

bt:GenreShape
    a               sh:NodeShape ;
    sh:targetClass  skos:Concept ;
    sh:property [ sh:path skos:inScheme ; sh:hasValue bt:genre-scheme ; sh:message "{$this} is in no scheme." ] ;
    sh:property [ sh:path [ sh:zeroOrMorePath skos:broader ] ; sh:hasValue bt:genre-literature ;
                  sh:message "{$this} does not lead up to the top of the scheme." ] .

# ---------------------------------------------------------------- people and publishers

bt:PersonShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Person ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] ;
    sh:property [ sh:path bs:born ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:gYear ] ;
    sh:property [ sh:path bs:died ; sh:maxCount 1 ; sh:datatype xsd:gYear ] ;
    sh:property [ sh:path bs:basedIn ; sh:maxCount 1 ; sh:class bs:Settlement ;
                  sh:message "{$this} is based in {$value}, which is not a settlement." ] ;
    sh:property [ sh:path bs:writesIn ; sh:in ( "en" "cy" "gd" "ar" ) ;
                  sh:message "{$value} is not one of the dataset's writing languages." ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} died in {$value}, before being born." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:born ?born ; bs:died ?value .
              FILTER ( xsd:integer(STR(?value)) < xsd:integer(STR(?born)) )
            }
        \"\"\" ;
    ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} is in a cycle of influence. Three authors are, by design (q34)." ;
        sh:select    "SELECT $this WHERE { $this bs:influencedBy+ $this }" ;
    ] .

bt:PublisherShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Publisher ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] ;
    sh:property [ sh:path bs:locatedIn ; sh:maxCount 1 ; sh:class bs:Settlement ] ;
    sh:property [ sh:path bs:imprintOf ; sh:maxCount 1 ; sh:class bs:Publisher ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} is an imprint of itself." ;
        sh:select    "SELECT $this WHERE { $this bs:imprintOf+ $this }" ;
    ] .

# ---------------------------------------------------------------- events

bt:EventShape
    a                    sh:NodeShape ;
    sh:targetClass       bs:Event ;
    sh:targetSubjectsOf  bs:heldAt ;
    sh:class             bs:Event ;
    sh:message           "{$this} is not typed as an event." ;
    sh:property [ sh:path bs:heldAt ; sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:Bookshop ;
                  sh:message "Events are held at bookshops; {$value} is not one." ] ;
    sh:property [ sh:path bs:eventDate ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:date ;
                  sh:message "{$value} is not a well-formed date." ] ;
    sh:property [ sh:path bs:eventKind ; sh:minCount 1 ;
                  sh:in ( "Reading" "Signing" "Panel" "Workshop" "Launch" "Lecture" "Book Club" ) ;
                  sh:message "{$value} is not a kind of event this trail runs." ] ;
    sh:property [ sh:path bs:featuring ; sh:minCount 1 ; sh:class bs:Author ;
                  sh:message "An event features at least one author." ] ;
    sh:property [ sh:path bs:attendance ; sh:datatype xsd:integer ; sh:minInclusive 0 ] ;
    sh:property [ sh:path bs:ticketPrice ; sh:maxCount 1 ; sh:datatype xsd:decimal ; sh:minInclusive 0 ;
                  sh:message "Ticket price {$value} is not a non-negative decimal." ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} features {$value}, who had died by then. A memorial, or a mistake?" ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:featuring ?value ; bs:eventDate ?date . ?value bs:died ?died .
              FILTER ( xsd:integer(SUBSTR(STR(?date), 1, 4)) > xsd:integer(STR(?died)) )
            }
        \"\"\" ;
    ] .

# ---------------------------------------------------------------- trail and stock

bt:TrailSegmentShape
    a               sh:NodeShape ;
    sh:targetClass  bs:TrailSegment ;
    sh:property [ sh:path bs:segmentFrom ; sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:Bookshop ;
                  sh:disjoint bs:segmentTo ; sh:message "{$this} starts and ends at {$value}." ] ;
    sh:property [ sh:path bs:segmentTo ; sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:Bookshop ] ;
    sh:property [ sh:path bs:distanceKm ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:decimal ;
                  sh:minExclusive 0 ; sh:message "A segment of {$value} km goes nowhere." ] .

bt:StockRecordShape
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [ sh:path bs:atShop ; sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:Bookshop ;
                  sh:message "{$value} is not typed as a bookshop." ] ;
    sh:property [ sh:path bs:ofWork ; sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:Work ] ;
    sh:property [ sh:path bs:copies ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:integer ; sh:minInclusive 0 ;
                  sh:message "{$value} copies." ] ;
    sh:property [
        sh:path bs:shelfPrice ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:decimal ; sh:minInclusive 0 ;
        sh:sparql [
            sh:prefixes  bt:prefixes ;
            sh:message   "{$value} is more than twice the recommended price." ;
            sh:select    "SELECT $this ?value WHERE { $this $PATH ?value ; bs:ofWork/bs:rrp ?rrp . FILTER ( ?value > 2 * ?rrp ) }" ;
        ] ;
    ] .

bt:SourceShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Source ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] ;
    sh:property [ sh:path bs:sourceKind ; sh:in ( "guidebook" "survey" "self-reported" "register" "newspaper" ) ;
                  sh:message "{$value} is not a recognised kind of source." ] ;
    sh:property [ sh:path bs:confidence ; sh:datatype xsd:decimal ; sh:minInclusive 0 ; sh:maxInclusive 1 ;
                  sh:message "Confidence {$value} is not between 0 and 1." ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, min_violations=40, focus=FAULT_FOCUS),
)
specs.register("s64", "shapesGraph", "report")

s(
    sid="s65", module=M,
    title="Shapes as questions",
    asks="Six facts about the clean data, asked as shapes and answered as information.",
    how="Nothing in this file is an error. Each shape asks a question the "
        "SPARQL course asks with a query, and the answer is a set of Info "
        "rows: the six shops without a website (q14), the eleven works with "
        "no ISBN (q15), the four towns with no bookshop (q16), the eight "
        "works no shop stocks, the three junctions on the trail, and the "
        "shops that stock nothing in their own specialism. A validation "
        "report at Info severity is a profile of the data, and a shapes file "
        "like this one can be kept and run whenever the data changes. It is "
        "the SPARQL course's q05 and q06 -- what is in here, what can I ask "
        "-- with the questions written down.",
    diagram="""
   sh:severity sh:Info      a row per answer, no effect on conformance

   question                                 asked with
   shops without a website                  sh:minCount on bs:website
   works with no ISBN                       sh:minCount on bs:isbn
   towns with no bookshop                   sh:minCount on ^bs:locatedIn
   works nobody stocks                      sh:minCount on ^bs:ofWork
   junctions on the trail                   sh:maxCount 2 on (bs:connectsTo | ^bs:connectsTo)
   shops stocking nothing in their specialism   a SPARQL constraint
""",
    learn=[
        "A shape with Info severity is a question. The report is the answer, one row per node.",
        "Profiles written as shapes are repeatable. Run the same file on next month's data and diff the reports.",
        "Every question here has a query in the SPARQL course. Choose the form by what you want back: a table, or a report.",
    ],
    body="""
bt:NoWebsite
    a sh:NodeShape ; sh:targetClass bs:Bookshop ;
    sh:property [ sh:path bs:website ; sh:minCount 1 ; sh:severity sh:Info ;
                  sh:message "{$this} has no website on record." ] .

bt:NoISBN
    a sh:NodeShape ; sh:targetClass bs:Work ;
    sh:property [ sh:path bs:isbn ; sh:minCount 1 ; sh:severity sh:Info ;
                  sh:message "{$this} has no ISBN." ] .

bt:TownWithoutShop
    a sh:NodeShape ; sh:targetClass bs:Settlement ;
    sh:property [ sh:path [ sh:inversePath bs:locatedIn ] ; sh:minCount 1 ; sh:severity sh:Info ;
                  sh:message "{$this} has no bookshop." ] .

bt:Unstocked
    a sh:NodeShape ; sh:targetClass bs:Work ;
    sh:property [ sh:path [ sh:inversePath bs:ofWork ] ; sh:minCount 1 ; sh:severity sh:Info ;
                  sh:message "No shop stocks {$this}." ] .

bt:Junction
    a sh:NodeShape ; sh:targetClass bs:Bookshop ;
    sh:property [ sh:path [ sh:alternativePath ( bs:connectsTo [ sh:inversePath bs:connectsTo ] ) ] ;
                  sh:maxCount 2 ; sh:severity sh:Info ;
                  sh:message "{$this} is a junction on the trail." ] .

bt:OffSpecialism
    a sh:NodeShape ; sh:targetClass bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} stocks nothing filed under its own specialism." ;
        sh:select    \"\"\"
            SELECT $this WHERE {
              $this bs:specialises ?genre .
              FILTER NOT EXISTS { $this bs:stocks/bs:genre/skos:broader* ?genre }
            }
        \"\"\" ;
    ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, violations=0, min_infos=32),
)
specs.register("s65", "severity", "report")

s(
    sid="s66", module=M,
    title="From report to issues",
    asks="A report turned into bs:DataIssue records -- the vocabulary already has a class for them.",
    how="The vocabulary declares bs:DataIssue, with bs:about and bs:message, "
        "and the clean data never uses them. They are what a validation "
        "result becomes once someone has to act on it. Validate with the "
        "shapes here, open the report as a tab, and run the CONSTRUCT: one "
        "issue per result, pointing at the focus node, carrying the message "
        "and the severity, and naming the constraint component so the issue "
        "can be sorted by kind. The result opens as a new tab, in the "
        "dataset's own vocabulary, ready to be saved next to the data or "
        "loaded into a tracker. The second query is the same list as a "
        "table. The SPARQL course's module 12 is about queries that hand a "
        "graph back; this is one of them.",
    diagram="""
   report                                        issues
   _:r  a sh:ValidationResult ;                  _:i  a bs:DataIssue ;
        sh:focusNode  bt:shop-foxed-page ;   ->       bs:about    bt:shop-foxed-page ;
        sh:resultMessage "..." ;                      bs:message  "..." ;
        sh:resultSeverity sh:Violation ;              sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent ... .            dct:type    sh:DatatypeConstraintComponent .
""",
    learn=[
        "A report is input as well as output. CONSTRUCT turns it into whatever the next process needs.",
        "Keep the focus node, the message, the severity and the component: they are what a person needs to act.",
        "The dataset's own vocabulary is the right target when the issues will live beside the data.",
    ],
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path rdfs:label ;    sh:minCount 1 ; sh:datatype rdf:langString ;
                  sh:message "A shop has a name with a language tag." ] ;
    sh:property [ sh:path bs:locatedIn ;  sh:minCount 1 ; sh:maxCount 1 ; sh:class bs:Settlement ;
                  sh:message "A shop is in exactly one settlement." ] ;
    sh:property [ sh:path bs:founded ;    sh:datatype xsd:gYear ;
                  sh:message "A founding year is an xsd:gYear." ] ;
    sh:property [ sh:path bs:staffCount ; sh:datatype xsd:integer ; sh:minInclusive 1 ;
                  sh:message "Staff count is a positive integer." ] ;
    sh:property [ sh:path bs:website ;    sh:maxCount 1 ; sh:severity sh:Warning ;
                  sh:message "At most one website." ] .

bt:EventShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [ sh:path bs:heldAt ;    sh:class bs:Bookshop ; sh:message "Held somewhere that is not a bookshop." ] ;
    sh:property [ sh:path bs:featuring ; sh:minCount 1 ;       sh:message "Nobody is featured." ] ;
    sh:property [ sh:path bs:eventDate ; sh:datatype xsd:date ; sh:message "Not a well-formed date." ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, min_violations=8),
    queries=[
        Query("Issues, as RDF in the dataset's vocabulary", """
PREFIX sh:  <http://www.w3.org/ns/shacl#>
PREFIX bs:  <https://example.org/bookshop-trail/schema#>
PREFIX dct: <http://purl.org/dc/terms/>
CONSTRUCT {
  [] a bs:DataIssue ;
     bs:about ?focus ;
     bs:message ?message ;
     sh:resultSeverity ?severity ;
     dct:type ?component .
}
WHERE {
  ?r a sh:ValidationResult ;
     sh:focusNode ?focus ;
     sh:resultSeverity ?severity ;
     sh:sourceConstraintComponent ?component .
  OPTIONAL { ?r sh:resultMessage ?message }
}"""),
        Query("The same list as a table, worst first", """
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?severity ?focus ?path ?message
WHERE {
  ?r a sh:ValidationResult ;
     sh:focusNode ?focus ;
     sh:resultSeverity ?severity .
  OPTIONAL { ?r sh:resultPath ?path }
  OPTIONAL { ?r sh:resultMessage ?message }
}
ORDER BY ?severity ?focus"""),
    ],
)
specs.register("s66", "report", "sparqlConstruct")

s(
    sid="s67", module=M,
    title="A rule set for the trail",
    asks="Infer each shop's country and each record's value, then check what only the inferred data can answer.",
    how="Three rules run before the checks: bs:inCountry from module 07's "
        "filter shape expression, bs:stockValue from its SPARQL rule, and "
        "bs:contributor from its union. Two constraints then use them. "
        "bt:WelshStock asks whether every shop in Wales stocks at least one "
        "work written in Welsh; one does not, and is reported as a warning. "
        "bt:HighValueStock sums the inferred values per shop and reports the "
        "shops holding more than five hundred pounds of stock as "
        "information. Neither question is askable of the asserted data "
        "without repeating the inference inside the query; with the rules "
        "in place the constraints are short, and the inferences are "
        "available to every shape in the file.",
    diagram="""
   order 0   rules      shop  bs:inCountry  country
                        record bs:stockValue copies x price
                        work  bs:contributor author, translator

   then      shapes     shops in Wales with no Welsh-language stock          warning
                        shops whose bs:stockValue sums to more than 500      info
""",
    learn=[
        "A rule set is a small ontology of derived properties. Write it once, and every shape in the file can use them.",
        "Constraints over inferred properties read like constraints over asserted ones, which is the reason to infer them.",
        "Keep the rules and the shapes that depend on them in one file, with the Inference mode in the LOAD IT link, so a reader cannot run one without the other.",
    ],
    body="""
bt:ShopRules
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:rule [
        a  sh:TripleRule ; sh:subject sh:this ; sh:predicate bs:inCountry ;
        sh:object [ sh:filterShape [ sh:class bs:Country ] ;
                    sh:nodes [ sh:path ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) ] ] ;
    ] .

bt:StockRules
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:rule [
        a  sh:SPARQLRule ; sh:prefixes bt:prefixes ;
        sh:construct "CONSTRUCT { $this bs:stockValue ?v } WHERE { $this bs:copies ?c ; bs:shelfPrice ?p . BIND ( ?c * ?p AS ?v ) }" ;
    ] .

bt:WorkRules
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:rule [
        a  sh:TripleRule ; sh:subject sh:this ; sh:predicate bs:contributor ;
        sh:object [ sh:union ( [ sh:path bs:author ] [ sh:path bs:translatedBy ] ) ] ;
    ] .

bt:WelshStock
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} is in Wales and stocks nothing written in Welsh." ;
        sh:select    \"\"\"
            SELECT $this WHERE {
              $this bs:inCountry bt:place-wales .
              FILTER NOT EXISTS { $this bs:stocks/bs:originalLanguage "cy" }
            }
        \"\"\" ;
    ] .

bt:HighValueStock
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} holds more than five hundred pounds of stock at shelf prices." ;
        sh:select    \"\"\"
            SELECT $this WHERE {
              { SELECT $this (SUM(?v) AS ?total)
                WHERE { ?record bs:atShop $this ; bs:stockValue ?v }
                GROUP BY $this }
              FILTER ( ?total > 500 )
            }
        \"\"\" ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=False, warnings=1, min_infos=3, focus=["shop-clock-tower", "shop-ex-libris"]),
)
specs.register("s67", "afRules", "afSparqlRule")

s(
    sid="s68", module=M,
    title="Challenge: the walking tour",
    asks="Four questions about the trail that each need two or three techniques at once. Try them before reading the shapes.",
    how="Every book town has at least two shops: a SPARQL target and an "
        "inverse path with sh:minCount 2 (all three pass). Every segment "
        "joins two shops that bs:connectsTo links in one direction or the "
        "other: a SPARQL constraint with a UNION (all pass). No two segments "
        "join the same pair of shops: a SPARQL constraint with a second "
        "segment variable (all pass). And which segments cross a border: a "
        "rule infers each shop's country first, then a constraint compares "
        "the two ends and reports the three that differ as information. The "
        "SPARQL course's module 14 sets challenges in the same spirit; these "
        "are the validation versions.",
    diagram="""
   book towns have two shops        sh:target [ SPARQL ]  +  sh:path [ sh:inversePath bs:locatedIn ] ; sh:minCount 2
   segment ends are linked          sh:sparql with { ?f bs:connectsTo ?t } UNION { ?t bs:connectsTo ?f }
   no duplicate segments            sh:sparql joining a second segment on the same two ends
   border crossings                 a rule for bs:inCountry, then a constraint comparing the ends
""",
    learn=[
        "Most real constraints are two techniques: a target that says who, and a path or a query that says what.",
        "A rule can do the join once so that several constraints stay simple.",
        "Passing constraints are worth keeping. They are the ones that will catch the next edit.",
    ],
    body="""
bt:BookTownShape
    a  sh:NodeShape ;
    sh:target [ a sh:SPARQLTarget ; sh:prefixes bt:prefixes ;
                sh:select "SELECT ?this WHERE { ?this bs:isBookTown true }" ] ;
    sh:property [ sh:path [ sh:inversePath bs:locatedIn ] ; sh:minCount 2 ;
                  sh:message "{$this} is a book town with fewer than two shops." ] .

bt:SegmentLinked
    a               sh:NodeShape ;
    sh:targetClass  bs:TrailSegment ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "The two ends of {$this} are not linked by bs:connectsTo." ;
        sh:select    \"\"\"
            SELECT $this WHERE {
              $this bs:segmentFrom ?f ; bs:segmentTo ?t .
              FILTER NOT EXISTS { { ?f bs:connectsTo ?t } UNION { ?t bs:connectsTo ?f } }
            }
        \"\"\" ;
    ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} duplicates {$value}." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:segmentFrom ?f ; bs:segmentTo ?t .
              ?value bs:segmentFrom ?f ; bs:segmentTo ?t .
              FILTER ( ?value != $this )
            }
        \"\"\" ;
    ] .

bt:ShopCountry
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:rule [
        a  sh:TripleRule ; sh:subject sh:this ; sh:predicate bs:inCountry ;
        sh:object [ sh:filterShape [ sh:class bs:Country ] ;
                    sh:nodes [ sh:path ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) ] ] ;
    ] .

bt:BorderCrossing
    a               sh:NodeShape ;
    sh:targetClass  bs:TrailSegment ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} crosses a border into {$value}." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:segmentFrom ?f ; bs:segmentTo ?t .
              ?f bs:inCountry ?from . ?t bs:inCountry ?value .
              FILTER ( ?from != ?value )
            }
        \"\"\" ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=False, violations=0, infos=3, focus=["seg-gutter-gilt-borderprint"]),
)
specs.register("s68", "afSparqlTarget", "sparql")
