"""Grader entry point the MCP server imports (delegates to BANK_CAT_SINGLE_TASK.grade())."""
from tasks_def.bank_cat_single import BANK_CAT_SINGLE_TASK


def grade(transcript: str = ""):
    return BANK_CAT_SINGLE_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
