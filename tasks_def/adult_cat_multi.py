"""The adult-impute-cat-multi task (grid: Adult · Categorical · Multi · No-coamp)."""
from sdk import repo_root
from tasks_def.configs import adult_cat_multi as config
from worlds.imputation.world import ImputationWorld

ADULT_CAT_MULTI_TASK = ImputationWorld(
    name="adult-impute-cat-multi",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "adult-impute-cat-multi",
)
