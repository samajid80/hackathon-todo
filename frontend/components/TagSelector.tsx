/**
 * Tag Selector Component (T022, T024)
 *
 * Features:
 * - Input field for entering tags
 * - Add/remove tags with chips display
 * - Max 10 tags validation
 * - Autocomplete with client-side filtering (debounced 300ms)
 * - Tag format validation (lowercase alphanumeric + hyphens)
 * - Visual feedback for invalid tags
 * - Keyboard navigation (Enter to add, Backspace to remove last)
 */

"use client";

import React, { useState, useRef, useEffect, KeyboardEvent, ChangeEvent } from "react";
import { useTags } from "@/lib/hooks/useTags";

export interface TagSelectorRef {
  addPendingTag: () => void; // Method to add any pending tag in the input field
}

export interface TagSelectorProps {
  selectedTags: string[];
  onChange: (tags: string[]) => void;
  maxTags?: number;
  placeholder?: string;
  className?: string;
  onInputChange?: (value: string) => void; // Expose current input value
}

export const TagSelector = React.forwardRef<TagSelectorRef, TagSelectorProps>(({
  selectedTags,
  onChange,
  maxTags = 10,
  placeholder = "Add tags (press Enter)",
  className = "",
  onInputChange,
}, ref) => {
  const [inputValue, setInputValue] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Debounced tag fetching
  const { tags: availableTags, isLoading } = useTags(inputValue);

  // Filter suggestions (client-side filtering)
  const suggestions = React.useMemo(() => {
    if (!inputValue.trim()) return [];

    const lowerInput = inputValue.toLowerCase().trim();
    return availableTags
      .filter(
        (tag) =>
          tag.includes(lowerInput) && !selectedTags.includes(tag)
      )
      .slice(0, 5); // Limit to 5 suggestions
  }, [inputValue, availableTags, selectedTags]);

  // Expose addPendingTag method to parent via ref
  React.useImperativeHandle(ref, () => ({
    addPendingTag: () => {
      if (inputValue.trim()) {
        addTag(inputValue);
      }
    },
  }));

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Validate tag format
  const validateTag = (tag: string): string | null => {
    const trimmed = tag.trim().toLowerCase();

    if (!trimmed) {
      return "Tag cannot be empty";
    }

    if (trimmed.length > 50) {
      return "Tag must be 50 characters or less";
    }

    if (!/^[a-z0-9-]+$/.test(trimmed)) {
      return "Tags can only contain lowercase letters, numbers, and hyphens";
    }

    if (selectedTags.includes(trimmed)) {
      return "Tag already added";
    }

    if (selectedTags.length >= maxTags) {
      return `Maximum ${maxTags} tags allowed`;
    }

    return null;
  };

  // Handle tag addition
  const addTag = (tag: string) => {
    const error = validateTag(tag);

    if (error) {
      setError(error);
      return;
    }

    const normalizedTag = tag.trim().toLowerCase();
    onChange([...selectedTags, normalizedTag]);
    setInputValue("");
    setError(null);
    setShowSuggestions(false);
  };

  // Handle tag removal
  const removeTag = (tagToRemove: string) => {
    onChange(selectedTags.filter((tag) => tag !== tagToRemove));
    setError(null);
  };

  // Handle input change
  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    setError(null);

    // Notify parent of input value changes
    if (onInputChange) {
      onInputChange(value);
    }

    // Show suggestions if there's input
    if (value.trim()) {
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  // Handle keyboard events
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (inputValue.trim()) {
        addTag(inputValue);
      }
    } else if (e.key === "Backspace" && !inputValue && selectedTags.length > 0) {
      // Remove last tag when backspace is pressed on empty input
      removeTag(selectedTags[selectedTags.length - 1]);
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (tag: string) => {
    addTag(tag);
    inputRef.current?.focus();
  };

  return (
    <div className={`relative ${className}`}>
      {/* Selected tags display */}
      <div className="flex flex-wrap gap-2 mb-2">
        {selectedTags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label={`Remove tag ${tag}`}
            >
              <svg
                className="w-3 h-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </span>
        ))}
      </div>

      {/* Input field */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => inputValue.trim() && setShowSuggestions(true)}
          placeholder={selectedTags.length >= maxTags ? `Maximum ${maxTags} tags` : placeholder}
          disabled={selectedTags.length >= maxTags}
          className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            error ? "border-red-500" : "border-gray-300"
          } ${selectedTags.length >= maxTags ? "bg-gray-100 cursor-not-allowed" : ""}`}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={error ? "tag-error" : "tag-help"}
        />

        {/* Autocomplete suggestions */}
        {showSuggestions && suggestions.length > 0 && (
          <div
            ref={suggestionsRef}
            className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto"
          >
            {suggestions.map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => handleSuggestionClick(tag)}
                className="w-full px-3 py-2 text-left hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
              >
                <span className="text-sm text-gray-900">{tag}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p id="tag-error" className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {/* Help text */}
      {!error && (
        <p id="tag-help" className="mt-1 text-sm text-gray-500">
          {selectedTags.length}/{maxTags} tags • lowercase alphanumeric + hyphens • press Enter to add
        </p>
      )}
    </div>
  );
});

TagSelector.displayName = "TagSelector";
