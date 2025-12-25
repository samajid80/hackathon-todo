/**
 * ChatMessage component for rendering individual messages.
 *
 * Displays user and assistant messages with styling and tool call info.
 * Supports tag display for tasks embedded in assistant messages.
 */

"use client";

import type { Message } from "@/lib/types";
import TagBadge from "./TagBadge";

interface ChatMessageProps {
  message: Message;
}

/**
 * Decode HTML entities in text.
 * Backend escapes quotes and other characters for XSS protection,
 * so we need to unescape them for display.
 */
function decodeHtmlEntities(text: string): string {
  const textarea = document.createElement('textarea');
  textarea.innerHTML = text;
  return textarea.value;
}

/**
 * Extract tags from message content for display.
 * Tags are expected to be in format: [...tags: work, urgent, home]
 */
function extractTagsFromContent(content: string): { cleanContent: string; tagsByLine: Map<number, string[]> } {
  const tagsByLine = new Map<number, string[]>();
  const lines = content.split('\n');

  const cleanLines = lines.map((line, index) => {
    // Match tags in format: [tag1, tag2, tag3] or similar patterns
    const tagMatch = line.match(/\[(?:tags?:?\s*)?([\w\s,\-]+)\]/i);
    if (tagMatch) {
      const tagsString = tagMatch[1];
      const tags = tagsString.split(',').map(t => t.trim()).filter(t => t.length > 0);
      if (tags.length > 0) {
        tagsByLine.set(index, tags);
        // Remove the tag annotation from the line
        return line.replace(/\[(?:tags?:?\s*)?([\w\s,\-]+)\]/i, '').trim();
      }
    }
    return line;
  });

  return {
    cleanContent: cleanLines.join('\n'),
    tagsByLine
  };
}

/**
 * Render tags with truncation (max 5 tags, "...+N more" for overflow).
 */
function renderTags(tags: string[]): JSX.Element {
  const maxDisplayTags = 5;
  const displayTags = tags.slice(0, maxDisplayTags);
  const remainingCount = tags.length - maxDisplayTags;

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {displayTags.map((tag, idx) => (
        <TagBadge key={idx} tag={tag} size="sm" />
      ))}
      {remainingCount > 0 && (
        <span className="text-xs text-gray-600 self-center">
          ...+{remainingCount} more
        </span>
      )}
    </div>
  );
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const decodedContent = decodeHtmlEntities(message.content);
  const { cleanContent, tagsByLine } = extractTagsFromContent(decodedContent);
  const displayContent = cleanContent;

  // Extract all tags for rendering (if message has embedded tags)
  const allTags: string[] = [];
  tagsByLine.forEach((tags) => {
    allTags.push(...tags);
  });

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gray-100 text-gray-900"
        }`}
      >
        {/* Message Content */}
        <p className="whitespace-pre-wrap break-words">{displayContent}</p>

        {/* Tags Display (if any tags found in content) */}
        {!isUser && allTags.length > 0 && (
          <div className="mt-2">
            {renderTags(allTags)}
          </div>
        )}

        {/* Tool Calls Info (for assistant messages) */}
        {!isUser && message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300">
            <p className="text-xs font-semibold text-gray-600 mb-2">
              Actions performed:
            </p>
            <div className="space-y-1">
              {message.tool_calls.map((toolCall, idx) => (
                <div key={idx} className="text-xs text-gray-600">
                  <span className="font-medium">{toolCall.tool}</span>
                  {toolCall.error ? (
                    <span className="text-red-600 ml-2">
                      (Error: {toolCall.error})
                    </span>
                  ) : (
                    <span className="text-green-600 ml-2">✓</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <p
          className={`mt-2 text-xs ${
            isUser ? "text-blue-200" : "text-gray-500"
          }`}
        >
          {new Date(message.created_at).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
