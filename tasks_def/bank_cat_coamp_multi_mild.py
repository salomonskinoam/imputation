"""The bank-impute-cat-coamp-multi-mild task (Bank Cat·Multi·Yes re-realization)."""
from sdk import repo_root
from tasks_def.configs import bank_cat_coamp_multi_mild as config
from worlds.imputation.world import ImputationWorld

BANK_CAT_COAMP_MULTI_MILD_TASK = ImputationWorld(
    name="bank-impute-cat-coamp-multi-mild",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "bank-impute-cat-coamp-multi-mild",
)
