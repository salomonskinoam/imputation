"""The adult-impute-cat-coamp-multi task (categorical co-amputate)."""
from sdk import repo_root
from tasks_def.configs import adult_cat_coamp_multi as config
from worlds.imputation.world import ImputationWorld

ADULT_CAT_COAMP_MULTI_TASK = ImputationWorld(
    name="adult-impute-cat-coamp-multi",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "adult-impute-cat-coamp-multi",
)
