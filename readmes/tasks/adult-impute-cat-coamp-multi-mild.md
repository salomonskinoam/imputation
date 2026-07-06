# adult-impute-cat-coamp-multi-mild: band-resolution record

**Verdict: viable: #band_supports = 7.1**

## Band

- Eval: `366d5ba6-60b7-4f2d-8f2c-2f132013f325` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.2925, 0.3105, 0.3480, 0.3666, 0.3684.
- Band (worst to best): 0.2925 to 0.3684.
- Width (spread): 0.0759.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.004381 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01239.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0759/0.01239 = **7.12**. endpoints ~6 LSDs apart.
- #observed = 4 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 7.12.
- viable: #band_supports = 7.1

## Strategy (5-solution analysis)

Spread driven by estimator family: HGB lands ~0.29, bagged RF/ExtraTrees ~0.35-0.37. MICE chaining uncorrelated with score; educ-num recovery inert (deterministic from observed education). Full table: analysis/366d5ba6-60b7-4f2d-8f2c-2f132013f325/ANALYSIS.md.

## Links

- Task: https://horizon.bespokelabs.ai/tasks/d78859a7-2bf0-4ceb-b54f-79bdd5718d4c
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/366d5ba6-60b7-4f2d-8f2c-2f132013f325
- Source JSON: `analysis/366d5ba6-60b7-4f2d-8f2c-2f132013f325/band_supports.json`
