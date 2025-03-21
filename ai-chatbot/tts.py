from dotenv import load_dotenv
import os
from google.cloud import texttospeech
from google.cloud import translate_v3 as translate
import re
import time
from pydub import AudioSegment
from google_creds import credentials

load_dotenv()

# Initialize Google Cloud TTS client
client = texttospeech.TextToSpeechClient(credentials=credentials)
translate_client = translate.TranslationServiceClient(credentials=credentials)

# Define which voices support SSML - this is a set you'll need to maintain
# Based on your error message, it appears Chirp3-HD voices might not support SSML
SSML_SUPPORTED_VOICES = {
    # Add voice names that support SSML here
    # For example: "en-US-Standard-D", "en-US-Wavenet-F"
    # If a voice is not in this set, we'll use plain text instead of SSML
}

def translate_text(text, target_language):
    try:
        parent = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global"
        response = translate_client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "target_language_code": target_language,
                "mime_type": "text/plain"
            }
        )
        translated_text = response.translations[0].translated_text
        print(f"Translated text: {translated_text}")
        return translated_text
    except Exception as e:
        print(f"Translation failed: {str(e)}")
        return text

def analyze_text_for_prosody(text):
    """
    Analyzes text and adds SSML markup for natural prosody including:
    - Pauses at commas, periods
    - Pitch changes for questions and exclamations (using prosody tags)
    - Natural emphasis on important words
    - Breathing patterns
    """
    # First clean up any existing SSML tags to avoid conflicts
    text = re.sub(r'<[^>]+>', '', text)
    
    # Add paragraph breaks for better phrasing
    text = re.sub(r'\n\s*\n', '\n</p><p>\n', text)
    text = f"<p>{text}</p>" if not text.startswith('<p>') else text
    
    # Add prosodic pauses for punctuation
    text = re.sub(r',\s*', ', <break time="200ms"/>', text)
    text = re.sub(r';\s*', '; <break time="300ms"/>', text)
    text = re.sub(r':\s*', ': <break time="250ms"/>', text)
    text = re.sub(r'\.\s+', '. <break time="400ms"/>', text)
    
    # Add emphasis to important words (common emphasis patterns)
    emphasis_words = ['must', 'critical', 'important', 'necessary', 'essential', 'key', 'vital']
    for word in emphasis_words:
        text = re.sub(rf'\b{word}\b', f'<emphasis level="moderate">{word}</emphasis>', text, flags=re.IGNORECASE)
    
    # Add vocal variety for questions and exclamations
    # Note: Using rate changes instead of pitch for broader compatibility
    questions = re.findall(r'[^.!?]*\?\s*', text)
    for q in questions:
        if q:
            # Instead of pitch change, use rate change for questions
            enhanced_q = q.replace('?', '<break time="100ms"/>?<break time="500ms"/>')
            text = text.replace(q, enhanced_q)
    
    exclamations = re.findall(r'[^.!?]*!\s*', text)
    for e in exclamations:
        if e:
            # Instead of pitch change, use rate and volume changes for exclamations
            enhanced_e = e.replace('!', '<break time="50ms"/>!<break time="500ms"/>')
            text = text.replace(e, enhanced_e)
    
    # Add breathing sounds at natural points
    text = re.sub(r'([.!?])\s+([A-Z])', r'\1 <break time="600ms"/><mark name="breath"/>\2', text)
    
    # Adjust speed for longer sentences (slowing down slightly for clarity)
    sentences = re.findall(r'[^.!?]*[.!?]', text)
    for s in sentences:
        word_count = len(s.split())
        if word_count > 15:  # For longer sentences
            enhanced_s = f'<prosody rate="95%">{s}</prosody>'
            text = text.replace(s, enhanced_s)
    
    # Wrap in speak tags for proper SSML
    text = f'<speak>{text}</speak>'
    
    # Remove duplicate or nested SSML tags
    text = text.replace('<speak><speak>', '<speak>')
    text = text.replace('</speak></speak>', '</speak>')
    
    return text

