# adult-impute-cat-coamp-multi: band-resolution record

**Verdict: co-amputating BOTH educ predictors over-hardened -> converged ~0.30; mild variant is the WORKS one**

## Band

- Eval: `ecee2395-e78b-4b7e-b007-5c0e5bd70099` (eval); 4 runs, 4 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.2918, 0.2965, 0.3113, 0.3185.
- Band (worst to best): 0.2918 to 0.3185.
- Width (spread): 0.0267.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.004381 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01239.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0267/0.01239 = **3.15**. endpoints ~2 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 3.15.
- co-amputating BOTH educ predictors over-hardened -> converged ~0.30; mild variant is the WORKS one

## Links

- Task: https://horizon.bespokelabs.ai/tasks/e8f5f994-0b95-46bc-a424-43d797c84fe0
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/ecee2395-e78b-4b7e-b007-5c0e5bd70099
- Analysis (strategy, human-authored, updated independently): `../analysis/adult-impute-cat-coamp-multi/STRATEGY.md`
- Source JSON: `../analysis/adult-impute-cat-coamp-multi/band_supports.json`
