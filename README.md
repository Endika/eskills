# eskills

A lean, trustworthy personal Claude Code skills pack. It encodes my own conventions
for detecting bugs, building features, testing, and shipping — and rides
[`superpowers`](https://github.com/obra/superpowers) rather than duplicating it.

The goal is **trust**: when I follow one of these skills, the result is what I
expect, with evidence — not a hopeful claim. This is the deliberate opposite of a
maximalist catalog; every skill earns its place.

## Requires

- **[`superpowers`](https://github.com/obra/superpowers)** — these skills invoke it
  by name (brainstorming, writing-plans, subagent-driven-development, systematic-debugging,
  verification-before-completion, finishing-a-development-branch). It is the **only**
  required runtime dependency. Nothing else is installed.

> Optional: `ux-bar` and `security-bar` layer on the `frontend-design` and
> `security-review` skills respectively, and `task-flow`'s SPIKE step can use
> `deep-research` / `feature-dev` — each is used only if present, none are required.

## Install

**Stable (any environment):**

```bash
claude plugin marketplace add Endika/eskills
claude plugin install eskills@endika
```

You only ever receive stable releases: work-in-progress commits on `main` share the
same `version` until release-please bumps it.

**Dev (load HEAD directly):**

```bash
claude --plugin-dir ~/eskills      # or: make dev
```

## Skills

Invoked as `eskills:<name>`.

### Core

| Skill            | Use when                                                                                                                                                                                                  |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `standards`      | About to commit, write/design tests, choose an ID type, or push — enforces my conventions floor.                                                                                                          |
| `task-flow`      | Implementing a feature end-to-end — orchestrates spec → plan → per-task implement/verify/review over superpowers, with a single human gate plus a human-pulled respec gate to correct the spec mid-build. |
| `spec-intake`    | Turning a task (Jira/Linear/URL/free text) into a normalized spec before planning.                                                                                                                        |
| `gen-uml`        | Generating a Mermaid diagram (architecture/flow/sequence) from existing code.                                                                                                                             |
| `postmortem`     | After an important bug/failure — capture, root cause, fix, lesson as an archivable doc.                                                                                                                   |
| `stack-gotchas`  | Hitting a known failure in my stack — release-please, GitHub Pages, Supabase — for a direct diagnose-and-recover recipe.                                                                                  |
| `context-budget` | Context feels heavy / added skills, MCP, or memory — audits whole-setup token consumption with a prioritized trim list.                                                                                   |

### Quality lenses

Short rubrics in my voice — usable standalone on a diff, and invoked by `task-flow`'s
review stage. Hard cap of **4**.

| Lens           | Use when                                                                                       |
| -------------- | ---------------------------------------------------------------------------------------------- |
| `ux-bar`       | Building/reviewing UI — my design-system and semantic-color rules on top of `frontend-design`. |
| `security-bar` | Reviewing for security — my checklist on top of `security-review`.                             |
| `arch-bar`     | Judging whether an architecture fits its scale — catches over- and under-engineering.          |
| `perf-bar`     | Assessing performance/algorithmic soundness — Big-O, N+1, egress, benchmarks.                  |

## How it relates to upstream

One rule shapes the whole repo:

> **Copy/adapt** small, stable ideas where I want _my_ version.
> **Reference** large, living engines where I want to ride their updates.

So `superpowers` is referenced (invoked by name); a few small patterns are adapted and
rewritten. ECC is never installed — it was mined for ideas only.

## Development

```bash
make            # list targets
make list       # skills + their trigger descriptions
make check      # validate frontmatter, JSON, and design caps (run before pushing)
make new name=<kebab>   # scaffold a new skill
make details    # component inventory + token cost (anti-bloat watch)
make tag        # create the release tag (validates plugin.json vs marketplace)
```

Single `main`, linear history, no feature branches. Releases via
[release-please](https://github.com/googleapis/release-please) (Conventional Commits →
version bump + CHANGELOG + tag).

## License

MIT © Endika
