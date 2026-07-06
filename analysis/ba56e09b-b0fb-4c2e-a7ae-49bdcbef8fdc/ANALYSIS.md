# california-impute-coamp-multi — 5-run solution analysis

Band: 0.270 · 0.298 · 0.329 · 0.346 · 0.395 (width 0.124, mean 0.327). HGB-MICE oracle 0.082; biggie ~4x the oracle. Widest, cleanest band of the co-amp set (all 5 runs distinct).

## Per-run comparison

| Rank | Run | Score | Pool? | Iteration | Model | Feature-eng | Key differentiator |
|---|---|---|---|---|---|---|---|
| 1 | run5 | 0.3945 | Yes (train-complete + test-complete pooled for no-label imputer) | Single-pass | HGB ensemble (4 seeds), early stopping, max_iter=1500 | log1p(rooms); per-target log-transform of counts; label-vs-nolabel split | Cleanest handling of the label leak: separate label model for train / no-label model for test, PLUS pools test-complete rows into the no-label fit and clips preds to train range |
| 2 | run4 | 0.3456 | No (inductive, train-complete only) | Single-pass | RF + GBM average, in log space | log(rooms) + distances to LA/SF/SD; per-room ratio target log(tgt/rooms) | Per-room ratio reparam + geographic distance features; deliberately drops label (CV showed label hurt on test) |
| 3 | run3 | 0.3287 | No (inductive, train-complete only) | Single-pass | GBM ensemble, 5 seeds | log1p(rooms), lat*lon, lat^2, lon^2, age*log_rooms; per-room ratio target | Same per-room ratio idea as run4 but no distance features and no label at all; income clipped to [0.5,15] |
| 4 | run1 | 0.2976 | No (inductive, train-complete only) | Single-pass | RandomForest per target, min_samples_leaf tuned | Raw obs cols only + one-hot label | Predicts RAW targets (no log / no per-room ratio); uses a proxy RF classifier to fabricate test labels, feeding label noise into test imputation |
| 5 | run2 | 0.2702 | No (inductive, train-complete only) | Single-pass | HGB + RF average | log1p(rooms) only; raw label as feature | WORST: uses the label as a plain feature but has NO test-time label so it silently switches to a no-label ensemble; raw (non-ratio) income target; least feature engineering |

Shared across all 5: all refit on complete rows and apply once (no true transductive re-estimation except run5's test-complete pooling); none run true MICE / iterative chained imputation; none reconstruct households/total_bedrooms first to feed the scored income/population predictions (the co-amputated reconstructors are imputed independently, not used as inputs). Every run correctly identified the {0,3,4,5} co-missing block and the {1,2,6,7} observed block.

## What separates the band

Two orthogonal levers explain the 0.27→0.39 spread. First, TARGET REPARAMETERIZATION: the top three runs (run5 log-transform, run4/run3 per-room-ratio) fit in a space where the skewed count targets are near-homoscedastic, while the bottom two (run1 raw targets, run2 raw income) fit on the RMSE-poor raw scale, directly inflating RMSE on the scored median_income and population. Second, LABEL HYGIENE: the scored rows are TEST rows with no label, so any solution leaning on the label must degrade gracefully. run5 wins by building an explicit no-label imputer for test (and even pooling test-complete rows into it, the only transductive move in the set) and clipping to the train range. run4/run3 take the middle by simply refusing the label. run1 loses ground by fabricating test labels with a proxy classifier and feeding that noise in; run2 loses most by combining raw targets with a fragile label-then-nolabel fallback. Feature engineering (distances, interactions) is a secondary tiebreaker: run4's geographic distances edge it above run3's polynomial terms, but neither matters as much as getting the target space and label handling right. No run touched MICE or reconstructor-first chaining, so that dimension is unexploited headroom, not a band driver here.

## Resolution (empirical bootstrap)

Re-ran the 5 submissions on the full test and bootstrapped test rows (B=300) for σ (`scratchpad/tiers_coamp.py`):
- σ̄ = **0.0116**, LSD(z=1.96) = **0.0323**, band width = 0.126.
- levels over band = 1 + width/LSD = **4.9**.
- adjacent flip-rates: all four **0.000** (every adjacent pair cleanly separated).
- **Empirical distinct levels = 5/5** — the strongest-separating co-amputate task.

WORKS (best co-amp): 5 fully distinct levels, biggie ~4× the oracle (0.082).
