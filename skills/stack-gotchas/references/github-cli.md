# gh CLI and PR plumbing — gotchas

## `gh pr edit` fails with a GraphQL error about project cards

- **Symptom:** any `gh pr edit` — even one that only touches the body — dies on a GraphQL
  error mentioning projects.
- **Means:** the command asks for classic-Projects fields the repo can no longer answer.
  The edit never reaches the body; nothing partial is written.
- **Fix:** patch the body through the REST API instead:
  `gh api -X PATCH repos/<owner>/<repo>/pulls/<n> -f body="$(cat body.md)"`. On a repo I
  don't own this returns 403 — see the next recipe.

## Writing to a repo I don't own returns 403

- **Symptom:** opening an issue or PR, or editing a body, fails with 403 despite a working
  token.
- **Means:** the PAT has no write scope on someone else's repository. This is not a
  misconfiguration to fix — it's the boundary.
- **Fix:** produce the text and open it through the web UI by hand. The agent's deliverable
  is the draft, never a claim that it was posted. Never invent a `#NN` to fill the gap.
  Drafting rules in `eskills:comms`.

## A stale Dependabot PR won't update

- **Symptom:** the branch is behind `main` and needs a refresh; `gh pr update-branch` looks
  like the tool for it.
- **Means:** that subcommand doesn't exist, and updating the branch through the API merges
  `main` into it, which breaks the linear history the repo requires.
- **Fix:** comment `@dependabot rebase` (or `@dependabot recreate` when the branch content
  itself is stale). Let the bot own its branch.

## A wait loop on `gh pr checks` never ends

- **Symptom:** a background until-loop polling a PR keeps running long after the work is
  done, burning a task slot.
- **Means:** once the PR is merged the checks query stops returning a pending state the
  loop recognizes, so the exit condition is never met.
- **Fix:** stop the task by hand after merging (`TaskStop`), or bound the loop with
  `timeout` from the start. Don't start an unbounded poll you won't come back to.

## A PR with auto-merge sits `BEHIND` forever

- **Symptom:** checks green, auto-merge armed, and the PR never merges; `mergeStateStatus`
  is `BEHIND`.
- **Means:** branch protection has `strict: true`, so the branch must be up to date, and
  auto-merge doesn't rebase for you when `main` moves.
- **Fix:** for your own branch, `git rebase origin/main` and
  `git push --force-with-lease`; for Dependabot, comment `@dependabot rebase`.

## `gh pr checks --json` is an unknown flag

- **Symptom:** a wait loop that filters failed checks never sees one, because the command
  errors with `unknown flag: --json` and the error goes to `/dev/null`.
- **Means:** this `gh` build's `pr checks` has no JSON output.
- **Fix:** read `gh pr view <n> --json state,statusCheckRollup` and filter on
  `conclusion`. Don't hide a poll's stderr until the command has been seen to work.
- **Related:** `gh pr checks --watch` launched right after opening a PR can exit at once with
  every check still `pending`: the checks aren't registered yet, so there is nothing to
  watch. Wait 20–30 s before watching, and re-read the checks before calling anything green.

## The CI badge says failing while every PR is green

- **Symptom:** the README badge (`.../workflow/status/<owner>/<repo>/ci.yml?branch=main`)
  shows failing, yet the PRs' CI and the latest merges are all green.
- **Means:** with `branch=main` the badge reads the newest run of that workflow on `main`.
  If the workflow no longer runs on `push` to `main` (a trigger dropped to stop double
  runs, then the caller that ran it on `main` was removed), the badge keeps showing an old
  cancelled or failed run from months ago.
- **Fix:** check the date of that run with
  `gh api "repos/<owner>/<repo>/actions/workflows/ci.yml/runs?branch=main&per_page=1"`.
  If it's stale, put `push: branches: [main]` back on the CI workflow. Don't switch the
  badge to `event=pull_request`: it goes green while `main` still runs no CI.
