'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { ChatMessage, WebSocketMessage, ChatData } from '@/types';
import {
  float32ToInt16,
  binaryStringToBase64,
  uint8ArrayToBinaryString,
  base64ToAudioBuffer,
  generateMessageId,
  resampleAudio,
  processVoiceChunk,
} from '@/lib/audio';
import {
  logWebSocket,
  logMicrophone,
  logAudio,
  logChat,
  logError,
  logSuccess,
  logInfo,
  logWarning,
} from '@/lib/logger';

interface PlaybackAudioState {
  audioContext: globalThis.AudioContext | null;
  audioQueue: string[];
  isPlaying: boolean;
}

interface UseVoiceAssistantOptions {
  wsUrl?: string;
}

export function useVoiceAssistant(options: UseVoiceAssistantOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState('Disconnected');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const endingSessionRef = useRef(false);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<AudioWorkletNode | null>(null);
  const captureAudioContextRef = useRef<AudioContext | null>(null);
  const pendingCaptureBufferRef = useRef<Float32Array>(new Float32Array(0));
  const audioContextRef = useRef<PlaybackAudioState>({
    audioContext: null,
    audioQueue: [],
    isPlaying: false,
  });

  const wsUrl = options.wsUrl || process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws/voice';
  const TARGET_SAMPLE_RATE = 24000;
  const CAPTURE_FRAME_SAMPLES = 2400; // 100ms @ 24kHz

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = async () => {
      try {
        // Detect user's timezone
        let timezoneInfo: { timezone: string; offset: string } | null = null;
        
        try {
          logInfo('Detecting timezone from public IP...');
          const response = await fetch('https://api.ipify.org?format=json', { method: 'GET' });
          if (response.ok) {
            const { ip } = await response.json();
            const tzResponse = await fetch(`https://ip-api.com/json/${ip}?fields=timezone,status`);
            if (tzResponse.ok) {
              const tzData = await tzResponse.json();
              if (tzData.status === 'success' && tzData.timezone) {
                timezoneInfo = { timezone: tzData.timezone, offset: new Date().toLocaleString('en-US', { timeZoneName: 'short' }).split(' ').pop() || '' };
                logInfo(`Timezone detected: ${timezoneInfo.timezone}`);
              }
            }
          }
        } catch (err) {
          logWarning(`Timezone detection failed, will use backend timezone: ${err}`);
        }

        logWebSocket(`Attempting to connect to ${wsUrl}`);
        const ws = new WebSocket(wsUrl);
        
        // Connection timeout (10 seconds)
        const connectionTimeout = setTimeout(() => {
          if (ws.readyState === WebSocket.CONNECTING) {
            logError(`WebSocket connection timeout - backend not responding at ${wsUrl}`);
            ws.close();
            setIsConnected(false);
            setStatus('Connection timeout - backend not responding');
            setError(`Could not connect to backend at ${wsUrl}`);
          }
        }, 10000);

        ws.onopen = () => {
          clearTimeout(connectionTimeout);
          endingSessionRef.current = false;
          logSuccess('Connected to backend');
          setIsConnected(true);
          setStatus('Connected. Ready to record.');
          setError(null);

          // Send timezone info if detected
          if (timezoneInfo) {
            try {
              ws.send(JSON.stringify({ type: 'timezone_info', timezone: timezoneInfo.timezone }));
              logInfo(`Sent timezone to backend: ${timezoneInfo.timezone}`);
            } catch (err) {
              logWarning(`Failed to send timezone: ${err}`);
            }
          }
        };

        ws.onmessage = (event) => {
          logWebSocket('Message received');
          try {
            const message = JSON.parse(event.data) as WebSocketMessage;
            handleMessage(message);
          } catch (err) {
            logError(`Failed to parse message: ${err}`);
          }
        };

        ws.onerror = () => {
          clearTimeout(connectionTimeout);
          logError('WebSocket error');
          setIsConnected(false);
          setStatus('Connection error - backend not running?');
          setError('Failed to connect to backend');
        };

        ws.onclose = () => {
          logWarning('Disconnected from backend');
          setIsConnected(false);
          if (!endingSessionRef.current) {
            setStatus('Disconnected');
          }
        };

        wsRef.current = ws;
      } catch (err) {
        logError(`Failed to connect: ${err}`);
        setStatus('Failed to connect to backend');
        setError(String(err));
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [wsUrl]);

  const handleMessage = (message: WebSocketMessage) => {
    logWebSocket(`Received: ${message.type}`);

    switch (message.type) {
      case 'status':
        logInfo(`Status: ${message.data}`);
        setStatus(message.data);
        break;

      case 'chat':
        const chatData = message.data as ChatData;
        logChat(`${chatData.role}: ${chatData.content?.substring(0, 50) || 'N/A'}...`);
        setMessages((prev) => [
          ...prev,
          {
            id: generateMessageId(),
            role: chatData.role,
            content: chatData.content,
            timestamp: Date.now(),
          },
        ]);
        break;

      case 'tool':
        const toolData = message.data;
        logInfo(`Tool: ${toolData.toolName} (${toolData.toolServer})`);
        setMessages((prev) => [
          ...prev,
          {
            id: generateMessageId(),
            role: 'tool',
            content: toolData.result,
            toolName: toolData.toolName,
            toolServer: toolData.toolServer,
            timestamp: Date.now(),
          },
        ]);
        break;

      case 'audio':
        logAudio(`Received audio chunk (${message.data.length} chars)`);
        queueAudioChunk(message.data);
        break;

      case 'interrupt':
        logInfo('Playback interrupted - user started speaking');
        clearAudioQueue();
        break;

      case 'error':
        if (typeof message.data === 'string' && message.data.toLowerCase().includes('buffer too small')) {
          logWarning(`Ignoring non-critical error: ${message.data}`);
          setStatus('Awaiting next input');
          return;
        }
        logError(message.data);
        setError(message.data);
        break;

      default:
        logWarning(`Unknown message type: ${message.type}`);
    }
  };

  const clearAudioQueue = () => {
    const ctx = audioContextRef.current;
    ctx.audioQueue = [];
    ctx.isPlaying = false;
    logInfo('Audio queue cleared for interruption');
  };

  const queueAudioChunk = (base64Audio: string) => {
    audioContextRef.current.audioQueue.push(base64Audio);
    playNextChunk();
  };

  const playNextChunk = useCallback(async () => {
    const ctx = audioContextRef.current;
    if (ctx.audioQueue.length === 0 || ctx.isPlaying) return;

    logAudio(`Audio queue: ${ctx.audioQueue.length} chunks waiting`);
    ctx.isPlaying = true;
    const base64Audio = ctx.audioQueue.shift() || '';

    try {
      // Create or get AudioContext (lazily on first audio)
      if (!ctx.audioContext) {
        ctx.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        logSuccess('AudioContext created');
      }

      const audioContext = ctx.audioContext;

      // Resume context if suspended (browser security requirement)
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
        logSuccess('AudioContext resumed');
      }

      // Decode and play audio
      const audioBuffer = base64ToAudioBuffer(base64Audio, audioContext, 24000);

      logAudio(
        `Playing audio: ${audioBuffer.length} samples (${(
          (audioBuffer.length / 24000) *
          1000
        ).toFixed(1)}ms)`
      );

      // Play the audio
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);

      source.onended = () => {
        logSuccess('Audio chunk finished playing');
        ctx.isPlaying = false;
        playNextChunk();
      };

      source.start(0);
    } catch (err) {
      logError(`Audio playback error: ${err}`);
      ctx.isPlaying = false;
      playNextChunk();
    }
  }, []);

  const startRecording = useCallback(async () => {
    try {
      logMicrophone('Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;
      logSuccess('Microphone access granted');

      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      captureAudioContextRef.current = audioContext;
      logSuccess(`AudioContext sample rate: ${audioContext.sampleRate} Hz`);
      const source = audioContext.createMediaStreamSource(stream);

      // Load and use AudioWorkletNode (modern approach)
      await audioContext.audioWorklet.addModule('/audio-processor.js');
      const processor = new AudioWorkletNode(audioContext, 'audio-processor');
      const muteGainNode = audioContext.createGain();
      muteGainNode.gain.value = 0;

      source.connect(processor);
      processor.connect(muteGainNode);
      muteGainNode.connect(audioContext.destination);

      // Handle audio messages from the worklet
      processor.port.onmessage = (event) => {
        if (event.data.type === 'audioData') {
          // Resample from native rate to 24kHz if needed
          const audioData = event.data.data as Float32Array;

          const resampled = audioContext.sampleRate !== TARGET_SAMPLE_RATE
            ? resampleAudio(audioData, audioContext.sampleRate, TARGET_SAMPLE_RATE)
            : audioData;

          const processed = processVoiceChunk(resampled);

          const pending = pendingCaptureBufferRef.current;
          const merged = new Float32Array(pending.length + processed.length);
          merged.set(pending, 0);
          merged.set(processed, pending.length);

          let offset = 0;
          while (merged.length - offset >= CAPTURE_FRAME_SAMPLES) {
            const frame = merged.slice(offset, offset + CAPTURE_FRAME_SAMPLES);
            sendAudioChunk(frame);
            offset += CAPTURE_FRAME_SAMPLES;
          }

          pendingCaptureBufferRef.current = merged.slice(offset);
        }
      };

      processorRef.current = processor;
      setIsRecording(true);
      setStatus('Recording...');
      logMicrophone(`Recording started with AudioWorkletNode (${audioContext.sampleRate}Hz)`);
    } catch (err) {
      logError(`Failed to start recording: ${err}`);
      setStatus('Microphone access denied');
      setError(String(err));
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (processorRef.current) {
      processorRef.current.port.onmessage = null;
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (captureAudioContextRef.current) {
      captureAudioContextRef.current.close();
      captureAudioContextRef.current = null;
    }

    pendingCaptureBufferRef.current = new Float32Array(0);

    setIsRecording(false);
    if (!endingSessionRef.current) {
      setStatus('Processing your speech...');
    }

    if (!endingSessionRef.current && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'end_turn' }));
    }
  }, []);

  const sendAudioChunk = useCallback((audioData: Float32Array) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      if (endingSessionRef.current) {
        return;
      }
      logError(`WebSocket not ready (state=${wsRef.current?.readyState}), stopping recording`);
      stopRecording();
      return;
    }

    try {
      // Convert float32 to int16
      const int16Data = float32ToInt16(audioData);

      // Convert int16 to binary string then to Uint8Array
      const uint8Data = new Uint8Array(int16Data.buffer);
      const binaryString = uint8ArrayToBinaryString(uint8Data);
      const base64Audio = binaryStringToBase64(binaryString);

      logAudio(`Chunk: ${audioData.length} samples → ${int16Data.length} int16 → ${base64Audio.length} base64 chars`);

      // Send to backend
      wsRef.current.send(JSON.stringify({ type: 'audio', data: base64Audio }));
    } catch (err) {
      logError(`Failed to send audio chunk: ${err}`);
      stopRecording();
    }
  }, [stopRecording]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    logChat('Starting new conversation');
    
    // Notify backend to send greeting for new conversation
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify({ type: 'new_conversation' }));
        logInfo('New conversation requested');
      } catch (err) {
        logError(`Failed to send new_conversation: ${err}`);
      }
    }
  }, []);

  const endSession = useCallback(() => {
    endingSessionRef.current = true;

    if (isRecording) {
      stopRecording();
    }

    clearAudioQueue();

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'close' }));
      wsRef.current.close();
    }

    setIsConnected(false);
    setStatus('Session ended');
    setError(null);
    logInfo('Session ended by user');
  }, [isRecording, stopRecording]);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  return {
    // State
    isConnected,
    isRecording,
    status,
    messages,
    error,

    // Methods
    startRecording,
    stopRecording,
    toggleRecording,
    clearMessages,
    endSession,
  };
}
