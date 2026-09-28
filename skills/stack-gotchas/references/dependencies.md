# Dependencies and Dependabot — gotchas

## Dependabot auto-merge lands a bump with no CI and no deploy

- **Symptom:** a dependency bump reaches `main` without the pipeline having run; nothing
  deployed.
- **Means:** auto-merge needs **three** things together — branch protection, the repo's
  `allow_auto_merge`, and a PAT. With the default `GITHUB_TOKEN` the merge is performed by
  a bot whose events don't trigger other workflows, so CI and deploy never fire.
- **Fix:** set all three. If only some are present, the bump merging is worse than it not
  merging, because it looks verified and isn't.

## An auto-merge workflow would merge a stranger's pull request

- **Symptom:** none until it's too late. The auto-merge workflow runs on
  `pull_request_target` with the PAT and gates on `github.actor == 'dependabot[bot]'`, or on
  the head ref starting with `release-please--`.
- **Means:** anyone can open a PR from a fork on a branch named `release-please--x`, and the
  job queues it for auto-merge with your PAT. It lands on `main` as soon as the required
  check passes. `github.actor` is only whoever fired the latest event, the known Dependabot
  confused deputy. The one thing holding it back is that GitHub waits for your approval
  before running CI for a first-time fork contributor.
- **Fix:** gate every job on a same-repo head,
  `github.event.pull_request.head.repo.full_name == github.repository`, and on the PR author
  instead of the actor. For Dependabot that's `user.login == 'dependabot[bot]'`. For
  release-please it's `user.login == github.repository_owner`, since it opens its PRs with
  the owner's PAT: check who opens them before shipping, or the release PR never merges
  again. When a new repo copies the workflow, copy the guarded one.

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

## A major bump never shows up, or shows up bundled with minor ones

- **Symptom:** an action or package sits several majors behind while the other repos moved,
  or a grouped Dependabot PR carries a major inside it.
- **Means:** an `ignore` of `version-update:semver-major` for `dependency-name: "*"` hides
  every major forever. A group without `update-types`, security groups included, takes
  majors too, so one lands next to minors in a single PR.
- **Fix:** no blanket major ignore (a targeted one with a reason is fine). Give every group
  `update-types: [minor, patch]`, so each major arrives as its own PR, and keep the
  auto-merge step gated to `semver-patch`/`semver-minor` so majors wait for a human.

## The auto-merge job fails with "Dependabot's commit signature is not verified"

- **Symptom:** a red `auto-merge` check on a Dependabot PR that merges anyway.
- **Means:** with `strict` branch protection the branch was rebased with the owner's PAT,
  so the head commit is no longer signed by Dependabot and `fetch-metadata` refuses on the
  `synchronize` event. Auto-merge was already armed when the PR opened.
- **Fix:** nothing, if auto-merge is armed and the required checks are green; it's noise.
  Check `autoMergeRequest` on the PR before chasing it.
