---
name: postmortem
description: Use when capturing an important bug or production failure — record the incident, root cause, fix, and lesson as an archivable markdown document.
---

# postmortem

## Overview

After an important bug or failure, capture what happened and why so the same class of
problem can't quietly recur. Blameless: the target is the system and the gap, not who
typed it. The output is one archivable markdown file.

## When to use

- A production failure, data issue, broken release, or a bug that cost real time.
- NOT every small hiccup — a typo fixed in 30 seconds doesn't earn a postmortem.

## Steps

1. **Find the real root cause first.** Use `superpowers:systematic-debugging` — don't
   document the symptom or the first plausible guess. The postmortem is only as good as
   the cause it names.
2. **Fill the template from evidence, not memory:** the actual error output, the
   commit/PR that fixed it, and the timeline if order mattered.
3. **Make prevention concrete.** "Be more careful" is not prevention. Name the specific
   thing that would have caught or blocked it: a test, a guard/validation, a CI gate, a
   `CLAUDE.md` note, or a durable memory.
4. **Save it outside the repo:** `../<repo>-notes/postmortems/YYYY-MM-DD-<slug>.md`.
   Internal docs are never committed (see `standards`) — archive it, don't ship it.

## Template

```markdown
# Postmortem: <short title>

- **Date:** YYYY-MM-DD
- **Severity:** low | medium | high
- **Impact:** who/what was affected, for how long

## Incident

<one paragraph: the observable failure>

## Timeline (only if order mattered)

- HH:MM — …

## Root cause

<the underlying cause found via systematic-debugging — the "why", not the symptom>

## Fix

<what changed; commit / PR reference>

## Prevention

<the specific thing that stops this class of bug recurring>
```
