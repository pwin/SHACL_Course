# -*- coding: utf-8 -*-
"""The deliberate mistakes.

The Bookshop Trail conforms to every shape in the SPARQL course, and a
validation course needs something to find. This script writes
data/faults.ttl -- a numbered overlay of wrong triples, each commented with
the lesson it exists for -- and the two combined files that lessons point at:

    data/bookshop-trail-faulty.ttl       bookshop-trail-1.1.ttl + faults.ttl
    data/bookshop-trail-faulty-1.2.ttl   bookshop-trail-1.2.ttl + faults.ttl + faults-1.2.ttl

The clean files are never touched. Nothing here changes the geography: the
new places are real Welsh towns with their real coordinates, and the faults
are in the other columns.

    python scripts/build_faults.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PREFIXES = """\
@prefix bt:    <https://example.org/bookshop-trail/> .
@prefix bs:    <https://example.org/bookshop-trail/schema#> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix dct:   <http://purl.org/dc/terms/> .
@prefix geo:   <http://www.opengis.net/ont/geosparql#> .
@prefix wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix prov:  <http://www.w3.org/ns/prov#> .
@prefix sh:    <http://www.w3.org/ns/shacl#> .
"""

FAULTS = PREFIXES + """
############################################################################
#  FAULTS  -- deliberate mistakes, layered on the Bookshop Trail
############################################################################
#  This file is never loaded on its own. It is appended to the clean data
#  to make bookshop-trail-faulty.ttl, which is what a lesson points at when
#  it needs something to find. Every fault is numbered, and the comment says
#  which lesson catches it. Together the numbers are the answer key for
#  module 11.
#
#  Where a fault needs a *missing* triple -- a shop with no name -- it lives
#  on a new resource, because an overlay can only add. Where it needs a
#  wrong or extra triple, it is added to a resource the clean data already
#  has, so The Inkwell ends up in two towns.
############################################################################


# ------------------------------------------------------------------------
#  Bookshops
# ------------------------------------------------------------------------

# F01  A shop with no rdfs:label and no bs:founded        -> s02, s04 (sh:minCount)
# F02  Its bs:staffCount is zero                           -> s13 (sh:minInclusive)
# F03  It is also typed as a publisher                     -> s25 (sh:not)
bt:shop-halfmoon
    a                   bs:Bookshop, bs:Publisher, geo:Feature ;
    bs:locatedIn        bt:place-hay-on-wye ;
    bs:staffCount       "0"^^xsd:integer ;
    bs:floorArea        "85.0"^^xsd:decimal ;
    bs:hasCafe          false ;
    bs:sellsSecondHand  true ;
    bs:specialises      bt:genre-poetry ;
    wgs84:lat           "52.0743"^^xsd:decimal ;
    wgs84:long          "-3.1261"^^xsd:decimal .

# F04  The Inkwell is placed in a second town              -> s04 (sh:maxCount)
bt:shop-inkwell  bs:locatedIn  bt:place-hay-on-wye .

# F05  A predicate with a typo. bs:foundedIn is not in the vocabulary,
#      and nothing but a closed shape will ever notice.    -> s27 (sh:closed)
bt:shop-inkwell  bs:foundedIn  "1979"^^xsd:gYear .

# F06  A shop where nearly every value is the wrong kind of thing
#        label with no language tag                        -> s11 (sh:datatype rdf:langString)
#        bs:locatedIn a string, not a place                -> s11 (sh:nodeKind), s12 (sh:class)
#        bs:founded an integer, not a gYear                -> s10 (sh:datatype)
#        bs:staffCount a decimal                           -> s10
#        bs:hasCafe a string                               -> s10
#        bs:floorArea negative                             -> s13 (sh:minExclusive)
#        a website with no scheme, and two of them         -> s15 (sh:pattern), s04 (sh:maxCount)
#        bs:specialises a place, not a genre               -> s12 (sh:class)
bt:shop-foxed-page
    a                   bs:Bookshop, geo:Feature ;
    rdfs:label          "The Foxed Page" ;
    bs:locatedIn        "Kendal" ;
    bs:founded          "1985"^^xsd:integer ;
    bs:floorArea        "-20.0"^^xsd:decimal ;
    bs:staffCount       "3.5"^^xsd:decimal ;
    bs:hasCafe          "yes" ;
    bs:sellsSecondHand  true ;
    bs:website          "www.foxed-page.example" ;
    bs:website          "https://foxed-page.example/"^^xsd:anyURI ;
    bs:specialises      bt:place-kendal ;
    wgs84:lat           "54.3280"^^xsd:decimal ;
    wgs84:long          "-2.7463"^^xsd:decimal .

