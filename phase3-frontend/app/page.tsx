/**
 * Home/Landing page for AI Todo Assistant.
 *
 * Shows application features and benefits to both authenticated and unauthenticated users.
 */

"use client";

import Link from "next/link";
import { useSession } from "@/lib/auth-client";
import Navigation from "@/components/Navigation";

export default function HomePage() {
  const { data: session, isPending } = useSession();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <Navigation />

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Manage Your Tasks with{" "}
            <span className="text-blue-600">Natural Language</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Say goodbye to complicated task managers. Just tell our AI assistant
            what you need to do, and it handles the rest.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            {!isPending && (
              <>
                {session?.user ? (
                  <Link
                    href="/chat"
                    className="px-8 py-4 text-lg font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
                  >
                    Go to Chat
                  </Link>
                ) : (
                  <>
                    <Link
                      href="/signup"
                      className="px-8 py-4 text-lg font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
                    >
                      Get Started Free
                    </Link>
                    <Link
                      href="/login"
                      className="px-8 py-4 text-lg font-medium text-gray-700 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Login
                    </Link>
                  </>
                )}
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
          How It Works
        </h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {/* Feature 1 */}
          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Just Ask
            </h3>
            <p className="text-gray-600">
              Type natural commands like "Add a task to buy groceries" or "Show
              me my incomplete tasks"
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              AI Understands
            </h3>
            <p className="text-gray-600">
              Our AI assistant understands context and intent, making task
              management feel like a conversation
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Instant Action
            </h3>
            <p className="text-gray-600">
              Tasks are created, updated, or completed instantly. No clicking
              through menus or forms
            </p>
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="container mx-auto px-4 py-16 bg-gray-50">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
          What You Can Do
        </h2>

        <div className="max-w-3xl mx-auto space-y-6">
          {/* Capability 1 */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold">+</span>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">
                  Create Tasks
                </h4>
                <p className="text-gray-600 mb-2">
                  "Add a task to buy groceries tomorrow"
                </p>
                <p className="text-sm text-gray-500 italic">
                  AI creates task with title and optional due date
                </p>
              </div>
            </div>
          </div>

          {/* Capability 2 */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">✓</span>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">
                  List Tasks
                </h4>
                <p className="text-gray-600 mb-2">
                  "What tasks do I have?" or "Show me incomplete tasks"
                </p>
                <p className="text-sm text-gray-500 italic">
                  AI retrieves and displays your tasks in a readable format
                </p>
              </div>
            </div>
          </div>

          {/* Capability 3 */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-bold">✓</span>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">
                  Complete Tasks
                </h4>
                <p className="text-gray-600 mb-2">
                  "I finished buying groceries"
                </p>
                <p className="text-sm text-gray-500 italic">
                  AI identifies and marks the task as complete
                </p>
              </div>
            </div>
          </div>

          {/* Capability 4 */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <span className="text-yellow-600 font-bold">✎</span>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">
                  Update Tasks
                </h4>
                <p className="text-gray-600 mb-2">
                  "Rename 'Buy groceries' to 'Buy groceries and snacks'"
                </p>
                <p className="text-sm text-gray-500 italic">
                  AI updates task details as requested
                </p>
              </div>
            </div>
          </div>

          {/* Capability 5 */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-red-600 font-bold">×</span>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-1">
                  Delete Tasks
                </h4>
                <p className="text-gray-600 mb-2">
                  "Delete the groceries task"
                </p>
                <p className="text-sm text-gray-500 italic">
                  AI asks for confirmation before deleting
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      {!isPending && !session?.user && (
        <section className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto bg-blue-600 rounded-2xl p-12 text-center text-white shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-xl mb-8 text-blue-100">
              Join thousands of users managing tasks with natural language
            </p>
            <Link
              href="/signup"
              className="inline-block px-8 py-4 text-lg font-medium text-blue-600 bg-white rounded-lg hover:bg-gray-100 transition-colors shadow-lg"
            >
              Sign Up Free
            </Link>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8">
        <div className="container mx-auto px-4 text-center">
          <p>© 2024 AI Todo Assistant. Built with Next.js and OpenAI.</p>
        </div>
      </footer>
    </div>
  );
}
