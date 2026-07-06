# diabetes-impute-cat-multi: band-resolution record

**Verdict: clinical modality; 3 valid runs converge ~0.27; marginal**

## Band

- Eval: (eval id in Links); 3 runs, 3 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.2600, 0.2700, 0.2800.
- Band (worst to best): 0.2600 to 0.2800 (3 valid runs + 2 agent crashes on the 90-103-class diag cols; eval id not recorded).
- Width (spread): 0.0200.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.005299 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01499.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0200/0.01499 = **2.33**. endpoints ~1 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 2.33.
- clinical modality; 3 valid runs converge ~0.27; marginal

## Links

- Task: https://horizon.bespokelabs.ai/tasks/28bebcc0-f53e-4e2d-8518-5888e7d8c2a8
