# Claude working notes — imputation

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

## Writing style

- Never use the em-dash. Use a comma, period, or parentheses. Also no "--" as a substitute.
- Keep drafts short. Fewer words than you think you need.
- OMIT any "co-authored by Claude" line from git commits.
- No inline imports. All imports at the top of the file, always.

## Evaluations — biggie-max-polara ONLY

- **Every eval uses `--model biggie-max-polara`. Never run any other model — there is no point.**
- Agent-type: always **`meteor`** (`--agent-type meteor`), hosted.
- Machine: `e2-custom-16-32768` (16 vCPU / 32 GB). Command:
  `horizon evaluations submit <task-id> --runs N --model biggie-max-polara --agent-type meteor --machine-type e2-custom-16-32768 --json`
- Note: each rollout is a DIFFERENT solution the model writes, so the multi-run score spread IS that
  model's skill band on the task (biggie's band). Do NOT call it noise. Re-run NOISE (σ) is a separate
  thing: re-scoring ONE fixed solution across seeds (~0 for pinned seeds) — the resolution ruler only.

## Oracle changes need approval

- **Never promote a solution to the oracle (`solution.sh`) without explicit user approval.** Present
  the candidate + its score and ask first.

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
