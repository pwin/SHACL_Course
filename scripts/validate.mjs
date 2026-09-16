#!/usr/bin/env node
// Validate a data file against a shapes file with the SHACL engine the Turtle
// Editor Viewer runs -- the same WebAssembly build, on your own machine.
//
//   node scripts/validate.mjs --data data/bookshop-trail-1.1.ttl \
//                             --shapes shapes/01-first-shapes/s01-every-bookshop-has-a-name.ttl
//   node scripts/validate.mjs --data ... --shapes ... --inference rules
//   node scripts/validate.mjs --data ... --shapes ... --format turtle > report.ttl
//   node scripts/validate.mjs --batch build/jobs.json --out build/results.json
//
// --inference  none (default) | rdfs | rules | rules-iterated
// --format     human (default) | json | turtle
//
// Before compiling, nested `sh:property [ ... ]` shapes are given IRIs so a
// result can name them ("bt:BookshopShape > property 2") and compound paths
// are rendered as expressions. The editor does both, so a report here reads
// the same as the report in the browser.
//
// Nothing is fetched. Both files are read from disk, and the engine refuses
// SERVICE inside a shapes graph.

import { createRequire } from 'node:module'
import { readFileSync, writeFileSync } from 'node:fs'
import { basename } from 'node:path'

const require = createRequire(import.meta.url)
const { Validator } = require('shacl-wasm-node')
const { DataFactory, Parser, Writer } = require('n3')

const SH = 'http://www.w3.org/ns/shacl#'
const RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
const BASE = 'http://example.org/'
const SHAPE_BASE = 'urn:shacl-course:shape:'

const PREFIXES = {
  bt: 'https://example.org/bookshop-trail/',
  bs: 'https://example.org/bookshop-trail/schema#',
  sh: SH,
  rdf: RDF,
  rdfs: 'http://www.w3.org/2000/01/rdf-schema#',
  owl: 'http://www.w3.org/2002/07/owl#',
  xsd: 'http://www.w3.org/2001/XMLSchema#',
  skos: 'http://www.w3.org/2004/02/skos/core#',
  dct: 'http://purl.org/dc/terms/',
  geo: 'http://www.opengis.net/ont/geosparql#',
  wgs84: 'http://www.w3.org/2003/01/geo/wgs84_pos#',
  prov: 'http://www.w3.org/ns/prov#',
  schema: 'https://schema.org/',
}

// Longest namespace first: bt: is a prefix of bs:, and a shop's schema
// property must not come out as bt:schema#founded.
const NAMESPACES = Object.entries(PREFIXES).sort((a, b) => b[1].length - a[1].length)

function shrink(iri) {
  if (typeof iri !== 'string') return iri
  for (const [p, ns] of NAMESPACES) {
    if (iri.startsWith(ns)) return p + ':' + iri.slice(ns.length)
  }
  return iri
}

// ---------------------------------------------------------------- arguments

function parseArgs(argv) {
  const out = { inference: 'none', format: 'human' }
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a.startsWith('--')) out[a.slice(2)] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true
  }
  return out
}

// ---------------------------------------------------------------- parsing

function parseTurtle(text) {
  let anonymous = 0
  const factory = { ...DataFactory, blankNode: (name) => DataFactory.blankNode(name || `anon-${anonymous++}`) }
  const parser = new Parser({ baseIRI: BASE, blankNodePrefix: '', factory })
  return parser.parse(text)
}

function toNTriples(quads) {
  const writer = new Writer({ format: 'N-Triples' })
  writer.addQuads(quads)
  let out = ''
  writer.end((error, result) => { if (error) throw error; out = result })
  return out
}

// ---------------------------------------------------------------- paths

