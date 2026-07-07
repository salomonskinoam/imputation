# adult-impute-cat-multi: band-resolution record

**Verdict: viable: 3 distinct tiers realized over spread 0.08 (capacity 7.8)**

## Band

- Eval: `b7da47bf-8993-46b4-a1fc-b692b070602e` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.3646, 0.3767, 0.3906, 0.4453, 0.4486.
- Band (worst to best): 0.3646 to 0.4486.
- Width (spread): 0.0840.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.004381 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01239.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0840/0.01239 = **7.78**. endpoints ~7 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 7.78.
- viable: 3 distinct tiers realized over spread 0.08 (capacity 7.8)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/fe13c0a7-39dc-4bbe-95b2-eae213467db3
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/b7da47bf-8993-46b4-a1fc-b692b070602e
- Source JSON: `analysis/b7da47bf-8993-46b4-a1fc-b692b070602e/band_supports.json`
