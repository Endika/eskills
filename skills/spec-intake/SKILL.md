---
name: spec-intake
description: Use when starting from a task described in Jira, Linear, a URL, or free text and you need it normalized into a spec (objective, acceptance criteria, constraints, definition of done) before planning.
---

# spec-intake

## Overview

Turn a task from anywhere — a Jira/Linear ticket, a URL, a Slack message, a vague
sentence — into one normalized spec, before any planning. Usable standalone, and the
entry point of `eskills:task-flow` Phase 1.

## Steps

1. **Pull the source.** Read the ticket/URL/message. Quote the real wording; don't
   paraphrase away a constraint.
2. **Resolve ambiguity now.** If the objective or a success condition is unclear, ask the
   few questions that change the work — before writing the spec, not after.
3. **Normalize** into the shape below.
4. **Classify** for the flow (this is what `task-flow` consumes next).

## Output shape

```markdown
## Objective

<one or two sentences: the outcome, in the user's terms>

## Acceptance criteria

- [ ] <observable, checkable condition>
- [ ] …

## Constraints

- <tech, data, deadline, compatibility, non-goals>

## Definition of done

- <tests, docs, review, deploy — what "finished" requires>

## Classification

- Project shape: greenfield | brownfield
- Hard-tech challenge: yes (algorithm / performance) | no
- UI surface: existing (built within the current design system, new pages included) |
  improve (refine the current design) | new (no design system yet, or a redesign) | none
```

## Notes

- **Acceptance criteria must be observable** — "X is faster" is not a criterion; "p95 <
  200ms on N=10k" is.
- The **classification** drives `task-flow`: brownfield → `feature-dev:code-explorer`;
  hard-tech → the SPIKE sub-phase; UI surface `improve` or `new` → the DESIGN sub-phase.
- **Ask the UI surface, don't infer it,** unless the request already says it ("new app",
  "redesign", "add page X"). Getting it wrong runs `shape` over a design system that
  already exists, so the question goes out in step 2 with the other ambiguities.
- Keep the spec outside the repo (see `eskills:standards`) — it's an internal doc.
