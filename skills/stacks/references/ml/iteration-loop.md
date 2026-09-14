# The iteration loop — mistake before metric

For the Python/PyTorch training side of a project whose model ships elsewhere (Esku
trains in `tools/train/` and serves ONNX in the browser). Solo project, no serving tier,
no A/B, no dashboards — so the discipline here is about **deciding what to change next**,
not about MLOps machinery.

The loop that works is not `train → metric → ship`. It is:

> **mistake → cluster → hypothesis → experiment → evidence**

## After every run that changes anything

1. **Split the failures** into false positives, false negatives, **abstentions** and
   low-confidence cases. Abstention is a first-class outcome when the model has a "nothing"
   class or a silence gate — a wrong answer and a refusal are not the same failure and must
   not be averaged together.
2. **Cluster by shared trait** — signer, hand, lighting, sequence length, word vs
   continuous signing, position in the sequence. A cluster is a hypothesis in waiting; a
   list of individual errors is not.
3. **Separate the model's fault from everything else**: a data bug, an ambiguous label, a
   convention that disagrees with itself across files, or a mismatch between how features
   are computed in training and in the app. Most "model problems" that survive a week turn
   out to be one of the last three.
4. **Route each big cluster to exactly one move**: better labels, better features, a
   different threshold, or a different model. Naming the move before running the experiment
   is what makes the result falsifiable.
5. **Keep every important mistake** as a regression check — a case in the bench, a slice in
   the evaluation, a line in the parity check.

## The ledger

One record per iteration, next to the code — not in a chat log, not in a notebook cell:

```text
Iteration:
Change:
Why this mattered:
Metric movement (mean ± sd across seeds):
Slice movement (which slices got worse):
False positives / false negatives / abstentions:
Unexpected errors:
Decision:
Tradeoff accepted:
Regression added:
```

**"Tradeoff accepted" and "slice movement" are the two lines that earn the whole ledger.**
A change that improves the headline number while quietly costing a slice is the normal
case, not the exception — and without those lines it gets remembered as a clean win.

## Origin

Mined from ECC `skills/mle-workflow`, cut to a single-person project with no production
serving. The serving, rollout, monitoring and team lanes of that skill are deliberately
dropped; its own scope note says to use only the lanes that fit.
