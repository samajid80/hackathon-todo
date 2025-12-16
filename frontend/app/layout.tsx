/**
 * Root layout component
 *
 * This is the main layout that wraps all pages in the application.
 * It includes:
 * - Global styles (Tailwind CSS)
 * - Metadata for SEO
 * - Error Boundary for graceful error handling (T139)
 * - Toast Provider for notifications (T140)
 * - Navbar with authentication (T038)
 * - Responsive layout structure
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/globals.css";
import { Navbar } from "@/components/Navbar";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ToastProvider } from "@/lib/toast-context";
import { ToastContainer } from "@/components/Toast";
import { ToastRenderer } from "@/components/ToastRenderer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    default: "Hackathon Todo - Organize Your Tasks Effortlessly",
    template: "%s | Hackathon Todo",
  },
  description:
    "A modern, secure task management application built for productivity and simplicity. Manage tasks efficiently with powerful filtering, sorting, and secure authentication.",
  keywords: [
    "task management",
    "todo app",
    "productivity",
    "task organizer",
    "secure todo",
    "Next.js",
    "React",
    "full-stack",
  ],
  authors: [{ name: "Hackathon Todo Team" }],
  creator: "Hackathon Todo Team",
  publisher: "Hackathon Todo",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://hackathon-todo.vercel.app",
    title: "Hackathon Todo - Organize Your Tasks Effortlessly",
    description:
      "A modern, secure task management application built for productivity and simplicity.",
    siteName: "Hackathon Todo",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Hackathon Todo - Task Management App",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Hackathon Todo - Organize Your Tasks Effortlessly",
    description:
      "A modern, secure task management application built for productivity and simplicity.",
    images: ["/og-image.png"],
    creator: "@hackathontodo",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ErrorBoundary>
          <ToastProvider>
            <div className="min-h-screen bg-gray-50 flex flex-col">
              {/* Navigation with user session (T038) */}
              <Navbar />

              {/* Main content */}
              <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
                {children}
              </main>

              {/* Footer */}
              <footer className="bg-white border-t border-gray-200 mt-auto">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                  <p className="text-center text-sm text-gray-500">
                    Built with Next.js 16 and FastAPI
                  </p>
                </div>
              </footer>
            </div>

            {/* Toast notifications renderer (T140) */}
            <ToastRenderer />
          </ToastProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
