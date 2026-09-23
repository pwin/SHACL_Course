# -*- coding: utf-8 -*-
"""Module 08 -- SHACL 1.2 and RDF 1.2."""
from shapecat import s, Query, D11, D12, DFAULTY, DFAULTY12
import specs

M = "08-shacl-1-2"

s(
    sid="s53", module=M,
    title="Two founding dates",
    asks="A shop has one founding year -- unless each year is a claim with a source, in which case it may have several.",
    how="bookshop-trail-1.2.ttl is the RDF 1.2 edition: the same data plus "
        "annotations. Four shops have two founding years, each written as "
        "bs:founded 1919 {| bs:claimedBy ...; bs:confidence ... |}, and the "
        "SPARQL course's q61 to q63 are about choosing between them. "
        "bt:OneFoundingYear is s04's sh:maxCount 1, and on this data it "
        "reports the four, plus the faulty claim on Marginalia (F33), as "
        "warnings. bt:SourcedClaims is the SHACL 1.2 answer: allow several "
        "values, and require every reifier of a bs:founded triple to conform "
        "to a shape -- a source of class bs:Source, a confidence no higher "
        "than 1. sh:reifierShape checks the annotation rather than the "
        "value. The claim on Marginalia has no source and a confidence of "
        "1.4, and is the one violation. sh:reificationRequired true would "
        "also demand that every founding year be a claim; this build of the "
        "engine reads it and does not enforce it, so the 28 unannotated "
        "years pass.",
    diagram="""
   bt:shop-ex-libris  bs:founded "1919"^^xsd:gYear {| bs:claimedBy bt:source-national-register ; bs:confidence 0.99 |} .
   bt:shop-ex-libris  bs:founded "1921"^^xsd:gYear {| bs:claimedBy bt:source-local-paper ;        bs:confidence 0.40 |} .

   sh:maxCount 1 on bs:founded         two values  ->  reported

   sh:reifierShape [ ... ]  on bs:founded
        for each reifier of << shop bs:founded year >>:  does it conform?
        Marginalia's claim: no bs:claimedBy, confidence 1.4   ->  violation, value 1960
""",
    learn=[
        "In RDF 1.2 a triple can carry annotations through a reifier. SHACL 1.2's sh:reifierShape validates the reifier, not the value.",
        "A cardinality that was right for plain data may be wrong for annotated data. Decide whether several claims are allowed before you constrain the count.",
        "sh:reificationRequired is in the draft and parsed by this engine, and not enforced by this build. Check what your validator does with it.",
    ],
    body="""
bt:OneFoundingYear
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path      bs:founded ;
        sh:maxCount  1 ;
        sh:severity  sh:Warning ;
        sh:message   "{$this} has more than one founding year on record." ;
    ] .

bt:SourcedClaims
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path                  bs:founded ;
        sh:reifierShape [
            sh:property [ sh:path bs:claimedBy ;  sh:minCount 1 ; sh:class bs:Source ] ;
            sh:property [ sh:path bs:confidence ; sh:maxInclusive 1 ; sh:minInclusive 0 ] ;
        ] ;
        sh:reificationRequired   true ;
        sh:message               "A founding year of {$value} is claimed without a proper source." ;
    ] .
""",
    data=DFAULTY12,
    expect=dict(conforms=False, violations=30, warnings=5, focus=["shop-marginalia", "shop-ex-libris"]),
)
specs.register("s53", "c12reifier", "turtle12annot")

