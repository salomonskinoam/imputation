# california-impute-direct: band-resolution record

**Verdict: viable: 5 distinct tiers realized over spread 0.16 (capacity 14.1)**

## Band

- Eval: `41ae826f-3fec-4b9a-938e-bbcbd0e225df` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.3645, 0.4376, 0.4499, 0.4964, 0.5227.
- Band (worst to best): 0.3645 to 0.5227.
- Width (spread): 0.1582.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.004267 (static offline resolution: N=8500 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01207.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.1582/0.01207 = **14.11**. endpoints ~13 LSDs apart.
- #observed = 5 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 14.11.
- viable: 5 distinct tiers realized over spread 0.16 (capacity 14.1)

## Strategy (5-solution analysis)

Sorted by transductive train+test POOLING: one half-missing column means pooling the observed test-feature rows 6-7x's the regressor's fit rows; both poolers take the top two, the three inductive fits are the bottom three, simplicity breaks ties. MICE over-iteration and using the label are neutral-to-harmful. Full table: analysis/41ae826f/ANALYSIS.md.

## Links

- Task: https://horizon.bespokelabs.ai/tasks/76263f44-25bb-48a4-82f1-6383a214e8f8
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/41ae826f-3fec-4b9a-938e-bbcbd0e225df
- Source JSON: `analysis/41ae826f-3fec-4b9a-938e-bbcbd0e225df/band_supports.json`
