# Supabase — gotchas

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

## The Supabase MCP can't apply DDL

- **Symptom:** schema changes through the MCP server don't take; only reads work.
- **Means:** that surface is read-oriented; DDL isn't part of what it will execute.
- **Fix:** send DDL to the Management API —
  `POST /v1/projects/{ref}/database/query` with the PAT. Related: under WSL the MCP's OAuth
  never closes its callback, so it needs a stdio wrapper with a PAT on disk instead.
