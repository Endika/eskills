---
name: security-bar
description: Use when reviewing changes for security to apply my checklist on top of security-review — input handling, secrets, authz, Supabase RLS, egress limits, server-side PIN enforcement, and the agent-harness surface (config secrets, hook injection, MCP risk, over-broad permissions).
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

## Harness / agent-config

Different target from the app checklist above: this audits **my own agent setup**, not the
code under review. The principle: **agent config is executable trust** — a hook or an MCP
server runs with my privileges, so it is code I am running, not configuration I am declaring.

- **Config secrets** — no real keys in `.claude/settings*.json`, hook scripts, or MCP
  configs that land in a repo (`sk-`, `ghp_`, `AKIA`, …). Only public-by-design keys belong
  client-side; everything else stays in the environment, never committed.
- **Hook injection** — every hook command is auditable and trusted; it fires on tool/session
  events with full shell privileges. Flag any hook that interpolates untrusted input (tool
  output, file contents, a PR title) into a shell command — that is an injection sink.
- **MCP server risk** — review each server before connecting; it sees my prompts and tool
  calls and can exfiltrate. Prefer pinned, known sources; treat a third-party server as code
  I am running, not a passive endpoint.
- **Permissions** — `allow` lists scoped to what's actually needed; no blanket wildcards
  (e.g. `Bash(*)`) that defeat the prompt gate. Remember a permission moved to user/global
  settings applies to every project, not just this one.

## Output

Report findings as `file:line → what an attacker does → the fix`. Distinguish a real
exposure from an accepted, documented risk (e.g. obscurity-bounded ids on a no-login app) —
but only if the acceptance was stated, not assumed.
