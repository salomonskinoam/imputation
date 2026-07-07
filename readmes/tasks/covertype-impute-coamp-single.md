# covertype-impute-coamp-single: band-resolution record

**Verdict: only 3 tiers realized (#obs) of the ~12 the test could resolve: a lone low outlier under a converged 0.59-0.61 pack. Rescue re-runs (more test data, harder amputation) both re-converged -> intrinsically sample-dependent, eliminated**

## Band

- Eval: `63093dca-ac27-48ad-891b-b0485a5c4d63` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.5330, 0.5928, 0.6094, 0.6096, 0.6104.
- Band (worst to best): 0.5330 to 0.6104.
- Width (spread): 0.0774.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.002473 (static offline resolution: N=15000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.00699.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0774/0.00699 = **12.07**. endpoints ~11 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 12.07.
- only 3 tiers realized (#obs) of the ~12 the test could resolve: a lone low outlier under a converged 0.59-0.61 pack. Rescue re-runs (more test data, harder amputation) both re-converged -> intrinsically sample-dependent, eliminated

## Links

- Task: https://horizon.bespokelabs.ai/tasks/d6237f92-5541-495d-a90e-25316f0247b1
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/63093dca-ac27-48ad-891b-b0485a5c4d63
- Source JSON: `analysis/63093dca-ac27-48ad-891b-b0485a5c4d63/band_supports.json`
