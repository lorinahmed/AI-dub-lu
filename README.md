# YouTube Video Dubber

An AI-powered application that can dub YouTube videos into any language using speech recognition, translation, and text-to-speech synthesis with ElevenLabs.

## Features

- Download YouTube videos
- Extract and transcribe audio using OpenAI Whisper
- Translate transcriptions to target language
- Generate high-quality speech using ElevenLabs TTS
- AI-powered speaker diarization and voice matching
- Synchronize new audio with original video
- Support for multiple languages
- Real-time job status tracking

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
cp env.example .env
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

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Submit Regular Dubbing Job
**POST** `/dub`

Submit a YouTube video for standard dubbing with automatic gender detection.

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "target_language": "es",
  "source_language": "en"
}
```

**Parameters:**
- `youtube_url` (required): Full YouTube URL
- `target_language` (required): Target language code (e.g., "es", "fr", "de")
- `source_language` (optional): Source language code (auto-detected if not provided)

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Dubbing job started successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/dub" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "target_language": "es",
    "source_language": "en"
  }'
```

#### 2. Submit AI-Powered Dubbing Job
**POST** `/dub/ai`

Submit a YouTube video for AI-enhanced dubbing with speaker diarization and intelligent voice matching.

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "target_language": "es",
  "source_language": "en",
  "use_ai_analysis": true
}
```

**Parameters:**
- `youtube_url` (required): Full YouTube URL
- `target_language` (required): Target language code
- `source_language` (optional): Source language code
- `use_ai_analysis` (optional): Enable AI analysis (default: true)

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "AI-powered dubbing job started successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/dub/ai" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "target_language": "es",
    "source_language": "en",
    "use_ai_analysis": true
  }'
```

#### 3. Check Job Status
**GET** `/status/{job_id}`

Get the current status and progress of a dubbing job.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "translating",
  "progress": 50,
  "message": "Translating transcription to target language",
  "error": null
}
```

**Status Values:**
- `initialized`: Job created
- `downloading`: Downloading YouTube video
- `extracting_audio`: Extracting audio from video
- `detecting_gender`: Detecting speaker gender
- `transcribing`: Transcribing audio to text
- `translating`: Translating text to target language
- `generating_speech`: Generating speech with TTS
- `synchronizing`: Syncing audio with video
- `completed`: Job completed successfully
- `failed`: Job failed

**Example:**
```bash
curl "http://localhost:8000/status/550e8400-e29b-41d4-a716-446655440000"
```

#### 4. Download Dubbed Video
**GET** `/download/{job_id}`

Get download information for a completed dubbed video.

**Response:**
```json
{
  "download_url": "/files/550e8400-e29b-41d4-a716-446655440000/dubbed_video.mp4"
}
```

**Example:**
```bash
curl "http://localhost:8000/download/550e8400-e29b-41d4-a716-446655440000"
```

#### 5. Get All Jobs
**GET** `/jobs`

Get statistics and information about all dubbing jobs.

**Response:**
```json
{
  "total_jobs": 10,
  "completed_jobs": 8,
  "failed_jobs": 1,
  "active_jobs": 1,
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "progress": 100,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/jobs"
```

#### 6. Health Check
**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "YouTube Video Dubber"
}
```

**Example:**
```bash
curl "http://localhost:8000/health"
```

## Supported Languages

### Text-to-Speech (ElevenLabs)
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Hindi (hi)
- Arabic (ar)

### Translation
All languages supported by Google Translate API.

### Transcription
All languages supported by OpenAI Whisper.

## Environment Variables

Create a `.env` file with the following variables:

```bash
# ElevenLabs API Key (Required for TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Google Translate API Key (Optional)
GOOGLE_TRANSLATE_API_KEY=your_google_translate_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# File Paths
OUTPUT_DIR=./outputs
UPLOAD_DIR=./uploads
TEMP_DIR=./temp

# TTS Configuration
TTS_SERVICE=elevenlabs
TTS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

## Architecture

```
YouTube URL → Download → Extract Audio → Transcribe → Translate → TTS → Sync → Final Video
                    ↓
              AI Analysis (Speaker Diarization, Gender Detection, Voice Matching)
```

## Processing Pipeline

### Regular Dubbing:
1. **Download**: Download YouTube video
2. **Extract Audio**: Extract audio track from video
3. **Gender Detection**: Detect speaker gender from audio
4. **Transcribe**: Convert audio to text using Whisper
5. **Translate**: Translate text to target language
6. **TTS**: Generate speech with gender-matched voice
7. **Sync**: Synchronize new audio with original video

### AI-Powered Dubbing:
1. **Download**: Download YouTube video
2. **Extract Audio**: Extract audio track from video
3. **AI Transcription**: Transcribe with speaker diarization
4. **AI Analysis**: Analyze speaker characteristics, gender, emotion
5. **Voice Matching**: Intelligently match voices per speaker
6. **Context Translation**: Translate with context preservation
7. **AI Speech Generation**: Generate speech with speaker-specific voices
8. **Sync**: Synchronize new audio with original video

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Job not found
- `500`: Internal server error

Error responses include a `detail` field with the error message.

## License

MIT License 