# california-impute-direct-multi: band-resolution record

**Verdict: viable: #band_supports = 27.1**

## Band

- Eval: (eval id in Links); 2 runs, 2 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.4000, 0.6000.
- Band (worst to best): 0.4000 to 0.6000 (endpoints only, not downloaded).
- Width (spread): 0.2000.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.002712 (static offline resolution: N=8500 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.00767.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.2000/0.00767 = **27.08**. endpoints ~26 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 27.08.
- viable: #band_supports = 27.1

## Links

- Task: https://horizon.bespokelabs.ai/tasks/596e923b-bb5d-4dd8-af48-19a2227c0ee0
