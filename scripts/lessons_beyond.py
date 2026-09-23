# -*- coding: utf-8 -*-
"""Module 12 -- Beyond this engine (reference)."""
from shapecat import s, Query, D11, DFAULTY
import specs

M = "12-beyond-this-engine"

s(
    sid="s69", module=M,
    title="A function you cannot call",
    asks="A SHACL function that turns a gYear into an integer -- declared, refused by this engine, and replaced by the same expression inline.",
    how="SHACL-AF lets a shapes graph declare a sh:SPARQLFunction: a name, "
        "parameters, and a SELECT that computes ?result, callable from any "
        "SPARQL in the file. bt:yearOf would make the STR cast of s14 a "
        "one-word call. This engine does not implement SHACL functions, and "
        "says so: a constraint that calls one stops the run with 'The "
        "custom function ... is not supported'. That is the right kind of "
        "failure. The calling shape here is deactivated so the file runs; "
        "take the sh:deactivated line off to see the message. "
        "bt:BornBefore1920Inline is the same constraint with the cast "
        "written out, and it lists the authors born before 1920 as "
        "information. A function is a convenience that ties the shapes to "
        "the validators that have it; the inline form runs everywhere.",
    diagram="""
   bt:yearOf  a sh:SPARQLFunction ;
       sh:parameter [ sh:path bt:year ] ;
       sh:returnType xsd:integer ;
       sh:select "SELECT (xsd:integer(STR($year)) AS ?result) WHERE {}" .

   FILTER ( bt:yearOf(?born) < 1920 )          this engine: error, "custom function ... is not supported"
   FILTER ( xsd:integer(STR(?born)) < 1920 )   every engine
""",
    learn=[
        "SHACL functions are SHACL-AF, optional, and not in this engine. The refusal is an error rather than silence.",
        "Anything a function would compute can be written inline. Do that when the shapes have to travel.",
        "pySHACL and TopBraid implement SHACL functions; Jena does not. Check before depending on one.",
    ],
    tryit="Remove sh:deactivated true from bt:BornBefore1920 and validate. The engine refuses "
          "the run and names the function.",
    body="""
bt:yearOf
    a  sh:SPARQLFunction ;
    sh:parameter   [ sh:path bt:year ] ;
    sh:returnType  xsd:integer ;
    sh:prefixes    bt:prefixes ;
    sh:select      "SELECT ( xsd:integer(STR($year)) AS ?result ) WHERE { }" .

# Calls the function. Deactivated so that this file runs on this engine.
bt:BornBefore1920
    a               sh:NodeShape ;
    sh:deactivated  true ;
    sh:targetClass  bs:Author ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} was born before 1920 (via bt:yearOf)." ;
        sh:select    "SELECT $this WHERE { $this bs:born ?born . FILTER ( bt:yearOf(?born) < 1920 ) }" ;
    ] .

# The same test, inline.
bt:BornBefore1920Inline
    a               sh:NodeShape ;
    sh:targetClass  bs:Author ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} was born in {$value}, before 1920." ;
        sh:select    "SELECT $this ?value WHERE { $this bs:born ?value . FILTER ( xsd:integer(STR(?value)) < 1920 ) }" ;
    ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, min_infos=3, violations=0),
)
specs.register("s69", "afFunctions", "afSparqlFunction")

s(
    sid="s70", module=M,
    title="Targets the engine ignores",
    asks="A SPARQL target type with a parameter, and sh:uniqueValuesFor: two features this build reads and does nothing with.",
    how="SHACL-AF's sh:SPARQLTargetType declares a reusable, parameterised "
        "target: bt:FoundedBefore takes a year and selects the shops opened "
        "before it. This engine compiles the shape, counts it, and gives it "
        "no focus nodes, so bt:OldShopShape checks nothing and the report "
        "says nothing about it. sh:uniqueValuesFor, from SHACL 1.2 Core, is "
        "the same story: read, counted, not enforced, so two works with the "
        "same ISBN would pass. Neither produces an error, and that is the "
        "hazard the whole of module 10 is about. bt:UniqueISBN is the "
        "portable form of the second: a SPARQL constraint that finds a "
        "second work with the same ISBN. The canary is the one result. The "
        "table in this module's README lists every feature by what this "
        "build does with it.",
    diagram="""
   feature                      this build        symptom
   sh:SPARQLTargetType          silent            no focus nodes, no error, shape counted
   sh:uniqueValuesFor           silent            duplicates pass
   sh:SPARQLFunction            error             "custom function ... is not supported" (s69)
   sh:resultAnnotation          silent            results appear without the annotation
   ?message in a constraint     silent            sh:message is used instead (s32)

   enforced since engine 0.3.0, and silent before it:
   sh:severity as annotation    enforced          the annotated severity is used
   sh:reificationRequired       enforced          unannotated values are reported

   canary  ->  1 row, so the run happened
""",
    learn=[
        "A feature that is read and ignored looks like conformance. Test each one with data that must fail.",
        "For a parameterised target, a sh:SPARQLTarget with the value written in, or sh:targetWhere, does the same job here.",
        "For uniqueness, a SPARQL constraint that looks for a second node with the same value runs on every engine.",
    ],
    tryit="Give two works the same ISBN in the data tab and validate. bt:UniqueISBN reports both; bt:UniqueByComponent reports neither.",
    body="""
bt:FoundedBefore
    a               sh:SPARQLTargetType ;
    rdfs:subClassOf sh:Target ;
    sh:parameter    [ sh:path bt:year ] ;
    sh:prefixes     bt:prefixes ;
    sh:select       "SELECT ?this WHERE { ?this bs:founded ?y . FILTER ( xsd:integer(STR(?y)) < $year ) }" .

# Never gets a focus node on this engine.
bt:OldShopShape
    a          sh:NodeShape ;
    sh:target  [ a bt:FoundedBefore ; bt:year 1950 ] ;
    sh:property [ sh:path bs:website ; sh:minCount 1 ; sh:severity sh:Info ;
                  sh:message "Never reported here: the target type is not implemented." ] .

# Read, not enforced.
bt:UniqueByComponent
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:property [ sh:path bs:isbn ; sh:uniqueValuesFor bs:Work ;
                  sh:message "Never reported here: sh:uniqueValuesFor is not enforced." ] .

# The portable form.
bt:UniqueISBN
    a               sh:NodeShape ;
    sh:targetClass  bs:Work ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:message   "{$this} shares its ISBN {$value} with another work." ;
        sh:select    \"\"\"
            SELECT $this ?value WHERE {
              $this bs:isbn ?value . ?other bs:isbn ?value . FILTER ( ?other != $this )
            }
        \"\"\" ;
    ] .

bt:Canary
    a              sh:NodeShape ;
    sh:targetNode  bt:shop-inkwell ;
    sh:property [ sh:path rdf:type ; sh:maxCount 0 ; sh:message "The canary: validation ran." ] .
""",
    data=D11, declare=True,
    expect=dict(conforms=False, violations=1, infos=0, focus=["shop-inkwell"]),
)
specs.register("s70", "afTargetType", "c12uniqueValuesFor")
