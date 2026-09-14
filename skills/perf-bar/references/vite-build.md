# Vite build and bundle

The bundle-side companion to `react.md`, for the Vite build that every app in the fleet
ships through. Same rule as the lens: measure first (`vite build` prints the chunk table,
`vite --profile` explains a slow dev server), then pull a lever.

## Chunking

- **Split vendors with the object form of `manualChunks`** — name a handful of groups you
  actually want cached separately.
- **Never split per package.** `id.split('node_modules/')[1]` as a chunking rule mints one
  chunk per dependency: hundreds of tiny files, each with its own request and its own
  cache entry. It looks like optimization and is the opposite.
- **Route-level dynamic `import()`** is the split that pays. A heavy component behind an
  interaction should not be in the first-load bundle.

## Weight

- **Don't ship `@vitejs/plugin-legacy` by default.** It inflates the bundle by roughly 40%
  and breaks source-map-based bundle analyzers. Add it when a real target browser demands
  it, not preventively. (No app in the fleet uses it today — that's the right default.)
- **Import paths must stay statically analyzable** or nothing is tree-shaken.

## Dependency pre-bundling

- **`optimizeDeps.include`** for CJS dependencies with interop problems — pre-bundling is
  what makes them ESM-shaped.
- **A stale `node_modules/.vite` cache produces phantom errors** that survive restarts and
  make no sense against the source. Clear it whenever dependencies change; it is the first
  thing to suspect when an error contradicts the code you are reading.
- **`server.warmup.clientFiles`** to pre-transform the routes you open every time.

## What hashed chunks mean at deploy time

A new build renames every chunk. A user with the page already open then requests a
filename that no longer exists, and the failure surfaces as a dynamic `import()` rejecting
mid-navigation — not as an obvious 404. Two mitigations, and they compose:

- keep the previous `dist/assets/` live for a deployment window;
- catch the dynamic-import failure in the router and force one reload.

For a PWA on `autoUpdate` this mostly resolves itself, which is exactly why the residual
case is confusing when it does appear — see the stale-deploy note in `stack-gotchas`.

## Not a lever

`vite preview` is a smoke test for the built bundle, never a production server. And
`vite build` only transpiles: type errors ship silently unless the build script runs
`tsc` first — which every app here already does.

## Origin

Mined from ECC `skills/vite-patterns` (Vite 7/8 era: Rolldown, `oxc` minifier), keeping
what applies to a static SPA build. Security items from the same source live in
`security-bar`, not here.
