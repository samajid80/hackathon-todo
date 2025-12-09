"""Add task command."""

from ..domain.enums import Priority
from ..services.task_service import TaskService
from ..utils.datetime_utils import is_valid_iso_date


def add_task_command(service: TaskService) -> None:
    """Prompt user to create a new task."""
    print("\n--- Add Task ---")

    # Get title with validation
    while True:
        title = input("Enter task title (or 'quit' to cancel): ").strip()
        if title.lower() == "quit":
            print("Operation cancelled.")
            return

        if not title:
            print("✗ Error: Title is required")
            continue

        if len(title) > 200:
            print("✗ Error: Title must be 200 characters or less")
            continue

        break

    # Get description (optional)
    description = input(
        "Enter task description (optional, press Enter to skip): "
    ).strip()

    # Get due date (optional)
    due_date: str | None = None
    while True:
        due_date_input = input(
            "Enter due date in YYYY-MM-DD format (optional, press Enter to skip): "
        ).strip()

        if not due_date_input:
            break

        if not is_valid_iso_date(due_date_input):
            print("✗ Error: Date must be in ISO format YYYY-MM-DD")
            continue

        due_date = due_date_input
        break

    # Get priority (optional)
    while True:
        priority_input = input(
            "Enter priority (low/medium/high, default: medium, or press Enter): "
        ).strip()

        if not priority_input:
            priority = Priority.MEDIUM
            break

        try:
            priority = Priority.from_string(priority_input)
            break
        except ValueError:
            print("✗ Error: Priority must be 'low', 'medium', or 'high'")
            continue

    # Create task
    success, message, task = service.create_task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
    )

    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ Error: {message}")
