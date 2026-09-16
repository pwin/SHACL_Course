# -*- coding: utf-8 -*-
"""The shapes catalogue: one place where every lesson is defined.

Each Lesson below becomes a .ttl file with a structured header, and the same
metadata drives the course document, the module READMEs and the checker.
Keeping them in one object is what stops the explanation and the shapes
drifting apart.

    python scripts/build_shapes.py     # write shapes/**/*.ttl and the READMEs
    python scripts/check_shapes.py     # validate every lesson, compare with expectations
"""
from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

import specs

ROOT = Path(__file__).resolve().parent.parent
SHAPES = ROOT / "shapes"
DATA = ROOT / "data"

# Where the course lives, and where a learner's browser can reach the files.
# The Turtle Editor Viewer takes ?dot=<url> for the data and &shapes=<url> for
# a shapes graph, so one link can carry a whole lesson.
REPO = "https://github.com/pwin/SHACL_Course"
SPARQL_REPO = "https://github.com/pwin/SPARQL_Course"
RAW_BASE = "https://raw.githubusercontent.com/pwin/SHACL_Course/main/"
EDITOR_BASE = "https://semantechs.co.uk/turtle-editor-viewer/"

# The data files a lesson can ask for. The clean ones are byte-identical to
# the SPARQL course's; the faulty ones add data/faults.ttl on top.
D11 = "bookshop-trail-1.1.ttl"
D12 = "bookshop-trail-1.2.ttl"
DFAULTY = "bookshop-trail-faulty.ttl"
DFAULTY12 = "bookshop-trail-faulty-1.2.ttl"
DSHOPS = "04-bookshops.ttl"
DPLACES = "03-places.ttl"
DPEOPLE = "05-people.ttl"
DBOOKS = "06-books.ttl"
DEVENTS = "07-events.ttl"
DGENRES = "02-genres.ttl"

# Inference modes the engine offers. `none` is SHACL as specified.
NONE = "none"
RDFS = "rdfs"
RULES = "rules"
RULES_ITERATED = "rules-iterated"

# Every prefix the course knows about. A lesson declares only the ones its
# shapes graph actually uses.
KNOWN_PREFIXES = [
    ("bt",     "https://example.org/bookshop-trail/"),
    ("bs",     "https://example.org/bookshop-trail/schema#"),
    ("sh",     "http://www.w3.org/ns/shacl#"),
    ("rdf",    "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs",   "http://www.w3.org/2000/01/rdf-schema#"),
    ("owl",    "http://www.w3.org/2002/07/owl#"),
    ("xsd",    "http://www.w3.org/2001/XMLSchema#"),
    ("skos",   "http://www.w3.org/2004/02/skos/core#"),
    ("dct",    "http://purl.org/dc/terms/"),
    ("geo",    "http://www.opengis.net/ont/geosparql#"),
    ("wgs84",  "http://www.w3.org/2003/01/geo/wgs84_pos#"),
    ("prov",   "http://www.w3.org/ns/prov#"),
    ("schema", "https://schema.org/"),
]
PREFIX_URI = dict(KNOWN_PREFIXES)

# Angle-bracket IRIs, quoted strings and comments can all contain a colon, so
# they are removed before looking for prefixed names. SPARQL text inside a
# sh:select string relies on sh:declare, not on @prefix, which is also why it
# is stripped here.
_IRI = re.compile(r"<[^>\s]*>")
_STR = re.compile(r"\"\"\".*?\"\"\"|\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'", re.S)
_COMMENT = re.compile("#[^" + chr(10) + "]*")
_PNAME = re.compile(r"(?<![A-Za-z0-9_-])([A-Za-z][A-Za-z0-9._-]*):")


def prefixes_used(text: str) -> set:
    """Which known prefixes a Turtle body actually mentions."""
    stripped = _COMMENT.sub(" ", _STR.sub(" ", _IRI.sub(" ", text)))
    return {m.group(1) for m in _PNAME.finditer(stripped)} & set(PREFIX_URI)