# F07  A shop that is described but never typed. sh:targetClass cannot see
#      it; sh:class fails on anything that points at it.   -> s12 (through its stock record)
bt:shop-ghost
    rdfs:label     "The Ghost Shop"@en ;
    bs:locatedIn   bt:place-durham ;
    bs:founded     "2001"^^xsd:gYear ;
    bs:staffCount  "2"^^xsd:integer .


# ------------------------------------------------------------------------
#  Works
# ------------------------------------------------------------------------

# F08  An ISBN written with hyphens                        -> s15 (sh:pattern)
# F09  Zero pages, and a negative price                    -> s13
bt:book-the-margin-notes
    a                    bs:Work ;
    rdfs:label           "The Margin Notes"@en ;
    dct:title            "The Margin Notes"@en ;
    bs:author            bt:author-dilys-tremain ;
    bs:publishedBy       bt:pub-pica ;
    bs:publicationYear   "2021"^^xsd:gYear ;
    bs:genre             bt:genre-poetry ;
    bs:pages             "0"^^xsd:integer ;
    bs:rrp               "-4.99"^^xsd:decimal ;
    bs:isbn              "978-0-14-118776-1" ;
    bs:originalLanguage  "en" .

# F10  An ISBN of the right shape with the wrong check digit.
#      Only arithmetic finds this one.                     -> s39 (a constraint component)
# F11  Published in 1990 by an author born in 1995         -> s31 (a SPARQL join)
bt:book-precocious
    a                    bs:Work ;
    rdfs:label           "Precocious"@en ;
    dct:title            "Precocious"@en ;
    bs:author            bt:author-dilys-tremain ;
    bs:publishedBy       bt:pub-pica ;
    bs:publicationYear   "1990"^^xsd:gYear ;
    bs:genre             bt:genre-poetry ;
    bs:pages             "96"^^xsd:integer ;
    bs:rrp               "8.99"^^xsd:decimal ;
    bs:isbn              "9780141187762" ;
    bs:originalLanguage  "en" .

# F12  A work from 1998 with no ISBN. Before 1970 that is allowed;
#      after it, it is a gap.                              -> s26 (sh:or)
# F13  Published by bt:pub-orbit, which is not well formed -> s24 (sh:node)
#      Its label and its title also disagree               -> s18 (sh:equals)
bt:book-unnumbered
    a                    bs:Work ;
    rdfs:label           "Unnumbered"@en ;
    dct:title            "Un-numbered"@en ;
    bs:author            bt:author-rab-fingal ;
    bs:publishedBy       bt:pub-orbit ;
    bs:publicationYear   "1998"^^xsd:gYear ;
    bs:genre             bt:genre-stray ;
    bs:pages             "210"^^xsd:integer ;
    bs:rrp               "9.99"^^xsd:decimal ;
    bs:originalLanguage  "en" .

