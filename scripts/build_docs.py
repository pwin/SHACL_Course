# -*- coding: utf-8 -*-
"""docs/index.html: the whole course as one document.

    python scripts/check_shapes.py      # first, so the measured reports are current
    python scripts/build_docs.py

Every lesson appears with its shapes, its explanation, the report the engine
produced for it, and buttons that open the lesson in the editor or copy the
shapes. The reference sections at the end are generated from the same tables
the READMEs use.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import catalogue  # noqa: E402,F401
import check_faults  # noqa: E402
import engine_matrix  # noqa: E402
import features  # noqa: E402
import specs  # noqa: E402
from shapecat import CATALOGUE, MODULE_INFO, REPO, SPARQL_REPO, EDITOR_BASE  # noqa: E402

BUILD = ROOT / "build"
DOCS = ROOT / "docs"
MAX_ROWS = 12

E = html.escape

# ---------------------------------------------------------------- highlighting

SPARQL_KW = re.compile(r"\b(SELECT|CONSTRUCT|ASK|WHERE|FILTER|BIND|AS|NOT|EXISTS|UNION|OPTIONAL|GROUP BY|HAVING|"
                       r"ORDER BY|DESC|ASC|LIMIT|PREFIX|GRAPH|MINUS|VALUES|SERVICE|DISTINCT|COUNT|SUM|STR|SUBSTR|"
                       r"REGEX|BOUND|COALESCE|FLOOR|LANG|IN)\b")
SPARQL_VAR = re.compile(r"(\$this|\$value|\$PATH|\$shapesGraph|\$currentShape|\$[A-Za-z][A-Za-z0-9]*|\?[A-Za-z][A-Za-z0-9]*)")

TOKEN = re.compile(r"""
    (?P<comment>\#[^\n]*)
  | (?P<lstring>"{3}[\s\S]*?"{3})
  | (?P<string>"(?:[^"\\\n]|\\.)*"(?:@[A-Za-z0-9-]+|\^\^[A-Za-z]+:[A-Za-z0-9_]+)?)
  | (?P<iri><[^>\s]*>)
  | (?P<annot>\{\||\|\}|@prefix)
  | (?P<sh>(?<![A-Za-z0-9])sh:[A-Za-z][A-Za-z0-9]*)
  | (?P<pname>(?<![A-Za-z0-9])[A-Za-z][A-Za-z0-9_-]*:[A-Za-z0-9_.-]*)
  | (?P<num>(?<![A-Za-z0-9_.-])-?\d+(?:\.\d+)?(?![A-Za-z0-9_-]))
  | (?P<kw>(?<![A-Za-z0-9_])(?:a|true|false)(?![A-Za-z0-9_]))
