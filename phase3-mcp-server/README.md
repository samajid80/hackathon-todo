# Phase 3 MCP Server - Model Context Protocol Tools

MCP (Model Context Protocol) server that provides task management tools for the Phase 3 AI chatbot. This service exposes 5 tools that enable natural language task operations via the OpenAI Agents SDK.

## Overview

The MCP server acts as a bridge between the Phase 3 backend (OpenAI agent) and the Phase 2 backend (task CRUD API). It implements the Model Context Protocol to expose task management capabilities as tools that can be called by AI agents.

## Architecture

```
┌─────────────────┐
│ Phase 3 Backend │ (OpenAI Agents SDK)
│  OpenAI Agent   │
└────────┬────────┘
         │ MCP Protocol
         │ (Tool Calls)
         ▼
┌─────────────────┐
│ Phase 3 MCP     │ (This Service)
│    Server       │
│                 │
│  Tools:         │
│  - add_task     │
│  - list_tasks   │
│  - complete_task│
│  - update_task  │
│  - delete_task  │
└────────┬────────┘
         │ HTTP REST API
         ▼
┌─────────────────┐
│ Phase 2 Backend │
│  Task CRUD API  │
│  /api/tasks     │
└─────────────────┘
```

## Features

- **5 MCP Tools**: Full CRUD operations for task management
- **JWT Verification**: Ensures user isolation and security
- **HTTP Client**: Communicates with Phase 2 backend REST API
- **Error Handling**: Graceful error responses with context
- **Input Validation**: Pydantic schemas for all tool inputs
- **Stateless Design**: No database dependency, pure API gateway

## Prerequisites

- **Python**: 3.13 or higher
- **Phase 2 Backend**: Must be running and accessible
- **JWT Secret**: Must match Phase 2, Phase 3 backend, and frontend

## Installation

### 1. Navigate to directory

```bash
cd hackathon-todo/phase3-mcp-server
```

### 2. Install dependencies

Using pip:
```bash
pip install -e .
```

Using pip with dev dependencies:
```bash
pip install -e ".[dev]"
```

Using uv (recommended):
```bash
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Phase 2 Backend URL
PHASE2_BACKEND_URL=http://localhost:8000

# JWT Secret (MUST match Phase 2 and Phase 3)
JWT_SECRET=<same-as-phase2>

# Server Configuration
PORT=8002
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**CRITICAL**: `JWT_SECRET` must be **identical** across all services.

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 4
```

The server will start on `http://localhost:8002`.

## MCP Tools

### 1. add_task

Creates a new task for the authenticated user.

**Parameters**:
```json
{
  "user_id": "string (required)",
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 2000 chars)"
}
```

**Returns**:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "completed": false,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Example Usage** (via OpenAI Agent):
```
User: "Add a task to buy groceries"
Agent: Calls add_task(user_id="...", title="buy groceries")
```

### 2. list_tasks

Retrieves all tasks for the authenticated user with optional filtering.

**Parameters**:
```json
{
  "user_id": "string (required)",
  "completed": "boolean (optional)"
}
```

**Returns**:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Buy groceries",
      "completed": false,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Example Usage**:
```
User: "What are my tasks?"
Agent: Calls list_tasks(user_id="...")
```

### 3. complete_task

Marks a task as completed or incomplete.

**Parameters**:
```json
{
  "user_id": "string (required)",
  "task_id": "string (required)",
  "completed": "boolean (default: true)"
}
```

**Returns**:
```json
{
  "id": "uuid",
  "title": "Buy groceries",
  "completed": true,
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Example Usage**:
```
User: "I finished buying groceries"
Agent: Calls list_tasks to find task, then complete_task(task_id="...")
```

### 4. update_task

Updates task title and/or description.

**Parameters**:
```json
{
  "user_id": "string (required)",
  "task_id": "string (required)",
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 2000 chars)"
}
```

**Returns**:
```json
{
  "id": "uuid",
  "title": "Buy groceries and snacks",
  "description": "Updated description",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**Example Usage**:
```
User: "Rename 'Buy groceries' to 'Buy groceries and snacks'"
Agent: Calls update_task(task_id="...", title="Buy groceries and snacks")
```

### 5. delete_task

Permanently deletes a task.

**Parameters**:
```json
{
  "user_id": "string (required)",
  "task_id": "string (required)"
}
```

**Returns**:
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

**Example Usage**:
```
User: "Delete the groceries task" (after confirmation)
Agent: Calls delete_task(task_id="...")
```

## API Endpoints

The MCP server exposes its tools via FastAPI endpoints:

### Tool Invocation

```bash
POST /mcp/invoke
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "tool": "add_task",
  "arguments": {
    "user_id": "uuid",
    "title": "Buy groceries"
  }
}
```

Response:
```json
{
  "result": { ... },
  "error": null
}
```

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "phase3-mcp-server",
  "version": "1.0.0"
}
```

## Development

### Project Structure

```
phase3-mcp-server/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── server.py               # MCP Server setup
│   ├── config.py               # Environment configuration
│   ├── clients/
│   │   └── phase2_client.py    # Phase 2 backend HTTP client
│   └── tools/
│       ├── add_task.py         # add_task tool handler
│       ├── list_tasks.py       # list_tasks tool handler
│       ├── complete_task.py    # complete_task tool handler
│       ├── update_task.py      # update_task tool handler
│       └── delete_task.py      # delete_task tool handler
├── tests/                      # Test suite
├── .env.example                # Environment template
├── pyproject.toml              # Dependencies
├── railway.json                # Railway deployment config
└── README.md                   # This file
```

### Adding a New Tool

1. Create tool handler in `app/tools/my_tool.py`:

```python
from mcp import Tool
from app.clients.phase2_client import Phase2Client

