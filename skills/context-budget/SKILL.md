---
name: context-budget
description: Use when context feels heavy or you've added skills, agents, MCP servers, or memory and want a token-consumption audit of the whole setup with a prioritized trim list.
---

# context-budget

## Overview

Audit what's eating my Claude Code context — skills, MCP servers, the CLAUDE.md chain, and
my growing memory — and produce a prioritized list of what to trim. The point is keeping
the **whole setup** lean, not just the pack. This is skill #11, a conscious break of the
10-cap, justified by token economy being a recurring concern.

## When to use

- Context feels heavy / output quality slips, or `/context` shows a big always-on chunk.
- I've added skills, agents, or MCP servers, or `MEMORY.md` keeps growing.
- Before adding more — to know if there's headroom.

## The key model: always-on vs on-demand

- **Always loaded** (every turn): skill `description` lines, MCP tool schemas, the CLAUDE.md
  chain, and **`MEMORY.md`** (the memory index). This is the real budget — trim here first.
- **On-demand** (only when invoked): a skill's SKILL.md body, an agent's prompt. Cheap — a
  long body costs nothing until it runs, so don't optimize bodies.

## How it works

### 1. Inventory

- **Skills:** `make details` (or `claude plugin details <plugin>`) for the pack's projected
  token cost; note each `description` length (always-on).
- **MCP servers:** count servers and tools (~500 tokens of schema per tool, always-on). Flag
  servers with many tools, or that just wrap a CLI I already have (`gh`, `git`, `supabase`).
- **CLAUDE.md + memory:** size of the CLAUDE.md chain and `MEMORY.md` + `memory/*.md`. The
  memory index is always-on, so its growth is a direct context tax.
- **Agents:** description length (loads on every spawn) and body size.

### 2. Classify each component

- **Always needed** → keep.
- **Sometimes needed** (domain-specific, rarely triggered) → lazy-load / disable until used.
- **Rarely needed / redundant / overlapping** → remove.

### 3. Detect the usual bloat

- Skill/agent `description` over ~30 words (an always-on tax on every turn).
- MCP over-subscription (tools I never call, or CLI-wrapper servers).
- `MEMORY.md` entries that are stale, duplicated, or no longer true → prune them.
- CLAUDE.md verbosity that should be a rule or a memory instead.

### 4. Report

Total always-on overhead, a breakdown by component (skills / MCP / CLAUDE.md / memory /
agents), the headroom left, and a **prioritized trim list — biggest always-on saving first**.

## Output

A short report plus the top 3 trims by always-on tokens saved. Act on the always-on items
first; on-demand bodies are not the problem.
