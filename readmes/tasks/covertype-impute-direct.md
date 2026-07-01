# covertype-impute-direct — analysis

Direct imputation-recovery task (Direction A). The student writes code that fills the missing cells;
the grader scores the recovered TEST cells against the true values. This is the working flagship of
the imputation world.

## Coordinates

- **task_id:** `ff227290-a39d-4cf8-a162-4d79b580743f` (version 2)
- **eval_id:** `c56b6c86-36e5-45da-9f9b-8d40ae038f2b` (biggie-max-polara, agent-type meteor, 5 runs)
- **batch:** `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`
- **task page:** https://horizon.bespokelabs.ai/tasks/ff227290-a39d-4cf8-a162-4d79b580743f
- **run page:** https://horizon.bespokelabs.ai/evaluations/c56b6c86-36e5-45da-9f9b-8d40ae038f2b
- **downloaded runs:** [`analysis/c56b6c86-36e5-45da-9f9b-8d40ae038f2b/`](../../analysis/c56b6c86-36e5-45da-9f9b-8d40ae038f2b/)
  (`runN_<score>.py` + `.json` + `_transcript.md`)

## Task design

- **Dataset:** Covertype (UCI id=31), 54 cartographic features, subsampled train 5,000 / test 30,000.
- **Amputation:** MAR (P(missing) ∝ observed `Slope` rank), rate 0.5, on the 3 top-MI numeric columns
  `Elevation`, `Horizontal_Distance_To_Roadways`, `Horizontal_Distance_To_Fire_Points` (NaN deletion).
- **Handshake:** code-only, test hidden. Deferred (`train_at_grade`): during the rollout the agent sees
  only training data; `test_features.npy` is a 0-row placeholder; test labels never exist agent-side.
  At grade the grader reveals the full corrupted test and re-runs the submitted `solution.py`.
- **Scoring (direct):** on the amputed TEST cells, `score = mean over amputed columns of
  clamp(1 − RMSE(method)/RMSE(naive mean-fill), 0, 1)`. 0 = no better than a column-mean fill,
  1 = perfect recovery. `best_observed = 1` (raw scores). Reference HGB-MICE oracle ≈ 0.26.

## Result

5/5 graded, 0 errored. Recovery **0.271 – 0.385, mean 0.326, std 0.046** — real agents beat the
HGB-MICE reference (0.26), with clear headroom to 1.0.

## Internal-run comparison

| run | recovery | regressor(s) | passes | pools test features | uses labels | distinctive |
|---|---|---|---|---|---|---|
| 2 | 0.385 | 2×HGB (diff leaves/L2) + RandomForest, averaged | single | yes | no | diverse ensemble, one shot |
| 1 | 0.377 | ExtraTrees + RF + HGB, weighted 0.5/0.25/0.25 | single sweep | yes | no | 3-family weighted ensemble |
| 4 | 0.301 | single HGB reg + HGB classifier | MICE ×6 | yes | yes (one-hot train + predicted test class-probs) | injects label signal, iterates |
| 3 | 0.299 | single HGB | MICE ×5 | yes | no | iterative refit, no ensemble |
| 5 | 0.271 | HGB ×5 seeds, averaged | single | **no** (inductive: fit on train only) | yes (label as NaN-aware column) | only non-pooling run |

## Resolution (how many separable levels)

Per SDK `noise_floor.md` (`tiers = 1 + width/LSD`, `LSD = z·√2·σ`). Noise source = the SDK's binding
one: **test-set resampling** (seeds are pinned → re-run noise ≈0). In §14 terms our score is a
**"sample" channel, scope "shared"** (method + naive baseline scored on the same resampled cells), so
σ sharpens as 1/√N. Only the statistic differs from F1, so we derive its own `v`.

**Closed-form bound (from the number of amputed values).** The "values" are the amputed cells per
column `m = rate·N_test ≈ 15,000`. With per-cell squared error `a_i` (mean = MSE) and κ_e = kurtosis of
the per-cell error (measured ≈ 3–5, avg ~4), CLT + delta method (naive denominator held fixed →
conservative) give, per column:

    σ(skill_c) ≤ (1 − skill_c)/2 · sqrt((κ_e − 1)/m)      [ = SDK sqrt(v/N): N=m, v=(1−skill)²(κ_e−1)/4 ]

so **σ ∝ 1/√(rate·N_test)**. Plug width=0.115, m=15k, z=2, skill≈0.33: κ_e=4 → σ≈0.0047 → **≈10 tiers
(floor)**; κ_e=3 → σ≈0.0039 → ≈12.

**Empirical check (bootstrap test rows, 500×, metric-exact):** σ = **0.0038** → LSD(z=2)=0.011 →
**≈12 tiers** across the realized band (≈37 across [0,best]). Sits at/above the closed-form floor; the
gap is the denominator-pairing variance the bound conservatively drops.

**Realized: the 5 runs resolve into 4 distinct tiers** (adjacent flip-rates 0.00 except run3≈run4 =
0.37): {run5 0.269} < {run3 0.299 ≈ run4 0.300} < {run1 0.377} < {run2 0.385}.

**Bottom line:** ~10–12 separable levels, set by √(rate·N_test); biggie already spans 4. Lever: test
cells grow with K² to resolve K levels (`m ≳ ((K−1)·z·(1−skill)/W)²·(κ_e−1)/2`). Code:
`scratchpad/tiers_direct.py`.

## Solution diversity / what separated skill

- **Ensemble diversity won.** The top two averaged different tree families (HGB + RF + ExtraTrees);
  the single-HGB runs scored ~0.08 lower.
- **MICE iteration did not help** vs a strong single-pass ensemble (runs 3, 4 lost to 1, 2).
- **Using the labels did not help** — both label-users (4, 5) landed at the bottom; imputing features
  from features was enough, and the label block added noise/overfitting.
- **Transductive pooling of train+test *features* helped** — the one inductive run (5) scored lowest.
  (Not a leak: features only, no labels; the agent never saw the test — pooling happens only when the
  grader runs the code at grade time.)

So the ~0.11 run-to-run spread is driven by genuine imputation-method quality, not numeric fiddling.

## Verdict

**WORKS / submit = YES.** The task discriminates on real imputation craft and real agents beat the
reference imputer. The 0.27–0.39 spread across the 5 runs IS biggie's skill band on the task (each run
is a different solution, not a seed re-run). A weak→strong model sweep would widen it; we only run
biggie, so this is the band. (Re-run σ — re-scoring one fixed solution — is a separate resolution
ruler, not measured here.)
