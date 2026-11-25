"""Summarize a Stryker mutation.json: survivors per file and tests that kill nothing."""
import json
import sys
from collections import defaultdict

report = json.load(open(sys.argv[1]))
tests = {}
for path, tf in report.get("testFiles", {}).items():
    for t in tf["tests"]:
        tests[t["id"]] = f'{path} :: {t["name"]}'

kills = defaultdict(int)
covers = defaultdict(int)
totals = defaultdict(int)
for path, f in sorted(report["files"].items()):
    lines = f["source"].splitlines()
    bad = []
    for m in f["mutants"]:
        totals[m["status"]] += 1
        for t in m.get("killedBy") or []:
            kills[t] += 1
        for t in m.get("coveredBy") or []:
            covers[t] += 1
        if m["status"] in ("Survived", "NoCoverage"):
            bad.append(m)
    if not bad:
        continue
    print(f"\n## {path}  ({len(bad)} of {len(f['mutants'])})")
    for m in sorted(bad, key=lambda m: m["location"]["start"]["line"]):
        ln = m["location"]["start"]["line"]
        src = lines[ln - 1].strip()[:110]
        print(f'  L{ln} {m["status"][:4]} {m["mutatorName"]}: {src}  ->  {m.get("replacement", "")[:60]!r}')

print("\n## Tests that reach mutated logic but kill nothing")
for tid in sorted(covers, key=lambda t: tests.get(t, t)):
    if kills[tid] == 0:
        print(f"  {tests.get(tid, tid)}  (covers {covers[tid]})")

print("\n## Totals", dict(totals))