def add_dynamic_audio_effects(audio_segment, character="jax"):
    """
    Add character-specific audio effects to make the TTS more natural and unique
    """
    # Character-specific audio profiles
    character_profiles = {
        "jax": {"bass": 2.0, "treble": 1.0, "clarity": 1.5},
        "viktor": {"bass": 3.0, "treble": 0.8, "clarity": 1.2},
        "lila": {"bass": 0.8, "treble": 1.4, "clarity": 1.8},
        "elias": {"bass": 1.5, "treble": 1.2, "clarity": 1.3}
    }
    
    profile = character_profiles.get(character, character_profiles["jax"])
    
    # Apply bass boost
    if profile["bass"] > 1.0:
        # Simple equalization for bass frequencies (approximately 60-250Hz)
        filtered = audio_segment.low_pass_filter(250)
        filtered = filtered.apply_gain(profile["bass"] - 1.0)
        audio_segment = audio_segment.overlay(filtered)
    
    # Apply treble enhancement
    if profile["treble"] > 1.0:
        # Simple equalization for treble frequencies (approximately 2000-8000Hz)
        filtered = audio_segment.high_pass_filter(2000)
        filtered = filtered.apply_gain(profile["treble"] - 1.0)
        audio_segment = audio_segment.overlay(filtered)
    
    # Apply clarity enhancement through subtle compression
    if profile["clarity"] > 1.0:
        # Normalization to improve clarity
        audio_segment = audio_segment.normalize(headroom=0.1)
    
    # Add very subtle room ambience to make it sound less sterile
    room_noise = AudioSegment.silent(duration=len(audio_segment))
    room_noise = room_noise.overlay(
        AudioSegment.silent(duration=len(audio_segment)).apply_gain(-45)  # Reduced from -30 to -45 for subtlety
    )
    audio_segment = audio_segment.overlay(room_noise)
    
    return audio_segment

def add_natural_breathing(audio_segment):
    """
    Add natural breathing sounds at marked positions
    """
    # Create a simple breath sound (could be replaced with a pre-recorded breath sound)
    breath_duration = 300  # ms
    breath = AudioSegment.silent(duration=breath_duration)
    # Add a subtle breath sound
    breath = breath.apply_gain(-25)  # Very quiet breath
    
    # Create a new audio segment with breaths inserted at appropriate points
    new_audio = AudioSegment.empty()
    current_position = 0
    
    # In a real implementation, you would identify the markers and insert breaths
    # For now, we'll add subtle breaths at regular intervals (every ~5 seconds)
    interval = 5000  # ms
    
    while current_position < len(audio_segment):
        chunk_duration = min(interval, len(audio_segment) - current_position)
        chunk = audio_segment[current_position:current_position + chunk_duration]
        new_audio += chunk
        
        if current_position + chunk_duration < len(audio_segment):
            # Only add breath if we're not at the end
            new_audio += breath
        
        current_position += chunk_duration
    
    return new_audio

