# YouTube Video Dubber

An AI-powered application that can dub YouTube videos into any language using speech recognition, translation, and text-to-speech synthesis.

## Features

- Download YouTube videos
- Extract and transcribe audio using OpenAI Whisper
- Translate transcriptions to target language
- Generate high-quality speech in target language
- Synchronize new audio with original video
- Support for multiple languages

## Prerequisites

- Python 3.8+
- FFmpeg installed on your system
- API keys for:
  - ElevenLabs (for high-quality TTS)
  - Google Translate (optional, for translation)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd dubber
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

1. Start the backend server:
```bash
python main.py
```

2. Open the frontend in your browser:
```bash
cd frontend
npm install
npm start
```

3. Enter a YouTube URL and select your target language to start dubbing!

## API Endpoints

- `POST /dub` - Submit a YouTube URL for dubbing
- `GET /status/{job_id}` - Check dubbing job status
- `GET /download/{job_id}` - Download the dubbed video

## Supported Languages

The app supports all languages available in:
- OpenAI Whisper (for transcription)
- Google Translate (for translation)
- ElevenLabs (for text-to-speech)

## Architecture

```
YouTube URL → Download → Extract Audio → Transcribe → Translate → TTS → Sync → Final Video
```

## License

MIT License 