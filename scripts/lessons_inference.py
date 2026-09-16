# -*- coding: utf-8 -*-
"""Module 09 -- Validating with inference (the RDFS closure)."""
from shapecat import s, Query, D11, DFAULTY, RDFS
import specs

M = "09-inference"

s(
    sid="s58", module=M,
    title="The event nobody typed",
    asks="Under RDFS inference, an event with no rdf:type is still an event, because bs:heldAt has a domain.",
    how="SHACL follows rdfs:subClassOf when it decides what a class covers, "
        "and nothing else in RDFS. The vocabulary is part of the data and "
        "says bs:heldAt has rdfs:domain bs:Event; without inference that is "
        "documentation, and the event nobody typed (F21) is invisible to "
        "sh:targetClass bs:Event -- s07 needed sh:targetSubjectsOf to reach "
        "it. With the Inference dropdown at RDFS the engine materialises the "
        "closure first: subclass, subproperty, domain and range. The event "
        "acquires rdf:type bs:Event, and bt:EventShape now has 61 focus nodes "
        "instead of 60. The probe lists them all as information so the count "
        "is visible in the headline, and the constraint finds nothing wrong "
        "with the untyped event beyond its missing type -- which the shape "
        "cannot report, because under inference the type is there.",
    diagram="""
   data:        bt:event-inkwell-2025-06-01  bs:heldAt bt:shop-inkwell .       (no rdf:type)
   vocabulary:  bs:heldAt  rdfs:domain  bs:Event .

   Inference: none    sh:targetClass bs:Event  ->  60 focus nodes
   Inference: RDFS    rdfs2: ?s bs:heldAt ?o  =>  ?s rdf:type bs:Event
                      sh:targetClass bs:Event  ->  61 focus nodes

   rules the closure applies: rdfs2, rdfs3, rdfs5, rdfs7, rdfs9, rdfs11  (domain, range, both hierarchies)
""",
    learn=[
        "Without inference, only asserted types and rdfs:subClassOf count. Domain and range are advice.",
        "The RDFS mode makes the vocabulary's domains and ranges part of the data for the run, and targets grow accordingly.",
        "A node that was invisible becomes checkable, and its missing type is no longer something a shape can see.",
    ],
    body="""
bt:EventShape
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:property [ sh:path bs:featuring ; sh:minCount 1 ] ;
    sh:property [ sh:path bs:eventDate ; sh:minCount 1 ; sh:maxCount 1 ] .

# Lists every focus node, so the headline shows how many there are.
bt:EventProbe
    a               sh:NodeShape ;
    sh:targetClass  bs:Event ;
    sh:sparql [
        sh:prefixes  bt:prefixes ;
        sh:severity  sh:Info ;
        sh:message   "{$this} is a focus node of the event shape." ;
        sh:select    "SELECT $this WHERE { }" ;
    ] .
""",
    data=DFAULTY, inference=RDFS, declare=True,
    expect=dict(infos=61, focus=["event-inkwell-2025-06-01"]),
)
specs.register("s58", "shaclRdfs", "targetClass")

s(
    sid="s59", module=M,
    title="The inference that hides an error",
    asks="The same class constraints as s12, under RDFS: two of the errors disappear and two new ones appear.",
    how="rdfs:range works the other way round from what a validator wants. "
        "bs:basedIn has range bs:Settlement, so under RDFS inference the "
        "author based in Wales (F16) makes Wales a settlement, and the "
        "publisher located in Wales (F19) does the same through the range of "
        "bs:locatedIn. Both sh:class bs:Settlement constraints now pass; the "
        "wrong data has typed the country to suit itself. Brecon, placed "
        "directly inside Wales (F26), still fails, because the range of "
        "bs:within is bs:Place and the constraint asks for a council area. "
        "Wales, now a settlement, fails that same constraint, because it "
        "sits directly inside Great Britain. And bt:PlaceKind from s26 -- a "
        "place is exactly one kind -- reports Wales again, a country and, "
        "since the inference, a settlement too. The SPARQL course's q143 "
        "calls this the inference "
        "nobody wanted. It is the reason inference is off by default here, "
        "and the reason to validate before you reason.",
    diagram="""
   bt:author-owen-harker  bs:basedIn  bt:place-wales .
   bs:basedIn  rdfs:range  bs:Settlement .

   none    sh:class bs:Settlement on bs:basedIn      Wales is a Country     ->  violation
   RDFS    rdfs3:  ?o is a bs:Settlement             Wales is now both     ->  passes
           bt:PlaceKind (sh:xone of the four kinds)  Wales is two kinds    ->  violation

   two errors hidden, two new ones surfaced, none of the data changed
""",
    learn=[
        "Range inference types the object to fit the property. A constraint that checks the object's class is then checking the inference, not the data.",
        "Validate the asserted data first. Inference is for what the data implies, not for what it should have said.",
        "The same shapes graph gives different reports under different inference settings. The report headline says which was used.",
    ],
    body="""
bt:PersonLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:Person ;
    sh:property [ sh:path bs:basedIn ; sh:class bs:Settlement ;
                  sh:message "{$this} is based in {$value}, which is not a settlement." ] .

bt:PublisherLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:Publisher ;
    sh:property [ sh:path bs:locatedIn ; sh:class bs:Settlement ;
                  sh:message "{$this} is located in {$value}, which is not a settlement." ] .

bt:SettlementLinks
    a               sh:NodeShape ;
    sh:targetClass  bs:Settlement ;
    sh:property [ sh:path bs:within ; sh:class bs:CouncilArea ;
                  sh:message "{$this} sits directly in {$value}, which is not a council area." ] .

bt:PlaceKind
    a               sh:NodeShape ;
    sh:targetClass  bs:Place ;
    sh:xone (
        [ sh:class bs:Country ]
        [ sh:class bs:Region ]
        [ sh:class bs:CouncilArea ]
        [ sh:class bs:Settlement ]
        [ sh:property [ sh:path skos:notation ; sh:hasValue "GB" ] ]
    ) ;
    sh:message  "{$this} is not exactly one kind of place." .
""",
    data=DFAULTY, inference=RDFS,
    expect=dict(conforms=False, violations=3, focus=["place-brecon", "place-wales"], nofocus=["author-owen-harker", "pub-orbit"]),
)
specs.register("s59", "shaclRdfs", "class")
