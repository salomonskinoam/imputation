# Imputation tasks: validity assessment and submission set

Every imputation task we built and whether its student-score band reflects **real imputation-skill
separation**. The verdict is **SPREAD + #band_supports**, never the mean (README_general_direction §3,
and `CLAUDE.md`): #band_supports >= 3 = a resolvable band = submit-viable; <= 2 = reject.

**This doc is SDK-owned and regenerable, not hand-maintained.** The single grid table below and one per-task
record under [`readmes/tasks/`](tasks/) are produced by `tools/band_report_impute.py` (which fills the
`sdk.hor_utils.band_report` schema) from the inlined run scores in `tasks_def/band_manifest.py`. Never edit
the table rows or records by hand:

```
python tools/band_report_impute.py --emit       # regenerate every record + upsert every master-table row
python tools/band_report_impute.py --validate    # check the row<->record invariant (every row links a record, and back)
```

Numbers come from the existing eval runs (no re-runs): band / spread / #observed from the run **scores**;
the noise floor (sigma -> LSD -> #band_supports) from a **static offline resolution** model (a task
property: N = rate*n_test scored cells + per-target class/dispersion structure, no per-cell predictions).
sigma is therefore an estimate, labeled `sigma_source` in each record; it upgrades to a prediction-resample
sigma once a task is re-evaluated with the predictions-persisting grader (`worlds/imputation/verify.py`).

**Read `#obs / #supports` as REALIZED / CAPACITY, not one number.** `#band_supports` (capacity) = how many
tiers the *test set* could resolve (1 + width/LSD); `#observed` (occupancy) = how many tiers the 5 runs
actually landed in. A wide band can have a high capacity yet a bad SHAPE (e.g. a lone low outlier under a
converged pack), so a large `#supports` next to a `NO` is not a contradiction: the verdict weighs shape and
(for the covertype co-amp tasks) cross-eval reproducibility, which a single eval's capacity cannot see.
The static sigma is a *sampling-noise* floor only; it does not capture run-to-run skill dispersion, so
`#supports` is an upper bound on resolvability, never a claim that the 5 runs form a skill gradient.

## The grid table

One row per task, sorted by the binary knobs (the last four columns) so the table reads as the 2x2^3 grid.

