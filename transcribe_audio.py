from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
import os
import wave
import contextlib
import tempfile
import subprocess
from dotenv import load_dotenv
from google_creds import credentials

# Load environment variables
load_dotenv()

# Initialize Google Cloud clients
speech_client = speech.SpeechClient(credentials=credentials)
translate_client = translate.Client(credentials=credentials)

def transcribe_audio(audio_file, language='en-US', retry_with_enhanced=True, convert_sample_rate=True):
    """
    Transcribe audio using Google Cloud Speech-to-Text with specified language
    
    Args:
        audio_file: Path to audio file
        language: Language code to use for transcription (e.g. 'en-US', 'hi-IN')
        retry_with_enhanced: Whether to retry with enhanced model if initial attempt fails
        convert_sample_rate: Whether to convert sample rate to match Google's recommended rate
    
    Returns:
        transcript or None if failed
    """
    try:
        # Get audio info and convert if needed
        with contextlib.closing(wave.open(audio_file, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        
        # If needed, convert audio to 16kHz (Google's preferred sample rate)
        working_audio_file = audio_file
        if convert_sample_rate and rate != 16000:
            fd, working_audio_file = tempfile.mkstemp(suffix='.wav')
            os.close(fd)
            
            subprocess.call([
                'ffmpeg', '-y', '-i', audio_file, 
                '-ar', '16000', '-ac', '1', 
                working_audio_file
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Converted audio to 16kHz for optimal transcription")
        
        with open(working_audio_file, "rb") as f:
            audio_content = f.read()
        
        audio = speech.RecognitionAudio(content=audio_content)
        
        # Configure Speech-to-Text with the user-selected language
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language,  # Use the selected language
            enable_automatic_punctuation=True,
            model="latest_long" if duration > 60 else "command_and_search",
            use_enhanced=True,
            enable_word_confidence=True if duration < 60 else False,
        )
        
        print(f"Transcribing with language: {language}")
        response = speech_client.recognize(config=config, audio=audio)
        
        # Clean up temp file if created
        if working_audio_file != audio_file:
            os.remove(working_audio_file)
            
        if not response.results:
            print("No speech detected in the audio.")
            
            # Retry with different settings if first attempt failed
            if retry_with_enhanced and not config.use_enhanced:
                print("Retrying with enhanced speech recognition...")
                config.use_enhanced = True
                response = speech_client.recognize(config=config, audio=audio)
                if not response.results:
                    return None
            else:
                return None

        # Process results
        transcript = ""
        highest_confidence = 0
        
        for result in response.results:
            if result.alternatives:
                current_transcript = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence
                
                print(f"🎤 Partial Transcription: {current_transcript}")
                print(f"🔍 Confidence: {confidence}")
                
                # Keep track of the highest confidence result
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    transcript = current_transcript
                
                # Accept high confidence result immediately
                if confidence > 0.8:
                    break
        
        if not transcript:
            print("No valid transcription results found.")
            return None
        
        print(f"🎤 Final Transcription: {transcript}")
        print(f"✅ Confidence: {highest_confidence}")
        print(f"🌍 Using Language: {language}")
        
        return transcript
            
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        if 'working_audio_file' in locals() and working_audio_file != audio_file and os.path.exists(working_audio_file):
            os.remove(working_audio_file)
        return None

if __name__ == "__main__":
    audio_file = "test_audio.wav"  # Replace with your test file
    transcript = transcribe_audio(audio_file, language="en-US")
    if transcript:
        print(f"Final Output - Transcript: {transcript}")
    else:
        print("Transcription failed.")