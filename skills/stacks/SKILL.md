---
name: stacks
description: Use when building or maintaining a project in one of my non-default stacks — Flipper Zero FAP in C now, Django / Flask / FastAPI coming — for its architecture, build, test, formatting and release conventions. Routes to references/<stack>/. The web stack (TS / Supabase / PWA) is the pack's implicit default and has no entry here.
---

# stacks

## Overview

One home for the **per-stack structure & build conventions** of stacks that fall **outside
the pack's implicit default** (the web stack — TS/Supabase/PWA — which every other skill
already assumes). One skill, many stacks: each stack is a folder under `references/`, so
breadth grows without adding skills or spending a trigger per stack.

## When to use

- Starting or extending a project in a stack listed below — read that stack's
  `references/<stack>/` files for its layering, build, tests, formatting and release flow.
- For a **failure** in one of these stacks → `eskills:stack-gotchas` (it carries the
  diagnose-and-recover recipes).

## How it's organized

`references/<stack>/` holds the concrete, copy-ready conventions for that stack, each
pattern traced to a real repo. Read the folder for the stack you're in.

| Stack                | Folder                | Status                                                      |
| -------------------- | --------------------- | ----------------------------------------------------------- |
| Flipper Zero FAP (C) | `references/flipper/` | architecture · build-and-test · formatting · release-please |
| Django               | `references/django/`  | _planned_                                                   |
| Flask                | `references/flask/`   | _planned_                                                   |
| FastAPI              | `references/fastapi/` | _planned_                                                   |

Adding a stack = a new `references/<stack>/` folder (and a row above). **No new skill, no
cap change** — that's the point.

## What this skill is NOT

- It does **not** restate the conventions floor — commits, test philosophy, IDs, repo
  hygiene, branches/PRs live in **`standards`** (stack-agnostic).
- It does **not** hold failure recipes — those are in **`stack-gotchas`**.
- It is **not** an orchestrator — building a feature end-to-end is **`task-flow`**.
- The **web stack has no folder** here: it's the implicit default baked into the whole pack.
  A stack earns a folder only when it's genuinely outside that default (embedded, native
  mobile, a non-JS backend…).
