'use client';

import React from 'react';

interface ClearButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

export function ClearButton({ onClick, disabled = false }: ClearButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        px-4 py-2 rounded-lg font-medium text-sm
        transition-all duration-300
        ${
          disabled
            ? 'bg-green-300 text-green-600 cursor-not-allowed'
            : 'bg-green-500 text-white hover:bg-green-600 active:scale-95'
        }
      `}
    >
      ➕ New Chat
    </button>
  );
}
