# adult-impute-cat-coamp-multi-mild — 5-run band analysis

Task: Adult census, categorical co-amputate MULTI. Scored targets = `occupation`,
`relationship`, `marital-status` (integer class codes). On amputated rows `education-num` is
also nulled but `education` (col 3) is kept as an anchor. Score = 1 − err/err_naive vs mode-fill,
clamped [0,1], averaged over the 3 targets. Observed band: 0.2925 → 0.3684, 4/5 distinct levels.

## Per-run comparison (sorted by score)

| score | model / estimator | handles co-amputated education-num? | exploits inter-target structure? | key distinguishing choice |
|---|---|---|---|---|
| 0.2925 (run2) | HistGradientBoostingClassifier, one per target, two variants (with-label / no-label) | Yes: deterministic edu->edu-num lookup, but col 4 NOT fed as predictor | **No.** Explicitly rejects chaining ("avoids error compounding"); each target predicted independently | The **only** gradient-boosting solution; independent per-target; separate with-label vs no-label models for train vs test |
| 0.3105 (run1) | RandomForest, 500 trees | Yes: edu->edu-num lookup, col 4 NOT fed | **Yes:** OOF-proba chaining. Each target's "chain" model sees the other two targets' out-of-fold probability vectors | RF + OOF-probability chaining; predicts test income label first and feeds it. Single estimator, no ensembling |
| 0.348 (run3) | ExtraTreesClassifier, 800 trees | Yes: edu->edu-num lookup, col 4 NOT fed | **Yes:** OOF-trained "full" models use the other two targets' predictions; 4-iteration refinement at inference | Trains chain models on OOF preds (robust to inference noise). Notably uses **no income label at all** |
| 0.3666 (run5) | RandomForest 800 **+** ExtraTrees 800, probabilities averaged | Yes: edu->edu-num lookup, and col 4 **IS** fed as a predictor | **No.** Each target predicted independently (targets excluded from feats, not fed to each other) | RF+ET probability-averaging ensemble; predicts test income label and feeds it. Richest estimator |
| 0.3684 (run4) | RandomForest, 400 trees | Yes: edu->edu-num lookup, col 4 NOT fed | **Yes:** mode-init then 3 rounds of iterative chained imputation using the other two predicted targets | Iterative chaining + income label as feature + predicted test label; most complete pipeline |

## What discriminates the score

The band is set mainly by **estimator choice (a)**, not by chaining or education-num handling. The
single lowest run (0.2925) is the **only** one built on HistGradientBoosting; the other four all use
bagged tree ensembles (RandomForest / ExtraTrees), which fit these high-cardinality categorical
targets better and occupy the whole top of the band. Inter-target chaining (c) does **not** explain
the spread: the 2nd-best run (run5, 0.3666) is fully independent per-target, while the 2nd-worst
(run1, 0.3105) does full OOF-probability chaining, so chaining and score are essentially uncorrelated
here. Education-num handling (b) is a non-factor: edu-num is a deterministic function of the observed
`education` column that every solution keeps, so recovering it adds no signal to the scored targets;
only run5 even feeds col 4 as a predictor, and its edge is far better explained by its RF+ET
probability-averaging ensemble than by the redundant edu-num feature. The final push into the
0.366-0.368 top comes from **richer ensembling** (run5's RF+ET average) or a **more thorough
iterative refinement plus using the income label as a feature** (run4) — the 0.29 solution did neither,
combining a weaker single estimator with a deliberately independent, no-chaining design.