function renderPath(node, bySubject, depth = 0) {
  if (node.termType === 'NamedNode') return shrink(node.value)
  if (depth > 20) return '…'
  const quads = bySubject.get(node.value) || []
  const get = (p) => quads.find(q => q.predicate.value === p)?.object
  if (get(RDF + 'first')) {
    const items = []
    let cur = node
    for (let i = 0; i < 50 && cur && cur.value !== RDF + 'nil'; i++) {
      const cq = bySubject.get(cur.value) || []
      const first = cq.find(q => q.predicate.value === RDF + 'first')?.object
      if (!first) break
      items.push(renderPath(first, bySubject, depth + 1))
      cur = cq.find(q => q.predicate.value === RDF + 'rest')?.object
    }
    return items.join(' / ')
  }
  const alt = get(SH + 'alternativePath')
  if (alt) return '(' + renderPath(alt, bySubject, depth + 1).split(' / ').join(' | ') + ')'
  const inv = get(SH + 'inversePath')
  if (inv) return '^' + wrap(renderPath(inv, bySubject, depth + 1))
  const zm = get(SH + 'zeroOrMorePath')
  if (zm) return wrap(renderPath(zm, bySubject, depth + 1)) + '*'
  const om = get(SH + 'oneOrMorePath')
  if (om) return wrap(renderPath(om, bySubject, depth + 1)) + '+'
  const zo = get(SH + 'zeroOrOnePath')
  if (zo) return wrap(renderPath(zo, bySubject, depth + 1)) + '?'
  return '_:' + node.value
}
const wrap = (s) => (/[ /|]/.test(s) ? '(' + s + ')' : s)

// ---------------------------------------------------------------- shapes

// Give every nested property shape an IRI, as the editor does, and remember
// a label for it and a rendering of any compound path.
function prepareShapes(quads) {
  const parentOf = new Map(), bySubject = new Map()
  for (const q of quads) {
    if (q.predicate.value === SH + 'property' && q.object.termType === 'BlankNode') parentOf.set(q.object.value, q.subject.value)
    const list = bySubject.get(q.subject.value)
    if (list) list.push(q); else bySubject.set(q.subject.value, [q])
  }
  const pathOf = new Map()
  for (const q of quads) if (q.predicate.value === SH + 'path' && q.object.termType === 'BlankNode') pathOf.set(q.subject.value, renderPath(q.object, bySubject))
  const namedAncestor = (node) => { let c = node; for (let i = 0; c !== undefined && i < 20; i++) { if (!parentOf.has(c)) return c; c = parentOf.get(c) } return node }
  const skolem = new Map(), labelByShape = new Map(), pathByShape = new Map(), countByParent = new Map()
  for (const blank of parentOf.keys()) {
    const parent = namedAncestor(blank)
    const n = (countByParent.get(parent) || 0) + 1
    countByParent.set(parent, n)
    const iri = SHAPE_BASE + (skolem.size + 1)
    skolem.set(blank, iri)
    labelByShape.set(iri, shrink(parent) + ' › property ' + n)
    if (pathOf.has(blank)) pathByShape.set(iri, pathOf.get(blank))
  }
  for (const [node, expr] of pathOf) if (!skolem.has(node)) pathByShape.set('_:' + node, expr)
  const rename = (t) => (t.termType === 'BlankNode' && skolem.has(t.value) ? DataFactory.namedNode(skolem.get(t.value)) : t)
  const renamed = quads.map(q => DataFactory.quad(rename(q.subject), q.predicate, rename(q.object), q.graph))
  return { text: toNTriples(renamed), labelByShape, pathByShape }
}

// ---------------------------------------------------------------- run

function fillMessage(message, focus, path, value) {
  if (!message || !message.includes('{')) return message || ''
  let out = message.replace(/\{[$?]this\}/g, () => focus)
  if (path !== null) out = out.replace(/\{[$?]path\}/g, () => path)
  if (value !== null) out = out.replace(/\{[$?]value\}/g, () => value)
  return out
}

function defaultMessage(component) {
  const local = component.slice(component.lastIndexOf('#') + 1).replace(/ConstraintComponent$/, '')
  return local ? `Does not satisfy sh:${local.charAt(0).toLowerCase()}${local.slice(1)}` : 'Does not conform'
}

const RANK = { Violation: 0, Warning: 1, Info: 2 }

