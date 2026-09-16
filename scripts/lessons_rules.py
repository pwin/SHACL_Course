# -*- coding: utf-8 -*-
"""Module 07 -- SHACL rules (SHACL Advanced Features)."""
from shapecat import s, Query, D11, DFAULTY, DSHOPS, RULES, RULES_ITERATED
import specs

M = "07-rules"

# The probe shape every lesson in this module uses in one form or another:
# a SPARQL constraint at Info severity that selects the inferred triples, so
# the report shows them. A validator has no other output channel.

s(
    sid="s43", module=M,
    title="Your first rule",
    asks="Every bookshop is also a schema:BookStore -- inferred, then made visible in the report.",
    how="sh:rule attaches a rule to a shape, and the rule fires once for each "
        "of the shape's focus nodes. A sh:TripleRule builds one triple from "
        "three node expressions: sh:subject sh:this is the focus node, "
        "sh:predicate rdf:type is a constant, sh:object schema:BookStore is a "
        "constant. With the Inference dropdown at none the rule is ignored; "
        "at rules it runs before validation, and the data the shapes see now "
        "has 33 triples nobody wrote. A validator's only output is its "
        "report, so bt:TypeProbe makes the inferences visible: a SPARQL "
        "constraint at Info severity that selects the new type, one row per "
        "shop. bt:BookStoreShape shows the other consequence: its target is "
        "the inferred class, and under rules it has 33 focus nodes. The data "
        "in the tab is not changed; the inferred graph lives only for the "
        "run.",
    diagram="""
   bt:BookshopShape
     sh:targetClass bs:Bookshop              33 focus nodes
     sh:rule [ a sh:TripleRule ;
        sh:subject   sh:this ;               <- the focus node
        sh:predicate rdf:type ;              <- a constant
        sh:object    schema:BookStore ]      <- a constant

   Inference: none     data as written             probe: 0 rows    BookStoreShape: 0 targets
   Inference: rules    data + 33 inferred triples  probe: 33 rows   BookStoreShape: 33 targets

   the report is the only window onto the inferences
""",
    learn=[
        "A rule fires on its shape's focus nodes. A shape with no target has no focus nodes and its rules never run.",
        "Rules run before validation. Everything downstream -- targets, constraints, counts -- sees the inferred triples.",
        "To see what a rule produced, write a shape that reports it. An Info-severity SPARQL constraint is the usual form.",
    ],
    tryit="Set Inference back to none and validate again: no rows, and the headline still "
          "says Conforms. Then set it to rules.",
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:rule [
        a             sh:TripleRule ;
        sh:subject    sh:this ;
        sh:predicate  rdf:type ;
        sh:object     schema:BookStore ;
    ] .

# Reports each inferred type as information.
bt:TypeProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred: {$this} rdf:type {$value}" ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this rdf:type ?value .
              FILTER ( ?value = schema:BookStore )
            }
        \"\"\" ;
    ] .

# A shape whose target only exists once the rule has run.
bt:BookStoreShape
    a               sh:NodeShape ;
    sh:targetClass  schema:BookStore ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] .
""",
    data=DSHOPS, inference=RULES, declare=True, extra_prefixes=("schema",),
    expect=dict(conforms=True, infos=33, violations=0),
)
specs.register("s43", "afRules", "afTripleRule")

s(
    sid="s44", module=M,
    title="A value copied along a path",
    asks="Each shop gets a bs:townName: the label of the town it is in -- every label, in every language.",
    how="sh:object can be a path expression, [ sh:path P ], whose values are "
        "the values of P at the focus node. ( bs:locatedIn rdfs:label ) is a "
        "sequence path, so the rule copies the town's labels onto the shop. "
        "A triple rule produces the cross product of its three expressions, "
        "and here that matters: Wigtown has an English and a "
        "Gaelic label, so both shops there get two town names, and so does "
        "every shop in a town with a Welsh or Gaelic name. The probe lists "
        "45 inferred triples for 33 shops. bt:OneTownName is a Core "
        "constraint on the derived property with sh:maxCount 1, and under "
        "rules it reports the twelve shops with two: a constraint on an "
        "inferred property behaves like any other, and here it is telling "
        "you the rule copied more than you meant. Filtering the expression is "
        "s45's subject.",
    diagram="""
   sh:rule [ a sh:TripleRule ;
       sh:subject   sh:this ;
       sh:predicate bs:townName ;
       sh:object    [ sh:path ( bs:locatedIn rdfs:label ) ] ]

   bt:shop-inkwell --locatedIn--> bt:place-wigtown --label--> "Wigtown"@en, "Baile na h-Uige"@gd
        inferred:  bt:shop-inkwell bs:townName "Wigtown"@en
                   bt:shop-inkwell bs:townName "Baile na h-Uige"@gd      cross product: two triples

   bt:OneTownName   sh:path bs:townName ; sh:maxCount 1   ->  reports the bilingual towns' shops
