# california-impute-direct-multi: band-resolution record

**Verdict: WORKS (widest numeric band): 0.40-0.60, evenly spread; real skill gradient, transductive pooling of the per-column fit**

## Band

- Eval: `cdb91691-0e32-49fa-a58f-42218dc0f062` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.4033, 0.4608, 0.5684, 0.5745, 0.6005.
- Band (worst to best): 0.4033 to 0.6005.
- Width (spread): 0.1972.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.002701 (static offline resolution: N=8500 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.00764.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.1972/0.00764 = **26.81**. endpoints ~26 LSDs apart.
- #observed = 4 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 26.81.
- WORKS (widest numeric band): 0.40-0.60, evenly spread; real skill gradient, transductive pooling of the per-column fit

## Links

- Task: https://horizon.bespokelabs.ai/tasks/596e923b-bb5d-4dd8-af48-19a2227c0ee0
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/cdb91691-0e32-49fa-a58f-42218dc0f062
- Analysis (strategy, human-authored, updated independently): `../analysis/california-impute-direct-multi/STRATEGY.md`
- Source JSON: `../analysis/california-impute-direct-multi/band_supports.json`
