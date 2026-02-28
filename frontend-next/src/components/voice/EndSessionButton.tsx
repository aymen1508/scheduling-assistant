'use client';

import React from 'react';

interface EndSessionButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

export function EndSessionButton({ onClick, disabled = false }: EndSessionButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        px-4 py-2 rounded-lg font-medium text-sm
        transition-all duration-300
        ${
          disabled
            ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
            : 'bg-red-500 text-white hover:bg-red-600 active:scale-95'
        }
      `}
    >
      🚪 Exit
    </button>
  );
}