""",
    learn=[
        "[ sh:path P ] as a node expression is 'the values of P at the focus node', and P can be any SHACL path.",
        "A triple rule multiplies out its expressions. Several values on one side mean several triples.",
        "Constraints apply to inferred triples exactly as to asserted ones. Use them to check what your rules did.",
    ],
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:rule [
        a             sh:TripleRule ;
        sh:subject    sh:this ;
        sh:predicate  bs:townName ;
        sh:object     [ sh:path ( bs:locatedIn rdfs:label ) ] ;
    ] .

bt:TownNameProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred: {$this} bs:townName {$value}" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:townName ?value }" ;
    ] .

bt:OneTownName
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      bs:townName ;
        sh:maxCount  1 ;
        sh:message   "{$this} has more than one town name: the rule copied every label." ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=False, infos=45, violations=12, focus=["shop-inkwell"]),
)
specs.register("s44", "afPathExpr", "afTripleRule")

s(
    sid="s45", module=M,
    title="Filtering the values",
    asks="Each shop gets a bs:inCountry: the one place above it that is a country.",
    how="A filter shape expression takes the values of one expression and "
        "keeps those that conform to a shape. sh:nodes is the input, here "
        "the path ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) that s20 "
        "used: every place above the shop's town. sh:filterShape is "
        "[ sh:class bs:Country ], and one place survives it. The rule "
        "asserts bs:inCountry, the probe shows 33 inferences, and "
        "bt:CountryRequired is a Core shape that only conforms once the rule "
        "has run: exactly one bs:inCountry, of class bs:Country. Set the "
        "dropdown to none and it reports 33 shops with none. The SPARQL "
        "course's q36 gets the same answer from a query.",
    diagram="""
   sh:object [
       sh:filterShape  [ sh:class bs:Country ] ;
       sh:nodes        [ sh:path ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) ]
   ]

   nodes:        { dumfries-galloway, scotland, gb }        from bt:shop-inkwell
   filterShape:  keep those that conform to [ sh:class bs:Country ]
   result:       { scotland }

   inferred:  bt:shop-inkwell  bs:inCountry  bt:place-scotland
""",
    learn=[
        "A filter shape expression is a WHERE clause for node expressions: input values in, conforming values out.",
        "Any shape can be the filter, so a filter can be as selective as a constraint.",
        "A Core shape that requires the inferred property is the cleanest test that a rule set did its job.",
    ],
    body="""
bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:rule [
        a             sh:TripleRule ;
        sh:subject    sh:this ;
        sh:predicate  bs:inCountry ;
        sh:object     [
            sh:filterShape  [ sh:class bs:Country ] ;
            sh:nodes        [ sh:path ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) ] ;
        ] ;
    ] .

bt:CountryProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred: {$this} bs:inCountry {$value}" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:inCountry ?value }" ;
    ] .

bt:CountryRequired
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      bs:inCountry ;
        sh:minCount  1 ;
        sh:maxCount  1 ;
        sh:class     bs:Country ;
        sh:message   "{$this} has no single country. Is the Inference dropdown set to rules?" ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=True, infos=33, violations=0),
)
specs.register("s45", "afFilterShape", "afNodeExpr")

