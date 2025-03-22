from flask import Flask, render_template, request, jsonify
import os
import time
import atexit
import signal
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage
from transcribe_audio import transcribe_audio
from tts import text_to_speech, translate_text
from gemini_api import get_character_response
from firebase_creds import cred
import subprocess

app = Flask(__name__)

load_dotenv()

firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
if not firebase_storage_bucket:
    raise ValueError("FIREBASE_STORAGE_BUCKET not set in .env file")

firebase_admin.initialize_app(cred, {'storageBucket': firebase_storage_bucket})
db = firestore.client()
bucket = storage.bucket()

UPLOAD_FOLDER = "static/audio"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def clear_collection(ip_address, character):
    collection_name = f"{ip_address.replace('.', '_')}_{character}"
    print(f"Clearing Firestore '{collection_name}' collection...")
    docs = db.collection(collection_name).stream()
    for doc in docs:
        doc.reference.delete()

def clear_storage(ip_address, character):
    prefix = f"audio/{ip_address.replace('.', '_')}_{character}/"
    print(f"Clearing Firebase Storage '{prefix}' folder...")
    blobs = bucket.list_blobs(prefix=prefix)
    for blob in blobs:
        blob.delete()

def cleanup_all():
    print("Cleaning up all Firebase data...")
    collections = db.collections()
    for collection in collections:
        for doc in collection.stream():
            doc.reference.delete()
    blobs = bucket.list_blobs(prefix="audio/")
    for blob in blobs:
        blob.delete()

cleanup_all()
atexit.register(cleanup_all)

def handle_shutdown(signal, frame):
    print("Received SIGINT (Ctrl+C). Performing cleanup...")
    cleanup_all()
    exit(0)

signal.signal(signal.SIGINT, handle_shutdown)

character_data = {
    'victor': {
        'name': 'Victor Graves',
        'title': 'Victor Graves – The Rude One',
        'description': 'A no-nonsense ex-military strategist who thinks everyone around him is an idiot. He’s brutally honest, sarcastic, and impatient but delivers some of the most effective, no-BS advice—if you can handle the insults.'
    },
    'jax': {
        'name': 'Jax Carter',
        'title': 'Jax "Wildcard" Carter – The Funny One',
        'description': 'A former stand-up comedian turned professional internet troll. He never takes anything seriously and roasts everyone, including you. Despite his chaotic nature, his advice is surprisingly useful—when he feels like giving it.'
    },
    'elias': {
        'name': 'Elias Sterling',
        'title': 'Elias Sterling – The Helpful Mentor',
        'description': 'A former professor who left academia to seek real wisdom. He’s calm, insightful, and asks thought-provoking questions that make you think deeply about your choices. A bit mysterious but always kind.'
    },
    'lila': {
        'name': 'Lila Moreau',
        'title': 'Lila Moreau – The Flirt',
        'description': 'A smooth-talking ex-private investigator who loves to tease and charm. Every conversation is a game to her, and she enjoys keeping you on your toes with playful flirtation while subtly guiding you toward the right answer.'
    }
}

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def index():
    return render_template('index.html')

def get_conversation(ip_address, character):
    collection_name = f"{ip_address.replace('.', '_')}_{character}"
    conversation_ref = db.collection(collection_name).order_by('timestamp')
    return [doc.to_dict() for doc in conversation_ref.stream()]

