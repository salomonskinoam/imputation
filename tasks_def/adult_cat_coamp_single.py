"""The adult-impute-cat-coamp-single task (categorical co-amputate)."""
from sdk import repo_root
from tasks_def.configs import adult_cat_coamp_single as config
from worlds.imputation.world import ImputationWorld

ADULT_CAT_COAMP_SINGLE_TASK = ImputationWorld(
    name="adult-impute-cat-coamp-single",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "adult-impute-cat-coamp-single",
)
