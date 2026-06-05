---
name: stack-gotchas
description: Use when hitting a known failure in my stack — release-please rate-limit or auto-merge loop, GitHub Pages env branch-policy, Supabase egress/RLS/stale-client-blob, or verifying mobile/responsive rendering in WSL — for a direct diagnose-and-recover recipe.
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
