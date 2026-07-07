# covertype-impute-direct: band-resolution record

**Verdict: viable: 4 distinct tiers realized over spread 0.11 (capacity 19.0)**

## Band

- Eval: `c56b6c86-36e5-45da-9f9b-8d40ae038f2b` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.2707, 0.2985, 0.3009, 0.3768, 0.3846.
- Band (worst to best): 0.2707 to 0.3846.
- Width (spread): 0.1139.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.002241 (static offline resolution: N=15000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.00634.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.1139/0.00634 = **18.97**. endpoints ~18 LSDs apart.
- #observed = 4 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 18.97.
- viable: 4 distinct tiers realized over spread 0.11 (capacity 19.0)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/ff227290-a39d-4cf8-a162-4d79b580743f
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/c56b6c86-36e5-45da-9f9b-8d40ae038f2b
- Analysis (strategy, human-authored, updated independently): `../analysis/covertype-impute-direct/STRATEGY.md`
- Source JSON: `../analysis/covertype-impute-direct/band_supports.json`