function validate(dataText, shapesText, inference) {
  const shapes = prepareShapes(parseTurtle(shapesText))
  const data = toNTriples(parseTurtle(dataText))
  const validator = Validator.fromTurtle(shapes.text, BASE)
  try {
    const report = validator.validateTurtle(data, BASE, inference)
    try {
      const results = report.results.map(r => {
        const path = r.path == null ? null : (r.path.startsWith('_:') ? (shapes.pathByShape.get(r.sourceShape) || shapes.pathByShape.get(r.path) || r.path) : shrink(r.path))
        const value = r.value == null ? null : shrink(String(r.value))
        const focus = shrink(r.focusNode)
        const severity = r.severity.slice(SH.length)
        return {
          severity,
          focusNode: focus,
          path,
          value,
          message: fillMessage(r.message, focus, path, value) || defaultMessage(r.component),
          sourceShape: r.sourceShape == null ? null : (shapes.labelByShape.get(r.sourceShape) || shrink(r.sourceShape)),
          component: shrink(r.component),
        }
      })
      results.sort((a, b) => RANK[a.severity] - RANK[b.severity] || a.focusNode.localeCompare(b.focusNode) || (a.path || '').localeCompare(b.path || '') || (a.value || '').localeCompare(b.value || '') || a.message.localeCompare(b.message))
      const counts = { Violation: 0, Warning: 0, Info: 0 }
      for (const r of results) counts[r.severity] = (counts[r.severity] || 0) + 1
      return { conforms: report.conforms, inference, shapeCount: validator.shapeCount, counts, results, turtle: report.toTurtle() }
    } finally { report.free() }
  } finally { validator.free() }
}

function human(out, dataName, shapesName) {
  const c = out.counts
  const lines = []
  lines.push(`${out.conforms ? 'Conforms' : 'Does not conform'} -- ${c.Violation} violation${c.Violation === 1 ? '' : 's'}, ${c.Warning} warning${c.Warning === 1 ? '' : 's'}, ${c.Info} info; ${out.shapeCount} shapes; inference ${out.inference}`)
  lines.push(`data ${dataName}   shapes ${shapesName}`)
  if (out.results.length) {
    lines.push('')
    const w = (s, n) => (s || '').toString().padEnd(n).slice(0, n)
    lines.push(`${w('severity', 9)} ${w('focus node', 34)} ${w('path', 26)} ${w('value', 22)} message`)
    for (const r of out.results) lines.push(`${w(r.severity, 9)} ${w(r.focusNode, 34)} ${w(r.path, 26)} ${w(r.value, 22)} ${r.message}`)
  }
  return lines.join('\n')
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  if (args.batch) {
    const jobs = JSON.parse(readFileSync(args.batch, 'utf8'))
    const results = jobs.map(job => {
      try {
        const out = validate(readFileSync(job.data, 'utf8'), readFileSync(job.shapes, 'utf8'), job.inference || 'none')
        if (!args.turtle) delete out.turtle
        return { id: job.id, ok: true, ...out }
      } catch (e) {
        return { id: job.id, ok: false, error: String(e && e.message ? e.message : e) }
      }
    })
    const text = JSON.stringify(results, null, 1)
    if (args.out) writeFileSync(args.out, text); else process.stdout.write(text)
    return
  }
  if (!args.data || !args.shapes) {
    console.error('usage: node scripts/validate.mjs --data <file> --shapes <file> [--inference none|rdfs|rules|rules-iterated] [--format human|json|turtle]')
    process.exit(2)
  }
  const out = validate(readFileSync(args.data, 'utf8'), readFileSync(args.shapes, 'utf8'), args.inference)
  if (args.format === 'turtle') process.stdout.write(out.turtle)
  else if (args.format === 'json') { delete out.turtle; process.stdout.write(JSON.stringify(out, null, 1)) }
  else console.log(human(out, basename(args.data), basename(args.shapes)))
  process.exitCode = out.conforms ? 0 : 1
}

main()
