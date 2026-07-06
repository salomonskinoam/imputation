# Imputation world — general direction

Summary of the design conversation, decisions, definitions, and the **measured** dataset
comparison, to bootstrap the imputation world repo. Companion to
[imputation_proposal.md](imputation_proposal.md) (the directional why/constraints) and to the
deeper running doc that lives in the reference repo (`../multimodal_fusion/imputation_world.md`).

## 1. What the world is (one paragraph)

A world of tasks where the student builds a model/code that predicts well on unseen data when the
data it learns from (and predicts on) has missing or corrupted values. Recovering/handling those
values is the *means*, not the graded end. We take **real** datasets and engineer difficulty by
**how we remove/corrupt cells** (which cells, which mechanism, what rate). The scaffolding (SDK
`HorTask` subclass, `train_at_grade` deferred mode, single shared Dockerfile, vendoring tools) is
cloned from the **multimodal_fusion** repo (`../multimodal_fusion/`), which is the reference world.

## 2. Definitions (terms used throughout)

- **Amputation** — deliberately deleting known cells to create missingness, so the deleted truth
  can be used to grade. **Imputation** — filling them back in. Two halves of one world.
- **MCAR** — a cell is missing by pure chance, independent of all values (easiest).
- **MAR** — missingness depends only on *observed* values (rewards cross-column modeling).
- **MNAR** — missingness depends on the *missing value itself* or unobserved factors (hardest;
  naive fills become systematically biased).
- **Instrumental** — the task is graded on a downstream objective that *fails* with bad handling
  and *succeeds* with good handling; never on cell-recovery in a vacuum. Beating the trivial
  baseline (naive fill) is the zero point.
- **Direct (cell-recovery) scoring** — grade the imputed cells against known truth (NRMSE for
  numeric, accuracy/macro-F1 for categorical). Requires *complete* cells we amputate ourselves.
- **Downstream scoring** — grade a prediction task that depends on the recovered features.
- **Agent-time vs grader-time** — student iterates during the rollout (default) vs trains at grade
  time (`train_at_grade`). Same graded artifact across both, as in fusion.

## 3. The band (corrected — and why it is NOT in the table)

**Band = the spread of scores that real student solutions get.** A task is good when weak and
strong solutions land far apart; it is bad when they bunch together — *whether they all score well
or all score badly*. The band collapses at **both** ends.

Earlier we (wrongly) tried to estimate band from the gap between two methods (mean-fill vs MICE) on
a downstream model. That is not the band, for three reasons:

1. **Two points are not a distribution.** The band is dispersion over the whole population of
   plausible solutions (lazy → expert), which we cannot enumerate or fake.
2. **Band is an inverted-U in difficulty, not monotonic.** Too easy → every method recovers → all
   near the ceiling. Too hard → no method beats baseline → all near the floor. Wide band lives in
   the middle.
3. **Correlation is non-monotonic for band.** Too little structure → smart imputers can't
   reconstruct. Too much → even *trivial* methods (or the downstream model itself) recover the
   signal → convergence. You want *medium* reconstructability.

There is also a **downstream-model confound**: a powerful model (gradient boosting) imputes
implicitly and shrugs off imputation quality, compressing all methods together.

**Conclusion: the band is unknowable until the world is built and real solutions are scored.** So
there is deliberately **no band column** below. Measuring the band is the first thing to do *after*
building, not before.

## 4. Decisions made so far

- **Missingness lives in both train and unseen/test** — the deployed pipeline must impute at
  inference; keeps the artifact identical across agent-time and grader-time.
- **Grade BOTH a downstream task AND imputation quality directly.** Not merely "open" — both are
  graded. Direct cell-recovery is the reliable separator (a robust downstream metric is insensitive,
  see §8); the downstream task supplies the instrumental framing. A deliberately **weak / fixed
  downstream model** is a third option that makes downstream sensitive again (see §10).
- **Real data only**, never synthetic; difficulty engineered via amputation. **CPU-only.**
- **Reuse the fusion repo scaffolding**; new domain code + new vendoring.
- **Deliverable is ALWAYS CODE, never data (decided).** The student submits a script/function that,
  given the (corrupted) test features, does what the prompt+grader define; the grader RUNS it to
  produce the graded `.npy` and scores that. **The student is never shown the test set** (no test
  features, no test labels) — the code is applied to a held-out corrupted test at grade time
  (deferred/`train_at_grade` path). This kills v1's test-feature visibility and the train+test
  pooling exploit (§12). v1 showed corrupted test features; this is the fix.

## 5. How each dataset cell was measured (one shared protocol)

Every row was produced by one shared analyzer (`scratchpad/analyze.py`) so the columns are
comparable. It fetches the real dataset, then computes each column by the fixed rule in §6. Each
value carries a provenance tag: **MEASURED** (computed now), **CITED** (from a source), or
**INFERRED** (could not fetch — explicit estimate). 13 rows are MEASURED; NHANES is INFERRED
(no clean canonical table exists on the open mirrors; it must be assembled from CDC components).

## 6. Column definitions (single-word titles; fixed before the table)

