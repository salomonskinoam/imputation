# covertype-impute-coamp-single — 5-run solution analysis

**Band:** width 0.077, mean 0.591; HGB-MICE oracle 0.321; MARGINAL — clustered high (0.533 · 0.593 · 0.609 · 0.610 · 0.610).

Task: delete `Elevation` (0) plus three co-amputated reconstructors (`Horizontal_Distance_To_Hydrology` col 3, `Soil_Type10` col 20, `Wilderness_Area4` col 53) on the affected rows; hide test. Only `Elevation` recovery is scored; the other three must be imputed to pass the gate but are not graded.

## Per-run comparison

| Rank | Run | Score | Pool or inductive | Iteration | Model (Elevation) | Key differentiator |
|---|---|---|---|---|---|---|
| 1 (best) | run2 | 0.6104 | Inductive (fit on complete rows, predict miss) | Single-pass | ET(800)+RF(500)+HGB blend, ET-heavy w=(0.7,0.15,0.15) | Deterministic one-hot recovery fed back as inputs; ET-dominant ensemble; clip to observed min/max |
| 2 | run3 | 0.6096 | Pool (vstack train+test, then impute) | Single-pass | ExtraTrees(800) only | Deterministic one-hot; single strong ET; clip |
| 3 | run5 | 0.6094 | Inductive | Single-pass | ExtraTrees(500) only | Deterministic one-hot; single ET; the "plain" reference solution |
| 4 | run1 | 0.5928 | Inductive | Single-pass | ET(500)+HGB blend, w_hgb=0.4 (ET-weighted) | One-hots imputed by CLASSIFIER ensemble (predict_proba), NOT deterministically — slightly weaker reconstructors feeding Elevation |
| 5 (worst) | run4 | 0.5330 | Inductive | Single-pass | HistGradientBoosting only (NO ExtraTrees) | Only run with zero ExtraTrees; adds 7-dim CV soft-label features; HGB alone underperforms ET on this target |

Notes:
- Nobody used MICE / iterative chained imputation. All 5 are single-pass (fit predictors on the observed columns, predict the missing cells once). The three co-amputated reconstructors are handled up front, then Elevation is predicted from a now-complete feature row.
- Reconstructor handling splits two ways. Runs 2/3/4/5 recover `Soil_Type10` and `Wilderness_Area4` **deterministically** from the one-hot sum constraint (missing cell = 1 − sum of siblings) — exact. Run1 alone treats them as ML classification targets and imputes class-1 probability, which is noisier. `Horizontal_Distance_To_Hydrology` is regressed by everyone (no closed form).
- Label use: only run3 and run4 load `train_labels`. Run3 loads but effectively ignores it; run4 is the only one that actually uses labels, folding a 5-fold CV soft-label distribution in as 7 extra regressor features. It still finishes last — labels did not rescue the HGB-only choice.
- Feature engineering is otherwise minimal: everyone predicts Elevation from the ~50 always-observed columns (plus the recovered one-hots). Clipping predictions to the observed Elevation range appears in runs 2/3/4 (harmless, roughly neutral).

## Why it clusters (marginal)

The hypothesis holds. The 44 residual soil/wilderness one-hot indicators plus slope/aspect/hillshade encode terrain so tightly that Elevation is largely determined by the observed row: cover type and soil are elevation-stratified in Covertype, so any sufficiently expressive tree model reads Elevation off the same signal and converges to nearly the same answer. That is why four independent solutions with different plumbing (pool vs inductive, single ET vs three-model blend, with or without deterministic one-hot recovery) all land within 0.001–0.018 of each other around 0.61 — the ceiling is set by the data's residual information about Elevation, not by engineering. The single outlier, run4 at 0.533, is the **only run that omits ExtraTrees** and leans entirely on HistGradientBoosting. On this high-cardinality, one-hot-dominated feature space ExtraTrees' randomized-split variance reduction fits Elevation better than boosted histograms, and its absence (not the co-amputation, not the label features, not pooling) is what drops run4 ~0.06 below the cluster. Co-amputating the three reconstructors barely moves the strong runs because the surviving 44 indicators carry Elevation on their own; the amputation removes redundant, not decisive, signal. The task is marginal because the floor (naive/HGB-MICE oracle 0.321, HGB-only run 0.533) and the clustered strong ceiling (~0.61) leave a narrow, model-choice-driven band rather than a wide skill gradient.

## Resolution (empirical bootstrap)

Re-ran the 5 submissions on the full test and bootstrapped test rows (B=300) for σ (`scratchpad/tiers_coamp.py`):
- σ̄ = **0.0036** (small — high-N, 15k Elevation cells), LSD(z=1.96) = **0.0101**, band width = 0.076.
- levels over band = 1 + width/LSD = **8.5** (theoretical; but the runs bunch, so realized is fewer).
- adjacent flip-rates: run4→run1 0.00, run1→run5 0.00, run5→run3 **0.047**, run3→run2 **0.083** (top two merge).
- **Empirical distinct levels = 4/5** — the ExtraTrees cluster resolves into ~3 tight steps + the HGB-only floor.

MARGINAL: 4 levels *technically* resolve because σ is tiny, but the band is narrow (0.076) and the
separation is a single model choice (ExtraTrees vs not), not a skill gradient — high mean, low headroom.
