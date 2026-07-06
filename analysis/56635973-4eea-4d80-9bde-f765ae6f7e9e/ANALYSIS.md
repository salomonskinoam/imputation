# adult-impute-cat-coamp-single-occ — 5-run analysis

Task: Adult census, categorical co-amputate SINGLE. Scored target = `occupation`
(col 6, 14 integer classes, mode 0.13). On amputated rows `education` (col 3) and
`education-num` (col 4) are also nulled (unscored, must be filled). Score =
1 - err/err_naive vs mode baseline, clamped [0,1]. Band: 5 runs span 0.091 -> 0.168,
capacity ~8, 3 realized levels. Slot WORKS.

## Per-run table (sorted by score)

| score | estimator / model | co-amputated education / education-num | feature engineering / distinguishing choice |
|---|---|---|---|
| 0.091 (run2) | **Single HGB**, `max_iter=400/500, lr=0.05, max_depth=6` (deep, one model per target) | **Model-imputes** them with dedicated HGB classifiers, then reconciles edu-num from education via a 1-1 map. But cols 3/4 are excluded from the occupation feature set, so this work never helps the score. | Adds a predicted income-label column (true label for train, `label_clf` HGB prediction for test). Deep unregularized trees, no averaging. |
| 0.1386 (run1) | **Ensemble**: HGB1 (`1500 iter, depth 3, lr 0.01`) + HGB2 (`1000, depth 3, lr 0.02, l2=1`) + RF (800 trees, leaf 5) + KNN (150, distance), weighted 1/1/0.5/1 on probs | **Mode-fill** only (global mode/median, not modeled). | Income-label feature (true train / predicted test). OHE+scaler pipeline for the KNN branch; shallow regularized HGB. |
| 0.1592 (run5) | **Single RandomForest**, `1500 trees, min_leaf=5, max_features=sqrt` | **Mode-fill** only. | OneHotEncoder on the 6 available categoricals; income-label feature (predicted for test via a second RF). A single bagged model, no HGB. |
| 0.1679 (run3) | **HGB ensemble, 5 seeds** identical hyperparams, all heavily regularized: `max_iter=200, lr=0.01, max_leaf_nodes=7, min_samples_leaf=60, l2=1`; averages class probs | **Median-fill** only. | **No income-label feature at all** — occupation predicted purely from the 11 always-observed columns. Shallowest/most-regularized trees, pure seed-averaging. |
| 0.1682 (run4) | **Mixed ensemble**: 5 HGB (`depth 3-4, lr 0.03-0.05, iter 80-150, min_leaf 25-40`) + 2 RF (500 trees, leaf 10/20); averages probs | **Mode-fill** only. | Income-label feature at fit time (true label), but at TEST substitutes a constant majority label, so the label column is effectively dead on the scored split. Broadest ensemble. |

## Discriminating skill

The separator is **regularization + probability-averaging across models, not estimator
family and not education reconstruction**. The lone low run (0.091) is the only one using a
single unregularized deep HGB (`max_depth=6`) that overfits the 14-class target; every run
above it either averages many shallow, strongly-regularized learners (run3/run4/run1) or uses
an inherently bagged single model (run5's RandomForest). Education/education-num handling does
NOT discriminate: all five exclude cols 3/4 from the occupation predictor (they are co-nulled
on the same rows, so useless as predictors), and run2's dedicated education imputer is pure
wasted effort that never touches the score, so option (b) reconstruct-first is a red herring.
Feature engineering is also not decisive: the two top runs lean least on the income-label
feature (run3 omits it entirely, run4 feeds a constant at test), while the low run uses it.

## Contrast with the mild-multi finding

Mild-multi's spread was driven by **estimator family** (HGB clustered low, bagged RF/ExtraTrees
high). Occupation-single shows a **different discriminator**: HGB is NOT inherently low here —
the two top scores (0.168, 0.168) are both HGB-based ensembles, and a single RandomForest lands
mid-pack (0.159). What matters is **within-family regularization and ensembling**: shallow +
seed/model-averaged (win) vs single deep tree (lose). So the axis shifted from "which estimator"
to "how regularized / how averaged," with estimator family largely washing out once variance is
controlled.
