FROM apex_arena:base
WORKDIR /workdir

# SINGLE shared Dockerfile for every imputation task. materialize() renders this (baking the task
# name into {{TASK_NAME}}). The COPY-FROM paths are ./tests/<pkg> because materialize injects the
# code packages under tests/ (the apex strict allowlist), so this file and materialize agree by
# construction. Do NOT hand-copy this per task.

RUN chmod 1755 /tmp

ENV PIP_NO_COLOR=1 \
    HF_HUB_DISABLE_PROGRESS_BARS=1 \
    HF_DATASETS_DISABLE_PROGRESS_BARS=1 \
    TQDM_DISABLE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/root/src \
    UV_HTTP_TIMEOUT=180 \
    UV_CONCURRENT_DOWNLOADS=4

# Which task this image is. active_config() reads this at build (setup_data) and prehook time.
ENV IMPUTATION_TASK={{TASK_NAME}}

# Layers heavy->cheap so editing grader/config never re-runs venv install or the data layout.

# ── Pre-flight checks (fast; fail before heavy work) ──────────────────────────
RUN mkdir -p /root/src
COPY ./task.yaml                       /root/src/task.yaml
COPY ./src/pre_build/check_build.py    /root/src/check_build.py
RUN python3 /root/src/check_build.py

# ── Heavy 1: venvs (model + grader) ───────────────────────────────────────────
RUN --mount=type=bind,source=./src/venvs,target=/tmp/venvs \
    UV_PROJECT_ENVIRONMENT=/venvs/model_venv uv sync \
        --project /tmp/venvs --only-group model --frozen \
    && UV_PROJECT_ENVIRONMENT=/venvs/grader_venv uv sync \
        --project /tmp/venvs --only-group grader --frozen --compile-bytecode \
    && chmod 755 /venvs \
    && chown -R model:model /venvs/model_venv \
    && chmod -R 755 /venvs/model_venv \
    && chmod -R 700 /venvs/grader_venv \
    && rm -rf /root/.cache/uv

# ── Heavy 2: inject code packages (from tests/) + build /data_root ────────────
RUN mkdir -p /root/src /data_agent /data_root
COPY ./tests/sdk        /root/src/sdk
COPY ./tests/worlds     /root/src/worlds
COPY ./tests/tasks_def  /root/src/tasks_def
# setup_data loads the committed npz (pure np.load, no download) and writes /data_root/<data_rel>.
RUN /venvs/model_venv/bin/python -m worlds.imputation.setup_data
RUN chmod -R 700 /data_root & chmod -R 755 /data_agent & wait

# ── Lock down all source under /root/src ──────────────────────────────────────
RUN chmod -R 700 /root/src

RUN mkdir -p /workdir/solution && \
    chown -R model:model /workdir/solution && \
    chmod -R 755 /workdir/solution

RUN mkdir -p /workdir/tmp && chown model:model /workdir/tmp && chmod 755 /workdir/tmp
ENV TMPDIR=/workdir/tmp TMP=/workdir/tmp TEMP=/workdir/tmp

COPY ./setup.sh /mcp_server/tasks/{{TASK_NAME}}/setup.sh
RUN chmod +x /mcp_server/tasks/{{TASK_NAME}}/setup.sh

COPY ./tests/    /tests/
COPY ./grader.py /tests/
RUN chown -R root:root /tests && chmod -R 700 /tests
