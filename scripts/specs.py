# -*- coding: utf-8 -*-
"""Where each lesson is defined in the standards.

One table of sections, keyed by a short name, and a map from lessons and
modules to the sections that define them. The module READMEs, the course
document and the .ttl headers all draw on this, and check_links.py fetches
every document and confirms each anchor still lands on a heading.
"""
from __future__ import annotations

SHACL = "https://www.w3.org/TR/shacl/"
AF = "https://www.w3.org/TR/shacl-af/"
CORE12 = "https://www.w3.org/TR/shacl12-core/"
SPARQL12 = "https://www.w3.org/TR/shacl12-sparql/"
NODEEXPR12 = "https://www.w3.org/TR/shacl12-node-expr/"
RULES12 = "https://www.w3.org/TR/shacl12-rules/"
SPARQL = "https://www.w3.org/TR/sparql12-query/"
RDF12 = "https://www.w3.org/TR/rdf12-concepts/"
TURTLE12 = "https://www.w3.org/TR/rdf12-turtle/"

# key -> (label, url)
SECTIONS = {
    # SHACL 1.0 Recommendation
    "shapes":          ("SHACL §2.1 Shapes", SHACL + "#shapes"),
    "constraints":     ("SHACL §2.1.1 Constraints, Parameters and Constraint Components", SHACL + "#constraints"),
    "focus":           ("SHACL §2.1.2 Focus Nodes", SHACL + "#focusNodes"),
    "targets":         ("SHACL §2.1.3 Targets", SHACL + "#targets"),
    "targetNode":      ("SHACL §2.1.3.1 sh:targetNode", SHACL + "#targetNode"),
    "targetClass":     ("SHACL §2.1.3.2 sh:targetClass", SHACL + "#targetClass"),
    "implicit":        ("SHACL §2.1.3.3 Implicit Class Targets", SHACL + "#implicit-targetClass"),
    "targetSubjectsOf":("SHACL §2.1.3.4 sh:targetSubjectsOf", SHACL + "#targetSubjectsOf"),
    "targetObjectsOf": ("SHACL §2.1.3.5 sh:targetObjectsOf", SHACL + "#targetObjectsOf"),
    "severity":        ("SHACL §2.1.4 Declaring the Severity of a Shape", SHACL + "#severity"),
    "message":         ("SHACL §2.1.5 Declaring Messages for a Shape", SHACL + "#message"),
    "deactivated":     ("SHACL §2.1.6 Deactivating a Shape", SHACL + "#deactivated"),
    "nodeShapes":      ("SHACL §2.2 Node Shapes", SHACL + "#node-shapes"),
    "propertyShapes":  ("SHACL §2.3 Property Shapes", SHACL + "#property-shapes"),
    "paths":           ("SHACL §2.3.1 SHACL Property Paths", SHACL + "#property-paths"),
    "pathSequence":    ("SHACL §2.3.1.2 Sequence Paths", SHACL + "#property-path-sequence"),
    "pathAlternative": ("SHACL §2.3.1.3 Alternative Paths", SHACL + "#property-path-alternative"),
    "pathInverse":     ("SHACL §2.3.1.4 Inverse Paths", SHACL + "#property-path-inverse"),
    "pathZeroOrMore":  ("SHACL §2.3.1.5 Zero-Or-More Paths", SHACL + "#property-path-zero-or-more"),
    "pathOneOrMore":   ("SHACL §2.3.1.6 One-Or-More Paths", SHACL + "#property-path-one-or-more"),
    "pathZeroOrOne":   ("SHACL §2.3.1.7 Zero-Or-One Paths", SHACL + "#property-path-zero-or-one"),
    "nonValidating":   ("SHACL §2.3.2 Non-Validating Property Shape Characteristics", SHACL + "#nonValidation"),
    "shapesGraph":     ("SHACL §3.1 Shapes Graph", SHACL + "#shapes-graph"),
    "dataGraph":       ("SHACL §3.2 Data Graph", SHACL + "#data-graph"),
    "validation":      ("SHACL §3.4 Validation", SHACL + "#validation-definition"),
    "failures":        ("SHACL §3.4.1 Failures", SHACL + "#failures"),
    "recursion":       ("SHACL §3.4.3 Handling of Recursive Shapes", SHACL + "#shapes-recursion"),
    "conformance":     ("SHACL §3.5 Conformance Checking", SHACL + "#conformance-definition"),
    "report":          ("SHACL §3.6 Validation Report", SHACL + "#validation-report"),
    "conforms":        ("SHACL §3.6.1.1 sh:conforms", SHACL + "#conforms"),
    "result":          ("SHACL §3.6.2 Validation Result", SHACL + "#results-validation-result"),
    "resultPath":      ("SHACL §3.6.2.2 sh:resultPath", SHACL + "#results-path"),
    "resultValue":     ("SHACL §3.6.2.3 sh:value", SHACL + "#results-value"),
    "sourceShape":     ("SHACL §3.6.2.4 sh:sourceShape", SHACL + "#results-source-shape"),
    "resultMessage":   ("SHACL §3.6.2.7 sh:resultMessage", SHACL + "#results-message"),
    "resultSeverity":  ("SHACL §3.6.2.8 sh:resultSeverity", SHACL + "#results-severity"),
    "valueNodes":      ("SHACL §3.7 Value Nodes", SHACL + "#value-nodes"),
    "class":           ("SHACL §4.1.1 sh:class", SHACL + "#ClassConstraintComponent"),
    "datatype":        ("SHACL §4.1.2 sh:datatype", SHACL + "#DatatypeConstraintComponent"),
    "nodeKind":        ("SHACL §4.1.3 sh:nodeKind", SHACL + "#NodeKindConstraintComponent"),
    "minCount":        ("SHACL §4.2.1 sh:minCount", SHACL + "#MinCountConstraintComponent"),
    "maxCount":        ("SHACL §4.2.2 sh:maxCount", SHACL + "#MaxCountConstraintComponent"),
    "range":           ("SHACL §4.3 Value Range Constraint Components", SHACL + "#core-components-range"),
    "minInclusive":    ("SHACL §4.3.2 sh:minInclusive", SHACL + "#MinInclusiveConstraintComponent"),
    "strings":         ("SHACL §4.4 String-based Constraint Components", SHACL + "#core-components-string"),
    "pattern":         ("SHACL §4.4.3 sh:pattern", SHACL + "#PatternConstraintComponent"),
    "languageIn":      ("SHACL §4.4.4 sh:languageIn", SHACL + "#LanguageInConstraintComponent"),
    "uniqueLang":      ("SHACL §4.4.5 sh:uniqueLang", SHACL + "#UniqueLangConstraintComponent"),
    "pairs":           ("SHACL §4.5 Property Pair Constraint Components", SHACL + "#core-components-property-pairs"),
    "equals":          ("SHACL §4.5.1 sh:equals", SHACL + "#EqualsConstraintComponent"),
    "disjoint":        ("SHACL §4.5.2 sh:disjoint", SHACL + "#DisjointConstraintComponent"),
    "lessThan":        ("SHACL §4.5.3 sh:lessThan", SHACL + "#LessThanConstraintComponent"),
    "lessThanOrEquals":("SHACL §4.5.4 sh:lessThanOrEquals", SHACL + "#LessThanOrEqualsConstraintComponent"),
    "logical":         ("SHACL §4.6 Logical Constraint Components", SHACL + "#core-components-logical"),
    "not":             ("SHACL §4.6.1 sh:not", SHACL + "#NotConstraintComponent"),
    "and":             ("SHACL §4.6.2 sh:and", SHACL + "#AndConstraintComponent"),
    "or":              ("SHACL §4.6.3 sh:or", SHACL + "#OrConstraintComponent"),
    "xone":            ("SHACL §4.6.4 sh:xone", SHACL + "#XoneConstraintComponent"),
    "node":            ("SHACL §4.7.1 sh:node", SHACL + "#NodeConstraintComponent"),
    "property":        ("SHACL §4.7.2 sh:property", SHACL + "#PropertyConstraintComponent"),
    "qualified":       ("SHACL §4.7.3 sh:qualifiedValueShape", SHACL + "#QualifiedValueShapeConstraintComponent"),
    "closed":          ("SHACL §4.8.1 sh:closed, sh:ignoredProperties", SHACL + "#ClosedConstraintComponent"),
    "hasValue":        ("SHACL §4.8.2 sh:hasValue", SHACL + "#HasValueConstraintComponent"),
    "in":              ("SHACL §4.8.3 sh:in", SHACL + "#InConstraintComponent"),
    "sparql":          ("SHACL §5 SPARQL-based Constraints", SHACL + "#sparql-constraints"),
    "sparqlSyntax":    ("SHACL §5.2 Syntax of SPARQL-based Constraints", SHACL + "#sparql-constraints-syntax"),
    "prefixes":        ("SHACL §5.2.1 Prefix Declarations for SPARQL Queries", SHACL + "#sparql-prefixes"),
    "prebound":        ("SHACL §5.3.1 Pre-bound Variables in SPARQL Constraints", SHACL + "#sparql-constraints-prebound"),
    "bindings":        ("SHACL §5.3.2 Mapping of Solution Bindings to Result Properties", SHACL + "#sparql-constraints-variables"),
    "components":      ("SHACL §6 SPARQL-based Constraint Components", SHACL + "#sparql-constraint-components"),
    "parameters":      ("SHACL §6.2.1 Parameter Declarations (sh:parameter)", SHACL + "#constraint-components-parameters"),
    "labelTemplate":   ("SHACL §6.2.2 Label Templates (sh:labelTemplate)", SHACL + "#labelTemplate"),
    "validators":      ("SHACL §6.2.3 Validators", SHACL + "#constraint-components-validators"),
    "selectValidator": ("SHACL §6.2.3.1 SELECT-based Validators", SHACL + "#SPARQLSelectValidator"),
    "askValidator":    ("SHACL §6.2.3.2 ASK-based Validators", SHACL + "#SPARQLAskValidator"),
    "prebinding":      ("SHACL Appendix A Pre-binding of Variables in SPARQL Queries", SHACL + "#pre-binding"),
    "syntaxRules":     ("SHACL Appendix B Summary of SHACL Syntax Rules", SHACL + "#syntax-rules"),
    "coreValidators":  ("SHACL Appendix D Summary of SHACL Core Validators", SHACL + "#core-validators"),
    "shaclRdfs":       ("SHACL §1.5 Relationship between SHACL and RDFS inferencing", SHACL + "#shacl-rdfs"),
    "shaclSparql":     ("SHACL §1.6 Relationship between SHACL and SPARQL", SHACL + "#shacl-sparql"),
    # SHACL Advanced Features
    "afTargets":       ("SHACL-AF §3 Custom Targets", AF + "#targets"),
    "afSparqlTarget":  ("SHACL-AF §3.1 SPARQL-based Targets", AF + "#SPARQLTarget"),
    "afTargetType":    ("SHACL-AF §3.2 SPARQL-based Target Types", AF + "#SPARQLTargetType"),
    "afAnnotations":   ("SHACL-AF §4 Annotation Properties", AF + "#sparql-constraints-annotations"),
    "afFunctions":     ("SHACL-AF §5 SHACL Functions", AF + "#functions"),
    "afSparqlFunction":("SHACL-AF §5.4 SPARQL-based Functions", AF + "#SPARQLFunction"),
    "afNodeExpr":      ("SHACL-AF §6 Node Expressions", AF + "#node-expressions"),
    "afFocusExpr":     ("SHACL-AF §6.1 Focus Node Expressions", AF + "#node-expressions-focus"),
    "afFilterShape":   ("SHACL-AF §6.3 Filter Shape Expressions", AF + "#node-expressions-filter-shape"),
    "afPathExpr":      ("SHACL-AF §6.5 Path Expressions", AF + "#node-expressions-path"),
    "afIntersection":  ("SHACL-AF §6.6 Intersection Expressions", AF + "#intersection"),
    "afUnion":         ("SHACL-AF §6.7 Union Expressions", AF + "#union"),
    "afExpression":    ("SHACL-AF §7 Expression Constraints", AF + "#ExpressionConstraintComponent"),
    "afRules":         ("SHACL-AF §8 SHACL Rules", AF + "#rules"),
    "afRulesSyntax":   ("SHACL-AF §8.2 General Syntax of SHACL Rules", AF + "#rules-syntax"),
    "afCondition":     ("SHACL-AF §8.2.1 sh:condition", AF + "#condition"),
    "afOrder":         ("SHACL-AF §8.2.2 sh:order", AF + "#rules-order"),
    "afRuleDeactivated":("SHACL-AF §8.2.3 sh:deactivated", AF + "#deactivated"),
    "afEntailment":    ("SHACL-AF §8.3 The sh:Rules Entailment Regime", AF + "#Rules"),
    "afExecution":     ("SHACL-AF §8.4 General Execution Instructions for SHACL Rules", AF + "#rules-execution"),
    "afTripleRule":    ("SHACL-AF §8.5 Triple Rules", AF + "#TripleRule"),
    "afSparqlRule":    ("SHACL-AF §8.6 SPARQL Rules", AF + "#SPARQLRule"),
    # SHACL 1.2 drafts
    "c12ShapeClass":   ("SHACL 1.2 Core §3.1.3.3 Implicit Class Targets and sh:ShapeClass", CORE12 + "#implicit-targetClass"),
    "c12targetWhere":  ("SHACL 1.2 Core §3.1.3.6 Where Targets (sh:targetWhere)", CORE12 + "#targetWhere"),
    "c12shape":        ("SHACL 1.2 Core §3.1.3.7 Explicit shape targets (sh:shape)", CORE12 + "#explicit-shape-target"),
    "c12severity":     ("SHACL 1.2 Core §3.1.4 Declaring the Severity of a Shape or Constraint", CORE12 + "#severity"),
    "c12subClassGraph":("SHACL 1.2 Core §6.3 Graph for rdfs:subClassOf Triples", CORE12 + "#subClassOfInShapesGraph"),
    "c12conformanceDisallows": ("SHACL 1.2 Core §6.7.1.2 sh:conformanceDisallows", CORE12 + "#conformanceDisallows"),
    "c12singleLine":   ("SHACL 1.2 Core §7.4.4 sh:singleLine", CORE12 + "#SingleLineConstraintComponent"),
    "c12lists":        ("SHACL 1.2 Core §7.5 List Constraint Components", CORE12 + "#core-components-list"),
    "c12subsetOf":     ("SHACL 1.2 Core §7.6.3 sh:subsetOf", CORE12 + "#SubsetOfConstraintComponent"),
    "c12reifier":      ("SHACL 1.2 Core §7.8.5 sh:reifierShape, sh:reificationRequired", CORE12 + "#ReifierShapeConstraintComponent"),
    "c12uniqueValuesFor": ("SHACL 1.2 Core §7.9.5 sh:uniqueValuesFor", CORE12 + "#UniqueValuesForConstraintComponent"),
    "c12nonValidating":("SHACL 1.2 Core §8 Non-Validating Shape Characteristics", CORE12 + "#nonValidation"),
    "s12prefixes":     ("SHACL 1.2 SPARQL §2 Prefix Declarations for SPARQL Queries", SPARQL12 + "#sparql-prefixes"),
    "s12constraints":  ("SHACL 1.2 SPARQL §3 SPARQL-based Constraints", SPARQL12 + "#sparql-constraints"),
    "s12bindings":     ("SHACL 1.2 SPARQL §3.3.2 Mapping of Solution Bindings to Result Properties", SPARQL12 + "#sparql-constraints-variables"),
    "s12components":   ("SHACL 1.2 SPARQL §4 SPARQL-based Constraint Components", SPARQL12 + "#sparql-constraint-components"),
    "s12nodeExpr":     ("SHACL 1.2 SPARQL §6 SPARQL-based Node Expressions", SPARQL12 + "#sparql-node-expressions"),
    "s12select":       ("SHACL 1.2 SPARQL §6.1 Select Expressions", SPARQL12 + "#SelectExpression"),
    "s12functions":    ("SHACL 1.2 SPARQL §7 Declaring SPARQL Functions based on Node Expressions", SPARQL12 + "#sparql-functions"),
    "n12intro":        ("SHACL 1.2 Node Expressions §2 Getting started with Node Expressions", NODEEXPR12 + "#getting-started"),
    "n12library":      ("SHACL 1.2 Node Expressions §4 Node Expressions Library", NODEEXPR12 + "#library"),
    "n12expression":   ("SHACL 1.2 Node Expressions §7.1 sh:expression", NODEEXPR12 + "#ExpressionConstraintComponent"),
    "r12overview":     ("SHACL 1.2 Rules §3 SPARQL-RL", RULES12 + "#overview"),
    "r12negation":     ("SHACL 1.2 Rules §3.4 Negation", RULES12 + "#desc-negation"),
    "r12stratification":("SHACL 1.2 Rules §4.4 Stratification", RULES12 + "#stratification"),
    # Neighbouring standards
    "sparqlPaths":     ("SPARQL 1.2 Query §9 Property Paths", SPARQL + "#x9-property-paths"),
    "sparqlNegationSection": ("SPARQL 1.2 Query §8 Negation", SPARQL + "#x8-negation"),
    "sparqlAggregates":("SPARQL 1.2 Query §11 Aggregates", SPARQL + "#x11-aggregates"),
    "sparqlConstruct": ("SPARQL 1.2 Query §16.2 CONSTRUCT", SPARQL + "#x16-2-construct"),
    "sparqlNegation":  ("SPARQL 1.2 Query §8.1 Filtering Using Graph Patterns", SPARQL + "#x8-1-filtering-using-graph-patterns"),
    "sparqlOperators": ("SPARQL 1.2 Query §17.3 Operator Mapping", SPARQL + "#x17-3-operator-mapping"),
    "rdf12triples":    ("RDF 1.2 Concepts §2.2 Triple Terms and Reification", RDF12 + "#section-triple-terms"),
    "rdf12dir":        ("RDF 1.2 Concepts §3.3 Literals", RDF12 + "#section-Graph-Literal"),
    "turtle12annot":   ("RDF 1.2 Turtle §2.9 Reifying Triples", TURTLE12 + "#reifying-triples"),
    "turtle12lists":   ("RDF 1.2 Turtle §2.8 Collections", TURTLE12 + "#collections"),
}

