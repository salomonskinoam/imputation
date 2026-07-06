# Claude working notes — imputation
Always look at the sdk docs and skills, they define methodology.


## What this repo is

An SDK "world" of **missing-value imputation** tasks (a `HorTask` subclass + task instances), built on
`sdk/` and structured like the reference world `../multimodal_fusion/`. Take REAL tabular data,
**amputate** (delete/NaN) cells, and grade how well the student handles them. Two task shapes:
- **Direct recovery** (working — `covertype-impute-direct`): grade imputed cells vs truth.
- **Downstream** (`covertype-impute`): predict a label through a fixed model; PARKED — too easy on
  Covertype (a standardizing linear model routes around the missingness). See below.

Design + findings live in `readmes/README_general_direction.md` and `readmes/README_building_the_world.md`
(running docs). Key code: `worlds/imputation/` (`config_world, amputate, setup_data, verify, world,
paths, prehook, prompt_builder, active, Dockerfile, data/*.npz`), `tasks_def/` (configs + instances),
`tasks/<task>/` (apex shims), root `hor.py`.

## Heavy local runs — ONLY with explicit user approval (never automatic)

**Never start heavy local compute on your own.** No local model fits, imputers, bootstraps, vetting,
resolution/σ measurement, or re-running agent submissions WITHOUT the user first approving that specific
run. It is a shared dev box; unapproved heavy jobs have wedged/crashed it (incl. "capped"/`nice`/`nohup`
— they still spike and `nohup` outlives the session). Reading files, editing, git, the hosted CLI, and
light data vendoring are always fine.

**Default to HOSTED for measurement.** Prefer vetting/oracle-band/resolution checks as a **validation run
on a THROWAWAY task** (create → push → `validate -a oracle` → read score → discard) or an
`evaluations submit`. If something genuinely needs local compute, STOP and ask the user to approve it
first; only run it once they say yes.

**New-task flow = EVAL-DIRECTLY (the local classifier vet is opt-in, ask first).** To add a task: vendor
(light) → **glance at the target columns' class balance / cardinality** (`np.bincount` on the npz — free,
no model) to pick sane targets (skip binary + mode-dominated cols) → build → **`evaluations submit` (7
runs)**. Do NOT auto-run a local reconstructability/classifier vet — the vet never predicts the band (only
a real eval does); its only extra value over the free class-balance glance is catching a floored/trivial
target, which the eval reveals anyway. The classifier vet stays available but is a heavy local run:
**ask the user before running it**, never automatically. Accept that an occasional eval returns a dud
(floored/converged) — that is a documented negative, cheaper than crashing the box.

## Scores: spread only
**We do NOT care about the mean. Only the SPREAD (the band).** Report min/max/std/spread/mean across runs,
but conclusions on viability are from the spread. A tight cluster is a bad task even at a high mean. single high outliers to a packed score are good. single low outliers are not as good.
std is much less telling than spread, and spread needs to also be reported as "how many distinct levels does it contain", as defined in the sdk docs

## Writing style

- Never use the em-dash. Use a comma, period, or parentheses. Also no "--" as a substitute.
- Keep drafts short. Fewer words than you think you need.
- OMIT any "co-authored by Claude" line from git commits.
- No inline imports. All imports at the top of the file, always.

## Grader timeout

**The platform's time cap is the ONLY timeout. Never impose a shorter grader-side watchdog, and
never reduce a timeout below the platform's.** The cap is the sysadmin's to own and to raise (one day they will);
our code must not undercut it. A hanging policy is killed by that cap and doesn't score, and we deal with it.

## Evaluations — biggie-max-polara ONLY

- **Every eval uses `--model biggie-max-polara`. Never run any other model — there is no point.**
- Agent-type: always **`meteor`** (`--agent-type meteor`), hosted.
- Machine: `e2-custom-16-32768` (16 vCPU / 32 GB). Command:
  `horizon evaluations submit <task-id> --runs N --model biggie-max-polara --agent-type meteor --machine-type e2-custom-16-32768 --json`
- Note: each rollout is a DIFFERENT solution the model writes, so the multi-run score spread IS that
  model's skill band on the task (biggie's band). Do NOT call it noise. Re-run NOISE (σ) is a separate
  thing: re-scoring ONE fixed solution across seeds (~0 for pinned seeds) — the resolution ruler only.

## Oracle

- **Never promote a solution to the oracle (`solution.sh`) without explicit user approval.** Present
  the candidate + its score and ask first.
- Oracles are NOT IMPORTANT until the final testing phase on taiga. the best observed until then should just be 1.0 even if we have offline "oracles" for testing. these are fake and do NOT reflect what the actual oracle is.

