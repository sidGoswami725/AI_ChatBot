import pyaudio
import wave
import numpy as np
import time
import audioop
from scipy import signal

def record_audio(filename, max_duration=30, silence_threshold=500, silence_duration=2.0):
    """
    Record audio with voice activity detection and noise reduction
    
    Args:
        filename: Output audio file path
        max_duration: Maximum recording duration in seconds
        silence_threshold: Amplitude threshold to detect silence
        silence_duration: Duration of silence (in seconds) to stop recording
    """
    # Higher quality audio settings
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100  # Increased from 16000 for better quality
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                    input=True, frames_per_buffer=CHUNK)
    
    print("Listening... (speak now)")
    
    # For silence detection
    silent_chunks = 0
    silent_threshold = silence_duration * (RATE / CHUNK)
    
    frames = []
    recording_started = False
    start_time = time.time()
    
    try:
        while True:
            # Check if max duration exceeded
            if time.time() - start_time > max_duration:
                print("Maximum recording duration reached")
                break
                
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Calculate audio level
            rms = audioop.rms(data, 2)
            
            # Voice activity detection
            if not recording_started and rms > silence_threshold:
                print("Recording started...")
                recording_started = True
                
            # Silence detection to end recording
            if recording_started:
                if rms < silence_threshold:
                    silent_chunks += 1
                    if silent_chunks > silent_threshold:
                        print("Silence detected, stopping recording")
                        break
                else:
                    silent_chunks = 0
    except KeyboardInterrupt:
        print("Recording stopped manually")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    if not recording_started or len(frames) < RATE // CHUNK:  # Less than 1 second of audio
        print("No speech detected, recording cancelled")
        return False
    
    # Apply preprocessing to improve audio quality
    audio_data = preprocess_audio(b''.join(frames), RATE, p.get_sample_size(FORMAT))
    
    # Save the processed audio
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(audio_data)
    wf.close()
    
    print(f"Recording finished and saved to {filename}")
    return True

def preprocess_audio(audio_bytes, sample_rate, sample_width):
    """Apply audio preprocessing to improve speech recognition quality"""
    # Convert bytes to numpy array
    audio = np.frombuffer(audio_bytes, dtype=np.int16)
    
    # Normalize audio
    audio = audio / np.max(np.abs(audio))
    
    # Apply noise reduction using a simple high-pass filter
    # This helps remove low-frequency background noise
    b, a = signal.butter(5, 80/(sample_rate/2), 'highpass')
    filtered_audio = signal.filtfilt(b, a, audio)
    
    # Apply a gentle low-pass filter to reduce high-frequency noise
    b, a = signal.butter(5, 8000/(sample_rate/2), 'lowpass')
    filtered_audio = signal.filtfilt(b, a, filtered_audio)
    
    # Convert back to the original scale
    filtered_audio = (filtered_audio * 32767).astype(np.int16)
    
    # Convert back to bytes
    return filtered_audio.tobytes()