/**
 * TagSelector Component Tests (T029)
 *
 * TODO: Set up testing infrastructure before running these tests:
 * 1. Install dependencies:
 *    npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom
 * 2. Create jest.config.js for Next.js
 * 3. Add test script to package.json: "test": "jest"
 *
 * Test Coverage:
 * - Render component with empty tags
 * - Add tag via Enter key
 * - Add tag via autocomplete suggestion
 * - Remove tag via chip close button
 * - Remove last tag via Backspace on empty input
 * - Max 10 tags validation
 * - Tag format validation (lowercase alphanumeric + hyphens)
 * - Duplicate tag prevention
 * - Tag length validation (1-50 characters)
 * - Autocomplete dropdown display
 * - Escape key closes autocomplete
 */

/*
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { TagSelector } from '../TagSelector';

// Mock useTags hook
jest.mock('@/lib/hooks/useTags', () => ({
  useTags: jest.fn(() => ({
    tags: ['work', 'personal', 'urgent', 'home'],
    isLoading: false,
    error: null,
    refetch: jest.fn(),
  })),
}));

describe('TagSelector', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  describe('Rendering', () => {
    test('renders input field with placeholder', () => {
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);
      expect(screen.getByPlaceholderText(/add tags/i)).toBeInTheDocument();
    });

    test('displays selected tags as chips', () => {
      render(<TagSelector selectedTags={['work', 'urgent']} onChange={mockOnChange} />);
      expect(screen.getByText('work')).toBeInTheDocument();
      expect(screen.getByText('urgent')).toBeInTheDocument();
    });

    test('shows help text with tag count', () => {
      render(<TagSelector selectedTags={['work']} onChange={mockOnChange} />);
      expect(screen.getByText(/1\/10 tags/i)).toBeInTheDocument();
    });

    test('disables input when max tags reached', () => {
      const maxTags = Array.from({ length: 10 }, (_, i) => `tag${i + 1}`);
      render(<TagSelector selectedTags={maxTags} onChange={mockOnChange} />);
      const input = screen.getByPlaceholderText(/maximum 10 tags/i);
      expect(input).toBeDisabled();
    });
  });

  describe('Adding Tags', () => {
    test('adds tag when Enter key is pressed', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'work{Enter}');

      expect(mockOnChange).toHaveBeenCalledWith(['work']);
    });

    test('normalizes tag to lowercase', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'URGENT{Enter}');

      expect(mockOnChange).toHaveBeenCalledWith(['urgent']);
    });

    test('trims whitespace from tags', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, '  work  {Enter}');

      expect(mockOnChange).toHaveBeenCalledWith(['work']);
    });

    test('clears input after adding tag', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i) as HTMLInputElement;
      await user.type(input, 'work{Enter}');

      expect(input.value).toBe('');
    });

    test('adds tag from autocomplete suggestion', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'wo');

      // Wait for suggestions to appear
      await waitFor(() => {
        expect(screen.getByText('work')).toBeInTheDocument();
      });

      // Click on suggestion
      const suggestion = screen.getByText('work');
      await user.click(suggestion);

      expect(mockOnChange).toHaveBeenCalledWith(['work']);
    });
  });

  describe('Removing Tags', () => {
    test('removes tag when close button is clicked', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={['work', 'urgent']} onChange={mockOnChange} />);

      const removeButtons = screen.getAllByLabelText(/remove tag/i);
      await user.click(removeButtons[0]); // Remove first tag

      expect(mockOnChange).toHaveBeenCalledWith(['urgent']);
    });

    test('removes last tag when Backspace is pressed on empty input', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={['work', 'urgent']} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, '{Backspace}');

      expect(mockOnChange).toHaveBeenCalledWith(['work']);
    });

    test('does not remove tag when Backspace is pressed on non-empty input', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={['work']} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'test{Backspace}');

      expect(mockOnChange).not.toHaveBeenCalled();
    });
  });

  describe('Validation', () => {
    test('shows error for max 10 tags', async () => {
      const user = userEvent.setup();
      const maxTags = Array.from({ length: 10 }, (_, i) => `tag${i + 1}`);
      render(<TagSelector selectedTags={maxTags} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/maximum 10 tags/i);
      await user.type(input, 'extra{Enter}');

      expect(screen.getByText(/maximum 10 tags allowed/i)).toBeInTheDocument();
      expect(mockOnChange).not.toHaveBeenCalled();
    });

    test('shows error for duplicate tag', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={['work']} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'work{Enter}');

      expect(screen.getByText(/tag already added/i)).toBeInTheDocument();
      expect(mockOnChange).not.toHaveBeenCalled();
    });

    test('shows error for invalid format (special characters)', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'urgent!!!{Enter}');

      expect(screen.getByText(/can only contain lowercase letters, numbers, and hyphens/i)).toBeInTheDocument();
      expect(mockOnChange).not.toHaveBeenCalled();
    });

    test('shows error for tag too long', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const longTag = 'a'.repeat(51);
      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, `${longTag}{Enter}`);

      expect(screen.getByText(/must be 50 characters or less/i)).toBeInTheDocument();
      expect(mockOnChange).not.toHaveBeenCalled();
    });

    test('shows error for empty tag', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, '   {Enter}');

      expect(screen.getByText(/cannot be empty/i)).toBeInTheDocument();
      expect(mockOnChange).not.toHaveBeenCalled();
    });

    test('clears error when valid input is typed', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={['work']} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);

      // Trigger error
      await user.type(input, 'work{Enter}');
      expect(screen.getByText(/tag already added/i)).toBeInTheDocument();

      // Type new input
      await user.type(input, 'urgent');
      expect(screen.queryByText(/tag already added/i)).not.toBeInTheDocument();
    });
  });

  describe('Autocomplete', () => {
    test('shows suggestions when typing', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'wo');

      await waitFor(() => {
        expect(screen.getByText('work')).toBeInTheDocument();
      });
    });

    test('filters out already selected tags from suggestions', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={['work']} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'wo');

      await waitFor(() => {
        expect(screen.queryByText('work')).not.toBeInTheDocument();
      });
    });

    test('closes suggestions when Escape is pressed', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'wo');

      await waitFor(() => {
        expect(screen.getByText('work')).toBeInTheDocument();
      });

      await user.type(input, '{Escape}');

      await waitFor(() => {
        expect(screen.queryByText('work')).not.toBeInTheDocument();
      });
    });

    test('hides suggestions when input is cleared', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'wo');

      await waitFor(() => {
        expect(screen.getByText('work')).toBeInTheDocument();
      });

      await user.clear(input);

      await waitFor(() => {
        expect(screen.queryByText('work')).not.toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA attributes', () => {
      render(<TagSelector selectedTags={[]} onChange={mockOnChange} />);
      const input = screen.getByPlaceholderText(/add tags/i);

      expect(input).toHaveAttribute('aria-invalid', 'false');
      expect(input).toHaveAttribute('aria-describedby', 'tag-help');
    });

    test('updates ARIA attributes when error occurs', async () => {
      const user = userEvent.setup();
      render(<TagSelector selectedTags={['work']} onChange={mockOnChange} />);

      const input = screen.getByPlaceholderText(/add tags/i);
      await user.type(input, 'work{Enter}');

      expect(input).toHaveAttribute('aria-invalid', 'true');
      expect(input).toHaveAttribute('aria-describedby', 'tag-error');
    });

    test('tag chips have aria-label', () => {
      render(<TagSelector selectedTags={['work']} onChange={mockOnChange} />);
      expect(screen.getByLabelText(/remove tag work/i)).toBeInTheDocument();
    });
  });
});
*/

export {}; // Make this a module to avoid TypeScript errors