| task | metric | band | spread | #obs / #supports | verdict | submit | links | type | #cols | co-amp | dataset |
|---|---|---|---|---|---|---|---|---|---|---|---|
| california-impute-direct | recovery | 0.364–0.523 | **0.158** | 5 / **14.11** | viable: 5 distinct tiers realized over spread 0.16 (capacity 14.1) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/76263f44-25bb-48a4-82f1-6383a214e8f8) · [eval](https://horizon.bespokelabs.ai/evaluations/41ae826f-3fec-4b9a-938e-bbcbd0e225df) · [record](tasks/california-impute-direct.md) | Num | Single | No | california |
| covertype-impute-direct-single | recovery | 0.620–0.710 (endpoints only, not downloaded) | **0.090** | 2 / **17.45** | WORKS (clustered): band 0.62-0.71; only the endpoints are on record (full run set not downloaded) | **YES** (clustered) | [task](https://horizon.bespokelabs.ai/tasks/6ed892d5-8d1b-49f2-b70e-df65a6957813) · [record](tasks/covertype-impute-direct-single.md) | Num | Single | No | covertype |
| california-impute-coamp-single | recovery | 0.151–0.262 | **0.111** | 4 / **7.46** | viable: 4 distinct tiers realized over spread 0.11 (capacity 7.5) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/f771caff-3d94-42f6-9804-7751bb1e06af) · [eval](https://horizon.bespokelabs.ai/evaluations/0253d895-67be-40b9-a006-15d66a821a7f) · [record](tasks/california-impute-coamp-single.md) | Num | Single | Yes | california |
| covertype-impute-coamp-single | recovery | 0.533–0.610 | **0.077** | 3 / **12.07** | only 3 tiers realized (#obs) of the ~12 the test could resolve: a lone low outlier under a converged 0.59-0.61 pack. Rescue re-runs (more test data, harder amputation) both re-converged -> intrinsically sample-dependent, eliminated | NO (clustered) | [task](https://horizon.bespokelabs.ai/tasks/d6237f92-5541-495d-a90e-25316f0247b1) · [eval](https://horizon.bespokelabs.ai/evaluations/63093dca-ac27-48ad-891b-b0485a5c4d63) · [record](tasks/covertype-impute-coamp-single.md) | Num | Single | Yes | covertype |
| california-impute-direct-multi | recovery | 0.400–0.600 (endpoints only, not downloaded) | **0.200** | 2 / **27.08** | WORKS (widest numeric band): 0.40-0.60; only the endpoints are on record (full run set not downloaded) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/596e923b-bb5d-4dd8-af48-19a2227c0ee0) · [record](tasks/california-impute-direct-multi.md) | Num | Multi | No | california |
| covertype-impute-direct | recovery | 0.271–0.385 | **0.114** | 4 / **18.97** | viable: 4 distinct tiers realized over spread 0.11 (capacity 19.0) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/ff227290-a39d-4cf8-a162-4d79b580743f) · [eval](https://horizon.bespokelabs.ai/evaluations/c56b6c86-36e5-45da-9f9b-8d40ae038f2b) · [record](tasks/covertype-impute-direct.md) | Num | Multi | No | covertype |
| california-impute-coamp-multi | recovery | 0.270–0.395 | **0.124** | 5 / **13.14** | viable: 5 distinct tiers realized over spread 0.12 (capacity 13.1) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/ef7addc9-3664-4b21-814d-75d9ae0a8080) · [eval](https://horizon.bespokelabs.ai/evaluations/ba56e09b-b0fb-4c2e-a7ae-49bdcbef8fdc) · [record](tasks/california-impute-coamp-multi.md) | Num | Multi | Yes | california |
| covertype-impute-coamp-multi | recovery | 0.288–0.329 | **0.041** | 3 / **7.33** | tight pack ~0.29 (width 0.04) with one high outlier; rescue re-runs stayed converged -> covertype's redundant residual gives intrinsically low separation, eliminated | NO (clustered) | [task](https://horizon.bespokelabs.ai/tasks/9e443879-143e-43f7-a6cb-6c57bdb03239) · [eval](https://horizon.bespokelabs.ai/evaluations/5114329d-9b82-4d24-8759-5cf8031a7f44) · [record](tasks/covertype-impute-coamp-multi.md) | Num | Multi | Yes | covertype |
| adult-impute-cat-single | recovery | 0.228–0.246 | **0.018** | 2 / **2.63** | occupation single converges: one classifier recipe -> shared MI ceiling ~0.24 | NO (converged) | [task](https://horizon.bespokelabs.ai/tasks/afba95ba-144c-47bb-9f1b-6707c4eb67fe) · [eval](https://horizon.bespokelabs.ai/evaluations/2be818d8-dd93-4f9b-9143-87112ac09d76) · [record](tasks/adult-impute-cat-single.md) | Cat | Single | No | adult |
| bank-impute-cat-single | recovery | 0.232–0.269 | **0.037** | 2 / **3.52** | job single converges on a 2nd dataset (four runs bunched ~0.233), confirms single-cat convergence | NO (converged) | [task](https://horizon.bespokelabs.ai/tasks/970837ef-cf77-4717-b134-e5f8b5dd5ffc) · [eval](https://horizon.bespokelabs.ai/evaluations/ec944173-61c8-4030-ab90-96a2d938d93b) · [record](tasks/bank-impute-cat-single.md) | Cat | Single | No | bank |
| adult-impute-cat-coamp-single-occ | recovery | 0.091–0.168 | **0.077** | 3 / **7.97** | viable: 3 distinct tiers realized over spread 0.08 (capacity 8.0) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/4d90aba0-2d22-4973-b3d4-204d9f813f24) · [eval](https://horizon.bespokelabs.ai/evaluations/56635973-4eea-4d80-9bde-f765ae6f7e9e) · [record](tasks/adult-impute-cat-coamp-single-occ.md) | Cat | Single | Yes | adult |
| bank-impute-cat-coamp-single-job | recovery | 0.051–0.075 | **0.024** | 2 / **2.62** | floored: job's single carrier is education; co-amputating it collapses recovery to naive | NO (floored) | [task](https://horizon.bespokelabs.ai/tasks/6beaf077-62ad-4565-ba11-754036ce1484) · [eval](https://horizon.bespokelabs.ai/evaluations/7f7f6ea9-2ba4-4895-9e75-8349b18aa5d0) · [record](tasks/bank-impute-cat-coamp-single-job.md) | Cat | Single | Yes | bank |
| adult-impute-cat-multi | recovery | 0.365–0.449 | **0.084** | 3 / **7.78** | viable: 3 distinct tiers realized over spread 0.08 (capacity 7.8) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/fe13c0a7-39dc-4bbe-95b2-eae213467db3) · [eval](https://horizon.bespokelabs.ai/evaluations/b7da47bf-8993-46b4-a1fc-b692b070602e) · [record](tasks/adult-impute-cat-multi.md) | Cat | Multi | No | adult |
| bank-impute-cat-multi | recovery | 0.142–0.227 | **0.085** | 3 / **7.64** | viable: 3 distinct tiers realized over spread 0.08 (capacity 7.6) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/f38b591d-24f3-438a-8f52-db48b286c6ea) · [eval](https://horizon.bespokelabs.ai/evaluations/175c88fc-d0ca-41e6-ad7f-30bdcdcfd22a) · [record](tasks/bank-impute-cat-multi.md) | Cat | Multi | No | bank |
| adult-impute-cat-coamp-multi-mild | recovery | 0.292–0.368 | **0.076** | 4 / **7.12** | viable: 4 distinct tiers realized over spread 0.08 (capacity 7.1) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/d78859a7-2bf0-4ceb-b54f-79bdd5718d4c) · [eval](https://horizon.bespokelabs.ai/evaluations/366d5ba6-60b7-4f2d-8f2c-2f132013f325) · [record](tasks/adult-impute-cat-coamp-multi-mild.md) | Cat | Multi | Yes | adult |
| bank-impute-cat-coamp-multi-mild | recovery | 0.065–0.119 | **0.054** | 3 / **5.26** | viable: 3 distinct tiers realized over spread 0.05 (capacity 5.3) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/aaf3e2af-455c-41cd-ad9d-b622be25f6d6) · [eval](https://horizon.bespokelabs.ai/evaluations/f834e331-1ae0-4063-b789-8cbc4193cb4a) · [record](tasks/bank-impute-cat-coamp-multi-mild.md) | Cat | Multi | Yes | bank |
| diabetes-impute-cat-multi | recovery | 0.260–0.280 (3 valid runs + 2 agent crashes on the 90-103-class diag cols; eval id not recorded) | **0.020** | 2 / **2.33** | clinical modality; 3 valid runs converge ~0.27; marginal | NO (converged) | [task](https://horizon.bespokelabs.ai/tasks/28bebcc0-f53e-4e2d-8518-5888e7d8c2a8) · [record](tasks/diabetes-impute-cat-multi.md) | Cat | Multi | No | diabetes (extra modality) |
| adult-impute-cat-coamp-multi | recovery | 0.292–0.319 | **0.027** | 2 / **3.15** | co-amputating BOTH educ predictors over-hardened -> converged ~0.30; mild variant is the WORKS one | NO (over-hardened) | [task](https://horizon.bespokelabs.ai/tasks/e8f5f994-0b95-46bc-a424-43d797c84fe0) · [eval](https://horizon.bespokelabs.ai/evaluations/ecee2395-e78b-4b7e-b007-5c0e5bd70099) · [record](tasks/adult-impute-cat-coamp-multi.md) | Cat | Multi | Yes | adult (aggressive variant) |
| adult-impute-cat-coamp-single | recovery | 0.051–0.074 | **0.023** | 1 / **1.96** | low-cardinality relationship (K=6) floored; superseded by adult-impute-cat-coamp-single-occ | NO (floored) | [task](https://horizon.bespokelabs.ai/tasks/dc36b759-947b-4c4a-96d4-13ba958ee3ff) · [eval](https://horizon.bespokelabs.ai/evaluations/ef3a3efd-09a0-43fe-a4ba-d970ba310950) · [record](tasks/adult-impute-cat-coamp-single.md) | Cat | Single | Yes | adult (superseded) |
| bank-impute-cat-coamp-single | recovery | 0.000–0.009 | **0.009** | 1 / **1.32** | low-cardinality education (K=4) floored to ~0; superseded by bank-impute-cat-coamp-single-job | NO (floored) | [task](https://horizon.bespokelabs.ai/tasks/0ab1d73b-33a1-4ca5-b9c2-e0313e2453b9) · [eval](https://horizon.bespokelabs.ai/evaluations/70d88898-69de-41f1-acc7-14d86f5abf5a) · [record](tasks/bank-impute-cat-coamp-single.md) | Cat | Single | Yes | bank (superseded) |

The table above IS the grid. The last four columns are the three INPUT knobs
(README_general_direction §15): **type** (numeric/categorical) x **# columns** (single/multi) x
**co-amputate** (no/yes) = 8 slots, realized on 2 datasets each = 16 cells, and rows are sorted in that
binary order (type -> #cols -> co-amp -> dataset). The 16 clean grid cells come first; below them are
superseded attempts and extras (their `dataset` cell carries the note): `adult-impute-cat-coamp-single`
(relationship K=6, floored -> replaced by the occupation salvage), `bank-impute-cat-coamp-single`
(education K=4, floored -> replaced by the job attempt), `adult-impute-cat-coamp-multi` (both educ
predictors co-amputated, over-hardened -> converged; the mild variant is the WORKS one), and
`diabetes-impute-cat-multi` (extra clinical modality, converged ~0.27). Not in the grid at all:
`covertype-impute` (downstream macro-F1; flat 0.48-0.50, PARKED).

## Findings

**Categorical inverts the numeric pattern.** Numeric: *single* spreads, *multi* can dilute (covertype).
Categorical: *single* **converges** (one classifier recipe -> shared MI ceiling; occupation ~0.24, job
~0.23 on both datasets), while *multi* **spreads** (columns of unequal difficulty; solutions vary in how
they exploit that the targets are mutually predictive).

**Co-amputate (slots 2 & 4).** Numeric: California co-amp spreads (fragile feature-*combination* recovered
with run-to-run skill), covertype co-amp is ELIMINATED (the 44 residual soil/wilderness indicators let
strong tree models converge; two rescue levers, more test data and harder amputation, both failed). Lesson:
oracle/vet reconstructability predicts floor-collapse, NOT the spread; only a real eval measures the band.

**Categorical co-amputate (the two last slots).** `co_amputate` nulls all targets on the SAME rows,
removing the co-observed sibling redundancy that made Cat·Multi·No spread. Consequences measured:
- **Cat·Single·Yes floors on LOW-cardinality, WORKS on HIGH-cardinality.** relationship (K=6), education
  (K=4), and job (K=12, education-carried) all FLOORED: each has a single strong carrier, co-amputate it ->
  collapse to naive. The fix (high-cardinality, distributed-predictor target): **occupation (K=14)**,
  co-amputating educ+educ-num, spreads 0.091->0.168, #band_supports ~8 -> WORKS. The floor was a
  target-choice artifact, not a slot property; target-specific (bank job floored), not dataset-specific.
- **Cat·Multi·Yes works at the right hardening.** Co-amputating BOTH occupation predictors over-hardened ->
  converged ~0.30; keeping `education` observed and removing only educ-num -> spread 0.29-0.37 (Adult) and
  a wide bimodal 0.065-0.119 (Bank). Hardening is a dial, not a switch.
- **The discriminated skill is modeling hygiene, not imputation sophistication** (5-solution analyses in
  the two records): occupation-single is sorted by regularization/averaging depth; adult mild-multi by
  estimator family. MICE chaining and reconstructing the co-amputated columns are inert (red herrings).

**The two direct tasks discriminate on DIFFERENT skills (non-redundant).** `covertype-impute-direct` and
`california-impute-direct` share the engine, but the biggie band on each is sorted by a different axis:
covertype by **diverse multi-family ensembling** (mean over 3 heterogeneous targets rewards model diversity),
california by **transductive train+test pooling** (one half-missing column -> pooling 6-7x's the fit rows).
Both punish MICE over-iteration and label use, and floor the pure-inductive fit. Same metric, different
bottleneck -> coverage of the skill, not a repeat.

## Methodology (brief)

- **Metric:** direct cell-recovery on the held-out TEST amputed cells vs truth (`1 - RMSE/RMSE_naive`
  numeric; `1 - err/err_naive` = accuracy vs majority categorical), averaged over target cols, clamped
  [0,1]. `best_observed = 1` -> raw scores.
- **Model:** every eval uses **biggie-max-polara**, agent-type **meteor**, hosted. Each rollout is a
  different solution, so the multi-run spread IS biggie's skill band (not re-run noise). Batch:
  `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`.
- **Handshake:** code-only, test hidden (deferred `train_at_grade`); the grader re-runs the submitted
  `solution.py` on the full held-out test at grade. Downloaded rollouts live in
  [`analysis/<eval8>/`](../analysis/) (heavy transcripts gitignored; the slim `band_supports.json` is
  committed).

## Per-task records

One record per task under [`readmes/tasks/`](tasks/), linked from each master-table row's `links` cell and
kept in sync by the invariant validator. Records are generated (`--emit`); the two flagship direct-recovery
tasks and the two categorical co-amp spreaders carry an extra strategy `narrative` (5-solution comparison).