s(
    sid="s46", module=M,
    title="Union and intersection",
    asks="Everyone who worked on a work, and the stocked works that match a shop's specialism.",
    how="sh:union and sh:intersection combine node expressions. "
        "bt:ContributorRule unions the author and the translator of a work "
        "into bs:contributor -- the SPARQL course's q18, as a rule -- which "
        "gives 74 works their authors and 5 translations their translators "
        "as well. bt:SpecialismRule intersects two sets at a shop: the works "
        "it stocks, and the works filed directly under the genre it "
        "specialises in, reached by ( bs:specialises [ sh:inversePath "
        "bs:genre ] ). What survives is bs:stocksInSpecialism, the stock that "
        "matches the sign over the door. The two probes count them.",
    diagram="""
   sh:union ( [ sh:path bs:author ] [ sh:path bs:translatedBy ] )
        { elin-morgan } U { noor-haddad }  =  { elin-morgan, noor-haddad }     two bs:contributor triples

   sh:intersection ( [ sh:path bs:stocks ]
                     [ sh:path ( bs:specialises [ sh:inversePath bs:genre ] ) ] )
        works stocked  n  works in the shop's own genre
""",
    learn=[
        "sh:union takes a list of expressions and yields their values together; sh:intersection yields the values in every one.",
        "Both take lists, so three or more expressions combine at once.",
        "An inverse path inside an expression is how a rule looks backwards -- here from a genre to the works filed under it.",
    ],
    body="""
bt:WorkShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:rule [
        a             sh:TripleRule ;
        sh:subject    sh:this ;
        sh:predicate  bs:contributor ;
        sh:object     [ sh:union ( [ sh:path bs:author ] [ sh:path bs:translatedBy ] ) ] ;
    ] .

bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:rule [
        a             sh:TripleRule ;
        sh:subject    sh:this ;
        sh:predicate  bs:stocksInSpecialism ;
        sh:object     [ sh:intersection (
                            [ sh:path bs:stocks ]
                            [ sh:path ( bs:specialises [ sh:inversePath bs:genre ] ) ]
                        ) ] ;
    ] .

bt:ContributorProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Translation ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred: {$this} bs:contributor {$value}" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:contributor ?value }" ;
    ] .

bt:SpecialismProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred: {$this} bs:stocksInSpecialism {$value}" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:stocksInSpecialism ?value }" ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=True, min_infos=12, violations=0),
)
specs.register("s46", "afUnion", "afIntersection")

s(
    sid="s47", module=M,
    title="A rule written in SPARQL",
    asks="The value of each stock line, and a flag on every work without an ISBN.",
    how="A sh:SPARQLRule runs a CONSTRUCT with $this pre-bound to the focus "
        "node, and every triple the template produces is inferred. Anything "
        "a triple rule cannot say -- arithmetic, a BIND, a FILTER NOT EXISTS "
        "-- goes here. bt:StockValueRule multiplies copies by shelf price, "
        "which is the SPARQL course's q21 done once per record and kept. "
        "bt:UnnumberedRule flags the works with no bs:isbn. The probes list "
        "the stock lines worth more than two hundred pounds and the eleven "
        "flagged works. The same pre-binding rules as sh:sparql apply: no "
        "MINUS, VALUES or SERVICE, and the prefixes come from sh:prefixes.",
    diagram="""
   sh:rule [ a sh:SPARQLRule ;
       sh:construct \"\"\"
           CONSTRUCT { $this bs:stockValue ?v }
           WHERE     { $this bs:copies ?c ; bs:shelfPrice ?p . BIND ( ?c * ?p AS ?v ) }
       \"\"\" ]

   bt:stock-inkwell--the-book-town   12 x 9.99   ->   bs:stockValue 119.88

   CONSTRUCT { $this bs:isbnMissing true } WHERE { FILTER NOT EXISTS { $this bs:isbn ?i } }
""",
    learn=[
        "A SPARQL rule is a CONSTRUCT per focus node. It is the escape hatch when a triple rule's three expressions are not enough.",
        "$this in the template is the focus node. Triples about other nodes can be built too; the template is free.",
        "The pre-binding restrictions of s34 apply to sh:construct as they do to sh:select.",
    ],
    body="""
bt:StockRecordShape
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:rule [
        a             sh:SPARQLRule ;
        sh:prefixes   bt:prefixes ;
        sh:construct  \"\"\"
            CONSTRUCT { $this bs:stockValue ?v }
            WHERE {
              $this bs:copies ?c ; bs:shelfPrice ?p .
              BIND ( ?c * ?p AS ?v )
            }
        \"\"\" ;
    ] .

bt:WorkShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:rule [
        a             sh:SPARQLRule ;
        sh:prefixes   bt:prefixes ;
        sh:construct  \"\"\"
            CONSTRUCT { $this bs:isbnMissing true }
            WHERE { FILTER NOT EXISTS { $this bs:isbn ?i } }
        \"\"\" ;
    ] .

bt:ValueProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred: {$this} bs:stockValue {$value} (over 200)" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:stockValue ?value FILTER ( ?value > 200 ) }" ;
    ] .

bt:UnnumberedProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred: {$this} bs:isbnMissing true" ;
        sh:select    "SELECT $this WHERE { $this bs:isbnMissing true }" ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=True, min_infos=12, violations=0, focus=["book-hedgerow-alphabet"]),
)
specs.register("s47", "afSparqlRule", "sparqlConstruct")

