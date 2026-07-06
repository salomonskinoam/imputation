# adult-impute-cat-coamp-single: band-resolution record

**Verdict: low-cardinality relationship (K=6) floored; superseded by adult-impute-cat-coamp-single-occ**

## Band

- Eval: `ef3a3efd-09a0-43fe-a4ba-d970ba310950` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.0511, 0.0617, 0.0623, 0.0702, 0.0738.
- Band (worst to best): 0.0511 to 0.0738.
- Width (spread): 0.0227.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.008384 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.02371.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0227/0.02371 = **1.96**. endpoints ~1 LSDs apart.
- #observed = 1 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 1.96.
- low-cardinality relationship (K=6) floored; superseded by adult-impute-cat-coamp-single-occ

## Links

- Task: https://horizon.bespokelabs.ai/tasks/dc36b759-947b-4c4a-96d4-13ba958ee3ff
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/ef3a3efd-09a0-43fe-a4ba-d970ba310950
- Source JSON: `analysis/ef3a3efd-09a0-43fe-a4ba-d970ba310950/band_supports.json`
