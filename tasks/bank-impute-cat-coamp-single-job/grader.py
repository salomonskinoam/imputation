"""Grader entry point the MCP server imports (delegates to BANK_CAT_COAMP_SINGLE_JOB_TASK.grade())."""
from tasks_def.bank_cat_coamp_single_job import BANK_CAT_COAMP_SINGLE_JOB_TASK


def grade(transcript: str = ""):
    return BANK_CAT_COAMP_SINGLE_JOB_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
