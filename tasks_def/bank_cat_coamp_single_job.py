"""The bank-impute-cat-coamp-single-job task (Cat·Single·Yes salvage hedge)."""
from sdk import repo_root
from tasks_def.configs import bank_cat_coamp_single_job as config
from worlds.imputation.world import ImputationWorld

BANK_CAT_COAMP_SINGLE_JOB_TASK = ImputationWorld(
    name="bank-impute-cat-coamp-single-job",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "bank-impute-cat-coamp-single-job",
)
