# california-impute-coamp-single: band-resolution record

**Verdict: viable: 4 distinct tiers realized over spread 0.11 (capacity 7.5)**

## Band

- Eval: `0253d895-67be-40b9-a006-15d66a821a7f` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.1507, 0.1521, 0.1923, 0.2106, 0.2619.
- Band (worst to best): 0.1507 to 0.2619.
- Width (spread): 0.1112.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.006087 (static offline resolution: N=8500 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01722.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.1112/0.01722 = **7.46**. endpoints ~6 LSDs apart.
- #observed = 4 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 7.46.
- viable: 4 distinct tiers realized over spread 0.11 (capacity 7.5)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/f771caff-3d94-42f6-9804-7751bb1e06af
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/0253d895-67be-40b9-a006-15d66a821a7f
- Source JSON: `analysis/0253d895-67be-40b9-a006-15d66a821a7f/band_supports.json`