# F14  A translation published six years before the original -> s18 (sh:lessThanOrEquals)
bt:book-the-dark-sea-fr
    a                    bs:Translation, bs:Work ;
    rdfs:label           "La mer sombre"@fr ;
    dct:title            "La mer sombre"@fr ;
    bs:translationOf     bt:book-the-dark-sea ;
    bs:author            bt:author-elin-morgan ;
    bs:translatedBy      bt:author-noor-haddad ;
    bs:publishedBy       bt:pub-thornfield ;
    bs:publicationYear   "2010"^^xsd:gYear ;
    bs:genre             bt:genre-translated-fiction ;
    bs:pages             "170"^^xsd:integer ;
    bs:rrp               "19.50"^^xsd:decimal ;
    bs:isbn              "9780141187778" ;
    bs:originalLanguage  "cy" .


# ------------------------------------------------------------------------
#  People and publishers
# ------------------------------------------------------------------------

# F15  Died before being born                               -> s14 (the gYear comparison)
# F16  Based in a country rather than a settlement          -> s12 (sh:class)
# F17  Writes in a language the dataset does not use        -> s17 (sh:in)
# F18  Influenced by himself                                -> s30 (a SPARQL constraint)
bt:author-owen-harker
    a                bs:Author, bs:Person ;
    rdfs:label       "Owen Harker"@en ;
    bs:born          "1970"^^xsd:gYear ;
    bs:died          "1965"^^xsd:gYear ;
    bs:basedIn       bt:place-wales ;
    bs:writesIn      "fr" ;
    bs:influencedBy  bt:author-owen-harker .

# F19  A publisher located in a country, and an imprint of itself
#                                                          -> s24 (sh:node), s30
bt:pub-orbit
    a             bs:Publisher ;
    rdfs:label    "Orbit and Orrery"@en ;
    bs:founded    "2011"^^xsd:gYear ;
    bs:locatedIn  bt:place-wales ;
    bs:imprintOf  bt:pub-orbit .


# ------------------------------------------------------------------------
#  Events
# ------------------------------------------------------------------------

# F20  An event with nearly everything wrong
#        held at a publisher                               -> s07 (sh:targetObjectsOf), s12
#        a kind of event the list does not have            -> s17 (sh:in)
#        a date with a thirteenth month                    -> s10 (an ill-formed literal)
#        negative attendance                               -> s13
#        a ticket price that is a word                     -> s10
#        nobody featuring                                  -> s07 (sh:minCount)
bt:event-foxed-page-2025-05-01
    a               bs:Event ;
    rdfs:label      "Recital at the Foxed Page"@en ;
    bs:heldAt       bt:pub-pica ;
    bs:eventKind    "Recital" ;
    bs:eventDate    "2025-13-01"^^xsd:date ;
    bs:attendance   "-5"^^xsd:integer ;
    bs:ticketPrice  "free" .

# F21  An event nobody typed. Invisible to sh:targetClass; found by
#      sh:targetSubjectsOf, and by RDFS inference on the domain of
#      bs:heldAt.                                          -> s07, s58
bt:event-inkwell-2025-06-01
    rdfs:label      "An evening nobody catalogued"@en ;
    bs:heldAt       bt:shop-inkwell ;
    bs:eventKind    "Reading" ;
    bs:eventDate    "2025-06-01"^^xsd:date ;
    bs:featuring    bt:author-rab-fingal ;
    bs:attendance   "30"^^xsd:integer ;
    bs:ticketPrice  "0.00"^^xsd:decimal .


# ------------------------------------------------------------------------
#  The trail and the stock
# ------------------------------------------------------------------------

# F22  A segment from The Inkwell to The Inkwell, of no length
#                                                          -> s18 (sh:disjoint), s13 (sh:minExclusive)
bt:seg-inkwell-inkwell
    a               bs:TrailSegment, geo:Feature ;
    rdfs:label      "The Inkwell to The Inkwell"@en ;
    bs:segmentFrom  bt:shop-inkwell ;
    bs:segmentTo    bt:shop-inkwell ;
    bs:distanceKm   "0.0"^^xsd:decimal ;
    bs:waymarked    true .

# F23  Negative copies, at three times the recommended price
#                                                          -> s13, s31 (a SPARQL join)
bt:stock-foxed-page--the-book-town
    a              bs:StockRecord ;
    bs:atShop      bt:shop-foxed-page ;
    bs:ofWork      bt:book-the-book-town ;
    bs:copies      "-2"^^xsd:integer ;
    bs:shelfPrice  "68.07"^^xsd:decimal .