def text_to_speech(text, language_code, character="jax", output_file="output.mp3"):
    # Use the full language_code (e.g., "en-US") instead of splitting
    full_language_code = language_code  # e.g., "en-US", "hi-IN"
    
    # Define voice settings for each character with updated Chirp3-HD voices
    voice_settings = {
        "jax": {
            "name": (
                "hi-IN-Chirp3-HD-Fenrir" if full_language_code == "hi-IN" else
                "ta-IN-Chirp3-HD-Fenrir" if full_language_code == "ta-IN" else
                "kn-IN-Chirp3-HD-Fenrir" if full_language_code == "kn-IN" else
                "te-IN-Chirp3-HD-Fenrir" if full_language_code == "te-IN" else
                "ml-IN-Chirp3-HD-Fenrir" if full_language_code == "ml-IN" else
                "bn-IN-Chirp3-HD-Fenrir" if full_language_code == "bn-IN" else
                "mr-IN-Chirp3-HD-Fenrir" if full_language_code == "mr-IN" else
                "gu-IN-Chirp3-HD-Fenrir" if full_language_code == "gu-IN" else
                "pa-IN-Wavenet-B" if full_language_code == "pa-IN" else
                "ja-JP-Chirp3-HD-Fenrir" if full_language_code == "ja-JP" else
                "fr-FR-Chirp3-HD-Fenrir" if full_language_code == "fr-FR" else
                "de-DE-Chirp3-HD-Fenrir" if full_language_code == "de-DE" else
                "es-US-Chirp3-HD-Fenrir" if full_language_code == "es-US" else  # Mapping es-ES to es-US voice
                "en-US-Chirp3-HD-Fenrir" if full_language_code == "en-US" else
                "en-US-Chirp3-HD-Fenrir"  # Default fallback
            ),
            "gender": texttospeech.SsmlVoiceGender.MALE,
            "speaking_rate": 0.95
        },
        "viktor": {
            "name": (
                "hi-IN-Chirp3-HD-Puck" if full_language_code == "hi-IN" else
                "ta-IN-Chirp3-HD-Orus" if full_language_code == "ta-IN" else
                "kn-IN-Chirp3-HD-Orus" if full_language_code == "kn-IN" else
                "te-IN-Chirp3-HD-Puck" if full_language_code == "te-IN" else
                "ml-IN-Chirp3-HD-Puck" if full_language_code == "ml-IN" else
                "bn-IN-Chirp3-HD-Puck" if full_language_code == "bn-IN" else
                "mr-IN-Chirp3-HD-Puck" if full_language_code == "mr-IN" else
                "gu-IN-Chirp3-HD-Puck" if full_language_code == "gu-IN" else
                "pa-IN-Wavenet-D" if full_language_code == "pa-IN" else
                "ja-JP-Chirp3-HD-Charon" if full_language_code == "ja-JP" else
                "fr-FR-Chirp3-HD-Puck" if full_language_code == "fr-FR" else
                "de-DE-Chirp3-HD-Puck" if full_language_code == "de-DE" else
                "es-US-Chirp-HD-D" if full_language_code == "es-US" else
                "en-US-Chirp3-HD-Puck" if full_language_code == "en-US" else
                "en-US-Chirp3-HD-Puck"  # Default fallback
            ),
            "gender": texttospeech.SsmlVoiceGender.MALE,
            "speaking_rate": 0.9
        },
        "lila": {
            "name": (
                "hi-IN-Chirp3-HD-Aoede" if full_language_code == "hi-IN" else
                "ta-IN-Chirp3-HD-Leda" if full_language_code == "ta-IN" else
                "kn-IN-Chirp3-HD-Leda" if full_language_code == "kn-IN" else
                "te-IN-Chirp3-HD-Aoede" if full_language_code == "te-IN" else
                "ml-IN-Chirp3-HD-Aoede" if full_language_code == "ml-IN" else
                "bn-IN-Chirp3-HD-Aoede" if full_language_code == "bn-IN" else
                "mr-IN-Chirp3-HD-Aoede" if full_language_code == "mr-IN" else
                "gu-IN-Chirp3-HD-Aoede" if full_language_code == "gu-IN" else
                "pa-IN-Wavenet-A" if full_language_code == "pa-IN" else
                "ja-JP-Chirp3-HD-Aoede" if full_language_code == "ja-JP" else
                "fr-FR-Chirp3-HD-Aoede" if full_language_code == "fr-FR" else
                "de-DE-Chirp3-HD-Aoede" if full_language_code == "de-DE" else
                "es-US-Chirp-HD-F" if full_language_code == "es-US" else
                "en-US-Chirp3-HD-Aoede" if full_language_code == "en-US" else
                "en-US-Chirp3-HD-Aoede"  # Default fallback
            ),
            "gender": texttospeech.SsmlVoiceGender.FEMALE,
            "speaking_rate": 1.0
        },
        "elias": {
            "name": (
                "hi-IN-Chirp3-HD-Charon" if full_language_code == "hi-IN" else
                "ta-IN-Chirp3-HD-Charon" if full_language_code == "ta-IN" else
                "kn-IN-Chirp3-HD-Charon" if full_language_code == "kn-IN" else
                "te-IN-Chirp3-HD-Charon" if full_language_code == "te-IN" else
                "ml-IN-Chirp3-HD-Charon" if full_language_code == "ml-IN" else
                "bn-IN-Chirp3-HD-Charon" if full_language_code == "bn-IN" else
                "mr-IN-Chirp3-HD-Charon" if full_language_code == "mr-IN" else
                "gu-IN-Chirp3-HD-Charon" if full_language_code == "gu-IN" else
                "pa-IN-Wavenet-D" if full_language_code == "pa-IN" else
                "ja-JP-Chirp3-HD-Charon" if full_language_code == "ja-JP" else
                "fr-FR-Chirp3-HD-Charon" if full_language_code == "fr-FR" else
                "de-DE-Chirp3-HD-Charon" if full_language_code == "de-DE" else
                "es-US-Chirp3-HD-Charon" if full_language_code == "es-US" else
                "en-US-Chirp3-HD-Charon" if full_language_code == "en-US" else
                "en-US-Chirp3-HD-Charon"  # Default fallback
            ),
            "gender": texttospeech.SsmlVoiceGender.MALE,
            "speaking_rate": 0.92
        }
    }
    voice_params = voice_settings.get(character, voice_settings["jax"])
    
    # Get the selected voice name
    voice_name = voice_params["name"]
    
    # Check if the voice supports SSML
    supports_ssml = voice_name in SSML_SUPPORTED_VOICES
    
    try:
        # If the voice supports SSML, use prosodic text, otherwise use plain text
        if supports_ssml:
            prosodic_text = analyze_text_for_prosody(text)
            print(f"Using SSML with prosodic text for TTS: {prosodic_text}")
            synthesis_input = texttospeech.SynthesisInput(ssml=prosodic_text)
        else:
            # Clean text of any SSML tags just to be safe
            clean_text = re.sub(r'<[^>]+>', '', text)
            print(f"Using plain text for TTS (voice doesn't support SSML): {clean_text}")
            synthesis_input = texttospeech.SynthesisInput(text=clean_text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=full_language_code,
            name=voice_name,
            ssml_gender=voice_params["gender"]
        )
        
        # Enhanced audio config with better quality
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=voice_params["speaking_rate"],
            effects_profile_id=["headphone-class-device"],  # Higher quality audio profile
            sample_rate_hertz=24000  # Higher sample rate for better clarity
        )

        print(f"Using Google Cloud TTS with language: {full_language_code}, voice: {voice_name}")
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        temp_file = f"temp_output_{time.time()}.mp3"
        with open(temp_file, "wb") as out:
            out.write(response.audio_content)

        # Load with pydub for additional audio processing
        audio = AudioSegment.from_mp3(temp_file)
        
        # Add character-specific audio effects
        audio = add_dynamic_audio_effects(audio, character)
        
        # Add natural breathing sounds
        audio = add_natural_breathing(audio)
        
        # Export the enhanced audio
        audio.export(output_file, format="mp3", bitrate="192k")
        
        os.remove(temp_file)
        print(f"Enhanced TTS audio saved to {output_file} for character: {character} in language: {language_code}")
        return True
    except Exception as e:
        print(f"Google Cloud TTS error: {str(e)}")
        
        # Fallback to a simpler version without SSML if there's an error
        if supports_ssml and ("SSML" in str(e) or "synthesis input" in str(e).lower()):
            print("Error with SSML, attempting fallback with plain text...")
            try:
                # Clean text of any SSML tags
                clean_text = re.sub(r'<[^>]+>', '', text)
                synthesis_input = texttospeech.SynthesisInput(text=clean_text)
                
                # Simpler audio config
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=voice_params["speaking_rate"]
                )
                
                response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
                
                with open(output_file, "wb") as out:
                    out.write(response.audio_content)
                
                print(f"Fallback TTS audio saved to {output_file}")
                return True
            except Exception as fallback_error:
                print(f"Fallback TTS also failed: {str(fallback_error)}")
        
        raise ValueError(f"Failed to generate speech for {language_code}")

