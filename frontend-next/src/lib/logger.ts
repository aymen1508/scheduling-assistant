/**
 * Logging utility with prefixes for debugging
 */

const debugLogsEnabled = process.env.NEXT_PUBLIC_DEBUG_LOGS === 'true';
const verboseAudioLogsEnabled = process.env.NEXT_PUBLIC_DEBUG_AUDIO === 'true';

export function log(message: string, prefix: string = '📍') {
  if (debugLogsEnabled) {
    console.log(`${prefix} ${message}`);
  }
}

export function logSuccess(message: string) {
  if (debugLogsEnabled) {
    console.log(`✅ ${message}`);
  }
}

export function logError(message: string) {
  console.error(`❌ ${message}`);
}

export function logInfo(message: string) {
  if (debugLogsEnabled) {
    console.info(`ℹ️ ${message}`);
  }
}

export function logWarning(message: string) {
  console.warn(`⚠️ ${message}`);
}

export function logAudio(message: string) {
  if (verboseAudioLogsEnabled) {
    console.log(`🎵 ${message}`);
  }
}

export function logWebSocket(message: string) {
  if (debugLogsEnabled) {
    console.log(`📡 ${message}`);
  }
}

export function logMicrophone(message: string) {
  if (verboseAudioLogsEnabled) {
    console.log(`🎤 ${message}`);
  }
}

export function logChat(message: string) {
  if (debugLogsEnabled) {
    console.log(`💬 ${message}`);
  }
}
