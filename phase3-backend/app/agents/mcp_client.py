"""
HTTP client for invoking MCP tools on Phase 3 MCP Server.

Used by OpenAI agent to execute tool calls via MCP server.
"""

import httpx
from typing import Dict, Any, Optional

from app.config import settings


class MCPClient:
    """
    Async HTTP client for Phase 3 MCP Server.

    Provides methods to invoke MCP tools remotely via HTTP.
    The agent uses this client to execute tool calls returned by OpenAI.
    """

    def __init__(self):
        """Initialize with MCP server URL from settings."""
        self.base_url = settings.mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)  # Longer timeout for tool execution

    async def invoke_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke an MCP tool on the MCP server.

        Args:
            tool_name: Name of the tool to invoke (e.g., 'add_task', 'list_tasks')
            parameters: Tool parameters (must include user_id)
            jwt_token: Optional JWT token for authenticated requests

        Returns:
            Tool execution result from MCP server

        Raises:
            ValueError: If tool execution fails (provides LLM-friendly error messages)
        """
        url = f"{self.base_url}/mcp"
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        payload = {
            "tool": tool_name,
            "parameters": parameters
        }

        try:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # Parse MCP response
            mcp_response = response.json()

            # Check for MCP-level errors
            if not mcp_response.get("success", True):
                error_msg = mcp_response.get("error", "Unknown MCP error")
                raise ValueError(f"MCP tool '{tool_name}' failed: {error_msg}")

            # Return the tool result
            return mcp_response.get("result", {})

        except httpx.HTTPStatusError as e:
            # HTTP error - provide structured error for LLM
            raise ValueError(
                f"Tool '{tool_name}' failed with HTTP {e.response.status_code}: "
                f"{e.response.text if e.response.text else 'No error details'}"
            )
        except httpx.RequestError as e:
            # Network/connection error
            raise ValueError(
                f"Tool '{tool_name}' failed due to connection error: {str(e)}"
            )
        except Exception as e:
            # Unexpected error
            raise ValueError(
                f"Tool '{tool_name}' failed unexpectedly: {str(e)}"
            )

    async def add_task(
        self,
        user_id: str,
        title: str,
        description: str = "",
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke add_task tool.

        Args:
            user_id: User identifier
            title: Task title
            description: Task description (optional)
            jwt_token: Optional JWT token

        Returns:
            Created task object
        """
        return await self.invoke_tool(
            "add_task",
            {"user_id": user_id, "title": title, "description": description},
            jwt_token
        )

    async def list_tasks(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke list_tasks tool.

        Args:
            user_id: User identifier
            completed: Optional completion status filter
            jwt_token: Optional JWT token

        Returns:
            List of task objects
        """
        params = {"user_id": user_id}
        if completed is not None:
            params["completed"] = completed

        return await self.invoke_tool("list_tasks", params, jwt_token)

    async def complete_task(
        self,
        user_id: str,
        task_id: str,
        completed: bool,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke complete_task tool.

        Args:
            user_id: User identifier
            task_id: Task identifier
            completed: Completion status
            jwt_token: Optional JWT token

        Returns:
            Updated task object
        """
        return await self.invoke_tool(
            "complete_task",
            {"user_id": user_id, "task_id": task_id, "completed": completed},
            jwt_token
        )

    async def update_task(
        self,
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke update_task tool.

        Args:
            user_id: User identifier
            task_id: Task identifier
            title: New title (optional)
            description: New description (optional)
            jwt_token: Optional JWT token

        Returns:
            Updated task object
        """
        params = {"user_id": user_id, "task_id": task_id}
        if title is not None:
            params["title"] = title
        if description is not None:
            params["description"] = description

        return await self.invoke_tool("update_task", params, jwt_token)

    async def delete_task(
        self,
        user_id: str,
        task_id: str,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke delete_task tool.

        Args:
            user_id: User identifier
            task_id: Task identifier
            jwt_token: Optional JWT token

        Returns:
            Deletion confirmation
        """
        return await self.invoke_tool(
            "delete_task",
            {"user_id": user_id, "task_id": task_id},
            jwt_token
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
