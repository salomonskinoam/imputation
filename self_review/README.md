# self_review

Running memory for the author-side self-review of each **submit-YES** imputation task, one file per
task: `self-review_<task_name>.md`. A reviewer works one task at a time; each file is that task's
running notebook (walk the live checklist, record status + evidence, keep a findings/open-questions log).
Later we fan out one subagent per file. `california-impute-direct` is the worked exemplar; copy its shape.

## Governing spec (settled)

- Format is **HorTask / fusion** (`task.yaml` + `grader.py` + `/workdir` + `/data_agent` + `solution.sh`),
  NOT Harbor/Project-Mirror. The Harbor docs (`quality_guide`, `finer_quality_control`,
  `task_design_guidelines`) were deleted from `sdk/horizon_docs` as stale.
- Live checklist = `sdk/horizon_docs/review_checklist.md` + `review_process.md` + `common_errors.md`.
- **Struck as stale** (do NOT hold a task to these): "Binary grading only" and "solution scores 100%".
  Our world is continuous score-band grading by design; the reference oracle scores its raw band, and
  `best_observed = 1` until the taiga final phase (see `CLAUDE.md`).

## Status legend

- **YES / NO / NA** as in the checklist.
- **RE** — reframed: the item assumed binary pass/fail; restated for a score-band task.
- **PENDING** — needs a run to confirm (e.g. hosted oracle validate); asserted from code so far.

## The submit-YES set (10)

Only these get a self-review; eliminated tasks are out of scope.

- [ ] california-impute-direct  — **exemplar, done**
- [ ] covertype-impute-direct-single
- [ ] california-impute-coamp-single
- [ ] california-impute-direct-multi
- [ ] covertype-impute-direct
- [ ] california-impute-coamp-multi
- [ ] adult-impute-cat-coamp-single-occ
- [ ] adult-impute-cat-multi
- [ ] adult-impute-cat-coamp-multi-mild
- [ ] bank-impute-cat-coamp-multi-mild