s(
    sid="s54", module=M,
    title="Constraining the claims themselves",
    asks="Every claim names one statement and a real source, and a claim about a founding year is about a bookshop.",
    how="A reifier is a node like any other, so it can be a focus node. "
        "sh:targetSubjectsOf bs:claimedBy picks every claim in the data, and "
        "the first two property shapes say it reifies exactly one statement "
        "and names a bs:Source. The attendance claimed by \"the manager\" "
        "(F34) fails the second. The third constraint looks inside the "
        "statement: rdf:reifies <<( ?shop bs:founded ?year )>> is a triple "
        "term pattern, and SPARQL 1.2 can match it. It requires the subject "
        "of a founding-year claim to be a bookshop, which all of them are, "
        "and the information rows list what each claim is about. Reifiers "
        "here are blank nodes, so the report shows them by label; the "
        "SPARQL course's q64 explains why that is what the annotation "
        "syntax produces.",
    diagram="""
   _:c1  rdf:reifies  <<( bt:shop-ex-libris bs:founded "1919"^^xsd:gYear )>> ;
         bs:claimedBy bt:source-national-register ;
         bs:confidence 0.99 .

   sh:targetSubjectsOf bs:claimedBy      ->  _:c1 and every other claim is a focus node

   SELECT $this ?value WHERE { $this rdf:reifies <<( ?value bs:founded ?year )>> }
        a triple term pattern: ?value binds to the shop inside the statement
""",
    learn=[
        "A reifier can be targeted and constrained directly. sh:targetSubjectsOf on the annotation property finds them all.",
        "A SPARQL constraint can take a triple term apart with <<( s p o )>> in the pattern.",
        "Blank-node reifiers appear in the report under the engine's labels. Name reifiers with ~ if you want stable identifiers (RDF 1.2 Turtle).",
    ],
    body="""
bt:ClaimShape
    a                    sh:NodeShape ;
    sh:targetSubjectsOf  bs:claimedBy ;
    sh:nodeKind          sh:BlankNode ;
    sh:property [
        sh:path      rdf:reifies ;
        sh:minCount  1 ;
        sh:maxCount  1 ;
        sh:message   "A claim reifies exactly one statement." ;
    ] ;
    sh:property [
        sh:path      bs:claimedBy ;
        sh:class     bs:Source ;
        sh:message   "{$value} is not a bs:Source." ;
    ] ;
    sh:property [
        sh:path          bs:confidence ;
        sh:datatype      xsd:decimal ;
        sh:minInclusive  0 ;
        sh:maxInclusive  1 ;
    ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "A founding-year claim about {$value}, which is not a bookshop." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this rdf:reifies <<( ?value bs:founded ?year )>> .
              FILTER NOT EXISTS { ?value a bs:Bookshop }
            }
        \"\"\" ;
    ] ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} is a claim about {$value}." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this rdf:reifies <<( ?value ?p ?o )>> .
            }
        \"\"\" ;
    ] .
""",
    data=DFAULTY12, declare=True,
    expect=dict(conforms=False, violations=1, min_infos=10, messages=["the manager is not a bs:Source"]),
)
specs.register("s54", "rdf12triples", "targetSubjectsOf")

s(
    sid="s55", module=M,
    title="The same fact modelled twice",
    asks="The RDF 1.1 stock records and the RDF 1.2 stock annotations agree on every count.",
    how="The 1.2 edition carries the stock twice: as bs:StockRecord nodes "
        "with bs:atShop, bs:ofWork and bs:copies, and as annotations on "
        "shop bs:stocks work. The SPARQL course's q68 shows the two side by "
        "side; this constraint checks that they agree. For each record it "
        "finds the annotation on the same shop and work through a triple "
        "term pattern and compares the counts. One annotation in the faulty "
        "data says thirteen copies where the record says twelve (F35). A "
        "check like this is what keeps a migration from RDF 1.1 to RDF 1.2 "
        "(q86, q121 in the SPARQL course) from drifting.",
    diagram="""
   RDF 1.1     bt:stock-inkwell--the-book-town  a bs:StockRecord ;
                   bs:atShop bt:shop-inkwell ; bs:ofWork bt:book-the-book-town ; bs:copies 12 .
   RDF 1.2     bt:shop-inkwell bs:stocks bt:book-the-book-town {| bs:copies 13 |} .

   SELECT $this ?value WHERE {
     $this bs:atShop ?shop ; bs:ofWork ?work ; bs:copies ?n .
     ?claim rdf:reifies <<( ?shop bs:stocks ?work )>> ; bs:copies ?value .
     FILTER ( ?value != ?n ) }
""",
    learn=[
        "When the same fact is modelled two ways, a constraint that joins them is the only thing that keeps them equal.",
        "A triple term pattern joins an annotation to the statement it annotates; the variables inside it bind like any others.",
        "Write the consistency check before the migration, run it after.",
    ],
    body="""
bt:StockAgreement
    a               sh:NodeShape ;
    sh:targetClass  bs:StockRecord ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "The annotation says {$value} copies; the record disagrees." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:atShop ?shop ; bs:ofWork ?work ; bs:copies ?n .
              ?claim rdf:reifies <<( ?shop bs:stocks ?work )>> ;
                     bs:copies ?value .
              FILTER ( ?value != ?n )
            }
        \"\"\" ;
    ] .
""",
    data=DFAULTY12, declare=True,
    expect=dict(conforms=False, violations=1, focus=["stock-inkwell--the-book-town"]),
)
specs.register("s55", "rdf12triples", "sparql")

