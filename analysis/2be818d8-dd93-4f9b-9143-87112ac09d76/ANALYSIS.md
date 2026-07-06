# adult-impute-cat-single — solution analysis

**Band:** 0.228–0.246, width 0.018, ~2–3 distinct levels. MARGINAL / converged. Offline
resolution LSD 0.0109 (~92 levels available across the score range), so the narrowness is a
real property of the task, not a resolution floor. Every run lands ~0.24.

Task recap: recover the integer-coded categorical `occupation` column (14 classes, col 6) in
Adult census under MAR. Scored by classification accuracy as skill = 1 − err/err_naive, where
err_naive is the majority-class baseline (0 = majority class, 1 = perfect). Grading is deferred /
inductive: the grader re-runs the student code on the hidden full test, so the test-set accuracy
of the fitted classifier is what the score reflects.

## Per-run comparison

| Rank | Run | Score | Classifier | Pool train+test? | Income label used? | Other-cat encoding | Key differentiator |
|---|---|---|---|---|---|---|---|
| 1 | run4 | 0.2462 | RF(1500) + ExtraTrees(1500), proba-summed | No (inductive) | No | Raw integer codes | 2-model tree ensemble, no label mismatch |
| 2 | run5 | 0.2455 | Single RF(800, leaf=5) | No (inductive) | No | OneHotEncoder via ColumnTransformer | One-hot pipeline, no label |
| 3 | run3 | 0.2422 | Single RF(1500, leaf=8) | No (inductive) | No | Manual one-hot of cat cols | One-hot by hand, numerics median-filled |
| 4 | run1 | 0.2415 | 5-seed RF(800, leaf=30) bag | No (inductive) | Yes (two-pass: predicts test income first) | Raw integer codes | Uses label as feature; estimates test label via a separate income RF |
| 5 | run2 | 0.2281 | Single RF(1000, leaf=20) | No (inductive) | Yes (−1 placeholder for test) | Raw integer codes | Lowest; train sees real label, test forced to label=−1 (train/test feature mismatch) |

Notes:
- **Classifier:** all five reach for the same tool, a scikit-learn tree ensemble
  (RandomForest, one adds ExtraTrees). No one tries gradient boosting, kNN, or a neural net.
- **Pool vs inductive:** none pool. Every run fits the occupation classifier on the observed-
  occupation *train* rows only, then predicts the NaN cells in both train and test. run2 and
  run3 compute medians over stacked train+test, but only for NaN safety on predictors, not for
  fitting, so training is inductive in all five.
- **Feature handling:** a split, but an inconsequential one. run1, run2, run4 feed the other
  categorical columns as raw integer codes; run3 and run5 one-hot them (run5 via a proper
  ColumnTransformer pipeline, run3 by hand). Tree ensembles split low-cardinality integer codes
  about as effectively as one-hot, so the two camps land in the same place.
- **Income label:** only run1 and run2 add the income label as a predictor. run1 does it
  carefully (trains a separate income RF, predicts test income in a first pass, then re-predicts
  occupation) so train and test feature vectors match. run2 does it naively: train rows get the
  real label but test rows are hard-coded to −1, creating a train/test feature-distribution
  mismatch that plausibly explains why run2 is the lowest scorer. The three runs that skip the
  label entirely (run3/4/5) are the top three.

## Why it converges

There is essentially one obvious approach and everyone finds it: fit a strong tree-ensemble
classifier on the other census columns to predict occupation, then fill the amputed cells. The
score is dominated by held-out multiclass accuracy, and occupation is only weakly predictable
from the remaining Adult features (age, education, workclass, hours, sex, marital status, etc.).
That mutual-information ceiling is a property of the *data*, not of the modeling choices, so it
pins the reachable accuracy at roughly 0.32–0.33 raw against a ~0.13–0.14 majority baseline,
i.e. skill ~0.24 for any competent classifier. The knobs the runs actually vary, RF vs
RF+ExtraTrees, one-hot vs integer codes, more or fewer trees, leaf size 5 vs 30, all sit on the
flat top of that ceiling and move the score by less than 0.02. The only lever that measurably
hurt was run2's careless label injection (test label = −1), which cost it the bottom of the band.
Nothing a run can do lifts it off the ceiling, so the band collapses to a ~0.018-wide cluster at
0.24 despite ~92 levels of resolution being available. The task discriminates almost nothing
about student skill.