""", re.X)


def highlight_sparql(text: str) -> str:
    out, pos = [], 0
    for m in SPARQL_VAR.finditer(text):
        out.append(SPARQL_KW.sub(lambda k: f'<b>{k.group(0)}</b>', E(text[pos:m.start()])))
        out.append(f'<span class="t-var">{E(m.group(0))}</span>')
        pos = m.end()
    out.append(SPARQL_KW.sub(lambda k: f'<b>{k.group(0)}</b>', E(text[pos:])))
    return "".join(out)


def highlight(turtle: str) -> str:
    out, pos = [], 0
    for m in TOKEN.finditer(turtle):
        out.append(E(turtle[pos:m.start()]))
        kind = m.lastgroup
        tok = m.group(0)
        if kind == "comment":
            out.append(f'<span class="t-comment">{E(tok)}</span>')
        elif kind == "lstring":
            out.append(f'<span class="t-string">{highlight_sparql(tok)}</span>')
        elif kind == "string":
            out.append(f'<span class="t-string">{E(tok)}</span>')
        elif kind == "iri":
            out.append(f'<span class="t-iri">{E(tok)}</span>')
        elif kind == "annot":
            out.append(f'<span class="t-annot">{E(tok)}</span>')
        elif kind == "sh":
            out.append(f'<span class="t-kw">{E(tok)}</span>')
        elif kind == "pname":
            out.append(f'<span class="t-pname">{E(tok)}</span>')
        elif kind == "num":
            out.append(f'<span class="t-num">{E(tok)}</span>')
        elif kind == "kw":
            out.append(f'<span class="t-fn">{E(tok)}</span>')
        pos = m.end()
    out.append(E(turtle[pos:]))
    return "".join(out)


# ---------------------------------------------------------------- pieces

def prose(text: str) -> str:
    """Paragraphs from a how/notes string; code-ish tokens in <code>."""
    paras = [" ".join(p.split()) for p in text.split(chr(10) + chr(10)) if p.strip()]
    def fmt(p):
        p = E(p)
        p = re.sub(r"(?<![\w/])((?:sh|bs|bt|rdf|rdfs|xsd|skos|owl|geo|schema|dct|wgs84):[A-Za-z][\w.-]*)", r"<code>\1</code>", p)
        p = re.sub(r"(?<![\w-])(s\d\d)\b", r'<a href="#\1">\1</a>', p)
        p = re.sub(r"(?<![\w-])(q\d{2,3})\b", r'<a href="%s/tree/main/queries">\1</a>' % SPARQL_REPO, p)
        p = re.sub(r"(?<![\w-])(F\d\d)\b", r'<a href="#faults">\1</a>', p)
        p = re.sub(r"\b(\$this|\$value|\$PATH|\$shapesGraph|\$currentShape|\?value|\?path|\?message|\?this)", r"<code>\1</code>", p)
        return f"<p>{p}</p>"
    return "".join(fmt(p) for p in paras)


def button_bar(l) -> str:
    return (f'<div class="btns">'
            f'<a class="btn primary" href="{E(l.editor_url)}" target="_blank" rel="noopener">Open in the editor</a>'
            f'<button class="btn" data-copy="{l.sid}">Copy shapes</button>'
            f'<a class="btn" href="{REPO}/blob/main/shapes/{l.module}/{E(l.filename)}" target="_blank" rel="noopener">The file</a>'
            f'</div>')


def report_block(l, results: dict) -> str:
    r = results.get(l.sid)
    if not r:
        return ""
    if not r.get("ok"):
        return (f'<div class="report err"><h4>The engine says</h4>'
                f'<p class="results-note">{E(r.get("error", ""))}</p></div>')
    c = r["counts"]
    verdict = "conforms" if r["conforms"] else "fails"
    head = (f'<span class="verdict {verdict}">{"Conforms" if r["conforms"] else "Does not conform"}</span> '
            f'&middot; {c["Violation"]} violation{"s" if c["Violation"] != 1 else ""}, {c["Warning"]} warning{"s" if c["Warning"] != 1 else ""}, '
            f'{c["Info"]} info &middot; {r["shapeCount"]} shapes')
    if l.inference != "none":
        head += f' &middot; inference <em>{E(l.inference)}</em>'
    rows = r["results"]
    if not rows:
        body = '<p class="results-note">Nothing to report.</p>'
    else:
        trs = []
        for x in rows[:MAX_ROWS]:
            msg = x["message"] if len(x["message"]) < 160 else x["message"][:157] + "…"
            trs.append(f'<tr class="sev-{x["severity"].lower()}"><td>{x["severity"]}</td><td><code>{E(x["focusNode"])}</code></td>'
                       f'<td><code>{E(x["path"] or "")}</code></td><td>{E(x["value"] or "")}</td><td>{E(msg)}</td>'
                       f'<td class="shape">{E(x["sourceShape"] or "")}</td></tr>')
        more = f'<p class="results-note">and {len(rows) - MAX_ROWS} more</p>' if len(rows) > MAX_ROWS else ""
        body = (f'<div class="tablewrap"><table><thead><tr><th>Severity</th><th>Focus node</th><th>Path</th>'
                f'<th>Value</th><th>Message</th><th>Shape</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div>{more}')
    return f'<div class="report"><h4>The report</h4><p class="headline">{head}</p>{body}</div>'


def lesson_html(l, results: dict) -> str:
    specs_html = "".join(f'<li><a href="{E(u)}">{E(t)}</a></li>' for t, u in specs.for_lesson(l.sid, l.module, limit=2))
    learn = "".join(f"<li>{prose(x)[3:-4]}</li>" for x in l.learn)
    notes = f'<h4>Note</h4>{prose(l.notes)}' if l.notes else ""
    tryit = f'<h4>Try it</h4>{prose(l.tryit)}' if l.tryit else ""
    queries = ""
    if l.queries:
        items = []
        for i, q in enumerate(l.queries):
            qid = f"{l.sid}-q{i}"
            items.append(f'<div class="query"><div class="qh"><span>{E(q.title)} <em>(on the {q.on})</em></span>'
                         f'<button class="btn small" data-copy="{qid}">Copy query</button></div>'
                         f'<div class="code-wrap"><pre class="code" id="code-{qid}">{highlight_sparql(q.text.strip())}</pre></div></div>')
        queries = f'<h4>Afterwards, in the SPARQL panel</h4>{"".join(items)}'
    data_line = f'<code>{E(l.data)}</code>' + (f' &middot; Inference <em>{E(l.inference)}</em>' if l.inference != "none" else "")
    return f"""
