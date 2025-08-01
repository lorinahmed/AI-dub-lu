# YouTube Video Dubber

An AI-powered application that can dub YouTube videos into any language using speech recognition, translation, and text-to-speech synthesis with ElevenLabs.

## Features

- Download YouTube videos
- Extract and transcribe audio using OpenAI Whisper
- Translate transcriptions to target language
- Generate high-quality speech using ElevenLabs TTS
- **AI-powered speaker diarization using PyAnnote**
- **Intelligent voice matching with ElevenLabs voices**
- **AI-powered speaker diarization using PyAnnote**
- **Intelligent voice matching with ElevenLabs voices**
- **Timing-aware translation and speed adjustment (always enabled for AI dubbing)**
- Synchronize new audio with original video
- Support for multiple languages
- Real-time job status tracking

## AI-Enhanced Dubbing with Timing Awareness

The AI-Enhanced dubbing feature automatically includes timing-aware translation and speed adjustment to ensure that dubbed audio matches the original dialogue timing:

### 1. Timing-Aware Translation
- Uses GPT to translate text while preserving timing constraints
- Calculates target word count based on original segment duration
- Ensures translated text can be spoken within the original time frame
- Preserves meaning while adapting length for natural speech

### 2. Adjustable TTS Speed
- Automatically adjusts TTS playback speed to match original timing
- Limits speed adjustments to ±15% to maintain natural voice quality
- Processes each dialogue segment individually for precise timing
- Combines segments with proper synchronization

### 3. AI-Enhanced Features
- Combines timing awareness with speaker diarization
- Maintains voice consistency per speaker
- Intelligent voice matching with timing constraints
- Preserves speaker characteristics while adjusting timing

### How It Works
1. **Speaker Diarization**: Identify different speakers in the audio
2. **Transcription**: Extract audio segments with precise timing using Whisper
3. **Timing-Aware Translation**: Use GPT to translate each segment with timing constraints
4. **Voice Matching**: Match appropriate voices to each speaker
5. **TTS Generation**: Generate speech for each segment with speed adjustment
6. **Synchronization**: Combine segments with original timing and sync with video

## Prerequisites

- Python 3.8+
- FFmpeg installed on your system
- API keys for:
  - ElevenLabs (for high-quality TTS)
  - Google Translate (optional, for translation)
  - OpenAI (for timing-aware translation)

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
- `timing_aware` (optional): Enable timing-aware translation and speed adjustment (default: true for AI dubbing)

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

# Hugging Face Token (Required for PyAnnote speaker diarization)
HUGGINGFACE_TOKEN=your_huggingface_token_here

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

## AI-Powered Features

### PyAnnote Speaker Diarization

The system uses **PyAnnote.audio** for advanced speaker diarization, which provides:

- **Accurate Speaker Identification**: Identifies "who spoke when" with precise timestamps
- **Multiple Speaker Support**: Handles conversations with multiple speakers
- **Timestamp Alignment**: Aligns speaker segments with transcription segments
- **High Precision**: Uses deep learning models for speaker recognition

**How it works:**
1. **Audio Analysis**: PyAnnote analyzes the audio waveform to detect speaker changes
2. **Speaker Timeline**: Creates a timeline showing when each speaker is talking
3. **Segment Alignment**: Aligns Whisper transcription segments with PyAnnote speaker segments
4. **Speaker Profiles**: Each detected speaker gets their own voice profile

**Example PyAnnote Output:**
```
[ 00:00:00.030 -->  00:00:28.161] SPEAKER_00
[ 00:00:28.245 -->  00:00:38.033] SPEAKER_02
[ 00:00:39.045 -->  00:00:54.452] SPEAKER_02
[ 00:01:56.417 -->  00:02:28.058] SPEAKER_01
```

### ElevenLabs Intelligent Voice Matching

The system implements sophisticated voice matching using ElevenLabs' voice library:

#### Voice Characteristics Analysis
For each detected speaker, the system analyzes:
- **Pitch Characteristics**: Mean pitch, pitch range, pitch standard deviation
- **Spectral Features**: Spectral centroid (voice brightness/warmth)
- **Energy Levels**: RMS energy (speaking intensity)
- **MFCC Features**: Voice timbre and texture
- **Speaking Rate**: Zero-crossing rate approximation

#### Voice Matching Algorithm
The system matches speakers to ElevenLabs voices using:

1. **Language Filtering**: Filters voices by target language support using `verified_languages` array
2. **Acoustic Scoring**: Calculates match scores based on:
   - **Pitch Compatibility**: Matches speaker pitch to voice gender characteristics
   - **Age Characteristics**: Uses spectral centroid to match age-appropriate voices
   - **Energy Level**: Matches speaking intensity to voice descriptions
   - **Voice Uniqueness**: Ensures each speaker gets a different voice when possible

3. **Score Calculation**:
   ```
   Score = Pitch Match (3.0) + Age Match (2.0) + Energy Match (1.5) + Accent Bonus (0.5)
   ```

#### Voice Selection Process
```
Speaker Analysis → Voice Download → Language Filter → Score Calculation → Best Match Selection
```

**Example Voice Matching:**
```
Speaker SPEAKER_00 (Pitch: 1407Hz, Energy: 0.034) → Charlie (Score: 2.00)
Speaker SPEAKER_02 (Pitch: 1160Hz, Energy: 0.040) → George (Score: 2.00)  
Speaker SPEAKER_01 (Pitch: 1424Hz, Energy: 0.045) → Will (Score: 4.00)
```

## Architecture

```
YouTube URL → Download → Extract Audio → AI Transcription → Voice Analysis → Voice Matching → TTS → Sync → Final Video
                    ↓
              PyAnnote Diarization + Whisper Alignment + ElevenLabs Voice Matching
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
3. **PyAnnote Diarization**: Identify speakers and create timeline
4. **Whisper Transcription**: Transcribe with word-level timestamps
5. **Segment Alignment**: Align Whisper segments with PyAnnote speakers
6. **Voice Analysis**: Analyze acoustic characteristics per speaker
7. **ElevenLabs Voice Matching**: Download and match voices by language + characteristics
8. **Context Translation**: Translate with speaker context preservation
9. **AI Speech Generation**: Generate speech with matched voices per speaker
10. **Audio Combination**: Combine speaker audio with timing preservation
11. **Sync**: Synchronize new audio with original video

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Job not found
- `500`: Internal server error

Error responses include a `detail` field with the error message.

## License

MIT License 