"""The diabetes-impute-cat-multi task (grid: Diabetes · Categorical · Multi · No-coamp)."""
from sdk import repo_root
from tasks_def.configs import diabetes_cat_multi as config
from worlds.imputation.world import ImputationWorld

DIABETES_CAT_MULTI_TASK = ImputationWorld(
    name="diabetes-impute-cat-multi",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "diabetes-impute-cat-multi",
)
