# Pitfalls that actually apply here

The ones from the general ML-engineering canon that are live risks in a solo,
train-here-serve-elsewhere project. The team-and-production ones (feature stores, canary
rollouts, on-call runbooks) are not in this list on purpose.

- **Tuning a threshold on the set you then report.** `sweep.py`, `sweep_continuous.py` and
  `sweep_health.py` exist precisely to search thresholds — so the number that comes out of
  a sweep is a _fitted_ number. Hold out a set the sweep never touches, or report the
  sweep's number as what it is: an upper bound.
- **An offline gain hiding a slice regression.** The headline can rise while the slice you
  actually ship to gets worse. This has already happened here once, trading isolated-word
  accuracy for continuous signing. Check slices before believing a total.
- **Train/serve skew.** Training computes features in Python; the app computes them in
  TypeScript against ONNX Runtime. Two implementations of "the same" preprocessing drift
  silently and the symptom looks like a model problem. Keep a parity check that runs the
  same input through both and compares — `make_parity.py` / `parity.json` is that check,
  and it only protects what it covers.
- **A convention that disagrees with itself.** Handedness, axis order, normalization: if
  two files encode opposite conventions the model learns both and neither. Consistency with
  the data beats anatomical correctness.
- **Reproducibility resting on an un-versioned artifact.** A checkpoint whose seed, data
  revision and feature code are not recorded cannot be compared against its successor.
  Stamp the run, not just the metric.
- **Padding waste mistaken for model cost.** Batch padding can dominate the training step
  before the model does. Profile the step before optimizing the architecture.
- **Rollback by retraining.** Keeping the previous exported model means a bad result is one
  file swap away from undone, instead of a training run away.

## Origin

Selected from the anti-patterns in ECC `skills/mle-workflow`, keeping only what is a live
risk in a solo, train-here-serve-elsewhere project. The parity check, the threshold sweeps
and the padding cost are local, not from the source.
