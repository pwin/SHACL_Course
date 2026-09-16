# -*- coding: utf-8 -*-
"""Module 02 -- What a value may be."""
from shapecat import s, Query, D11, DFAULTY, DSHOPS
import specs

M = "02-value-constraints"

s(
    sid="s10", module=M,
    title="The right kind of value",
    asks="Years are xsd:gYear, counts are integers, prices are decimals, flags are booleans, and a date is a date.",
    how="sh:datatype compares the datatype IRI of each value with the one "
        "named, and also checks that the lexical form is valid for that "
        "datatype. So \"1985\"^^xsd:integer fails a gYear constraint although "
        "the digits are the right ones; \"3.5\"^^xsd:decimal fails an integer "
        "constraint; the plain string \"yes\" fails a boolean constraint; a "
        "website written without ^^xsd:anyURI is an xsd:string and fails; and "
        "\"2025-13-01\"^^xsd:date carries the right datatype but is ill-formed, "
        "which the specification says is a violation too. Seven values on the "
        "faulty data fail, all of them from the three resources that fault "
        "file F06, F20 and F25 describe.",
    diagram="""
   value                              sh:datatype        result
   "1979"^^xsd:gYear                  xsd:gYear          ok
   "1985"^^xsd:integer                xsd:gYear          violation: wrong datatype, same digits
   "3.5"^^xsd:decimal                 xsd:integer        violation
   "yes"                              xsd:boolean        violation: a plain string is xsd:string
   "www.foxed-page.example"           xsd:anyURI         violation: xsd:string
   "2025-13-01"^^xsd:date             xsd:date           violation: right datatype, ill-formed
   "11000.0"^^xsd:decimal             xsd:integer        violation
""",
    learn=[
        "sh:datatype checks the datatype IRI and the well-formedness of the lexical form, nothing more.",
        "A number written without a datatype is what Turtle makes of it: 12 is an integer, 12.5 a decimal, \"12\" a string.",
        "An ill-formed literal is a violation even when its datatype matches. Validators are allowed to catch what parsers let through.",
    ],
    body="""
bt:BookshopValues
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path bs:founded ;    sh:datatype xsd:gYear ;
                  sh:message "A founding year is an xsd:gYear, not {$value}." ] ;
    sh:property [ sh:path bs:staffCount ; sh:datatype xsd:integer ] ;
    sh:property [ sh:path bs:floorArea ;  sh:datatype xsd:decimal ] ;
    sh:property [ sh:path bs:hasCafe ;    sh:datatype xsd:boolean ] ;
    sh:property [ sh:path bs:website ;    sh:datatype xsd:anyURI ;
                  sh:message "A website is an xsd:anyURI. {$value} is a plain string." ] .

bt:EventValues
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [ sh:path bs:eventDate ;   sh:datatype xsd:date ;
                  sh:message "{$value} is not a well-formed xsd:date." ] ;
    sh:property [ sh:path bs:ticketPrice ; sh:datatype xsd:decimal ] ;
    sh:property [ sh:path bs:attendance ;  sh:datatype xsd:integer ] .

bt:SettlementValues
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:property [ sh:path bs:population ; sh:datatype xsd:integer ] ;
    sh:property [ sh:path bs:isBookTown ; sh:datatype xsd:boolean ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=7, focus=["shop-foxed-page", "event-foxed-page", "place-newtown"]),
)
specs.register("s10", "datatype")

s(
    sid="s11", module=M,
    title="IRI, literal or blank node",
    asks="A shop's town is a node, not a string; a shop's name is a literal with a language tag.",
    how="sh:nodeKind sorts values into the three kinds of RDF term and the "
        "three pairs: sh:IRI, sh:Literal, sh:BlankNode, sh:BlankNodeOrIRI, "
        "sh:BlankNodeOrLiteral, sh:IRIOrLiteral. bs:locatedIn \"Kendal\" fails "
        "sh:nodeKind sh:IRI. The labels are literals, so sh:Literal passes for "
        "all of them, including \"The Foxed Page\" with no language tag; what "
        "catches that one is sh:datatype rdf:langString, because a literal "
        "with a tag has that datatype and one without is an xsd:string. The "
        "SPARQL course's shapes.ttl makes the same point in its first "
        "property shape.",
    diagram="""
                                sh:IRI   sh:Literal   sh:BlankNode
   bt:place-kendal                ok        -             -
   "Kendal"                       -         ok            -
   [ a bs:Place ]                 -         -             ok

   "The Inkwell"@en    datatype rdf:langString
   "The Foxed Page"    datatype xsd:string      <- no tag, so not a langString
""",
    learn=[
        "sh:nodeKind is about the kind of term. It cannot tell a well-formed IRI from a nonsense one; sh:pattern or sh:class can.",
        "A language-tagged string has datatype rdf:langString. Asking for xsd:string on labels rejects every tagged one.",
        "Use sh:nodeKind sh:IRI on object properties as a first line of defence: it catches the string where a node should be before sh:class has to.",
    ],
    body="""
bt:BookshopTerms
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      bs:locatedIn ;
        sh:nodeKind  sh:IRI ;
        sh:message   "A shop's town is a place, not the string {$value}." ;
    ] ;
    sh:property [
        sh:path      rdfs:label ;
        sh:nodeKind  sh:Literal ;
        sh:datatype  rdf:langString ;
        sh:message   "Names carry a language tag: \\"{$value}\\" has none." ;
    ] ;
    sh:property [
        sh:path      bs:specialises ;
        sh:nodeKind  sh:IRI ;
    ] ;
    sh:property [
        sh:path      geo:hasGeometry ;
        sh:nodeKind  sh:BlankNodeOrIRI ;
    ] ;
    sh:property [
        sh:path      bs:website ;
        sh:nodeKind  sh:Literal ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=2, focus=["shop-foxed-page"]),
)
specs.register("s11", "nodeKind", "datatype")

