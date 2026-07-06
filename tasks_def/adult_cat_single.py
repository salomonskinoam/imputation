"""The adult-impute-cat-single task (grid: Adult · Categorical · Single · No-coamp)."""
from sdk import repo_root
from tasks_def.configs import adult_cat_single as config
from worlds.imputation.world import ImputationWorld

ADULT_CAT_SINGLE_TASK = ImputationWorld(
    name="adult-impute-cat-single",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "adult-impute-cat-single",
)
