"""Display utility functions for console formatting."""

from typing import List

from ..domain.task import Task


def truncate(text: str, width: int) -> str:
    """Truncate text to width characters, adding '...' if truncated."""
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


def format_task_table(tasks: List[Task]) -> str:
    """Format tasks as a pretty table with columns."""
    if not tasks:
        return ""

    # Column widths
    id_width = 8
    title_width = 50
    priority_width = 8
    status_width = 10
    due_date_width = 12

    # Header
    lines = []
    header = (
        f"{'ID':<{id_width}} | "
        f"{'Title':<{title_width}} | "
        f"{'Priority':<{priority_width}} | "
        f"{'Status':<{status_width}} | "
        f"{'Due Date':<{due_date_width}}"
    )
    lines.append(header)

    # Separator
    sep_length = (
        id_width
        + title_width
        + priority_width
        + status_width
        + due_date_width
        + 12  # separators
    )
    lines.append("-" * sep_length)

    # Rows
    for task in tasks:
        task_id = task.id[:8]
        title = truncate(task.title, title_width)
        priority = task.priority.value
        status = task.status.value
        due_date = task.due_date if task.due_date else "-"

        # Add overdue indicator
        if task.is_overdue:
            due_date = f"{due_date} ⚠️"

        row = (
            f"{task_id:<{id_width}} | "
            f"{title:<{title_width}} | "
            f"{priority:<{priority_width}} | "
            f"{status:<{status_width}} | "
            f"{due_date:<{due_date_width}}"
        )
        lines.append(row)

    return "\n".join(lines)
