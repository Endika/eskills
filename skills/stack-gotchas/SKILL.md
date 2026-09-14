---
name: stack-gotchas
description: Use when hitting a known failure in my stack — release-please rate-limit or auto-merge loop, GitHub Pages env branch-policy or a deploy queue jammed by cancel-in-progress, Supabase egress/RLS/stale-client-blob, a Flipper FAP release/build/version-triad failure or a FAP whose UI won't refresh when launched from favourites/quick-buttons, verifying mobile/responsive rendering in WSL, or a Docker engine/context mix-up under WSL — for a direct diagnose-and-recover recipe.
---

# stack-gotchas

## Overview

Diagnose-and-recover recipes for failures I've actually hit. Each is **symptom → what it
really means → fix** — not a tutorial. The recipes live in `references/`, one file per
family; this page is the symptom index. Match the symptom, open that file, apply the
recipe.

## Find the symptom

| It looks like                                                                            | Open                           |
| ---------------------------------------------------------------------------------------- | ------------------------------ |
| A release didn't cut; the release PR is stuck, looping, or forbidden from opening        | `references/release-please.md` |
| A Pages deploy is rejected, queues forever, or every retry says cancelled                | `references/github-pages.md`   |
| It only breaks inside WSL; an image or container seems to have vanished                  | `references/wsl.md`            |
| Egress blown, anonymous writes possible, or fields vanishing after another client writes | `references/supabase.md`       |
| A FAP won't build or test, the catalog rejects it, or its screen stays blank             | `references/flipper.md`        |
| Personal data is reachable, or data leaves to a third party undisclosed                  | `references/gdpr.md`           |

## What belongs here

Failures **actually hit**, with what the symptom really meant and what fixed it. Not
prevention, not conventions, not a tutorial — those live in the lenses and in `stacks`. A
recipe with no scar behind it makes every other recipe less trustworthy.
