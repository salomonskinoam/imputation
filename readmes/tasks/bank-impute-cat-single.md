# bank-impute-cat-single: band-resolution record

**Verdict: job single converges on a 2nd dataset (four runs bunched ~0.233), confirms single-cat convergence**

## Band

- Eval: `ec944173-61c8-4030-ab90-96a2d938d93b` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.2318, 0.2331, 0.2341, 0.2344, 0.2692.
- Band (worst to best): 0.2318 to 0.2692.
- Width (spread): 0.0374.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.005237 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01481.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0374/0.01481 = **3.52**. endpoints ~3 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 3.52.
- job single converges on a 2nd dataset (four runs bunched ~0.233), confirms single-cat convergence

## Links

- Task: https://horizon.bespokelabs.ai/tasks/970837ef-cf77-4717-b134-e5f8b5dd5ffc
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/ec944173-61c8-4030-ab90-96a2d938d93b
- Source JSON: `analysis/ec944173-61c8-4030-ab90-96a2d938d93b/band_supports.json`