## Jargon

- **the student** — the agent solving a task. **runs** — evaluations (agent rollouts). "do 5 runs" =
  5 evals. **grader == judge**. **world** — the Docker environment a task lives in.
- **produce** — running the student's solution to generate the graded artifact. NEVER call this
  "build" (build = Docker images only).

## CLI

- Use `horizon_env/bin/horizon` / `horizon_env/bin/python hor.py`. Always NAME the task.
- **Always hosted** (`-m hosted` for validate; `evaluations submit` for evals). Never `-m local`.
- mini_batch_id: `0067d7a3-4134-40d9-a4eb-c29faeeb24fe` (use for all `hor.py create`).
- Flow: `hor.py create <task> --mini-batch-id <id>` → `hor.py push <task>` →
  `horizon tasks validate -m hosted -a noop|-a oracle <task-id> --wait` → `evaluations submit`.
- **Commands are always complete** — fill real values (task name/id, eval id). If a value is unknown,
  say so and how to get it, then stop. Never hand back a `<placeholder>` command.

### Always surface the links

Whenever an eval is submitted/running, give the direct links, no exceptions:
- run: `https://horizon.bespokelabs.ai/evaluations/<eval-id>`
- task: `https://horizon.bespokelabs.ai/tasks/<task-id>`
Show both, as soon as the ids are known and again when results land.

### Validation logs are truncated in the terminal

Hosted validate prints a lossy one-line `Feedback:`. The score is above it (do not `tail` it off).
For build/grade failures read the full log via `horizon tasks validate-logs` — never trust the
terminal summary for debugging.

### Validate -a oracle "FAILED" can be cosmetic

We use raw scores (`best_observed=1`), so a valid oracle scoring <1 makes hosted `validate -a oracle`
report FAILED even though it graded fine. Check the actual score + `all checks passed` in the log;
only a traceback / gate failure is a real failure.

## Lifecycle (get this right or the world breaks)

`vendor (offline → commit npz)` → `setup_data.py` (Docker build → FULL CLEAN to `/data_root`, 700) →
`prehook.py` (container setup, root → amputate the student view to `/data_agent`, 755; deferred:
full train + hidden test) → rollout (student writes `solution.py`) → `stage_inputs()` (grade → reveal
full test) → `_produce` re-runs the deliverable → `verify.py` scores. Encapsulation: test labels +
un-amputated truth live ONLY in `/data_root`; `/data_agent` holds only corrupted features + train
labels; prehook ends with a leak-guard.

Handshake (decided): CODE-only, test HIDDEN. Deferred (`train_at_grade=True`), `peek_test=0` → the
student never sees the real test; the grader re-runs their code on the full held-out test at grade.
Consequence: deliverables must be **0-row-safe** (sklearn `.transform` errors on 0 samples).

## Container paths (from `sdk.path_mappings`; never invent paths)

| Constant | Path | Perms | Purpose |
|---|---|---|---|
| `CONTAINER_DATA_AGENT` | `/data_agent` | 755 | student-visible corrupted data |
| `CONTAINER_DATA_ROOT` | `/data_root` | 700 | grader-only clean data + all labels |
| `CONTAINER_WORKDIR` | `/workdir` | agent r/w | student scratch + `solution/` |
| `CONTAINER_ROOT` / `/root/src` | `/root` , `/root/src` | 700 | grader home / source |
| `CONTAINER_ACTIVE_CONFIG` | `/root/active_config.json` | grader | merged config side-channel |

World rel-paths join onto these in `worlds/imputation/paths.py`. All path values are `pathlib.Path`.
`IMPUTATION_TASK` env (baked in the Dockerfile, exported in `setup.sh`) selects the active task for
`worlds.imputation.active.active_config()`.

## Fail-fast, zero-fallback

One linear code path. Producers always write their output (even empty); consumers read it
unconditionally (missing = crash = surfaced). No `if X.exists()` guards, no stub/placeholder scores,
no conditional degradation. Only business logic branches; technicalities are guaranteed by the
pipeline.

## Dockerfile rules

- ONE shared template per world (`worlds/imputation/Dockerfile`, `{{TASK_NAME}}` baked by
  materialize). Tasks ship no Dockerfile.
- Keep it lean: venv sync (uv, from `src/venvs/`), inject code under `/root/src` from `tests/`, run
  `python -m worlds.imputation.setup_data`, lock permissions. No inline package lists, no logic.

## Running docs

Keep `readmes/README_general_direction.md` (design + findings) and `readmes/README_building_the_world.md`
(build plan) current after any substantive decision/finding. Short entries, no timestamps.

---

When the user wants something "for each X", assign a subagent per X, then synthesize.
