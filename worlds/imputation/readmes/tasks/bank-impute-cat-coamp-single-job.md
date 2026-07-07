# bank-impute-cat-coamp-single-job: band-resolution record

**Verdict: floored: job's single carrier is education; co-amputating it collapses recovery to naive**

## Band

- Eval: `7f7f6ea9-2ba4-4895-9e75-8349b18aa5d0` (eval); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.0511, 0.0655, 0.0677, 0.0686, 0.0751.
- Band (worst to best): 0.0511 to 0.0751.
- Width (spread): 0.0240.

## Noise floor (this row's calculation)

- Metric: recovery.
- sigma_abs = 0.005237 (static offline resolution: N=10000 scored cells/target (rate*n_test) + per-target class/dispersion structure; NO prediction resample).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01481.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0240/0.01481 = **2.62**. endpoints ~2 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 2.62.
- floored: job's single carrier is education; co-amputating it collapses recovery to naive

## Links

- Task: https://horizon.bespokelabs.ai/tasks/6beaf077-62ad-4565-ba11-754036ce1484
- Eval (eval): https://horizon.bespokelabs.ai/evaluations/7f7f6ea9-2ba4-4895-9e75-8349b18aa5d0
- Analysis (strategy, human-authored, updated independently): `../analysis/bank-impute-cat-coamp-single-job/STRATEGY.md`
- Source JSON: `../analysis/bank-impute-cat-coamp-single-job/band_supports.json`