s(
    sid="s48", module=M,
    title="Conditions, and a rule switched off",
    asks="Shops with a cafe get an amenity; shops without a website get a status; a third rule is present and inactive.",
    how="sh:condition names one or more shapes the focus node must conform "
        "to before the rule fires. bt:CafeRule fires only for shops that "
        "conform to bt:HasCafe, and 22 do. bt:OfflineRule uses a negated "
        "condition, [ sh:not bt:HasWebsite ], and fires for the six without "
        "one: negation as failure, which s52 comes back to. bt:SecondHandRule "
        "carries sh:deactivated true and produces nothing; a rule can be "
        "kept in the file and out of the run exactly as a shape can. The "
        "probe shows the 28 inferred triples.",
    diagram="""
   sh:rule [ a sh:TripleRule ;
       sh:condition bt:HasCafe ;                  <- fires only if $this conforms to this shape
       sh:subject sh:this ; sh:predicate bs:amenity ; sh:object "cafe" ]

   bt:HasCafe  a sh:NodeShape ; sh:property [ sh:path bs:hasCafe ; sh:hasValue true ]

   sh:condition [ sh:not bt:HasWebsite ]         <- fires if $this does NOT conform

   sh:deactivated true                           <- compiled, never fired
""",
    learn=[
        "sh:condition is a guard: a conformance check of the focus node before the rule runs. Several conditions must all hold.",
        "[ sh:not S ] as a condition is negation as failure: the rule fires because something is absent.",
        "sh:deactivated works on rules as on shapes.",
    ],
    body="""
bt:HasCafe     a sh:NodeShape ; sh:property [ sh:path bs:hasCafe ; sh:hasValue true ] .
bt:HasWebsite  a sh:NodeShape ; sh:property [ sh:path bs:website ; sh:minCount 1 ] .

bt:BookshopShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:rule [
        a             sh:TripleRule ;
        sh:condition  bt:HasCafe ;
        sh:subject    sh:this ;
        sh:predicate  bs:amenity ;
        sh:object     "cafe" ;
    ] ;
    sh:rule [
        a             sh:TripleRule ;
        sh:condition  [ sh:not bt:HasWebsite ] ;
        sh:subject    sh:this ;
        sh:predicate  bs:status ;
        sh:object     "offline" ;
    ] ;
    sh:rule [
        a               sh:TripleRule ;
        sh:deactivated  true ;
        sh:subject      sh:this ;
        sh:predicate    bs:amenity ;
        sh:object       "second-hand" ;
    ] .

bt:AmenityProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred: {$this} has {$value}" ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              { $this bs:amenity ?value } UNION { $this bs:status ?value }
            }
        \"\"\" ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=True, infos=28, violations=0),
)
specs.register("s48", "afCondition", "afRuleDeactivated")

s(
    sid="s49", module=M,
    title="Order, and rules that feed rules",
    asks="A shop's country, then the country's name from it -- and the same second rule placed where it sees nothing.",
    how="Rules run in ascending sh:order, and every rule at one order sees "
        "the graph as it stood before that order began. bt:CountryRule at "
        "order 0 infers bs:inCountry as in s45. bt:NameRule at order 1 reads "
        "bs:inCountry and copies the country's labels to bs:countryName; the "
        "probe shows it fired for every shop. bt:NameRuleTooEarly is the same "
        "rule at order 0, in the same shape as the rule it depends on, and "
        "infers nothing: bs:inCountry did not exist when order 0 began. The "
        "second probe reports zero rows for it. sh:order is set on the "
        "shape, and it is the only sequencing SHACL-AF offers.",
    diagram="""
   order 0    bt:CountryRule        shop bs:inCountry country
              bt:NameRuleTooEarly   reads bs:inCountry ... which is not there yet   -> nothing
   order 1    bt:NameRule           reads bs:inCountry                             -> countryName

   a rule sees the graph as it was when its order began
""",
    learn=[
        "A rule that consumes what another produces must be at a higher sh:order, on a different shape.",
        "Same order means same view of the data. Two rules at order 0 cannot see each other's results.",
        "When a rule infers nothing, check the order before the expressions.",
    ],
    body="""
bt:CountryShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:order        0 ;
    sh:rule [
        a             sh:TripleRule ;
        sh:subject    sh:this ;
        sh:predicate  bs:inCountry ;
        sh:object     [ sh:filterShape [ sh:class bs:Country ] ;
                        sh:nodes [ sh:path ( bs:locatedIn [ sh:oneOrMorePath bs:within ] ) ] ] ;
    ] ;
    # Same order as the rule it depends on: sees no bs:inCountry, infers nothing.
    sh:rule [
        a             sh:TripleRule ;
        sh:subject    sh:this ;
        sh:predicate  bs:countryNameTooEarly ;
        sh:object     [ sh:path ( bs:inCountry rdfs:label ) ] ;
    ] .

bt:NameShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:order        1 ;
    sh:rule [
        a             sh:TripleRule ;
        sh:subject    sh:this ;
        sh:predicate  bs:countryName ;
        sh:object     [ sh:path ( bs:inCountry rdfs:label ) ] ;
    ] .

bt:NameProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "inferred at order 1: {$this} bs:countryName {$value}" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:countryName ?value }" ;
    ] .

