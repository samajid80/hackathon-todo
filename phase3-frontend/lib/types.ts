/**
 * TypeScript type definitions for Phase 3 Frontend.
 *
 * Defines types for conversations, messages, tasks, and API responses.
 */

// Conversation types
export interface Conversation {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  tool_calls?: ToolCall[];
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result?: any;
  error?: string;
}

// Task types (from Phase 2)
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

// API request types
export interface SendMessageRequest {
  conversation_id?: string;
  message: string;
}

export interface SendMessageResponse {
  conversation_id: string;
  user_message: Message;
  assistant_message: Message;
  tool_calls?: ToolCall[];
}

export interface GetConversationHistoryResponse {
  conversation_id: string;
  messages: Message[];
}

export interface ListConversationsResponse {
  conversations: Conversation[];
}

// API error type
export interface APIError {
  detail: string;
  status?: number;
}
