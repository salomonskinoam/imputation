# Strategy analysis — california-impute-direct, 5 runs (eval 41ae826f)

biggie-max-polara, 5 runs. Task: recover the NaN'd `median_income` (col 0 of 8) in California housing;
score = `1 − RMSE(method)/RMSE(mean-fill)` over the 8480 amputed TEST cells. Per-run solution code is
`runN_<score>.py`; transcripts `runN_<score>_transcript.md`.

## Band and the axes that move it

Hosted band (worst→best): **0.364 · 0.438 · 0.450 · 0.496 · 0.523**. The runs differ on several axes
at once (pooling, model family/ensemble, iteration, label use, feature engineering) and the scores
spread significantly across them — a rich, multi-axis task, not a one-knob one. The strongest single
sorter *here* is **transductive train+test feature pooling**: since only `median_income` is amputed at
~50%, an inductive fit trains the income regressor on just the ~1.5k train rows with observed income,
while pooling adds the ~8.5k TEST rows that still have observed income → ~10k fit rows vs ~1.5k. The two
poolers take the top two slots; among them and below, model choice and simplicity move the rest.

| rank | run | score | model | **pool train+test?** | iteration | uses label | feature-eng |
|---|---|---|---|---|---|---|---|
| 1 | 3 | **0.523** | single HGB | **YES (`vstack`)** | single-pass | no | none |
| 2 | 4 | 0.496 | BayesianRidge MICE → HGB+ExtraTrees blend | **YES (pool)** | MICE 25-iter + refine | yes (aux NaN col) | log1p |
| 3 | 5 | 0.450 | 8×HGB seed-average | no (inductive) | single-pass | no | log + 4 ratios |
| 4 | 1 | 0.438 | single HGB | no (inductive) | single-pass | yes (train-only variant) | 3 ratios |
| 5 | 2 | 0.364 | HGB + Ridge + GBR | no (inductive) | MICE 3-iter | yes (one-hot) | none |

**The two transductive runs (3, 4) are the top two; all three inductive runs (5, 1, 2) are below
them.** Pooling is worth ~0.05–0.15 of recovery here — the dominant lever. (No leak: pooling shares
test *features* only; test labels never exist in `/data_agent`, and the agent never sees the test set,
its code does the pooling when the grader re-runs it on the full test.)

## Secondary signals

- **Simpler won among the poolers.** run3 (plain single-pass HGB, no label, no feature-eng) beat run4
  (MICE 25-iter + BayesianRidge + HGB/ExtraTrees blend + log + label-aux) by 0.026. All of run4's
  extra machinery added nothing over a clean per-column HGB regression.
- **Feature engineering did not rescue inductive fits.** run5's heavy log+ratio 8-seed ensemble (0.450)
  and run1's ratio features (0.438) still lost to the plain *transductive* run3. Engineering features
  is the wrong lever; the data-access pattern (pooling) dominates.
- **Using the label was neutral-to-harmful.** The three label-users are runs 4, 1, 2 — they include the
  worst (run2) and exclude the best (run3). The discretized price tier carries little extra income
  signal beyond the features, and it is unavailable at test time anyway. Same finding as covertype.
- **MICE over-iteration didn't help.** run2 (worst) is inductive + MICE(3); iterating buys nothing when
  the fit can't see test features. run4 shows MICE(25) only breaks even *because* it also pools.

## Per-run notes

- **run3 (0.523, best):** vstack(train, test) → per-column single-pass HGB on observed rows, native NaN
  handling, column-mean safety net. Deterministic, minimal, no label, no feature-eng. Simplicity + the
  right access pattern.
- **run4 (0.496):** two-stage — transductive IterativeImputer(BayesianRidge, max_iter=25) with an
  all-NaN label column appended, then a per-column HGB+ExtraTrees blend refinement in log-space with
  per-column clipping. Pooling put it 2nd; the complexity cost it 1st.
- **run5 (0.450):** inductive 8×HGB seed-average with log transforms + 4 ratio features
  (rooms/household, beds/room, pop/household, beds/household), early stopping, high L2. Careful but
  inductive → capped below the poolers.
- **run1 (0.438):** inductive single HGB with 3 ratio features; trains a label-aware variant for the
  train fill and a label-free variant for test (honest train/test separation). Inductive ceiling again.
- **run2 (0.364, worst):** inductive MICE (3 iterations) with HGB + Ridge + GradientBoosting and one-hot
  labels, per-column range clipping, no feature-eng. Inductive + iteration on an unseen-test problem =
  the floor of the band. (Its `<20 observed rows → skip` guard does NOT skip median_income — it has
  ~1500 observed train rows — so that is not the cause.)

## Takeaway for the task

The band is driven by a real, interpretable, learnable strategy difference (transductive pooling, then
simplicity), not noise — exactly what a good discriminating task should show. All 5 runs are pairwise
separable (`scratchpad/tiers_california.py`: adjacent flip-rate 0.000, σ̄≈0.0075, ~8 levels over the
band). Same qualitative lessons as covertype (pooling wins, MICE/label don't), now replicated on an
independent dataset.
