#!/usr/bin/env bash
set -euo pipefail
# Run under model_venv (the prehook amputates the student view with numpy). IMPUTATION_TASK selects
# which task's merged config active_config() resolves (also baked as an image ENV; exported here
# defensively).
export IMPUTATION_TASK=adult-impute-cat-coamp-single
/venvs/model_venv/bin/python -m worlds.imputation.prehook
