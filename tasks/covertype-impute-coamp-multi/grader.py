"""Grader entry point the MCP server imports (delegates to COVERTYPE_COAMP_MULTI_TASK.grade())."""
from tasks_def.covertype_coamp_multi import COVERTYPE_COAMP_MULTI_TASK


def grade(transcript: str = ""):
    return COVERTYPE_COAMP_MULTI_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
