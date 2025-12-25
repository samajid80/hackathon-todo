"""
HTTP client for calling Phase 2 Backend REST API.

Provides methods for all task CRUD operations via Phase 2 endpoints.
"""

import httpx
from typing import Dict, Any, List, Optional

from app.config import settings


class Phase2Client:
    """
    Async HTTP client for Phase 2 Backend task management API.

    All MCP tools use this client to interact with Phase 2 backend,
    ensuring the backend remains the single source of truth for tasks.
    """

    def __init__(self):
        """Initialize with base URL from settings."""
        self.base_url = settings.phase2_backend_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new task via Phase 2 backend.

        Args:
            user_id: User identifier
            title: Task title (required, 1-200 chars)
            description: Task description (optional, 0-2000 chars)
            due_date: Due date in ISO 8601 format (YYYY-MM-DD) (optional)
            priority: Priority level: "low", "medium", or "high" (optional, default: "medium")
            tags: Optional list of tags (max 10 tags, 1-50 chars each, lowercase alphanumeric + hyphens)
            jwt_token: Optional JWT token for authentication

        Returns:
            Task object from Phase 2 backend

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.base_url}/api/tasks/"
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        payload = {"title": title, "description": description}
        if due_date is not None:
            payload["due_date"] = due_date
        if priority is not None:
            payload["priority"] = priority
        if tags is not None:
            payload["tags"] = tags

        response = await self.client.post(
            url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def list_tasks(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        jwt_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List tasks for a user via Phase 2 backend.

        Args:
            user_id: User identifier
            completed: Optional filter by completion status
            tags: Optional filter by tags (AND logic: task must have all tags)
            jwt_token: Optional JWT token for authentication

        Returns:
            List of task objects

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.base_url}/api/tasks/"
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        params = {}
        if completed is not None:
            params["completed"] = str(completed).lower()
        if tags:
            # Phase 2 backend expects tags as comma-separated query param
            params["tags"] = ",".join(tags)

        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def complete_task(
        self,
        user_id: str,
        task_id: str,
        completed: bool,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark task as complete/incomplete via Phase 2 backend.

        Args:
            user_id: User identifier
            task_id: Task identifier
            completed: Completion status
            jwt_token: Optional JWT token for authentication

        Returns:
            Updated task object

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.base_url}/api/tasks/{task_id}/complete"
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        response = await self.client.patch(
            url,
            json={"completed": completed},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def delete_task(
        self,
        user_id: str,
        task_id: str,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a task via Phase 2 backend.

        Args:
            user_id: User identifier
            task_id: Task identifier
            jwt_token: Optional JWT token for authentication

        Returns:
            Success confirmation

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.base_url}/api/tasks/{task_id}"
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        response = await self.client.delete(url, headers=headers)
        response.raise_for_status()

        # Phase 2 backend returns 204 No Content on successful delete
        if response.status_code == 204:
            return {"status": "deleted", "task_id": task_id}

        return response.json()

    async def update_task(
        self,
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update task fields via Phase 2 backend.

        Args:
            user_id: User identifier
            task_id: Task identifier
            title: New title (optional)
            description: New description (optional)
            due_date: New due date in ISO 8601 format YYYY-MM-DD (optional)
            priority: New priority level: "low", "medium", or "high" (optional)
            tags: New tags list (optional, replaces existing tags)
            jwt_token: Optional JWT token for authentication

        Returns:
            Updated task object

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.base_url}/api/tasks/{task_id}"
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        payload = {}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if due_date is not None:
            payload["due_date"] = due_date
        if priority is not None:
            payload["priority"] = priority
        if tags is not None:
            payload["tags"] = tags

        response = await self.client.put(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_task(
        self, user_id: str, task_id: str, jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a single task by ID via Phase 2 backend.

        Args:
            user_id: User identifier
            task_id: Task identifier
            jwt_token: Optional JWT token for authentication

        Returns:
            Task object

        Raises:
            httpx.HTTPStatusError: If API request fails (404 if task not found)
        """
        url = f"{self.base_url}/api/tasks/{task_id}"
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    async def list_tags(self, user_id: str, jwt_token: Optional[str] = None) -> List[str]:
        """
        List all unique tags for a user via Phase 2 backend.

        Args:
            user_id: User identifier
            jwt_token: Optional JWT token for authentication

        Returns:
            List of unique tags (alphabetically sorted)

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.base_url}/api/tasks/tags"
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
