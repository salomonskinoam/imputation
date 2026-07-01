"""Grader entry point the MCP server imports (delegates to COVERTYPE_DIRECT_TASK.grade())."""
from tasks_def.covertype_direct import COVERTYPE_DIRECT_TASK


def grade(transcript: str = ""):
    return COVERTYPE_DIRECT_TASK.grade(transcript)


if __name__ == "__main__":
    print(grade().model_dump())
