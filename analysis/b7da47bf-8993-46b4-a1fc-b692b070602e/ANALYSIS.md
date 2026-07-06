# adult-impute-cat-multi — solution analysis

**Band: 0.365–0.449, width 0.084, ~8 levels in band (~4 realized). WORKS. Offline LSD 0.0121.**

Recover THREE integer-coded categorical columns in Adult census under MAR: `marital-status`
(col 5, 7 classes, easy ~0.71), `occupation` (col 6, 14 classes, hard ~0.25), `relationship`
(col 7, 6 classes, easy ~0.65). Scored by accuracy vs majority-class baseline
(skill = 1 - err/err_naive), averaged over the 3 columns.

## Per-run table

| Rank | Run | Score | Approach | Other-target cols as predictors? | Pool train+test? | Key differentiator |
|---|---|---|---|---|---|---|
| 1 | run2 | 0.4486 | HGBT, iterative chained, 3 iters, raw integer codes, no label | YES, chained, refits on imputed other-targets each round | YES (vstack) | Clean recipe: pool + chain + **no label feature**. Simplest winner. |
| 2 | run1 | 0.4453 | HGBT, iterative chained, 3 iters, **one-hot** cats + standardized numerics, no label | YES, chained via imputed_targets in feature builder | YES (vstack) | Same recipe as run2; one-hot encoding instead of raw codes (marginally lower). |
| 3 | run5 | 0.3906 | HGBT, iterative chained, 4 iters, mode-init, label as **NaN sentinel** | YES, chained (Xcur carries imputed targets) | YES (vstack) | Pools + chains but adds a label feature that is NaN for all test rows, so a dead/misleading split on the scored rows. |
| 4 | run3 | 0.3767 | HGBT native categorical, **single pass (no iteration)**, label = **predicted** class for test | PARTIAL, other targets included but only their observed values (NaN, never re-imputed) | NO (trains on train rows only) | No chaining, no pooling; leans on a predicted-label feature. Native categorical encoding is the one plus. |
| 5 | run4 | 0.3646 | HGBT, iterative chained, 4 iters, label = **true int (train) vs proba (test)** | YES, chained | NO (fits on X_train_lab only) | Lowest: label feature is a hard train/test **covariate shift** (integer 0/1 on train, continuous proba on test) on the very rows that are scored; also no pooling. |

## What separates top (0.45) from bottom (0.36)

Three levers sort the runs cleanly, and they compound:

1. **Do NOT use the class label as a predictor.** The scored cells live on TEST rows where the
   label is unknown, so any label feature must be faked (predicted, proba, or NaN sentinel),
   creating a train/test mismatch exactly where accuracy is measured. The two winners (run1, run2)
   omit the label entirely. run5 injects it as NaN-for-test (mild drag), run3 as a predicted class,
   and run4 as true-int-vs-proba (the worst mismatch, lowest score).
2. **Pool test features into the imputer.** MAR is per-column, so a test row missing one target
   usually has the other two observed; vstacking train+test lets the model condition on those
   observed cells at fit time. run1/run2/run5 pool; run3/run4 do not.
3. **Iterate/chain the other target columns.** Refitting each target on the *current imputations*
   of the other two (run1, run2, run4, run5) exploits the relationship<->marital<->sex redundancy.
   run3 does a single pass and only sees the other targets' non-amputed values, never re-imputing
   them, so it leaves the redundancy on the table.

The top cluster = pool + chain + no label. Every deviation from that recipe costs a level.

## Why it spreads (vs single-occupation, which converged)

The single-occupation task graded one hard column (~0.25 recoverable) whose signal is nearly
exhausted by "HGBT on all features"; every solution hits the same low ceiling and the band collapses.
Here the score averages three columns, and the two EASY ones (marital ~0.71, relationship ~0.65) are
mutually near-deterministic and strongly tied to sex/age. Because amputation is MAR *per column*, an
affected row almost always has the other two targets observed, so those columns are a live, high-value
predictor. Accuracy on the easy columns is therefore highly sensitive to design choices that most
runs get partially right: whether you chain the imputed other-targets, iterate, pool the test rows,
and whether you avoid poisoning the model with an unusable label feature. Each choice nudges the
easy-column accuracy by a few points, and those dominate the 3-column average, so runs land at
distinct levels (0.36 / 0.38 / 0.39 / 0.44 / 0.45) instead of stacking on one ceiling. The redundancy
that makes the easy columns recoverable is exactly what makes exploitation optional and therefore
variable, and that optionality is the spread.
