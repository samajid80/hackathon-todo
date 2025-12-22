"""
OpenAI Agents SDK integration for Phase 3 Backend.

Handles AI-powered natural language understanding with automatic tool calling.
"""

from agents import Agent, Runner, function_tool, RunResult
from typing import List, Dict, Any, Optional, Annotated
import asyncio
import os
from openai import APIError, RateLimitError, APIConnectionError

from app.config import settings

# Set OpenAI API key in environment for Agents SDK
# The Agents SDK reads from os.environ, not from pydantic settings
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0
):
    """
    Decorator to retry async functions with exponential backoff.

    Handles OpenAI API errors with progressive delay between retries.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        exponential_base: Base for exponential calculation (default: 2.0)
        max_delay: Maximum delay between retries (default: 60.0)

    Retries on:
        - RateLimitError: OpenAI API rate limit exceeded
        - APIConnectionError: Network/connection issues
        - APIError: General OpenAI API errors
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except RateLimitError as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"Rate limit hit. Retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        delay = min(delay * exponential_base, max_delay)
                    else:
                        raise ValueError(
                            "OpenAI API rate limit exceeded. Please try again in a few moments."
                        ) from e

                except APIConnectionError as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"Connection error. Retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        delay = min(delay * exponential_base, max_delay)
                    else:
                        raise ValueError(
                            "Unable to connect to OpenAI API. Please check your connection and try again."
                        ) from e

                except APIError as e:
                    last_exception = e
                    # Only retry on server errors (5xx), not client errors (4xx)
                    if hasattr(e, 'status_code') and 500 <= e.status_code < 600:
                        if attempt < max_retries:
                            print(f"API error {e.status_code}. Retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(delay)
                            delay = min(delay * exponential_base, max_delay)
                        else:
                            raise ValueError(
                                "OpenAI API is experiencing issues. Please try again later."
                            ) from e
                    else:
                        # Don't retry client errors
                        raise ValueError(f"OpenAI API error: {str(e)}") from e

            # Should never reach here, but just in case
            raise last_exception

        return wrapper
    return decorator


# System prompt for todo assistant (T030)
SYSTEM_PROMPT = """You are a helpful AI assistant for managing todo lists.

Your capabilities:
- Add new tasks
- List existing tasks
- Mark tasks as complete
- Update task details (title, description)
- Delete tasks

CRITICAL - Task ID Requirements:
- Task IDs are UUIDs (e.g., "550e8400-e29b-41d4-a716-446655440000"), NOT integers
- When users reference a task by title/description, you MUST:
  1. First call list_tasks() to get all tasks
  2. Find the matching task in the results
  3. Extract the UUID from the "id" field
  4. Use that UUID for complete_task, update_task, or delete_task
- NEVER guess or make up task IDs
- NEVER use integers like "1" or "2" as task IDs