s(
    sid="s12", module=M,
    title="sh:class, and why it needs rdf:type",
    asks="What a shop, a person, an event, a record and a settlement may point at.",
    how="sh:class C passes a value when the value has rdf:type C, or a type "
        "that is an rdfs:subClassOf C in the data graph. It fails everything "
        "else: a literal, a node of the wrong class, and a node with no "
        "rdf:type at all. That last case is the one to remember. The Ghost "
        "Shop (F07) has a label, a town and a founding year, and fails "
        "sh:class bs:Bookshop because nobody typed it. Six values fail on the "
        "faulty data: the string town and the place used as a genre (F06), "
        "an author based in a country (F16), the record at the untyped shop "
        "(F24), Brecon placed inside Wales with no council area between "
        "(F26), and the event held at a publisher (F20). bt:pub-orbit is "
        "typed bs:Publisher and passes sh:class bs:Publisher, whatever else is "
        "wrong with it; module 04 comes back to that with sh:node.",
    diagram="""
   sh:class bs:Bookshop  passes a value v  when the data has

        v  rdf:type  bs:Bookshop
   or   v  rdf:type  C .   C  rdfs:subClassOf+  bs:Bookshop        (in the data graph)

   bt:shop-ghost  rdfs:label "The Ghost Shop"@en ; bs:locatedIn ... ; bs:founded ...
                  (no rdf:type)                                     -> fails

   bt:book-cold-harbour-he  a bs:Translation .   bs:Translation rdfs:subClassOf bs:Work
                                                                    -> passes sh:class bs:Work
""",
    learn=[
        "sh:class is a test of rdf:type, with rdfs:subClassOf followed in the data graph. It says nothing about the node's other properties.",
        "An untyped node fails sh:class however well described it is. If your data does not type everything, say so with sh:node instead (module 04).",
        "sh:class on a literal fails. That is the intended answer, not an error.",
    ],
    body="""
bt:BookshopLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path bs:locatedIn ;   sh:class bs:Settlement ;
                  sh:message "{$this} is located in {$value}, which is not a settlement." ] ;
    sh:property [ sh:path bs:specialises ; sh:class skos:Concept ;
                  sh:message "A specialism is a concept from the genre scheme, not {$value}." ] .

bt:PersonLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:Person ;
    sh:property [ sh:path bs:basedIn ; sh:class bs:Settlement ] .

bt:EventLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [ sh:path bs:heldAt ;    sh:class bs:Bookshop ] ;
    sh:property [ sh:path bs:featuring ; sh:class bs:Author ] .

bt:StockLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [ sh:path bs:atShop ; sh:class bs:Bookshop ;
                  sh:message "{$value} is not typed as a bookshop." ] ;
    sh:property [ sh:path bs:ofWork ; sh:class bs:Work ] .

bt:SettlementLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:property [ sh:path bs:within ; sh:class bs:CouncilArea ;
                  sh:message "A settlement sits directly inside a council area; {$value} is not one." ] .

bt:WorkLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [ sh:path bs:publishedBy ; sh:class bs:Publisher ] ;
    sh:property [ sh:path bs:author ;      sh:class bs:Author ] ;
    sh:property [ sh:path bs:translationOf ; sh:class bs:Work ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=6,
                focus=["shop-foxed-page", "author-owen-harker", "stock-ghost", "place-brecon", "event-foxed-page"],
                nofocus=["pub-orbit", "book-unnumbered"]),
)
specs.register("s12", "class")

s(
    sid="s13", module=M,
    title="Ranges",
    asks="Coordinates on the globe, counts that are not negative, prices that are not negative, a confidence between 0 and 1.",
    how="The four range components compare each value with a constant: "
        "sh:minInclusive and sh:maxInclusive allow equality, sh:minExclusive "
        "and sh:maxExclusive do not. They use SPARQL's comparison, so numbers "
        "of different numeric types compare by value. A value that cannot be "
        "compared at all -- the ticket price \"free\" against 0 -- is a "
        "violation, which is what the specification says should happen. Ten "
        "values fail on the faulty data, each named in the message with "
        "{$value}.",
    diagram="""
   sh:minInclusive 1      v >= 1        0 fails,  1 passes
   sh:minExclusive 0      v >  0        0 fails,  0.1 passes
   sh:maxInclusive 90     v <= 90       152.5 fails
   sh:maxExclusive ...    v <  ...

   "free"  compared with 0    cannot be compared  ->  violation
""",
    learn=[
        "Inclusive or exclusive is the whole difference between the pairs. 'Positive' is minExclusive 0; 'not negative' is minInclusive 0.",
        "Comparison is SPARQL's: an integer and a decimal compare by value, a string and a number do not compare and the value fails.",
        "Ranges are where {$value} in a message earns its place. Say the number.",
    ],
    body="""
bt:PlaceRanges
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:property [ sh:path wgs84:lat ;  sh:minInclusive -90 ;  sh:maxInclusive 90 ;
                  sh:message "Latitude {$value} is off the globe." ] ;
    sh:property [ sh:path wgs84:long ; sh:minInclusive -180 ; sh:maxInclusive 180 ] ;
    sh:property [ sh:path bs:population ; sh:minInclusive 0 ] .

bt:BookshopRanges
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path bs:staffCount ; sh:minInclusive 1 ;
                  sh:message "{$this} reports {$value} staff." ] ;
    sh:property [ sh:path bs:floorArea ;  sh:minExclusive 0 ;
                  sh:message "Floor area must be positive, not {$value}." ] .

