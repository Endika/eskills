# Dependencies and Dependabot — gotchas

## Dependabot auto-merge lands a bump with no CI and no deploy

- **Symptom:** a dependency bump reaches `main` without the pipeline having run; nothing
  deployed.
- **Means:** auto-merge needs **three** things together — branch protection, the repo's
  `allow_auto_merge`, and a PAT. With the default `GITHUB_TOKEN` the merge is performed by
  a bot whose events don't trigger other workflows, so CI and deploy never fire.
- **Fix:** set all three. If only some are present, the bump merging is worse than it not
  merging, because it looks verified and isn't.

## A red Dependabot check with nothing to fix

- **Symptom:** the security job fails, but the advisory has no action left in it.
- **Means:** what's installed already exceeds the patched version, so the job has an empty
  set to work on and exits non-zero anyway. The alert then closes itself.
- **Fix:** confirm the installed version against the advisory before touching anything.
  This is a no-op failure, not a vulnerability.

## Vitest bumps arrive as two PRs that each break `npm ci`

- **Symptom:** `vitest` and `@vitest/coverage-v8` are proposed separately and neither PR
  installs.
- **Means:** the two versions are locked to each other; `npm ci` refuses the mismatch that
  each PR creates on its own.
- **Fix:** land both bumps in one commit — take one branch, apply the other's bump on top,
  and close the second PR.

## An `overrides` entry doesn't reach the vulnerable transitive package

- **Symptom:** a CVE in a nested dependency survives an `overrides` block that looks right.
- **Means:** npm's nested `overrides` form only applies within the parent it's declared
  under. The transitive copy is reached by the **global** form, at the top of `overrides`.
- **Fix:** use the global form. Dependabot never proposes overrides at all, so this is
  always a manual edit.

## The typescript-eslint major PR can never go green

- **Symptom:** a Dependabot PR bumping TypeScript to 7 fails forever.
- **Means:** typescript-eslint's peer range caps at `<6.1.0`. No amount of re-running
  changes that; the PR is unmergeable until upstream widens the peer.
- **Fix:** hold the PR, or drop typescript-eslint. Repos already on Biome have no such cap
  and are on 7 already.
