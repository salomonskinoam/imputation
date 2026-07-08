# california-impute-direct-multi: strategy analysis

**Band (worst→best): 0.403 · 0.461 · 0.568 · 0.575 · 0.601 — a clean two-group split driven by transductive train+test pooling of the fit, not luck.**

biggie-max-polara, 5 runs. Task: recover the NaN'd `median_income` (col 0) AND `population` (col 4) in
California housing (numeric multi-column). Amputation is per-column MAR (~50% each), so an affected row
usually still has the OTHER target observed; score = `1 − RMSE(method)/RMSE(mean-fill)` over the amputed
TEST cells (skill-vs-mean). Because BOTH columns are amputed independently, each target has observed rows
in both train and test, so pooling roughly doubles the fit set per column.

## Per-run table

| rank | run | score | estimator | **pools train+test for the FIT?** | other-target handling / chaining | feature-eng | distinguishing choice |
|---|---|---|---|---|---|---|---|
| 5 | 2 | **0.403** | old GBR(800) + RF(pop) | **NO — fits on train-only** (`X_all[:n_train]`) | mean-fill base, then MICE-style 3-iter chaining | log feats, log(y) | one-hot label with a **uniform 1/n_classes vector for test rows** (train/test mismatch) |
| 4 | 5 | 0.461 | HistGBR (native NaN) | **NO — fits on `X_train` only** | leaves other target NaN, HGB native; single-pass | log(pop) only | two models per col (with-label / without-label) but inductive ceiling |
| 3 | 1 | 0.568 | HistGBR via `IterativeImputer` | **YES (`vstack`)** | genuine MICE chaining, `max_iter=20` | log1p on 5 cols | pooled + fully chained IterativeImputer, no label |
| 2 | 3 | 0.575 | HistGBR per col | **YES (`vstack`)** | leaves other NaN, HGB native; single-pass | log1p + 6 log-ratios | pooled single-pass HGB with log-ratio features |
| 1 | 4 | **0.601** | 5×HistGBR seed-ensemble | **YES (`vstack`)** | mild chaining (col0 imputed feeds col4 feats) | log + ratio feats | **ratio-target for population**: predict `log(pop/households)`, then ×households |

## What separates top from bottom

- **The dominant lever is transductive pooling of the FIT.** The two runs that train their per-column
  regressor on train rows only (run2 `X_all[:n_train]`, run5 `X_train`) are the bottom two; the three
  runs that fit on the pooled `vstack(train, test)` observed rows (run1, run3, run4) are the top three.
  The gap between the groups is ~0.10 (0.461 → 0.568), far larger than any spread inside a group. Same
  finding as the single-column task, now on the multi variant. Note run2 *vstacks* for prediction but
  still trains on train-only, so it does not get the pooling benefit — a code-legible trap.
- **Chaining/iteration is NOT the driver.** run2 iterates the most (3-pass, mutual updates) and is the
  worst; run3 does no chaining and is 2nd; run1's 20-iter IterativeImputer lands 3rd. Iterating buys
  nothing when the fit can't see test features (run2), and doesn't beat a plain pooled single-pass
  (run3 > run1). Chaining is a neutral secondary lever here.
- **Within the poolers, targeted engineering separates the top.** run4 wins by the domain-aware
  population target `log(pop/households)·households` (persons-per-household is far more stable than raw
  population) plus a 5-seed ensemble. run3's log-ratio features edge run1's plain IterativeImputer.
- **Within the non-poolers, model family + clean features separate them.** run5 (HGB, native NaN, no
  label noise) beats run2 (old sklearn GBR + a uniform-prior label vector that mismatches the trained
  distribution at test time). Both are inductive, so both are capped below every pooler.
- **Label use was neutral-to-harmful.** The two label-users (run2, run5) are the bottom two; the three
  no-label poolers are the top three. The discretized price tier is unavailable at test time anyway,
  and run2's uniform-prior workaround actively injects noise.

## Verdict

This is a **skill / strategy gradient**, not luck of choice. The band splits cleanly along one
code-legible axis — whether the per-column regressor is fit on the pooled train+test observed rows or on
train alone — and that axis puts the three poolers (0.568–0.601) a full ~0.10 above the two inductive
fits (0.403–0.461), exactly reproducing the single-column task's dominant lever on this independent
multi-column setup. The ordering inside each group is also traceable to concrete choices (run4's
ratio-target + ensemble > run3's log-ratios > run1's plain IterativeImputer; run5's HGB + clean features
> run2's old GBR + uniform-label noise), so no rank step is left to chance. The strongest single piece of
evidence is the pooling boundary itself: run2 even `vstack`s the data yet trains on `X_all[:n_train]`, so
it forfeits the pooling gain and lands at the floor — the split is about a specific line of code, not
about which model was picked.
