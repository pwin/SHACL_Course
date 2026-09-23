# -*- coding: utf-8 -*-
"""Module 06 -- Your own constraint components."""
from shapecat import s, Query, D11, DFAULTY
import specs

M = "06-constraint-components"

s(
    sid="s39", module=M,
    title="An ISBN check digit",
    asks="Every ISBN-13's last digit is the check digit its first twelve imply.",
    how="s15 showed that a pattern cannot add up. A constraint component "
        "can: it is a sh:ConstraintComponent with one or more sh:parameter "
        "declarations and a validator, and once declared it is used like a "
        "Core component -- here as bt:isbn13 true on a property shape. The "
        "validator is a sh:SPARQLAskValidator: an ASK that must come back "
        "true for a value to pass, with $value bound to the value and each "
        "parameter bound to its own variable. The query weights the twelve "
        "digits 1, 3, 1, 3 and so on, sums them, and compares the check "
        "digit. All 63 ISBNs in the clean data pass; the one with the wrong "
        "last digit (F10) fails. A value that does not match the thirteen-"
        "digit pattern is left to s15's sh:pattern and passes here, so the "
        "hyphenated ISBN is not reported twice. SPARQL has no modulus "
        "operator, so the arithmetic is written with FLOOR, in BINDs that "
        "keep the ASK readable.",
    diagram="""
   bt:ISBN13ConstraintComponent
     sh:parameter [ sh:path bt:isbn13 ]           <- the property that switches it on
     sh:validator [ a sh:SPARQLAskValidator ;
        sh:ask "ASK { FILTER ( <check digit arithmetic on $value> ) }" ]

   a property shape uses it:   sh:property [ sh:path bs:isbn ; bt:isbn13 true ]

   9 7 8 0 1 4 1 1 8 7 7 6 | 2
   x1x3x1x3x1x3x1x3x1x3x1x3          sum 109  ->  (10 - 9) mod 10 = 1  !=  2   -> fails

   SPARQL has no modulus operator; x mod 10 is written x - 10 * FLOOR(x / 10)
""",
    learn=[
        "A constraint component is a parameter plus a validator. Declaring one turns a query into vocabulary.",
        "An ASK validator answers per value: true passes. $value is the value, $this the focus node, $PATH the path, and every parameter is a variable of the same name.",
        "Leave what a Core component already checks to that component. A custom validator should test one thing.",
    ],
    body="""
bt:ISBN13ConstraintComponent
    a  sh:ConstraintComponent ;
    rdfs:label  "ISBN-13 check digit" ;
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
                     + xsd:integer(SUBSTR(?s, 11, 1)) + 3 * xsd:integer(SUBSTR(?s, 12, 1))
                     AS ?sum )
              # SPARQL has no modulus operator: x mod 10 is x - 10 * FLOOR(x / 10)
              BIND ( 10 - (?sum - 10 * FLOOR(?sum / 10)) AS ?c )
              BIND ( ?c - 10 * FLOOR(?c / 10) AS ?check )
              FILTER ( !REGEX(?s, "^97[89][0-9]{10}$") || ?check = xsd:integer(SUBSTR(?s, 13, 1)) )
            }
        \"\"\" ;
    ] .

bt:WorkShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [
        sh:path    bs:isbn ;
        bt:isbn13  true ;
    ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, violations=1, focus=["book-precocious"], nofocus=["book-the-margin-notes", "book-the-dark-sea-fr"]),
)
specs.register("s39", "components", "askValidator")

s(
    sid="s40", module=M,
    title="A SELECT validator with parameters",
    asks="A value is at most some multiple of a value reached through two properties -- a shelf price against a recommended price, said generally.",
    how="s31 wrote 'shelf price at most twice the RRP' as a SPARQL constraint "
        "with the properties spelled out. bt:MaxMultipleOfConstraintComponent "
        "makes the same check reusable: three parameters, bt:maxMultipleOf "
        "for the factor, bt:viaProperty for the hop to the other node and "
        "bt:comparedWith for the property there. A sh:propertyValidator with "
        "a SELECT returns one row per failing value, and $PATH inside it is "
        "the using shape's path. sh:labelTemplate gives the constraint a "
        "readable name that tools can show. The one record at three times "
        "the recommended price (F23) is reported, exactly as in s31, and the "
        "shape that uses the component is three lines.",
    diagram="""
   component            parameters                  validator
   bt:MaxMultipleOf...  bt:maxMultipleOf (decimal)   SELECT $this ?value WHERE {
                        bt:viaProperty   (IRI)         $this $PATH ?value ; $viaProperty ?other .
                        bt:comparedWith  (IRI)         ?other $comparedWith ?reference .
                                                       FILTER ( ?value > $maxMultipleOf * ?reference ) }

   use    sh:property [ sh:path bs:shelfPrice ;
                        bt:maxMultipleOf 2.0 ; bt:viaProperty bs:ofWork ; bt:comparedWith bs:rrp ]
""",
    learn=[
        "A SELECT validator returns the failing rows, like sh:sparql; an ASK validator answers per value. Use SELECT when the query is a join.",
        "Parameters that are IRIs can stand for predicates in the pattern, which is how a component stays general.",
        "sh:propertyValidator is for property shapes and may use $PATH; sh:nodeValidator is for node shapes; sh:validator serves both.",
    ],
    body="""
bt:MaxMultipleOfConstraintComponent
    a  sh:ConstraintComponent ;
    rdfs:label        "at most a multiple of a value elsewhere" ;
    sh:labelTemplate  "at most {$maxMultipleOf} times {$viaProperty}/{$comparedWith}" ;
    sh:parameter [ sh:path bt:maxMultipleOf ; sh:datatype xsd:decimal ] ;
    sh:parameter [ sh:path bt:viaProperty ;   sh:nodeKind sh:IRI ] ;
    sh:parameter [ sh:path bt:comparedWith ;  sh:nodeKind sh:IRI ] ;
    sh:propertyValidator [
        a  sh:SPARQLSelectValidator ;
        sh:prefixes  bt:prefixes ;
        sh:message   "{$value} is more than the allowed multiple of the reference price." ;
        sh:select  \"\"\"
            SELECT $this ?value WHERE {
              $this $PATH ?value ;
                    $viaProperty ?other .
              ?other $comparedWith ?reference .
              FILTER ( ?value > $maxMultipleOf * ?reference )
            }
        \"\"\" ;
    ] .

bt:StockRecordShape
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:property [
        sh:path           bs:shelfPrice ;
        bt:maxMultipleOf  2.0 ;
        bt:viaProperty    bs:ofWork ;
        bt:comparedWith   bs:rrp ;
    ] .
""",
    data=DFAULTY, declare=True,
    expect=dict(conforms=False, violations=1, focus=["stock-foxed-page"]),
)
specs.register("s40", "selectValidator", "parameters")

s(
    sid="s41", module=M,
    title="A required language, and an optional parameter",
    asks="Every Welsh place has a Welsh name -- with an option to accept one from skos:altLabel.",
    how="sh:languageIn says which languages are allowed; nothing in Core says "
        "one is required. bt:RequiredLanguageConstraintComponent does: "
        "bt:requiredLanguage names a tag, and the property validator reports "
        "a focus node with no value of $PATH in that language. A second "
        "parameter, bt:alsoAccept, is marked sh:optional true: when the "
        "using shape leaves it out the variable is unbound, and the query "
        "copes with COALESCE. The shape targets the places inside Wales with "
        "a SPARQL target from s33. Three council areas -- Powys, Ceredigion "
        "and the City of Cardiff -- have English names only, and are "
        "reported as warnings; the towns all have Welsh ones.",
    diagram="""
   sh:parameter [ sh:path bt:requiredLanguage ]                      required
   sh:parameter [ sh:path bt:alsoAccept ; sh:optional true ]         may be absent

   SELECT $this WHERE {
     FILTER NOT EXISTS {
       { $this $PATH ?l }
       UNION
       { $this ?p ?l . FILTER ( BOUND($alsoAccept) && ?p = $alsoAccept ) }
       FILTER ( LANG(?l) = $requiredLanguage )
     }
   }

   bt:place-powys   rdfs:label "Powys"@en        no @cy  ->  warning
""",
    learn=[
        "A component can require what Core can only permit. 'At least one value in language X' is one line once the component exists.",
        "sh:optional true on a parameter means the variable may be unbound. Test with BOUND or COALESCE rather than assuming.",
        "Targets and components compose: the component says what to check, the target says of whom.",
    ],
    body="""
bt:RequiredLanguageConstraintComponent
    a  sh:ConstraintComponent ;
    rdfs:label  "a value in a required language" ;
    sh:parameter [ sh:path bt:requiredLanguage ; sh:datatype xsd:string ] ;
    sh:parameter [ sh:path bt:alsoAccept ; sh:nodeKind sh:IRI ; sh:optional true ] ;
    sh:propertyValidator [
        a  sh:SPARQLSelectValidator ;
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} has no name in the required language." ;
        sh:select  \"\"\"
            SELECT $this WHERE {
              FILTER NOT EXISTS {
                { $this $PATH ?l }
                UNION
                { $this ?p ?l . FILTER ( BOUND($alsoAccept) && ?p = $alsoAccept ) }
                FILTER ( LANG(?l) = $requiredLanguage )
              }
            }
        \"\"\" ;
    ] .

