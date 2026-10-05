# release-please — gotchas

## release-please: "Resource not accessible by integration"

- **Symptom:** release-please fails at "Creating N releases…" despite correct token perms.
- **Means:** GitHub **secondary** rate-limit (abuse detection) on the `github-actions[bot]`
  token, _not_ a permissions bug. Tell-tale: a release succeeded seconds earlier; `gh api
rate_limit` core looks healthy. Usually triggered by a burst (dependabot opening ~12 PRs).
- **Fix:** (1) create the missing release with **your user token**, full 40-char SHA:
  `gh release create vX.Y.Z --target <full-sha> --title vX.Y.Z --notes "<CHANGELOG section>" --latest`.
  (2) Swap the PR label `autorelease: pending` → `autorelease: tagged` via REST (`gh api`),
  or it retries forever. (3) Let the bot cooldown clear (~minutes–1h) with no more
  content-creation calls. Code usually deployed anyway (Pages runs on push independently).

## release-please: infinite auto-merge loop

- **Symptom:** the release PR never merges; the workflow re-dispatches itself every ~90s.
- **Means:** the bot's PR (made with `GITHUB_TOKEN`) gets **no CI run** → the required
  `verify` check never appears → auto-merge can't complete; it lands only via a fragile
  fast-forward that breaks if `main` advanced by hand in parallel.
- **Fix:** create the tag/release yourself at `main` HEAD
  (`gh release create vX.Y.Z --target <main-sha>`) → no pending release → no re-dispatch →
  loop stops. Replicate the bump in `package.json` + `.release-please-manifest.json` +
  `CHANGELOG.md` via a normal user PR so CI runs. **Don't hand-merge `main` mid-release.**
  Durable fix: give release-please a **PAT** (its PRs then trigger CI) and drop the
  unconditional self-redispatch.

## release-please: "GitHub Actions is not permitted to create or approve pull requests" (new repo)

- **Symptom:** on a **freshly created** repo, the Release workflow's release-please step
  fails almost immediately (~15s) with `release-please failed: GitHub Actions is not
permitted to create or approve pull requests.` The CI workflow is fine; only release PR
  creation fails.
- **Means:** new repos default the repo Actions setting to
  `default_workflow_permissions=read` + `can_approve_pull_request_reviews=false`.
  release-please must **open its release PR**, and the repo/org toggle overrides the
  workflow-level `permissions: pull-requests: write` — so the in-workflow grant is not
  enough on its own.
- **Fix:** enable it once (Settings → Actions → General → "Allow GitHub Actions to create
  and approve pull requests"), via API:
  ```
  gh api -X PUT repos/<owner>/<repo>/actions/permissions/workflow \
    -f default_workflow_permissions=write -F can_approve_pull_request_reviews=true
  gh run rerun <failed-release-run-id>
  ```
  Do this right after `gh repo create` for any new FAP / sister app — it's a one-time
  per-repo setting, not a code or token problem. (Distinct from the secondary rate-limit
  and auto-merge-loop failures above.)

## `uv.lock` keeps the previous version of the project itself

- **Symptom:** after a release, `uv.lock` still pins the project at the version it had
  before the bump, and `uv sync --locked` in CI starts failing.
- **Means:** release-please bumps `pyproject.toml` and the changelog, but nothing re-locks.
  `uv sync --frozen` hides it: it uses the lock as is and checks nothing.
- **Fix:** add the lock to the release PR through `extra-files`, with a jsonpath over TOML:
  `{ "type": "toml", "path": "uv.lock", "jsonpath": "$.package[?(@.name.value=='<name>')].version" }`.
  Relocking by hand fixes the symptom and breaks again on the next release. Keep
  `--locked`, never `--frozen`, on the quality job's `uv sync`.

## The release PR sits with no CI until someone touches it

- **Symptom:** release-please opens its PR, auto-merge is armed, and no check ever starts.
  CI only runs once someone pushes to the branch or approves by hand.
- **Means:** the action has no `token:`, so it opens the PR with `GITHUB_TOKEN`, and
  GitHub never starts a workflow from an event that token caused.
- **Fix:** `token: ${{ secrets.RELEASE_PLEASE_TOKEN }}` on the `release-please-action`
  step. Grep every repo for a release-please step without it; one copied workflow is
  enough to spread it.

## A `Release-As:` footer never reaches `main`

- **Symptom:** a PR whose only commit is an empty one carrying `Release-As: x.y.z` merges,
  GitHub says merged, and no release with that version ever comes.
- **Means:** a rebase merge drops commits that end up empty, so the footer is discarded.
  `gh pr merge --rebase` reports no error and the PR still shows as merged.
- **Fix:** put the footer on a commit with real content, and confirm it with
  `git log origin/main` after the merge. Typical need: with `release-type: simple` only
  `feat:` and `fix:` release, so a `docs:` change to a file in `extra-files` never
  publishes by itself.
