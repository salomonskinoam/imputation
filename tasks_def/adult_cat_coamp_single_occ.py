"""The adult-impute-cat-coamp-single-occ task (high-cardinality Cat·Single·Yes salvage)."""
from sdk import repo_root
from tasks_def.configs import adult_cat_coamp_single_occ as config
from worlds.imputation.world import ImputationWorld

ADULT_CAT_COAMP_SINGLE_OCC_TASK = ImputationWorld(
    name="adult-impute-cat-coamp-single-occ",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "adult-impute-cat-coamp-single-occ",
)
