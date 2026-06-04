---
name: task-flow
description: Use when implementing a feature or multi-step task end-to-end — orchestrates spec intake, adaptive analysis, planning, and a per-task implement/verify/review loop over superpowers, with a single human gate after the plan; includes a human-pulled respec gate to correct the spec mid-build.
---

# task-flow

## Overview

My end-to-end flow for building a feature with trust. It is a **thin orchestrator** over
`superpowers` — it sequences existing skills, it does not re-implement them. One human
gate (after the plan); everything else runs automatically with per-task gates. The
keystone is an adversarial verifier that re-earns "done" in fresh context.

## When to use

- Implementing a feature or non-trivial task from a spec, ticket, or request.
- NOT for a one-line fix or a quick question — the ceremony isn't worth it there.

## Phase 1 — understand & plan (auto, adaptive)

1. **`eskills:spec-intake`** — normalize the task into objective, acceptance criteria,
   constraints, definition of done. It also classifies **greenfield vs brownfield** and
   flags a **hard-tech challenge** (complex algorithm / performance bottleneck).
2. **If brownfield →** `feature-dev:code-explorer` to understand the existing code before
   planning.
3. **If hard-tech challenge → SPIKE sub-phase:** explore 2–3 approaches, benchmark
   candidates if needed (apply `eskills:perf-bar`), and pick the approach **before**
   committing the plan. Use `deep-research` (if available) / `feature-dev:code-architect`
   as needed.
4. **`superpowers:brainstorming`** — refine intent and trade-offs.
5. **`superpowers:writing-plans`** — produce the plan, enriched with the template below.
6. Emit the **PLAN + acceptance criteria + subagent design + chosen-approach rationale**.

### Plan template (integrated — not a separate skill)

Each task in the plan carries:

- exact files to create/modify;
- the change, concretely (no "add error handling" placeholders);
- **acceptance criteria** — observable and checkable;
- **validation commands** — the exact lint/typecheck/test commands that prove it.

## 🚦 GATE — the only human stop

I review the plan + acceptance criteria and approve. Nothing in Phase 2 starts until I do.

**Compact here.** This gate is the prime context boundary: once the plan is approved,
`/compact` to drop the exploration/brainstorming context and carry only the plan into
Phase 2. Do the same after each milestone or before an unrelated task — strategic
compaction at logical boundaries beats arbitrary auto-compaction mid-task.

## Phase 2 — build (auto), per task via `superpowers:subagent-driven-development`

For each task, in order:

1. **Implementer** — implements, tests, commits, self-reviews. Reports `DONE` /
   `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`.
2. **Spec reviewer** (independent) — does the code match the spec?
3. **Adversarial verifier** (fresh context — my reinforcement). Does **not** trust the
   implementer's self-report. Re-runs the gates itself — **lint + typecheck + tests**, per
   `eskills:standards` — and checks real output against the acceptance criteria. It
   **defaults to NOT done, and marks done only when it has itself seen lint pass, typecheck
   pass, tests pass, and the output meet every acceptance criterion.**
4. **Quality reviewer** — applies only the lenses that apply to this task:
   `eskills:ux-bar` / `eskills:security-bar` / `eskills:arch-bar` / `eskills:perf-bar`.
5. All green → mark task complete → next task.

Model selection: cheap model for mechanical tasks, capable model for review/judgment.

Test discipline comes from `eskills:standards` (integration tests, in-memory fakes, no
mocks) — intentionally, not from `superpowers:test-driven-development`; my test philosophy
differs.

## Phase 2 — respec gate (human-pulled)

A human-pulled escape hatch, available throughout Phase 2. Not a sequential step — an
interrupt I fire when, watching the changes go by, I realize the **spec itself missed
something** (a component that should be reused instead of rebuilt, scope to drop, a plan
assumption that's false). There is no automatic trigger: only I pull this cord.

When pulled (I say something like "stop, the spec is wrong about…"):

1. **Pause** the per-task loop — do not start the next task.
2. **Capture the correction conversationally** — I state in natural language what was
   missed: drop scope ("don't build/use this"), redirect ("reuse object/component Y"), or
   fix a plan assumption.
3. **Single gate, two decisions** — show me what is already built, then ask:
   - **Altura:** edit spec and continue · re-plan affected tasks · re-plan everything.
   - **Fate of built work:** discard (git reset / abandon) · keep and adapt.
4. **Re-spec** via `eskills:spec-intake` — update **only** the requirements I asked to
   change. No trail; the "why" lives in the conversation, not the document.
5. **Re-plan** the affected tasks via `superpowers:writing-plans` from the corrected spec.
6. **Re-launch** Phase 2 over the affected tasks. The adversarial verifier is unchanged.

**Compact after a discard.** A re-spec that discards work is a context boundary like the
plan gate — `/compact` to drop the abandoned-work context before re-launching.

## Phase 3 — finish (auto)

- `superpowers:verification-before-completion` + a final review pass.
- `superpowers:finishing-a-development-branch`.
- PR / release in my flow: Conventional Commits (`eskills:standards`), release-please.

## Why the adversarial verifier

The known failure mode is an agent claiming tests pass when they don't. The spec and
quality reviewers read the diff and can inherit a false "tests passing" claim. The
adversarial verifier re-runs the gates in fresh context and defaults to "not done",
turning "the agent says it's done" into "it's done, and here is the evidence a second
agent produced while trying to prove otherwise." That is trust, made into a gate.
