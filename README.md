# DALL-BOT: Interactive Character Chatbot

Welcome to **DALL-BOT**, an interactive chatbot application powered by Flask, Firebase, Google Cloud services, and the Gemini API. Engage with four unique AI characters—Victor Graves, Jax Carter, Elias Sterling, and Lila Moreau—each with distinct personalities and backstories. Whether you prefer text or voice input, DALL-BOT supports multiple languages and delivers a dynamic, engaging experience with synthesized speech and real-time transcription.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Characters](#characters)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multi-Character Interaction**: Chat with four distinct AI personas, each with unique tones and backstories.
- **Voice and Text Input**: Record audio or type messages, with real-time transcription and text-to-speech (TTS).
- **Multilingual Support**: Supports languages including English, Hindi, Tamil, Kannada, Telugu, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Japanese, French, German, and Spanish.
- **Cloud Integration**: Uses Firebase for storage and Firestore for conversation persistence, alongside Google Cloud for TTS and transcription.
- **Dynamic Audio Effects**: Character-specific audio enhancements for a more immersive experience.
- **Responsive UI**: Sleek, modern interface with a sidebar for character selection and chat history.

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Google Cloud Speech-to-Text, Text-to-Speech, Translation; Gemini API
- **Database/Storage**: Firebase Firestore, Firebase Storage
- **Audio Processing**: FFmpeg, PyDub
- **Environment Management**: python-dotenv
- **Deployment**: Render

## Installation

### Prerequisites

- Python 3.8+
- Node.js (for FFmpeg if not installed separately)
- Google Cloud account and Firebase project
- Gemini API key
- Render account for deployment

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/dall-bot.git
   cd dall-bot

   Set Up Virtual Environment

bash

Collapse

Wrap

Copy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies

bash

Collapse

Wrap

Copy
pip install -r requirements.txt
The requirements.txt includes:

text

Collapse

Wrap

Copy
flask
firebase-admin
google-cloud-speech
google-cloud-texttospeech
google-cloud-translate
pydub
python-dotenv
requests
Install FFmpeg

On macOS: brew install ffmpeg
On Ubuntu: sudo apt install ffmpeg
On Windows: Download from FFmpeg website and add to PATH.
Configure Environment Variables

Ensure you have the necessary environment variables set up for Firebase, Google Cloud, and Gemini API. These should include credentials for Firebase Storage, Firestore, Google Cloud services, and the Gemini API key. Refer to the respective documentation for details on obtaining these credentials.

Set Up Firebase

Create a Firebase project and enable Firestore and Storage.
Configure your Firebase credentials as environment variables.
Deploy on Render

Sign up for a Render account at render.com.
Create a new Web Service and connect your GitHub repository.
Set the build command to pip install -r requirements.txt and the start command to python app.py.
Add the necessary environment variables in Render's dashboard.
Deploy the application.
The deployed application is available at: https://ai-chatbot-1-h7qz.onrender.com

Usage
Access the App

Visit the deployed application at https://ai-chatbot-1-h7qz.onrender.com.

Select a Character

Click a character from the sidebar (Victor, Jax, Elias, or Lila).

Choose a Language

Use the dropdown to select your preferred language.

Interact

Voice: Click the microphone button, speak, and click again to stop. The audio will be transcribed and responded to.
Text: Type a message and press "Send" or Enter.
Clear Chat: Click "Clear Chat" to reset the conversation.
Listen to Responses

Responses include synthesized audio playable via the embedded audio controls.

Characters
Victor Graves: Ex-military strategist, rude but effective.
Jax Carter: Former comedian and internet troll, funny and chaotic.
Elias Sterling: Wise ex-professor, calm and insightful.
Lila Moreau: Flirty ex-private investigator, charming and playful.
Project Structure

dall-bot/
├── static/                 # Static assets (CSS, JS, images)
│   ├── script.js          # Frontend JavaScript logic
│   ├── style.css          # CSS styling
│   ├── audio/             # Temporary audio storage
│   ├── victor.jpeg        # Character images
│   ├── jax.jpeg
│   ├── elias.jpeg
│   ├── lila.jpeg
│   ├── mic_button.png
│   └── send_button.png
├── templates/              # HTML templates
│   ├── index.html         # Welcome page
│   └── character_template.html  # Chat interface
├── app.py                 # Main Flask application
├── firebase_creds.py      # Firebase credentials setup
├── gemini_api.py          # Gemini API integration
├── google_creds.py        # Google Cloud credentials setup
├── requirements.txt       # Python dependencies
├── transcribe_audio.py    # Audio transcription logic
├── tts.py                 # Text-to-speech logic
└── README.md              # This file
