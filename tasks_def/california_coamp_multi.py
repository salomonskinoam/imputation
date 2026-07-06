"""The california-impute-coamp-multi task (grid slot 4 on California: Numeric·Multi·CoAmp)."""
from sdk import repo_root
from tasks_def.configs import california_coamp_multi as config
from worlds.imputation.world import ImputationWorld

CALIFORNIA_COAMP_MULTI_TASK = ImputationWorld(
    name="california-impute-coamp-multi",
    config=config.CONFIG,
    source_dir=repo_root() / "tasks" / "california-impute-coamp-multi",
)