bt:WelshPlaceShape
    a  sh:NodeShape ;
    sh:target [
        a            sh:SPARQLTarget ;
        sh:prefixes  bt:prefixes ;
        sh:select    "SELECT ?this WHERE { ?this bs:within+ bt:place-wales }" ;
    ] ;
    sh:property [
        sh:path              rdfs:label ;
        bt:requiredLanguage  "cy" ;
        bt:alsoAccept        skos:altLabel ;
        sh:severity          sh:Warning ;
    ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, warnings=3, focus=["place-powys", "place-ceredigion", "place-city-of-cardiff"]),
)
specs.register("s41", "parameters", "labelTemplate")

s(
    sid="s42", module=M,
    title="Core components are SPARQL too",
    asks="sh:minCount and sh:minInclusive written as constraint components -- the second in a version that understands years.",
    how="Appendix D of the specification defines every Core component as a "
        "SPARQL validator. bt:AtLeastConstraintComponent is sh:minCount in "
        "that form, with one difference forced by this engine: a SELECT "
        "property validator here runs once per value node, so a validator "
        "that counts values never runs when there are none. The component is "
        "therefore declared for node shapes, with the property to count as a "
        "second parameter, and a sh:nodeValidator counts the values of "
        "$countProperty per focus node. It finds the Hebrew translation "
        "without a translator that s08 found. bt:MinYearConstraintComponent "
        "is what sh:minInclusive would be if it cast a gYear to an integer "
        "first, which is the fix s14 wrote by hand: an ASK validator "
        "comparing xsd:integer(STR($value)) with the parameter. Two works in "
        "the clean data were published before 1950, and are reported as "
        "information. Writing a Core component out this way is the quickest "
        "way to see what it does, and the quickest way to make a version that "
        "does something slightly different.",
    diagram="""
   Appendix D, sh:minCount, as a query:
     SELECT $this WHERE {
       { SELECT $this (COUNT(?v) AS ?n) WHERE { OPTIONAL { $this $PATH ?v } } GROUP BY $this }
       FILTER ( ?n < $minCount ) }

   here, as a node-shape component:   bt:TranslationShape  bt:countProperty bs:translatedBy ; bt:atLeast 1
     (a property validator would run per value on this engine, and a node with no values has none)

   bt:minYear 1950 on bs:publicationYear:
     ASK { FILTER ( xsd:integer(STR($value)) >= $minYear ) }
     "1948"^^xsd:gYear -> 1948 >= 1950 is false -> reported, where sh:minInclusive could not compare at all
""",
    learn=[
        "Every Core component has a SPARQL definition in Appendix D. When one behaves unexpectedly, read that first.",
        "A custom component can be a Core component with one change. That is often the right fix for a datatype the engine will not compare.",
        "On this engine, SELECT property validators run per value, ASK validators run per value, and node validators run per focus node. Count with a node validator.",
    ],
    body="""
bt:AtLeastConstraintComponent
    a  sh:ConstraintComponent ;
    rdfs:label  "at least N values of a property (sh:minCount, written out)" ;
    sh:parameter [ sh:path bt:countProperty ; sh:nodeKind sh:IRI ] ;
    sh:parameter [ sh:path bt:atLeast ;       sh:datatype xsd:integer ] ;
    sh:nodeValidator [
        a  sh:SPARQLSelectValidator ;
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} has fewer values of the counted property than required." ;
        sh:select  \"\"\"
            SELECT $this WHERE {
              { SELECT $this (COUNT(?v) AS ?n)
                WHERE { OPTIONAL { $this $countProperty ?v } }
                GROUP BY $this }
              FILTER ( ?n < $atLeast )
            }
        \"\"\" ;
    ] .

bt:MinYearConstraintComponent
    a  sh:ConstraintComponent ;
    rdfs:label  "not before a year (sh:minInclusive for xsd:gYear)" ;
    sh:parameter [ sh:path bt:minYear ; sh:datatype xsd:integer ] ;
    sh:validator [
        a  sh:SPARQLAskValidator ;
        sh:prefixes  bt:prefixes ;
        sh:message   "{$value} is earlier than the year allowed." ;
        sh:ask  "ASK { FILTER ( xsd:integer(STR($value)) >= $minYear ) }" ;
    ] .

bt:TranslationShape
    a                 sh:NodeShape ;
    sh:targetClass    bs:Translation ;
    bt:countProperty  bs:translatedBy ;
    bt:atLeast        1 .

bt:YearShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [ sh:path bs:publicationYear ; bt:minYear 1950 ; sh:severity sh:Info ] .

bt:FoundedShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [ sh:path bs:founded ; bt:minYear 1900 ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, violations=1, infos=2, focus=["book-cold-harbour-he", "book-north-of-the-tweed"]),
)
specs.register("s42", "coreValidators", "components")
