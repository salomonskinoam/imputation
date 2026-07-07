# bank-impute-cat-coamp-single: band-resolution record

**Verdict: low-cardinality education (K=4) floored to ~0; superseded by bank-impute-cat-coamp-single-job**

## Band

- Eval: `70d88898-69de-41f1-acc7-14d86f5abf5a` (eval); 5 runs, 0 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.0001, 0.0074, 0.0086, 0.0093, 0.0095.
- Band (worst to best): 0.0001 to 0.0095.
- Width (spread): 0.0094.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.010267 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.02904.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0094/0.02904 = **1.32**. endpoints ~0 LSDs apart.
- #observed = 1 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 1.32.
- low-cardinality education (K=4) floored to ~0; superseded by bank-impute-cat-coamp-single-job

## Links

- Task: https://horizon.bespokelabs.ai/tasks/0ab1d73b-33a1-4ca5-b9c2-e0313e2453b9
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/70d88898-69de-41f1-acc7-14d86f5abf5a
- Analysis (strategy, human-authored, updated independently): `../analysis/bank-impute-cat-coamp-single/STRATEGY.md`
- Source JSON: `../analysis/bank-impute-cat-coamp-single/band_supports.json`
