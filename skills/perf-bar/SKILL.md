---
name: perf-bar
description: Use when assessing performance or algorithmic soundness — Big-O on hot paths, N+1 queries, Supabase egress, and benchmarking hard challenges; feeds the SPIKE sub-phase and per-task review.
---

# perf-bar

## Overview

My performance/algorithmic bar. Usable standalone on a diff, fed into the **SPIKE**
sub-phase of `eskills:task-flow` (approach selection), and invoked by its per-task review.
It earns its own lens because bottlenecks are a recurring core challenge. (This is the 4th
lens — the hard cap; a new lens must displace one.)

## Hot-path checklist

- **Big-O where it matters.** Profile or reason about complexity on hot paths; an O(n²)
  loop on a small list is fine, on a hot path it isn't. Don't micro-optimize cold code.
- **N+1 queries.** A query inside a loop over rows → batch it, join it, or prefetch.
- **Payload size, not just row count.** What crosses the wire per operation? Big blobs,
  over-fetching, sending a whole row when a version number would do.

## Per-stack hot-spots

Same lens, applied to the stack in play — the footgun I hit most in each:

- **React / Vite:** wasted re-renders → memoize (`memo`/`useMemo`/`useCallback`), stable list keys, split context; virtualize long lists. Profile with the React DevTools profiler, don't guess.
- **Django:** ORM **N+1** → `select_related` (FK) / `prefetch_related` (M2M); fetch only needed columns (`.only()`/`.values()`); never run a query inside a template or loop.
- **Flask / FastAPI:** **blocking I/O on an async path** — a sync DB/HTTP call inside `async def` stalls the event loop → use an async client or offload to a threadpool; keep CPU-bound work off the loop.
- **Kotlin coroutines:** blocking work on the wrong dispatcher → `Dispatchers.IO` for blocking calls, wrap with `withContext`; no `runBlocking` on hot paths; don't re-collect cold `Flow`s needlessly.

## Supabase egress — my binding limit

The Free-tier wall is **egress (bytes transmitted), not DB size**. Egress ≈
`blob_size × updates × connected_clients`. Levers, in order:

1. **Cap unbounded growth.** Any field that grows per action (history, trash, logs) needs a
   hard cap — uncapped blobs grow quadratically and blow the limit.
2. **Don't ship the whole row on every change.** Broadcast only `{version}` over Realtime;
   fetch the full payload only when the remote version is newer (version-gated fetch).
3. **Write-through the local cache** so a client doesn't refetch its own write.

## Hard challenges

When the task is flagged hard-tech: in the SPIKE, **benchmark candidate approaches on
representative input before committing the plan** — measure, don't guess. Keep the
micro-benchmark; it's the evidence the approach was chosen on merit.

## Output

Report findings as `location → cost (Big-O / bytes / queries) → the lever`. Separate a
measured regression from a theoretical one; prefer numbers.
