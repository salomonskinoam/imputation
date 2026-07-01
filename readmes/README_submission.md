# Imputation tasks: validity assessment and submission set

Every imputation task we built and whether its student score reflects **real imputation-skill
separation**. One row per task, with the task / run / analysis links. The full per-task writeup (task
design, internal-run comparison, solution diversity, coordinates) is one file under
[`readmes/tasks/`](tasks/), linked from each row's `analysis`.

**1 submitted (submit = YES) · 0 pending · 1 parked**, of 2 tasks built.

## Master table

`band` = recorded worst→best run (raw recovery score). `submit`: **YES** = valid skill-separating task;
**NO/parked** = rejected or shelved. Metric `recovery` = mean over amputed columns of
`1 − RMSE(method)/RMSE(naive mean-fill)`, clamped [0,1] (0 = mean-fill, 1 = perfect).

| task | handshake | metric | band | mean | std | ref | verdict | submit | links |
|---|---|---|---|---|---|---|---|---|---|
| covertype-impute-direct | code-only, test hidden (deferred) | recovery | 0.27–0.39 | 0.326 | 0.046 | 0.26 (HGB-MICE) | WORKS — separates on imputation method; agents beat the reference | **YES** | [task](https://horizon.bespokelabs.ai/tasks/ff227290-a39d-4cf8-a162-4d79b580743f) · [run](https://horizon.bespokelabs.ai/evaluations/c56b6c86-36e5-45da-9f9b-8d40ae038f2b) · [analysis](tasks/covertype-impute-direct.md) |
| covertype-impute (downstream) | code-only, test hidden (deferred) | macro-F1 | 0.48–0.50 | 0.489 | 0.008 | 0.39 (HGB-MICE) | PARKED — downstream too easy; standardized linear model routes around the missingness (README_general_direction §12 / B0) | NO | [task](https://horizon.bespokelabs.ai/tasks/c20fa806-8b3a-4c34-bfb9-f3f97c7cd3d4) · [run](https://horizon.bespokelabs.ai/evaluations/75c6fd79-e30a-4a52-b442-64ca9ced3642) |

## Methodology (brief)

- **Metric:** direct cell-recovery on the held-out TEST amputed cells vs truth (see the per-task file
  and README_general_direction §13). `best_observed = 1` → raw scores; read absolute recovery vs the
  reference imputer, not just the spread.
- **Model:** every eval uses **biggie-max-polara**, agent-type **meteor**, hosted (see `CLAUDE.md`).
  Each rollout is a different solution the model writes, so the multi-run spread IS biggie's skill band
  on the task (README_general_direction §3). A weak→strong model sweep would widen it, but we only run
  biggie, so biggie's band is the band. (Distinct from re-run σ, re-scoring one fixed solution.)
- **Handshake:** code-only, test hidden (deferred `train_at_grade`) — the agent never sees the test;
  the grader re-runs the submitted `solution.py` on the full held-out test at grade. Downloaded runs
  live in [`analysis/<eval_id>/`](../analysis/) as `runN_<score>.{py,json}` + `_transcript.md`.
- Batch for all tasks: `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`.

## Per-task analysis

- [`readmes/tasks/covertype-impute-direct.md`](tasks/covertype-impute-direct.md) — the working
  direct-recovery flagship (task design, 5-run comparison, solution diversity).
- The downstream `covertype-impute` is parked (analysis in README_general_direction §12).
