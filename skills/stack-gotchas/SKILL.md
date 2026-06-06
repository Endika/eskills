---
name: stack-gotchas
description: Use when hitting a known failure in my stack — release-please rate-limit or auto-merge loop, GitHub Pages env branch-policy, Supabase egress/RLS/stale-client-blob, a Flipper FAP release/build/version-triad failure or a FAP whose UI won't refresh when launched from favourites/quick-buttons, or verifying mobile/responsive rendering in WSL — for a direct diagnose-and-recover recipe.
---

# stack-gotchas

## Overview

Diagnose-and-recover recipes for failures I've actually hit. Each is **symptom → what it
really means → fix** — not a tutorial. Match the symptom, apply the recipe.

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

## Verify mobile/responsive rendering in WSL (no sudo)

- **Symptom:** you need to _see/measure_ real mobile widths but there's no Linux browser;
  Windows Edge headless **clamps window width to ~500px** (screenshots <450px render a wider
  layout cropped — misleading), and puppeteer can't drive the Windows `.exe` from WSL (stdio
  pipe breaks; its CDP debug port is unreachable over NAT).
- **Means:** you need a _native Linux_ Chromium, but the one puppeteer downloads is missing
  `libnss3`/`libnspr4`/`libasound2` and there's no passwordless sudo.
- **Fix (all without root):**
  ```
  npx -y @puppeteer/browsers install chrome@stable        # native linux chromium
  apt-get download libnss3 libnspr4 libasound2t64         # download .deb, no sudo
  for d in *.deb; do dpkg -x "$d" root; done              # extract libs locally
  # run with: LD_LIBRARY_PATH=$PWD/root/usr/lib/x86_64-linux-gnu  <chrome> …
  ```
  Drive via `puppeteer-core` (`executablePath` = that chrome; `LD_LIBRARY_PATH` in the env).
  Then `setViewport({ width, deviceScaleFactor: 2, isMobile: true })` at any width, measure
  `scrollWidth`/`getBoundingClientRect`, **bisect** overflow by toggling `display:none` per
  child, and confirm a fix by injecting the style and re-measuring before editing. Keep the
  env until done — don't re-download the ~150MB browser mid-task.
- **Before re-debugging a "still broken" UI report:** confirm the user isn't on a **stale
  deploy or cached PWA** (check the live tag + that `autoUpdate` activated). Much of this
  class of confusion is version lag, not a bug.

## Supabase: egress blown (not DB size)

- **Symptom:** Free-tier limit hit while DB size is tiny.
- **Means:** the binding limit is **egress** ≈ `blob_size × updates × connected_clients`.
  Usually an unbounded field in a JSON blob growing quadratically (history/trash snapshots).
- **Fix:** cap growing fields hard; make history an audit-log (no full snapshots); broadcast
  only `{version}` over Realtime and version-gate full fetches; write-through the local
  cache. See `eskills:perf-bar`. Next lever: split the growing field into its own table.

## Supabase: open-write RLS

- **Symptom:** anyone with the anon key can overwrite a row via PostgREST.
- **Means:** RLS is `SELECT true` + `INSERT/UPDATE true`; client-side PIN/rate-limit give
  no server protection (the anon key ships in the client).
- **Fix:** restrict direct writes; enforce ownership/PIN in an RPC with RLS. See
  `eskills:security-bar`.

## Supabase: stale-client blob wipe

- **Symptom:** a newly-added field (e.g. subgroups) silently disappears after another user
  edits.
- **Means:** whole-blob rewrite + Zod stripping unknown keys + a manual-update PWA → a stale
  cached client (running old code) drops fields its schema doesn't know on its next write.
  The optimistic `version` check doesn't protect (same-version-lineage overwrite).
- **Fix:** stamp `_schemaVersion` on every write + a Postgres BEFORE UPDATE trigger
  rejecting writes whose version < stored (→ HTTP 426 → "please update" prompt); flip the
  PWA to `autoUpdate`. **Operational rule: bump `SCHEMA_VERSION` whenever the snapshot shape
  changes**, or the guard won't protect the new field.

## Flipper FAP: release-please leaves application.fam un-bumped

- **Symptom:** `version.h` and the manifest bump on release, but `application.fam`'s
  `fap_version` stays behind → catalog/CI version mismatch.