<article class="lesson" id="{l.sid}">
  <div class="lhead"><span class="lid">{l.sid.upper()}</span><h3>{E(l.title)}</h3></div>
  <p class="asks">{E(l.asks)}</p>
  <p class="dataline">Data: {data_line}</p>
  {button_bar(l)}
  <div class="code-wrap"><pre class="code" id="code-{l.sid}">{highlight(l.shapes_text.strip())}</pre></div>
  <div class="mech">
    <div class="mech-prose"><h4>How it works</h4>{prose(l.how)}</div>
    <div class="mech-diagram"><h4>Diagram</h4><pre class="diagram">{E(l.diagram.strip(chr(10)))}</pre></div>
  </div>
  <div class="learn"><h4>What to take away</h4><ul>{learn}</ul>{notes}{tryit}</div>
  {report_block(l, results)}
  {queries}
  <p class="specline">Defined in <ul class="specs">{specs_html}</ul></p>
</article>"""


def module_html(module: str, lessons: list, results: dict) -> str:
    title, blurb = MODULE_INFO[module]
    num = module.split("-")[0]
    spec_links = "".join(f'<li><a href="{E(u)}">{E(t)}</a></li>' for t, u in specs.for_module(module))
    body = "".join(lesson_html(l, results) for l in lessons)
    return f"""
<section class="module" id="m{num}">
  <div class="module-head"><div class="module-num">Module {num}</div><h2>{E(title)}</h2>
  <p class="module-blurb">{E(blurb)}</p>
  <details class="standards"><summary>In the standards</summary><ul>{spec_links}</ul></details></div>
  {body}
</section>"""


def lab_html() -> str:
    return f"""
<section class="module" id="m00">
  <div class="module-head"><div class="module-num">Module 00</div><h2>The lab</h2>
  <p class="module-blurb">Twenty minutes on the tool before the first shape. Everything runs in the Turtle Editor Viewer at
  <a href="{EDITOR_BASE}">semantechs.co.uk/turtle-editor-viewer</a>; the parser, the SPARQL engine and the SHACL engine run
  inside the page, and nothing you load leaves your browser. The full text is
  <a href="{REPO}/tree/main/shapes/00-the-lab">shapes/00-the-lab/README.md</a>.</p></div>

  <div class="grid2">
    <div class="panel"><h3>Two tabs and a button</h3>
      <p>The data goes in the first tab. Press <b>+</b> for a second tab and load the shapes into it. Switch back to the data tab,
      choose the shapes tab in the <b>Shapes</b> dropdown, leave <b>Inference</b> at <em>none</em>, press <b>Validate</b>.</p>
      <p>Every lesson's <b>Open in the editor</b> button does all of that: <code>?dot=</code> carries the data,
      <code>&amp;shapes=</code> the shapes, <code>&amp;inference=</code> the mode.</p></div>
    <div class="panel"><h3>Reading the report</h3>
      <p>The headline: Conforms or not, the counts by severity, and how many shapes compiled. Then one row per result:
      severity, focus node, path, value, message, and which shape said so.</p>
      <p><b>Report as tab</b> opens the report as RDF, so the SPARQL panel can query it. <b>Export report</b> saves it.</p></div>
    <div class="panel"><h3>The Inference dropdown</h3>
      <p><em>none</em> is SHACL as specified. <em>RDFS</em> validates the closure of the data (module 09). <em>rules</em> runs the
      shapes graph's <code>sh:rule</code>s once first (module 07); <em>rules, iterated</em> repeats them to a fixpoint.</p>
      <p>The tab's text is never changed; the expanded graph lives for the run only.</p></div>
    <div class="panel"><h3>Two things about the headline</h3>
      <p>The shapes count is how many shapes compiled; compare it with what you wrote. And <b>Conforms</b> means no violations
      were found, which is also what it says when nothing was checked. Lesson s09 is about that.</p></div>
  </div>

  <h4 class="subhead">The same engine, from the command line</h4>
  <div class="code-wrap"><pre class="code">npm install --prefix scripts
node scripts/validate.mjs --data data/bookshop-trail-faulty.ttl --shapes shapes/01-first-shapes/s02-reading-a-violation.ttl
node scripts/validate.mjs --data data/bookshop-trail-1.1.ttl --shapes shapes/07-rules/s51-to-a-fixpoint.ttl --inference rules-iterated
node scripts/validate.mjs ... --format turtle &gt; report.ttl</pre></div>
  <p class="module-blurb"><code>scripts/validate.mjs</code> names the nested property shapes and renders the compound paths as the
  editor does, so its rows match the browser's. <code>python scripts/check_shapes.py</code> runs every lesson through it and compares
  the report with what the lesson claims; <code>python scripts/check_faults.py</code> confirms every numbered fault is caught by the
  lesson that names it.</p>
