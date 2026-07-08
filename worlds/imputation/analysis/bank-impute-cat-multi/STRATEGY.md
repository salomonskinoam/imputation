# bank-impute-cat-multi: strategy analysis

**Band: 0.142–0.227, spread 0.085, 3 realized tiers (floor defect / cluster / lone top). Low mean (~0.19). Viable but the spread is mostly a floor defect plus a lucky outlier, not a clean skill gradient.**

Recover FOUR integer-coded categorical columns in Bank Marketing under MAR (per-column, no
co-amputation): `job` (col 1, 12 classes, medium ~0.29), `marital` (col 2, 3 classes, low ~0.18),
`education` (col 3, 4 classes, medium ~0.33), `month` (col 10, 12 classes, easy ~0.63). Scored by
accuracy vs the majority-class baseline (skill = 1 - err/err_naive), averaged over the 4 columns.
Only originally-missing cells are scored. The easy `month` column dominates the average; the other
three sit near their majority baselines, which is why the mean lands at ~0.19.

## Per-run table

| Rank | Run | Score | Estimator | Chain / pool / label | Encoding | Distinguishing choice |
|---|---|---|---|---|---|---|
| 5 | run2 | 0.1419 | HGBT, iterative chained, 3 iters | chains imputed targets; pools test only for PREDICT, **fits on train rows only**; no label | raw codes, **no `categorical_features`** (12-class cols treated as ordinal) | Two compounding defects: high-card cats as ordinal numeric AND it drops test-observed rows from the fit. The one clearly-worse solution. |
| 4 | run5 | 0.1899 | HGBT, iterative chained, 4 iters | chains; pools train+test (fits on all observed incl. test); no label | mode-init, **`categorical_features` declared** | Textbook "do everything right" recipe (pool + chain + declared cats). Lands mid-pack. |
| 3 | run1 | 0.1903 | HGBT, iterative chained, 3 iters | chains; pools train+test; no label; early_stopping | native-NaN init, **`categorical_features` declared** | Essentially run5 with NaN-init instead of mode-init; +0.0004 (noise-level tie). |
| 2 | run4 | 0.1975 | HGBT, **single pass, no iteration** | pools train+test; no chaining beyond first pass; no label | native NaN, **no `categorical_features`** | Does LESS than run1/run5 (no chain, no declared cats) yet edges them out. Strong evidence the "levers" don't drive a gradient here. |
| 1 | run3 | 0.2269 | **RandomForest** per column (500/1000 trees) + HGB blend on `month` | trains on train rows only (no pool); **uses the label as a feature** (predicted for test) | **-999 sentinel**, per-column CV-tuned models | Only genuinely different strategy: RF + per-column tuning + label feature + a 0.7/0.3 RF/HGB ensemble on `month`. The lone top tier. |

## What separates top from bottom

The five runs sort into three tiers, but only the bottom edge has a legible code driver:

1. **The floor (run2) is a real defect.** It is the only run that both (a) treats the two 12-class
   columns (`job`, `month`) as ordinal numerics (no `categorical_features`) and (b) restricts the
   classifier fit to train-portion rows, throwing away every test row whose target happens to be
   observed. Since `month` carries most of the score, mis-encoding it as ordinal is the plausible
   reason run2 alone drops ~0.05 below the pack.
2. **The middle cluster (run5/run1/run4 = 0.1899/0.1903/0.1975) is a shared ceiling, not a ladder.**
   These three make materially different choices, chain + declared-cats (run5), chain + native-NaN
   (run1), and single-pass + no-declared-cats (run4), yet land within 0.008 of each other. The run
   that does the LEAST (run4, no iteration, no categorical declaration) is the one that ranks highest
   of the three. That inversion of the adult-task "levers" is the signature of noise around a common
   floor, not skill.
3. **The top (run3) is a different strategy whose edge is not attributable.** run3 wins by ~0.027 with
   an RF/ensemble/per-column/label recipe. But the label feature it leans on is exactly what DRAGGED
   solutions down in the sibling `adult-impute-cat-multi` task, and run3 forgoes pooling (a documented
   plus), so its win contradicts the family's own gradient. That makes the +0.027 look like which
   solution got drawn rather than a reproducible skill.

## Verdict

The 0.085 spread is real in the arithmetic but thin in meaning: it is one legible floor defect plus a
lone lucky top, wrapped around a three-run noise cluster, not a clean skill gradient. The strongest
evidence is the middle tier itself, three genuinely different recipes (chain vs single-pass, declared
vs ordinal categoricals) collapse into a 0.008 band, and the run doing the least work (run4) ranks
above the two "correct" ones, which is what a shared near-floor ceiling looks like rather than a skill
ladder. Only run2's ordinal-encoding-plus-train-only-fit is a defect the code makes legible; run3's win
rides a label feature that the same task family showed to be harmful, so it reads as luck of the draw.
Classification: mostly LUCK OF CHOICE near the floor, with a single skill-legible defect at the bottom,
and no evidence of a graduated skill signal in the middle or top.

This file is HUMAN-owned and updated independently; editing it never re-touches the generated table or record (see sdk/methodology/noise_floor.md §15b, the analysis seam).
