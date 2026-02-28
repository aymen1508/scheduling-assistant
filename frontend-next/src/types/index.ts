/**
 * Type definitions for the Voice Assistant application
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'tool';
  content: string;
  timestamp: number;
  toolName?: string;
  toolServer?: string;
}

export interface ConnectionStatus {
  isConnected: boolean;
  isRecording: boolean;
  status: string;
  error?: string;
}

export interface WebSocketMessage {
  type: 'status' | 'chat' | 'audio' | 'error' | 'interrupt' | 'tool';
  data: any;
}

export interface ChatData {
  role: 'user' | 'assistant';
  content: string;
}

export interface AudioChunk {
  data: string; // base64 encoded
  timestamp: number;
}
