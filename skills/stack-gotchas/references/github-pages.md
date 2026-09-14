# GitHub Pages — gotchas

## GitHub Pages: deploy rejected with empty logs after master→main rename

- **Symptom:** the deploy job fails with **no steps and empty logs**.
- **Means:** rejected at the environment gate — the `github-pages` env's
  deployment-branch-policy still lists only the old branch (`master`).
- **Fix:**
  ```
  gh api -X POST repos/<owner>/<repo>/environments/github-pages/deployment-branch-policies -f name=main
  gh api repos/<owner>/<repo>/environments/github-pages/deployment-branch-policies --jq '.branch_policies[]'
  gh api -X DELETE repos/<owner>/<repo>/environments/github-pages/deployment-branch-policies/<id>
  ```
  Set the default branch before the first deploy; ensure Pages `build_type=workflow`.

## GitHub Pages: `deployment_queued` timeout, then every retry says "Deployment cancelled"

- **Symptom:** two distinct failures, usually in that order. First, deploy runs sit at
  `Current status: deployment_queued` for the whole timeout and abort with
  `##[error]Timeout reached, aborting!` — logs are **full** and the build step succeeded
  (unlike the empty-log branch-policy failure above). Then every re-run or re-dispatch of
  that same commit fails within seconds with `##[error]Deployment cancelled.`
- **Means:** two different things, and conflating them wastes an hour.
  1. The **timeout** is GitHub-side; githubstatus can read "All Systems Operational" while
     it happens, and it is intermittent — the same commit may deploy fine minutes later.
     No local cause was ever established.
  2. The **sticky cancellation** is deterministic and the important one. The Pages
     deployment ID **is the commit SHA**. Aborting cancels the deployment for that SHA, and
     the cancelled state is permanent, so every later attempt at the _same commit_ is
     rejected outright. Retrying can never work.
  3. **Never press "Re-run".** The first attempt already uploaded the `github-pages`
     artifact; the re-run uploads a second with the same name into the same run, and
     `deploy-pages` refuses with `Multiple artifacts named "github-pages" were unexpectedly
found for this workflow run. Artifact count is 2.` A third dead end for the same commit.
- **Fix:** all three routes are closed for a jammed commit — re-run, re-dispatch and waiting
  each fail by a different mechanism. **Land a new commit** so the deploy gets a fresh SHA
  and a clean run. Prefer a real pending change over an empty commit. Then set
  `concurrency: {group: pages, cancel-in-progress: false}`: cancelling does not stop the
  deployment it already queued, it just poisons that SHA, so `true` manufactures this
  failure on every burst of merges. GitHub's own Pages starter workflow says the same —
  _"do NOT cancel in-progress runs, as we want to allow these production deployments to
  complete."_
- **Before diagnosing a bundle mismatch, `git pull`.** Comparing a local `dist/` against the
  live page after a release, without pulling the release commit, shows a hash mismatch that
  is purely a stale `package.json` version — not a failed deploy. Verify with
  `curl -s <url> | grep -oE 'index-[A-Za-z0-9_-]+\.js'` against a fresh build of the
  **pulled** default branch.

## Pages won't enable on a brand-new repo

- **Symptom:** the deploy workflow fails because Pages isn't enabled, and the workflow's
  own `enablement: true` doesn't help.
- **Means:** enabling Pages is an account-level action; the `GITHUB_TOKEN` inside the
  workflow can't perform it.
- **Fix:** enable it once from outside the workflow with a user token:
  `gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow`.