def prologue_for(names) -> str:
    """An @prefix block in the canonical order, aligned."""
    names = set(names)
    rows = [(p, u) for p, u in KNOWN_PREFIXES if p in names]
    if not rows:
        return ""
    width = max(len(p) for p, _ in rows) + 1
    return chr(10).join(f"@prefix {(p + ':').ljust(width)} <{u}> ." for p, u in rows)


# A prefix declaration block for SPARQL text inside shapes. A lesson that uses
# sh:prefixes bt:prefixes includes this by setting `declare=True`; the block
# is then written into its file so the file stands on its own.
DECLARE = """\
# Prefixes for the SPARQL inside this file. @prefix lines are Turtle syntax
# and do not reach the query engine; sh:declare does.
bt:prefixes
    a  owl:Ontology ;
    sh:declare [ sh:prefix "bt" ;   sh:namespace "https://example.org/bookshop-trail/"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "bs" ;   sh:namespace "https://example.org/bookshop-trail/schema#"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "rdf" ;  sh:namespace "http://www.w3.org/1999/02/22-rdf-syntax-ns#"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "rdfs" ; sh:namespace "http://www.w3.org/2000/01/rdf-schema#"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "xsd" ;  sh:namespace "http://www.w3.org/2001/XMLSchema#"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "skos" ; sh:namespace "http://www.w3.org/2004/02/skos/core#"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "dct" ;  sh:namespace "http://purl.org/dc/terms/"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "geo" ;  sh:namespace "http://www.opengis.net/ont/geosparql#"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "schema" ; sh:namespace "https://schema.org/"^^xsd:anyURI ] ;
    sh:declare [ sh:prefix "sh" ;   sh:namespace "http://www.w3.org/ns/shacl#"^^xsd:anyURI ] .
"""


@dataclass
class Query:
    """A companion SPARQL query: something to run on the data or on the
    report after validating, in the editor's SPARQL panel."""
    title: str
    text: str
    on: str = "report"          # "report" or "data"


