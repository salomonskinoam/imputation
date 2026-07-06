"""The adult-impute-cat-coamp-multi-mild task (categorical co-amputate)."""
from sdk import repo_root
from tasks_def.configs import adult_cat_coamp_multi_mild as config
from worlds.imputation.world import ImputationWorld

ADULT_CAT_COAMP_MULTI_MILD_TASK = ImputationWorld(
    name="adult-impute-cat-coamp-multi-mild",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "adult-impute-cat-coamp-multi-mild",
)
