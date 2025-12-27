"use client";

/**
 * Chat page for Phase 3 Frontend with OpenAI ChatKit.
 *
 * Main page for natural language todo management via AI assistant.
 */

import { useChatKit, ChatKit } from "@openai/chatkit-react";
import AuthGuard from "@/components/AuthGuard";
import Navigation from "@/components/Navigation";
import { getAuthToken } from "@/lib/api";

export default function ChatPage() {
  const { control } = useChatKit({
    api: {
      url: "http://localhost:8001/chatkit",
      domainKey: "dev-domain-key", // Any string works for local development
      fetch: async (input, init) => {
        // Add JWT authorization to all ChatKit requests
        const token = await getAuthToken();

        const headers = new Headers(init?.headers);
        if (token) {
          headers.set("Authorization", `Bearer ${token}`);
        }

        return fetch(input, {
          ...init,
          headers,
          credentials: "include",
        });
      },
    },
    theme: {
      colorScheme: "light",
    },
    startScreen: {
      greeting: "Welcome! How can I help you manage your tasks today?",
      prompts: [
        {
          label: "List tasks",
          prompt: "List all my tasks",
        },
        {
          label: "Add task",
          prompt: "Add a new task: Buy groceries",
        },
        {
          label: "Check pending",
          prompt: "What tasks do I have pending?",
        },
      ],
    },
  });

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Navigation />

        <div className="container mx-auto max-w-4xl px-4 py-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Chat with Your AI Assistant
            </h1>
            <p className="mt-2 text-gray-600">
              Ask me anything about your tasks - I can help you create, list, complete, update, or delete them
            </p>
          </div>

          <div className="h-[600px] w-full">
            <ChatKit
              control={control}
              className="h-full w-full rounded-lg shadow-lg bg-white"
            />
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}
