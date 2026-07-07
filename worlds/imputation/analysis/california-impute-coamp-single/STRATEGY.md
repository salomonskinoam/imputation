# california-impute-coamp-single — 5-solution analysis

Band (sorted): 0.151 · 0.152 · 0.192 · 0.211 · 0.262 | width 0.111 | mean 0.194. HGB-MICE oracle was 0.000.

| rank | run | score | pool train+test? | iteration | model / ensemble | reconstructs total_rooms first? | key differentiator |
|---|---|---|---|---|---|---|---|
| 1 | run2 | 0.262 | YES (vstack observed train+test → X_pool) | single-pass | col0: RF+ExtraTrees+HGB mean; col2: RF on log1p | NO (both predicted directly from cols {1,3,4,5,6,7}, independent models) | transductive pooling of test observed rows into the label-free income imputer; plain raw-feature ensemble, no over-engineering, no KNN drag |
| 2 | run5 | 0.211 | NO (inductive, complete train rows only) | single-pass | GradientBoosting + HGB + ExtraTrees, equal mean | NO (income + rooms fit independently, raw target) | richest feature set (log1p, ratios, lat*lon, lat^2, lon^2, lat+lon) on income directly; no KNN, no label |
| 3 | run1 | 0.192 | means only pooled; models fit on train obs | single-pass | HGB, blended 50/50 with lat/lon KNN for col0 | NO (independent per-column; col2 GBM, col0 GBM+geoKNN) | 50/50 geographic KNN blend on income — helps modestly but the KNN half caps the gain |
| 4 | run3 | 0.152 | NO (inductive, train obs only) | single-pass | RF+HGB+ExtraTrees+KNN, hand-tuned per-column blend weights | NO (both columns via same blended_predict, independent) | hardcoded CV blend weights (income no-label = 0*RF, 1*HGB, 0.75*ET, 0*KNN); one-hot label used for train only, no test lift; overfit weights |
| 5 | run4 | 0.151 | NO (inductive, complete rows only) | single-pass | 2xHGB + RF + ExtraTrees on log(target), weighted 0.40/0.25/0.20/0.15 | NO (independent per-column ensembles) | logs the income target and predicts in log-space + heavy weight on a deep HGB; log transform on already-compact income hurts, explicitly drops the label |

## What separates the band

Every solution is single-pass and predicts income directly from the six always-observed columns; nobody ran MICE/IterativeImputer, and nobody used the reconstructed `total_rooms` as an input to income (they treat the two targets as independent regressions). So iteration and chaining are NOT what moved the score. Two things did. First, transductive pooling: run2 (best) is the only one that vstacks the observed test rows into the label-free income imputer, giving the model more of the true test-region distribution to fit — a real, if small, edge on a location-driven target. Second, restraint on the income model: the winners (run2, run5) feed the raw target to a plain tree ensemble with light or rich engineered features and no gimmicks, while the losers add machinery that fights this fragile signal — run4 predicts income in log-space (wrong for an already-compact variable) and run3 leans on overfit hand-tuned blend weights and a KNN component. The label is a red herring: it is only available on train, so any label-aware model (run3's one-hot, run1/run2's with-label train branch) helps train imputation that is never scored and does nothing for the hidden test. Since California income has no single strong predictor and `total_rooms` is co-amputated, the whole band sits low (0.15–0.26); the separation is entirely about which model best fits a weak raw-feature combination without distorting it, not about algorithmic sophistication.

## Resolution (empirical bootstrap)

Re-ran the 5 submissions on the full test and bootstrapped test rows (B=300) for σ (`scratchpad/tiers_coamp.py`):
- σ̄ = **0.0060**, LSD(z=1.96) = √2·1.96·σ̄ = **0.0166**, band width = 0.113.
- levels over band = 1 + width/LSD = **7.8**.
- adjacent flip-rates: run4→run3 **0.087** (merge), run3→run1 0.00, run1→run5 0.00, run5→run2 0.00.
- **Empirical distinct levels = 4/5** (only the two near-tied floor runs, 0.148/0.154, merge).

WORKS: a genuine 4-level band the HGB-MICE oracle (0.00) entirely missed.
