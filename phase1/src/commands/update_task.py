"""Update task command."""

from ..domain.enums import Priority
from ..services.task_service import TaskService
from ..utils.datetime_utils import is_valid_iso_date


def update_task_command(service: TaskService) -> None:
    """Prompt user to update a task."""
    print("\n--- Update Task ---")

    # Get task ID
    while True:
        task_id = input("Enter task ID to update (or 'quit' to cancel): ").strip()

        if task_id.lower() == "quit":
            print("Operation cancelled.")
            return

        # Check if task exists (support partial ID like first 8 chars)
        task = service.get_task_by_partial_id(task_id)
        if task is not None:
            break

        print(f"✗ Error: Task not found (ID: {task_id})")

    # Display current task
    print("\nCurrent task:")
    print(f"  Title: {task.title}")
    print(f"  Description: {task.description}")
    print(f"  Due Date: {task.due_date or '-'}")
    print(f"  Priority: {task.priority.value}")

    # Get field to update
    print("\nFields to update:")
    print("  1. Title")
    print("  2. Description")
    print("  3. Due Date")
    print("  4. Priority")

    while True:
        field_choice = input("\nSelect field to update (1-4): ").strip()

        if field_choice == "1":
            field = "title"
            break
        elif field_choice == "2":
            field = "description"
            break
        elif field_choice == "3":
            field = "due_date"
            break
        elif field_choice == "4":
            field = "priority"
            break
        else:
            print("✗ Error: Please enter 1, 2, 3, or 4")
            continue

    # Get new value based on field
    new_title: str | None = None
    new_description: str | None = None
    new_due_date: str | None = None
    new_priority: Priority | None = None

    if field == "title":
        while True:
            new_title = input("Enter new title: ").strip()
            if new_title:
                break
            print("✗ Error: Title cannot be empty")

    elif field == "description":
        new_description = input(
            "Enter new description (or press Enter for empty): "
        ).strip()

    elif field == "due_date":
        while True:
            new_value_input = input(
                "Enter new due date in YYYY-MM-DD format (or press Enter to remove): "
            ).strip()

            if not new_value_input:
                new_due_date = None
                break

            if not is_valid_iso_date(new_value_input):
                print("✗ Error: Date must be in ISO format YYYY-MM-DD")
                continue

            new_due_date = new_value_input
            break

    elif field == "priority":
        while True:
            priority_input = input("Enter new priority (low/medium/high): ").strip()

            try:
                new_priority = Priority.from_string(priority_input)
                break
            except ValueError:
                print("✗ Error: Priority must be 'low', 'medium', or 'high'")
                continue

    # Update task (use full task ID from object)
    success, message, updated_task = service.update_task(
        task_id=task.id,
        title=new_title,
        description=new_description,
        due_date=new_due_date,
        priority=new_priority,
    )

    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ Error: {message}")
