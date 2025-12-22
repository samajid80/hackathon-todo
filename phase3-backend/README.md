# Phase 3 Backend - AI-Powered Todo Chatbot

FastAPI backend service that provides natural language chatbot functionality for todo management using OpenAI Agents SDK and Model Context Protocol (MCP).

## Overview

This service acts as the orchestration layer between the frontend chat interface and the Phase 2 backend API. It uses:
- **OpenAI Agents SDK** for natural language understanding and conversation management
- **Model Context Protocol (MCP)** for tool execution (task CRUD operations)
- **SQLModel** for conversation and message persistence
- **JWT authentication** for user isolation and security

## Architecture

```
┌─────────────────┐
│  Phase 3 Frontend│ (Next.js + ChatKit)
└────────┬────────┘
         │ POST /api/{user_id}/chat
         ▼
┌─────────────────┐
│ Phase 3 Backend │ (This Service)
│  - JWT Auth     │
│  - OpenAI Agent │
│  - Conversation │
│    Storage      │
└────────┬────────┘
         │ MCP Tools
         ▼
┌─────────────────┐
│ Phase 3 MCP     │
│    Server       │
│  - add_task     │
│  - list_tasks   │
│  - complete_task│
│  - update_task  │
│  - delete_task  │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│ Phase 2 Backend │
│  - Task CRUD    │
│  - User Auth    │
└─────────────────┘
```

## Features

- **Natural Language Understanding**: Converts user messages into task operations
- **Conversation Persistence**: Stores chat history in PostgreSQL
- **Multi-Tool Support**: Integrates 5 MCP tools for full CRUD operations
- **User Isolation**: JWT-based authentication ensures data privacy
- **Error Handling**: Graceful degradation and user-friendly error messages
- **Rate Limiting**: 10 requests/minute per user
- **OpenAI Function Calling**: Automatic tool selection based on user intent

## Prerequisites

- **Python**: 3.13 or higher
- **PostgreSQL**: Neon PostgreSQL database (shared with Phase 2)
- **OpenAI API Key**: From https://platform.openai.com/api-keys
- **Phase 3 MCP Server**: Must be running (port 8002 by default)
- **Phase 2 Backend**: Must be running (port 8000 by default)

## Installation

### 1. Clone the repository

```bash
cd hackathon-todo/phase3-backend
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

Edit `.env` and configure:

```bash
# Database (use same DATABASE_URL as Phase 2)
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# OpenAI API Key
OPENAI_API_KEY=sk-...

# JWT Secret (MUST match Phase 2 and Phase 3 frontend)
JWT_SECRET=<same-as-phase2>
JWT_ALGORITHM=EdDSA

# MCP Server URL
MCP_SERVER_URL=http://localhost:8002

# Phase 2 Backend URL
PHASE2_BACKEND_URL=http://localhost:8000

# CORS Origins
CORS_ORIGINS=http://localhost:3001,http://localhost:3000

# Server
PORT=8001
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**CRITICAL**: `JWT_SECRET` must be **identical** across Phase 2 backend, Phase 3 backend, and Phase 3 frontend for authentication to work.

### 4. Run database migrations

The Phase 3 backend requires two additional tables:

```bash
# From project root
psql "$DATABASE_URL" < backend/migrations/003_create_conversations_table.sql
psql "$DATABASE_URL" < backend/migrations/004_create_messages_table.sql
```

Verify tables exist:
```bash
psql "$DATABASE_URL" -c "\dt"
```

You should see `conversations` and `messages` tables.

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

The server will start on `http://localhost:8001`.

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "phase3-backend",
  "version": "1.0.0"
}
```

### Readiness Check

```bash
GET /readiness
```

Checks database connectivity.

### Chat Endpoint

```bash
POST /api/{user_id}/chat
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "message": "Add a task to buy groceries tomorrow"
}
```

Response:
```json
{
  "conversation_id": "uuid",
  "message": "I've added 'buy groceries' to your tasks for tomorrow.",
  "timestamp": "2024-01-15T10:30:00Z",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "title": "buy groceries",
        "description": "tomorrow"
      },
      "result": {
        "id": "task-uuid",
        "title": "buy groceries",
        "completed": false
      }
    }
  ]
}
```

## Supported Natural Language Commands

### Add Task
- "Add a task to buy milk"
- "Create a new task: review report by Friday"
- "I need to schedule a meeting with John"

### List Tasks
- "What tasks do I have?"
- "Show me my incomplete tasks"
- "List all my tasks"

### Complete Task
- "I finished buying groceries"
- "Mark task X as done"
- "Complete the report review task"

### Update Task
- "Rename 'Review report' to 'Review quarterly report'"
- "Change the deadline for task X to tomorrow"
- "Update task description"

### Delete Task
- "Delete the groceries task"
- "Remove task about meeting"

Note: Delete operations require confirmation.

## Development

### Project Structure

```
phase3-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Environment configuration
│   ├── db.py                   # Database connection
│   ├── agents/
│   │   ├── openai_agent.py     # OpenAI Agents SDK setup
│   │   └── mcp_client.py       # MCP server client
│   ├── auth/
│   │   └── jwt_middleware.py   # JWT validation
│   ├── models/
│   │   └── chat.py             # Conversation & Message models
│   ├── routes/
│   │   ├── health.py           # Health endpoints
│   │   └── chat.py             # Chat endpoint
│   ├── services/
│   │   └── chat_service.py     # Business logic
│   ├── schemas/
│   │   └── chat.py             # Pydantic schemas
│   └── utils/
│       └── rate_limiter.py     # Rate limiting
├── tests/                      # Test suite
├── .env.example                # Environment template
├── pyproject.toml              # Dependencies
├── railway.json                # Railway deployment
└── README.md                   # This file
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Specific test file
pytest tests/test_chat.py -v
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