# F24  A record at the shop nobody typed (F07)              -> s12 (sh:class versus sh:node)
bt:stock-ghost--the-book-town
    a              bs:StockRecord ;
    bs:atShop      bt:shop-ghost ;
    bs:ofWork      bt:book-the-book-town ;
    bs:copies      "1"^^xsd:integer ;
    bs:shelfPrice  "22.69"^^xsd:decimal .


# ------------------------------------------------------------------------
#  Places
# ------------------------------------------------------------------------

# F25  Newtown, Powys -- a real town, with faults in every other column
#        two English labels                                -> s16 (sh:uniqueLang)
#        a population that is a decimal                    -> s10
#        a latitude north of the pole                      -> s13 (sh:maxInclusive)
#        no geometry                                       -> s64 (sh:minCount)
#        a second book town in Powys                       -> s28 (sh:qualifiedMaxCount, reported on Powys), s33
bt:place-newtown
    a              bs:Settlement, bs:Place, geo:Feature ;
    rdfs:label     "Newtown"@en ;
    rdfs:label     "New Town"@en ;
    rdfs:label     "Y Drenewydd"@cy ;
    bs:within      bt:place-powys ;
    bs:population  "11000.0"^^xsd:decimal ;
    bs:isBookTown  true ;
    wgs84:lat      "152.5132"^^xsd:decimal ;
    wgs84:long     "-3.3141"^^xsd:decimal .

# F26  Brecon, placed directly inside Wales with no council area between
#                                                          -> s12 (sh:class)
bt:place-brecon
    a              bs:Settlement, bs:Place, geo:Feature ;
    rdfs:label     "Brecon"@en ;
    rdfs:label     "Aberhonddu"@cy ;
    bs:within      bt:place-wales ;
    bs:population  "8000"^^xsd:integer ;
    bs:isBookTown  false ;
    wgs84:lat      "51.9470"^^xsd:decimal ;
    wgs84:long     "-3.3900"^^xsd:decimal ;
    geo:hasGeometry         bt:geom-brecon ;
    geo:hasDefaultGeometry  bt:geom-brecon .

bt:geom-brecon
    a          <http://www.opengis.net/ont/sf#Point>, geo:Geometry ;
    geo:asWKT  "<http://www.opengis.net/def/crs/OGC/1.3/CRS84> POINT(-3.3900 51.9470)"^^geo:wktLiteral .

# F27  Two council areas each inside the other. Nothing in Core can say
#      'containment is not circular'.                       -> s30 (a SPARQL path), s22 (sh:hasValue)
bt:place-loop-a
    a           bs:CouncilArea, bs:Place ;
    rdfs:label  "Loop A"@en ;
    bs:within   bt:place-loop-b .

bt:place-loop-b
    a           bs:CouncilArea, bs:Place ;
    rdfs:label  "Loop B"@en ;
    bs:within   bt:place-loop-a .

# F28  A French label on Kendal                             -> s16 (sh:languageIn)
bt:place-kendal  rdfs:label  "Kendal"@fr .


# ------------------------------------------------------------------------
#  Genres and sources
# ------------------------------------------------------------------------

# F29  A concept in no scheme, under no broader concept     -> s22 (sh:hasValue with a path)
bt:genre-stray
    a               skos:Concept ;
    skos:prefLabel  "Stray"@en ;
    rdfs:label      "Stray"@en .

# F30  Two concepts, each broader than the other            -> s22, s30
bt:genre-loop-a
    a               skos:Concept ;
    skos:inScheme   bt:genre-scheme ;
    skos:prefLabel  "Loop A"@en ;
    rdfs:label      "Loop A"@en ;
    skos:broader    bt:genre-loop-b .

