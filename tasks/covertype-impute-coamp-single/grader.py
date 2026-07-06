"""Grader entry point the MCP server imports (delegates to COVERTYPE_COAMP_SINGLE_TASK.grade())."""
from tasks_def.covertype_coamp_single import COVERTYPE_COAMP_SINGLE_TASK


def grade(transcript: str = ""):
    return COVERTYPE_COAMP_SINGLE_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
