"""Grader entry point the MCP server imports (delegates to BANK_CAT_COAMP_MULTI_MILD_TASK.grade())."""
from tasks_def.bank_cat_coamp_multi_mild import BANK_CAT_COAMP_MULTI_MILD_TASK


def grade(transcript: str = ""):
    return BANK_CAT_COAMP_MULTI_MILD_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
