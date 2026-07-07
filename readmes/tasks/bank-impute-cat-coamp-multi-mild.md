# bank-impute-cat-coamp-multi-mild: band-resolution record

**Verdict: viable: 3 distinct tiers realized over spread 0.05 (capacity 5.3)**

## Band

- Eval: `f834e331-1ae0-4063-b789-8cbc4193cb4a` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.0645, 0.0663, 0.1024, 0.1090, 0.1190.
- Band (worst to best): 0.0645 to 0.1190.
- Width (spread): 0.0545.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.004527 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01280.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0545/0.01280 = **5.26**. endpoints ~4 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 5.26.
- viable: 3 distinct tiers realized over spread 0.05 (capacity 5.3)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/aaf3e2af-455c-41cd-ad9d-b622be25f6d6
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/f834e331-1ae0-4063-b789-8cbc4193cb4a
- Source JSON: `analysis/f834e331-1ae0-4063-b789-8cbc4193cb4a/band_supports.json`