async def my_tool_handler(user_id: str, **kwargs):
    """Handler for my_tool MCP tool."""
    client = Phase2Client()
    result = await client.call_endpoint(user_id, kwargs)
    return result
```

2. Register tool in `app/server.py`:

```python
from app.tools.my_tool import my_tool_handler

mcp_server.add_tool(
    Tool(
        name="my_tool",
        description="Description of what the tool does",
        input_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                # ... other parameters
            },
            "required": ["user_id"]
        },
        handler=my_tool_handler
    )
)
```

3. Update OpenAI agent to recognize the new tool.

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Specific test file
pytest tests/test_tools.py -v
```

### Linting and Type Checking

```bash
# Format code
ruff format .

# Lint code
ruff check . --fix

# Type checking
mypy app/ --strict
```

## Deployment

### Railway Deployment

#### 1. Create Railway Project

```bash
railway init
```

#### 2. Set Environment Variables

In Railway dashboard, add:
- `PHASE2_BACKEND_URL` (URL of deployed Phase 2 backend)
- `JWT_SECRET` (same as Phase 2)
- `PORT=8002`
- `ENVIRONMENT=production`

#### 3. Deploy

```bash
railway up
```

Railway will automatically detect `railway.json` and deploy the service.

#### 4. Verify Deployment

```bash
curl https://your-railway-url.railway.app/health
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PHASE2_BACKEND_URL` | Yes | - | Phase 2 backend API URL |
| `JWT_SECRET` | Yes | - | JWT signing secret (must match Phase 2) |
| `PORT` | No | `8002` | Server port |
| `ENVIRONMENT` | No | `development` | Environment (development/production) |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Testing Tools Manually

You can test tools using curl:

### Test add_task

```bash
curl -X POST http://localhost:8002/mcp/invoke \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "tool": "add_task",
    "arguments": {
      "user_id": "your-user-id",
      "title": "Test task"
    }
  }'
```

### Test list_tasks

```bash
curl -X POST http://localhost:8002/mcp/invoke \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "tool": "list_tasks",
    "arguments": {
      "user_id": "your-user-id"
    }
  }'
```

## Troubleshooting

### Phase 2 Backend Connection Issues

**Error**: `httpx.ConnectError: Failed to connect to Phase 2 backend`

**Solution**:
- Verify Phase 2 backend is running
- Check `PHASE2_BACKEND_URL` in `.env`
- Ensure network connectivity

### JWT Validation Errors

**Error**: `401 Unauthorized`

**Solution**:
- Verify `JWT_SECRET` matches across all services
- Check JWT token is valid and not expired
- Ensure Authorization header is correctly formatted

### Tool Execution Errors

**Error**: `Tool execution failed: 404 Not Found`

**Solution**:
- Verify Phase 2 backend endpoints are correct
- Check that task_id exists and belongs to user
- Ensure user_id is valid

### User Isolation Errors

**Error**: `403 Forbidden: Task does not belong to user`

**Solution**:
- Verify user_id from JWT matches task owner
- Check that task exists in database
- Ensure Phase 2 backend enforces ownership

## Security Considerations

### JWT Verification
- All tools verify JWT token before execution
- User ID extracted from JWT payload
- Token signature validated using `JWT_SECRET`

### User Isolation
- All tools enforce user_id ownership
- Cross-user access prevented by Phase 2 backend
- Tools never accept user_id from request (extracted from JWT)

### Input Validation
- Pydantic schemas validate all inputs
- Length limits enforced (title: 200 chars, description: 2000 chars)
- SQL injection prevented by Phase 2 backend (parameterized queries)

### Network Security
- Use HTTPS in production
- Limit CORS to trusted origins
- Keep `JWT_SECRET` secure and rotated

## Dependencies

### Core Dependencies
- **FastAPI**: Web framework
- **MCP**: Model Context Protocol SDK
- **httpx**: HTTP client for Phase 2 API
- **PyJWT**: JWT token handling
- **pydantic**: Data validation
- **pydantic-settings**: Environment configuration

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **ruff**: Linting and formatting
- **mypy**: Type checking

## Performance Considerations

### Stateless Design
- No database dependency
- Fast startup and shutdown
- Horizontal scaling supported

### HTTP Client Pooling
- Connection pooling enabled in httpx client
- Reduces latency for repeated requests
- Configurable timeout and retry settings

### Error Handling
- Graceful degradation when Phase 2 unavailable
- Detailed error messages for debugging
- Retry logic for transient failures

## Model Context Protocol (MCP)

This service implements the MCP specification, which enables:
- **Tool Discovery**: Agents can query available tools
- **Schema Validation**: Input/output schemas for type safety
- **Error Handling**: Standardized error responses
- **Composability**: Tools can be composed into workflows

For more information on MCP, see: https://github.com/anthropics/model-context-protocol

## Contributing

When contributing to this service:

1. **Follow MCP conventions** for tool naming and schemas
2. **Add tests** for new tools
3. **Update tool documentation** in this README
4. **Verify backward compatibility** with existing tools
5. **Test with Phase 2 backend** before deploying

## Related Services

- **Phase 2 Backend**: Task CRUD API (`backend/`)
- **Phase 3 Backend**: OpenAI agent orchestration (`phase3-backend/`)
- **Phase 3 Frontend**: Chat interface (`phase3-frontend/`)

## Support

For issues or questions:
1. Check this README for tool documentation
2. Review Phase 2 backend API documentation
3. Check the Phase 3 specification (`specs/002-chatbot-interface/`)
4. Review MCP protocol documentation

## Version History

- **1.0.0** (2024-01-15): Initial release
  - 5 MCP tools (add, list, complete, update, delete)
  - JWT authentication
  - Phase 2 backend integration
  - Error handling and validation
