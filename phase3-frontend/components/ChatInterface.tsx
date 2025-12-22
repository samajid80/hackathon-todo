/**
 * ChatInterface component using OpenAI ChatKit.
 *
 * Main chat UI for conversing with the AI assistant.
 */

"use client";

import { useState } from "react";
import { sendMessage } from "@/lib/api";
import type { Message } from "@/lib/types";
import ChatMessage from "./ChatMessage";
import LoadingSpinner from "./LoadingSpinner";

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userInput = input.trim();
    setInput("");
    setError(null);

    // Step 1: Immediately show user's message (optimistic update)
    const tempUserId = `temp-${Date.now()}`;
    const optimisticUserMessage: Message = {
      id: tempUserId,
      conversation_id: conversationId || "",
      role: "user",
      content: userInput,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, optimisticUserMessage]);

    // Step 2: NOW show loading spinner (AI is "thinking")
    setIsLoading(true);

    try {
      // Call chat API
      const response = await sendMessage({
        conversation_id: conversationId || undefined,
        message: userInput,
      });

      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Step 3: Replace temp user message with real one and add assistant response
      setMessages((prev) => [
        ...prev.filter((msg) => msg.id !== tempUserId), // Remove temp message
        {
          id: response.user_message.id,
          conversation_id: response.conversation_id,
          role: "user",
          content: response.user_message.content,
          created_at: response.user_message.created_at,
        },
        {
          id: response.assistant_message.id,
          conversation_id: response.conversation_id,
          role: "assistant",
          content: response.assistant_message.content,
          created_at: response.assistant_message.created_at,
          tool_calls: response.assistant_message.tool_calls,
        },
      ]);
    } catch (err) {
      console.error("Failed to send message:", err);
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove optimistic message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== tempUserId));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-12">
            <p className="text-lg font-medium mb-2">
              Welcome to your AI Todo Assistant!
            </p>
            <p className="text-sm">
              Try saying: &quot;Add a task to buy groceries&quot; or &quot;Show me my tasks&quot;
            </p>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <LoadingSpinner />
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
