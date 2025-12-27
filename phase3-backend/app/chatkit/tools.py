"""
ChatKit tool definitions that wrap MCP client calls.

Provides OpenAI function calling tool definitions for task management operations.
Each tool invokes the corresponding MCP client method.
"""

from typing import Dict, Any, Optional


# Tool definitions for OpenAI function calling
# These will be bound to ChatKitServer in T020

def get_add_task_tool() -> Dict[str, Any]:
    """
    Tool definition for adding a new task.

    Returns:
        OpenAI function calling tool schema
    """
    return {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user with a title and optional description",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task (1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    }
                },
                "required": ["title"]
            }
        }
    }


def get_list_tasks_tool() -> Dict[str, Any]:
    """
    Tool definition for listing user's tasks.

    Returns:
        OpenAI function calling tool schema
    """
    return {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user, optionally filtered by completion status",
            "parameters": {
                "type": "object",
                "properties": {
                    "completed": {
                        "type": "boolean",
                        "description": "Filter by completion status (true=completed, false=pending, omit=all)"
                    }
                },
                "required": []
            }
        }
    }


def get_complete_task_tool() -> Dict[str, Any]:
    """
    Tool definition for marking a task as complete/incomplete.

    Returns:
        OpenAI function calling tool schema
    """
    return {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed or incomplete",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to update"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "True to mark complete, false to mark incomplete"
                    }
                },
                "required": ["task_id", "completed"]
            }
        }
    }


def get_update_task_tool() -> Dict[str, Any]:
    """
    Tool definition for updating task details.

    Returns:
        OpenAI function calling tool schema
    """
    return {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title and/or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task (optional)"
                    }
                },
                "required": ["task_id"]
            }
        }
    }


def get_delete_task_tool() -> Dict[str, Any]:
    """
    Tool definition for deleting a task.

    Returns:
        OpenAI function calling tool schema
    """
    return {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The UUID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    }


def get_all_tools() -> list[Dict[str, Any]]:
    """
    Get all ChatKit tool definitions.

    Returns:
        List of all tool schemas for OpenAI function calling
    """
    return [
        get_add_task_tool(),
        get_list_tasks_tool(),
        get_complete_task_tool(),
        get_update_task_tool(),
        get_delete_task_tool()
    ]