| Title | Meaning | Rule |
|---|---|---|
| **Dataset** | Identity | Name. |
| **Rows** | Full usable sample size | Rows after dropping missing-target rows. |
| **Features** | Predictor count (cat/num) | # feature columns, split categorical/numeric. |
| **Types** | Feature-type mix | Categorical if object/category/bool or ≤10 distinct values; `Mixed` if 10–90% of cols categorical, else `Numeric`/`Categorical`. |
| **Task** | Native objective | Classification / Regression / Ordinal. |
| **Correlation** | Inter-feature dependence | Median over features of each feature's max \|Spearman\| with any other (cats ordinal-encoded, median-imputed). High ≥0.6, Med 0.3–0.6, Low <0.3. |
| **Native** | Pre-existing missingness | Missing-cell fraction *after* converting disguised sentinels (`?`, `-200`, blanks, `-7/-8/-9`) to NaN. None <2%, Some 2–30%, Heavy >30%. |
| **Recovery** | Direct-scoring feasibility (derived) | From Native: `Yes` <2%, `Partial` 2–30%, `Hard` >30%. |
| **Signal** | Feature→target predictiveness | HistGradientBoosting, 30% holdout: macro-F1 (classif) or R² (regr). Strong/Moderate/Weak. Model-dependent ceiling, NOT a band. |
| **Verdict** | Flagship fit per the recipe | Terse judgment from signal × signal-concentration × top-feature reconstructability × scoring fit (reasoning + measured numbers in §10). |

## 7. The measured comparison

The three lowest-signal datasets were **dropped** — see §10 for why (no ceiling = no room for an
imputation gap): **Wine Quality** (F1 0.39), **Diabetes-130** (F1 0.39), **Beijing PM2.5** (R² 0.38).
All Signal/Verdict values are MEASURED except NHANES (INFERRED, marked `*`).

| Dataset | Rows | Feats (cat/num) | Types | Task | Corr | Native | Recovery | Signal | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| FICO HELOC | 10,000 | 22 (0/22) | Numeric | Classif | High | Some | Partial | Moderate | **Top pick** — concentrated, medium reconstruct (R²0.89), authentic MNAR codes (−7/−8/−9) |
| Covertype | 581,012 | 54 (44/10) | Mixed | Classif | Low | None | Yes | Moderate | **Top pick** — `Elevation` concentrated (32%), medium reconstruct (R²0.83) |
| Adult | 48,842 | 14 (5/9) | Mixed | Classif | Low | None | Yes | Moderate | Good (categorical) — `relationship` medium-reconstruct (+0.21); covers categorical imputation |
| California | 20,640 | 9 (1/8) | Mixed | Regr | High | None | Yes | Strong | Care — geo feats mutually redundant (R²0.98); real lever is `MedInc`, not lat/long |
| Telco Churn | 7,043 | 19 (16/3) | Mixed | Classif | Med | None | Yes | Strong | Marginal — weak concentration (14%) & weak reconstruct (+0.11) |
| Default-Credit | 30,000 | 23 (7/16) | Mixed | Classif | High | None | Yes | Moderate | Trap — top feat `PAY_0` unreconstructable (−0.26); amputation unrecoverable by anyone |
| Online Shoppers | 12,330 | 17 (5/12) | Mixed | Classif | Med | None | Yes | Strong | Trap — `PageValues` dominates (45%) but unreconstructable (R²0.08) |
| Air Quality (De Vito) | 9,357 | 12 (0/12) | Numeric | Regr | High | Some | Partial | Strong | Direct-only — downstream trivial (sensor proxy); top feat fully reconstructable (R²0.98) |
| Bank Marketing | 45,211 | 16 (7/9) | Mixed | Classif | Low | Some | Partial | Strong | Avoid — top signal is leakage (`duration`) & unreconstructable (R²−0.04) |
| Superconductivity | 21,263 | 81 (2/79) | Numeric | Regr | High | None | Yes | Strong | Avoid — signal spread (top1 1.6%) & fully redundant (R²0.999); GBM routes around |
| NHANES | ~14k | mixed | Mixed | Classif | Med* | Heavy | Hard/Part | Mod* | TBD (inferred) — assemble from CDC components first; realistic heavy MNAR |

Corr buckets: High ≥0.6 / Med 0.3–0.6 / Low <0.3. Native: None <2% / Some 2–30% / Heavy >30%.
Subsampled to 8,000 rows for the compute (full size under Rows). Rows ordered by Verdict (best first).

Per-row caveats:
- **Air Quality**: downstream R² 0.99 because benzene (target) is near-deterministic from a co-located
  tin-oxide sensor — downstream trivial; only useful for *direct* recovery scoring.
- **Covertype**: 44 of 54 features are binary one-hot indicators (counted categorical); `Elevation`
  is the numeric lever.
- **Natively-missing (Bank, Air Quality, FICO, NHANES)**: direct scoring needs a carved-out complete
  subset (no truth where natively missing).

## 8. Considerations and findings

- **Type-mix coverage**: Mixed (Adult, Default-Credit, Bank, Online Shoppers, Telco, Diabetes,
  Covertype), pure Numeric (Wine, Superconductivity, Air Quality, FICO), no pure-categorical
  survivor (Soybean was cut for size). To exercise categorical imputation + macro-F1 scoring, lean
  on the Mixed set.
- **Complete vs natively-missing**: complete datasets (Recovery=Yes) support *both* scoring modes
  by amputating with known truth. Natively-missing ones (Partial/Hard) are downstream-only unless
  we carve out their complete rows.
- **Downstream-metric sensitivity probe (NOT the band)**: as a sanity check the analyzer also ran a
  single two-method comparison — mean-fill vs MICE under 40% MNAR on the top features, scored by a
  gradient-boosting downstream model. The gap was **flat across all 13 datasets** (≈0, sometimes
  negative). This does **not** measure the band, but it is strong evidence that a *robust
  gradient-boosting downstream metric is largely insensitive to imputation quality*. Design
  implication: to get any score separation we will likely need **direct cell-recovery scoring**
  and/or a deliberately imputation-*fragile* / fixed downstream model — not a strong GBM. This is a
  property of the scoring design to settle when we build, and the reason both scoring modes stay on
  the table.