bt:WorkRanges
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [ sh:path bs:pages ; sh:minInclusive 1 ; sh:message "{$value} pages is not a book." ] ;
    sh:property [ sh:path bs:rrp ;   sh:minInclusive 0 ; sh:message "A negative price: {$value}." ] .

bt:StockRanges
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [ sh:path bs:copies ;     sh:minInclusive 0 ] ;
    sh:property [ sh:path bs:shelfPrice ; sh:minInclusive 0 ] .

bt:SegmentRanges
    a               sh:NodeShape ;
    sh:targetClass  bs:TrailSegment ;
    sh:property [ sh:path bs:distanceKm ; sh:minExclusive 0 ; sh:maxExclusive 1000 ;
                  sh:message "A segment of {$value} km goes nowhere, or too far." ] .

bt:EventRanges
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [ sh:path bs:attendance ;  sh:minInclusive 0 ] ;
    sh:property [ sh:path bs:ticketPrice ; sh:minInclusive 0 ;
                  sh:message "Ticket price {$value} cannot be compared with 0." ] .

bt:SourceRanges
    a               sh:NodeShape ;
    sh:targetClass  bs:Source ;
    sh:property [ sh:path bs:confidence ; sh:minInclusive 0 ; sh:maxInclusive 1 ;
                  sh:message "Confidence is a proportion; {$value} is more than certain." ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=10,
                focus=["place-newtown", "shop-halfmoon", "shop-foxed-page", "book-the-margin-notes",
                       "stock-foxed-page", "seg-inkwell-inkwell", "event-foxed-page", "source-rumour"]),
)
specs.register("s13", "range", "minInclusive")

