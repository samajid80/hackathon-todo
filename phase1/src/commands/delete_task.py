"""Delete task command."""

from ..services.task_service import TaskService


def delete_task_command(service: TaskService) -> None:
    """Delete a task with confirmation."""
    print("\n--- Delete Task ---")

    # Get task ID
    while True:
        task_id = input("Enter task ID to delete (or 'quit' to cancel): ").strip()

        if task_id.lower() == "quit":
            print("Operation cancelled.")
            return

        # Check if task exists (support partial ID like first 8 chars)
        task = service.get_task_by_partial_id(task_id)
        if task is not None:
            break

        print(f"✗ Error: Task not found (ID: {task_id})")

    # Confirm deletion
    print(f"\nTask: {task.title}")
    while True:
        confirm = input("Are you sure you want to delete this task? (yes/no): ").strip()

        if confirm.lower() in ["yes", "y"]:
            success, message, _ = service.delete_task(task.id)
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ Error: {message}")
            return

        elif confirm.lower() in ["no", "n"]:
            print("Deletion cancelled")
            return

        else:
            print("✗ Error: Please enter 'yes' or 'no'")
            continue