This service is configured for deployment on Railway.

#### 1. Create Railway Project

```bash
railway init
```

#### 2. Set Environment Variables

In Railway dashboard, add:
- `DATABASE_URL` (from Neon PostgreSQL)
- `OPENAI_API_KEY`
- `JWT_SECRET` (same as Phase 2)
- `JWT_ALGORITHM=EdDSA`
- `MCP_SERVER_URL` (URL of deployed MCP server)
- `PHASE2_BACKEND_URL` (URL of deployed Phase 2 backend)
- `CORS_ORIGINS` (your frontend URL)
- `PORT=8001`
- `ENVIRONMENT=production`

#### 3. Deploy

```bash
railway up
```

Railway will automatically detect `railway.json` and deploy the FastAPI service.

#### 4. Verify Deployment

```bash
curl https://your-railway-url.railway.app/health
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `JWT_SECRET` | Yes | - | JWT signing secret (must match Phase 2) |
| `JWT_ALGORITHM` | No | `EdDSA` | JWT algorithm |
| `MCP_SERVER_URL` | Yes | - | Phase 3 MCP server URL |
| `PHASE2_BACKEND_URL` | No | `http://localhost:8000` | Phase 2 backend URL |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:3001` | Allowed CORS origins |
| `PORT` | No | `8001` | Server port |
| `ENVIRONMENT` | No | `development` | Environment (development/production) |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Rate Limiting

Default rate limits:
- **Chat endpoint**: 10 requests/minute per user
- Returns HTTP 429 with `Retry-After` header when exceeded

### OpenAI Configuration

The service uses:
- **Model**: `gpt-4o` (configurable in `app/agents/openai_agent.py`)
- **Temperature**: 0.7
- **Max tokens**: 500
- **Function calling**: Enabled for MCP tools

## Troubleshooting

### Database Connection Issues

**Error**: `ValueError: DATABASE_URL environment variable is not set`

**Solution**: Ensure `.env` file exists and contains valid `DATABASE_URL`.

### OpenAI API Errors

**Error**: `openai.AuthenticationError`

**Solution**: Verify `OPENAI_API_KEY` is valid and has available credits.

### JWT Validation Errors

**Error**: `HTTPException: Could not validate credentials`

**Solution**: Ensure `JWT_SECRET` matches across Phase 2 backend, Phase 3 backend, and Phase 3 frontend.

### MCP Server Connection Issues

**Error**: `httpx.ConnectError`

**Solution**: Verify Phase 3 MCP server is running and `MCP_SERVER_URL` is correct.

### CORS Errors

**Error**: `Access to fetch blocked by CORS policy`

**Solution**: Add frontend URL to `CORS_ORIGINS` environment variable.

## Security Considerations

### JWT Authentication
- All chat endpoints require valid JWT token
- User ID extracted from JWT and enforced in all operations
- Tokens validated using `JWT_SECRET` from environment

### User Isolation
- Conversations scoped to authenticated user
- MCP tools verify user ownership before operations
- Cross-user data access prevented

### Input Validation
- Message length limited to 1-2000 characters
- User messages sanitized before storage
- Pydantic validation on all inputs

### Rate Limiting
- 10 requests/minute per user
- Prevents abuse and controls OpenAI costs

### Environment Security
- Never commit `.env` file
- Use environment variables in production
- Rotate `JWT_SECRET` and `OPENAI_API_KEY` regularly

## Dependencies

### Core Dependencies
- **FastAPI**: Web framework
- **SQLModel**: ORM and database models
- **OpenAI**: OpenAI API client
- **openai-agents**: OpenAI Agents SDK
- **asyncpg**: PostgreSQL async driver
- **PyJWT**: JWT token handling
- **httpx**: HTTP client for MCP server
- **pydantic-settings**: Environment configuration

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **ruff**: Linting and formatting
- **mypy**: Type checking

## Contributing

When contributing to this service:

1. **Run tests** before committing
2. **Follow PEP 8** style guide (enforced by ruff)
3. **Add type hints** for all functions
4. **Update tests** for new features
5. **Update documentation** for API changes

## License

This project is part of the Hackathon Todo application.

## Related Services

- **Phase 2 Backend**: Task CRUD API (`backend/`)
- **Phase 3 MCP Server**: MCP tool server (`phase3-mcp-server/`)
- **Phase 3 Frontend**: Chat interface (`phase3-frontend/`)

## Support

For issues or questions:
1. Check this README
2. Review the main project documentation
3. Check the Phase 3 specification (`specs/002-chatbot-interface/`)

## Version History

- **1.0.0** (2024-01-15): Initial release
  - Natural language task management
  - 5 MCP tools (add, list, complete, update, delete)
  - Conversation persistence
  - JWT authentication
  - Rate limiting