s(
    sid="s14", module=M,
    title="Comparing years",
    asks="No shop opened before 1800, and nobody died before they were born -- said in a way this engine can evaluate.",
    how="The years in this dataset are xsd:gYear, and SPARQL's < is not "
        "defined for that datatype. bt:YearRangeNaive puts sh:minInclusive "
        "\"1800\"^^xsd:gYear on The Inkwell's founding year of 1979, and the "
        "engine reports a violation: it cannot make the comparison, and a "
        "comparison it cannot make is a failure. The same shape would flag "
        "all 33 shops. The SPARQL course meets this in q07 and q13, and the "
        "fix is the same: go through the string. bt:YearRangeShape is a "
        "SPARQL constraint (module 05 covers the syntax) that casts "
        "xsd:integer(STR(?y)) and compares the integers; it passes The "
        "Inkwell and everyone else. bt:LifespanShape does the same for born "
        "and died, and finds the one author in the faulty data who died "
        "before he was born.",
    diagram="""
   "1979"^^xsd:gYear  >=  "1800"^^xsd:gYear ?

     sh:minInclusive          SPARQL has no < for gYear   ->  violation, on every shop
     xsd:integer(STR(?y))     1979 >= 1800                ->  true

   The SPARQL course's shapes.ttl has sh:lessThan between bs:born and
   bs:died. On this engine that is eight findings, all of them on authors
   whose dates are in the right order. Same cause.
""",
    learn=[
        "Range comparisons on xsd:gYear do not work on this engine, and fail closed: every value is reported. xsd:date compares as expected.",
        "Cast through STR() and compare integers, in a SPARQL constraint. It is longer, and it is right.",
        "When a range shape reports every node, suspect the datatype before the data.",
    ],
    body="""
# The shape you would write first. Wrong on this engine: gYear does not compare.
bt:YearRangeNaive
    a              sh:NodeShape ;
    sh:targetNode  bt:shop-inkwell ;
    sh:property [
        sh:path          bs:founded ;
        sh:minInclusive  "1800"^^xsd:gYear ;
        sh:message       "sh:minInclusive on a gYear: reported although 1979 is after 1800." ;
    ] .

# The same rule, evaluated on integers.
bt:YearRangeShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} opened in {$value}, before 1800." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:founded ?value .
              FILTER ( xsd:integer(STR(?value)) < 1800 )
            }
        \"\"\" ;
    ] .

# Nobody dies before they are born.
bt:LifespanShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Person ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} died in {$value}, before being born." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:born ?born ; bs:died ?value .
              FILTER ( xsd:integer(STR(?value)) < xsd:integer(STR(?born)) )
            }
        \"\"\" ;
    ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, violations=2, focus=["shop-inkwell", "author-owen-harker"], nofocus=["author-perrin-oakes"]),
)
specs.register("s14", "range", "sparql")

s(
    sid="s15", module=M,
    title="Strings: length and pattern",
    asks="An ISBN-13 is thirteen digits starting 978 or 979; a website starts with a scheme; an event kind is one of seven words.",
    how="sh:pattern is a SPARQL REGEX over the string form of each value, "
        "with sh:flags passed through, so \"i\" makes it case-insensitive. "
        "sh:minLength and sh:maxLength count characters of the string form. "
        "The hyphenated ISBN (F08) fails the pattern and the maximum length, "
        "one row each. The ISBN with a wrong check digit (F10) passes: it is "
        "thirteen digits starting 978, and no pattern can do arithmetic. "
        "Module 06 writes the constraint component that can. The website "
        "without a scheme (F06) fails ^https?://, and the eventKind "
        "\"Recital\" fails the list of seven, spelled as an alternation.",
    diagram="""
   sh:pattern "^97[89][0-9]{10}$"
   "9787063088596"        matches                 ok
   "978-0-14-118776-1"    hyphens                 violation  (and 17 > 13 for maxLength)
   "9780141187762"        wrong check digit       passes -- a pattern cannot add up

   sh:pattern "^(reading|signing|panel|workshop|launch|lecture|book club)$" ; sh:flags "i"
   "Launch"               matches case-insensitively
   "Recital"              violation
""",
    learn=[
        "sh:pattern works on the lexical form of any literal, gYears included. It is a regular expression, so anchor it.",
        "Length is measured in characters of the string form. \"12\" and 12 both have length 2.",
        "A pattern checks shape, not truth. Anything that needs arithmetic or a lookup needs SPARQL.",
    ],
    body="""
bt:WorkStrings
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [
        sh:path       bs:isbn ;
        sh:pattern    "^97[89][0-9]{10}$" ;
        sh:minLength  13 ;
        sh:maxLength  13 ;
        sh:message    "An ISBN-13 is 978 or 979 and ten more digits, no hyphens: {$value}." ;
    ] .

bt:BookshopStrings
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path     bs:website ;
        sh:pattern  "^https?://" ;
        sh:message  "A website starts with http:// or https://: {$value}." ;
    ] .

