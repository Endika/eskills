# React hot-spots (SPA)

The per-rule detail behind the **React / Vite** line in `perf-bar`. Scope: React 18/19
rendering in a **Vite SPA** — the pack's default web stack. Everything here is about INP
and wasted work on the client; there is no SSR, no RSC and no hydration in this stack, so
those rules are deliberately absent (see _Out of scope_).

Apply it like the rest of the lens: find the cost first, then the lever. A re-render that
nobody can perceive is not a finding.

## 1. Wasted re-renders — the default suspect

- **Derive during render, never in `useEffect`.** Compute it in the body; a `useState` +
  `useEffect` pair mirroring props costs two extra renders and leaves a stale window.
  (An effect that _subscribes_ to something external — `popstate`, a custom event, a timer
  — is not this antipattern.)
- **Don't subscribe to state you only read in a callback.** Read it at call time from the
  ref/getter instead; subscribing re-renders the component on every change it ignores.
- **Subscribe to the derived boolean, not the raw value.** Context value `cart` re-renders
  every consumer on any cart change; `cart.length > 0` only flips when emptiness does.
  Pair with the "split context" lever already in the lens.
- **Hoist non-primitive default props.** `<List items={items ?? []} />` mints a new array
  every render and defeats `memo`; hoist `const EMPTY: Item[] = []` to module scope.
- **Primitive deps in effects.** `[{ id, name }]` is a new identity every render — pass
  `[id, name]`.
- **Functional `setState` for stable callbacks.** `useCallback(() => setN((n) => n + 1), [])`
  needs no dependency on `n`.
- **Lazy initializer for expensive initial state.** `useState(() => parse(input))`, not
  `useState(parse(input))` — the latter runs on every render and throws the result away.
- **Never define a component inside a component.** A new function identity each render is
  a new element type: React unmounts the subtree and loses its state.
- **Don't memo primitives.** `useMemo(() => x + 1, [x])` costs more than it saves. `memo`
  earns its place on object identity and genuinely expensive work.
- **Split hooks with independent inputs** so one source changing doesn't re-run the other.
- **Interaction logic belongs in the event handler,** which runs on the action, not in an
  effect that re-runs on every dep change.

## 2. Rendering and the DOM

- **`content-visibility: auto` + `contain-intrinsic-size`** on long-list rows — the browser
  skips offscreen layout and paint. The cheap first move before reaching for virtualization.
- **Animate the wrapper, not the SVG.** Transforming a wrapping `<div>` is composited;
  transforming the SVG itself repaints.
- **Ternary, not `&&`, for conditional render.** `{count && <Badge/>}` renders a literal
  `0` when count is 0. Use `{count > 0 ? <Badge/> : null}`.
- **Hoist static JSX** to module scope so it isn't rebuilt per render.
- **Trim SVG coordinate precision** (`10.123456` → `10.12`) — sub-pixel difference, real bytes.
- **`startTransition` / `useTransition`** for non-urgent updates (filters, search results):
  React keeps the previous UI interactive and gives you `isPending` for free.
- **`useDeferredValue`** when an expensive render trails a fast-changing input.
- **`<Activity mode="hidden">`** (React 19) to hide a subtree while keeping its state and
  effects — cheaper than unmount/remount for tabs and panels you flip between.

## 3. Data and storage

- **Deduplicate the fetch, not just the render.** With no query library in this stack, two
  components wanting the same row must share one call through a provider or an in-flight
  promise cache — not two Supabase round-trips. Egress is the binding limit (see the lens).
- **`localStorage` carries a `version` field** and small payloads: the API is synchronous
  and blocks the main thread, and an unversioned blob is a migration you can't do later.
  This is the client-side twin of the version-gated fetch.
- **Cache the `localStorage` read** — once per mount, not once per render.
- **Share one global listener.** Every component adding its own `scroll`/`resize` handler
  multiplies the work; one hook over a single subscription serves all of them.
- **`{ passive: true }` on scroll and touch listeners** so they can't block scrolling.

## 4. Hot JavaScript

Only worth it on a measured hot path — a cold loop over ten items is not a finding.

- `Set` / `Map` for membership and repeated lookups instead of `Array.includes` (`O(1)` vs `O(n)`).
- One pass instead of `filter().map()` — `flatMap` or a single loop.
- A linear scan for min/max beats `sort()` (`O(n)` vs `O(n log n)`); `toSorted()` when you
  need a sorted copy without mutating.
- Hoist `RegExp` literals out of loops; cache `arr.length` and repeated property access.
- Batch DOM writes through one class swap instead of property-by-property.
- `requestIdleCallback` for work nobody is waiting on.

## 5. Stable callbacks

- **`useEffectEvent`** (exported from React 19.2) for the "latest value, stable identity"
  case — its value must **not** go in the effect's dep array.
- **Ref-held handler** for the same need pre-19.2: keep `handlerRef.current = handler` and
  hand children a `useCallback(..., [])` wrapper.
- **Module-scope guard for app-once init** (telemetry, a logger) — not a mount effect.

## Out of scope

Excluded on purpose, not forgotten: RSC and Server Components, Server Actions, request
waterfalls behind `await`, hydration flicker and `suppressHydrationWarning`, and
Next-specific bundle tooling. None of it exists in a Vite SPA. If a project ever ships the
React Compiler, demote section 1's manual memoization to review-only — the compiler does it.

## Origin

Mined from ECC `skills/react-performance`, itself adapted from Vercel Labs'
`react-best-practices` (MIT). Rewritten for this stack: store-selector rules restated as
Context, the query-library rule restated as Supabase deduplication, and everything
server-rendered dropped.
