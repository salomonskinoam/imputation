"""The bank-impute-cat-single task (Bank Cat·Single·No re-realization)."""
from sdk import repo_root
from tasks_def.configs import bank_cat_single as config
from worlds.imputation.world import ImputationWorld

BANK_CAT_SINGLE_TASK = ImputationWorld(
    name="bank-impute-cat-single",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "bank-impute-cat-single",
)
