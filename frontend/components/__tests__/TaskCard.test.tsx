/**
 * TaskCard with Tags Component Tests (T030)
 *
 * TODO: Set up testing infrastructure before running these tests:
 * 1. Install dependencies:
 *    npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom
 * 2. Create jest.config.js for Next.js
 * 3. Add test script to package.json: "test": "jest"
 *
 * Test Coverage:
 * - Verify tags are displayed when task has tags
 * - Verify tags are not displayed when task has no tags
 * - Verify tag styling for pending vs completed tasks
 * - Verify tag icon is displayed
 * - Verify multiple tags are displayed correctly
 * - Verify tags section has correct spacing
 */

/*
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TaskCard } from '../TaskCard';
import { Task } from '@/types/task';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('TaskCard - Tags Display', () => {
  const baseTask: Task = {
    id: '123',
    title: 'Test Task',
    description: 'Test description',
    due_date: '2025-12-31',
    priority: 'medium',
    status: 'pending',
    tags: [],
    user_id: 'user123',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  };

  describe('Tags Rendering', () => {
    test('displays tags when task has tags', () => {
      const taskWithTags: Task = {
        ...baseTask,
        tags: ['work', 'urgent'],
      };

      render(<TaskCard task={taskWithTags} />);

      expect(screen.getByText('work')).toBeInTheDocument();
      expect(screen.getByText('urgent')).toBeInTheDocument();
    });

    test('does not display tags section when task has no tags', () => {
      const taskWithoutTags: Task = {
        ...baseTask,
        tags: [],
      };

      render(<TaskCard task={taskWithoutTags} />);

      // Tags section should not exist
      expect(screen.queryByText('work')).not.toBeInTheDocument();
    });

    test('does not display tags section when tags is undefined', () => {
      const taskWithUndefinedTags: Task = {
        ...baseTask,
        tags: undefined as any,
      };

      render(<TaskCard task={taskWithUndefinedTags} />);

      // Tags section should not exist
      expect(screen.queryByText('work')).not.toBeInTheDocument();
    });

    test('displays multiple tags correctly', () => {
      const taskWithManyTags: Task = {
        ...baseTask,
        tags: ['work', 'urgent', 'important', 'personal', 'home'],
      };

      render(<TaskCard task={taskWithManyTags} />);

      expect(screen.getByText('work')).toBeInTheDocument();
      expect(screen.getByText('urgent')).toBeInTheDocument();
      expect(screen.getByText('important')).toBeInTheDocument();
      expect(screen.getByText('personal')).toBeInTheDocument();
      expect(screen.getByText('home')).toBeInTheDocument();
    });

    test('displays tag icon for each tag', () => {
      const taskWithTags: Task = {
        ...baseTask,
        tags: ['work'],
      };

      const { container } = render(<TaskCard task={taskWithTags} />);

      // Check for SVG icon (tag icon path)
      const tagIcon = container.querySelector('svg[viewBox="0 0 24 24"]');
      expect(tagIcon).toBeInTheDocument();
    });
  });

  describe('Tags Styling', () => {
    test('applies active task styling to tags for pending tasks', () => {
      const pendingTask: Task = {
        ...baseTask,
        status: 'pending',
        tags: ['work'],
      };

      const { container } = render(<TaskCard task={pendingTask} />);

      // Check for blue styling classes
      const tagElement = screen.getByText('work').parentElement;
      expect(tagElement).toHaveClass('bg-blue-50');
      expect(tagElement).toHaveClass('text-blue-700');
      expect(tagElement).toHaveClass('border-blue-200');
    });

    test('applies completed task styling to tags for completed tasks', () => {
      const completedTask: Task = {
        ...baseTask,
        status: 'completed',
        tags: ['work'],
      };

      const { container } = render(<TaskCard task={completedTask} />);

      // Check for gray styling classes
      const tagElement = screen.getByText('work').parentElement;
      expect(tagElement).toHaveClass('bg-gray-100');
      expect(tagElement).toHaveClass('text-gray-500');
    });

    test('tags have proper spacing and layout', () => {
      const taskWithTags: Task = {
        ...baseTask,
        tags: ['work', 'urgent'],
      };

      const { container } = render(<TaskCard task={taskWithTags} />);

      // Check for flex-wrap class on tags container
      const tagsContainer = screen.getByText('work').parentElement?.parentElement;
      expect(tagsContainer).toHaveClass('flex');
      expect(tagsContainer).toHaveClass('flex-wrap');
      expect(tagsContainer).toHaveClass('gap-1.5');
    });
  });

  describe('Accessibility', () => {
    test('tags have aria-label for screen readers', () => {
      const taskWithTags: Task = {
        ...baseTask,
        tags: ['work', 'urgent'],
      };

      render(<TaskCard task={taskWithTags} />);

      expect(screen.getByLabelText('Tag: work')).toBeInTheDocument();
      expect(screen.getByLabelText('Tag: urgent')).toBeInTheDocument();
    });

    test('tag icons have aria-hidden attribute', () => {
      const taskWithTags: Task = {
        ...baseTask,
        tags: ['work'],
      };

      const { container } = render(<TaskCard task={taskWithTags} />);

      const tagIcon = container.querySelector('svg[viewBox="0 0 24 24"]');
      expect(tagIcon).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Tag Position', () => {
    test('tags appear after badges and before dates section', () => {
      const taskWithTags: Task = {
        ...baseTask,
        tags: ['work'],
      };

      const { container } = render(<TaskCard task={taskWithTags} />);

      // Get all main sections
      const taskCard = container.querySelector('.bg-white');
      const sections = taskCard?.querySelectorAll('div > div');

      // Verify order: badges section exists, then tags, then dates
      const badgesSection = container.querySelector('.flex.flex-wrap.gap-2.mb-3');
      const tagsSection = screen.getByText('work').parentElement?.parentElement;

      expect(badgesSection).toBeInTheDocument();
      expect(tagsSection).toBeInTheDocument();

      // Tags should come after badges in DOM order
      if (badgesSection && tagsSection) {
        const badgesIndex = Array.from(taskCard?.children || []).indexOf(badgesSection as Element);
        const tagsIndex = Array.from(taskCard?.children || []).indexOf(tagsSection as Element);
        expect(tagsIndex).toBeGreaterThan(badgesIndex);
      }
    });
  });
});
*/

export {}; // Make this a module to avoid TypeScript errors
