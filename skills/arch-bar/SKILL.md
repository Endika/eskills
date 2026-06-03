---
name: arch-bar
description: Use when judging whether a design's architecture fits its scale — catches both over-engineering and under-engineering, agnostic to SaaS, small monolith, or microservices.
---

# arch-bar

## Overview

My architecture bar: **the right structure for the problem, no premature complexity.**
Scale-agnostic — it judges fit, not fashion. Usable standalone on a design, and invoked by
the quality stage of `eskills:task-flow`. It deliberately looks **both** ways: complexity
that isn't earned, and simplicity that's about to hit a wall. Unlike the other lenses, this
one is standalone — it delegates to no upstream engine; the rubric below is the whole tool.

## Over-engineering — complexity that isn't earned

- Microservices, queues, event sourcing, or a plugin system for a tiny single-user tool.
- Abstractions with one implementation; layers that only forward calls.
- Generality "for the future" that YAGNI hasn't asked for.
- → Collapse it to the simplest thing that meets the actual acceptance criteria.

## Under-engineering — simplicity about to hit a wall

- A structure with a **known** scaling cliff: e.g. one growing JSON blob where a field
  causes quadratic growth and blows a real limit (see the egress scar in
  `eskills:perf-bar`).
- No boundary where one is clearly needed — domain logic fused into the UI or the DB row.
- Missing seam for the change that is _already_ on the roadmap.
- → Add exactly the one boundary that removes the wall; not a framework.

## How to judge

1. What's the real scale (users, data, write rate, team)? Size to **that**, not to a
   hypothetical.
2. For each piece of structure, ask: what breaks if I remove it? If "nothing soon", it's
   over-built. If "a known limit, soon", it's under-built.
3. Name the _one_ change that most improves fit. Prefer reversible, minimal moves (a
   boundary, a cap, a split) over rewrites.

## Output

Report `over` / `under` / `fits` with the specific piece and the single highest-leverage
change. YAGNI is the default, but never at the cost of a wall you can already see.
