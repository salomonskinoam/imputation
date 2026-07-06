# covertype-impute-direct-single: band-resolution record

**Verdict: viable: #band_supports = 17.5**

## Band

- Eval: (eval id in Links); 2 runs, 2 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.6200, 0.7100.
- Band (worst to best): 0.6200 to 0.7100 (endpoints only, not downloaded).
- Width (spread): 0.0900.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.001934 (static offline resolution: N=15000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.00547.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0900/0.00547 = **17.45**. endpoints ~16 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 17.45.
- viable: #band_supports = 17.5

## Links

- Task: https://horizon.bespokelabs.ai/tasks/6ed892d5-8d1b-49f2-b70e-df65a6957813