</section>"""


def faults_html() -> str:
    rows = []
    for fid, lessons, subject in check_faults.faults(ROOT / "data" / "faults.ttl") + check_faults.faults(ROOT / "data" / "faults-1.2.ttl"):
        rows.append((fid, subject or "", lessons))
    # descriptions: first line of each fault comment
    desc = {}
    for path in (ROOT / "data" / "faults.ttl", ROOT / "data" / "faults-1.2.ttl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = check_faults.FAULT.match(line)
            if m:
                desc[m.group(1)] = re.sub(r"\s+->.*$", "", m.group(2)).strip()
    trs = "".join(f'<tr><td><code>{fid}</code></td><td>{E(desc.get(fid, ""))}</td><td><code>{E(subj)}</code></td>'
                  f'<td>{" ".join(f"<a href=#{s}>{s}</a>" for s in lessons)}</td></tr>' for fid, subj, lessons in rows)
    return f"""
<section class="module ref" id="faults">
  <div class="module-head"><div class="module-num">Reference</div><h2>The faults</h2>
  <p class="module-blurb">Thirty-six deliberate mistakes, appended to the clean data to make <code>bookshop-trail-faulty.ttl</code>.
  Each says which lesson catches it, and <code>scripts/check_faults.py</code> confirms that it does. The clean files are the
  SPARQL course's, byte for byte.</p></div>
  <div class="tablewrap"><table><thead><tr><th>Fault</th><th>What is wrong</th><th>Resource</th><th>Caught by</th></tr></thead>
  <tbody>{trs}</tbody></table></div>
</section>"""


def matrix_html() -> str:
    trs = "".join(
        f'<tr><td>{E(f)}</td><td>{E(sp)}</td><td class="st-{st}">{E(engine_matrix.STATUS_LABEL[st])}</td>'
        f'<td>{" ".join(f"<a href=#{x.strip()}>{x.strip()}</a>" if re.fullmatch(r"s\d\d", x.strip()) else E(x.strip()) for x in les.split(",")) if les else ""}</td>'
        f'<td>{E(note)}</td></tr>'
        for f, sp, st, les, note in engine_matrix.ROWS)
    return f"""
<section class="module ref" id="engine">
  <div class="module-head"><div class="module-num">Reference</div><h2>What this engine does with each feature</h2>
  <p class="module-blurb">Measured against <code>shacl-wasm-node</code> 0.2.0, the build the editor ships, while the course was
  written. <em>runs</em> means a lesson shows it; <em>error</em> means the engine refuses and says why; <em>silent</em> means the
  feature is read and ignored, and the report looks the same as if it had passed. Module 12's README has the comparison with
  pySHACL.</p></div>
  <div class="tablewrap"><table><thead><tr><th>Feature</th><th>Defined in</th><th>This build</th><th>Lesson</th><th>Note</th></tr></thead>
  <tbody>{trs}</tbody></table></div>
</section>"""


def features_html() -> str:
    where = {}
    for l in CATALOGUE:
        for t in features.terms_in(l):
            where.setdefault(t, []).append(l)
    groups = []
    for group, items in features.TERMS:
        trs = []
        for term, key in items:
            label, url = specs.SECTIONS[key]
            refs = " ".join(f'<a href="#{l.sid}">{l.sid}</a>' for l in where.get(term, []))
            trs.append(f'<tr><td><code>{E(term)}</code></td><td><a href="{E(url)}">{E(label)}</a></td><td>{refs}</td></tr>')
        groups.append(f'<h4 class="subhead">{E(group)}</h4><div class="tablewrap"><table><thead><tr><th>Term</th><th>Defined in</th>'
                      f'<th>Lessons</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div>')
    return f"""
<section class="module ref" id="features">
  <div class="module-head"><div class="module-num">Reference</div><h2>Every term, and where it is shown</h2>
  <p class="module-blurb">Generated from the shapes themselves, so it cannot disagree with them. The same index is
  <a href="{REPO}/blob/main/FEATURES.md">FEATURES.md</a> in the repository.</p></div>
  {"".join(groups)}
</section>"""


def standards_html() -> str:
    parts = []
    for heading, items in specs.READING_LIST:
        lis = "".join(f'<li><a href="{E(u)}">{E(t)}</a> — {E(d)}</li>' for u, t, d in items)
        parts.append(f'<h4 class="subhead">{E(heading)}</h4><ul class="reading">{lis}</ul>')
    return f"""
