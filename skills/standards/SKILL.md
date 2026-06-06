---
name: standards
description: Use when about to commit, write or design tests, choose an ID type, or push — enforces my non-negotiable conventions for commits, test design, repo hygiene, IDs, and pre-push checks.
---

# standards

## Overview

My non-negotiable conventions — the floor every other skill stands on. When one
applies, follow it exactly; it overrides generic defaults. Flag a real conflict
once, then proceed (don't rehash).

## Commits

- **One line only:** `type(scope): subject` — English, imperative. **No body** unless I explicitly ask. Detail belongs in the PR description, not the commit.
- **No trailers:** never add `Co-Authored-By:`, and never add a `🤖 Generated with Claude Code` footer to commits or PR bodies.
- Pick the Conventional Commit type honestly: `feat`/`fix` cut releases; `chore`/`docs`/`refactor`/`test` don't. Scaffolding is `chore`, not `feat`.
- In release-please + auto-merge repos the amend window is ~seconds. Get the one-line message right the first time.
- **Bots are exempt:** dependabot / release-please author their own commits with structured multi-line bodies (machine-readable footers, changelogs). That's expected — the one-line rule governs commits I write, not bot commits.
- **Integrate PRs by rebase** (squash only for a messy WIP branch) — **never a merge commit**. `main` stays strictly linear; release-please keeps its release PR rebased on `main` automatically.

## Branches

- **Never commit straight to the default branch.** Feature work goes on a short-lived branch (`feat/…`, `fix/…`, `chore/…`), pushed and opened as a **PR** — even in a solo repo.
- One branch = one purpose; keep it small. Integrate by **rebase** (see Commits), then delete the branch. `main` stays strictly linear.
- **Bots are exempt:** release-please and dependabot manage their own branches/PRs.

## Pull Requests

- **Title:** same `type(scope): subject` as a commit — English, imperative, one line.
- **Body — clear and simple to read, by sections** (the structure lives here, not in a repo template file): **What & why** (1-2 sentences) → **Changes** (short bullets) → **Testing** (commands run + result) → **Notes** (risks / screenshots / follow-ups). **Drop any section that doesn't apply** — scannable, no filler, no checklist boilerplate.
- **No trailers, no footer:** never a `🤖 Generated with Claude Code` footer and never `Co-Authored-By:` — same rule as commits.
- Link the issue with `Closes #N` when there is one.

## Tests

Fewer, higher-signal tests over a high count. Before writing one, ask: _"If I delete
this, what real bug could ship undetected?"_ If the answer is "none / TypeScript
catches it", don't write it.

- **No mock-only tests.** Don't `vi.fn()`/spy a port and assert it was called — that tests wiring, not behavior. Build a small in-memory fake of the port and assert the observable outcome.
- **Prefer integration-flavored tests:** one test exercising use case → service → repository (memory repo) beats three mock-at-every-seam unit tests.
- **Skip trivial passthroughs:** a use case that just forwards to an already-tested service needs no test of its own.
- **A VO getter is not a test.** Test the behavior the value object enforces (validation, equality, immutability), not the generated property.
- **Coverage % is not a target.** 80% with rich behavioral assertions beats 100% of trivial ones.

## Repo hygiene

- **Never `git add -A` / `git add .` / `git add --all`.** Inspect `git status --short` and stage explicit paths.
- Repo holds **only project code + README** (+ LICENSE/config). Internal docs, specs, plans and checklists live **outside the repo** in a sibling `../<repo>-notes/` dir — never committed, and **never `.gitignore`'d either** (gitignoring a doc is itself the violation; just don't stage it).
- **Skill defaults are wrong here — override them.** `brainstorming`, `writing-plans` and `task-flow` default to saving specs/plans at `docs/superpowers/...` _inside_ the repo and then committing them. Do NOT follow that. When bootstrapping a project, create `../<repo>-notes/` as a sibling of the repo **before the first spec/plan write**, and target it from that very first Write. The first time a spec lands in `docs/` inside the repo, the rule is already broken.
- If an internal doc reaches the repo anyway: `git rm` it (or rewrite history with the user's OK if already pushed) and move it to `../<repo>-notes/`. Never "fix" it by adding the path to `.gitignore`.
- Code, identifiers, log strings, file/var names, UI strings → **English**. Comments minimal — only the non-obvious "why".

## IDs

- Default to **UUID v7** (`uuidv7`, RFC 9562) for any newly generated entity ID — no need to ask each time. The ~1 KB dependency is acceptable; time-ordering is worth it.
- No-flag exceptions: short URL-friendly slugs (not UUIDs at all). If a project already standardized on v4, follow it — don't refactor existing IDs unprompted.

## Before pushing

Run **all** the gates CI runs, as one batched call — not just tests:

> **lint + typecheck + tests**

- Prefer the project's single `verify`/`check` script if it exposes one. Passing CI is the floor, not a stretch goal.
- Non-negotiable whenever the task ends in a push (especially "súbelo para que aplique release") — lint failures gate releases too.

## Pushback discipline

Once I validate a decision ("OK, hazlo"), stop adding caveats or re-validation on the
same point. Group critical warnings once, up front. Push back again only for genuinely
new, un-flagged risks (security, data loss).
