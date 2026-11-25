"""Greedy minimal test set from a disableBail Stryker report.

usage: prune.py mutation.json [--alone] PRUNABLE_PREFIX [PRUNABLE_PREFIX...]
--alone ignores every non-prunable test (cover the mutants with prunable tests only).
Tests whose file starts with a prunable prefix may be dropped; every other test
is kept. Prints the prunable tests that kill nothing the kept set does not kill.
"""
import json, sys
from collections import defaultdict

report = json.load(open(sys.argv[1]))
args = sys.argv[2:]
alone = '--alone' in args
prefixes = [a for a in args if a != '--alone']
names, files = {}, {}
for tf, data in report.get('testFiles', {}).items():
    for t in data['tests']:
        names[t['id']] = t['name']; files[t['id']] = tf
killers = []
for f in report['files'].values():
    for m in f['mutants']:
        if m['status'] in ('Killed', 'Timeout') and m.get('killedBy'):
            killers.append(set(m['killedBy']))
prunable = {t for t, tf in files.items() if any(tf.startswith(p) or p in tf for p in prefixes)}
fixed = set() if alone else set(files) - prunable
if alone:
    killers = [k & prunable for k in killers if k & prunable]
todo = [k for k in killers if not (k & fixed)]
chosen = set()
while todo:
    score = defaultdict(int)
    for k in todo:
        for t in k & prunable: score[t] += 1
    if not score: break
    best = max(score, key=score.get)
    chosen.add(best)
    todo = [k for k in todo if best not in k]
drop = sorted(prunable - chosen, key=lambda t: (files[t], names[t]))
print(f"prunable={len(prunable)} keep={len(chosen)} drop={len(drop)}")
for t in drop: print(f"  {files[t].split('tests/')[-1]} :: {names[t]}")
