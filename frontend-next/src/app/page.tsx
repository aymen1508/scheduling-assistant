'use client';

import React, { useEffect, useState } from 'react';
import { useVoiceAssistant } from '@/hooks/useVoiceAssistant';
import { ChatPanel } from '@/components/voice/ChatPanel';
import { RecordButton } from '@/components/voice/RecordButton';
import { ClearButton } from '@/components/voice/ClearButton';
import { EndSessionButton } from '@/components/voice/EndSessionButton';
import { StatusIndicator } from '@/components/voice/StatusIndicator';

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const voiceAssistant = useVoiceAssistant();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">🎙️</div>
          <p className="text-gray-600 text-lg font-semibold">Initializing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-2xl h-screen max-h-[90vh] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 shadow-lg">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            🎙️ Voice Assistant
          </h1>
          <StatusIndicator
            isConnected={voiceAssistant.isConnected}
            status={voiceAssistant.status}
            error={voiceAssistant.error}
          />
        </div>

        {/* Chat Panel */}
        <ChatPanel
          messages={voiceAssistant.messages}
          isLoading={voiceAssistant.isRecording}
        />

        {/* Controls */}
        <div className="bg-gray-50 border-t border-gray-200 p-6 flex gap-4 items-center justify-between">
          <div className="flex gap-3">
            <RecordButton
              isRecording={voiceAssistant.isRecording}
              isConnected={voiceAssistant.isConnected}
              onClick={voiceAssistant.toggleRecording}
            />
            <ClearButton
              onClick={voiceAssistant.clearMessages}
              disabled={!voiceAssistant.isConnected}
            />
            <EndSessionButton
              onClick={voiceAssistant.endSession}
              disabled={!voiceAssistant.isConnected && !voiceAssistant.isRecording}
            />
          </div>

          {/* Connection Status */}
          {!voiceAssistant.isConnected && (
            <div className="text-sm text-yellow-600 font-semibold">
              Connecting...
            </div>
          )}

          {/* Recording Indicator */}
          {voiceAssistant.isRecording && (
            <div className="flex items-center gap-2 text-red-500 font-semibold animate-pulse">
              <span className="w-2 h-2 bg-red-500 rounded-full"></span>
              Recording...
            </div>
          )}
        </div>

        {/* Error Banner */}
        {voiceAssistant.error && (
          <div className="bg-red-50 border-t border-red-200 p-4">
            <div className="flex items-start gap-3">
              <span className="text-xl">⚠️</span>
              <div>
                <p className="text-sm font-semibold text-red-800">Error</p>
                <p className="text-sm text-red-700">{voiceAssistant.error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
