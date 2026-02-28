'use client';

import React from 'react';

interface RecordButtonProps {
  isRecording: boolean;
  isConnected: boolean;
  onClick: () => void;
  isLoading?: boolean;
}

export function RecordButton({
  isRecording,
  isConnected,
  onClick,
  isLoading = false,
}: RecordButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={!isConnected || isLoading}
      className={`
        relative px-6 py-3 rounded-lg font-semibold text-white
        transition-all duration-300 transform
        disabled:opacity-50 disabled:cursor-not-allowed
        ${
          isRecording
            ? 'bg-red-500 hover:bg-red-600 shadow-lg hover:shadow-xl animate-pulse-ring'
            : 'bg-blue-500 hover:bg-blue-600 shadow-md hover:shadow-lg hover:scale-105'
        }
      `}
    >
      <span className="flex items-center gap-2">
        {isRecording ? (
          <>
            <span className="animate-pulse">🔴</span>
            Stop Recording
          </>
        ) : (
          <>
            <span>🎤</span>
            Start Recording
          </>
        )}
      </span>
    </button>
  );
}