<section class="module ref" id="standards">
  <div class="module-head"><div class="module-num">Reference</div><h2>The standards</h2>
  <p class="module-blurb">Everything this course teaches is defined in one of these, usually in one short section, and each lesson's
  header names the sections it is defined by. <code>python scripts/check_links.py</code> fetches every document and confirms each
  anchor still lands on its heading.</p></div>
  {"".join(parts)}
</section>"""


# ---------------------------------------------------------------- page

CSS = """
:root {
  --paper:#fbfaf7; --paper-2:#f2f1ec; --paper-3:#e7e6df; --ink:#191d24; --ink-2:#454c58; --ink-3:#6f7784;
  --rule:#d8d7cf; --route:#c8006e; --route-soft:#fbe9f2; --bracken:#4a6b3d; --bracken-soft:#eaf0e6;
  --amber:#9a6b00; --amber-soft:#fbf1dc; --code-bg:#f4f3ee; --code-edge:#e2e1d8;
  --t-kw:#8a2f6b; --t-fn:#1d5c73; --t-var:#245a2a; --t-str:#8a4b1a; --t-iri:#4a5160; --t-pname:#2f4858; --t-com:#8b8f86; --t-num:#8a4b1a; --t-annot:#c8006e;
  --sans:"Atkinson Hyperlegible",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --mono:"JetBrains Mono",ui-monospace,"Cascadia Mono",Consolas,monospace;
  --maxw:74ch; color-scheme:light;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper:#14161a; --paper-2:#1b1e23; --paper-3:#24282e; --ink:#e8e6e0; --ink-2:#b9bcc2; --ink-3:#8b9099; --rule:#2f343b;
  --route:#ff5fa8; --route-soft:#33101f; --bracken:#8fbe79; --bracken-soft:#18241a; --amber:#d9a441; --amber-soft:#2a2113;
  --code-bg:#191c21; --code-edge:#2b3037;
  --t-kw:#e59ad0; --t-fn:#7fc8e0; --t-var:#9ed5a3; --t-str:#e0b083; --t-iri:#9aa3b0; --t-pname:#a8c4d4; --t-com:#71776f; --t-num:#e0b083; --t-annot:#ff5fa8;
  color-scheme:dark; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink); font-family:var(--sans); font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased; }