# Which sections a module is defined by, in the order the README lists them.
MODULE_SPECS = {
    "00-the-lab": ["shapesGraph", "dataGraph", "validation", "report", "conforms"],
    "01-first-shapes": ["shapes", "targets", "targetClass", "targetNode", "targetSubjectsOf", "targetObjectsOf",
                        "implicit", "propertyShapes", "minCount", "maxCount", "severity", "message", "deactivated",
                        "result", "conformance"],
    "02-value-constraints": ["datatype", "nodeKind", "class", "range", "strings", "pattern", "languageIn",
                             "uniqueLang", "in", "hasValue", "pairs", "lessThan", "lessThanOrEquals", "equals", "disjoint"],
    "03-property-paths": ["paths", "pathSequence", "pathInverse", "pathAlternative", "pathZeroOrMore",
                          "pathOneOrMore", "pathZeroOrOne", "resultPath", "sparqlPaths"],
    "04-shapes-and-logic": ["node", "property", "logical", "not", "and", "or", "xone", "qualified", "closed",
                            "recursion", "valueNodes"],
    "05-sparql-constraints": ["sparql", "sparqlSyntax", "prefixes", "prebound", "bindings", "prebinding",
                              "afSparqlTarget", "c12targetWhere", "report", "shaclSparql"],
    "06-constraint-components": ["components", "parameters", "labelTemplate", "validators", "selectValidator",
                                 "askValidator", "coreValidators"],
    "07-rules": ["afRules", "afRulesSyntax", "afTripleRule", "afSparqlRule", "afCondition", "afOrder",
                 "afRuleDeactivated", "afExecution", "afNodeExpr", "afPathExpr", "afFilterShape", "afUnion",
                 "afIntersection", "afEntailment", "r12overview", "r12stratification"],
    "08-shacl-1-2": ["c12reifier", "c12ShapeClass", "c12targetWhere", "c12shape", "c12severity", "c12singleLine",
                     "c12subsetOf", "c12conformanceDisallows", "rdf12triples", "turtle12annot"],
    "09-inference": ["shaclRdfs", "c12subClassGraph", "targetClass", "class"],
    "10-debugging": ["failures", "conformance", "targets", "valueNodes", "severity", "sourceShape", "datatype"],
    "11-putting-it-together": ["shapesGraph", "report", "result", "afRules", "sparql"],
    "12-beyond-this-engine": ["afFunctions", "afSparqlFunction", "afTargetType", "afAnnotations", "afExpression",
                              "n12intro", "n12library", "s12nodeExpr", "s12functions", "c12uniqueValuesFor",
                              "c12lists", "r12overview", "r12negation"],
}