bt:genre-loop-b
    a               skos:Concept ;
    skos:inScheme   bt:genre-scheme ;
    skos:prefLabel  "Loop B"@en ;
    rdfs:label      "Loop B"@en ;
    skos:broader    bt:genre-loop-a .

# F31  A source of a kind the list does not have, more than fully confident
#                                                          -> s17 (sh:in), s13 (sh:maxInclusive)
bt:source-rumour
    a              bs:Source, prov:Entity ;
    rdfs:label     "Heard in the pub"@en ;
    bs:sourceKind  "hearsay" ;
    bs:confidence  "1.4"^^xsd:decimal .


# ------------------------------------------------------------------------
#  For SHACL 1.2: a node that names its own shape
# ------------------------------------------------------------------------

# F32  sh:shape in the data graph is a target in SHACL 1.2  -> s56
bt:shop-halfmoon  sh:shape  bt:NewShopShape .
"""

FAULTS_12 = PREFIXES + """
############################################################################
#  FAULTS, RDF 1.2 EDITION -- mistakes in the statements about statements
############################################################################
#  Appended after faults.ttl to make bookshop-trail-faulty-1.2.ttl. These
#  need the RDF 1.2 annotation syntax, so they cannot live in faults.ttl.
############################################################################

# F33  A founding claim with no source and a confidence above one
#                                                          -> s53 (sh:reifierShape)
bt:shop-marginalia  bs:founded  "1960"^^xsd:gYear
    {| bs:confidence  "1.4"^^xsd:decimal |} .

# F34  An attendance claimed by a string rather than a source
#                                                          -> s54
bt:event-ex-libris-2025-01-18  bs:attendance  "999"^^xsd:integer
    {| bs:claimedBy  "the manager" |} .

# F35  A stock annotation that disagrees with its RDF 1.1 record
#      (the record says 12 copies of The Book Town at The Inkwell)
#                                                          -> s55
bt:shop-inkwell  bs:stocks  bt:book-the-book-town
    {| bs:copies  "13"^^xsd:integer |} .

# F36  A shop notice that runs to two lines                -> s57 (sh:singleLine)
bt:shop-verso  skos:note  "Translated fiction from twenty languages.\\nAsk at the counter."@en .
"""


def banner(title: str, lines: list[str]) -> str:
    rule = "#" * 76
    body = "".join(f"#  {l}\n" for l in lines)
    return f"\n\n{rule}\n#  {title}\n{rule}\n{body}{rule}\n\n"


def main() -> None:
    (DATA / "faults.ttl").write_text(FAULTS, encoding="utf-8", newline="\n")
    (DATA / "faults-1.2.ttl").write_text(FAULTS_12, encoding="utf-8", newline="\n")

    clean11 = (DATA / "bookshop-trail-1.1.ttl").read_text(encoding="utf-8")
    faulty = (clean11
              + banner("==== faults.ttl ====", [
                  "The clean dataset above, then data/faults.ttl. Each fault is",
                  "numbered and says which lesson catches it."])
              + FAULTS)
    (DATA / "bookshop-trail-faulty.ttl").write_text(faulty, encoding="utf-8", newline="\n")

    clean12 = (DATA / "bookshop-trail-1.2.ttl").read_text(encoding="utf-8")
    faulty12 = (clean12
                + banner("==== faults.ttl ====", ["The RDF 1.2 dataset above, then data/faults.ttl."])
                + FAULTS
                + banner("==== faults-1.2.ttl ====", ["Then the faults that need annotation syntax."])
                + FAULTS_12)
    (DATA / "bookshop-trail-faulty-1.2.ttl").write_text(faulty12, encoding="utf-8", newline="\n")

    n = sum(1 for line in (FAULTS + FAULTS_12).splitlines() if line.startswith("# F"))
    print(f"wrote data/faults.ttl and data/faults-1.2.ttl ({n} numbered faults), "
          f"bookshop-trail-faulty.ttl, bookshop-trail-faulty-1.2.ttl")


if __name__ == "__main__":
    main()