- **High correlation is not automatically good** (see §3): Superconductivity (0.91) and California
  (0.88) are highly correlated, which can mean even simple methods recover — to be checked at build.

## 9. Open questions / next steps

- Pick the flagship dataset(s) and the corruption mechanism(s) jointly (mechanism + rate + which
  columns), then **build** and only then measure the real band.
- Decide the scoring design per instance: direct recovery vs downstream-with-a-fragile-model (or
  both), given the §8 insensitivity finding.
- Settle categorical coverage (possibly re-add a pure-categorical dataset despite small N).
- Stand up the world package by cloning the fusion scaffolding.

## 10. Signal strategy & how to select a dataset

### Why we want STRONG signal (and dropped the weak ones)

Think of three score levels on a downstream-graded task:

- **Ceiling** — score with clean, un-amputated data. *This is exactly what the Signal column
  measures.*
- **Good-handling** — score after amputation + a skilled imputer.
- **Floor** — score after amputation + naive fill (≈ the trivial baseline).

The thing we eventually grade lives in the **gap between good-handling and floor**. That gap can
only exist if there is height to fall from — a high ceiling. **Weak-signal datasets have no
ceiling**, so corruption cannot open a gap; the target was never recoverable. That is why Wine
(0.39), Diabetes-130 (0.39) and Beijing (0.38) were dropped.

### "Impute until the signal is lost" — corrected

The instinct (start from strong signal, then corrupt until signal degrades) is right, **but the
signal must be lost for the *naive* solution, not for everyone**. Corrupt too far and even a good
imputer can't recover → all solutions collapse to the floor together → no separation (the
both-ends-collapse from §3). The target operating point:

> naive fill → signal **gone** (floor) │ skilled imputer → signal **largely recovered** (near ceiling)

### The downstream confound and the three ways to open a gap

A robust gradient-boosting downstream model imputes implicitly and shrugs off imputation quality —
measured flat across all datasets (§8). So "corrupt until signal lost" on a strong GBM loses it for
*both* naive and good at once. To make the gap real, use **one of**:

1. **Direct cell-recovery scoring** — grade imputed cells vs truth (NRMSE / macro-F1). Good vs naive
   separate by construction; no model to route around.
2. **A weak / fixed downstream model** — e.g. logistic/linear regression, or a frozen pre-trained
   model. It *cannot self-heal*, so imputation quality propagates straight into the score. (This is
   the option that revives downstream grading; cheap to add and worth testing per instance.)
3. **Concentrate the corruption on one irreplaceable-but-reconstructable feature** — important
   enough that amputating it moves the score, reconstructable enough that a good imputer recovers it,
   so even a GBM can't fully route around it.

**Decision: we grade BOTH a downstream task AND direct imputation quality** (and will trial the weak
fixed downstream model), so a task isn't hostage to a single insensitive metric.

### The two measured levers for picking the corruption target

Per dataset we measured, for the single highest-mutual-information feature:

- **Top1 / Top3** — that feature's (and the top-3's) share of total feature→target mutual
  information. High Top1 ⇒ signal **concentrated** ⇒ amputating it actually moves the downstream.
- **Reconstruct** — how well that feature can be rebuilt from all the OTHER features (GBM holdout
  R² for numeric; balanced-accuracy lift over base for categorical). This is the key axis:
  - **Medium (≈0.5–0.9 R², or clear positive cat-lift)** = the sweet spot: skilled imputers recover,
    lazy fills don't, room for skill to separate.
  - **Too high (>0.95)** = even trivial linear imputers recover ⇒ method choice barely matters, and a
    strong downstream routes around it.
  - **Too low / negative** = *no* method can recover ⇒ amputation is unrecoverable by anyone ⇒
    uniform collapse. "Irreplaceable feature" trap.

Measured (top feature per dataset):

| Dataset | Top feature | Top1 | Top3 | Reconstruct | Read |
|---|---|---|---|---|---|
| FICO HELOC | ExternalRiskEstimate | 0.19 | 0.38 | R² 0.89 | concentrated + medium-high → **good** |
| Covertype | Elevation | 0.32 | 0.48 | R² 0.83 | concentrated + medium → **good** |
| Adult | relationship (cat) | 0.22 | 0.54 | +0.21 lift | medium cat → **good (categorical)** |
| California | longitude | 0.27 | 0.76 | R² 0.98 | geo redundancy; use MedInc → **care** |
| Telco Churn | Contract (cat) | 0.14 | 0.33 | +0.11 lift | weak/weak → **marginal** |
| Default-Credit | PAY_0 | 0.20 | 0.42 | −0.26 lift | unreconstructable → **trap** |
| Online Shoppers | PageValues | 0.45 | 0.64 | R² 0.08 | unreconstructable → **trap** |
| Air Quality | PT08.S2(NMHC) | 0.48 | 0.65 | R² 0.98 | fully reconstructable → **direct-only** |
| Bank Marketing | duration | 0.36 | 0.63 | R² −0.04 | leakage + unreconstructable → **avoid** |
| Superconductivity | range_fie | 0.02 | 0.05 | R² 0.999 | spread + redundant → **avoid** |

Caveat: only the single top-MI feature was probed. The real design step is to pick a feature (or
small set) that is *both* signal-bearing and in the medium-reconstructability band — which may not be
the literal top-MI feature. So this is a grounded shortlist + the deciding metric, not a final lock.

### The selection recipe (operational)

