# adult-impute-cat-single: band-resolution record

**Verdict: occupation single converges: one classifier recipe -> shared MI ceiling ~0.24**

## Band

- Eval: `2be818d8-dd93-4f9b-9143-87112ac09d76` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.2281, 0.2415, 0.2422, 0.2455, 0.2462.
- Band (worst to best): 0.2281 to 0.2462.
- Width (spread): 0.0181.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.003919 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01108.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0181/0.01108 = **2.63**. endpoints ~2 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 2.63.
- occupation single converges: one classifier recipe -> shared MI ceiling ~0.24

## Links

- Task: https://horizon.bespokelabs.ai/tasks/afba95ba-144c-47bb-9f1b-6707c4eb67fe
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/2be818d8-dd93-4f9b-9143-87112ac09d76
- Analysis (strategy, human-authored, updated independently): `../analysis/adult-impute-cat-single/STRATEGY.md`
- Source JSON: `../analysis/adult-impute-cat-single/band_supports.json`