bt:TooEarlyProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "inferred at order 0: {$this} bs:countryNameTooEarly {$value} -- should never appear" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:countryNameTooEarly ?value }" ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=True, min_infos=33, warnings=0, violations=0),
)
specs.register("s49", "afOrder", "afExecution")

s(
    sid="s50", module=M,
    title="One pass",
    asks="bs:within made transitive by a rule, run once: how far a single pass reaches.",
    how="bs:within is declared transitive in the vocabulary, and the clean "
        "data asserts 63 direct links. bt:TransitiveRule is the transitivity "
        "axiom as a SPARQL rule: where $this is within B and B is within C, "
        "$this is within C. SHACL-AF defines one pass, so each place gains "
        "the links two hops long and no more: the probe counts 63 asserted "
        "plus the two-hop pairs, and a settlement four levels below Great "
        "Britain still has no direct link to it. The SPARQL course's module "
        "18 measures the same closure with a reasoner and with a property "
        "path: 186 pairs. s51 is this file again, iterated.",
    diagram="""
   asserted      york -> north-yorkshire -> yorkshire -> england -> gb          (4 links)
   one pass adds york -> yorkshire, north-yorkshire -> england, yorkshire -> gb  (2 hops)
   still missing york -> england, york -> gb, north-yorkshire -> gb             (3 and 4 hops)

   Inference: rules            one pass, as SHACL-AF defines
   Inference: rules, iterated  repeated to a fixpoint (s51)
""",
    learn=[
        "A SHACL-AF rule set runs once. A rule whose output is its own input reaches one more step, and stops.",
        "The specification declines to define repetition. What an engine does about that is the engine's, not SHACL's.",
        "Before writing a transitive rule, ask whether a property path at query time would do (the SPARQL course, q27 and q140).",
    ],
    body="""
bt:PlaceShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:rule [
        a             sh:SPARQLRule ;
        sh:prefixes   bt:prefixes ;
        sh:construct  \"\"\"
            CONSTRUCT { $this bs:within ?c }
            WHERE     { $this bs:within ?b . ?b bs:within ?c . }
        \"\"\" ;
    ] .

# Counts every bs:within link a place has, asserted or inferred.
bt:WithinProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} bs:within {$value}" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:within ?value }" ;
    ] .

# True only once the closure is complete.
bt:ReachesGB
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:property [
        sh:path      bs:within ;
        sh:hasValue  bt:place-gb ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} has no direct bs:within link to Great Britain yet." ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=True, min_infos=100, min_warnings=1),
)
specs.register("s50", "afEntailment", "afExecution")

s(
    sid="s51", module=M,
    title="To a fixpoint",
    asks="The same rule, repeated until nothing new appears: the full closure, and the count the SPARQL course measured.",
    how="This is s50's file with the Inference dropdown at rules, iterated. "
        "The engine runs the rule set, adds what it produced, and runs it "
        "again until a round adds nothing, up to ten rounds. The probe now "
        "counts 186 bs:within pairs -- the number the SPARQL course's "
        "reasoning table gives for the OWL reasoners and for the path "
        "bs:within+ -- and bt:ReachesGB reports nothing, because every "
        "settlement now has its direct link to Great Britain. Iteration is "
        "outside SHACL-AF. It is useful for a rule like this one and unsafe "
        "for a rule that tests for absence, which is s52.",
    diagram="""
   round 1   two-hop links appear
   round 2   three- and four-hop links appear
   round 3   nothing new  ->  stop

   63 asserted  ->  186 pairs, the same 186 as bs:within+ in the SPARQL course
""",
    learn=[
        "Iterating a rule set gives the least fixpoint for rules that only add. The result is what a reasoner would materialise.",
        "The ten-round cap is a safety net. A rule that mints a new term every round never settles, and the engine stops with an error rather than running out of memory.",
        "A validator does not persist inferences. To keep the closure, run the same CONSTRUCT in the SPARQL course's module 17 and store it.",
    ],
    body="""
bt:PlaceShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:rule [
        a             sh:SPARQLRule ;
        sh:prefixes   bt:prefixes ;
        sh:construct  \"\"\"
            CONSTRUCT { $this bs:within ?c }
            WHERE     { $this bs:within ?b . ?b bs:within ?c . }
        \"\"\" ;
    ] .

bt:WithinProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} bs:within {$value}" ;
        sh:select    "SELECT $this ?value WHERE { $this bs:within ?value }" ;
    ] .

