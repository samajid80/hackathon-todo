"""
MCP Server implementation using Official MCP SDK.

Manages registration and execution of MCP tools for task management.
"""

from typing import Dict, Any, Callable, Awaitable


class MCPServer:
    """
    MCP Server for managing and executing tools.

    This is a simplified implementation that will be enhanced with
    the official MCP SDK once tools are registered.
    """

    def __init__(self, name: str = "todo-mcp-server"):
        """
        Initialize MCP Server.

        Args:
            name: Server identifier
        """
        self.name = name
        self.tools: Dict[str, Callable[..., Awaitable[Dict[str, Any]]]] = {}

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Awaitable[Dict[str, Any]]],
        description: str = ""
    ) -> None:
        """
        Register an MCP tool handler.

        Args:
            name: Tool name (e.g., 'add_task')
            handler: Async function to execute tool
            description: Tool description for OpenAI function calling
        """
        self.tools[name] = handler
        print(f"[MCP Server] Registered tool: {name}")

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered MCP tool.

        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
            Exception: If tool execution fails
        """
        if tool_name not in self.tools:
            available_tools = ", ".join(self.tools.keys())
            raise ValueError(
                f"Tool '{tool_name}' not found. Available tools: {available_tools}"
            )

        handler = self.tools[tool_name]

        try:
            result = await handler(**parameters)
            print(f"[MCP Server] Tool '{tool_name}' executed successfully")
            return result

        except Exception as e:
            print(f"[MCP Server] Tool '{tool_name}' execution failed: {str(e)}")
            raise


# Global MCP Server instance
mcp_server = MCPServer("todo-mcp-server")


# Tool registration will be done in individual tool modules
# Example:
# from app.tools import add_task
# mcp_server.register_tool("add_task", add_task.handler, add_task.description)