# Per-lesson overrides: the first two are what the .ttl header shows. A lesson
# not listed here takes the first two of its module's list.
LESSON_SPECS: dict[str, list[str]] = {}


def register(sid: str, *keys: str) -> None:
    LESSON_SPECS[sid] = list(keys)


def for_lesson(sid: str, module: str, limit: int = 2) -> list[tuple[str, str]]:
    keys = LESSON_SPECS.get(sid) or MODULE_SPECS.get(module, [])
    return [SECTIONS[k] for k in keys[:limit]]


def for_module(module: str) -> list[tuple[str, str]]:
    seen, out = set(), []
    for k in MODULE_SPECS.get(module, []):
        if k not in seen:
            seen.add(k)
            out.append(SECTIONS[k])
    return out


# The reading list at the end of the README and the course document.
READING_LIST = [
    ("The specifications", [
        (SHACL, "Shapes Constraint Language (SHACL)",
         "The W3C Recommendation of 2017. Modules 01 to 06 and 10 are defined here; §4 is the constraint component reference you will open most often, and Appendix D shows each Core component as the SPARQL it is equivalent to."),
        (AF, "SHACL Advanced Features",
         "A Working Group Note rather than a Recommendation, and the definition of SPARQL-based targets, node expressions and SHACL rules. Module 07 is defined here."),
        (CORE12, "SHACL 1.2 Core",
         "A Working Draft, still changing. The reification constraints, sh:targetWhere, sh:ShapeClass, per-constraint severities and the new string and list components are here. Module 08 says which of them the engine runs."),
        (SPARQL12, "SHACL 1.2 SPARQL Extensions",
         "The 1.2 edition of SHACL-SPARQL: constraints, constraint components, prefix declarations, and SPARQL-based node expressions."),
        (NODEEXPR12, "SHACL 1.2 Node Expressions",
         "A library of node expression functions with a namespace of its own. Not implemented by the engine in the editor; module 12 explains where it is heading."),
        (RULES12, "SHACL 1.2 Rules (SPARQL-RL)",
         "A rule language with stratified negation, different in design from SHACL-AF rules. Not implemented by the engine; the last lesson of module 07 reads it for what it fixes."),
    ]),
    ("The data model and the query language", [
        (SPARQL, "SPARQL 1.2 Query Language",
         "Everything inside sh:select, sh:ask and sh:construct is SPARQL. The SPARQL course covers it in full; this course points at it where a constraint needs it."),
        (RDF12, "RDF 1.2 Concepts and Abstract Syntax",
         "Triple terms and reifiers, which module 08 validates."),
        (TURTLE12, "RDF 1.2 Turtle",
         "The syntax of every file here, including the {| ... |} annotations in the 1.2 edition of the data."),
    ]),
]
