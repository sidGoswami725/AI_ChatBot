# Character Chatbot
[DALL-BOT(Deployment link)](https://ai-chatbot-1-h7qz.onrender.com)

A Flask-based interactive chatbot application that lets users engage in conversations with AI-powered characters through text or voice inputs.

## Overview

This project features four distinct AI characters—Jax, Victor, Lila, and Elias—each with their own personality, backstory, and tone. Users can chat with them by recording audio or typing text, with responses generated in real-time and delivered via synthesized speech. The app supports multiple languages, stores conversation history in Firebase, and includes audio processing enhancements for a natural experience.


### Characters
- *Jax "Wildcard" Carter*: A sarcastic comedian who roasts users while providing helpful answers.
- *Victor Graves*: A blunt ex-military strategist who gives no-nonsense advice.
- *Lila Moreau*: A flirtatious ex-private investigator who charms while assisting.
- *Elias Sterling*: A wise mentor offering thoughtful, practical guidance.

## Features✨
- *Voice Input*: Record audio with voice activity detection and noise reduction.
- *Transcription*: Convert audio to text using Google Cloud Speech-to-Text.
- *Text-to-Speech*: Generate natural-sounding responses with Google Cloud TTS, enhanced with prosody and character-specific effects.
- *Multilingual Support*: Supports languages like English, Hindi, Tamil, French, and more.
- *Conversation History*: Stored in Firebase Firestore and synced per user IP and character.
- *Audio Storage*: Uploaded to Firebase Storage with public URLs for playback.
- *Character Personalities*: Responses generated via Gemini API with unique character prompts.

## Setup
Follow these detailed steps to set up the Character Chat Application on your local machine:

### 1. Prerequisites 📋
- Python 3.8+
- Flask
- Firebase account with Firestore & Storage configured
- Google Cloud API access for Speech-to-Text and Text-to-Speech
- OpenAI API Key (if using OpenAI models)

### 2. Installation
Clone the repository:
bash
git clone https://github.com/your-username/character-chatbot.git  
cd character-chatbot  

Install dependencies:
bash
pip install -r requirements.txt  


### 3. Environment Variables
Create a .env file and add the required API keys:

API_KEY=your_gemini_api_key  
FIREBASE_CREDENTIALS=path/to/your/firebase-credentials.json  
FIREBASE_STORAGE_BUCKET=your-firebase-bucket-name  
GOOGLE_CLOUD_PROJECT=your-google-cloud-project  

### 5. Set Up Google Cloud Credentials
   - Go to [Google Cloud Console](https://console.cloud.google.com).

   - Create a project or use an existing one.
   - Enable the Speech-to-Text and Text-to-Speech APIs:
     - Navigate to "APIs & Services" > "Library."
     - Search for and enable "Cloud Speech-to-Text API" and "Cloud Text-to-Speech API."
   - Create a service account:
     - Go to "IAM & Admin" > "Service Accounts."
     - Click "Create Service Account," name it (e.g., `character-chat`), and grant it "Editor" role.
     - Generate a JSON key and download it (e.g., `google-credentials.json`).
   - Place the JSON file in your project directory and update `FIREBASE_CREDENTIALS` in `.env` with its path.


### 6. Set Up Firebase
   - Visit [Firebase Console](https://console.firebase.google.com).

   - Create a new project (e.g., `character-chat-app`).
   - Enable Firestore and Storage:
     - Go to "Firestore Database" > "Create Database" (start in test mode for simplicity).
     - Go to "Storage" > "Get Started" and set up default rules.
   - Generate a service account key:
     - Go to "Project Settings" > "Service Accounts."
     - Click "Generate new private key" and download the JSON (e.g., `firebase-credentials.json`).
   - Place the JSON in your project directory and update `FIREBASE_CREDENTIALS` in `.env`.
   - Copy your storage bucket name from "Storage" (e.g., `your-project-id.appspot.com`) and set it as `FIREBASE_STORAGE_BUCKET`.


### 7. Obtain a Gemini API Key

   - Sign up for access to the Gemini API (check the provider’s official site for details).
   - Generate an API key and add it to `.env` as `API_KEY`.


### 8. Install FFmpeg

     - FFmpeg is required for audio conversion. Install it based on your OS:
     - On macOS:
     brew install ffmpeg

   #### - On Ubuntu:
   
      sudo apt-get install ffmpeg
   
   #### - On Windows:
   - Download from [FFmpeg website](https://ffmpeg.org/download.html).
   
       - Extract and add the `bin` folder to your system PATH (e.g., `C:\ffmpeg\bin`).
       - Verify installation:
       ffmpeg -version
   

### 9. Verify Setup


    - Ensure all dependencies are installed (`pip list` should show `flask`, `google-cloud-speech`, etc.).
   - Check that `.env` is correctly configured and service account JSONs are accessible.


### Running the Application

### 1. Start the Flask Server

   python app.py
   The app runs on `http://localhost:5003`.

### 2. Access the Web Interface
   
   - Open a browser and navigate to `http://localhost:5003`.
   - Select a character from the sidebar.

### 3. Interact with Characters

   - Voice Input: Click the microphone button to record (up to 10 seconds).
   - Text Input: Type a message and click send.
   - Select a language from the dropdown.

### 4.  View Conversation History
   
   - Messages and audio responses appear in the chat window.

### 5. Clear Chat

   - Click "Clear Chat" to reset the conversation.


## File Structure 🌳

/character-chatbot  
│── static/  
│   ├── style.css         # Frontend styles  
│   ├── script.js         # Chat UI interactions  
│── templates/  
│   ├── index.html        # Main page  
│   ├── character_template.html # Chat interface  
│── app.py                # Flask backend  
│── gemini_api.py         # AI response generation   
│── transcribe_audio.py   # Speech-to-text using Google Cloud  
│── tts.py                # Text-to-speech processing  
│── requirements.txt      # Dependencies  
│── README.md             # Project documentation  


### Dependencies

- flask: Web framework
- google-cloud-speech: Speech-to-Text
- google-cloud-texttospeech: Text-to-Speech
- python-dotenv: Environment variable management
- firebase-admin: Firebase integration
- pydub, torchaudio, scipy: Audio processing
- requests: API calls

### Notes
- Grant microphone permissions in your browser for voice input.
- Audio files in static/audio/ are temporary and cleaned up after upload.
- IP-based conversation separation may not work in shared networks.
- Some voices (e.g., Chirp3-HD) may not support SSML; plain text is used as a fallback.

## API Endpoints
- **/** - Home page 
- **/<character>** - Chat page for a specific character 
- **/process_audio** - Handles voice input 
- **/process_text** - Handles text input 

### Troubleshooting
- Transcription Fails: Verify Google Cloud credentials and audio file.
- TTS Errors: Check language code and voice in tts.py.
- Firebase Issues: Confirm service account permissions and bucket setup.
- No Audio Output: Ensure FFmpeg is installed and in PATH.

### Contributing 🌟
 Submit pull requests or open issues for bugs and features!


## Credits
 Developed by **DALL-Eminators**.

## License
 MIT License.
