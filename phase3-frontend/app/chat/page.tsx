/**
 * Chat page for Phase 3 Frontend.
 *
 * Main page for natural language todo management via AI assistant.
 */

import AuthGuard from "@/components/AuthGuard";
import ChatInterface from "@/components/ChatInterface";
import Navigation from "@/components/Navigation";

export default function ChatPage() {
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

          <ChatInterface />
        </div>
      </div>
    </AuthGuard>
  );
}
