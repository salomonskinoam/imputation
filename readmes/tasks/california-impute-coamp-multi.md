# california-impute-coamp-multi: band-resolution record

**Verdict: viable: #band_supports = 13.1**

## Band

- Eval: `ba56e09b-b0fb-4c2e-a7ae-49bdcbef8fdc` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.2702, 0.2976, 0.3287, 0.3456, 0.3945.
- Band (worst to best): 0.2702 to 0.3945.
- Width (spread): 0.1243.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.003621 (static offline resolution: N=8500 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01024.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.1243/0.01024 = **13.14**. endpoints ~12 LSDs apart.
- #observed = 5 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 13.14.
- viable: #band_supports = 13.1

## Links

- Task: https://horizon.bespokelabs.ai/tasks/ef7addc9-3664-4b21-814d-75d9ae0a8080
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/ba56e09b-b0fb-4c2e-a7ae-49bdcbef8fdc
- Source JSON: `analysis/ba56e09b-b0fb-4c2e-a7ae-49bdcbef8fdc/band_supports.json`
