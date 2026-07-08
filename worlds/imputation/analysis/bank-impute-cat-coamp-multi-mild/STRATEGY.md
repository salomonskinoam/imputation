# bank-impute-cat-coamp-multi-mild: strategy analysis

**Band: 0.0645–0.1190, spread 0.055, 3 realized tiers, all hugging the floor. Submit YES, but the
spread is a clean two-cluster split on ESTIMATOR FAMILY (HGB low, RandomForest high), not chaining
or feature engineering.**

Bank telemarketing, categorical CO-amputation (mild). Five columns go NaN together on the same rows:
`job`(1), `marital`(2), `education`(3), `day_of_week`(9, unscored), `month`(10). Scored = job, marital,
education, month (skill = 1 - err/err_naive vs mode, averaged). Because all five vanish on the SAME
rows, the co-missing siblings are NOT available as predictors on the affected rows: every solution
correctly predicts from the 11 always-observed columns, and any "chaining" of the other targets can
only feed in the model's own noisy predictions, never truth. No run makes the wrong assumption that a
sibling target is observable on a scored row.

## Per-run table

| Rank | Run | Score | estimator / model | co-amputated siblings as predictors? | encoding / feature choice | distinguishing choice |
|---|---|---|---|---|---|---|
| 5 | run2 | 0.0645 | **HGB** per target, `max_iter=400, depth=4, lr=0.05`, CV-majority fallback | No; observed-11 only | raw int codes; label feature (train), label-free models for test | Single deep HGB; two model sets (with/without label). HGB family. |
| 4 | run4 | 0.0663 | **HGB**, 2-round chained (round-1 probs as extra feats), per-target tuned hp | Chained via **predicted probs** of siblings | raw codes; **label feature = 0 for test** (dead/mismatched on scored rows) | Most elaborate pipeline (stacked probs) yet lands 2nd-lowest. HGB family. |
| 3 | run3 | 0.1024 | **RandomForest**, 500 trees, `min_leaf=5`, CV-majority fallback | No; observed-11 only, chaining explicitly rejected after CV | raw codes; **no label feature** | Plain single-pass RF; docstring notes chaining didn't beat CV, so dropped it. |
| 2 | run5 | 0.1090 | **RandomForest**, per-target tuned (700 trees, depth 6–10) | No; observed-11 only | raw codes; **no label feature** (despite docstring) | Tuned single-pass RF, no chaining/pooling. |
| 1 | run1 | 0.1190 | **RandomForest**, 400 trees, 1-round chained via OOF | Chained via **OOF/hard** sibling predictions | raw codes; **no label feature** | **Pools complete train+test rows** for the imputer + chains on OOF. Only run to pool. |

## What separates top from bottom

The runs fall into two clean clusters and the boundary maps exactly onto estimator family:

1. **Estimator family is the separator.** The two bottom runs (0.0645, 0.0663) both use
   HistGradientBoosting; all three top runs (0.1024–0.1190) use RandomForest. Nothing else splits the
   clusters this cleanly. This matches the documented mild-multi finding on this data (HGB clusters
   low, bagged RF/ExtraTrees high) so it is corroborated prior, not a one-off coincidence.
2. **Elaboration does NOT rescue HGB.** run4 is the single most sophisticated pipeline in the set (two
   rounds, round-1 class probabilities stacked as features, per-target tuned hyperparameters) and it
   still lands 2nd-from-bottom. Effort spent on chaining and stacking did not overcome the family
   choice, which is the strongest evidence the family axis, not the pipeline, is driving the spread.
3. **Pooling + chaining is a minor within-RF bump, not the main axis.** Inside the RF cluster the
   ordering (run3 0.1024 < run5 0.1090 < run1 0.1190) tracks a small gradient: run1 is the only run
   that pools complete train+test rows and chains on OOF, run5 tunes per-target, run3 is plainest.
   The whole within-RF span (~0.017) is a third of the family gap (~0.036).
4. **Label feature is confounded with family, not independently decisive.** Both HGB runs touch a label
   feature (run4 feeds a dead 0 at test; run2 fits label-free test models); all RF runs omit it. Since
   run2 is effectively label-free at test yet still lands bottom, family, not the label, is the driver.

## Verdict

This is best read as **STRATEGY DIVERSITY on estimator family, a legible code driver, not pure luck of
choice**. The two bottom runs share one concrete, identifiable characteristic that all three top runs
avoid (HistGradientBoosting vs RandomForest), the clusters separate cleanly on exactly that axis, and
the most elaborate HGB pipeline (run4) fails to escape the low cluster, which rules out "the bottom
two just wrote worse code." That said, the honesty caveat matters: scores hug the floor (0.06–0.12),
the absolute gap is only ~0.055, and with 5 runs a perfect 2-vs-3 family split carries real
coincidence risk, so confidence is moderate rather than high, propped up mainly by the corroborating
mild-multi prior on this same dataset. Within the winning RF family the finer ordering (pool+chain >
tuned > plain) is a genuine but small skill gradient sitting on top of a shared low ceiling.
