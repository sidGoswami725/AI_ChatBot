# Character Chatbot

A Flask-based interactive chatbot application that lets users engage in conversations with AI-powered characters through text or voice inputs.

## Overview

DALL-BOT is a web-based chat application that allows users to interact with four distinct AI characters: Victor Graves, Jax Carter, Elias Sterling, and Lila Moreau. Each character has a unique personality and backstory, providing tailored responses to user inputs via text or audio. The application leverages Google Cloud services for speech-to-text (STT), text-to-speech (TTS), and translation, alongside Firebase for data storage and the Gemini API for character response generation. Built with Flask, this project offers multilingual support and a dynamic, user-friendly interface.

This project is designed as a cloud-deployed service and does not include instructions for local setup, focusing instead on its architecture and functionality.

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


### 10. Render Setup
   - Sign up for a Render account at [Render](render.com)

    - Create a new Web Service and connect your GitHub repository.
    -  Set the build command to pip install -r requirements.txt and the start command to python app.py.
    -  Add the necessary environment variables in Render's dashboard.
    -  Deploy the application.

   

### Usage


### 1. Access the App

### 2. Visit the deployed application

### 3. Select a Character

   - Click a character from the sidebar (Victor, Jax, Elias, or Lila).

### 4. Choose a Language

   
   - Use the dropdown to select your preferred language.

### 5. Interact


   - Voice: Click the microphone button, speak, and click again to stop. The audio will be transcribed and responded to.
   - Text: Type a message and press "Send" or Enter.
   - Clear Chat: Click "Clear Chat" to reset the conversation.


### 6. Listen to Responses

   - Responses include synthesized audio playable via the embedded audio controls.

## File Structure 🌳

/backend  
│── static/  
│   ├── style.css         # Frontend styles  
│   ├── script.js         # Chat UI interactions  
│── templates/  
│   ├── index.html        # Main page  
│   ├── character_template.html # Chat interface  
│── app.py                # Flask backend  
│── gemini_api.py         # AI response generation  
│── record_audio.py       # Audio recording logic  
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
