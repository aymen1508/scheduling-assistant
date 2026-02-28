'use client';

import React from 'react';
import { ChatMessage as ChatMessageType } from '@/types';
import { formatTime } from '@/lib/audio';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isTool = message.role === 'tool';

  if (isTool) {
    return (
      <div className="mb-3 flex justify-start">
        <div className="max-w-sm bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg px-3 py-2 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">⚙️</span>
            <div>
              <div className="text-xs font-bold text-purple-700">
                {message.toolName || 'Tool'}
              </div>
              <div className="text-xs text-purple-600">
                {message.toolServer || 'MCP'}
              </div>
            </div>
          </div>
          <p className="text-xs text-gray-700 break-words bg-white bg-opacity-50 px-2 py-1 rounded mt-1">
            {message.content}
          </p>
          <div className="text-xs text-purple-500 mt-1">
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`mb-4 flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-sm rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-none shadow-lg'
            : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-900 rounded-bl-none shadow-md'
        }`}
      >
        <div className="text-xs font-bold mb-1 opacity-75">
          {isUser ? '👤 You' : '🤖 Assistant'}
        </div>
        <p className="text-sm break-words leading-relaxed">{message.content}</p>
        <div className={`text-xs mt-2 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
}

interface ChatPanelProps {
  messages: ChatMessageType[];
  isLoading?: boolean;
}

export function ChatPanel({ messages, isLoading = false }: ChatPanelProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  React.useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto bg-gradient-to-b from-gray-50 to-white rounded-lg shadow-inner p-6 space-y-2"
    >
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <div className="text-6xl mb-4 opacity-30">💬</div>
            <p className="text-lg font-medium text-gray-500">No messages yet</p>
            <p className="text-sm text-gray-400 mt-2">Start recording to begin your conversation</p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gradient-to-r from-gray-100 to-gray-200 text-gray-900 rounded-2xl rounded-bl-none px-4 py-3 shadow-md">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce animation-delay-100"></div>
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce animation-delay-200"></div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
