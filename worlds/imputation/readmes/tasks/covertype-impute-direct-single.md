# covertype-impute-direct-single: band-resolution record

**Verdict: WORKS (clustered): band 0.62-0.71, a 2-vs-3 split; real skill gradient, transductive train+test pooling separates the clusters**

## Band

- Eval: `6ce009ad-9656-4c22-8562-b0447e705265` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.6201, 0.6228, 0.7014, 0.7025, 0.7053.
- Band (worst to best): 0.6201 to 0.7053.
- Width (spread): 0.0852.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.001947 (static offline resolution: N=15000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.00551.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0852/0.00551 = **16.47**. endpoints ~15 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 16.47.
- WORKS (clustered): band 0.62-0.71, a 2-vs-3 split; real skill gradient, transductive train+test pooling separates the clusters

## Links

- Task: https://horizon.bespokelabs.ai/tasks/6ed892d5-8d1b-49f2-b70e-df65a6957813
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/6ce009ad-9656-4c22-8562-b0447e705265
- Analysis (strategy, human-authored, updated independently): `../analysis/covertype-impute-direct-single/STRATEGY.md`
- Source JSON: `../analysis/covertype-impute-direct-single/band_supports.json`