s(
    sid="s56", module=M,
    title="A node that names its own shape",
    asks="A shop that says in the data which shape it should conform to, and a shape with no other target.",
    how="SHACL 1.2 adds sh:shape as a target that lives in the data graph: "
        "a triple n sh:shape S makes n a focus node of S. bt:NewShopShape has "
        "no target of its own. Fault F32 adds bt:shop-halfmoon sh:shape "
        "bt:NewShopShape to the data, and the shape now checks that one shop "
        "and reports its missing name. This is the opposite direction from "
        "every other target: the shapes graph normally decides what to "
        "check, and here the data volunteers. It suits records that carry "
        "their own profile, and it is the third 1.2 target this course has "
        "used, after sh:targetWhere in s33 and sh:ShapeClass in s08.",
    diagram="""
   shapes graph                         data graph
   bt:NewShopShape  a sh:NodeShape       bt:shop-halfmoon  sh:shape  bt:NewShopShape .
     (no sh:target*)                          ^ this triple is the target

   focus nodes of bt:NewShopShape = { bt:shop-halfmoon }
""",
    learn=[
        "sh:shape in the data graph is a target. It is the only target the data can set for itself.",
        "The 1.2 targets so far: sh:targetWhere (a shape), sh:ShapeClass (a class), sh:shape (the data). All run in this engine.",
        "sh:targetNode in the shapes graph and sh:shape in the data graph name the same relationship from opposite ends.",
    ],
    body="""
bt:NewShopShape
    a  sh:NodeShape ;
    sh:property [ sh:path rdfs:label ;   sh:minCount 1 ; sh:message "A new shop needs a name: {$this}." ] ;
    sh:property [ sh:path bs:locatedIn ; sh:minCount 1 ; sh:class bs:Settlement ] ;
    sh:property [ sh:path bs:founded ;   sh:minCount 1 ; sh:datatype xsd:gYear ] .
""",
    data=DFAULTY,
    expect=dict(conforms=False, violations=2, focus=["shop-halfmoon"], shapes=4),
)
specs.register("s56", "c12shape", "c12targetWhere")

s(
    sid="s57", module=M,
    title="New in 1.2 Core, and what this build does with it",
    asks="Notices stay on one line; the vocabulary's union classes are lists of classes; and the 1.2 features this engine reads but does not enforce.",
    how="Two of the SHACL 1.2 Core additions run here. sh:singleLine true "
        "rejects a string with a line break, and the notice on Verso that "
        "runs to two lines (F36) is reported. The list constraints check RDF "
        "collections: the vocabulary, which is part of the data, declares two "
        "classes as owl:unionOf lists, and sh:memberShape [ sh:class "
        "owl:Class ] with sh:minListLength 2 checks each list's members and "
        "length. Three more 1.2 features are accepted by this build without "
        "effect, and are recorded here so that nobody relies on them: "
        "sh:severity written as an annotation on a single constraint, "
        "sh:reificationRequired (s53), and sh:uniqueValuesFor. Module 12 has "
        "the full table. Where a feature is read and ignored, the report "
        "looks the same as if the feature had passed, which is the case for "
        "a canary shape (s09). One note on syntax: the editor's Turtle "
        "parser accepts an annotation inside [ ... ] only as the last "
        "item, so the annotated constraint is written on a named property "
        "shape.",
    diagram="""
   sh:singleLine true                  "Translated fiction ...\\nAsk at the counter."   ->  violation

   owl:unionOf ( bs:Bookshop bs:Publisher )
   sh:property [ sh:path owl:unionOf ; sh:memberShape [ sh:class owl:Class ] ; sh:minListLength 2 ]
        each member checked, length checked                                     ->  passes

   read but not enforced by this build:
   sh:minCount 1 {| sh:severity sh:Warning |}      the result is still a Violation
   sh:reificationRequired true                     unannotated values pass
   sh:uniqueValuesFor bs:Work                      duplicates pass
""",
    learn=[
        "sh:singleLine and the list constraints are the 1.2 Core additions this engine runs today.",
        "A feature an engine parses and ignores fails silently. Test each 1.2 feature with data that should fail before trusting it.",
        "Module 12 is the reference for what runs, what errors, and what is silent.",
    ],
    body="""
bt:NoticeShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Bookshop ;
    sh:property [
        sh:path        skos:note ;
        sh:singleLine  true ;
        sh:message     "A shop notice is one line: {$value}" ;
    ] .

bt:UnionClassShape
    a                    sh:NodeShape ;
    sh:targetSubjectsOf  owl:unionOf ;
    sh:property [
        sh:path           owl:unionOf ;
        sh:memberShape    [ sh:class owl:Class ] ;
        sh:minListLength  2 ;
        sh:message        "A union class lists at least two classes." ;
    ] .

# Read by this build, not enforced: the result is a Violation, not a Warning.
# The property shape is named rather than written as [ ... ] because the
# editor's Turtle parser wants an annotation to be the last thing inside a
# blank node's brackets; a named subject has no such restriction.
bt:AnnotatedSeverity
    a               sh:NodeShape ;
    sh:targetNode   bt:shop-halfmoon ;
    sh:property     bt:AnnotatedSeverity-label .

bt:AnnotatedSeverity-label
    a            sh:PropertyShape ;
    sh:path      rdfs:label ;
    sh:message   "Written as a Warning on the constraint; reported by this build as a Violation." ;
    sh:minCount  1 {| sh:severity sh:Warning |} .
""",
    data=DFAULTY12,
    expect=dict(conforms=False, violations=1, warnings=1, focus=["shop-verso"]),
)
specs.register("s57", "c12singleLine", "c12lists")
