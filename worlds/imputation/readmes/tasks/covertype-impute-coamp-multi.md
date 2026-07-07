# covertype-impute-coamp-multi: band-resolution record

**Verdict: tight pack ~0.29 (width 0.04) with one high outlier; rescue re-runs stayed converged -> covertype's redundant residual gives intrinsically low separation, eliminated**

## Band

- Eval: `5114329d-9b82-4d24-8759-5cf8031a7f44` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.2877, 0.2882, 0.2906, 0.3002, 0.3290.
- Band (worst to best): 0.2877 to 0.3290.
- Width (spread): 0.0413.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.002305 (static offline resolution: N=15000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.00652.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0413/0.00652 = **7.33**. endpoints ~6 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 7.33.
- tight pack ~0.29 (width 0.04) with one high outlier; rescue re-runs stayed converged -> covertype's redundant residual gives intrinsically low separation, eliminated

## Links

- Task: https://horizon.bespokelabs.ai/tasks/9e443879-143e-43f7-a6cb-6c57bdb03239
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/5114329d-9b82-4d24-8759-5cf8031a7f44
- Analysis (strategy, human-authored, updated independently): `../analysis/covertype-impute-coamp-multi/STRATEGY.md`
- Source JSON: `../analysis/covertype-impute-coamp-multi/band_supports.json`