bt:EventStrings
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [
        sh:path     bs:eventKind ;
        sh:pattern  "^(reading|signing|panel|workshop|launch|lecture|book club)$" ;
        sh:flags    "i" ;
        sh:message  "{$value} is not one of the seven kinds of event." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=4, focus=["book-the-margin-notes", "shop-foxed-page", "event-foxed-page"],
                nofocus=["book-precocious"]),
)
specs.register("s15", "strings", "pattern")

s(
    sid="s16", module=M,
    title="Languages",
    asks="Place names are in English, Welsh or Gaelic, and one name per language; shop names carry a tag.",
    how="sh:languageIn takes a list of language tags and passes a value whose "
        "tag matches one of them, with the usual prefix rule, so cy-GB would "
        "match cy. A literal with no tag matches nothing, which is how the "
        "shop named without a tag is caught a second way. sh:uniqueLang true "
        "says no two values share a language tag; Newtown (F25) has two "
        "English labels and fails. Kendal's French label (F28) fails "
        "sh:languageIn. The SPARQL course's q11 lists the Welsh and Gaelic "
        "names these shapes are about.",
    diagram="""
   sh:languageIn ( "en" "cy" "gd" )
   "Wigtown"@en             ok
   "Baile na h-Uige"@gd     ok
   "Kendal"@fr              violation
   "The Foxed Page"         violation: no tag, so no match

   sh:uniqueLang true
   "Newtown"@en, "New Town"@en, "Y Drenewydd"@cy     two @en  ->  violation
""",
    learn=[
        "sh:languageIn is an allow-list of tags. It rejects untagged literals, which is often what you want on a label.",
        "sh:uniqueLang is one per language, not one in total. It is the constraint for 'one preferred label per language'.",
        "A uniqueLang result has no sh:value: the problem is the pair, not either member.",
    ],
    body="""
bt:PlaceNames
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:property [
        sh:path        rdfs:label ;
        sh:languageIn  ( "en" "cy" "gd" ) ;
        sh:message     "Place names are in English, Welsh or Gaelic: {$value}." ;
    ] .

bt:SettlementNames
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:property [
        sh:path        rdfs:label ;
        sh:uniqueLang  true ;
        sh:message     "{$this} has more than one name in the same language." ;
    ] .

bt:ShopNames
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path        rdfs:label ;
        sh:languageIn  ( "en" "cy" "gd" ) ;
        sh:message     "\\"{$value}\\" has no language tag, or one not in the list." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=3, focus=["place-kendal", "place-newtown", "shop-foxed-page"]),
)
specs.register("s16", "languageIn", "uniqueLang")

s(
    sid="s17", module=M,
    title="A fixed list of values",
    asks="Kinds of event, kinds of source and writing languages come from short lists, and every country is inside Great Britain.",
    how="sh:in lists the allowed values, and every value of the path must be "
        "one of them. \"Recital\" (F20), \"hearsay\" (F31) and \"fr\" (F17) "
        "are not. sh:hasValue is the other direction: at least one value of "
        "the path must be the one named, and the other values do not matter. "
        "bt:CountryShape uses it to say that each country's bs:within includes "
        "bt:place-gb, which is true of all three. Both compare terms exactly: "
        "\"Reading\" and \"reading\" are different, and so are 1 and \"1\".",
    diagram="""
   sh:in ( "Reading" "Signing" "Panel" "Workshop" "Launch" "Lecture" "Book Club" )
        every value of the path must be in the list       "Recital"  ->  violation

   sh:hasValue bt:place-gb
        some value of the path must be this term          bt:place-scotland bs:within bt:place-gb   ok

   comparison is by term:  "Reading" != "reading",  1 != "1",  "1979"^^xsd:gYear != 1979
""",
    learn=[
        "sh:in is 'all values from this list'; sh:hasValue is 'this value is among them'.",
        "Both are exact term comparisons. Datatype and language tag are part of the term.",
        "A short closed list belongs in sh:in. A long or changing one belongs in the data, where a sh:class or a SPARQL constraint can look it up (module 05).",
    ],
    body="""
bt:EventKinds
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [
        sh:path     bs:eventKind ;
        sh:in       ( "Reading" "Signing" "Panel" "Workshop" "Launch" "Lecture" "Book Club" ) ;
        sh:message  "{$value} is not a kind of event this trail runs." ;
    ] .

bt:SourceKinds
    a               sh:NodeShape ;
    sh:targetClass  bs:Source ;
    sh:property [
        sh:path     bs:sourceKind ;
        sh:in       ( "guidebook" "survey" "self-reported" "register" "newspaper" ) ;
        sh:message  "{$value} is not a recognised kind of source." ;
    ] .

bt:AuthorLanguages
    a               sh:NodeShape ;
    sh:targetClass  bs:Author ;
    sh:property [
        sh:path     bs:writesIn ;
        sh:in       ( "en" "cy" "gd" "ar" ) ;
        sh:message  "The dataset has four writing languages; {$value} is not one." ;
    ] .

bt:CountryShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Country ;
    sh:property [
        sh:path      bs:within ;
        sh:hasValue  bt:place-gb ;
        sh:message   "Every country in this dataset is part of Great Britain." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=3, focus=["event-foxed-page", "source-rumour", "author-owen-harker"]),
)
specs.register("s17", "in", "hasValue")

