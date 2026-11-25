# Mutation testing

Coverage says a line ran; mutation testing says a test would notice if that line were wrong.
The tool flips one thing at a time (`>` to `>=`, `||` to `&&`, a condition to `false`, a
return value to empty) and re-runs the tests. A mutant the tests catch is **killed**; one
they miss **survived**; one no test even reaches is **NoCoverage**.

## Scope

- Mutate only the **files the change touched**, never the whole repo on a normal task.
- Logic goes to zero unexplained survivors wherever it lives: `domain/`, `application/`,
  pure helpers, and infrastructure adapters that decide something (a realtime adapter that
  reuses channels and sends only a version number guards egress; mutate it).
- UI: move the logic out of components into pure functions (`presentation/utils`, hooks)
  and hold those to zero. Components get 2–4 behaviour tests each (what gets saved,
  validation, edit pre-fill, one key conditional); measure their score, don't chase it.
- Skip config, wiring-only glue and generated code.
- No score target, same as coverage. The unit of work is the individual surviving mutant.

## Reduce, don't inflate

Mutation testing exists to find useless tests as much as missing ones. Closing survivors by
adding a test per mutant multiplies the suite; don't.

- First strengthen an existing test: assert the whole result (`toEqual` on the object or
  the appended history entry), use fixtures with two items so id matching is exercised,
  turn a family of guard tests into one `it.each` table.
- Add a new test only when nothing fits.
- Then prune: run once with `--disableBail` (every killing test gets recorded) and compute
  the minimal set that still kills every mutant with `references/stryker/prune.py report.json --alone
  <test-file-prefixes>`. Delete the rest.
- **Never prune** tests that guard what Stryker can't generate: PIN enforced server-side,
  throttles, egress limits, payload caps, "does not mutate its input" (React state relies
  on it), and named regression tests. They "kill nothing" by design.

## Triage — every Survived or NoCoverage mutant gets one verdict

1. **Missing test** → write the behavior test that kills it (a boundary, the other branch of
   a guard, the error case). Most survivors are this: `cents > MAX` vs `cents >= MAX` with
   no test at the limit.
2. **Dead code** → the mutant can't change behavior because the code doesn't matter. Delete
   it.
3. **Equivalent mutant** → the change is observably identical (a `<` vs `<=` on a value
   that can never be equal, a placeholder entry a later filter drops). First try rewriting
   the code so the redundant branch disappears; otherwise mark it in place with
   `// Stryker disable next-line <Mutator>: <reason>`. Don't write a test to pin it.

A mutant in a `throw` guard that survives is almost always case 1: the validation exists
and nothing proves it. Duplicated code shows up as the same survivor in several files:
extract it once and test it once.

Disable comments are **not honoured** everywhere:
- In the middle of a multi-line method chain, a `next-line` mark is ignored. Wrap the whole
  statement in `// Stryker disable <Mutator>: reason` … `// Stryker restore <Mutator>`.
- Around a `catch` clause, even the wrapping block is ignored. Extract the read into a small
  function whose `try`/`catch` lines can each carry a `next-line` mark.

## TypeScript + Vitest — StrykerJS

Installed once, outside every repo (like the Python CLIs in `~/.local/venvs`), so no
project gains a dependency or a config file:

```bash
mkdir -p ~/.local/share/stryker && cd ~/.local/share/stryker && npm init -y
npm i @stryker-mutator/core @stryker-mutator/vitest-runner typescript@^6
```

`typescript@^6` is deliberate: TypeScript 7 ships no JS API and Stryker's tsconfig
preprocessor crashes on it (`ts.parseConfigFileTextToJson is not a function`). `npx -p`
doesn't work either: when the project already has `typescript`, npx skips it and Stryker
can't resolve it from its own folder.

Copy the noise plugin next to it so it can resolve `@stryker-mutator/api`:

```bash
cp <eskills>/skills/standards/references/stryker/noise-ignorer.mjs ~/.local/share/stryker/
```

It ignores mutants nobody should test: error-message text, string labels passed to
`assert*`/`require*` helpers, and `className`/`style` attributes.

Keep the config in `../<repo>-notes/stryker.config.json`, never in the repo:

```json
{
  "testRunner": "vitest",
  "plugins": ["@stryker-mutator/vitest-runner", "<home>/.local/share/stryker/noise-ignorer.mjs"],
  "ignorers": ["noise"],
  "mutate": ["src/domain/x.ts", "src/application/y.ts"],
  "reporters": ["clear-text", "json"],
  "jsonReporter": { "fileName": "../<repo>-notes/mutation.json" },
  "concurrency": 4
}
```

Run it from the repo root with
`~/.local/share/stryker/node_modules/.bin/stryker run ../<repo>-notes/stryker.config.json`.
Then read the result with `references/stryker/triage.py ../<repo>-notes/mutation.json`. It lists
survivors per file and the tests that reach mutated code but kill nothing.

- Add `--incremental --incrementalFile ../<repo>-notes/stryker-incremental.json` while
  iterating on the same files.
- In a git worktree, run `npm ci`. A symlinked `node_modules` is not copied into
  Stryker's sandbox and the run dies with `Cannot find package 'vitest'`.
- While `.stryker-tmp/` exists, Vitest picks up the copied tests. Count tests with
  `--exclude '.stryker-tmp/**'`, and delete the folder if a run was killed.
- Never run it alongside another heavy job.
- Cost on EventSplit:
  - 2 domain files, 200 mutants: 7.5 min, then 34 s incremental.
  - All of `application/` plus `infrastructure/`, 1,762 mutants at concurrency 8: 28 min.

## Python

Not wired yet. Pick the tool when the first Python project needs it.
