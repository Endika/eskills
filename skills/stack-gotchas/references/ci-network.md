# CI network — gotchas

## A download works locally and fails on the runner

- **Symptom:** a scheduled job's `fetch` to one source dies with `fetch failed` after about
  10 s, every run, while the same URL answers instantly from home.
- **Means:** 10 s is Node's connect timeout: the TCP handshake never completed, so no
  header (user agent included) was ever sent. The host is refusing the runner's network,
  often everything outside one country.
- **Fix:** confirm from outside with a multi-node TCP check (check-host.net, `check-tcp`):
  if only the home country's node connects, it's a geo-block and no header will fix it.
  Fetch that source from a host in the right country (a cron on the home box) and make
  the CI job keep the source's previous data, named in its PR, instead of shipping it
  empty. Never tunnel the runner into the home network to get around it.
