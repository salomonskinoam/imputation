# adult-impute-cat-coamp-single-occ: band-resolution record

**Verdict: viable: #band_supports = 8.0**

## Band

- Eval: `56635973-4eea-4d80-9bde-f765ae6f7e9e` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.0910, 0.1386, 0.1592, 0.1679, 0.1682.
- Band (worst to best): 0.0910 to 0.1682.
- Width (spread): 0.0772.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.003919 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01108.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0772/0.01108 = **7.97**. endpoints ~7 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 7.97.
- viable: #band_supports = 8.0

## Strategy (5-solution analysis)

Spread driven by regularization/averaging depth, NOT estimator family: a single deep HGB overfits the 14-class target (0.091); shallow regularized ensembles or a bagged RandomForest reach 0.168. Reconstructing the co-amputated education first is a red herring (occupation never consumes it). Full table: analysis/56635973-4eea-4d80-9bde-f765ae6f7e9e/ANALYSIS.md.

## Links

- Task: https://horizon.bespokelabs.ai/tasks/4d90aba0-2d22-4973-b3d4-204d9f813f24
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/56635973-4eea-4d80-9bde-f765ae6f7e9e
- Source JSON: `analysis/56635973-4eea-4d80-9bde-f765ae6f7e9e/band_supports.json`
