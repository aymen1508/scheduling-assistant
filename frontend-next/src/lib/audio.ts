/**
 * Utility functions for audio processing
 */

/**
 * Resample audio from one sample rate to another
 * Using simple linear interpolation for quality resampling
 */
export function resampleAudio(
  audioData: Float32Array,
  fromRate: number,
  toRate: number
): Float32Array {
  if (fromRate === toRate) {
    return audioData;
  }

  const ratio = toRate / fromRate;
  const newLength = Math.ceil(audioData.length * ratio);
  const resampled = new Float32Array(newLength);

  // Linear interpolation resampling
  for (let i = 0; i < newLength; i++) {
    const srcIndex = i / ratio;
    const srcIndexFloor = Math.floor(srcIndex);
    const srcIndexFraction = srcIndex - srcIndexFloor;

    if (srcIndexFloor + 1 < audioData.length) {
      // Linear interpolation between two samples
      resampled[i] =
        audioData[srcIndexFloor] * (1 - srcIndexFraction) +
        audioData[srcIndexFloor + 1] * srcIndexFraction;
    } else {
      // Use last sample for edge case
      resampled[i] = audioData[srcIndexFloor];
    }
  }

  return resampled;
}

/**
 * Convert Float32Array to Int16Array (PCM16)
 */
export function float32ToInt16(float32Array: Float32Array): Int16Array {
  const int16Array = new Int16Array(float32Array.length);
  
  for (let i = 0; i < float32Array.length; i++) {
    const sample = Math.max(-1, Math.min(1, float32Array[i]));
    int16Array[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
  }
  
  return int16Array;
}

/**
 * Light voice preprocessing for better transcription robustness:
 * - Remove DC offset
 * - Apply gentle auto-gain toward target RMS
 * - Hard-limit to prevent clipping
 */
export function processVoiceChunk(input: Float32Array): Float32Array {
  if (input.length === 0) return input;

  const output = new Float32Array(input.length);

  let mean = 0;
  for (let i = 0; i < input.length; i++) {
    mean += input[i];
  }
  mean /= input.length;

  let rms = 0;
  for (let i = 0; i < input.length; i++) {
    const sample = input[i] - mean;
    rms += sample * sample;
  }
  rms = Math.sqrt(rms / input.length);

  const targetRms = 0.12;
  const minRms = 0.003;
  const maxGain = 4.0;
  const gain = rms > minRms ? Math.min(targetRms / rms, maxGain) : 1.0;

  for (let i = 0; i < input.length; i++) {
    let sample = (input[i] - mean) * gain;

    if (sample > 0.98) sample = 0.98;
    if (sample < -0.98) sample = -0.98;

    output[i] = sample;
  }

  return output;
}

/**
 * Convert Int16Array (PCM16) to Float32Array
 */
export function int16ToFloat32(int16Array: Int16Array): Float32Array {
  const float32Array = new Float32Array(int16Array.length);
  
  for (let i = 0; i < int16Array.length; i++) {
    const int16 = int16Array[i];
    float32Array[i] = int16 < 0x8000 ? int16 / 0x7fff : (int16 - 0x10000) / 0x8000;
  }
  
  return float32Array;
}

/**
 * Convert binary string to base64
 */
export function binaryStringToBase64(binaryString: string): string {
  return btoa(binaryString);
}

/**
 * Convert base64 to binary string
 */
export function base64ToBinaryString(base64String: string): string {
  return atob(base64String);
}

/**
 * Convert Uint8Array to binary string
 */
export function uint8ArrayToBinaryString(uint8Array: Uint8Array): string {
  let binaryString = '';
  for (let i = 0; i < uint8Array.length; i++) {
    binaryString += String.fromCharCode(uint8Array[i]);
  }
  return binaryString;
}

/**
 * Convert binary string to Uint8Array
 */
export function binaryStringToUint8Array(binaryString: string): Uint8Array {
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

/**
 * Convert base64 audio to playable audio buffer
 */
export function base64ToAudioBuffer(
  base64Audio: string,
  audioContext: AudioContext,
  sampleRate: number = 24000
): AudioBuffer {
  const binaryString = base64ToBinaryString(base64Audio);
  const bytes = binaryStringToUint8Array(binaryString);

  // Create audio buffer
  const channels = 1;
  const audioBuffer = audioContext.createBuffer(channels, bytes.length / 2, sampleRate);
  const float32Data = audioBuffer.getChannelData(0);

  // Convert int16 to float32
  const int16Array = new Int16Array(bytes.buffer);
  const float32Array = int16ToFloat32(int16Array);

  float32Data.set(float32Array);

  return audioBuffer;
}

/**
 * Generate a unique message ID
 */
export function generateMessageId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Format timestamp to readable time
 */
export function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });
}
