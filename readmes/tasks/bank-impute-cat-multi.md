# bank-impute-cat-multi: band-resolution record

**Verdict: viable: 3 distinct tiers realized over spread 0.08 (capacity 7.6)**

## Band

- Eval: `175c88fc-d0ca-41e6-ad7f-30bdcdcfd22a` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.1419, 0.1899, 0.1903, 0.1975, 0.2269.
- Band (worst to best): 0.1419 to 0.2269.
- Width (spread): 0.0850.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.004527 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01280.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0850/0.01280 = **7.64**. endpoints ~7 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 7.64.
- viable: 3 distinct tiers realized over spread 0.08 (capacity 7.6)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/f38b591d-24f3-438a-8f52-db48b286c6ea
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/175c88fc-d0ca-41e6-ad7f-30bdcdcfd22a
- Source JSON: `analysis/175c88fc-d0ca-41e6-ad7f-30bdcdcfd22a/band_supports.json`
