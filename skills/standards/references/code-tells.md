# Tells of generated code

The watchlist behind "comments only for the non-obvious why" and the review lenses, for
code rather than prose (prose is `comms/references/ai-tells.md`).

**The goal is not evading a detector.** Zero-shot detectors on code are no more reliable
than on text, and the research that measures generated code finds the same defect
categories as in human code, only more of them. Every tell below is here because it costs
a reader something — a line to skip, an error nobody will see, a helper that already
existed — not because it looks machine-made.

## Comments

- **Narrating the code**: `# increment the counter` over `i += 1`, a docstring that repeats
  the signature (`x (int): the x value`) on a two-line function.
- **Step banners**: `# Step 1: load the data`, `# Step 2: …` — the function body is the
  steps; if it needs signposts, it wants splitting.
- **Talking to the reader**: "In a real application you would…", "Replace with your…",
  "You may want to adjust this". The reader is the maintainer, and there is no other
  application.
- **Narrating the change instead of the code**: "Fixed the bug", "Now uses the new API",
  "Updated to handle X". That belongs in the commit; in the file it goes stale on the next
  edit.

## Error handling — both directions

- **Swallowed or decorative handling inside**: `except: pass`, a `try/except Exception`
  around everything that logs and carries on, `None` checks on values that cannot be
  `None`, re-validating arguments the type already guarantees.
- **Fallbacks that hide a failure**: returning `[]`, `0` or a default when something went
  wrong. The caller now believes there was nothing — the silent-truncation bug.
- **…and missing handling at the edges.** The same code that wraps the interior in `try`
  often skips validation where input actually arrives — a request body, a file, a length
  before a copy. It is the main security gap measured in generated C, and error-handling
  gaps run at about twice the human rate in PR review.

## Structure

- **Rebuilding instead of reusing**: a new helper, parser or constant next to one the repo
  already has, or an idiom that ignores the surrounding file. Duplicated blocks are the
  best-measured trend of assisted code; the cause is not having read what is there.
- **One enormous function or class** doing what the codebase would split — or the reverse,
  files split apart with no cohesion between what sits in each.
- **Speculative flexibility**: an interface with one implementation, a factory for one
  product, options nobody asked for, "for extensibility". `arch-bar` owns the verdict.
- **Excess I/O**: re-reading a file, re-querying inside a loop, a network call per item.
  The largest multiplier in PR review, and `perf-bar`'s territory.
- **Residue**: unused imports and parameters, names like `processed_user_data_result`,
  logging at every step, emoji in `print`/log output (`✅ Done!`).

## Placeholders

`your-api-key-here`, `YOUR_TOKEN_HERE`, `# TODO: implement this`, `example.com` in code
that ships. Each one is a feature that looks finished and isn't.

## Tests

- Asserting that a mock was called (already banned in `standards` → Tests).
- A test that restates the implementation line by line, so it fails when the code is
  rewritten, never when it is wrong.
- Assertions that cannot fail, names like `test_should_work_correctly`, and a test edited
  until it passes instead of the code fixed until it does.

## Dependencies that don't exist

A generated import or install line can name a package that was never published: 5.2% of
suggestions from commercial models and 21.7% from open ones in 2025, 4.6–6.1% across the
2026 frontier cohort. Several models invent the _same_ names, which is what makes
registering them an attack (slopsquatting). Before adding a dependency a model proposed,
confirm it exists, is the one you meant, and has a history.

## What the hook checks

`hooks/code-tells.py` runs on `git commit` and scans only the lines being added, outside
Markdown and plain text. It matches the mechanical subset — reader-directed comments,
placeholders, step banners, emoji in log calls, and a Python `except: pass` — and warns
without blocking. Everything else above needs judgment and stays a review item.

Measured on 2026-09-24 against real history, lines added per commit: **0 of 1,301** commits
across ten of my repos, and **3 of 1,800** across mypy, pact-python, go-jsonnet, kapacitor
and Momentum firmware. Of those three, one is a bare `except:` that really does swallow an
error, one is deliberate (mypy's crash reporter must not crash), and one labels the stages
of a bit-slicing algorithm with `// Step N:` — a banner that earns its place. Two patterns
were narrowed to get there:

- **Only bare `except:` or `except Exception:`** followed by `pass`.
  `except ValueError: pass` is an ordinary idiom — all five mypy hits of the broad pattern
  were correct code.
- **No empty JS `catch {}`.** Across my repos it hit 8 times: 5 were correct (a guarded
  `localStorage` read, a test awaiting a rejection, an optional parse) and the other 3 one
  secret-scan script copied between repos.

## Origin

There is no community list for code the way Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) is for
prose; that page has no section on code. What exists is measurement, and the sections above
lean on it:

- CodeRabbit, _State of AI vs Human Code Generation_ (2025): 470 PRs; 1.7× issues overall,
  3× readability, ~2× error handling, ~8× excessive I/O. Authorship inferred, not confirmed.
- GitClear, _AI Copilot Code Quality_ (2025): 211M changed lines; duplicated blocks up 8×
  in 2024, while moved (reused) code fell.
- _AI-Generated Smells_ (arXiv 2605.02741): long methods and god classes, with code volume
  tracking architectural decay at ρ=0.94.
- _Human-Written vs. AI-Generated Code_ (arXiv 2508.21634): generated C lacks defensive
  constructs — the "missing at the edges" half.
- Package hallucination: USENIX Security 2025 (arXiv 2501.19012) and the 2026
  re-evaluation (arXiv 2605.17062).

The comment, placeholder and residue items come from practice, not from these studies —
which is why the hook's patterns were measured against real history before shipping.
