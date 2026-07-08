# covertype-impute-direct-single: strategy analysis

**Clustered band 0.620->0.705 (2 low, 3 high): the split is one legible code lever, pooling train+test rows into the fit set, not luck.**

biggie-max-polara, 5 runs. Task: recover one NaN'd continuous column (0 Elevation, ~50% missing) in
Covertype under MAR; score = `1 − RMSE(method)/RMSE(mean-fill)` on the held-out test. Every run reaches
for the same core estimator (ExtraTreesRegressor over the other 53 columns); the band is not sorted by
model family. It is sorted by whether the regressor is fit on train rows only (inductive) or on the pooled
train+test observed rows (transductive), exactly the California-style single-target regime.

## Per-run table

| rank | run | score | estimator | uses other 53 cols | fits on | feature-eng | distinguishing choice |
|---|---|---|---|---|---|---|---|
| 5 | 2 | **0.6201** | ExtraTrees(2000, max_feat=0.8) | yes, all 53 as predictors | **train obs only** | none (raw, mean-fill predictors) | inductive: model never sees test rows |
| 4 | 5 | **0.6228** | ExtraTrees(800)+HGB blend 80/20 | yes, +label col for train | **train obs only** | none | inductive; adds label (didn't lift it off the floor) |
| 3 | 3 | **0.7014** | ExtraTrees(1000)+HGB blend 80/20 | yes | **pooled train+test obs** (`vstack`) | none | transductive pooling |
| 2 | 4 | **0.7025** | ExtraTrees(1000), clip to obs min/max | yes | **pooled train+test obs** (`vstack`) | clip only | transductive pooling + extrapolation clamp |
| 1 | 1 | **0.7053** | ExtraTrees(800, max_feat=0.7) | yes | **pooled train+test obs** (concat) | none | transductive pooling, leanest model |

## What separates top from bottom

- **Pooling is the whole gap.** The 0.62 pair (run2, run5) both fit only on `train[obs_mask]`; the 0.70
  trio (run1, run3, run4) all stack train+test and fit on the union of observed rows, so the regressor is
  trained on the actual test feature distribution it must impute back into. With one target column at
  ~50% missing, added transductive rows (and matching feature geometry) are the dominant lever, the same
  finding the California sibling reports.
- **Model family is second-order and roughly cancels.** Within the low group the two use different
  estimators (run2 pure ExtraTrees at 2000 trees; run5 an ET+HGB blend with a label feature) yet land
  0.0027 apart. Within the high group the estimators also differ (blend, clipped ET, lean ET) yet cluster
  within 0.004. Depth of trees, blending, and clipping barely move the needle once pooling is fixed.
- **The label did not rescue the floor.** run5 is the only low run that engineers a feature (a label
  column for train-row imputation), and it still sits in the bottom pair, consistent with the sibling
  world's "labels are neutral-to-harmful" negative. Its missing pooling outweighs its extra feature.

## Verdict

This clustered band is a **real skill/strategy gradient, not luck of choice.** The two low runs are not
algorithmically indistinguishable from the high trio that happened to draw unlucky: they share one
concrete, code-visible deficiency, both fit the regressor on train-observed rows only while all three high
runs pool train+test before fitting. That the two clusters map cleanly onto a single binary lever
(inductive vs transductive), while the incidental choices that vary within each cluster (tree count,
ET-vs-blend, clipping, label use) leave the scores within ~0.004 of each other, is strong evidence the
0.08 gap is caused by the pooling decision rather than sampling noise. The clustered 2-vs-3 shape is
therefore honest: it reflects that pooling is a near-binary craft choice on a single-target task, so runs
land in one of two tiers rather than smearing across a continuum, but the tier a run lands in is earned by
an identifiable decision.