@app.route('/<character>')
def character_chat(character):
    if character not in character_data:
        return "Character not found", 404
    ip_address = request.remote_addr
    conversation = get_conversation(ip_address, character)
    return render_template('character_template.html',
                         character_id=character,
                         character_name=character_data[character]['name'],
                         character_title=character_data[character]['title'],
                         character_description=character_data[character]['description'],
                         conversation=conversation,
                         ip_address=ip_address)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    synthesized_audio_path = None
    recorded_audio_path = None
    converted_audio_path = None
    try:
        ip_address = request.remote_addr.replace('.', '_')
        character = request.form.get('character')
        selected_language = request.form.get('language', 'en-US')
        
        if not character:
            return jsonify({"error": "No character specified"}), 400
        if not selected_language:
            return jsonify({"error": "No language selected"}), 400
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']
        timestamp = str(time.time_ns())
        recorded_audio_path = f"{UPLOAD_FOLDER}/recorded_audio_{timestamp}.webm"
        audio_file.save(recorded_audio_path)
        print(f"Received and saved audio to {recorded_audio_path}")

        # Convert WebM to WAV using ffmpeg
        converted_audio_path = f"{UPLOAD_FOLDER}/converted_audio_{timestamp}.wav"
        subprocess.run([
            'ffmpeg', '-y', '-i', recorded_audio_path, 
            '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', 
            converted_audio_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Converted audio to {converted_audio_path}")

        recorded_blob_path = f"audio/{ip_address}_{character}/recorded_audio_{timestamp}.wav"
        recorded_blob = bucket.blob(recorded_blob_path)
        recorded_blob.upload_from_filename(converted_audio_path)  # Upload the converted WAV
        recorded_blob.make_public()
        recorded_audio_url = recorded_blob.public_url
        print(f"Uploaded recorded audio to {recorded_blob_path}: {recorded_audio_url}")

        transcript = transcribe_audio(converted_audio_path, language=selected_language)
        if not transcript:
            return jsonify({"error": "Transcription failed or no speech detected"}), 500
        print(f"Transcription successful: '{transcript}'")

        target_language = selected_language.split("-")[0]
        transcript_en = translate_text(transcript, "en")
        response_en = get_character_response(transcript_en, "en-US", character)
        if "Error" in response_en:
            return jsonify({"error": f"Failed to get response: {response_en}"}), 500

        response = translate_text(response_en, target_language)
        synthesized_audio_path = f"{UPLOAD_FOLDER}/synthesized_audio_{timestamp}.mp3"
        text_to_speech(response, selected_language, character, synthesized_audio_path)
        print(f"Synthesized audio saved to {synthesized_audio_path}")

        synthesized_blob_path = f"audio/{ip_address}_{character}/synthesized_audio_{timestamp}.mp3"
        synthesized_blob = bucket.blob(synthesized_blob_path)
        synthesized_blob.upload_from_filename(synthesized_audio_path)
        synthesized_blob.make_public()
        synthesized_audio_url = synthesized_blob.public_url
        print(f"Uploaded synthesized audio to {synthesized_blob_path}: {synthesized_audio_url}")

        conversation_ref = db.collection(f"{ip_address}_{character}")
        conversation_ref.add({
            'user_input_id': f"user_input_{timestamp}",
            'timestamp': firestore.SERVER_TIMESTAMP,
            'user_input': transcript,
            'response': response,
            'character': character,
            'selected_language': selected_language,
            'recorded_audio_url': recorded_audio_url,
            'synthesized_audio_url': synthesized_audio_url
        })

        conversation = [doc.to_dict() for doc in conversation_ref.order_by('timestamp').stream()]
        
        return jsonify({
            "transcript": transcript,
            "response": response,
            "character": character,
            "selected_language": selected_language,
            "recorded_audio_url": recorded_audio_url,
            "synthesized_audio_url": synthesized_audio_url,
            "conversation": conversation
        })
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion error: {e.stderr.decode()}")
        return jsonify({"error": "Audio conversion failed"}), 500
    except Exception as e:
        import traceback
        print(f"Error in process_audio: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        if recorded_audio_path and os.path.exists(recorded_audio_path):
            os.remove(recorded_audio_path)
        if converted_audio_path and os.path.exists(converted_audio_path):
            os.remove(converted_audio_path)
        if synthesized_audio_path and os.path.exists(synthesized_audio_path):
            os.remove(synthesized_audio_path)

@app.route('/process_text', methods=['POST'])
def process_text():
    synthesized_audio_path = None
    try:
        ip_address = request.remote_addr.replace('.', '_')
        data = request.get_json()
        text = data.get('text', '').strip()
        character = data.get('character')
        selected_language = data.get('language', 'en-US')
        
        if not character:
            return jsonify({"error": "No character specified"}), 400
        if not selected_language:
            return jsonify({"error": "No language selected"}), 400
        if not text:
            return jsonify({"error": "No text provided"}), 400

        full_language_code = selected_language
        target_language = selected_language.split("-")[0]

        text_en = translate_text(text, "en")
        response_en = get_character_response(text_en, "en-US", character)
        if "Error" in response_en:
            return jsonify({"error": f"Failed to get response: {response_en}"}), 500

        response = translate_text(response_en, target_language)
        timestamp = str(time.time_ns())
        user_input_id = f"user_input_{timestamp}"
        synthesized_audio_path = f"{UPLOAD_FOLDER}/synthesized_audio_{timestamp}.mp3"
        text_to_speech(response, full_language_code, character, synthesized_audio_path)
        print(f"Synthesized audio saved to {synthesized_audio_path}")

        synthesized_blob_path = f"audio/{ip_address}_{character}/synthesized_audio_{timestamp}.mp3"
        synthesized_blob = bucket.blob(synthesized_blob_path)
        synthesized_blob.upload_from_filename(synthesized_audio_path)
        synthesized_blob.make_public()
        synthesized_audio_url = synthesized_blob.public_url
        print(f"Uploaded synthesized audio to {synthesized_blob_path}: {synthesized_audio_url}")

        conversation_ref = db.collection(f"{ip_address}_{character}")
        conversation_ref.add({
            'user_input_id': user_input_id,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'user_input': text,
            'response': response,
            'character': character,
            'selected_language': full_language_code,
            'recorded_audio_url': None,
            'synthesized_audio_url': synthesized_audio_url
        })

        conversation = [doc.to_dict() for doc in conversation_ref.order_by('timestamp').stream()]
        
        return jsonify({
            "transcript": text,
            "response": response,
            "character": character,
            "selected_language": full_language_code,
            "recorded_audio_url": None,
            "synthesized_audio_url": synthesized_audio_url,
            "conversation": conversation
        })
    except Exception as e:
        import traceback
        print(f"Error in process_text: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        if synthesized_audio_path and os.path.exists(synthesized_audio_path):
            os.remove(synthesized_audio_path)

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        character = data.get('character')
        if not ip_address or not character:
            return jsonify({"error": "Missing IP address or character"}), 400
        
        clear_collection(ip_address, character)
        clear_storage(ip_address, character)
        print(f"Cleared chat for IP: {ip_address}, Character: {character}")
        return jsonify({"message": "Chat cleared"}), 200
    except Exception as e:
        print(f"Error in clear_chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5003))
    app.run(host="0.0.0.0", port=port, debug=True)
