Workflow for task operations by title:
User: "Complete the groceries task"
You:
1. Call list_tasks()
2. Search results for task with title containing "groceries"
3. Extract the UUID (e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
4. Call complete_task(task_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890", completed=true)

Guidelines:
- Be conversational and friendly
- Confirm actions clearly with specific task details
- Ask for clarification when commands are ambiguous
- Stay focused on todo management
- Always include task titles in your responses
- When listing tasks, format them clearly with their IDs
- If multiple tasks match, ask which one the user means

When users give vague commands, ask specific questions.
Always confirm successful operations with the task details.

If a user's request is unclear or could apply to multiple tasks, ask which specific task they mean before taking action.

CRITICAL - Delete Confirmation Workflow:
1. If user says "delete [task]" WITHOUT explicit confirmation (e.g., "yes", "confirm", "delete it"):
   - First list the task to identify the UUID
   - Ask ONCE: "Are you sure you want to delete '[task title]'?"
   - Wait for user response
2. If user confirms (says "yes", "confirm", "delete it", "sure", or similar):
   - IMMEDIATELY call delete_task(task_id="...")
   - Do NOT ask for confirmation again
   - Confirm the deletion was successful
3. If user already said "yes delete it" or "confirm deletion" in their message:
   - Skip asking for confirmation
   - Directly call delete_task(task_id="...")

NEVER ask for confirmation more than once. After user confirms, DELETE immediately.
"""


def create_agent_tools(mcp_client: Any, user_id: str, jwt_token: Optional[str] = None):
    """
    Create function tools that are bound to a specific user and MCP client.

    This factory pattern allows tools to call the MCP server while maintaining
    user context via closure.

    Args:
        mcp_client: MCP client for executing tool operations
        user_id: User identifier to bind to all tool calls
        jwt_token: Optional JWT token for authenticated MCP requests

    Returns:
        List of function_tool decorated async functions
    """

    @function_tool
    async def add_task(
        title: Annotated[str, "Task title (required, 1-200 characters)"],
        description: Annotated[str, "Task description (optional, 0-2000 characters)"] = "",
        due_date: Annotated[Optional[str], "Due date in ISO 8601 format YYYY-MM-DD (e.g., '2025-12-26')"] = None,
        priority: Annotated[Optional[str], "Priority level: 'low', 'medium', or 'high' (default: 'medium')"] = None
    ) -> str:
        """Create a new todo task with title, description, due date, and priority."""
        params = {"user_id": user_id, "title": title, "description": description}
        if due_date is not None:
            params["due_date"] = due_date
        if priority is not None:
            params["priority"] = priority

        result = await mcp_client.invoke_tool(
            "add_task",
            params,
            jwt_token
        )
        return str(result)

    @function_tool
    async def list_tasks(
        completed: Annotated[Optional[bool], "Filter by completion status (true=completed, false=incomplete, omit=all)"] = None
    ) -> str:
        """List user's tasks, optionally filtered by completion status."""
        params = {"user_id": user_id}
        if completed is not None:
            params["completed"] = completed
        result = await mcp_client.invoke_tool("list_tasks", params, jwt_token)
        return str(result)

    @function_tool
    async def complete_task(
        task_id: Annotated[str, "Task identifier (UUID)"],
        completed: Annotated[bool, "Completion status (true = complete, false = incomplete)"]
    ) -> str:
        """Mark a task as complete or incomplete."""
        result = await mcp_client.invoke_tool(
            "complete_task",
            {"user_id": user_id, "task_id": task_id, "completed": completed},
            jwt_token
        )
        return str(result)

    @function_tool
    async def update_task(
        task_id: Annotated[str, "Task identifier (UUID)"],
        title: Annotated[Optional[str], "New task title (optional, 1-200 characters)"] = None,
        description: Annotated[Optional[str], "New task description (optional, 0-2000 characters)"] = None,
        due_date: Annotated[Optional[str], "New due date in ISO 8601 format YYYY-MM-DD (e.g., '2025-12-26')"] = None,
        priority: Annotated[Optional[str], "New priority level: 'low', 'medium', or 'high'"] = None
    ) -> str:
        """Update task fields including title, description, due date, and priority."""
        params = {"user_id": user_id, "task_id": task_id}
        if title is not None:
            params["title"] = title
        if description is not None:
            params["description"] = description
        if due_date is not None:
            params["due_date"] = due_date
        if priority is not None:
            params["priority"] = priority
        result = await mcp_client.invoke_tool("update_task", params, jwt_token)
        return str(result)

    @function_tool
    async def delete_task(
        task_id: Annotated[str, "Task identifier (UUID)"]
    ) -> str:
        """Permanently delete a task (use with confirmation)."""
        result = await mcp_client.invoke_tool(
            "delete_task",
            {"user_id": user_id, "task_id": task_id},
            jwt_token
        )
        return str(result)

    return [add_task, list_tasks, complete_task, update_task, delete_task]


class InMemorySessionFromMessages:
    """
    Custom Session implementation that initializes from existing message history.

    This allows us to use the Agents SDK while maintaining our existing
    database-backed conversation storage in PostgreSQL.
    """

    def __init__(self, messages: List[Dict[str, str]]):
        """
        Initialize session with existing messages.

        Args:
            messages: List of {"role": "user|assistant", "content": "..."} dicts
        """
        # Convert to Session item format (exclude last message as it's passed as input)
        self.items = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages[:-1]
        ] if len(messages) > 1 else []

    async def get_items(self, limit: int | None = None) -> List[dict]:
        """Retrieve conversation history for the session."""
        if limit is None:
            return self.items
        return self.items[-limit:]

    async def add_items(self, items: List[dict]) -> None:
        """Store new items for the session (in-memory only)."""
        self.items.extend(items)

    async def pop_item(self) -> dict | None:
        """Remove and return the most recent item."""
        return self.items.pop() if self.items else None

    async def clear_session(self) -> None:
        """Clear all items (no-op for our use case)."""
        self.items = []


def extract_tool_calls_from_result(result: RunResult) -> List[Dict[str, Any]]:
    """
    Extract tool calls log from RunResult for debugging/transparency.

    Args:
        result: RunResult from Runner.run()

    Returns:
        List of tool call records with tool name, parameters, and results
    """
    from agents import ToolCallItem, ToolCallOutputItem

    tool_calls_log = []
    tool_call_map = {}

    # Iterate through all items in the run result
    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            try:
                # Found a tool call - extract data from raw attribute
                raw_item = item.raw

                # Get tool call ID
                call_id = getattr(raw_item, 'id', None)
                if not call_id:
                    continue  # Skip if no ID found

                # Extract tool name (could be in function.name or name)
                tool_name = 'unknown'
                if hasattr(raw_item, 'function') and hasattr(raw_item.function, 'name'):
                    tool_name = raw_item.function.name
                elif hasattr(raw_item, 'name'):
                    tool_name = raw_item.name

                # Extract arguments (could be in function.arguments or arguments)
                arguments = {}
                if hasattr(raw_item, 'function') and hasattr(raw_item.function, 'arguments'):
                    arguments = raw_item.function.arguments
                elif hasattr(raw_item, 'arguments'):
                    arguments = raw_item.arguments

                tool_call_map[call_id] = {
                    "tool": tool_name,
                    "parameters": arguments,
                    "call_id": call_id
                }
            except (AttributeError, Exception) as e:
                # Silently skip tool calls we can't parse
                print(f"[Debug] Skipping unparseable tool call: {e}")
                continue

        elif isinstance(item, ToolCallOutputItem):
            try:
                # Found tool output - match it to the tool call
                if hasattr(item, 'tool_call_id') and item.tool_call_id in tool_call_map:
                    call_record = tool_call_map[item.tool_call_id]
                    call_record["result"] = getattr(item, 'output', 'No output')
                    tool_calls_log.append(call_record)
            except (AttributeError, Exception) as e:
                # Silently skip outputs we can't parse
                print(f"[Debug] Skipping unparseable tool output: {e}")
                continue

    # Clean up call_id from final log (internal detail)
    for record in tool_calls_log:
        record.pop("call_id", None)

    return tool_calls_log


@retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
async def run_agent(
    messages: List[Dict[str, str]],
    user_id: str,
    mcp_client: Any,
    jwt_token: Optional[str] = None
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Run OpenAI agent with conversation history and MCP tool support.

    Includes automatic retry with exponential backoff for OpenAI API errors.

    Args:
        messages: Conversation history [{"role": "user|assistant", "content": "..."}]
        user_id: User identifier for tool calls
        mcp_client: MCP client for executing tools
        jwt_token: JWT token for authenticated MCP tool calls

    Returns:
        Tuple of (assistant_response, tool_calls_log)

    Raises:
        ValueError: User-friendly error message after retries exhausted
    """
    # Create tools bound to this user and MCP client
    tools = create_agent_tools(mcp_client, user_id, jwt_token)

    # Create agent with tools
    # Use gpt-4o-mini for fast, cost-effective responses (10x faster than gpt-4-turbo-preview)
    agent = Agent(
        name="Todo Assistant",
        instructions=SYSTEM_PROMPT,
        model="gpt-4o-mini",  # Fast model: ~500ms vs ~5-7s for gpt-4-turbo-preview
        tools=tools
    )

    # Convert message history to Session-compatible format
    session = InMemorySessionFromMessages(messages)

    # Get latest user message (last message in list)
    latest_user_message = messages[-1]["content"] if messages else ""

    # Run agent with conversation context
    result: RunResult = await Runner.run(
        agent,
        input=latest_user_message,
        session=session
    )

    # Extract tool calls log from RunResult
    tool_calls_log = extract_tool_calls_from_result(result)

    # Return final output and tool calls
    return result.final_output, tool_calls_log
