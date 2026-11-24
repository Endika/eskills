# Mutation testing

Coverage says a line ran; mutation testing says a test would notice if that line were wrong.
The tool flips one thing at a time (`>` to `>=`, `||` to `&&`, a condition to `false`, a
return value to empty) and re-runs the tests. A mutant the tests catch is **killed**; one
they miss **survived**; one no test even reaches is **NoCoverage**.

## Scope

- Mutate only the **logic files the change touched**: `domain/`, `application/`, pure
  helpers. Never the whole repo.
- Skip UI components, infrastructure adapters, config and generated code: their mutants are
  string and markup noise, and the honest test for them is an integration or e2e test.
- No score target, same as coverage. The unit of work is the individual surviving mutant.

## Triage — every Survived or NoCoverage mutant gets one verdict

1. **Missing test** → write the behavior test that kills it (a boundary, the other branch of
   a guard, the error case). Most survivors are this: `cents > MAX` vs `cents >= MAX` with
   no test at the limit.
2. **Dead code** → the mutant can't change behavior because the code doesn't matter. Delete
   it.
3. **Equivalent mutant** → the change is observably identical (e.g. a different error
   message string nobody asserts, a `<` vs `<=` on a value that can never be equal). Name it
   in the report with the one-line reason; don't write a test to pin it.

A mutant in a `throw` guard that survives is almost always case 1: the validation exists
and nothing proves it.

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

Run from the repo root:

```bash
~/.local/share/stryker/node_modules/.bin/stryker run \
  --testRunner vitest \
  --mutate 'src/domain/x.ts,src/application/y.ts' \
  --reporters clear-text \
  --incremental --incrementalFile ../<repo>-notes/stryker-incremental.json \
  --concurrency 2
```

- `--mutate` takes the touched files, comma-separated (globs work).
- The incremental file lives in `../<repo>-notes/`, never in the repo. Stryker's
  `.stryker-tmp/` sandbox is removed on exit; the repo stays clean.
- `--concurrency 2` keeps the machine usable; never run it alongside another heavy job.
- Cost, measured on EventSplit (2 domain files, 200 mutants): **7.5 min** the first run,
  **34 s** the incremental re-run. Hence: touched files only, and keep the incremental file.

## Python

Not wired yet. Pick the tool when the first Python project needs it.
