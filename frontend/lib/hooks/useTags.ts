/**
 * useTags Hook (T023, T056-T058)
 *
 * Features:
 * - Fetch all unique tags used by the user
 * - Client-side caching with 5-minute TTL (T058)
 * - Debounced fetching (300ms) for autocomplete
 * - Loading and error states
 * - Automatic refetch on mount if cache is stale
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { getUserTags } from "@/lib/api/tasks";

// Cache for tags (T058)
let tagsCache: string[] | null = null;
let tagsCacheTimestamp: number = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Fetch all unique tags for the authenticated user (T056)
 *
 * Calls the GET /api/tasks/tags endpoint which returns all unique tags
 * used across all user's tasks, sorted alphabetically.
 */
async function fetchTags(): Promise<string[]> {
  return getUserTags();
}

/**
 * Check if cache is valid
 */
function isCacheValid(): boolean {
  if (!tagsCache) return false;
  const now = Date.now();
  return now - tagsCacheTimestamp < CACHE_TTL;
}

export interface UseTagsResult {
  tags: string[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch and cache user tags with debouncing
 *
 * @param searchQuery - Optional search query for filtering (debounced 300ms)
 * @returns Tags array, loading state, error state, and refetch function
 */
export function useTags(searchQuery?: string): UseTagsResult {
  const [tags, setTags] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  // Fetch tags function
  const loadTags = async () => {
    // Use cache if valid
    if (isCacheValid() && tagsCache) {
      setTags(tagsCache);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const fetchedTags = await fetchTags();

      // Update cache
      tagsCache = fetchedTags;
      tagsCacheTimestamp = Date.now();

      if (isMountedRef.current) {
        setTags(fetchedTags);
        setIsLoading(false);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to fetch tags";

      if (isMountedRef.current) {
        setError(errorMessage);
        setIsLoading(false);
        setTags([]);
      }
    }
  };

  // Debounced refetch for search queries
  useEffect(() => {
    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Load from cache immediately if available and valid
    if (isCacheValid() && tagsCache) {
      setTags(tagsCache);
      return;
    }

    // Debounce API call (300ms)
    debounceTimerRef.current = setTimeout(() => {
      loadTags();
    }, 300);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [searchQuery]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  return {
    tags,
    isLoading,
    error,
    refetch: loadTags,
  };
}