- **Means:** the `generic` updater needs the marker comment and it's missing/edited —
  `fap_version="x.y.z"  # x-release-please-version`. Without the exact `x-release-please-version`
  comment on that line, the updater silently no-ops.
- **Fix:** restore the marker comment on the `fap_version` line; keep the triad
  `application.fam` ↔ `version.h` ↔ `.release-please-manifest.json` in sync. See
  `stacks/references/flipper/release-please.md`.

## Flipper FAP: catalog submission rejected on version/commit

- **Symptom:** the official catalog CI fails the entry.
- **Means:** the manifest `commit_sha` points at a later **fix** commit instead of the
  tagged **release** commit, or the entry version ≠ `fap_version`.
- **Fix:** point `commit_sha` at the release commit; make the catalog version equal
  `fap_version`. (Catalog-update-flow memory + `stacks` → flipper.)

## Flipper FAP: host test won't compile (furi symbols)

- **Symptom:** `make test` fails to compile with undefined furi references.
- **Means:** a file under test (transitively) includes `furi` — furi isn't available on the
  host gcc build; the layering leaked.
- **Fix:** keep `domain/` pure C and move the furi-touching code behind a plain-C signature
  in `platform/`. Only test `domain/`. See `stacks/references/flipper/architecture.md`.

## Flipper FAP: cppcheck flags entry points as unusedFunction

- **Symptom:** `make linter` errors on `unusedFunction` for `main.c` / `*_app.c` / port files.
- **Means:** those functions are called by the firmware, not within the TU — a cppcheck
  false positive, not dead code.
- **Fix:** add a path-scoped `--suppress=unusedFunction:<path>` (or inline
  `// cppcheck-suppress`), never disable the check globally. See
  `stacks/references/flipper/formatting.md`.

## Flipper FAP: blank/stale UI when launched from favourites or quick-buttons

- **Symptom:** the screen is blank or frozen (UI never refreshes) when the app is opened
  from a **desktop favourite** or a **quick-press button** shortcut — but it works fine
  when opened from the **Apps menu**. (Reported by catalog users on two of my apps.)
- **Means:** the app only calls `view_port_update()` in reaction to input — the main loop
  blocks on `furi_message_queue_get(..., FuriWaitForever)` and paints nothing until a key
  is pressed. The Apps menu **masks** it: the loader's background hourglass animation
  forces a GUI redraw, so the first frame appears. Favourites/quick-buttons skip that
  loader → nothing triggers the draw. The app was leaning on an external redraw ("a bug"),
  not driving its own.
- **Fix:** force the redraw from the app itself. (1) Draw once immediately after
  `gui_add_view_port(...)` with `view_port_update(view_port)`. (2) Don't depend on input to
  paint: either give the queue a **finite timeout** (`furi_message_queue_get(q, &e, 50)`)
  and call `view_port_update()` **every loop tick**, or call it after **every** state
  change (including the initial state). Same fix for a `ViewDispatcher`/`SceneManager` app:
  ensure the first scene transition happens before the loop blocks. See
  `stacks/references/flipper/architecture.md`.

## GDPR: open-RLS exposes personal data

- **Symptom:** any anon key holder can read/update/delete rows that contain names, email, or
  financial data (e.g. EventSplit's events blob).
- **Means:** open-write RLS (`SELECT/INSERT/UPDATE true`) isn't just a security bug — it's a
  **personal-data exposure / breach risk** under GDPR (unauthorized access to identifiable
  people, including third parties who never consented).
- **Fix:** restrict direct writes / enforce ownership in an RPC (the security fix →
  `eskills:security-bar`); then in the privacy notice, only claim protections you actually
  have. Don't document "your data is protected" while RLS is open. See `eskills:gdpr`.

## GDPR: undisclosed international transfer to an AI provider

- **Symptom:** the app sends user audio/text to OpenAI/Anthropic/Google/Azure, but the
  privacy notice (if any) doesn't mention it (mintza).
- **Means:** that's a **processor + international transfer (US)** with no disclosure and no
  transfer mechanism named — a GDPR gap, and possibly special-category data (voice).
- **Fix:** disclose every AI provider as a processor + name the transfer basis (SCCs/DPF) in
  the notice; confirm no-training-on-API-data + retention; send the model the **minimum**
  content, no needless identifiers. See `eskills:gdpr` (AI-processor posture).
