# Metrics — pick them from what the mistake costs

Every metric makes one kind of error cheap and another likely. State which, and who pays,
before reporting the number.

- **Precision** when a wrong positive costs more — a confident wrong sign shown to someone
  learning is worse than a shrug.
- **Recall** when the miss costs more — a model that refuses half the time teaches nothing.
- **F1** only when the tradeoff really is balanced and you can explain why.
- **Abstention rate alongside both.** With a "nothing" class or a silence gate, accuracy
  over the answered cases is not the system's behaviour. Report answered / refused / wrong
  as three numbers, because lowering the gate moves all three at once.
- **Latency and model size are metrics too**, not footnotes: they bound what can ship to a
  browser at all.

## Seeds: the local rule

Multi-seed runs already exist here — `experiment.py` sweeps 7/13/29/41, `health_train.py`
and `lsefs_train.py` take `--seeds` (the latter defaulting to a single one). The gap has
never been running them; it is the decision rule applied afterwards.

> **Report mean ± sd across seeds. Never the best seed.**

Seed-to-seed spread on this data reaches ~0.024. Any gain smaller than that spread is
noise, no matter how clean the run looked, and the max of four seeds is the noisiest
statistic available. A change worth keeping either moves the mean by more than the spread,
or it is a change kept for a reason other than the metric — which is a legitimate answer,
as long as the ledger says so.

`train.py` is the one where a reported gain cannot be told from luck: it runs a single
seed, and seeds twice with different values — `torch.manual_seed(11)` at line 154 against
`SEED = 7` at line 199 — so which one is in force depends on the path taken. It also seeds
`torch` and `numpy` but not `random` or cuDNN, which is enough for the run to move under a
refactor that touches neither.

## Always against a baseline

A number on its own means nothing. Compare against: the previous shipped model, and the
dumbest thing that could work (most-frequent class, nearest neighbour on the features).
A gain over nothing is not a gain over the baseline.

## Slices before headline

Report the metric per slice you care about — word-level vs continuous signing, per signer,
per hand — before the aggregate. The known tradeoff on this project (vocabulary size
against continuous-signing accuracy) is invisible in the headline number and obvious one
slice down.

## Origin

Metric-and-mistake economics adapted from ECC `skills/mle-workflow`, with its serving,
rollout and team lanes dropped. The seed rule and every file-level fact are from this
project, not from the source.