a { color:var(--route); text-decoration-thickness:1px; text-underline-offset:2px; }
code { font-family:var(--mono); font-size:.86em; }
.shell { display:grid; grid-template-columns:250px minmax(0,1fr); }
.rail { position:sticky; top:0; align-self:start; height:100vh; overflow-y:auto; padding:28px 20px 40px; border-right:1px solid var(--rule); background:var(--paper-2); }
.rail .brand { font-family:var(--serif); font-size:1.15rem; line-height:1.25; margin:0 0 4px; }
.rail .brand em { font-style:italic; color:var(--route); }
.rail .tagline { font-size:.78rem; color:var(--ink-3); margin:0 0 20px; }
.rail ol { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:1px; }
.rail ol a { display:grid; grid-template-columns:26px 1fr auto; align-items:baseline; gap:6px; padding:6px 8px; border-radius:2px; color:var(--ink-2); text-decoration:none; font-size:.82rem; line-height:1.3; }
.rail ol a:hover { background:var(--paper-3); color:var(--ink); }
.rail .n { font-family:var(--mono); font-size:.72rem; color:var(--route); }
.rail .c { font-family:var(--mono); font-size:.68rem; color:var(--ink-3); }
.rail .railnote { font-size:.74rem; color:var(--ink-3); margin-top:22px; padding-top:14px; border-top:1px solid var(--rule); }
main { padding:0 0 100px; min-width:0; }
.hero { padding:44px 40px 34px; border-bottom:1px solid var(--rule); }
.hero .logo { width:64px; height:64px; display:block; margin:0 0 18px; }
.eyebrow { font-family:var(--mono); font-size:.7rem; letter-spacing:.14em; text-transform:uppercase; color:var(--route); margin:0 0 14px; }
h1 { font-family:var(--serif); font-weight:600; font-size:clamp(2.1rem,4.4vw,3.1rem); line-height:1.05; margin:0 0 16px; letter-spacing:-.015em; max-width:22ch; }
h1 small { display:block; font-size:.5em; color:var(--ink-3); font-weight:400; margin-top:6px; }
.standfirst { font-size:1.06rem; color:var(--ink-2); max-width:var(--maxw); margin:0 0 26px; }
.standfirst strong { color:var(--ink); font-weight:400; border-bottom:2px solid var(--route-soft); }
.facts { display:flex; flex-wrap:wrap; margin-top:8px; border-top:1px solid var(--rule); }
.fact { padding:14px 26px 12px 0; margin-right:26px; }
.fact b { display:block; font-family:var(--mono); font-size:1.45rem; font-weight:700; line-height:1; color:var(--ink); }
.fact span { font-size:.76rem; color:var(--ink-3); }
.intro { padding:34px 40px 10px; }
.intro h2, .subhead { font-family:var(--serif); font-weight:600; font-size:1.5rem; margin:34px 0 10px; letter-spacing:-.01em; }
h4.subhead { font-size:1.15rem; margin:30px 0 8px; }
.intro p { max-width:var(--maxw); color:var(--ink-2); }
.intro p strong { color:var(--ink); }
.grid2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:22px; margin:22px 0; }
.panel { border:1px solid var(--rule); border-radius:3px; padding:16px 18px; background:var(--paper-2); }
.panel h3 { font-family:var(--sans); font-size:.8rem; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-3); margin:0 0 10px; }
.panel p { margin:0 0 8px; font-size:.92rem; }
.tablewrap { overflow-x:auto; margin:14px 0 20px; border:1px solid var(--rule); border-radius:3px; }
table { border-collapse:collapse; width:100%; font-size:.86rem; }
th, td { text-align:left; padding:8px 12px; border-bottom:1px solid var(--rule); vertical-align:top; }
th { font-size:.7rem; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-3); background:var(--paper-2); font-weight:700; }
tr:last-child td { border-bottom:none; }
td.shape { color:var(--ink-3); font-family:var(--mono); font-size:.78rem; }
.module { padding:0 40px; scroll-margin-top:12px; }
.module-head { padding:52px 0 8px; margin-top:34px; border-top:2px solid var(--ink); }
.module-num { font-family:var(--mono); font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; color:var(--route); }
.module-head h2 { font-family:var(--serif); font-weight:600; font-size:clamp(1.6rem,3vw,2.1rem); margin:6px 0 10px; letter-spacing:-.015em; }
.module-blurb { max-width:var(--maxw); color:var(--ink-2); margin:0 0 8px; }
details.standards { max-width:var(--maxw); font-size:.88rem; color:var(--ink-2); margin:8px 0 0; }
details.standards summary { cursor:pointer; color:var(--ink-3); }
details.standards ul { margin:6px 0 0; padding-left:18px; }
.lesson { padding:30px 0 26px; border-bottom:1px solid var(--rule); scroll-margin-top:12px; }
.lhead { display:flex; align-items:baseline; gap:12px; }
.lid { font-family:var(--mono); font-size:.78rem; font-weight:700; color:var(--paper); background:var(--route); padding:2px 7px; border-radius:2px; letter-spacing:.04em; }
.lhead h3 { font-family:var(--serif); font-weight:600; font-size:1.35rem; margin:0; letter-spacing:-.01em; }
.asks { max-width:var(--maxw); color:var(--ink-2); margin:8px 0 6px; font-size:1.02rem; }
.dataline { font-size:.82rem; color:var(--ink-3); margin:0 0 12px; }
.btns { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 12px; }
.btn { font:inherit; font-size:.8rem; padding:6px 12px; border:1px solid var(--rule); border-radius:3px; background:var(--paper-2); color:var(--ink); cursor:pointer; text-decoration:none; }
.btn:hover { background:var(--paper-3); }
.btn.primary { background:var(--route); border-color:var(--route); color:#fff; }
.btn.primary:hover { filter:brightness(1.08); }
.btn.small { padding:3px 9px; font-size:.74rem; }
.btn.done { border-color:var(--bracken); color:var(--bracken); }
.code-wrap { overflow-x:auto; background:var(--code-bg); border:1px solid var(--code-edge); border-radius:3px; }
pre.code { margin:0; padding:15px 18px; font-family:var(--mono); font-size:.82rem; line-height:1.55; }
pre.code b { color:var(--t-kw); font-weight:700; }
.t-kw { color:var(--t-kw); font-weight:700; } .t-fn { color:var(--t-fn); } .t-var { color:var(--t-var); } .t-string { color:var(--t-str); }
.t-iri { color:var(--t-iri); } .t-pname { color:var(--t-pname); } .t-comment { color:var(--t-com); font-style:italic; } .t-num { color:var(--t-num); } .t-annot { color:var(--t-annot); font-weight:700; }
.mech { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.05fr); gap:26px; margin-top:20px; align-items:start; }
.mech h4, .learn h4, .report h4, h4.q { font-family:var(--sans); font-size:.74rem; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3); margin:0 0 8px; }
.mech-prose p { margin:0 0 10px; color:var(--ink-2); font-size:.95rem; }
pre.diagram { margin:0; padding:14px 16px; background:var(--paper-2); border:1px solid var(--rule); border-radius:3px; font-family:var(--mono); font-size:.76rem; line-height:1.45; overflow-x:auto; color:var(--ink-2); }
.learn { margin-top:18px; max-width:var(--maxw); }
.learn ul { margin:0; padding-left:20px; color:var(--ink-2); font-size:.95rem; }
.learn li { margin-bottom:6px; }
.learn h4 { margin-top:14px; }
.learn p { color:var(--ink-2); font-size:.95rem; margin:0 0 8px; }
.report { margin-top:18px; }
.headline { font-size:.92rem; color:var(--ink-2); margin:0 0 6px; }
.verdict { font-weight:700; } .verdict.conforms { color:var(--bracken); } .verdict.fails { color:var(--route); }
.results-note { font-size:.86rem; color:var(--ink-3); margin:4px 0; }
tr.sev-violation td:first-child { color:var(--route); font-weight:700; }
tr.sev-warning td:first-child { color:var(--amber); font-weight:700; }
tr.sev-info td:first-child { color:var(--bracken); font-weight:700; }
.report.err .results-note { color:var(--route); font-family:var(--mono); }
.query { margin:10px 0; }
.qh { display:flex; justify-content:space-between; align-items:center; font-size:.86rem; color:var(--ink-2); margin:0 0 6px; }
.qh em { color:var(--ink-3); }
.specline { font-size:.78rem; color:var(--ink-3); margin:16px 0 0; }
ul.specs { display:inline; padding:0; margin:0; }
ul.specs li { display:inline; } ul.specs li + li::before { content:" · "; }
.ref .module-head { border-top-color:var(--ink-3); }
td.st-runs { color:var(--bracken); font-weight:700; } td.st-partial { color:var(--amber); font-weight:700; } td.st-error { color:var(--ink-2); font-weight:700; } td.st-silent { color:var(--route); font-weight:700; }
ul.reading { max-width:var(--maxw); color:var(--ink-2); font-size:.92rem; }
ul.reading li { margin-bottom:8px; }
footer { padding:40px; color:var(--ink-3); font-size:.8rem; border-top:1px solid var(--rule); margin-top:40px; }
@media (max-width: 900px) { .shell { grid-template-columns:1fr; } .rail { position:static; height:auto; border-right:none; border-bottom:1px solid var(--rule); }
  .mech { grid-template-columns:1fr; } .hero, .intro, .module, footer { padding-left:18px; padding-right:18px; } }
