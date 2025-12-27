"""
ChatKitServer implementation for Phase 3 backend using real ChatKit API.

Extends chatkit.server.ChatKitServer to provide todo-specific functionality.
Integrates MCP tools, conversation persistence, and OpenAI Agents SDK streaming.
"""

from typing import AsyncIterator
import os

# Real ChatKit API imports
from chatkit.server import ChatKitServer as BaseChatKitServer
from chatkit.types import ThreadMetadata, UserMessageItem, AssistantMessageItem, ThreadStreamEvent
from chatkit.agents import AgentContext, stream_agent_response, simple_to_agent_input

# OpenAI Agents SDK
from agents import Agent, function_tool, Runner

# Our imports
from app.chatkit.postgresql_store import PostgreSQLStore, UserContext
from app.agents.mcp_client import MCPClient
from app.config import settings


class TodoChatKitServer(BaseChatKitServer[UserContext]):
    """
    ChatKit server for todo management chatbot.

    Provides:
    - Session-based conversation persistence via PostgreSQL
    - MCP tool integration (add_task, list_tasks, etc.)
    - OpenAI Agents SDK streaming
    - User isolation via UserContext
    """

    def __init__(self, store: PostgreSQLStore):
        """Initialize ChatKit server with PostgreSQL store."""
        super().__init__(store=store)
        self.mcp_client = MCPClient()

    def _create_agent(self, context: UserContext) -> Agent:
        """
        Create an OpenAI Agent with MCP tools bound.

        Args:
            context: UserContext containing user_id and jwt_token for tool calls

        Returns:
            Configured Agent instance with todo management tools
        """
        user_id = context.user_id
        jwt_token = context.jwt_token

        # Define tools as function_tool wrappers around MCP client
        @function_tool
        async def add_task(
            title: str,
            description: str = "",
            due_date: str | None = None,
            priority: str | None = None,
            tags: list[str] | None = None
        ) -> dict:
            """
            Create a new task with a title and optional details.

            Args:
                title: Task title (required)
                description: Task description (optional)
                due_date: Due date in YYYY-MM-DD format (optional)
                priority: Priority level: "low", "medium", or "high" (optional)
                tags: List of tags (optional)
            """
            return await self.mcp_client.add_task(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                tags=tags,
                jwt_token=jwt_token
            )

        @function_tool
        async def list_tasks(completed: bool | None = None) -> dict:
            """List all tasks, optionally filtered by completion status."""
            return await self.mcp_client.list_tasks(
                user_id=user_id,
                completed=completed,
                jwt_token=jwt_token
            )

        @function_tool
        async def complete_task(task_id: str, completed: bool) -> dict:
            """Mark a task as completed or incomplete."""
            return await self.mcp_client.complete_task(
                user_id=user_id,
                task_id=task_id,
                completed=completed,
                jwt_token=jwt_token
            )

        @function_tool
        async def update_task(
            task_id: str,
            title: str | None = None,
            description: str | None = None,
            due_date: str | None = None,
            priority: str | None = None,
            tags: list[str] | None = None
        ) -> dict:
            """
            Update a task's details.

            Args:
                task_id: Task identifier (required)
                title: New task title (optional)
                description: New task description (optional)
                due_date: New due date in YYYY-MM-DD format (optional)
                priority: New priority level: "low", "medium", or "high" (optional)
                tags: New list of tags (optional, replaces existing tags)
            """
            return await self.mcp_client.update_task(
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                tags=tags,
                jwt_token=jwt_token
            )

        @function_tool
        async def delete_task(task_id: str) -> dict:
            """Permanently delete a task."""
            return await self.mcp_client.delete_task(
                user_id=user_id,
                task_id=task_id,
                jwt_token=jwt_token
            )

        # Create agent with tools
        agent = Agent(
            name="TodoAssistant",
            model="gpt-4o-mini",
            instructions="""You are a helpful todo management assistant.
            You help users manage their tasks through natural language.

            IMPORTANT DATE HANDLING:
            - When users provide dates in formats like "31/12/2025", "Dec 31 2025", or "31st December 2025",
              you MUST convert them to YYYY-MM-DD format (e.g., "2025-12-31") before calling the tools.
            - Always validate the date format before making tool calls.
            - For partial dates like "tomorrow" or "next Monday", calculate the exact date and use YYYY-MM-DD format.

            PRIORITY HANDLING:
            - Valid priority values are: "low", "medium", or "high" (lowercase).
            - If user says "urgent" or "important", use "high" priority.

            TAGS HANDLING:
            - Tags should be lowercase, alphanumeric with hyphens allowed.
            - Convert user input like "Home" to ["home"], or "Work Items" to ["work-items"].

            UPDATING TASKS:
            - When user wants to update a task by title (e.g., "update task titled 'Buy Watch'"):
              1. First call list_tasks() to get all tasks
              2. Find the task with matching title in the results
              3. Extract the task's "id" field from the result
              4. Call update_task(task_id=<id>, due_date=<converted_date>) with the proper task_id
            - The task_id is required for update_task - you cannot update by title directly.
            - Always provide at least one field to update (title, description, due_date, priority, or tags).

            DELETING TASKS (IMPORTANT - ALWAYS CONFIRM):
            - When user asks to delete a task, NEVER delete it immediately.
            - Instead, follow these steps:
              1. First call list_tasks() to find the task
              2. Show the task details (title, description, due date, etc.)
              3. Ask the user: "Are you sure you want to delete this task? Type 'yes' to confirm or 'no' to cancel."
              4. Wait for the user's response
              5. ONLY call delete_task() if the user explicitly confirms with "yes", "confirm", "delete it", or similar affirmative response
              6. If user says "no", "cancel", or anything else, do NOT delete and say "Deletion cancelled."
            - This confirmation step is MANDATORY for all delete operations to prevent accidental data loss.

            When users ask to create, list, update, complete, or delete tasks, use the appropriate tools.
            Be conversational and helpful. Always confirm what you did after completing an action.""",
            tools=[add_task, list_tasks, complete_task, update_task, delete_task],
        )

        return agent

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: UserContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Stream ThreadStreamEvent instances for a new user message.

        Args:
            thread: Metadata for the thread being processed
            input_user_message: The incoming message to respond to
            context: UserContext with user_id

        Yields:
            ThreadStreamEvent instances as the agent processes the message
        """
        if not input_user_message:
            # No message to process
            return

        # Create agent with user's context
        agent = self._create_agent(context)

        # Create AgentContext for streaming
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Load conversation history from store
        history_items = []
        try:
            # Load existing messages from the thread
            page = await self.store.load_thread_items(
                thread_id=thread.id,
                after=None,
                limit=100,  # Load last 100 messages for context
                order="asc",  # Chronological order
                context=context,
            )
            history_items = page.data
        except Exception:
            # If thread doesn't exist yet, that's fine - empty history
            pass

        # Convert all thread items (history + new message) to agent input
        messages = []

        # Add conversation history
        for item in history_items:
            if isinstance(item, UserMessageItem):
                # Extract text from content
                text = ""
                if item.content:
                    for part in item.content:
                        if hasattr(part, 'text'):
                            text = part.text
                            break
                        elif isinstance(part, dict) and part.get('text'):
                            text = part['text']
                            break
                if text:
                    # Format matching simple_to_agent_input output
                    messages.append({
                        'role': 'user',
                        'type': 'message',
                        'content': [{'type': 'input_text', 'text': text}]
                    })
            elif isinstance(item, AssistantMessageItem):
                # Extract text from content
                text = ""
                if item.content:
                    for part in item.content:
                        if hasattr(part, 'text'):
                            text = part.text
                            break
                        elif isinstance(part, dict) and part.get('text'):
                            text = part['text']
                            break
                if text:
                    # Assistant message format
                    messages.append({
                        'role': 'assistant',
                        'type': 'message',
                        'content': [{'type': 'output_text', 'text': text}]
                    })

        # Add new user message
        if input_user_message:
            new_msg = await simple_to_agent_input(input_user_message)
            messages.extend(new_msg)

        # Run agent with full conversation history
        result = Runner.run_streamed(
            agent,
            messages,
            context=agent_context,
        )

        # Convert agent response stream to ChatKit ThreadStreamEvents
        async for event in stream_agent_response(agent_context, result):
            yield event
