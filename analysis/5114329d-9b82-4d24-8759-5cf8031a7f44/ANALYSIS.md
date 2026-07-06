# covertype-impute-coamp-multi — 5-solution analysis

Band: width **0.041** (0.288 · 0.288 · 0.291 · 0.300 · 0.329), mean **0.299**; HGB-MICE oracle 0.153. MARGINAL/weak — the narrowest band in the world.

## Per-run comparison

| rank | run | score | pool (train+test)? | iteration | model (continuous targets) | key differentiator |
|---|---|---|---|---|---|---|
| 1 | run1 | 0.3290 | YES (vstack train+test to fit) | single-pass | HGB + RF + ET averaged (0.4/0.3/0.3) | Only run that pools test rows into the fit AND blends a boosted learner (HGB) into the ensemble |
| 2 | run4 | 0.3002 | no (train obs rows only) | single-pass | RF + ET + distance-weighted KNN, /3 | Adds scaled-feature KNN to the tree ensemble |
| 3 | run3 | 0.2906 | no (train obs rows only) | 2-stage MICE-lite (OOF stage-1 -> augment) | RF only (500 trees) | Only MICE-style run; per-column stage choice (col0 stage1, cols 3/5/9 stage2) |
| 4 | run2 | 0.2882 | no (train obs rows only) | single-pass | RF only (500 trees, min_leaf=2) | Plainest: single RF per target |
| 5 | run5 | 0.2877 | no (train obs rows only) | single-pass | RF + ET averaged (0.5/0.5) | RF+ET blend, no KNN/HGB, no pooling |

Shared across all 5 (the reason it bunches):
- **Reconstructors handled identically and near-perfectly.** Every run recovers Soil_Type10 (col 20) and Wilderness_Area4 (col 53) from the one-hot sum-to-one constraint (`1 - sum(other group members)`). But cols 20/53 are co-amputated reconstructors that are NOT scored, so this shared perfect step contributes nothing to score spread. The scored targets are Elevation (0), Roadways (5), Fire_Points (9); col 3 (Hydrology) is also co-amputated and unscored.
- **Same feature pool.** All use the 48 always-observed columns (54 minus the 6 co-amputated) as predictors. Once reconstructors are filled, everyone feeds essentially the same design matrix to a tree regressor.
- **Same model family.** All scored-target regressors are tree ensembles (RF/ET/HGB) at similar capacity (400-500 trees). No linear model or tuned GBM alternative that would move the needle.
- **No label use.** None of the 5 uses `y_train` for imputation (run1 loads it but never feeds it; others load/ignore). Labels are the one signal that could separate runs, and nobody exploits it.

## Why it's bunched (weak)

Two forces compress this band. First, **the scored quantity is a mean over 3 continuous targets** (Elevation, Roadways, Fire_Points), and averaging independent per-target recovery scores shrinks spread by roughly 1/sqrt(3) versus any single target: a run that gets lucky on one target is pulled back toward the mean by the other two. Second, and more decisive, **the residual soil/wilderness indicator signal is strong and identical for everyone**: after the two one-hot reconstructors are recovered exactly (a deterministic step all 5 share), the 44 binary soil/wilderness dummies plus the remaining continuous features carry enough signal that any competent tree regressor converges to nearly the same predictions. Elevation in particular is tightly determined by soil type and hillshade/aspect, so RF, ET, and HGB all land in the same neighborhood. The differentiators that exist are second-order: run1 edges ahead (0.329) because it is the only run that both (a) pools the hidden test rows into the fit, enlarging the training set, and (b) mixes a boosted learner (HGB, weight 0.4) into the ensemble, giving a slightly lower-bias fit than the pure bagging ensembles. run4's KNN and run3's MICE-lite two-stage refit each buy a hair over the plain RF (run2) / RF+ET (run5) baselines, but with the reconstructor step neutralized and the score averaged over 3 well-determined targets, none of these choices can open more than ~0.04. The band is real but marginal: the task barely distinguishes modeling skill because the easy shared structure dominates.

## Resolution (closed-form; empirical bootstrap deferred)

The empirical bootstrap re-run (`scratchpad/tiers_coamp.py`) was heavy and interrupted for this task, so
these are the closed-form ruler numbers (σ = (1−skill)·√((κ−1)/4)/√N averaged over the 3 targets, N ≈
15k cells/col, κ≈4):
- σ ≈ **0.0029**, LSD(z=1.96) ≈ **0.0079**, band width = 0.041.
- levels over band = 1 + width/LSD = **6.2** (theoretical).
- distinct among the 5 runs ≈ **3/5**: {0.288, 0.288, 0.291} merge, then {0.300}, {0.329}.

MARGINAL/weak: even though σ is small, the band is only 0.041 wide and three runs are near-tied at the
floor — the residual soil-indicator signal + 3-target averaging leave almost no skill gradient.
