---
name: stack-gotchas
description: Use when hitting a known failure in my stack — release-please or a stuck release, a GitHub Pages deploy that won't land, a gh CLI / PAT / Dependabot / npm-resolution dead end, Supabase egress or RLS, a Flipper FAP that won't build or refresh, WSL and host-OS oddities (disk, registry, Docker context), or a remote box hanging on a prompt — for a direct diagnose-and-recover recipe.
---

# stack-gotchas

## Overview

Diagnose-and-recover recipes for failures I've actually hit. Each is **symptom → what it
really means → fix** — not a tutorial. The recipes live in `references/`, one file per
family; this page is the symptom index. Match the symptom, open that file, apply the
recipe.

## Find the symptom

| It looks like                                                                                       | Open                           |
| --------------------------------------------------------------------------------------------------- | ------------------------------ |
| A release didn't cut; the release PR is stuck, looping, or forbidden from opening                   | `references/release-please.md` |
| A Pages deploy is rejected, queues forever, or every retry says cancelled                           | `references/github-pages.md`   |
| It only breaks inside WSL, the disk won't shrink, or an image or container seems to have vanished   | `references/wsl.md`            |
| Egress blown, anonymous writes possible, or fields vanishing after another client writes            | `references/supabase.md`       |
| A FAP won't build or test, the catalog rejects it, or its screen stays blank                        | `references/flipper.md`        |
| Personal data is reachable, or data leaves to a third party undisclosed                             | `references/gdpr.md`           |
| A `gh` command dies on a GraphQL error, a 403 on a repo I don't own, or a poll loop that never ends | `references/github-cli.md`     |
| A dependency bump merges without CI, won't install, or can never go green                           | `references/dependencies.md`   |
| A command on a remote box hangs with no output, or a process match kills the wrong thing            | `references/remote-ops.md`     |

## What belongs here

Failures **actually hit**, with what the symptom really meant and what fixed it. Not
prevention, not conventions, not a tutorial — those live in the lenses and in `stacks`. A
recipe with no scar behind it makes every other recipe less trustworthy.
