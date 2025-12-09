"""List tasks command."""

from ..domain.enums import Priority, Status
from ..services.task_service import TaskService
from ..utils.display_utils import format_task_table


def list_tasks_command(service: TaskService) -> None:
    """Display tasks with optional filtering and sorting."""
    print("\n--- List Tasks ---")

    # Get filter status
    filter_status: Status | None = None
    while True:
        status_input = input(
            "Filter by status (pending/completed/all, default: all): "
        ).strip()

        if not status_input or status_input.lower() == "all":
            break

        try:
            filter_status = Status.from_string(status_input)
            break
        except ValueError:
            print("✗ Error: Status must be 'pending', 'completed', or 'all'")
            continue

    # Get filter priority
    filter_priority: Priority | None = None
    while True:
        priority_input = input(
            "Filter by priority (low/medium/high/all, default: all): "
        ).strip()

        if not priority_input or priority_input.lower() == "all":
            break

        try:
            filter_priority = Priority.from_string(priority_input)
            break
        except ValueError:
            print("✗ Error: Priority must be 'low', 'medium', 'high', or 'all'")
            continue

    # Get filter overdue
    filter_overdue = False
    while True:
        overdue_input = input(
            "Show only overdue tasks? (yes/no, default: no): "
        ).strip()

        if not overdue_input or overdue_input.lower() == "no":
            break

        if overdue_input.lower() == "yes":
            filter_overdue = True
            break

        print("✗ Error: Please enter 'yes' or 'no'")
        continue

    # Get sort option
    sort_by: str | None = None
    while True:
        sort_input = input(
            "Sort by (priority/due_date/status/none, default: none): "
        ).strip()

        if not sort_input or sort_input.lower() == "none":
            break

        if sort_input.lower() in ["priority", "due_date", "status"]:
            sort_by = sort_input.lower()
            break

        print("✗ Error: Sort must be 'priority', 'due_date', 'status', or 'none'")
        continue

    # Get and display tasks
    tasks = service.list_tasks(
        filter_status=filter_status,
        filter_priority=filter_priority,
        filter_overdue=filter_overdue,
        sort_by=sort_by,
    )

    if not tasks:
        print("\nNo tasks found")
    else:
        print("\n")
        table = format_task_table(tasks)
        print(table)
        print(f"\nTotal: {len(tasks)} task(s)")
