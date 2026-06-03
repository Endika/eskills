---
name: security-bar
description: Use when reviewing changes for security to apply my checklist on top of security-review — input handling, secrets, authz, Supabase RLS, egress limits, and server-side PIN enforcement.
---

# security-bar

## Overview

My security checklist. It layers on top of `security-review` (reference it for the broad
sweep) and adds the things that actually bite me. Usable standalone on a diff, and invoked
by the quality stage of `eskills:task-flow`.

## The principle I keep relearning

**Client-side guards are not security.** The anon key ships in the client; a PIN, a
rate-limit, or a check that lives only in front-end code provides zero server-side
protection. If it must be enforced, it is enforced on the server.

## Checklist

- **Input handling** — validate and bound every external input (size, type, shape). Parse,
  don't trust. Watch unbounded growth (a field that can balloon a stored blob).
- **Secrets** — none in the client bundle or the repo; only public-by-design keys are
  client-side. Confirm what a shipped key can actually do.
- **Authz** — every privileged action checks who's allowed, server-side. No "the UI hides
  the button" as the only control.
- **Supabase RLS** — no table with open anon `SELECT true` **and** `INSERT/UPDATE true`;
  that lets anyone with the anon key read and overwrite rows via PostgREST, bypassing the
  app. Restrict direct writes; route privileged writes through an RPC that checks the rule.
- **Server-side PIN / ownership enforcement** — a PIN stored in a public blob is not a
  lock. Enforce it in an RPC with RLS restricting the direct write.
- **Egress / abuse limits** — see `eskills:perf-bar`; a missing cap is both a cost and an
  abuse vector.

## Output

Report findings as `file:line → what an attacker does → the fix`. Distinguish a real
exposure from an accepted, documented risk (e.g. obscurity-bounded ids on a no-login app) —
but only if the acceptance was stated, not assumed.
