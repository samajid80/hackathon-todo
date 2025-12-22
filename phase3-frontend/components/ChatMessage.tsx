/**
 * ChatMessage component for rendering individual messages.
 *
 * Displays user and assistant messages with styling and tool call info.
 */

"use client";

import type { Message } from "@/lib/types";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

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
        <p className="whitespace-pre-wrap break-words">{message.content}</p>

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
