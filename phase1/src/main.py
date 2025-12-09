"""Main entry point for the todo application."""

from .storage.repository import InMemoryTaskRepository
from .services.task_service import TaskService
from .commands.add_task import add_task_command
from .commands.list_tasks import list_tasks_command
from .commands.update_task import update_task_command
from .commands.complete_task import complete_task_command
from .commands.delete_task import delete_task_command


def main() -> None:
    """Main application loop."""
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    print("\n" + "=" * 40)
    print("   === Todo Application ===")
    print("=" * 40)

    while True:
        print("\n1. Add Task")
        print("2. List Tasks")
        print("3. Update Task")
        print("4. Complete Task")
        print("5. Delete Task")
        print("6. Exit")

        while True:
            option = input("\nSelect option (1-6): ").strip()

            if option in ["1", "2", "3", "4", "5", "6"]:
                break

            print(" Invalid option. Please enter a number between 1 and 6")

        try:
            if option == "1":
                add_task_command(service)
            elif option == "2":
                list_tasks_command(service)
            elif option == "3":
                update_task_command(service)
            elif option == "4":
                complete_task_command(service)
            elif option == "5":
                delete_task_command(service)
            elif option == "6":
                print("\nGoodbye!")
                break
        except Exception as e:
            print(f" An unexpected error occurred: {str(e)}")
            print("Returning to menu...")


if __name__ == "__main__":
    main()
