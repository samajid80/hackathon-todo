"""
Main FastAPI application for Phase 3 MCP Server.

Exposes MCP tools for task management via HTTP endpoints.
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.config import settings
from app.server import mcp_server

# Import all MCP tools
from app.tools import add_task, list_tasks, complete_task, update_task, delete_task


app = FastAPI(
    title="Phase 3 MCP Server",
    description="Model Context Protocol tools for task management",
    version="1.0.0",
)


# Register all MCP tools on startup
@app.on_event("startup")
async def register_tools():
    """Register all MCP tools with the MCP server."""
    mcp_server.register_tool(
        name=add_task.TOOL_NAME,
        handler=add_task.add_task,
        description=add_task.TOOL_DESCRIPTION
    )
    mcp_server.register_tool(
        name=list_tasks.TOOL_NAME,
        handler=list_tasks.list_tasks,
        description=list_tasks.TOOL_DESCRIPTION
    )
    mcp_server.register_tool(
        name=complete_task.TOOL_NAME,
        handler=complete_task.complete_task,
        description=complete_task.TOOL_DESCRIPTION
    )
    mcp_server.register_tool(
        name=update_task.TOOL_NAME,
        handler=update_task.update_task,
        description=update_task.TOOL_DESCRIPTION
    )
    mcp_server.register_tool(
        name=delete_task.TOOL_NAME,
        handler=delete_task.delete_task,
        description=delete_task.TOOL_DESCRIPTION
    )
    print("[MCP Server] All tools registered successfully")


class MCPRequest(BaseModel):
    """Request model for MCP tool invocation."""

    tool: str
    parameters: Dict[str, Any]


class MCPResponse(BaseModel):
    """Response model for MCP tool invocation."""

    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Phase 3 MCP Server",
        "version": "1.0.0",
        "status": "running",
        "available_tools": list(mcp_server.tools.keys()) if hasattr(mcp_server, 'tools') else [],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "phase3-mcp-server"}


@app.post("/mcp", response_model=MCPResponse)
async def invoke_mcp_tool(
    request: MCPRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Invoke an MCP tool.

    Args:
        request: MCPRequest with tool name and parameters
        authorization: Optional Authorization header with Bearer token

    Returns:
        MCPResponse with tool execution result

    Raises:
        HTTPException: 400 if tool not found, 500 if tool execution fails
    """
    try:
        # Extract JWT token from Authorization header and add to parameters
        parameters = request.parameters.copy()
        if authorization and authorization.startswith("Bearer "):
            jwt_token = authorization.replace("Bearer ", "")
            parameters["jwt_token"] = jwt_token

        # Execute tool via MCP server
        result = await mcp_server.execute_tool(request.tool, parameters)
        return MCPResponse(success=True, result=result)

    except ValueError as e:
        # Tool not found
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Tool execution failed
        print(f"[MCP] Tool execution error: {type(e).__name__}: {str(e)}")
        return MCPResponse(success=False, error=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)