def detect_sentence_boundaries(text):
    """
    Detect sentence boundaries and return a list of sentences with their punctuation type
    """
    # This regex captures sentences ending with ., !, or ? with any trailing spaces
    sentence_pattern = re.compile(r'[^.!?]+[.!?](?:\s+|$)')
    sentences = sentence_pattern.findall(text)
    
    result = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            punctuation = sentence[-1] if sentence[-1] in '.!?' else '.'
            result.append((sentence, punctuation))
    
    return result

if __name__ == "__main__":
    # Base English messages tailored to each character
    character_tests = {
        "jax": "Hey Jax, roast me while telling me how to cook pasta! Make sure you explain all the steps clearly.",
        "viktor": "Viktor, how do I fix my car? It's making a strange noise when I brake. Is this serious?",
        "lila": "Lila, can you help me pick an outfit? I have a job interview tomorrow, and I want to make a good impression.",
        "elias": "Elias, how do I make a tough decision? I'm stuck between two job offers, and I'm not sure which one to choose."
    }

    # Supported languages
    languages = [
        "en-US", "hi-IN", "ta-IN", "kn-IN", "te-IN", "ml-IN", "bn-IN",
        "mr-IN", "gu-IN", "pa-IN", "ja-JP", "fr-FR", "de-DE", "es-US"
    ]

    output_files = []
    for character, base_message in character_tests.items():
        for lang_code in languages:
            if(lang_code == "en-US"):
                # Translate the base message to the target language
                target_language = lang_code.split("-")[0]
                test_text = translate_text(base_message, target_language)
                output_file = f"test_output_{character}_{lang_code}.mp3"
                print(f"\nTesting {character} in {lang_code}:")
                text_to_speech(test_text, lang_code, character, output_file)
                output_files.append(output_file)