@dataclass
class Lesson:
    sid: str                    # "s07"
    module: str                 # folder name, e.g. "01-first-shapes"
    title: str
    asks: str                   # what it checks, in one sentence
    how: str                    # the mechanism, a short paragraph
    diagram: str                # an ASCII diagram of the mechanism
    learn: list[str]            # takeaways
    body: str                   # the shapes graph, without the prefixes
    data: str = D11
    inference: str = NONE
    notes: str = ""             # engine caveats, gotchas
    tryit: str = ""             # edits to make in the editor, and what changes
    declare: bool = False       # include the sh:declare block
    extra_prefixes: tuple = ()
    # What the checker must find. Counts are per severity; `focus` is a list
    # of local names that must appear among the focus nodes; `nofocus` must
    # not. A lesson with no expectation still has to run without error.
    expect: dict = field(default_factory=dict)
    queries: list = field(default_factory=list)
    # Where this lesson sits inside its module. Ids are permanent, so a lesson
    # added later cannot take the number its position deserves; this
    # overrides the reading order without touching the id.
    place: float = 0.0
    report: str = ""            # measured summary, filled in by check_shapes.py
    order: int = 0

    @property
    def sort_key(self) -> float:
        return self.place or float(self.sid[1:])

    @property
    def filename(self) -> str:
        slug = self.title.lower()
        for ch in " ,'()/?*:\"<>|!$":
            slug = slug.replace(ch, "-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return f"{self.sid}-{slug.strip('-')}.ttl"

    @property
    def path(self) -> Path:
        return SHAPES / self.module / self.filename

    @property
    def prologue(self) -> str:
        names = prefixes_used(self.body) | set(self.extra_prefixes) | {"sh"}
        if self.declare:
            names |= prefixes_used(DECLARE)
        return prologue_for(names)

    @property
    def data_url(self) -> str:
        return RAW_BASE + "data/" + self.data

    @property
    def shapes_url(self) -> str:
        return RAW_BASE + "shapes/" + self.module + "/" + self.filename

    @property
    def editor_url(self) -> str:
        """A link that opens the editor with the data in the first tab, the
        shapes in a second tab already selected, and the inference mode set."""
        url = (EDITOR_BASE + "?dot=" + quote(self.data_url, safe="")
               + "&shapes=" + quote(self.shapes_url, safe=""))
        if self.inference != NONE:
            url += "&inference=" + self.inference
        return url

    @property
    def shapes_text(self) -> str:
        """The shapes graph as a learner should paste it: prefixes, the
        declaration block if needed, then the shapes."""
        parts = [self.prologue, ""]
        if self.declare:
            parts += [DECLARE.rstrip(), ""]
        parts.append(self.body.strip())
        parts.append("")
        return chr(10).join(parts)

    @property
    def copy_text(self) -> str:
        nl = chr(10)
        head = [
            "# " + self.sid.upper() + "  " + self.title,
            "# " + self.asks,
            "# Data: " + self.data + ("" if self.inference == NONE else f"   Inference: {self.inference}"),
            "# The Bookshop Trail, SHACL -- " + REPO,
        ]
        return nl.join(head) + nl * 2 + self.shapes_text

    def text(self) -> str:
        """The .ttl file: a header a learner can read, then the shapes."""
        rule = "# " + "=" * 74
        out = [rule, f"#  {self.sid.upper()}  {self.title}", rule, "#"]

        def block(label, content, bullet=False):
            out.append(f"#  {label}")
            if bullet:
                for item in content:
                    wrapped = textwrap.wrap(item, 66)
                    out.append(f"#    - {wrapped[0]}")
                    for cont in wrapped[1:]:
                        out.append(f"#      {cont}")
            else:
                for para in content.split(chr(10) + chr(10)):
                    for line in textwrap.wrap(" ".join(para.split()), 70):
                        out.append(f"#    {line}")
                    out.append("#")
                if not bullet:
                    out.pop()
            out.append("#")

        block("CHECKS", self.asks)
        block("HOW IT WORKS", self.how)
        out.append("#  DIAGRAM")
        for line in self.diagram.strip(chr(10)).splitlines():
            out.append(f"#    {line}".rstrip())
        out.append("#")
        block("WHAT TO TAKE AWAY", self.learn, bullet=True)
        if self.notes:
            block("NOTE", self.notes)
        if self.tryit:
            block("TRY IT", self.tryit)
        out.append(f"#  DATA      {self.data}")
        if self.inference != NONE:
            out.append(f"#  INFERENCE {self.inference}   (the Inference dropdown in the editor)")
        out.append(f"#  LOAD IT   {self.editor_url}")
        for i, (label, url) in enumerate(specs.for_lesson(self.sid, self.module, limit=2)):
            out.append(f"#  {'SPEC     ' if i == 0 else '         '} {label}")
            out.append(f"#            {url}")
        if self.report:
            out.append(f"#  REPORTS   {self.report}")
        out.append(rule)
        out.append("")
        out.append(self.shapes_text)
        if self.queries:
            out.append("")
            out.append("# " + "-" * 72)
            out.append("#  AFTERWARDS.  Queries to run in the SPARQL panel: on the report")
            out.append("#  (Report as tab, then query that tab) or on the data.")
            out.append("# " + "-" * 72)
            for q in self.queries:
                out.append("#")
                out.append(f"#  -- {q.title}  (on the {q.on})")
                for line in q.text.strip().splitlines():
                    out.append(("#  " + line).rstrip())
            out.append("")
        return chr(10).join(out)


CATALOGUE: list[Lesson] = []


def s(**kwargs) -> Lesson:
    item = Lesson(**kwargs)
    item.order = len(CATALOGUE)
    CATALOGUE.append(item)
    return item


MODULE_INFO = {
    "01-first-shapes": (
        "First shapes",
        "Everything here runs in the browser: the data in one tab, the shapes "
        "in another, then Validate. A shape has two halves. The target says "
        "which nodes to look at; the constraints say what must be true of "
        "them. The report lists each place the data falls short. This module "
        "makes that structure familiar, and teaches you to read one result "
        "in full before you write anything complicated.",
    ),
    "02-value-constraints": (
        "What a value may be",
        "The constraint components that look at one value at a time: its "
        "datatype and node kind, its class, its numeric range, its length and "
        "pattern, its language tag, and how it compares with another property "
        "of the same node. The difference between a value and its lexical "
        "form matters here, and an xsd:gYear causes the same trouble it "
        "causes in SPARQL.",
    ),
    "03-property-paths": (
        "Property paths in shapes",
        "sh:path is not always a single predicate. A property shape can follow "
        "a sequence of steps, walk a link backwards, take either of two "
        "routes, or continue for any number of hops. These are the paths "
        "SPARQL has, written as RDF. One lesson repeats the SPARQL course's "
        "point about fixed-length chains, because the same mistake is just as "
        "easy to make in a shape.",
    ),
    "04-shapes-and-logic": (
        "Shapes inside shapes, and logic",
        "A constraint can hand a value to another shape. sh:node, sh:not, "
        "sh:and, sh:or and sh:xone are all built on that idea, as are "
        "qualified value shapes ('at least one of the values is a ...'), "
        "closed shapes that reject any property not listed, and shapes that "
        "refer to themselves.",
    ),
    "05-sparql-constraints": (
        "Targets and constraints in SPARQL",
        "Some conditions cannot be written with the Core components: a join "
        "between two nodes, an arithmetic comparison, a path that must not "
        "lead back to its start. SHACL-SPARQL lets a SELECT query decide, "
        "with $this bound to the node under test. The module also writes "
        "targets in SPARQL, sets out what pre-binding forbids, and queries "
        "the report as the RDF graph it is.",
    ),
    "06-constraint-components": (
        "Your own constraint components",
        "sh:minCount is a parameter and a validator, and a shapes graph can "
        "declare new components on the same terms. A constraint component "
        "gives a SPARQL check a name and parameters, so the shapes that use "
        "it read like Core and the query is written once. Appendix D of the "
        "specification defines every Core component this way.",
    ),
    "07-rules": (
        "SHACL rules",
        "The Advanced Features note lets a shape infer triples as well as "
        "check them. A triple rule builds one triple from node expressions; a "
        "SPARQL rule runs a CONSTRUCT. Rules run before validation, so a "
        "result can depend on an inferred triple. The editor's Inference "
        "dropdown switches them on. A validator's only output is its report, "
        "so each lesson here uses a shape to make its inferences visible.",
    ),
    "08-shacl-1-2": (
        "SHACL 1.2 and RDF 1.2",
        "The RDF 1.2 edition of the data has statements about statements: a "
        "shop with two founding dates, each claimed by a source. SHACL 1.2 "
        "can validate the claims themselves, target nodes by a shape rather "
        "than by a class, and declare a class that is its own shape. The "
        "module uses what the engine in the editor runs today and lists the "
        "parts of the 1.2 drafts it does not.",
    ),
    "09-inference": (
        "Validating with inference",
        "SHACL follows rdfs:subClassOf when it works out what a class covers, "
        "and nothing else. The editor can materialise the RDFS closure first "
        "(subclass, subproperty, domain and range), which changes the report "
        "in both directions: it finds nodes nobody typed, and it makes some "
        "errors disappear. Two lessons, and a pointer to the SPARQL course's "
        "module on reasoning.",
    ),
    "10-debugging": (
        "Debugging shapes",
        "'Conforms' is what a validator says when the data is right, and also "
        "what it says when it checked nothing. This module collects the ways "
        "a shape goes wrong without an error: a target that matches nothing, "
        "a path in the wrong direction, a datatype or language tag that stops "
        "a match, a severity that does not inherit. Each comes with the check "
        "that catches it.",
    ),
    "11-putting-it-together": (
        "Putting it together",
        "A complete shapes graph for the Bookshop Trail, run on the clean data "
        "and then on the faulty edition as its answer key; shapes used as "
        "questions rather than rules; a report turned into a list of issues "
        "in the dataset's own vocabulary; and a rule set that enriches the "
        "graph before checking it.",
    ),
    "12-beyond-this-engine": (
        "Beyond this engine",
        "Reference rather than lesson. Validators differ in what they "
        "implement, and the SHACL 1.2 drafts are still changing. This module "
        "records what the engine in the editor does with each feature it "
        "does not implement -- an error for some, no output for others -- and "
        "where pySHACL, TopBraid and Jena differ from it.",
    ),
}