bt:ReachesGB
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:property [
        sh:path      bs:within ;
        sh:hasValue  bt:place-gb ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} has no direct bs:within link to Great Britain yet." ;
    ] .
""",
    data=D11, inference=RULES_ITERATED, declare=True,
    expect=dict(conforms=True, infos=186, warnings=0),
)
specs.register("s51", "afEntailment", "r12overview")

s(
    sid="s52", module=M,
    title="Negation that goes stale",
    asks="Mark the shops without a website, then give every such shop a placeholder website -- and see the mark outlive its reason.",
    how="bt:MarkRule at order 1 gives a shop with no website a bs:status "
        "\"offline\", a conclusion drawn from absence. bt:FillRule at order 2 "
        "gives the same shops a placeholder bs:website. Rules only add, so "
        "after the run six shops have both a website and a status that says "
        "they have none. The probe finds them. Swapping the orders would fix "
        "this case, because the mark would then be tested after the fill, "
        "and the true fix in general is to make sure nothing later supplies "
        "what a rule tested the absence of. SHACL 1.2 Rules (SPARQL-RL) "
        "requires a rule set to be stratified so that negation only looks at "
        "strata that are already complete; SHACL-AF has no such requirement, "
        "and the responsibility is the author's.",
    diagram="""
   order 1   MarkRule    condition [ sh:not HasWebsite ]   ->  shop bs:status "offline"     (6 shops)
   order 2   FillRule    condition [ sh:not HasWebsite ]   ->  shop bs:website <placeholder> (6 shops)

   after the run:   bt:shop-marginalia  bs:website <...pending> ;  bs:status "offline" .
                    both true in the graph; the second no longer true of the data

   SPARQL-RL: stratify, so that NOT EXISTS is only ever evaluated over a finished stratum
""",
    learn=[
        "A rule that tests for absence draws a conclusion that a later rule can invalidate. Rules never retract.",
        "Order the rule set so that nothing after a negation supplies what it tested for, or keep to a single pass and check by hand.",
        "Stratified negation is what SHACL 1.2 Rules adds; until then it is a discipline rather than a guarantee.",
    ],
    body="""
bt:HasWebsite  a sh:NodeShape ; sh:property [ sh:path bs:website ; sh:minCount 1 ] .

bt:MarkShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:order        1 ;
    sh:rule [
        a             sh:TripleRule ;
        sh:condition  [ sh:not bt:HasWebsite ] ;
        sh:subject    sh:this ;
        sh:predicate  bs:status ;
        sh:object     "offline" ;
    ] .

bt:FillShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:order        2 ;
    sh:rule [
        a             sh:TripleRule ;
        sh:condition  [ sh:not bt:HasWebsite ] ;
        sh:subject    sh:this ;
        sh:predicate  bs:website ;
        sh:object     <https://example.org/bookshop-trail/website-pending> ;
    ] .

bt:StaleProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} is marked offline and has the website {$value}: the mark outlived its reason." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:status "offline" ; bs:website ?value .
            }
        \"\"\" ;
    ] .
""",
    data=D11, inference=RULES, declare=True,
    expect=dict(conforms=True, warnings=6, violations=0, focus=["shop-marginalia"]),
)
specs.register("s52", "r12negation", "r12stratification")