1. **Strong-enough ceiling** (Signal ≥ Moderate) — else nothing to fall from.
2. **Concentrated, signal-bearing target feature** (decent Top1) — so amputation moves the score.
3. **Medium reconstructability of that feature** (~0.5–0.9) — the regime where imputation skill
   separates; avoid both "irreplaceable" (≈0) and "trivially recoverable" (>0.95).
4. **Complete cells available** (Recovery = Yes) for direct scoring, OR accept downstream-only.
5. **A scoring mode that can't self-heal** — direct recovery and/or a weak fixed downstream model.
6. Build, then (and only then) measure the real **band**.

## 11. Amputation & corruption types (reminder)

Missingness is described by **three independent knobs** — mechanism, functional shape, and structural
pattern — plus rate; and beyond deletion there is the **corruption** family (value present but wrong).

**Mechanism (Rubin 1976) — *why* a cell goes missing:**
- **MCAR** — missing by pure chance, independent of all values (easiest; methods converge).
- **MAR** — missingness depends only on *observed* values (rewards cross-column modeling).
- **MNAR** — depends on the *missing value itself* or unobserved factors (hardest; naive fills become
  systematically biased — the widest-skill regime).

**Functional shape — *which* values go missing** (sub-types of MAR/MNAR, as in R `mice::ampute`):
- **RIGHT** (drop high values), **LEFT** (drop low), **MID** (drop middle), **TAIL** (drop both
  extremes). This is the knob that makes a mean-fill biased in a specific, exploitable direction.

**Structural pattern — *where* the holes sit:**
- **Univariate** (one column), **Monotone** (staircase — once missing, all later columns missing;
  typical of dropout/longitudinal), **Arbitrary / non-monotone** (any cell), **Blockwise** (whole
  groups of columns missing together — e.g. a sensor/modality drops; overlaps the fusion world).

**Rate** — second independent knob (e.g. 10 / 30 / 50% of targeted cells).

