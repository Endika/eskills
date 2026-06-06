# release-please for a FAP

Source of truth: the `release-please-config.json`, `.release-please-manifest.json`,
`application.fam` and `.github/workflows/` of `flipper-trivia-zero`, `flipper-habit-flow`,
`flipper-nfc-stock`, `flipper-hyper-focus-calc` (identical pattern across all four).

## The version triad — must always match

One logical version lives in **three** files; release-please keeps them in sync, and the
catalog/CI reject a mismatch:

1. `application.fam` → `fap_version="0.1.3"  # x-release-please-version`
2. `include/version.h` (or root `version.h` in nfc-stock) — the C constant
3. `.release-please-manifest.json` → `{ ".": "0.1.3" }`

The `# x-release-please-version` **marker comment is mandatory** — the `generic` updater
silently no-ops on `application.fam` without it. (See `stack-gotchas` for the failure
mode when these drift.)

## release-please-config.json

Pre-1.0 apps bump minor on feat, patch on fix (the `pre-major` flags):

```json
{
  "packages": {
    ".": {
      "release-type": "simple",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": true,
      "extra-files": [
        "include/version.h",
        { "type": "generic", "path": "application.fam" }
      ]
    }
  }
}
```

`.release-please-manifest.json`:

```json
{ ".": "0.1.3" }
```

## CI workflows

`ci.yml` — lint + format-check + host tests (+ Python pipeline for apps with a `tools/`
generator like trivia):

```yaml
- run: sudo apt-get update && sudo apt-get install -y build-essential cppcheck clang-format
- name: Run linter
  run: make linter
- name: Check format
  run: git ls-files '*.c' '*.h' | xargs clang-format --dry-run --Werror
- name: Run tests
  run: make test
# trivia only: ruff check / ruff format --check / mypy --strict / pytest under tools/
```

`release.yml` — release-please cuts the release, then the FAP is built and attached:

```yaml
- uses: googleapis/release-please-action@v5
# on a published release:
- uses: flipperdevices/flipperzero-ufbt-action@v0.1 # build the .fap
- name: Upload FAP to release
  run: gh release upload ... # attach the .fap artifact
```

## Auto-merging the release PR (sister-app pattern)

To make the release PR auto-merge (as the web sister apps do — kartaak/EventSplit/mintza/
converthub/Monete), fold the merge into the release workflow. After the release-please
step, when it opened a PR, rebase-merge it and re-dispatch so the merge is picked up:

```yaml
permissions: { actions: write, contents: write, pull-requests: write }
# token: ${{ secrets.RELEASE_PLEASE_TOKEN || github.token }}  # PAT lets the merge re-trigger workflows
- if: ${{ steps.release.outputs.pr }}
  env: { GH_TOKEN: ${{ secrets.RELEASE_PLEASE_TOKEN || github.token }}, REPO: ${{ github.repository }}, WORKFLOW: ${{ github.workflow }}, PR_JSON: ${{ steps.release.outputs.pr }} }
  run: |
    PR=$(echo "$PR_JSON" | jq -r .number); BRANCH=$(echo "$PR_JSON" | jq -r .headBranchName)
    gh pr merge --rebase --auto -R "$REPO" "$PR" \
      || gh pr merge --rebase -R "$REPO" "$PR" \
      || gh api -X PATCH "repos/$REPO/git/refs/heads/main" -f sha="$(gh api "repos/$REPO/git/refs/heads/$BRANCH" --jq .object.sha)"
    # wait for MERGED, delete the branch, then: gh workflow run "$WORKFLOW" -R "$REPO" --ref main
```

Required one-time repo setup (new repos default these OFF — see `stack-gotchas`):
- `gh api -X PATCH repos/<o>/<r> -F allow_auto_merge=true -F allow_rebase_merge=true`
- `gh api -X PUT repos/<o>/<r>/actions/permissions/workflow -f default_workflow_permissions=write -F can_approve_pull_request_reviews=true`
- Add the **`RELEASE_PLEASE_TOKEN`** PAT secret (all the sister apps have it) so the bot's
  merge re-triggers workflows and the release is cut hands-off. Without it, the
  `github.token` fallback + the explicit `gh workflow run` re-dispatch still close the loop,
  but the PAT is the durable fix (avoids the auto-merge-loop gotcha). `flipper-tutu` is the
  first Flipper app wired this way (the other four still merge their release PR by hand).

## Catalog

Submitting to the official catalog: the manifest's `commit_sha` must point at the
**release** commit (the tagged one), **not** a later fix commit, and the catalog entry's
version must equal `fap_version` — otherwise the catalog CI fails. (Recorded in
`stack-gotchas` and the catalog-update-flow memory.)
