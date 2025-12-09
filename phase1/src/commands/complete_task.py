"""Complete task command."""

from ..services.task_service import TaskService


def complete_task_command(service: TaskService) -> None:
    """Mark a task as completed."""
    print("\n--- Complete Task ---")

    # Get task ID
    while True:
        task_id = input(
            "Enter task ID to mark as complete (or 'quit' to cancel): "
        ).strip()

        if task_id.lower() == "quit":
            print("Operation cancelled.")
            return

        # Check if task exists (support partial ID like first 8 chars)
        task = service.get_task_by_partial_id(task_id)
        if task is not None:
            break

        print(f"✗ Error: Task not found (ID: {task_id})")

    # Mark as completed (use full task ID from object)
    success, message, _ = service.complete_task(task.id)

    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ Error: {message}")
