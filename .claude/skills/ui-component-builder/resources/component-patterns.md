# Next.js Component Patterns for Todo App

## General Guidelines
- Server Components: Default for static/data-fetching (e.g., fetch tasks server-side).
- Client Components: For state/interactivity (e.g., useState, useEffect).
- Styling: Tailwind classes only (e.g., 'flex flex-col space-y-2').
- API Integration: Use '@/lib/api' for calls (e.g., api.getTasks()).
- Auth: Include session checks if protected.

## Example Patterns
### Server Component (e.g., TaskList)
async function TaskList() {
  const tasks = await api.getTasks();
  return (
    <ul className="list-disc">
      {tasks.map(task => <li key={task.id}>{task.title}</li>)}
    </ul>
  );
}

### Client Component (e.g., TaskForm)
'use client';
import { useState } from 'react';

export default function TaskForm() {
  const [title, setTitle] = useState('');
  // ... onSubmit logic
  return <form>...</form>;
}