**Corruption (value present but WRONG — beyond classic missingness; the proposal says "missing OR
corrupted"):**
- **Disguised missing** — sentinels that look like data (`0`, `-200`, `-999`, `"unknown"`); the
  student must first *discover* it. (Seen natively in Air Quality `-200`, FICO `-7/-8/-9`.)
- **Noise injection** — additive/multiplicative noise on cells.
- **Outliers / cell errors** — implausible replacements.
- **Category / label corruption** — wrong category or swapped values.
- **Rounding / unit / discretization errors.**

For this world the default lever is **MNAR + a directional shape (RIGHT/LEFT) on a chosen feature, at
a tuned rate**, with disguised-missing as the natural "make them discover it" variant.

## 12. v1 eval findings → creating spread (adversarial amputation & handshake)

**v1 (covertype-impute, MAR-0.5) is TOO EASY — no spread.** 5 hosted runs (biggie-max-polara) all
scored macro-F1 ≈ 0.48–0.50 (std 0.008): well above our HGB-MICE oracle (0.386) and floor (0.247), but
bunched → the task doesn't separate skill. Inspected submissions (`scratchpad/agent_solutions/`):
every run = **pool train+test → MICE/KNN impute the 3 NaN cols → feature-engineer for the linear model
(cos(Aspect), log1p(distances), StandardScaler)**.

### Why "no spread" — corrected (feature-engineering was NOT the dominant lever)

Earlier claim ("feature engineering, not imputation, was dominant") is **retracted**. Decomposition of
the raw macro-F1 (frozen raw logistic):

| solution | macro-F1 | added |
|---|---|---|
| mean-fill + raw features | 0.247 | — |
| HGB-MICE + raw features (our oracle) | 0.386 | **imputation +0.14** |
| MICE/KNN + standardize/log1p/cos (agents) | ~0.49 | **feature-eng +0.10 on top** |

So **both levers contribute, and imputation ≥ feature-eng** — not "dominant." Mechanism for the
feature-eng lever (measured earlier): standardizing the raw logistic lifted clean-data macro-F1 ~0.42→
0.50, because L2 on wildly-scaled raw features (Elevation ~10³, Hillshade ~10², binaries 0/1)
under-weights the big-scale numerics; standardizing fixes the conditioning. The agents simply recovered
the ~+0.08 our RAW frozen model withheld. **Real cause of no-spread:** *every lever here is easy* —
MAR keeps the target range observable (≈0.83 reconstructable) so any imputer recovers, and
standardizing is obvious — so a competent model always finds the good solution and 5 runs of one strong
model converge high. Spread needs the good solution to be **hard to find** (adversarial amputation)
and/or a metric that isolates imputation. Caveat: this decomposition mixes different imputers; a clean
2×2 ablation (mean/HGB × raw/standardized) will nail exact contributions — folded into the panel below.

### Direction A — direct imputation-quality scoring (STANDING; its own task)

Keep this on the table every iteration until scheduled. It becomes its **own task variant with its own
prompt + grader, gated by a config flag** (not a tweak to the downstream task). Deliverable = code that
outputs imputed values; grade NRMSE (numeric) / accuracy (categorical) vs withheld truth. No downstream
model, no feature-eng confound → the score IS imputation quality, so spread is separation-by-recovery.
We WILL build this; it stays listed until we say "build it now."

### Direction B — salvage the current downstream task (NaN-only)

Stay with plain **NaN deletion** (no corruption). Two parts: structural changes + amputation levers.

**Fairness principle (how we know a task is possible, not impossible):** for any amputation, the
question "fair vs impossible" = *is there a solution that, seeing only what the student sees, reaches
near the clean ceiling?* The **panel measures this**: a reachable top ⇒ solvable/fair (and the drop to
naive is the skill band); a floored top ⇒ we over-tuned severity ⇒ dial back. So we tune each lever so
BOTH the top is reachable AND the spread is wide. All the levers below map to real phenomena (correlated
sensor failure, censoring/saturation, deployment shift) — realistic, not contrived.

**Structural changes (decided; independent of amputation):**
- **Code-only deliverable + held-out test the student never sees** (§4): the student's imputer is run by
  the grader on unseen corrupted test. This alone kills the train+test pooling exploit and the
  test-feature-visibility issue.
- **Grader standardizes** before the frozen model: removes the "just standardize" feature-eng lever
  (which added ~+0.08 in v1), leaving imputation as the differentiator. Requires the standardize
  re-check (below).

**Amputation levers (NaN-only), tuned via the panel:**
1. **Co-amputate the reconstructors** (correlated / blockwise): remove the target feature AND its top
   predictors on the SAME rows → no observed columns to reconstruct from. Attacks reconstructability
   head-on. Fair as long as *some* structure remains (don't remove all predictors).
2. **MNAR self-masking** (value-dependent RIGHT/LEFT): drop where the target's OWN value is high/low →
   observed rows don't span the missing range → forces extrapolation, biases the conditional mean.
   Highest floor-collapse risk → moderate rates only.
- Train/test **shift** is now largely **subsumed** by the held-out-test handshake (student can't pool
  anyway); keep as an optional extra, not a core lever.

**DROPPED:** *corrupt-not-delete* (inject wrong values) — unrealistic, "cheaty", hard to engineer, and
non-scalable; and the old "#5 medium-reconstructable/informative-MNAR" — folded into target-feature/rate
tuning and #2. Stay with NaNs.

**Recommendation:** structural changes (code-only + held-out test + grader-standardize) + **#1 (co-amputate
reconstructors)** as the primary recovery-difficulty lever, **#2 (MNAR self-mask)** as the secondary,
rate-tuned to avoid floor-collapse (§3). Confirm empirically via the panel — do NOT lock by intuition.

**Direction B caveat — re-check under standardization.** Since the grader will standardize (or the
student always standardizes anyway), the offline check must be **re-run with standardization ON** to
confirm a *theoretical* imputation gap still survives when everything else is known (clean-oracle vs
naive under a standardizing model). If imputation adds nothing once scaling is neutralized, Direction B
on that dataset is dead and we lean on Direction A.

### B0 panel RESULT (measured) — Direction B fails on Covertype under standardization

Ran the panel (`scratchpad/panel_adversarial.py`): solution panel × {MAR, MNAR 0.5/0.7, co-amputate
0.3/0.5} under both raw and standardized frozen logistic. **Under the STD grader every config is flat**
(spread best−floor = +0.002…+0.012; oracle 0.497 ≈ mean-fill 0.48–0.49), *even co-amputating Elevation
plus all its reconstructors on half the rows*. The standardized linear model **routes around** the
missing cartographic block using the remaining signal (notably Covertype's 44 binary soil/wilderness
indicators). The RAW grader shows a wide spread (0.27→0.38) but that spread is "did you standardize,"
not "did you impute" (the v1 problem). Net: on Covertype, RAW grader rewards standardizing, STD grader
rewards nothing — **downstream scoring is a weak lever for imputation spread** (re-confirms §8 at build
level). Direction B might work only on a leaner, low-redundancy dataset (few features, one irreplaceable
target); Direction A (direct recovery) is the robust path and is prioritized.

### The panel calibration (original plan; superseded for Covertype by the B0 result above)

Offline, mirroring how v1 was calibrated: run a **solution panel** — {drop/mean, median, KNN,
MICE-linear, MICE-HGB, MICE-HGB+standardize, clean-oracle} — under **each NaN-only amputation lever (#1
co-amputate, #2 MNAR self-mask, and combos)**, with the **grader standardizing**, and measure the downstream spread
(plus the direct-recovery spread as reference). Pick the amputation(s) that yield the widest **monotone**
spread **without floor-collapse**. Only then rebuild the task.

## 13. Direction A WORKS — the direct-recovery task (covertype-impute-direct)

We built and shipped Direction A: `covertype-impute-direct` (task_id
`ff227290-a39d-4cf8-a162-4d79b580743f`). Handshake = **code-only, test hidden** (deferred; the agent
sees only training data during the rollout, `test_features` is a 0-row placeholder; the grader re-runs
the submitted `solution.py` on the full held-out test at grade). Score = imputation recovery on the
amputed TEST cells vs truth: mean over amputed columns of `1 − RMSE(method)/RMSE(naive mean-fill)`,
clamped [0,1] (0 = mean-fill, 1 = perfect).

**First eval (biggie-max-polara, 5 runs, eval `c56b6c86`):** 5/5 graded, 0 errored. Recovery
**0.27–0.39, mean 0.326, std 0.046** — real agents BEAT our HGB-MICE reference (0.26), with clear
headroom to 1.0. The task **discriminates on real imputation craft** (a genuine ~0.11 method-driven
spread across runs):

| run | recovery | what it did (differences) |
|---|---|---|
| 2 | 0.385 | 2×HGB (diff leaves/L2) + RandomForest, averaged; single pass |
| 1 | 0.377 | ExtraTrees + RF + HGB weighted ensemble; single sweep |
| 4 | 0.301 | single HGB, MICE 6 iters, + uses labels (one-hot train + predicted test class-probs) |
| 3 | 0.299 | single HGB, MICE 5 iters |
| 5 | 0.271 | HGB×5 seeds, single pass, + label column; ONLY run that does not pool test (inductive fit) |

Lessons from the submissions: **ensemble diversity won** (top two averaged ExtraTrees/RF/HGB);
**MICE iteration didn't help** vs a strong single-pass ensemble; **using the labels didn't help**
(both label-users landed at the bottom); **transductive pooling of train+test *features* helped** (the
one inductive run scored lowest).

**On "train+test pooling" and test visibility (NOT a leak):** the agent never sees the test set — it is
0 rows during the rollout, and test *labels* never exist in `/data_agent`. "Pooling" is what the
submitted CODE does when the grader runs it at grade time: to impute the test's missing cells the code
must read the test *features*, and several submissions concatenate train+test feature matrices to give
the imputation regressor more rows. Features only, no labels, and nothing the agent memorized. A stricter
"inductive only" variant (fit on train, apply to test, no cross-test sharing) is possible but is a
design preference, not a leak fix.

**Conclusion: Direction A is the working flagship.** Direction B (downstream) stays parked (§12 / B0).
Per-eval analysis: `analysis/<eval_id>/`; submission index: `submissions/`.

## 14. Second dataset — california-impute-direct (engine generalizes)

Stamped a second direct-recovery task with only a new npz + config + shim (engine untouched),
proving the "task = npz + config + shim" claim. Raw California housing (OpenML 537, 20640 blocks,
8 features). Amputate `median_income` under MAR (driver `latitude`), rate 0.5, n_train=3000,
n_test=17000 (8480 amputed test cells). Continuous `median_house_value` discretized into 5 quantile
tiers to satisfy the engine's integer-label/stratify contract (direct scoring ignores label values).

- task_id `76263f44-25bb-48a4-82f1-6383a214e8f8`
- Vetting (`scratchpad/vet_california.py`): `median_income` reconstructs at R^2 ~0.68 from features
  alone (0.5-0.9 sweet spot). Rooms/bedrooms/households ~0.95-0.97 (too easy), age 0.27 (floor risk).
  Single target on purpose: population (0.82) is near-trivial via households (corr 0.91) and would
  dilute the band; resolution comes from large n_test instead.
- Local sanity (`scratchpad/sanity_california.py`) + hosted validate agree: HGB-MICE oracle **0.367**,
  mean-fill **0.000**. noop -> 0. Oracle hosted shows cosmetic FAILED (best_observed=1, oracle<1) but
  `tests_passed 1/1`, `all checks passed` — a real grade.
- Biggie band (eval `41ae826f`, 5 runs): **0.36–0.52, mean 0.454, std 0.054, width 0.158** — beat the
  HGB-MICE reference (0.367) on 4/5. Resolution (`scratchpad/tiers_california.py`): σ̄≈0.0075, **all 5
  runs pairwise separable (flip-rate 0.000) → 5/5 distinct levels, ~8 over the band**. Stronger than
  covertype (wider band, cleaner realized separation). Same lessons: train+test **feature** pooling
  won (top two), MICE over-iteration lost (worst). **WORKS → submit YES.** See
  `readmes/tasks/california-impute-direct.md`.

## 15. Making tasks differ ON PURPOSE — the input-knob grid

Covertype and California discriminate on *different* skills (covertype: ensemble diversity across 3
heterogeneous targets; california: transductive pooling on 1 target — see each
`analysis/<eval_id>/ANALYSIS.md`). But that difference was **accidental** (it fell out of 3-vs-1
targets), not designed. Lesson: with biggie's fixed strategy space, a new "complete numeric table,
ampute 1 col" task tends to collapse onto the SAME winning lever (strong tree imputer + pooling). A new
dataset buys different *content* for free but NOT a different *discriminating skill*.

**An axis qualifies only if it is (a) an INPUT we set — a property of the data or of the amputation, not
a description of the recovered output — AND (b) changes the SKILL taught, not merely the difficulty.**
Changing a constant (rate, or how hard the chosen target is to reconstruct) moves difficulty within one
skill; it is a tuning dial, not an axis. This is why "recovery path" and "reconstruct regime" from the
earlier draft are OUT as axes: they described the output/difficulty. What survives are three input levers:

- **Amputed-column type** — we ampute a **numeric** vs a **categorical** column. Input: which column /
  dataset. Skill: regression-imputation (NRMSE) vs classification-imputation (accuracy). [needs the
  additive cat branch in `verify.py` + a dataset that has a categorical, recoverable target]
- **Number of amputed columns** — we ampute **one** column vs **several** heterogeneous columns. Input:
  amputation config. Skill: a single conditional regression vs a multi-column portfolio (this is the
  covertype-vs-california lever, ensemble-diversity vs data-access). [config-only]
- **Co-amputate the reconstructors** — on the affected rows we delete the target **only** (isolated) vs
  the target **AND its top predictor columns** (blockwise). Input: amputation pattern. Skill: exploit the
  strong direct correlates vs recover when the direct predictors are themselves missing (lean on weak /
  indirect signal + priors). [config-only]

**Rejected as axes:** **rate** and **target reconstructability** (difficulty dials, not skills — kept
only as VETTING knobs so the band lands in the 0.5–0.9 sweet spot, §10); **MAR→MNAR** (self-masking
shifts the *bias* but the winning strategy stays "strong conditional imputer"). **Candidate axes, NOT
yet endorsed** (each is a genuine input that *might* change the skill, to test later): **disguised-missing
sentinels** (missing encoded as a plausible value like −200, so the student must first DETECT the
missingness → adds a data-cleaning skill) and **tail-deletion** (delete the target's extreme values →
forces extrapolation beyond the observed range vs interpolation).

**Hard constraint:** every variant is a NEW task (new config + shim + task_id). Never edit the two
shipped tasks; the categorical scorer must be an ADDITIVE, gated branch in `verify.py` that leaves the
numeric path byte-identical.

**The grid = 2^3 = 8 slots** (Type × #Columns × Co-amputate). Each slot is a distinct skill-combo; the
two shipped tasks are one knob-flip apart (both Numeric/Isolated, differ only on #Columns):

| # | Task | Amputed type | # columns | Co-amputate reconstructors | Comments (hypothesized skill / feasibility) |
|---|---|---|---|---|---|
| 1 | ✓ california | Numeric | Single | No | single conditional regression → data-access / pooling lever |
| 2 | — | Numeric | Single | Yes | recover one col when its predictors are also gone → indirect signal + priors; VET (floor-collapse risk) |
| 3 | ✓ covertype | Numeric | Multi | No | multi-column portfolio → ensemble-diversity lever |
| 4 | — | Numeric | Multi | Yes | blockwise deletion of several cols + their predictors → recover from residual structure; VET |
| 5 | — | Categorical | Single | No | classification imputation of one cat col (calibration/mode) → needs cat branch + cat dataset |
| 6 | — | Categorical | Single | Yes | cat recovery without direct predictors; VET |
| 7 | — | Categorical | Multi | No | several cat cols jointly → cat portfolio |
| 8 | — | Categorical | Multi | Yes | cat blockwise recovery; VET |

**Datasets ≠ slots (correction to "one dataset per slot").** Two of the three axes (#columns,
co-amputate) are **config-only**, so ONE dataset fills all four of its Type-slots by changing the
amputation. Only the **Type** axis forces a different (or Mixed) dataset. So the 8 slots need ~2
datasets that *afford* the targets: our numeric ones (covertype/california, already cover slots 1–4 by
config) + one categorical dataset with a recoverable cat target (Adult is the shortlisted afford-er,
covers 5–8). Each slot still needs the dataset to afford it (≥2 heterogeneous targets for Multi; a
co-amputable target with named reconstructors). ⚠ Co-amputate slots need floor-collapse vetting first.

### 15a. Co-amputate slots built (2 & 4, both datasets) — result + a key lesson

Built all four co-amputate tasks (slots 2 & 4 × {California, Covertype}), 5 runs each (20 runs). Two
engine tweaks made the axis clean and safe (verified no change to the base tasks): `co_amputate` now
selects rows MAR-on-driver like the base tasks (so only the reconstructor deletion differs), and
`_direct_score` scores only the configured `target_cols` (co-amputated reconstructors are imputed-but-
unscored, so "single" stays single).

| task | band | width | distinct | vs oracle | verdict |
|---|---|---|---|---|---|
| california-impute-coamp-multi | 0.27–0.39 | 0.124 | 5/5 | oracle 0.08 | WORKS (best) |
| california-impute-coamp-single | 0.15–0.26 | 0.111 | ~3/5 | oracle 0.00 | WORKS |
| covertype-impute-coamp-single | 0.53–0.61 | 0.077 | ~3/5 (bunched) | oracle 0.32 | MARGINAL |
| covertype-impute-coamp-multi | 0.29–0.33 | 0.041 | ~3/5 | oracle 0.15 | MARGINAL/weak |

**Lesson (important): oracle skill does NOT predict the biggie band.** The vet (HGB-MICE oracle) said
California co-amp would floor (0.00/0.08) and Covertype would be the viable one (0.32/0.15). The real
evals inverted it: **California co-amp separates best** (biggie recovers the fragile rooms/household-ratio
combination with run-to-run skill variance → wide spread), while **Covertype co-amp clusters high** (the
44 residual soil/wilderness indicators let strong models converge → narrow band, esp. multi at width
0.04). So use the oracle vet only to avoid *true* floor-collapse (nobody recovers), NOT to predict spread
— only a real eval measures the band. Levels here are closed-form (bootstrap deferred; machine was
saturated). Per-task detail: `analysis/<eval_id>/ANALYSIS.md`; summary in README_submission.md.

## 16. Categorical imputation — the scorer, the results, and the next datasets

### 16a. The categorical scorer (built, generic, gated)
Added a categorical branch to `verify._direct_score`, gated by a new `categorical_cols` config key
(numeric tasks are byte-identical). Score per categorical target = `1 − err/err_naive`, err =
misclassification rate on the amputed cells, err_naive = majority-class error (0 = mode-fill, 1 =
perfect). Categorical targets are integer class-coded FEATURE columns; `prompt_builder` gets a categorical
framing. Verified perfect→1.0, mode-fill→0.0. **No infra beyond this: a new categorical dataset = a
`vendor_*.py` (fetch + integer-code + complete carve-out) + config + shim, like Adult.**

### 16b. Offline resolution (levels are a task PROPERTY, not an observation)
Resolution = the finest trustworthy score gap, computed BEFORE any run. `scratchpad/offline_resolution.py`:
`LSD = 1.96·√2·σ`, `σ = sqrt(err_naive(1−err_naive)/N)/err_naive` at the majority operating point,
N = `rate·n_test` amputed cells, /√k over k targets. **Max levels over [0,1] = 1/LSD** is the task's
resolution; after an eval, **levels-in-band = 1 + band_width/LSD**. Adult: ~82–92 levels available, so its
narrow single band is a real convergence, not a resolution limit.

### 16c. Adult result — single CONVERGES, multi SPREADS (inverts the numeric pattern)
Adult (UCI id=2, native categorical, complete carve-out 45,222 rows; `tools/vendor_adult.py`). Target vet
(`scratchpad/vet_adult.py`) flipped our assumption: **`occupation`** (14 classes, mode 0.13) is the sweet
spot (classifier skill ~0.25); `relationship`/`marital-status` are EASY (~0.65/0.71, mutually predictable
via marital↔relationship↔sex); `workclass` floors; `education` is a trap (twin `education-num`).

| task | band | levels-in-band | verdict |
|---|---|---|---|
| adult-impute-cat-single (occupation) | 0.23–0.25 (w 0.018) | ~2–3 | MARGINAL (converged) |
| adult-impute-cat-multi (occ+rel+marital) | 0.36–0.45 (w 0.084) | ~8 (~4 realized) | **WORKS** |

**Key finding: categorical inverts numeric.** Numeric side: single spreads, multi dilutes (covertype).
Categorical side: **single converges** (occupation has ONE obvious approach — fit a strong classifier →
everyone hits the same MI ceiling ~0.24), **multi spreads** (three columns of different difficulty where,
under MAR-per-column, the OTHER targets are usually still observed and are mutually predictive, so
exploiting the redundancy via pool + chain + label-omission is optional → solutions vary → spread). So the
categorical spreader is the **multi** cell.

### 16d. Categorical target-selection recipe (extends §10, which was numeric)
For a categorical target column: (1) **native** categorical (no discretizing a numeric col); (2)
cardinality > 2 (more classes = more headroom); (3) mode NOT dominant (majority freq well under ~0.6, else
err_naive tiny → no room + noise amplified); (4) **medium** reconstructability (skill ~0.2–0.6) — avoid a
near-deterministic twin (converges high) and avoid unreconstructable (floors); (5) prefer a **multi** cell
with 3+ heterogeneous, partially-redundant columns (the spread generator).

### 16e. Next categorical datasets — DIFFERENT modalities, no infra (decided)
To get another WORKS categorical task from a fundamentally different modality (Opus investigation), build
BOTH — each is just vendor + config + shim:
- **Diabetes 130-US Hospitals** (clinical; UCI id 296, ~101k rows, complete after dropping high-missing
  cols). Structural clone of the working Adult-multi: the admission triad
  (`admission_type`↔`admission_source`↔`discharge_disposition`) is a mutually-predictive cluster,
  `readmitted` (mode ~0.54, weakly predictable) is the hard anchor. Multi cell over those. Risk: mild
  mode-domination (~0.47–0.60). Confidence medium-high.
- **Connect-4** (board-game state; UCI id 26 / OpenML 40668, 67,557 rows, fully complete, 42 cells ∈
  {x,o,blank}). Fundamentally different: redundancy is **physical/logical** (gravity + turn parity), not
  statistical. Hide 3–5 balanced mid-board cells. Risk (real): **convergence** — a strong tree ensemble
  may learn gravity/parity implicitly, collapsing the naive-vs-clever gap → per-cell balance + headroom
  vet first. Confidence medium-low.

Rejected: Soybean (ideal structure, only 683 rows), Nursery (factorial → independent columns → floor),
Mushroom (small, near-deterministic). As always: the vet only guards floor/convergence-shape; **only a
real 5-run eval decides viability.**

### 16f. Categorical co-amputate — the last two knob-slots (measured)

Filled Cat·Single·Yes and Cat·Multi·Yes (co_amputate on the categorical scorer, config-only on Adult/Bank;
5 runs each, biggie-max-polara/meteor). Mechanism fact: co_amputate nulls ALL targets on the SAME rows, so
it removes the co-observed sibling redundancy that made Cat·Multi·No spread.

- **Cat·Single·Yes → floors on LOW-cardinality, WORKS on HIGH-cardinality (salvaged).** First attempts
  floored: adult relationship K=6 (co-amp marital+sex) → 0.05–0.07, 2 levels at the floor; bank education K=4
  (co-amp job) → ~0; bank job K=12 (co-amp education) → ~0.065. Each has ONE strong carrier; co-amputate it
  and you land at naive. **Fix = a HIGH-cardinality target with DISTRIBUTED predictors:** occupation K=14
  (co-amp educ+educ-num) spreads 0.091→0.168, **3 realized levels / capacity 8 → WORKS**
  (adult-impute-cat-coamp-single-occ). So the floor was a target-choice artifact, not a slot property; the
  California distributed-signal intuition DOES transfer, but only to a high-card categorical (a low-card
  single-carrier target has no residual to differentiate on). It is target-specific, not dataset-specific:
  the Bank column floored because job's carrier is a single column (education), not because Bank can't.
- **Cat·Multi·Yes → WORKS, at the right hardening.** Co-amputating BOTH of occupation's predictors
  (educ-num+educ) over-hardened → converged ~0.30 (3 levels). Co-amputating only educ-num, keeping educ as
  an OBSERVED anchor → band 0.29–0.37, 4/7.2 levels (adult-impute-cat-coamp-multi-mild). **Hardening is a
  dial, not a switch**: keep one strong reconstructor observed (floor-anchor for the easy targets), remove
  the other. Building both the aggressive best-shot and the mild hedge was the right call; the hedge won.
  **Caveat (5-solution analysis, `analysis/366d5ba6…/ANALYSIS.md`):** the spread is driven by ESTIMATOR
  choice (HGB@0.29 vs bagged RF/ExtraTrees@0.35–0.37 on the 14-class targets), NOT by MICE chaining
  (uncorrelated with score) or educ-num recovery (deterministic from observed `education`). So the slot is a
  real spreader, but the discriminated skill is "pick the right ensemble for a high-cardinality categorical
  target," a weaker axis than the numeric-coamp fragile-combination skill.
