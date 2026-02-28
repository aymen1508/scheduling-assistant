/**
 * AudioWorklet Processor for real-time audio processing
 * This runs in a separate audio thread for better performance
 */

class AudioProcessorWorklet extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (input && input.length > 0) {
      const channelData = input[0];
      const audioCopy = new Float32Array(channelData.length);
      audioCopy.set(channelData);
      // Post the audio data to the main thread
      this.port.postMessage({
        type: 'audioData',
        data: audioCopy,
      });
    }
    return true; // Keep the processor running
  }
}

registerProcessor('audio-processor', AudioProcessorWorklet);