s(
    sid="s18", module=M,
    title="Comparing two properties",
    asks="A segment's two ends differ; a work's label and title agree; a translation is not older than its original; and the gYear problem again.",
    how="The property pair components compare the values of sh:path with the "
        "values of another property of the same focus node. sh:disjoint "
        "bs:segmentTo on bs:segmentFrom says no value is shared; the segment "
        "from The Inkwell to The Inkwell (F22) fails. sh:equals dct:title on "
        "rdfs:label says the two value sets are identical; the work whose "
        "title is hyphenated and whose label is not (F13) fails, and the "
        "result names the value on each side. sh:lessThanOrEquals compares by "
        "value, and the second property must be a plain predicate, but "
        "sh:path can be a sequence: (bs:translationOf bs:publicationYear) "
        "reaches the original's year, to be compared with the translation's "
        "own. Those are gYears, so on this engine every translation is "
        "reported, the one published before its original (F14) among six "
        "that are in order. bt:DiscountShape does the same comparison on "
        "decimals and behaves: it reports, as information, every stock record "
        "whose shelf price is below the recommended price.",
    diagram="""
   focus node          sh:path values        compared with      component
   bt:seg-...          bs:segmentFrom         bs:segmentTo       sh:disjoint      shared value -> violation
   bt:book-...         rdfs:label             dct:title          sh:equals        sets differ  -> violation
   bt:book-...-fr      translationOf/pubYear  bs:publicationYear sh:lessThanOrEquals   gYear: cannot compare
   bt:stock-...        ofWork/rrp             bs:shelfPrice      sh:lessThanOrEquals   rrp <= shelf?  no -> info

   the second property is always a single predicate; the first may be a path
""",
    learn=[
        "sh:equals and sh:disjoint compare value sets; sh:lessThan and sh:lessThanOrEquals compare every pair of values.",
        "The compared property is a predicate on the focus node. To compare with something further away, put the path on sh:path and the predicate on the other side.",
        "sh:lessThan on xsd:gYear reports every pair on this engine. Use the STR cast from s14 when years are involved.",
    ],
    body="""
bt:SegmentEnds
    a               sh:NodeShape ;
    sh:targetClass  bs:TrailSegment ;
    sh:property [
        sh:path      bs:segmentFrom ;
        sh:disjoint  bs:segmentTo ;
        sh:message   "{$this} starts and ends at {$value}." ;
    ] .

bt:WorkTitles
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [
        sh:path     rdfs:label ;
        sh:equals   dct:title ;
        sh:message  "rdfs:label and dct:title disagree on {$this}: {$value}." ;
    ] .

# gYear: reported for every translation, in order or not. See s14.
bt:TranslationDates
    a               sh:NodeShape ;
    sh:targetClass  bs:Translation ;
    sh:property [
        sh:path              ( bs:translationOf bs:publicationYear ) ;
        sh:lessThanOrEquals  bs:publicationYear ;
        sh:message           "Original {$value}: cannot be compared with the translation's gYear on this engine." ;
    ] .

# Decimals compare. Which stock is sold below the recommended price?
bt:DiscountShape
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [
        sh:path              ( bs:ofWork bs:rrp ) ;
        sh:lessThanOrEquals  bs:shelfPrice ;
        sh:severity          sh:Info ;
        sh:message           "{$this}: RRP {$value} is above the shelf price. A discount." ;
    ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, focus=["seg-inkwell-inkwell", "book-unnumbered", "book-the-dark-sea-fr"], min_infos=1),
)
specs.register("s18", "pairs", "lessThanOrEquals")
