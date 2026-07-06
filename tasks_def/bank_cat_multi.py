"""The bank-impute-cat-multi task (grid: Bank · Categorical · Multi · No-coamp)."""
from sdk import repo_root
from tasks_def.configs import bank_cat_multi as config
from worlds.imputation.world import ImputationWorld

BANK_CAT_MULTI_TASK = ImputationWorld(
    name="bank-impute-cat-multi",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "bank-impute-cat-multi",
)
