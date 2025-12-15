---
name: ui-component-builder
description: Build reusable Next.js UI components from specs, incorporating Tailwind CSS, server/client patterns, and API integration.
version: 1.0
---

# UI Component Builder Skill

## Overview
This skill generates TypeScript Next.js components (e.g., forms, lists) based on UI specs, ensuring responsiveness, interactivity where needed, and adherence to Phase 2 patterns like Tailwind styling and API calls via /lib/api.ts.

## Instructions
1. Parse the UI spec (e.g., @specs/ui/components.md or @specs/features/task-crud.md) for component details like props, state, and interactions.
2. Determine component type:
   - Use server components by default for data fetching.
   - Switch to client components ('use client') only for interactivity (e.g., forms with hooks).
3. Generate TSX code:
   - Apply Tailwind CSS classes for styling (no inline styles).
   - Integrate API client for data ops (e.g., fetch tasks with auth headers).
   - Follow existing patterns from @resources/component-patterns.md.
4. Handle props and events: e.g., onSubmit for forms, onClick for buttons.
5. Output the full component file, ready for /frontend/app/tasks/components/.
6. Suggest imports (e.g., from 'next', 'react') and any new deps for package.json.

## Inputs
- Spec reference: e.g., @specs/ui/pages.md
- Optional: Existing component paths for extension (e.g., /frontend/components/Button.tsx)

## Outputs
- Generated TSX file (e.g., TaskForm.tsx)
- Suggestions for layout integration (e.g., in page.tsx)
- Validation notes from script (e.g., lint checks)

## Examples
### Example 1: Task List Component
Input Spec: "Create TaskList component to display tasks with title, status, edit/delete buttons."
Output: TaskList.tsx with map over tasks array, Tailwind grid, client-side for buttons.

### Example 2: Form Component
Input Spec: "Build TaskForm for adding/updating tasks with title/description inputs."
Output: TaskForm.tsx as client component with useState, onSubmit fetching API.

## Dependencies
- Next.js 16, TypeScript, Tailwind CSS (assume installed; add to package.json if needed).

## Testing
Run the included script tsx-generator.py with sample spec snippet to preview output.