"""

JS = """
document.addEventListener('click', function (ev) {
  var b = ev.target.closest('button[data-copy]'); if (!b) return;
  var pre = document.getElementById('code-' + b.getAttribute('data-copy')); if (!pre) return;
  var head = pre.getAttribute('data-head') || '';
  var text = head + pre.textContent;
  function done() { var old = b.textContent; b.textContent = 'Copied'; b.classList.add('done'); setTimeout(function () { b.textContent = old; b.classList.remove('done'); }, 1400); }
  if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(done); }
  else { var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); done(); } catch (e) {} document.body.removeChild(ta); }
});
"""


def main() -> None:
    results = {}
    for p in (BUILD / "results").glob("s*.json"):
        results[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    by_module: dict[str, list] = {}
    for l in CATALOGUE:
        by_module.setdefault(l.module, []).append(l)
    for lessons in by_module.values():
        lessons.sort(key=lambda l: l.sort_key)

    n_faults = sum(1 for line in (ROOT / "data" / "faults.ttl").read_text(encoding="utf-8").splitlines() if line.startswith("# F")) \
        + sum(1 for line in (ROOT / "data" / "faults-1.2.ttl").read_text(encoding="utf-8").splitlines() if line.startswith("# F"))
    n_terms = sum(len(items) for _, items in features.TERMS)

    rail = ['<a href="#m00"><span class="n">00</span><span>The lab</span><span class="c"></span></a>']
    for module, lessons in by_module.items():
        num = module.split("-")[0]
        rail.append(f'<a href="#m{num}"><span class="n">{num}</span><span>{E(MODULE_INFO[module][0])}</span><span class="c">{lessons[0].sid}–{lessons[-1].sid}</span></a>')
    for anchor, label in (("faults", "The faults"), ("engine", "What the engine does"), ("features", "Every term"), ("standards", "The standards")):
        rail.append(f'<a href="#{anchor}"><span class="n">—</span><span>{label}</span><span class="c"></span></a>')

    modules = "".join(module_html(m, ls, results) for m, ls in by_module.items())

    # The copy heads: the four-line comment a learner gets with the shapes.
    heads = "".join(f'<script type="application/json" id="head-{l.sid}">{json.dumps(l.copy_text[:l.copy_text.index(chr(10)+chr(10))+2])}</script>' for l in CATALOGUE)

    logo = ""
    logo_path = ROOT / "assets" / "semantechs-logo.png"
    if logo_path.exists():
        import base64
        logo = f'<img class="logo" alt="Semantechs" src="data:image/png;base64,{base64.b64encode(logo_path.read_bytes()).decode()}">'

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Bookshop Trail — SHACL</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=Atkinson+Hyperlegible:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="shell">
<nav class="rail">
  <p class="brand">The Bookshop Trail <em>SHACL</em></p>
  <p class="tagline">A Semantechs teaching resource</p>
  <ol>{"".join(f"<li>{a}</li>" for a in rail)}</ol>
  <p class="railnote">The companion to <a href="{SPARQL_REPO}">the SPARQL course</a>: same data, same editor, the other way of asking it questions.</p>
</nav>
<main>
<header class="hero">
  {logo}
  <p class="eyebrow">A Semantechs teaching resource</p>
  <h1>The Bookshop Trail <small>a SHACL course</small></h1>
  <p class="standfirst">Seventy shapes graphs that take a beginner from <strong>sh:minCount 1</strong> to SPARQL constraints, custom
  constraint components, SHACL-AF rules and the parts of SHACL 1.2 that run today, against the SPARQL course's dataset and in the
  same browser editor. Every lesson has been run through the engine, and the report it produced is printed beside it.</p>
  <div class="facts">
    <div class="fact"><b>{len(CATALOGUE)}</b><span>lessons</span></div>
    <div class="fact"><b>{len(by_module)}</b><span>modules</span></div>
    <div class="fact"><b>{n_faults}</b><span>numbered faults</span></div>
    <div class="fact"><b>{n_terms}</b><span>SHACL terms shown</span></div>
    <div class="fact"><b>1</b><span>engine, in the browser</span></div>
  </div>
</header>

<section class="intro">
  <h2>Start here</h2>
  <p>Open the editor at <a href="{EDITOR_BASE}">semantechs.co.uk/turtle-editor-viewer</a>, or press <strong>Open in the editor</strong>
  on lesson <a href="#s01">s01</a> below: the data arrives in one tab and the shapes in another, already selected. Press
  <strong>Validate</strong>. Then read <a href="#m00">the lab</a> for what the panel shows, and start on module 01.</p>
  <p>Each lesson is one file: what it checks, how it works, a diagram, what to take away, and the shapes graph itself, with a link
  that loads it. Read the header before you press Validate; the report will make more sense.</p>
  <p>This course and <a href="{SPARQL_REPO}">the SPARQL course</a> are two halves of one package. They share the Bookshop Trail
  data and the editor, and lessons here point at the queries there when a query asks the same question a shape answers.
  A shape says what well-formed data looks like and reports where the data falls short; a query asks a question and returns a table.
  Both are worth knowing, and knowing one makes the other quicker.</p>
  <h2>A suggested order</h2>
  <p>00 → 01 → 02 (s10, s12, s14) → 03 (s20, s22) → 04 (s24, s27, s28) → <strong>05 in full</strong> → 06 (s39) → <strong>07 in full</strong>
  → 10 → 11. Module 08 needs the RDF 1.2 edition of the data and reads best after the SPARQL course's module 11; module 09 after
  its module 18; module 12 is reference.</p>
</section>

{lab_html()}
{modules}
{faults_html()}
{matrix_html()}
{features_html()}
{standards_html()}

<footer>
  <p>The Bookshop Trail, SHACL. MIT licence; copyright © 2026 Peter Winstanley. The Semantechs name and mark are excluded from the licence.
  Everything except the geography is fiction. Source and files: <a href="{REPO}">{REPO}</a>.</p>
</footer>
</main>
</div>
{heads}
<script>
(function () {{
  document.querySelectorAll('script[id^="head-"]').forEach(function (s) {{
    var pre = document.getElementById('code-' + s.id.slice(5)); if (pre) pre.setAttribute('data-head', JSON.parse(s.textContent));
  }});
}})();
{JS}
</script>
</body>
</html>"""
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote docs/index.html ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
