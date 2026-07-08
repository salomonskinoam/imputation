# self-review — california-impute-direct

**Verdict (band):** viable, 5 distinct tiers over spread 0.158 (capacity 14.1).
**Submit: BLOCKED** on F3 (CRITICAL root-grade-rerun reward hack, world-wide) + F4 (oracle fails hosted
validation). Band is fine; the world's grade-time isolation is not. See Findings.
**Band:** 0.3645 · 0.4376 · 0.4499 · 0.4964 · 0.5227 (eval `41ae826f`, 5/5 non-degenerate).
**Links:** [task](https://horizon.bespokelabs.ai/tasks/76263f44-25bb-48a4-82f1-6383a214e8f8) ·
[eval](https://horizon.bespokelabs.ai/evaluations/41ae826f-3fec-4b9a-938e-bbcbd0e225df) ·
[record](../worlds/imputation/readmes/tasks/california-impute-direct.md) ·
[analysis](../worlds/imputation/analysis/california-impute-direct/STRATEGY.md)

Premise: amputate `median_income` (col 0 of 8) at ~50% under MAR driven by latitude; grade recovered
TEST cells vs truth, `1 − RMSE(method)/RMSE(mean-fill)`. Single numeric target, no co-amp.

Evidence tags: `[code]` read from source, `[eval]` from the 5-run rollout, `[pending]` needs a run.

---

## 1. Task description + Dockerfile

### Task anatomy follows the spec
**YES** `[code]` — files present: [task.yaml](../tasks/california-impute-direct/task.yaml),
[grader.py](../tasks/california-impute-direct/grader.py) (delegates to `CALIFORNIA_DIRECT_TASK.grade()`),
[solution.sh](../tasks/california-impute-direct/solution.sh), [setup.sh](../tasks/california-impute-direct/setup.sh),
`tests/README.txt`, `src/venvs/{pyproject.toml,uv.lock}`, `src/{pre_build,pre_push,pre_agent}`. Dockerfile is
the shared world template ([worlds/imputation/Dockerfile](../worlds/imputation/Dockerfile)); tasks ship none, per world rule.
`task.yaml` prompt is `<PLACEHOLDER>` in git, injected at push by `src.pre_push.prompt_builder`; a pre_build
check ([check_build.py](../tasks/california-impute-direct/src/pre_build/check_build.py)) blocks push if it survives, so the pushed task the reviewer sees has the real prompt.

### Metadata fields present + sensible
**YES** `[code]` — `difficulty: medium`, `category: machine learning`, tags (imputation, missing-data, tabular,
california-housing, direct-recovery), `references`. Values match the task (medium difficulty consistent with the
0.36–0.52 band: recoverable, not trivial). Category set to `machine learning` per owner call (was `imputation`).

### Datasets properly cited
**YES** `[code]` — `references: "California housing (Pace & Barry, 1997), OpenML id=537"`, matches the config
provenance in [configs/california_direct.py](../tasks_def/configs/california_direct.py) (StatLib, 1990 census, OpenML 537). Public, non-benchmark dataset, so no plagiarism concern.

### Description looks human-written / doesn't ramble
**YES (accepted)** `[code]` — generated from the [prompt_builder.py](../worlds/imputation/prompt_builder.py)
template; decision on record: a generated prompt is fine as long as the template is coherent, and it is (data
layout → scoring → deliverable contract → 0-row/hidden-test warning → live package list). No backstory, no fluff,
no test/grader leakage in the prompt body.

### All dependencies pinned
**YES** `[code]` — [pyproject.toml](../tasks/california-impute-direct/src/venvs/pyproject.toml) pins exact
versions: `numpy==2.1.3`, `scikit-learn==1.5.2`, `torch==2.5.1` (CPU wheel index), grader group likewise;
`uv.lock` committed. No floating ranges.

### One premise / workflow
**YES** `[code]` — single coherent task: recover one amputed numeric column. No unrelated subtasks.

### Dockerfile has the libraries the agent needs
**YES** `[code]` — `model_venv` provides numpy + scikit-learn (the oracle uses `IterativeImputer` +
`HistGradientBoostingRegressor`) + torch. Internet blocked; the prompt says so and pip would fail, all deps
pre-synced. torch is available but unused by the oracle (headroom for the student), acceptable.

## 2. Requirements alignment

### A test/grader path for each requirement
**YES (RE)** `[code]` — the requirement is "recover the missing cells accurately"; it is graded directly by
`_direct_score` in [verify.py](../worlds/imputation/verify.py) (per-column `1 − RMSE/RMSE_naive`, mean over amputed
target cols). In the HorTask model the grader IS the requirement check; the lone pytest `test_solution_scored`
only asserts the artifact gate. Shape/finiteness/no-NaN requirements → `check_artifact` gate. Aligned: everything
the prompt asks for (write two arrays, right shape, finite, only-missing scored) is enforced.

### Description not ambiguous
**YES** `[code]` — the prompt fixes the output paths, both shapes `(n, 8)`, column order preserved, "every value
finite", "only the originally-missing cells are scored", and the 0-row test handling. No "sort but unspecified
order" class of ambiguity.

## 3. Solution verification

### Oracle runs correctly and scores in-band, deterministically
**YES (RE)** `[code+eval]` — [solution.sh](../tasks/california-impute-direct/solution.sh) writes a 0-row-safe
`solution.py` (IterativeImputer+HGB, `random_state=0`), reads row counts at runtime, guards the empty test.
"Scores 100%, tested 3x" is struck (binary framing). The remaining real concern (does the graded path run
cleanly?) is already met: the 5-run eval graded 5 distinct solutions to valid in-band scores, and the reference
is deterministic. No separate oracle-validate is owed now (oracle promotion is a taiga-final step, not this cycle).

### Solution is not hardcoded
**YES** `[code]` — a genuine conditional imputer, no answer baked in. The deferred handshake (0-row test
placeholder during the rollout, full hidden test substituted at grade) makes hardcoding test values impossible by
construction.

### No look-ahead bias
**YES** `[code+eval]` — test is hidden; grader re-runs the submitted `solution.py` on the full held-out test at
grade. The strongest rollouts pool train+test *features* (transductive), which is legitimate: test *labels* never
exist in `/data_agent`, and the agent never sees the test set, its code does the pooling when the grader runs it.
No target leakage.

### Solution does not read/write tests/
**YES** `[code]` — reads `/data_agent/california`, writes `/workdir/solution/`. Never touches `tests/`.

## 4. Test quality

### Not brittle
**YES** `[code]` — scoring is numeric (RMSE ratio); no regex, no string matching, no import-string checks.

### Hardcoded thresholds reasonable
**YES (RE)** `[code]` — no pass/fail threshold exists (continuous score). Score clamped to [0,1]; the naive
baseline (train-observed column mean) is a principled, non-arbitrary reference, not a tuned cutoff.

### No test assumes unstated behavior
**YES** `[code]` — grader scores exactly the amputed cells of the configured `target_cols`, which is what the
prompt describes. Nothing graded that the prompt does not ask for.

### Test functions have docstrings
**YES (fixed)** `[code]` — `test_solution_scored` in [verify.py](../worlds/imputation/verify.py) now has a
WHAT/WHY docstring (was F1). Shared file, so the fix covers all 10 tasks.

### Ground truth isolated from the agent
**YES (mapped)** `[code]` — the checklist's "grader reads from tests-folder copy" maps to: truth (clean features
+ all labels) lives in `/data_root` at 700, grader-only; `/data_agent` (755) holds only corrupted features +
train labels. `leak_guard()` in [prehook.py:56](../worlds/imputation/prehook.py#L56) asserts no `test_labels.npy`
reaches `/data_agent`. This is stronger than a tests-folder copy.

## 5. Grader quality

### Non-determinism / flaws / bugs
**YES** `[code]` — `compute_scores` is a pure function of the on-disk arrays; oracle imputer is seeded; the naive
baseline uses train-observed mean vs test truth (principled). Re-scoring one fixed solution is deterministic. No
obvious bug in the numeric path; clamp guards divide-by-tiny (`base <= 1e-12 → 0`).

### GradingResult has proper subscores/weights
**YES (RE)** `[code]` — single primary objective `recovery`; `_direct_score` also returns `per_col` detail and
persists `predictions_b64` for offline resolution. No weighted subscores because the task is single-objective
(one target col here); the mean-over-cols weighting is uniform and appropriate. Note for multi-target tasks: same
uniform mean, revisit if unequal-difficulty columns should be weighted (not this task).

## 6. Evaluation review

### Rollout: weak runs fail for good reasons (band separation)
**YES (RE)** `[eval]` — reframed from pass/fail to band separation. Per
[STRATEGY.md](../worlds/imputation/analysis/california-impute-direct/STRATEGY.md): the band is sorted by
**transductive train+test pooling**, then simplicity. The two poolers take the top two slots (0.523, 0.496); the
three inductive fits sit below (0.450, 0.438, 0.364). The low runs lose for an interpretable, learnable reason
(inductive ceiling; MICE over-iteration and label use are inert), not a dumb one. All 5 pairwise separable.

### Hard/impossible to reward-hack
**NO (CRITICAL — F3)** `[argus]` — my initial YES was WRONG. It held only for the *rollout* uid (1000). At
*grade* time the deliverable re-run executes as **root** (no privilege drop in `run_in_venv`), so `solution.py`
can read `/data_root` truth and copy `test_features.npy` into `test_imputed.npy` for `recovery=1.0`. Argus
verified with a probe (uid=0, `LEAK_OK`, total=1.0). See F3. Applies to all 10 direct-recovery tasks.

## 7. Platform compatibility

### Runs on all machines (Linux/Mac, x86/arm)
**YES (likely)** `[code]` — pure Python + numpy/sklearn/torch-cpu, no arch-specific code or native extensions we
control; torch pinned to the CPU wheel. `[pending]` not explicitly exercised on Mac/arm, but nothing arch-bound.

## 8. Task spec compliance

### Meets the project spec
**YES (RE)** `[code]` — evals use `biggie-max-polara`, agent-type `meteor`, hosted, machine `e2-custom-16-32768`
(per CLAUDE.md). Category `imputation`. "Pass rate" is reframed as the band (spread 0.158, 5 tiers). Compute fits
the 6-vCPU/32 GB envelope.

## 9. Additional review

### Own review beyond the checklist
**YES** — this document. Additional angle checked: the pooling strategy is not a leak (verified test labels never
materialize in `/data_agent`); the band is a real skill gradient, not re-run noise (each rollout is a distinct
solution).

### No LLM used to review
**NA (flagged)** — this self_review harness is explicitly LLM-run author-side pre-review. The checklist's
"no LLM" attestation is for the human reviewer's official pass and is out of scope for this file. Human sign-off
stays separate.

---

## Findings / action items

- **F3 (CRITICAL — reward hack, WORLD-WIDE):** grade-time re-run of `solution.py` executes as **root**, so it can
  read `/data_root` truth and forge `recovery=1.0` by copying `test_features.npy`. Argus-verified (uid=0,
  total=1.0) across Env&Grading Lint / Reward Hack / Static Checklist. Hits all 10 direct-recovery YES tasks.
  Fix: run the grade-time deliverable re-run as uid=1000 (thread `user=1000/group=1000` into the re-run, matching
  the agent bash tool) so the 700-root barrier holds at grade time. Honest solutions (read `/data_agent` only)
  unaffected; leak script → ~0. **Blocker; needs owner decision on where the fix lands (SDK `run_in_venv` vs a
  world-level `_produce` override).**
- **F4 (ERROR — oracle fails validation):** direct-mode score is unnormalized (`_direct_score` never applies
  `best_observed`), so the reference scores 0.3673 raw and permanently fails the platform's `>=0.999` oracle gate;
  it is also beaten by 4/5 rollouts (train-only, not transductive). Fix (a): set `best_observed` to the achievable
  ceiling (~0.43) + re-tune `solution.sh` transductive; or (b) relax the binary oracle gate for continuous tasks
  (platform-side, not in our control). Ties directly to the open framing question below.
- **F1 (fixed):** added a WHAT/WHY docstring to `test_solution_scored` in the shared
  [verify.py](../worlds/imputation/verify.py); covers all 10 tasks.
- **Category (fixed):** `task.yaml` category set to `machine learning` (per owner). Same change is owed on the
  other 9 YES tasks' `task.yaml` during fan-out.

## Open questions

- Reviewer-facing framing: does the reviewer accept the band-separation narrative in lieu of a pass/fail rollout?
  If not, we need a one-paragraph "why partial grading" note attached at submission.

## Review log

- Initial pass from source + the 5-run eval + record + STRATEGY. (Wrongly cleared reward-hack; see below.)
- Applied: F1 docstring (shared verify.py) and category → `machine learning`.
- **Argus run on task v1** (4 rubrics, all completed): Reward Hack **FAIL**, Static Checklist **FAIL**,
  Environment & Grading Lint **FAIL**, Dynamic Checklist **FAIL**. Findings collapse to two real defects:
  **F3** (CRITICAL root-grade-rerun leak, world-wide) and **F4** (unnormalized oracle fails hosted validation).
  QC tab: https://horizon.bespokelabs.ai/tasks/76263f44-25bb-48a4-82f1-6383a214e8f8?tab=qc-agent
- Status flips to **BLOCKED on F3** (security). F3 must be fixed and re-verified before this task can submit; the
  fix is engine-level so it clears the blocker for all 10 tasks at once.
