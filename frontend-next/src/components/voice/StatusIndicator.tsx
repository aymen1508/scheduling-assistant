'use client';

import React from 'react';

interface StatusIndicatorProps {
  isConnected: boolean;
  status: string;
  error?: string | null;
}

export function StatusIndicator({ isConnected, status, error }: StatusIndicatorProps) {
  return (
    <div className="flex items-center gap-3">
      {/* Status Dot */}
      <div className="relative">
        <div
          className={`w-4 h-4 rounded-full ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`}
        />
        {isConnected && (
          <div className="absolute inset-0 bg-green-500 rounded-full animate-pulse"></div>
        )}
      </div>

      {/* Status Text */}
      <div className="flex flex-col">
        <span className="text-sm font-semibold text-gray-700">
          {isConnected ? '✅ Connected' : '❌ Disconnected'}
        </span>
        {error && (
          <span className="text-xs text-red-600 mt-0.5">
            {error}
          </span>
        )}
      </div>
    </div>
  );
}
